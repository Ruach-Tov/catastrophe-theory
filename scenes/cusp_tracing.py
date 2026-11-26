"""
Whitney's Cusp Singularity — animated with tracing.

y₁ = x₁³ + x₁x₂, y₂ = x₂

A horizontal line sweeps downward in x₂ (the parameter direction).
For x₂ > 0: the mapping is one-to-one (1 pre-image everywhere).
At x₂ = 0: the cusp forms (3 pre-images coalesce at the origin).
For x₂ < 0: the cusp curve encloses a region with 3 pre-images.

The animation shows: as x₂ decreases, a single projected point
SPLITS into three — the birth of the cusp singularity.

Reference: Arnol'd, Catastrophe Theory, Ch. 2
           Whitney, "On singularities of mappings of Euclidean spaces," 1955
"""

from manim import *
import numpy as np


class CuspTracing(ThreeDScene):
    """The cusp singularity with animated parameter sweep."""

    def construct(self):
        # Title
        title = Text("Whitney's Cusp Singularity", font_size=36)
        subtitle = MathTex(r"y_1 = x_1^3 + x_1 x_2, \quad y_2 = x_2", font_size=28)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        self.set_camera_orientation(phi=65 * DEGREES, theta=-40 * DEGREES)

        # === The surface ===
        # Plot in (y₁, y₂, x₁) space: (x₁³ + x₁·x₂, x₂, x₁)
        surface = Surface(
            lambda u, v: np.array([u**3 + u * v, v, u]),
            u_range=[-1.3, 1.3],
            v_range=[-2.5, 1.0],
            resolution=(40, 30),
            fill_opacity=0.4,
            stroke_width=0.3,
        )
        surface.set_color_by_gradient(BLUE_B, PURPLE_B)

        # The projection plane (z = 0, i.e., the (y₁, y₂) plane)
        plane = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 1.0],
            resolution=(10, 10),
            fill_opacity=0.08,
            stroke_width=0.2,
            stroke_color=GREY,
        )

        # Axes
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5], y_range=[-2.5, 1.5], z_range=[-1.5, 1.5],
            x_length=6, y_length=4, z_length=3,
        )

        self.play(Create(axes), Create(plane), run_time=1)
        self.play(Create(surface), run_time=2)

        # The cusp curve on the projection plane:
        # Parametric: (y₁, y₂) = (-2t³, -3t²) for t ∈ [-0.9, 0.9]
        cusp_curve = ParametricFunction(
            lambda t: np.array([-2 * t**3, -3 * t**2, 0]),
            t_range=[-0.9, 0.9],
            color=RED,
            stroke_width=3,
        )
        self.play(Create(cusp_curve))

        cusp_label = Text("cusp curve", font_size=16, color=RED)
        self.add_fixed_in_frame_mobjects(cusp_label)
        cusp_label.to_corner(UR)
        self.play(Write(cusp_label))
        self.wait(1)

        # === Sweep: a horizontal line at fixed x₂ moves downward ===
        # At each x₂, the mapping x₁ → y₁ = x₁³ + x₁·x₂ is a cubic.
        # For x₂ > 0: monotone (1 real root for each y₁) → 1 pre-image
        # For x₂ < 0: has local max and min → 3 real roots for some y₁ → 3 pre-images

        x2_param = ValueTracker(0.8)  # start above the cusp

        # For a given x₂, solve x₁³ + x₁·x₂ = 0 at y₁=0 to find the pre-images
        # At y₁=0: x₁(x₁² + x₂) = 0 → x₁=0 always; x₁=±√(-x₂) if x₂ < 0

        # Draw a horizontal slice on the surface at current x₂
        def make_surface_slice(x2):
            return ParametricFunction(
                lambda u: np.array([u**3 + u * x2, x2, u]),
                t_range=[-1.3, 1.3],
                color=YELLOW,
                stroke_width=2,
            )

        # And its projection on the plane
        def make_proj_slice(x2):
            return ParametricFunction(
                lambda u: np.array([u**3 + u * x2, x2, 0]),
                t_range=[-1.3, 1.3],
                color=YELLOW,
                stroke_width=2,
            )

        surface_slice = always_redraw(lambda: make_surface_slice(x2_param.get_value()))
        proj_slice = always_redraw(lambda: make_proj_slice(x2_param.get_value()))

        # A marker point at x₁=0 on both surface and plane
        marker_sphere = always_redraw(lambda: Dot3D(
            point=np.array([0, x2_param.get_value(), 0]),
            color=YELLOW, radius=0.06,
        ))
        marker_plane = always_redraw(lambda: Dot3D(
            point=np.array([0, x2_param.get_value(), 0]),
            color=YELLOW, radius=0.06,
        ))

        self.play(Create(surface_slice), Create(proj_slice),
                  Create(marker_sphere), Create(marker_plane))

        # Annotation for phase 1: above the cusp
        note_above = Text("x₂ > 0: one-to-one\n(1 pre-image everywhere)", font_size=14)
        self.add_fixed_in_frame_mobjects(note_above)
        note_above.to_corner(DL)
        self.play(Write(note_above))

        # Sweep down: x₂ from 0.8 → 0 (approaching the cusp point)
        self.play(
            x2_param.animate.set_value(0.05),
            run_time=3,
            rate_func=linear,
        )
        self.play(FadeOut(note_above))

        # At x₂ ≈ 0: the cusp point
        note_cusp = Text("x₂ = 0: the cusp point\n(3 pre-images coalesce)", font_size=14, color=RED)
        self.add_fixed_in_frame_mobjects(note_cusp)
        note_cusp.to_corner(DL)
        self.play(Write(note_cusp))
        self.play(x2_param.animate.set_value(0), run_time=1)
        self.wait(1)
        self.play(FadeOut(note_cusp))

        # Sweep below: x₂ from 0 → -2 (inside the cusp)
        note_below = Text(
            "x₂ < 0: the cubic folds\n"
            "→ 3 pre-images inside the cusp curve\n"
            "→ the projection self-intersects",
            font_size=14,
        )
        self.add_fixed_in_frame_mobjects(note_below)
        note_below.to_corner(DL)
        self.play(Write(note_below))

        self.play(
            x2_param.animate.set_value(-2.0),
            run_time=4,
            rate_func=linear,
        )
        self.wait(1)
        self.play(FadeOut(note_below))

        # === Rotate to show the fold structure ===
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(4)
        self.stop_ambient_camera_rotation()

        # Final annotation
        final_note = Text(
            "The cusp is the second atom of singularity.\n"
            "Every generic singularity splits into\n"
            "folds and cusps (Whitney, 1955).",
            font_size=14,
        )
        self.add_fixed_in_frame_mobjects(final_note)
        final_note.to_corner(DR)
        self.play(Write(final_note))
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
