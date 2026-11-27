"""
Geodesic Globe — Arnol'd Figure 1 with tessellated Earth in manim.

A geodesic sphere (320 triangular tiles, continent-colored) hovers
above a projection plane. The tiles project down to the plane,
creating the fold singularity where near and far continents overlap.

Like arnold_figure1.py but with real geographic data on a board-game globe.

Reference: Arnol'd, Catastrophe Theory, Ch. 2, Figure 1
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import manim_merkle_hash
manim_merkle_hash.install()

from ruach_manim import RuachScene, attribution, reading_time
from manim import *
import numpy as np

# Import the geodesic builder:
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples'))
from geodesic_globe import build_geodesic_globe, CONTINENT_COLORS, OCEAN_COLOR


def color_from_rgb(rgb):
    return ManimColor(rgb)


class GeodesicFigure1(ThreeDScene):
    """Arnol'd Figure 1 with a tessellated geodesic Earth."""

    def construct(self):
        title = Text("Arnol'd Figure 1 — Geodesic Earth", font_size=32)
        subtitle = Text("320 tiles project to a plane — the fold at the limb", font_size=18)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(Write(title), Write(subtitle))
        self.wait(reading_time("Arnol'd Figure 1 Geodesic Earth 320 tiles project to a plane the fold at the limb"))
        self.play(FadeOut(title), FadeOut(subtitle))

        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)

        # Build the geodesic globe (level 1 = 80 faces for performance):
        verts, faces, cell_data = build_geodesic_globe(level=1)

        # === Projection plane at z = -2 ===
        plane = Surface(
            lambda u, v: np.array([u, v, -2]),
            u_range=[-1.5, 1.5],
            v_range=[-1.5, 1.5],
            resolution=(6, 6),
            fill_opacity=0.06,
            stroke_width=0.2,
            stroke_color=GREY,
        )
        limb = ParametricFunction(
            lambda t: np.array([np.cos(t), np.sin(t), -2]),
            t_range=[0, TAU],
            color=RED,
            stroke_width=2,
        )

        self.play(Create(plane), Create(limb), run_time=1)

        # === Build the globe as triangular polygons ===
        globe_tris = VGroup()
        proj_tris_near = VGroup()
        proj_tris_far = VGroup()

        for (a, b, c), data in zip(faces, cell_data):
            va, vb, vc = verts[a], verts[b], verts[c]
            rgb = data['color']

            # Sphere triangle:
            tri = Polygon(
                va, vb, vc,
                fill_color=rgb_to_color(rgb),
                fill_opacity=0.8,
                stroke_color=GREY,
                stroke_width=0.3,
            )
            globe_tris.add(tri)

            # Projection: drop z, keep x,y, place at z=-2
            # Centroid determines near/far:
            centroid = (va + vb + vc) / 3
            is_near = centroid[2] > 0  # z > 0 = facing camera initially

            proj_tri = Polygon(
                np.array([va[0], va[1], -2]),
                np.array([vb[0], vb[1], -2]),
                np.array([vc[0], vc[1], -2]),
                fill_color=rgb_to_color(rgb),
                stroke_color=GREY,
                stroke_width=0.2,
            )

            if is_near:
                proj_tri.set_fill(opacity=0.7)
                proj_tris_near.add(proj_tri)
            else:
                proj_tri.set_fill(opacity=0.12)
                proj_tris_far.add(proj_tri)

        # === Phase 1: Show the globe ===
        self.play(Create(globe_tris), run_time=3)
        self.wait(1)

        # === Phase 2: Project to the plane ===
        note1_text = "Projecting tiles to the plane..."
        note1 = Text(note1_text, font_size=14)
        self.add_fixed_in_frame_mobjects(note1)
        note1.to_corner(DL)
        self.play(Write(note1))

        # Far side first (light), then near side (heavy):
        self.play(Create(proj_tris_far), run_time=1)
        self.play(Create(proj_tris_near), run_time=1.5)
        self.play(FadeOut(note1))

        # === Phase 3: Annotate the fold ===
        fold_text = (
            "At the limb: near and far tiles overlap.\n"
            "The projection maps two tiles to one region.\n"
            "Continent labels collide — information is lost."
        )
        fold_note = Text(fold_text, font_size=12)
        self.add_fixed_in_frame_mobjects(fold_note)
        fold_note.to_corner(DL)
        self.play(Write(fold_note))
        self.wait(reading_time(fold_text))
        self.play(FadeOut(fold_note))

        # === Phase 4: Rotate to show the fold from different angles ===
        rotate_text = "As the view rotates, different continents\nenter and leave the fold."
        rotate_note = Text(rotate_text, font_size=14)
        self.add_fixed_in_frame_mobjects(rotate_note)
        rotate_note.to_corner(DL)
        self.play(Write(rotate_note))

        self.begin_ambient_camera_rotation(rate=0.25)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(rotate_note))

        # === Phase 5: Connection to UMAP ===
        final_text = (
            "Every dimensionality reduction is a projection.\n"
            "UMAP, PCA, t-SNE — all create folds\n"
            "where high-dimensional structure is lost.\n"
            "The geodesic globe makes the loss visible."
        )
        final = Text(final_text, font_size=13, color=YELLOW)
        self.add_fixed_in_frame_mobjects(final)
        final.to_corner(DR)
        self.play(Write(final))
        self.wait(reading_time(final_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])
