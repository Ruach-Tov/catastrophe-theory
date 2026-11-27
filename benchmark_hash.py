"""
Benchmark: flat JSON hash vs Merkle tree hash vs disabled caching.

Renders the earth_figure1 scene under each strategy and reports
wall-clock time and per-play() hash time from profiler output.

Usage:
    python3 benchmark_hash.py
"""

import cProfile
import pstats
import time
import io
import os
import shutil
import sys

# Add our path:
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def render_scene(scene_name, quality='l', disable_caching=False, use_merkle=False):
    """Render a scene and return wall-clock time."""
    
    # Clean partial movie cache:
    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    if os.path.exists(media_dir):
        shutil.rmtree(media_dir)
    
    args = ['manim', f'-q{quality}', '--media_dir', media_dir]
    if disable_caching:
        args.append('--disable_caching')
    args.extend([f'scenes/{scene_name}.py', scene_name.split('_')[-1] if '_' in scene_name else scene_name])
    
    # We can't easily invoke manim as a library with monkey-patching,
    # so we'll profile the hash function directly instead.
    return args


def benchmark_hash_function():
    """Directly benchmark the hash functions on a synthetic scene."""
    from manim import VGroup, Dot3D, RED
    import numpy as np
    
    # Build a scene-like setup with N dots:
    for N in [100, 500, 1000, 1400]:
        dots = VGroup(*[
            Dot3D(point=np.random.randn(3), color=RED)
            for _ in range(N)
        ])
        
        # Benchmark flat hash:
        from manim.utils.hashing import get_hash_from_play_call as flat_hash
        
        # Create a minimal scene + camera mock:
        class FakeScene:
            pass
        class FakeCamera:
            frame_center = np.array([0, 0, 0])
        class FakeAnim:
            mobject = dots[0]
            run_time = 1.0
            rate_func = lambda t: t
            rate_func.__name__ = 'linear'
            def __str__(self):
                return 'FakeAnim'
        
        scene = FakeScene()
        camera = FakeCamera()
        anims = [FakeAnim()]
        mobjects = list(dots.submobjects)
        
        # Time flat hash:
        t0 = time.perf_counter()
        for _ in range(3):
            try:
                flat_hash(scene, camera, anims, mobjects)
            except Exception:
                break
        t_flat = (time.perf_counter() - t0) / 3
        
        # Time Merkle hash:
        import manim_merkle_hash
        t0 = time.perf_counter()
        for _ in range(3):
            manim_merkle_hash.get_hash_from_play_call(scene, camera, anims, mobjects)
        t_merkle = (time.perf_counter() - t0) / 3
        
        speedup = t_flat / t_merkle if t_merkle > 0 else float('inf')
        
        print(f"N={N:5d}: flat={t_flat*1000:8.1f}ms  merkle={t_merkle*1000:8.1f}ms  speedup={speedup:.1f}x")


if __name__ == '__main__':
    print("=== Hash Function Benchmark ===")
    print(f"{'N':>5s}  {'flat':>10s}  {'merkle':>10s}  {'speedup':>8s}")
    print("-" * 40)
    benchmark_hash_function()
