"""
Arnol'd Figure 1 — The Fold Singularity via Sphere Projection.

A point traces along the sphere (x₁ direction), and its projection
onto the plane below traces the fold. Then the coordinate system
morphs: y₁ → r (radial), showing the "suitable change of coordinates"
Arnol'd describes.

Reference: Arnol'd, Catastrophe Theory, Ch. 2, Figure 1
"""

from manim import *
import numpy as np


class ArnoldFigure1(ThreeDScene):
    """The sphere projection fold, with coordinate morphing."""

    def construct(self):
        # Title
        title = Text("Arnol'd, Figure 1", font_size=36)
        subtitle = Text("The fold singularity — sphere projected to plane", font_size=22)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(Write(title), Write(subtitle))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Set up 3D
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)

        # === PHASE 1: The sphere and its projection ===

        # Draw a hemisphere (the visible half)
        sphere = Surface(
            lambda u, v: np.array([
                np.cos(u) * np.cos(v),
                np.sin(u) * np.cos(v),
                np.sin(v) + 1.5,  # lift it up
            ]),
            u_range=[0, TAU],
            v_range=[-PI / 2, PI / 2],
            resolution=(40, 20),
            fill_opacity=0.3,
            stroke_width=0.5,
        )
        sphere.set_color_by_gradient(BLUE_B, BLUE_D)

        # The projection plane (z = 0)
        plane = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-1.8, 1.8],
            v_range=[-1.8, 1.8],
            resolution=(10, 10),
            fill_opacity=0.1,
            stroke_width=0.3,
            stroke_color=GREY,
        )

        # The equator (fold line on the sphere, at v=0)
        equator = ParametricFunction(
            lambda t: np.array([np.cos(t), np.sin(t), 1.5]),
            t_range=[0, TAU],
            color=RED,
            stroke_width=3,
        )

        # The projection of the equator (unit circle on the plane)
        equator_proj = ParametricFunction(
            lambda t: np.array([np.cos(t), np.sin(t), 0]),
            t_range=[0, TAU],
            color=RED,
            stroke_width=3,
            stroke_opacity=0.6,
        )

        self.play(Create(plane), run_time=1)
        self.play(Create(sphere), run_time=2)
        self.play(Create(equator), Create(equator_proj))
        self.wait(1)

        # Label the fold
        fold_label = Text("fold (equator)", font_size=18, color=RED)
        self.add_fixed_in_frame_mobjects(fold_label)
        fold_label.to_corner(UR)
        self.play(Write(fold_label))

        # === PHASE 2: Tracing point along x₁ ===

        # A point that moves along a meridian (great circle in x₁ direction)
        # Parametrize: start at north pole, trace down over equator to south
        trace_param = ValueTracker(-PI / 2 + 0.1)

        # The point on the sphere
        point_sphere = always_redraw(lambda: Dot3D(
            point=np.array([
                np.cos(0) * np.cos(trace_param.get_value()),
                np.sin(0) * np.cos(trace_param.get_value()),
                np.sin(trace_param.get_value()) + 1.5,
            ]),
            color=YELLOW,
            radius=0.08,
        ))

        # Its projection on the plane
        point_proj = always_redraw(lambda: Dot3D(
            point=np.array([
                np.cos(0) * np.cos(trace_param.get_value()),
                np.sin(0) * np.cos(trace_param.get_value()),
                0,
            ]),
            color=YELLOW,
            radius=0.06,
        ))

        # The projection line (vertical dashed)
        proj_line = always_redraw(lambda: DashedLine(
            start=np.array([
                np.cos(0) * np.cos(trace_param.get_value()),
                np.sin(0) * np.cos(trace_param.get_value()),
                np.sin(trace_param.get_value()) + 1.5,
            ]),
            end=np.array([
                np.cos(0) * np.cos(trace_param.get_value()),
                np.sin(0) * np.cos(trace_param.get_value()),
                0,
            ]),
            color=YELLOW_A,
            stroke_width=1,
        ))

        self.play(Create(point_sphere), Create(point_proj), Create(proj_line))

        # Trace from north pole down to south pole
        # The projection moves inward (toward center) as the point
        # crosses the equator, then back out — the FOLD
        self.play(
            trace_param.animate.set_value(PI / 2 - 0.1),
            run_time=6,
            rate_func=linear,
        )
        self.wait(1)

        # Annotation: the projection reverses at the equator
        note1 = Text(
            "At the equator: projection reverses\n"
            "→ two points on sphere map to one on plane\n"
            "→ this is the fold singularity",
            font_size=14,
        )
        self.add_fixed_in_frame_mobjects(note1)
        note1.to_corner(DL)
        self.play(Write(note1))
        self.wait(2)
        self.play(FadeOut(note1))

        # === PHASE 3: Coordinate morphing y₁ → r ===

        # Fade the 3D sphere, focus on the projection plane
        self.play(
            FadeOut(sphere), FadeOut(equator), FadeOut(point_sphere),
            FadeOut(proj_line),
            self.camera.animate.set_euler_angles(phi=0, theta=-PI / 2),
            run_time=2,
        )

        # Now we're looking straight down at the plane
        # The equator projection is a circle — in Cartesian (y₁, y₂)
        # Arnol'd says: change coordinates to r, θ

        coord_label_cart = MathTex(r"(y_1, y_2)", font_size=28, color=WHITE)
        self.add_fixed_in_frame_mobjects(coord_label_cart)
        coord_label_cart.to_corner(UL)
        self.play(Write(coord_label_cart))
        self.wait(1)

        # Morph label: (y₁, y₂) → (r, θ)
        coord_label_polar = MathTex(r"(r, \theta)", font_size=28, color=GREEN)
        self.add_fixed_in_frame_mobjects(coord_label_polar)
        coord_label_polar.to_corner(UL)

        # Add radial lines to suggest polar coordinates:
        radial_lines = VGroup()
        for angle in np.linspace(0, TAU, 12, endpoint=False):
            line = Line(
                start=np.array([0, 0, 0.01]),
                end=np.array([1.5 * np.cos(angle), 1.5 * np.sin(angle), 0.01]),
                color=GREEN,
                stroke_width=1,
                stroke_opacity=0.4,
            )
            radial_lines.add(line)

        # Concentric circles for r:
        r_circles = VGroup()
        for r in [0.3, 0.6, 0.9, 1.2]:
            circ = ParametricFunction(
                lambda t, r=r: np.array([r * np.cos(t), r * np.sin(t), 0.01]),
                t_range=[0, TAU],
                color=GREEN,
                stroke_width=1,
                stroke_opacity=0.3,
            )
            r_circles.add(circ)

        self.play(
            Transform(coord_label_cart, coord_label_polar),
            Create(radial_lines),
            Create(r_circles),
            run_time=2,
        )

        # Mark r = 1 as the fold (the equator projection)
        r_label = MathTex(r"r = 1 \text{ (fold)}", font_size=20, color=RED)
        self.add_fixed_in_frame_mobjects(r_label)
        r_label.next_to(equator_proj, RIGHT)
        self.play(Write(r_label))

        # Final annotation
        final_note = Text(
            "In polar coordinates (r, θ):\n"
            "the fold is simply r = 1\n"
            "y₁ = x₁² becomes the normal form",
            font_size=16,
        )
        self.add_fixed_in_frame_mobjects(final_note)
        final_note.to_corner(DR)
        self.play(Write(final_note))
        self.wait(3)

        # Clean exit
        self.play(*[FadeOut(mob) for mob in self.mobjects])
