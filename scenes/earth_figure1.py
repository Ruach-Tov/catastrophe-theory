"""
Arnol'd Figure 1 with Earth — real coastlines projected to a plane.

The globe rotates above a projection plane. Points on the sphere
(colored by continent) project down to the plane. As the globe
rotates, continents enter and leave the fold — the limb where
near and far sides overlap.

The projection plane is normal to the spin axis (orthographic
projection along the viewing direction).

Data: Natural Earth 110m countries (GeoJSON)
Reference: Arnol'd, Catastrophe Theory, Ch. 2, Figure 1
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ruach_manim import RuachScene, ArnoldColors, attribution, reading_time
from manim import *
import numpy as np
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / 'data'
GEOJSON = DATA_DIR / 'ne_110m_countries.geojson'

CONTINENT_COLORS = {
    'Africa':        '#e6194B',
    'Asia':          '#3cb44b',
    'Europe':        '#4363d8',
    'North America': '#f58231',
    'South America': '#911eb4',
    'Oceania':       '#42d4f4',
    'Antarctica':    '#aaffc3',
}

POINTS_PER_CONTINENT = 200  # fewer for manim performance


def point_in_polygon(x, y, polygon):
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_multipolygon(lon, lat, geometry):
    if geometry['type'] == 'Polygon':
        return point_in_polygon(lon, lat, geometry['coordinates'][0])
    elif geometry['type'] == 'MultiPolygon':
        for polygon in geometry['coordinates']:
            if point_in_polygon(lon, lat, polygon[0]):
                return True
    return False


def bbox_of_geometry(geometry):
    coords = []
    if geometry['type'] == 'Polygon':
        coords = geometry['coordinates'][0]
    elif geometry['type'] == 'MultiPolygon':
        for poly in geometry['coordinates']:
            coords.extend(poly[0])
    if not coords:
        return None
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return (min(lons), max(lons), min(lats), max(lats))


def generate_earth_points():
    """Generate continent-colored points within real coastlines."""
    np.random.seed(42)
    with open(GEOJSON) as f:
        geo = json.load(f)

    continent_features = {}
    for feature in geo['features']:
        continent = feature['properties'].get('CONTINENT', 'Unknown')
        if continent not in CONTINENT_COLORS:
            continue
        if continent not in continent_features:
            continent_features[continent] = []
        continent_features[continent].append(feature)

    all_points = []
    for continent, features in continent_features.items():
        color = CONTINENT_COLORS[continent]
        n_per_country = max(3, POINTS_PER_CONTINENT // len(features))
        continent_pts = []

        for feature in features:
            geom = feature['geometry']
            bbox = bbox_of_geometry(geom)
            if bbox is None:
                continue
            lon_min, lon_max, lat_min, lat_max = bbox
            pts = []
            for _ in range(n_per_country * 50):
                if len(pts) >= n_per_country:
                    break
                lon = np.random.uniform(lon_min, lon_max)
                sin_lat = np.random.uniform(
                    np.sin(np.radians(lat_min)),
                    np.sin(np.radians(lat_max)))
                lat = np.degrees(np.arcsin(np.clip(sin_lat, -1, 1)))
                if point_in_multipolygon(lon, lat, geom):
                    lat_r = np.radians(lat)
                    lon_r = np.radians(lon)
                    x = np.cos(lat_r) * np.cos(lon_r)
                    y = np.cos(lat_r) * np.sin(lon_r)
                    z = np.sin(lat_r)
                    pts.append((x, y, z, continent, color))
            continent_pts.extend(pts)

        if len(continent_pts) > POINTS_PER_CONTINENT:
            np.random.shuffle(continent_pts)
            continent_pts = continent_pts[:POINTS_PER_CONTINENT]
        all_points.extend(continent_pts)

    return all_points


class EarthArnoldFigure1(ThreeDScene):
    """Arnol'd Figure 1 with real Earth coastlines."""

    def construct(self):
        # Title
        title = Text("Arnol'd Figure 1 — The Earth", font_size=32)
        subtitle = Text("Orthographic projection creates the fold singularity", font_size=20)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(Write(title), Write(subtitle))
        self.wait(reading_time("Arnol'd Figure 1 The Earth orthographic projection creates the fold singularity"))
        self.play(FadeOut(title), FadeOut(subtitle))

        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)

        # Generate earth points
        earth_points = generate_earth_points()

        # === The projection plane (z = -2) ===
        plane = Surface(
            lambda u, v: np.array([u, v, -2]),
            u_range=[-1.8, 1.8],
            v_range=[-1.8, 1.8],
            resolution=(8, 8),
            fill_opacity=0.08,
            stroke_width=0.2,
            stroke_color=GREY,
        )

        # The limb circle on the plane:
        limb = ParametricFunction(
            lambda t: np.array([np.cos(t), np.sin(t), -2]),
            t_range=[0, TAU],
            color=RED,
            stroke_width=2,
        )

        self.play(Create(plane), Create(limb), run_time=1)

        # === Plot earth points on the sphere (at z offset +1.5) ===
        SPHERE_CENTER = np.array([0, 0, 0])

        # Group dots by continent for coloring:
        sphere_dots = VGroup()
        plane_dots_near = VGroup()
        plane_dots_far = VGroup()
        proj_lines = VGroup()

        for x, y, z, continent, color in earth_points:
            # Sphere point:
            sp = np.array([x, y, z])
            sphere_dot = Dot3D(point=sp, color=color, radius=0.02)
            sphere_dots.add(sphere_dot)

            # Projection to the plane (drop z, project x,y to plane at z=-2):
            # Orthographic: just (x, y) on the plane
            pp = np.array([x, y, -2])

            # Is this point on the near side? (z > 0 from default view)
            if z > 0:  # visible hemisphere
                plane_dot = Dot3D(point=pp, color=color, radius=0.015)
                plane_dots_near.add(plane_dot)
            else:  # far side — the fold
                plane_dot = Dot3D(point=pp, color=color, radius=0.01)
                plane_dot.set_opacity(0.15)
                plane_dots_far.add(plane_dot)

        # Show the sphere points
        self.play(Create(sphere_dots), run_time=2)
        self.wait(1)

        # Show projection to plane — far side first (light), then near side (heavy)
        note1 = Text("Projecting to the plane...", font_size=16)
        self.add_fixed_in_frame_mobjects(note1)
        note1.to_corner(DL)
        self.play(Write(note1))

        self.play(Create(plane_dots_far), run_time=1)
        self.play(Create(plane_dots_near), run_time=1.5)

        self.play(FadeOut(note1))

        # Annotation: the fold
        fold_note_text = (
            "Near the limb (red circle): two continents overlap.\n"
            "The projection maps two sphere-points to one plane-point.\n"
            "This is the fold singularity — information is lost."
        )
        fold_note = Text(fold_note_text, font_size=12)
        self.add_fixed_in_frame_mobjects(fold_note)
        fold_note.to_corner(DL)
        self.play(Write(fold_note))
        self.wait(reading_time(fold_note_text))
        self.play(FadeOut(fold_note))

        # === Rotate the globe to show different folds ===
        rotate_note = Text("As the globe rotates, different continents\nenter and leave the fold.", font_size=14)
        self.add_fixed_in_frame_mobjects(rotate_note)
        rotate_note.to_corner(DL)
        self.play(Write(rotate_note))

        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(8)
        self.stop_ambient_camera_rotation()

        self.play(FadeOut(rotate_note))

        # === Final: the connection ===
        final_text = (
            "Every dimensionality reduction creates folds.\n"
            "UMAP, PCA, neural network projections —\n"
            "all lose information at their singularities.\n"
            "Arnol'd classified these losses in 1984."
        )
        final = Text(final_text, font_size=13, color=YELLOW)
        self.add_fixed_in_frame_mobjects(final)
        final.to_corner(DR)
        self.play(Write(final))
        self.wait(reading_time(final_text))

        self.play(*[FadeOut(mob) for mob in self.mobjects])
