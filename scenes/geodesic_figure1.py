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

        # === Three projection planes (corner of a room) ===
        P = 2.0  # plane offset

        # XY plane (floor, z = -P):
        plane_xy = Surface(
            lambda u, v: np.array([u, v, -P]),
            u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
            resolution=(6, 6), fill_opacity=0.06,
            stroke_width=0.2, stroke_color=GREY,
        )
        limb_xy = ParametricFunction(
            lambda t: np.array([np.cos(t), np.sin(t), -P]),
            t_range=[0, TAU], color=RED, stroke_width=2,
        )

        # XZ plane (back wall, y = -P):
        plane_xz = Surface(
            lambda u, v: np.array([u, -P, v]),
            u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
            resolution=(6, 6), fill_opacity=0.06,
            stroke_width=0.2, stroke_color=GREY,
        )
        limb_xz = ParametricFunction(
            lambda t: np.array([np.cos(t), -P, np.sin(t)]),
            t_range=[0, TAU], color=RED_A, stroke_width=1.5,
        )

        # YZ plane (side wall, x = -P):
        plane_yz = Surface(
            lambda u, v: np.array([-P, u, v]),
            u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
            resolution=(6, 6), fill_opacity=0.06,
            stroke_width=0.2, stroke_color=GREY,
        )
        limb_yz = ParametricFunction(
            lambda t: np.array([-P, np.cos(t), np.sin(t)]),
            t_range=[0, TAU], color=RED_B, stroke_width=1.5,
        )

        self.play(
            Create(plane_xy), Create(limb_xy),
            Create(plane_xz), Create(limb_xz),
            Create(plane_yz), Create(limb_yz),
            run_time=1.5,
        )

        # === Build the globe and three projections ===
        globe_tris = VGroup()
        # XY projection (floor):
        proj_xy_near = VGroup()
        proj_xy_far = VGroup()
        # XZ projection (back wall):
        proj_xz_near = VGroup()
        proj_xz_far = VGroup()
        # YZ projection (side wall):
        proj_yz_near = VGroup()
        proj_yz_far = VGroup()

        for (a, b, c), data in zip(faces, cell_data):
            va, vb, vc = verts[a], verts[b], verts[c]
            rgb = data['color']
            col = rgb_to_color(rgb)
            centroid = (va + vb + vc) / 3

            # Sphere triangle:
            tri = Polygon(va, vb, vc,
                fill_color=col, fill_opacity=0.8,
                stroke_color=GREY, stroke_width=0.3)
            globe_tris.add(tri)

            # XY projection (drop z → floor):
            near_z = centroid[2] > 0
            p = Polygon(
                np.array([va[0], va[1], -P]),
                np.array([vb[0], vb[1], -P]),
                np.array([vc[0], vc[1], -P]),
                fill_color=col, stroke_color=GREY, stroke_width=0.15)
            p.set_fill(opacity=0.6 if near_z else 0.1)
            (proj_xy_near if near_z else proj_xy_far).add(p)

            # XZ projection (drop y → back wall):
            near_y = centroid[1] > 0
            p = Polygon(
                np.array([va[0], -P, va[2]]),
                np.array([vb[0], -P, vb[2]]),
                np.array([vc[0], -P, vc[2]]),
                fill_color=col, stroke_color=GREY, stroke_width=0.15)
            p.set_fill(opacity=0.6 if near_y else 0.1)
            (proj_xz_near if near_y else proj_xz_far).add(p)

            # YZ projection (drop x → side wall):
            near_x = centroid[0] > 0
            p = Polygon(
                np.array([-P, va[1], va[2]]),
                np.array([-P, vb[1], vb[2]]),
                np.array([-P, vc[1], vc[2]]),
                fill_color=col, stroke_color=GREY, stroke_width=0.15)
            p.set_fill(opacity=0.6 if near_x else 0.1)
            (proj_yz_near if near_x else proj_yz_far).add(p)

        # === Phase 1: Show the globe ===
        self.play(Create(globe_tris), run_time=3)
        self.wait(1)

        # === Phase 2: Project to all three planes ===
        note1_text = "Projecting tiles to three planes..."
        note1 = Text(note1_text, font_size=14)
        self.add_fixed_in_frame_mobjects(note1)
        note1.to_corner(DL)
        self.play(Write(note1))

        # Far side first (light), then near side (heavy), all three planes:
        self.play(
            Create(proj_xy_far), Create(proj_xz_far), Create(proj_yz_far),
            run_time=1,
        )
        self.play(
            Create(proj_xy_near), Create(proj_xz_near), Create(proj_yz_near),
            run_time=1.5,
        )
        self.play(FadeOut(note1))

        # === Phase 3: Annotate the fold ===
        fold_text = (
            "Each plane shows a different fold.\n"
            "Each projection loses different information.\n"
            "Three views, three singularities, one globe."
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
