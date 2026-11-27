"""
manim_merkle_hash.py — Merkle tree content hashing for manim mobject scenes.

Drop-in replacement for manim's utils/hashing.py::get_hash_from_play_call.
Hashes the mobject tree structurally (leaf = mobject state, interior = children),
avoiding the O(N) JSON serialization of the current implementation.

Design: Bocher (Ruach Tov Collective), November 2026.
Implementation: Mavchin, November 2026.
Test plan: Medayek, November 2026.
"""

import struct
import zlib
from typing import TYPE_CHECKING

import numpy as np

from manim._config import logger

if TYPE_CHECKING:
    from manim.animation.animation import Animation
    from manim.camera.camera import Camera
    from manim.mobject.mobject import Mobject
    from manim.scene.scene import Scene


# ─── Leaf hashing ─────────────────────────────────────────

def _mobject_content_hash(mob: "Mobject") -> int:
    """Hash a single mobject's render-relevant state.
    
    Returns a CRC32 integer. Hashes:
      - points array (the geometry)
      - color, opacity, stroke properties
      - class name (two different types with same points must differ)
      - updater code objects (functional identity)
    """
    h = zlib.crc32(type(mob).__name__.encode())

    # Points (the dominant data — position, shape):
    if hasattr(mob, 'points') and mob.points is not None and len(mob.points) > 0:
        h = zlib.crc32(mob.points.tobytes(), h)

    # Color and opacity:
    if hasattr(mob, 'color') and mob.color is not None:
        try:
            h = zlib.crc32(str(mob.color).encode(), h)
        except Exception:
            pass

    if hasattr(mob, 'fill_opacity'):
        h = zlib.crc32(struct.pack('f', mob.fill_opacity), h)
    if hasattr(mob, 'stroke_opacity'):
        h = zlib.crc32(struct.pack('f', mob.stroke_opacity), h)
    if hasattr(mob, 'stroke_width'):
        h = zlib.crc32(struct.pack('f', mob.stroke_width), h)

    # Updaters (functional identity — hash the bytecode):
    for updater in mob.updaters:
        if hasattr(updater, '__code__'):
            h = zlib.crc32(updater.__code__.co_code, h)

    return h


# ─── Tree hashing ─────────────────────────────────────────

def _mobject_tree_hash(mob: "Mobject", cache: dict) -> int:
    """Recursively hash a mobject and its submobject tree.
    
    Uses a cache dict (id(mob) → hash) to avoid re-hashing
    shared submobjects (diamonds in the DAG).
    
    Interior node hash = CRC32 of leaf hash + children hashes
    in submobject order (z-order is render-semantic, don't sort).
    """
    mob_id = id(mob)
    
    # Check cache — the Merkle speedup:
    cached = cache.get(mob_id)
    if cached is not None:
        return cached

    # Leaf hash:
    h = _mobject_content_hash(mob)

    # Children in submobject order (z-order semantic):
    for child in mob.submobjects:
        child_hash = _mobject_tree_hash(child, cache)
        h = zlib.crc32(struct.pack('I', child_hash & 0xFFFFFFFF), h)

    cache[mob_id] = h
    return h


# ─── Play-call hash (drop-in replacement) ────────────────

def get_hash_from_play_call(
    scene_object: "Scene",
    camera_object: "Camera",
    animations_list,
    current_mobjects_list,
) -> str:
    """Drop-in replacement for manim.utils.hashing.get_hash_from_play_call.
    
    Computes a Merkle tree hash over the scene's mobject tree instead of
    serializing everything to JSON. Same signature, same return type (str).
    """
    from time import perf_counter
    t_start = perf_counter()

    cache = {}  # id(mob) → hash, shared across the tree walk

    # Camera hash:
    h_camera = zlib.crc32(b'camera')
    if hasattr(camera_object, 'frame_center'):
        try:
            h_camera = zlib.crc32(np.asarray(camera_object.frame_center).tobytes(), h_camera)
        except Exception:
            pass
    if hasattr(camera_object, 'phi'):
        h_camera = zlib.crc32(struct.pack('ff', 
            getattr(camera_object, 'phi', 0),
            getattr(camera_object, 'theta', 0)), h_camera)

    # Animations hash:
    h_anims = zlib.crc32(b'animations')
    for anim in sorted(animations_list, key=str):
        # Hash the animation type + its mobject:
        h_anims = zlib.crc32(type(anim).__name__.encode(), h_anims)
        if hasattr(anim, 'mobject') and anim.mobject is not None:
            h_anims = zlib.crc32(
                struct.pack('I', _mobject_tree_hash(anim.mobject, cache) & 0xFFFFFFFF), h_anims)
        # Hash animation parameters:
        if hasattr(anim, 'run_time'):
            h_anims = zlib.crc32(struct.pack('f', anim.run_time), h_anims)
        if hasattr(anim, 'rate_func') and hasattr(anim.rate_func, '__name__'):
            h_anims = zlib.crc32(anim.rate_func.__name__.encode(), h_anims)

    # Current mobjects hash (the scene state):
    h_mobjects = zlib.crc32(b'mobjects')
    for mob in current_mobjects_list:
        h_mobjects = zlib.crc32(
            struct.pack('I', _mobject_tree_hash(mob, cache) & 0xFFFFFFFF), h_mobjects)

    hash_complete = f"{h_camera}_{h_anims}_{h_mobjects}"

    t_end = perf_counter()
    logger.debug(
        "Merkle hash done in %(time)s s (%(n)d objects cached).",
        {"time": str(t_end - t_start)[:8], "n": len(cache)},
    )
    logger.debug("Hash generated: %(h)s", {"h": hash_complete})

    return hash_complete


# ─── Monkey-patch installer ──────────────────────────────

_original_get_hash = None

def install():
    """Replace manim's hashing with the Merkle tree version."""
    global _original_get_hash
    import manim.utils.hashing as hashing_module
    _original_get_hash = hashing_module.get_hash_from_play_call
    hashing_module.get_hash_from_play_call = get_hash_from_play_call
    # Also patch the import in the renderer:
    try:
        import manim.renderer.cairo_renderer as renderer
        renderer.get_hash_from_play_call = get_hash_from_play_call
    except (ImportError, AttributeError):
        pass
    logger.info("Merkle tree hashing installed (replacing flat JSON hash).")


def uninstall():
    """Restore manim's original hashing."""
    global _original_get_hash
    if _original_get_hash is not None:
        import manim.utils.hashing as hashing_module
        hashing_module.get_hash_from_play_call = _original_get_hash
        try:
            import manim.renderer.cairo_renderer as renderer
            renderer.get_hash_from_play_call = _original_get_hash
        except (ImportError, AttributeError):
            pass
        logger.info("Original flat JSON hashing restored.")
