"""
Geodesic globe → UMAP projection — where do the folds form?

Takes the 320 geodesic face centroids (3D unit sphere, labeled by continent),
projects them through UMAP to 2D, and visualizes both spaces:
  - 3D: the geodesic globe (known geometry)
  - 2D: the UMAP embedding (learned projection)

The question: does UMAP create folds and cusps in the same places
as the orthographic projection, or does it find different singularities?

Also renders as a manim scene with the globe on the left and
UMAP embedding on the right.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples'))

import manim_merkle_hash
manim_merkle_hash.install()

from ruach_manim import reading_time
from manim import *
import numpy as np

from geodesic_globe import build_geodesic_globe, CONTINENT_COLORS, OCEAN_COLOR


class UMAPProjection(ThreeDScene):
    """Side-by-side: geodesic globe and its UMAP embedding."""

    def construct(self):
        title = Text("Geodesic Earth → UMAP", font_size=32)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        self.wait(reading_time("UMAP projection"))
        self.play(FadeOut(title))

        # Build globe data:
        verts, faces, cell_data = build_geodesic_globe(level=1)

        # Extract centroids and labels for UMAP:
        centroids = []
        colors = []
        labels = []
        for (a, b, c), data in zip(faces, cell_data):
            centroid = (verts[a] + verts[b] + verts[c]) / 3
            centroid /= np.linalg.norm(centroid)
            centroids.append(centroid)
            colors.append(data['color'])
            labels.append(data['continent'])

        X = np.array(centroids)  # (N, 3)

        # Run UMAP:
        try:
            import umap
            reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=10, min_dist=0.3)
            X_2d = reducer.fit_transform(X)
        except ImportError:
            # Fallback: use PCA if UMAP not installed:
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=2, random_state=42)
            X_2d = reducer.fit_transform(X)

        # Normalize UMAP output to fit in a display region:
        X_2d -= X_2d.mean(axis=0)
        scale = 2.0 / max(X_2d.max() - X_2d.min(), 1e-6)
        X_2d *= scale

        # === Layout: globe on left (3D), UMAP on right (2D overlay) ===
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)

        # Build globe (shifted left):
        globe_tris = VGroup()
        SHIFT_LEFT = np.array([-2.5, 0, 0])
        for (a, b, c), data in zip(faces, cell_data):
            va, vb, vc = verts[a], verts[b], verts[c]
            tri = Polygon(
                va + SHIFT_LEFT, vb + SHIFT_LEFT, vc + SHIFT_LEFT,
                fill_color=rgb_to_color(data['color']),
                fill_opacity=0.8,
                stroke_color=GREY,
                stroke_width=0.3,
            )
            globe_tris.add(tri)

        self.play(Create(globe_tris), run_time=2)

        # Build UMAP dots (shifted right, on a flat plane):
        SHIFT_RIGHT = np.array([2.5, 0, 0])
        umap_dots = VGroup()
        for i, (x2d, col) in enumerate(zip(X_2d, colors)):
            dot = Dot3D(
                point=np.array([x2d[0], x2d[1], 0]) + SHIFT_RIGHT,
                color=rgb_to_color(col),
                radius=0.06,
            )
            umap_dots.add(dot)

        # Animate: dots appear in UMAP space:
        note_text = "UMAP projects 3D sphere to 2D\npreserving local neighborhood structure"
        note = Text(note_text, font_size=13)
        self.add_fixed_in_frame_mobjects(note)
        note.to_corner(DL)
        self.play(Write(note))
        self.play(Create(umap_dots), run_time=2)
        self.wait(reading_time(note_text))
        self.play(FadeOut(note))

        # Draw connection lines from globe centroids to UMAP positions
        # (just a few to show the mapping, not all 80):
        connection_lines = VGroup()
        np.random.seed(42)
        sample_indices = np.random.choice(len(centroids), size=12, replace=False)
        for i in sample_indices:
            start = centroids[i] + SHIFT_LEFT
            end = np.array([X_2d[i][0], X_2d[i][1], 0]) + SHIFT_RIGHT
            line = DashedLine(start, end, color=YELLOW_A, stroke_width=0.5, dash_length=0.1)
            connection_lines.add(line)

        mapping_text = "Each tile maps from sphere to embedding.\nThe mapping preserves neighbors but creates distortion."
        mapping_note = Text(mapping_text, font_size=12)
        self.add_fixed_in_frame_mobjects(mapping_note)
        mapping_note.to_corner(DL)
        self.play(Write(mapping_note), Create(connection_lines), run_time=1.5)
        self.wait(reading_time(mapping_text))
        self.play(FadeOut(mapping_note), FadeOut(connection_lines))

        # Rotate the globe to show it's 3D while UMAP is flat:
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(5)
        self.stop_ambient_camera_rotation()

        # Final insight:
        final_text = (
            "Where does UMAP create its folds?\n"
            "The sphere has no edges — but the\n"
            "2D embedding must tear somewhere.\n"
            "That tear is the singularity."
        )
        final = Text(final_text, font_size=13, color=YELLOW)
        self.add_fixed_in_frame_mobjects(final)
        final.to_corner(DR)
        self.play(Write(final))
        self.wait(reading_time(final_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])
