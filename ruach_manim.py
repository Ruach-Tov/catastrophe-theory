"""
ruach_manim — local extensions to manim for Ruach Tov research animations.

Idioms:
  - Attribution: every scene carries provenance (who, when, what paper)
  - Hash verification: animated objects can display their construction hash
  - Arnol'd conventions: standard colors for folds (red), cusps (red), 
    surfaces (blue-purple gradient), projection planes (grey), 
    tracing points (yellow), horizon/max curves (red)
  - Paired comparison: side-by-side scenes with matched parameters
  - Neural network overlays: show activation regions, silenced neurons,
    fold singularities in the decision boundary

Usage:
    from ruach_manim import RuachScene, ArnoldColors, attribution

    class MyScene(RuachScene):
        ATTRIBUTION = attribution(
            authors=["Heath Hunnicutt", "Mavchin"],
            reference="Arnol'd, Catastrophe Theory, Ch. 10",
            date="2026-11-26",
        )
        
        def construct(self):
            self.show_attribution()
            # ... your scene ...
"""

from manim import *
import numpy as np
from dataclasses import dataclass
from typing import List, Optional


# ─── Standard Colors (Arnol'd conventions) ───────────────

class ArnoldColors:
    """Color conventions for catastrophe theory animations."""
    FOLD = RED                    # fold lines, cusp curves
    CUSP = RED                    # cusp points
    SURFACE = [BLUE_B, PURPLE_B]  # surface gradient
    TERRAIN = [GREEN_D, GREEN_E]  # landscape surfaces
    PLANE = GREY                  # projection planes
    TRACE = YELLOW                # moving points, surveyor rays
    TRACE_LIGHT = YELLOW_A        # secondary traces
    HORIZON = RED                 # max function curves
    SINGULARITY = YELLOW          # singular points (dots)
    # Neural network extensions:
    ACTIVE = GREEN                # active neurons / regions
    SILENCED = RED_D              # dead/silenced neurons
    GATE = GOLD                   # one-way gate action
    RELU_POS = BLUE               # ReLU positive region
    RELU_NEG = GREY_D             # ReLU negative region (zero output)


# ─── Attribution ──────────────────────────────────────────

@dataclass
class Attribution:
    authors: List[str]
    reference: str
    date: str
    collective: str = "Ruach Tov Collective"
    note: Optional[str] = None


def attribution(**kwargs) -> Attribution:
    return Attribution(**kwargs)


# ─── Base Scene ───────────────────────────────────────────

class RuachScene(ThreeDScene):
    """Base scene with attribution, standard setup, and utilities."""
    
    ATTRIBUTION: Optional[Attribution] = None

    def show_attribution(self, duration=2):
        """Display attribution card at the start of the scene."""
        if self.ATTRIBUTION is None:
            return
        a = self.ATTRIBUTION
        
        lines = [
            Text(a.reference, font_size=24),
            Text(f"by {', '.join(a.authors)}", font_size=18),
            Text(f"{a.collective}, {a.date}", font_size=14, color=GREY),
        ]
        if a.note:
            lines.append(Text(a.note, font_size=14, color=GREY))
        
        group = VGroup(*lines).arrange(DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(*lines)
        self.play(*[Write(l) for l in lines])
        self.wait(duration)
        self.play(*[FadeOut(l) for l in lines])

    def annotate(self, text, corner=DL, font_size=14, color=WHITE):
        """Add a corner annotation (the Arnol'd commentary style)."""
        note = Text(text, font_size=font_size, color=color)
        self.add_fixed_in_frame_mobjects(note)
        note.to_corner(corner)
        self.play(Write(note))
        return note

    def dismiss(self, *mobjects):
        """Fade out annotations."""
        self.play(*[FadeOut(m) for m in mobjects])


class RuachScene2D(Scene):
    """Base 2D scene with the same utilities."""
    
    ATTRIBUTION: Optional[Attribution] = None

    def show_attribution(self, duration=2):
        if self.ATTRIBUTION is None:
            return
        a = self.ATTRIBUTION
        lines = [
            Text(a.reference, font_size=24),
            Text(f"by {', '.join(a.authors)}", font_size=18),
            Text(f"{a.collective}, {a.date}", font_size=14, color=GREY),
        ]
        group = VGroup(*lines).arrange(DOWN, buff=0.2)
        self.play(*[Write(l) for l in lines])
        self.wait(duration)
        self.play(*[FadeOut(l) for l in lines])

    def annotate(self, text, corner=DL, font_size=14, color=WHITE):
        note = Text(text, font_size=font_size, color=color)
        note.to_corner(corner)
        self.play(Write(note))
        return note

    def dismiss(self, *mobjects):
        self.play(*[FadeOut(m) for m in mobjects])


# ─── Reusable Components ─────────────────────────────────

def make_projection_plane(x_range=(-2, 2), y_range=(-2, 2), z=0):
    """A standard translucent projection plane."""
    return Surface(
        lambda u, v: np.array([u, v, z]),
        u_range=x_range,
        v_range=y_range,
        resolution=(10, 10),
        fill_opacity=0.08,
        stroke_width=0.2,
        stroke_color=ArnoldColors.PLANE,
    )


def make_fold_surface(u_range=(-1.5, 1.5), v_range=(-1.5, 1.5)):
    """Whitney's fold: (x₁, x₂) → (x₁², x₂, x₁)."""
    surface = Surface(
        lambda u, v: np.array([u**2, v, u]),
        u_range=u_range,
        v_range=v_range,
        resolution=(30, 30),
        fill_opacity=0.6,
    )
    surface.set_color_by_gradient(*ArnoldColors.SURFACE)
    return surface


def make_cusp_surface(u_range=(-1.3, 1.3), v_range=(-2.5, 1.0)):
    """Whitney's cusp: (x₁, x₂) → (x₁³ + x₁x₂, x₂, x₁)."""
    surface = Surface(
        lambda u, v: np.array([u**3 + u * v, v, u]),
        u_range=u_range,
        v_range=v_range,
        resolution=(40, 30),
        fill_opacity=0.4,
        stroke_width=0.3,
    )
    surface.set_color_by_gradient(*ArnoldColors.SURFACE)
    return surface


def make_cusp_curve(t_range=(-0.9, 0.9)):
    """The cusp curve (semi-cubic parabola) on the projection plane."""
    return ParametricFunction(
        lambda t: np.array([-2 * t**3, -3 * t**2, 0]),
        t_range=t_range,
        color=ArnoldColors.CUSP,
        stroke_width=3,
    )


def make_relu_plot(axes, x_range=(-3, 3)):
    """ReLU = max(0, x) on given axes."""
    return axes.plot(
        lambda x: max(0, x),
        x_range=x_range,
        color=ArnoldColors.HORIZON,
        stroke_width=4,
    )


# ─── Neural Network Visualization ────────────────────────

def make_activation_boundary(weight, bias, x_range=(-3, 3), y_range=(-3, 3)):
    """The fold line z = w·x + b = 0 for a single neuron.
    Returns a Line on the (x₁, x₂) plane."""
    # w₁x₁ + w₂x₂ + b = 0
    if len(weight) == 2:
        w1, w2 = weight
        if abs(w2) > 1e-8:
            # x₂ = -(w₁x₁ + b) / w₂
            start = np.array([x_range[0], -(w1 * x_range[0] + bias) / w2, 0])
            end = np.array([x_range[1], -(w1 * x_range[1] + bias) / w2, 0])
        else:
            x_cross = -bias / w1 if abs(w1) > 1e-8 else 0
            start = np.array([x_cross, y_range[0], 0])
            end = np.array([x_cross, y_range[1], 0])
        return Line(start, end, color=ArnoldColors.FOLD, stroke_width=2)
    return None
