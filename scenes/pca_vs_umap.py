"""
PCA vs UMAP — side-by-side projection comparison on geodesic Earth.

Globe in the center, PCA embedding on the left, UMAP embedding on the right.
Same data, same colors, different projections, different singularities.

Where does each method tear the sphere?
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


class PCAvsUMAP(ThreeDScene):
    """Side-by-side: PCA (left), globe (center), UMAP (right)."""

    def construct(self):
        title = Text("PCA vs UMAP — Geodesic Earth", font_size=30)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        self.wait(reading_time("PCA versus UMAP"))
        self.play(FadeOut(title))

        self.set_camera_orientation(phi=70 * DEGREES, theta=-25 * DEGREES)

        # Build globe data:
        verts, faces, cell_data = build_geodesic_globe(level=1)

        # Extract centroids:
        centroids = []
        colors = []
        for (a, b, c), data in zip(faces, cell_data):
            centroid = (verts[a] + verts[b] + verts[c]) / 3
            centroid /= np.linalg.norm(centroid)
            centroids.append(centroid)
            colors.append(data['color'])

        X = np.array(centroids)

        # PCA:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X)

        # UMAP:
        import umap
        reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=10, min_dist=0.3)
        X_umap = reducer.fit_transform(X)

        # Normalize both to same scale:
        def normalize_2d(X_2d, scale=1.2):
            X_2d = X_2d - X_2d.mean(axis=0)
            X_2d = X_2d / (np.abs(X_2d).max() + 1e-8) * scale
            return X_2d

        X_pca = normalize_2d(X_pca)
        X_umap = normalize_2d(X_umap)

        # === Layout: PCA left (-3.5), Globe center (0), UMAP right (+3.5) ===
        SHIFT_L = np.array([-3.5, 0, 0])
        SHIFT_R = np.array([3.5, 0, 0])

        # Globe (center, slightly smaller):
        globe_tris = VGroup()
        GLOBE_SCALE = 0.8
        for (a, b, c), data in zip(faces, cell_data):
            va, vb, vc = verts[a] * GLOBE_SCALE, verts[b] * GLOBE_SCALE, verts[c] * GLOBE_SCALE
            tri = Polygon(va, vb, vc,
                fill_color=rgb_to_color(data['color']),
                fill_opacity=0.8,
                stroke_color=GREY, stroke_width=0.3)
            globe_tris.add(tri)

        # PCA dots (left):
        pca_dots = VGroup()
        for x2d, col in zip(X_pca, colors):
            dot = Dot3D(
                point=np.array([x2d[0], x2d[1], 0]) + SHIFT_L,
                color=rgb_to_color(col), radius=0.05)
            pca_dots.add(dot)

        # UMAP dots (right):
        umap_dots = VGroup()
        for x2d, col in zip(X_umap, colors):
            dot = Dot3D(
                point=np.array([x2d[0], x2d[1], 0]) + SHIFT_R,
                color=rgb_to_color(col), radius=0.05)
            umap_dots.add(dot)

        # Labels:
        pca_label = Text("PCA", font_size=20, color=BLUE)
        umap_label = Text("UMAP", font_size=20, color=GREEN)
        globe_label = Text("3D", font_size=18, color=WHITE)
        self.add_fixed_in_frame_mobjects(pca_label, umap_label, globe_label)
        pca_label.move_to(UP * 3.2 + LEFT * 3.5)
        globe_label.move_to(UP * 3.2)
        umap_label.move_to(UP * 3.2 + RIGHT * 3.5)

        # === Phase 1: Show the globe ===
        self.play(Create(globe_tris), Write(globe_label), run_time=2)
        self.wait(1)

        # === Phase 2: PCA projection appears ===
        note_pca = Text("PCA: linear projection\nfinds axes of maximum variance", font_size=12, color=BLUE)
        self.add_fixed_in_frame_mobjects(note_pca)
        note_pca.to_corner(DL)
        self.play(Write(pca_label), Write(note_pca), Create(pca_dots), run_time=2)
        self.wait(reading_time("PCA linear projection finds axes of maximum variance"))
        self.play(FadeOut(note_pca))

        # === Phase 3: UMAP projection appears ===
        note_umap = Text("UMAP: nonlinear embedding\npreserves local neighborhoods", font_size=12, color=GREEN)
        self.add_fixed_in_frame_mobjects(note_umap)
        note_umap.to_corner(DL)
        self.play(Write(umap_label), Write(note_umap), Create(umap_dots), run_time=2)
        self.wait(reading_time("UMAP nonlinear embedding preserves local neighborhoods"))
        self.play(FadeOut(note_umap))

        # === Phase 4: Comparison annotation ===
        compare_text = (
            "Same data, different projections.\n"
            "PCA preserves global variance — tears at the poles.\n"
            "UMAP preserves neighbors — tears between continents."
        )
        compare = Text(compare_text, font_size=12)
        self.add_fixed_in_frame_mobjects(compare)
        compare.to_corner(DL)
        self.play(Write(compare))
        self.wait(reading_time(compare_text))
        self.play(FadeOut(compare))

        # === Phase 5: Rotate to show 3D vs flat ===
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        # === Final insight ===
        final_text = (
            "Every projection creates singularities.\n"
            "The choice of method determines\n"
            "WHERE the information is lost."
        )
        final = Text(final_text, font_size=14, color=YELLOW)
        self.add_fixed_in_frame_mobjects(final)
        final.to_corner(DR)
        self.play(Write(final))
        self.wait(reading_time(final_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])
