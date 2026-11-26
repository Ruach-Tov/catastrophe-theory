"""
ReLU as Arnol'd's Maximum Function.

ReLU(x) = max(0, x) — the simplest maximum function.
Two competing functions (f₁=0, f₂=x) exchange dominance at x=0.
The singularity at x=0 is a fold — structurally stable.

A silenced neuron: the fold has been pushed off the data manifold
(all inputs produce x<0, so the max is always f₁=0).

One-Way ReLU: the fold can reform — the catastrophe is reversible.

Reference: Arnol'd, Catastrophe Theory, Ch. 10
           (Singularities in Optimization Problems: the Maximum Function)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ruach_manim import RuachScene2D, ArnoldColors, attribution, reading_time
from manim import *
import numpy as np


class ReLUAsMax(RuachScene2D):
    """ReLU = max(0, x), shown as two competing functions."""

    ATTRIBUTION = attribution(
        authors=["Heath Hunnicutt", "Mavchin"],
        reference="Arnol'd, Catastrophe Theory, Ch. 10",
        date="2026-11-26",
        note="ReLU as the maximum function",
    )

    def construct(self):
        self.show_attribution()

        axes = Axes(
            x_range=[-3, 3, 1], y_range=[-1, 3, 1],
            x_length=8, y_length=5,
            axis_config={"include_tip": True},
        )
        labels = axes.get_axis_labels(x_label="x", y_label="")

        # The two competing functions:
        f1 = axes.plot(lambda x: 0, x_range=[-3, 3], color=BLUE_D, stroke_width=2)
        f1_label = MathTex("f_1 = 0", font_size=22, color=BLUE_D)
        f1_label.next_to(axes.c2p(-2, 0), UP)

        f2 = axes.plot(lambda x: x, x_range=[-3, 3], color=GREEN_D, stroke_width=2)
        f2_label = MathTex("f_2 = x", font_size=22, color=GREEN_D)
        f2_label.next_to(axes.c2p(2, 2), LEFT)

        # The maximum = ReLU:
        relu = axes.plot(lambda x: max(0, x), x_range=[-3, 3], color=RED, stroke_width=4)
        relu_label = MathTex(r"\max(0, x)", font_size=24, color=RED)
        relu_label.next_to(axes.c2p(1.5, 1.5), RIGHT)

        # The singularity at x=0:
        sing_dot = Dot(axes.c2p(0, 0), color=YELLOW, radius=0.1)
        sing_label = Text("fold singularity", font_size=18, color=YELLOW)
        sing_label.next_to(sing_dot, DOWN + RIGHT)

        self.play(Create(axes), Write(labels))
        self.play(Create(f1), Write(f1_label))
        self.play(Create(f2), Write(f2_label))
        self.wait(1)

        # The max emerges:
        self.play(Create(relu), Write(relu_label), run_time=2)
        self.play(Create(sing_dot), Write(sing_label))
        self.wait(2)

        # Annotation — display time from information content:
        note_text = (
            "The kink at x=0 is structurally stable\n"
            "— it cannot be removed by small perturbation.\n"
            "Every ReLU neuron creates one of these folds."
        )
        note = Text(note_text, font_size=16)
        note.to_corner(DR)
        self.play(Write(note))
        self.wait(reading_time(note_text))
