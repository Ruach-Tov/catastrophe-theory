"""
Arnol'd Figure 29 — Caustics: wavefront propagation and ray concentration.

A wavefront propagates from a curved boundary. Rays (normals to the
wavefront) converge where the boundary curves. The CAUSTIC is the
envelope of the ray family — the bright line where rays concentrate.

The caustic is a fold singularity of the ray map: two rays arrive
at the same point. This is the swimming pool pattern — sunlight
refracting through wavy water creates a network of bright caustic
curves on the pool floor.

Reference: Arnol'd, Catastrophe Theory, Ch. 6 (Caustics, Wave Fronts,
           and Their Metamorphoses)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import manim_merkle_hash
manim_merkle_hash.install()

from ruach_manim import reading_time
from manim import *
import numpy as np


class ArnoldFigure29(Scene):
    """Wavefront propagation with caustic formation."""

    def construct(self):
        title = Text("Arnol'd Fig 29 — Caustics", font_size=32)
        subtitle = Text("Where rays concentrate, light burns bright", font_size=18, color=GREY)
        subtitle.next_to(title, DOWN)
        self.play(Write(title), Write(subtitle))
        self.wait(reading_time("Caustics where rays concentrate"))
        self.play(FadeOut(title), FadeOut(subtitle))

        # === The curved boundary (source of waves) ===
        # A concave curve — waves emanating inward will converge

        def boundary(t):
            """Curved boundary: a parabolic reflector."""
            return np.array([t, 0.3 * t**2 - 2.5, 0])

        boundary_curve = ParametricFunction(
            boundary, t_range=[-3, 3], color=WHITE, stroke_width=3,
        )

        self.play(Create(boundary_curve), run_time=1)

        note1 = Text("A curved boundary — waves propagate inward", font_size=14)
        note1.to_corner(DL)
        self.play(Write(note1))
        self.wait(1)
        self.play(FadeOut(note1))

        # === Rays: normals to the boundary ===
        N_RAYS = 25
        t_values = np.linspace(-2.5, 2.5, N_RAYS)

        def boundary_normal(t):
            """Inward-pointing unit normal to the boundary."""
            # Tangent: (1, 0.6t, 0)
            dx, dy = 1.0, 0.6 * t
            norm = np.sqrt(dx**2 + dy**2)
            # Normal (rotated 90° inward = toward positive y):
            nx, ny = -dy / norm, dx / norm
            return np.array([nx, ny, 0])

        # Draw rays from boundary points along normals:
        rays = VGroup()
        RAY_LENGTH = 5.0

        for t in t_values:
            start = boundary(t)
            normal = boundary_normal(t)
            end = start + normal * RAY_LENGTH
            ray = Line(start, end, stroke_color=YELLOW_A, stroke_width=0.8, stroke_opacity=0.4)
            rays.add(ray)

        self.play(Create(rays), run_time=2)

        # === The caustic: envelope of the ray family ===
        # For boundary y = 0.3x² - 2.5, the caustic is the evolute.
        # Parametric caustic: center of curvature as function of t.
        #
        # y'(x) = 0.6x, y''(x) = 0.6
        # Radius of curvature R = (1 + y'²)^(3/2) / |y''|
        # Center of curvature = point + R * normal

        def caustic_point(t):
            pos = boundary(t)
            dx, dy = 1.0, 0.6 * t
            ddx, ddy = 0.0, 0.6
            speed_sq = dx**2 + dy**2
            speed = np.sqrt(speed_sq)
            # Curvature: κ = |x'y'' - y'x''| / (x'² + y'²)^(3/2)
            kappa = abs(dx * ddy - dy * ddx) / speed_sq**1.5
            if kappa < 1e-8:
                return pos + boundary_normal(t) * 50  # nearly straight, caustic at infinity
            R = 1.0 / kappa
            normal = boundary_normal(t)
            return pos + normal * R

        # Draw the caustic curve:
        caustic_t = np.linspace(-2.2, 2.2, 200)
        caustic_points = [caustic_point(t) for t in caustic_t]
        # Filter out points that go off-screen:
        caustic_points = [p for p in caustic_points if abs(p[0]) < 5 and abs(p[1]) < 4]

        if len(caustic_points) > 2:
            caustic_curve = VMobject(stroke_color=RED, stroke_width=4)
            caustic_curve.set_points_smoothly(caustic_points)

            caustic_label = Text("caustic", font_size=16, color=RED)
            # Place label near the cusp of the caustic:
            mid = caustic_points[len(caustic_points) // 2]
            caustic_label.next_to(mid, RIGHT, buff=0.3)

            note2 = Text("The CAUSTIC: where rays concentrate\n(the envelope of the ray family)", font_size=13)
            note2.to_corner(DL)
            self.play(Write(note2))
            self.play(Create(caustic_curve), Write(caustic_label), run_time=2)
            self.wait(reading_time("The caustic where rays concentrate the envelope of the ray family"))
            self.play(FadeOut(note2))

        # === Wavefronts propagating ===
        # Show successive wavefronts (equidistant curves from the boundary)
        # moving inward, deforming as they approach the caustic

        note3 = Text("Wavefronts propagate inward.\nAt the caustic, the wavefront develops a cusp.", font_size=13)
        note3.to_corner(DL)
        self.play(Write(note3))

        for dist in [0.5, 1.0, 1.5, 2.0, 2.5]:
            wf_points = []
            for t in np.linspace(-2.5, 2.5, 100):
                pos = boundary(t)
                normal = boundary_normal(t)
                wf_pt = pos + normal * dist
                if abs(wf_pt[0]) < 5 and abs(wf_pt[1]) < 4:
                    wf_points.append(wf_pt)

            if len(wf_points) > 2:
                wf = VMobject(stroke_color=BLUE_B, stroke_width=1.5, stroke_opacity=0.6)
                wf.set_points_smoothly(wf_points)
                self.play(Create(wf), run_time=0.5)

        self.play(FadeOut(note3))
        self.wait(1)

        # === Final insight ===
        final_text = (
            "The caustic is a fold singularity.\n"
            "Two rays arrive at the same point —\n"
            "the same geometry as Whitney's fold.\n\n"
            "Swimming pool light, whispering galleries,\n"
            "rainbow arcs — all are caustics.\n"
            "All are folds."
        )
        final = Text(final_text, font_size=13, color=YELLOW)
        final.to_corner(DR)
        self.play(Write(final))
        self.wait(reading_time(final_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])
