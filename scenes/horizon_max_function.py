"""
Arnol'd Figure 47 (1e) / Figure 50 (3e) — The Maximum Function as a Horizon.

F(y) = max_x f(x, y)

"Let y be the azimuth of the line of vision, x be the distance and f be 
the angle of elevation of the landscape at distance x in the azimuth 
direction y. Then F determines the line of the horizon."

The animation:
  1. A topographic landscape (two hills) in 3D
  2. Rotate to show it as a projection (Arnol'd's perspective)
  3. Split: main view rotates to overhead (contours appear),
     a clone slides to lower-left showing the horizon projection
  4. A surveyor's ray sweeps across azimuths, projecting onto 
     the ridge line — the maximum function in action

Reference: Arnol'd, Catastrophe Theory, Ch. 10
           "Singularities in Optimization Problems: the Maximum Function"
"""

from manim import *
import numpy as np


def landscape(x, y):
    """Two hills: a smooth landscape function f(x, y)."""
    # Hill 1: centered at (-0.5, 0.3)
    h1 = 1.8 * np.exp(-((x + 0.5)**2 + (y - 0.3)**2) / 0.4)
    # Hill 2: centered at (0.6, -0.2), slightly taller
    h2 = 2.2 * np.exp(-((x - 0.6)**2 + (y + 0.2)**2) / 0.3)
    # Gentle rolling baseline
    base = 0.3 * np.sin(x * 0.5) * np.cos(y * 0.7)
    return h1 + h2 + base


def horizon_at_azimuth(y_val, x_range=(-2, 2), n=200):
    """The maximum function: F(y) = max_x f(x, y).
    Returns (max_height, argmax_x)."""
    xs = np.linspace(x_range[0], x_range[1], n)
    fs = np.array([landscape(x, y_val) for x in xs])
    idx = np.argmax(fs)
    return fs[idx], xs[idx]


class HorizonMaxFunction(ThreeDScene):
    """Arnol'd's horizon line as the maximum function."""

    def construct(self):
        # Title
        title = Text("Arnol'd, Figure 47", font_size=36)
        subtitle = MathTex(r"F(y) = \max_x f(x, y)", font_size=28)
        subtitle2 = Text("The horizon is a maximum function", font_size=20)
        subtitle.next_to(title, DOWN, buff=0.3)
        subtitle2.next_to(subtitle, DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(title, subtitle, subtitle2)
        self.play(Write(title), Write(subtitle), Write(subtitle2))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(subtitle2))

        # === PHASE 1: The landscape in 3D ===
        self.set_camera_orientation(phi=55 * DEGREES, theta=-35 * DEGREES)

        terrain = Surface(
            lambda u, v: np.array([u, v, landscape(u, v)]),
            u_range=[-2, 2],
            v_range=[-1.5, 1.5],
            resolution=(60, 40),
            fill_opacity=0.7,
            stroke_width=0.3,
            checkerboard_colors=[GREEN_D, GREEN_E],
        )

        axes = ThreeDAxes(
            x_range=[-2.5, 2.5], y_range=[-2, 2], z_range=[-0.5, 3],
            x_length=6, y_length=4, z_length=3,
        )
        x_label = MathTex("x", font_size=22).move_to(axes.c2p(2.5, 0, 0) + RIGHT * 0.3)
        y_label = MathTex("y", font_size=22).move_to(axes.c2p(0, 2, 0) + UP * 0.3)
        z_label = MathTex("f(x,y)", font_size=18).move_to(axes.c2p(0, 0, 3) + UP * 0.3)

        self.play(Create(axes), run_time=1)
        self.play(Create(terrain), run_time=3)

        label_note = Text("Two hills — a landscape", font_size=16)
        self.add_fixed_in_frame_mobjects(label_note)
        label_note.to_corner(DL)
        self.play(Write(label_note))
        self.wait(1)

        # Slow rotation to appreciate the 3D shape
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(4)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(label_note))

        # === PHASE 2: The surveyor's view ===
        # Rotate to Arnol'd's perspective: looking along x (distance),
        # y is azimuth (left-right), f is elevation (up)

        survey_note = Text(
            "The surveyor looks along x (distance)\n"
            "y = azimuth, f = elevation\n"
            "The horizon = max elevation at each azimuth",
            font_size=14,
        )
        self.add_fixed_in_frame_mobjects(survey_note)
        survey_note.to_corner(DL)
        self.play(Write(survey_note))

        # Rotate to side view: looking along x-axis
        self.move_camera(phi=80 * DEGREES, theta=0 * DEGREES, run_time=3)
        self.wait(2)
        self.play(FadeOut(survey_note))

        # === PHASE 3: The horizon line ===
        # Draw the horizon: F(y) = max_x f(x, y) for each y

        # Compute the horizon curve
        y_vals = np.linspace(-1.5, 1.5, 100)
        horizon_points = []
        for y_val in y_vals:
            max_h, _ = horizon_at_azimuth(y_val)
            horizon_points.append(np.array([0, y_val, max_h]))

        # The horizon as a thick curve on the x=0 plane (the "screen" the surveyor sees)
        horizon_curve = VMobject(stroke_color=RED, stroke_width=4)
        horizon_curve.set_points_smoothly(horizon_points)

        horizon_label = Text("the horizon F(y)", font_size=16, color=RED)
        self.add_fixed_in_frame_mobjects(horizon_label)
        horizon_label.to_corner(UR)

        self.play(Create(horizon_curve), Write(horizon_label), run_time=3)
        self.wait(1)

        # === PHASE 4: Sweeping surveyor's ray ===
        # A ray from the surveyor (at x=-2) sweeps across azimuths
        # At each azimuth, it finds the maximum — the horizon point

        azimuth = ValueTracker(-1.4)

        # The ray: a line from x=-2 to the argmax point at current azimuth
        def make_ray():
            y_val = azimuth.get_value()
            max_h, max_x = horizon_at_azimuth(y_val)
            return Line(
                start=np.array([-2, y_val, 0]),
                end=np.array([max_x, y_val, max_h]),
                color=YELLOW,
                stroke_width=2,
            )

        # The horizon point (where the ray touches the ridge)
        def make_horizon_dot():
            y_val = azimuth.get_value()
            max_h, _ = horizon_at_azimuth(y_val)
            return Dot3D(
                point=np.array([0, y_val, max_h]),
                color=YELLOW,
                radius=0.06,
            )

        # The landscape point (actual peak the ray hits)
        def make_peak_dot():
            y_val = azimuth.get_value()
            max_h, max_x = horizon_at_azimuth(y_val)
            return Dot3D(
                point=np.array([max_x, y_val, max_h]),
                color=YELLOW_A,
                radius=0.05,
            )

        ray = always_redraw(make_ray)
        horizon_dot = always_redraw(make_horizon_dot)
        peak_dot = always_redraw(make_peak_dot)

        ray_note = Text(
            "The surveyor's ray sweeps across azimuths.\n"
            "At each y, it finds the maximum elevation.\n"
            "The ridge line = the horizon.",
            font_size=14,
        )
        self.add_fixed_in_frame_mobjects(ray_note)
        ray_note.to_corner(DL)
        self.play(Write(ray_note))

        self.play(Create(ray), Create(horizon_dot), Create(peak_dot))

        # Sweep the ray across all azimuths
        self.play(
            azimuth.animate.set_value(1.4),
            run_time=6,
            rate_func=linear,
        )
        self.wait(1)
        self.play(FadeOut(ray_note))

        # === PHASE 5: The key insight ===
        insight = Text(
            "The horizon is CONTINUOUS but NOT SMOOTH\n"
            "— even though the landscape is smooth.\n"
            "The breaks in the horizon are\n"
            "structurally stable singularities.",
            font_size=14,
        )
        self.add_fixed_in_frame_mobjects(insight)
        insight.to_corner(DL)
        self.play(Write(insight))

        # Highlight the break in the horizon (where hills exchange dominance)
        # Sweep back slowly to show the transition
        self.play(
            azimuth.animate.set_value(-1.4),
            run_time=4,
            rate_func=linear,
        )
        self.wait(2)

        final = Text(
            "ReLU(x) = max(0, x) is this same function.\n"
            "Neural networks compute compositions\n"
            "of maximum functions — horizons of horizons.",
            font_size=14,
            color=YELLOW,
        )
        self.add_fixed_in_frame_mobjects(final)
        final.to_corner(DR)
        self.play(Write(final))
        self.wait(3)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
