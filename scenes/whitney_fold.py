"""
Whitney's Fold Singularity — the first atom of catastrophe theory.

y₁ = x₁², y₂ = x₂

A parabolic sheet projected onto a plane. The fold line (the equator)
is where two inverse images coalesce into one. This singularity is
structurally stable — small perturbations can't remove it.

In neural networks: each ReLU creates a fold. The activation boundary
at z=0 is a fold singularity where the network transitions from
linear (z>0) to constant (z≤0).

Reference: Arnol'd, Catastrophe Theory, Ch. 2 (Whitney's Singularity Theory)
"""

from manim import *
import numpy as np


class FoldSingularity(ThreeDScene):
    """The fold: y₁ = x₁², y₂ = x₂, projected to the (y₁, y₂) plane."""

    def construct(self):
        # Title
        title = Text("Whitney's Fold Singularity", font_size=36)
        subtitle = MathTex(r"y_1 = x_1^2, \quad y_2 = x_2", font_size=28)
        subtitle.next_to(title, DOWN)
        
        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Set up 3D camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # The parabolic surface: (x₁, x₂) → (x₁², x₂, x₁)
        # We plot in (y₁, y₂, x₁) space to show the fold
        surface = Surface(
            lambda u, v: np.array([u**2, v, u]),
            u_range=[-1.5, 1.5],
            v_range=[-1.5, 1.5],
            resolution=(30, 30),
            fill_opacity=0.6,
        )
        surface.set_color_by_gradient(BLUE, GREEN)

        # The fold line (at x₁ = 0, the minimum of the parabola)
        fold_line = ParametricFunction(
            lambda t: np.array([0, t, 0]),
            t_range=[-1.5, 1.5],
            color=RED,
            stroke_width=4,
        )

        # Axes
        axes = ThreeDAxes(
            x_range=[-0.5, 2.5], y_range=[-2, 2], z_range=[-2, 2],
            x_length=5, y_length=4, z_length=4,
        )
        x_label = axes.get_x_axis_label(MathTex("y_1"))
        y_label = axes.get_y_axis_label(MathTex("y_2"))
        z_label = axes.get_z_axis_label(MathTex("x_1"))

        self.play(Create(axes), Write(x_label), Write(y_label), Write(z_label))
        self.play(Create(surface), run_time=3)
        self.play(Create(fold_line))

        # Annotation
        fold_label = Text("fold line", font_size=20, color=RED)
        fold_label.move_to(np.array([0, -2, 0.5]))
        self.add_fixed_in_frame_mobjects(fold_label)

        self.wait(1)

        # Rotate to show the projection
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        # Annotation: two pre-images above the fold, zero below
        note = Text(
            "Above the fold: 2 pre-images\nBelow the fold: 0 pre-images",
            font_size=18,
        )
        self.add_fixed_in_frame_mobjects(note)
        note.to_corner(DR)
        self.play(Write(note))
        self.wait(3)
