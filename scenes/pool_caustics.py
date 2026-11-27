"""
Swimming Pool Caustics — Arnol'd's most beautiful example.

Multiple wave sources create a wavy water surface. Sunlight at 30°
refracts through the surface and concentrates on the pool floor
in the characteristic bright network of curves — the caustic pattern.

Each bright line is a fold singularity: two refracted rays arrive
at the same point on the pool floor. The cusp points (where bright
lines meet) are Whitney's second singularity.

This is what Arnol'd means when he says catastrophe theory is
"experimentally observable" — look at a swimming pool.

Reference: Arnol'd, Catastrophe Theory, Ch. 6
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import manim_merkle_hash
manim_merkle_hash.install()

from ruach_manim import reading_time
from manim import *
import numpy as np


class PoolCaustics(ThreeDScene):
    """Sunlight through a wavy pool surface → caustics on the floor."""

    def construct(self):
        title = Text("Swimming Pool Caustics", font_size=32)
        subtitle = Text("Sunlight through waves — Arnol'd Ch. 6", font_size=18, color=GREY)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(Write(title), Write(subtitle))
        self.wait(reading_time("Swimming Pool Caustics"))
        self.play(FadeOut(title), FadeOut(subtitle))

        self.set_camera_orientation(phi=55 * DEGREES, theta=-35 * DEGREES)

        # === Water surface: superposition of wave sources ===
        # 4 wave sources at different positions create interference
        wave_sources = [
            {'pos': (-1.0, -0.5), 'freq': 3.0, 'amp': 0.08, 'phase': 0},
            {'pos': (0.8, 0.3),   'freq': 4.0, 'amp': 0.06, 'phase': 1.2},
            {'pos': (-0.3, 1.0),  'freq': 3.5, 'amp': 0.07, 'phase': 2.5},
            {'pos': (0.5, -0.8),  'freq': 2.8, 'amp': 0.05, 'phase': 0.8},
        ]

        def water_height(x, y):
            """Superposition of circular waves."""
            h = 0
            for src in wave_sources:
                r = np.sqrt((x - src['pos'][0])**2 + (y - src['pos'][1])**2)
                h += src['amp'] * np.cos(src['freq'] * r * 2 * np.pi + src['phase'])
            return h

        def water_normal(x, y, eps=0.01):
            """Surface normal via finite differences."""
            hx = (water_height(x + eps, y) - water_height(x - eps, y)) / (2 * eps)
            hy = (water_height(x, y + eps) - water_height(x, y - eps)) / (2 * eps)
            # Normal = (-dh/dx, -dh/dy, 1), normalized
            n = np.array([-hx, -hy, 1.0])
            return n / np.linalg.norm(n)

        POOL_SIZE = 2.0
        WATER_Z = 1.0    # water surface height
        FLOOR_Z = -1.0   # pool floor height

        # Water surface:
        water = Surface(
            lambda u, v: np.array([u, v, WATER_Z + water_height(u, v)]),
            u_range=[-POOL_SIZE, POOL_SIZE],
            v_range=[-POOL_SIZE, POOL_SIZE],
            resolution=(60, 60),
            fill_opacity=0.25,
            stroke_width=0.2,
            stroke_color=BLUE_B,
            checkerboard_colors=[BLUE_D, BLUE_E],
        )

        # Pool floor:
        floor = Surface(
            lambda u, v: np.array([u, v, FLOOR_Z]),
            u_range=[-POOL_SIZE, POOL_SIZE],
            v_range=[-POOL_SIZE, POOL_SIZE],
            resolution=(4, 4),
            fill_opacity=0.15,
            stroke_width=0.3,
            stroke_color=GREY_D,
        )

        self.play(Create(floor), run_time=0.5)
        self.play(Create(water), run_time=2)

        note1 = Text("Water surface: 4 superposed wave sources", font_size=13)
        self.add_fixed_in_frame_mobjects(note1)
        note1.to_corner(DL)
        self.play(Write(note1))
        self.wait(1)
        self.play(FadeOut(note1))

        # === Sunlight: parallel rays at 30° angle ===
        # Sun direction: (sin30°, 0, -cos30°) = (0.5, 0, -0.866)
        sun_dir = np.array([0.5, 0.0, -np.cos(np.radians(30))])
        sun_dir /= np.linalg.norm(sun_dir)

        # Snell's law: refraction at the water surface
        # n_air = 1.0, n_water = 1.33
        N_AIR = 1.0
        N_WATER = 1.33

        def refract_ray(incident, normal, n1, n2):
            """Snell's law vector form."""
            cos_i = -np.dot(incident, normal)
            if cos_i < 0:
                normal = -normal
                cos_i = -cos_i
            sin2_t = (n1 / n2)**2 * (1 - cos_i**2)
            if sin2_t > 1:
                return None  # total internal reflection
            cos_t = np.sqrt(1 - sin2_t)
            return (n1 / n2) * incident + ((n1 / n2) * cos_i - cos_t) * normal

        # Trace rays through the water surface to the pool floor:
        # Sample a grid of rays hitting the water surface
        N_GRID = 80
        xs = np.linspace(-POOL_SIZE + 0.1, POOL_SIZE - 0.1, N_GRID)
        ys = np.linspace(-POOL_SIZE + 0.1, POOL_SIZE - 0.1, N_GRID)

        floor_hits = []  # where refracted rays hit the floor

        for x in xs:
            for y in ys:
                h = water_height(x, y)
                surface_pt = np.array([x, y, WATER_Z + h])
                normal = water_normal(x, y)

                refracted = refract_ray(sun_dir, normal, N_AIR, N_WATER)
                if refracted is None:
                    continue

                # Trace to floor (z = FLOOR_Z):
                if abs(refracted[2]) < 1e-10:
                    continue
                t = (FLOOR_Z - surface_pt[2]) / refracted[2]
                if t < 0:
                    continue
                hit = surface_pt + t * refracted
                if abs(hit[0]) < POOL_SIZE and abs(hit[1]) < POOL_SIZE:
                    floor_hits.append(hit[:2])

        floor_hits = np.array(floor_hits)

        # === Caustic visualization: density of floor hits ===
        # Bin the hits into a 2D histogram — bright = many rays = caustic
        from matplotlib.colors import LinearSegmentedColormap

        hist_res = 100
        H, xedges, yedges = np.histogram2d(
            floor_hits[:, 0], floor_hits[:, 1],
            bins=hist_res,
            range=[[-POOL_SIZE, POOL_SIZE], [-POOL_SIZE, POOL_SIZE]],
        )

        # Normalize and create a light pattern on the floor:
        H = H.T  # transpose for correct orientation
        H = H / (H.max() + 1e-10)

        # Draw the caustic pattern as bright dots on the floor:
        caustic_dots = VGroup()
        threshold = 0.3  # only show bright regions

        for i in range(hist_res):
            for j in range(hist_res):
                if H[i, j] > threshold:
                    cx = (xedges[j] + xedges[j + 1]) / 2
                    cy = (yedges[i] + yedges[i + 1]) / 2
                    brightness = min(1.0, H[i, j] * 1.5)
                    dot = Dot3D(
                        point=np.array([cx, cy, FLOOR_Z + 0.01]),
                        radius=0.025,
                        color=interpolate_color(DARK_BLUE, WHITE, brightness),
                    )
                    dot.set_opacity(brightness * 0.8)
                    caustic_dots.add(dot)

        note2 = Text("Sunlight at 30° refracts through the waves.\nBright lines on the floor = CAUSTICS (fold singularities).", font_size=12)
        self.add_fixed_in_frame_mobjects(note2)
        note2.to_corner(DL)
        self.play(Write(note2))
        self.play(Create(caustic_dots), run_time=2)
        self.wait(reading_time("Sunlight refracts through waves bright lines on floor are caustics fold singularities"))
        self.play(FadeOut(note2))

        # Draw a few sample rays:
        sample_rays = VGroup()
        np.random.seed(42)
        for _ in range(8):
            x = np.random.uniform(-1.5, 1.5)
            y = np.random.uniform(-1.5, 1.5)
            h = water_height(x, y)
            surface_pt = np.array([x, y, WATER_Z + h])
            normal = water_normal(x, y)
            refracted = refract_ray(sun_dir, normal, N_AIR, N_WATER)
            if refracted is None:
                continue
            # Incoming ray:
            incoming_start = surface_pt - sun_dir * 1.5
            ray_in = Line(incoming_start, surface_pt, stroke_color=YELLOW, stroke_width=1, stroke_opacity=0.5)
            # Refracted ray to floor:
            t = (FLOOR_Z - surface_pt[2]) / refracted[2]
            hit = surface_pt + t * refracted
            ray_out = Line(surface_pt, hit, stroke_color=YELLOW_A, stroke_width=1, stroke_opacity=0.4)
            sample_rays.add(ray_in, ray_out)

        self.play(Create(sample_rays), run_time=1)

        # Rotate to appreciate:
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        # === Final ===
        final_text = (
            "Each bright line is a fold:\n"
            "two refracted rays arrive at one point.\n"
            "Where bright lines meet: a cusp.\n\n"
            "Look at a swimming pool.\n"
            "You are seeing catastrophe theory."
        )
        final = Text(final_text, font_size=13, color=YELLOW)
        self.add_fixed_in_frame_mobjects(final)
        final.to_corner(DR)
        self.play(Write(final))
        self.wait(reading_time(final_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])
