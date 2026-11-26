"""
Whitney's Cusp Singularity — the second atom of catastrophe theory.

y₁ = x₁³ + x₁x₂, y₂ = x₂

Three inverse images coalesce at the cusp point. The semi-cubic
parabola y₁² = (4/27)y₂³ bounds the region with three pre-images.

In neural networks: where multiple ReLU folds meet, cusps form
at the junction of decision boundaries. These are the structurally
stable features of the activation landscape.

Reference: Arnol'd, Catastrophe Theory, Ch. 2 (Whitney's Singularity Theory)
"""

from manim import *
import numpy as np


class CuspSingularity(ThreeDScene):
    """The cusp: y₁ = x₁³ + x₁x₂, y₂ = x₂."""

    def construct(self):
        title = Text("Whitney's Cusp Singularity", font_size=36)
        subtitle = MathTex(r"y_1 = x_1^3 + x_1 x_2, \quad y_2 = x_2", font_size=28)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)

        # The cusp surface: (x₁, x₂) → (x₁³ + x₁x₂, x₂, x₁)
        surface = Surface(
            lambda u, v: np.array([u**3 + u * v, v, u]),
            u_range=[-1.5, 1.5],
            v_range=[-2, 1],
            resolution=(40, 30),
            fill_opacity=0.6,
        )
        surface.set_color_by_gradient(PURPLE, ORANGE)

        # The cusp curve in the (y₁, y₂) plane:
        # Critical set: 3x₁² + x₂ = 0 → x₂ = -3x₁²
        # Image: y₁ = x₁³ + x₁(-3x₁²) = -2x₁³, y₂ = -3x₁²
        # Parametric: (y₁, y₂) = (-2t³, -3t²)
        cusp_curve = ParametricFunction(
            lambda t: np.array([-2 * t**3, -3 * t**2, 0]),
            t_range=[-0.8, 0.8],
            color=RED,
            stroke_width=4,
        )

        axes = ThreeDAxes(
            x_range=[-3, 3], y_range=[-3, 1], z_range=[-2, 2],
            x_length=6, y_length=4, z_length=4,
        )

        self.play(Create(axes))
        self.play(Create(surface), run_time=3)
        self.play(Create(cusp_curve))

        # Rotate
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        note = Text(
            "Inside the cusp: 3 pre-images\nOutside: 1 pre-image\nOn the curve: 2 coalesce",
            font_size=16,
        )
        self.add_fixed_in_frame_mobjects(note)
        note.to_corner(DR)
        self.play(Write(note))
        self.wait(3)
