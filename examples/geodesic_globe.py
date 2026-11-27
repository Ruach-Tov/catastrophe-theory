"""
Geodesic globe — tessellated earth for UMAP visualization experiments.

Subdivides an icosahedron to create a geodesic sphere, then colors
each cell by which continent it falls within. The result is an
abstracted board-game-like map of Earth.

Level 2 gives ~162 cells — enough to recognize continents,
few enough to animate smoothly in manim.

This is the dataset for UMAP projection experiments:
  - Project the globe to 2D → observe folds and cusps
  - Color by continent → see information loss at the fold
  - Animate the projection → watch singularities form
"""

import numpy as np
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'
GEOJSON = DATA_DIR / 'ne_110m_countries.geojson'

CONTINENT_COLORS = {
    'Africa':        [0.90, 0.10, 0.29],
    'Asia':          [0.24, 0.71, 0.29],
    'Europe':        [0.26, 0.39, 0.85],
    'North America': [0.96, 0.51, 0.19],
    'South America': [0.57, 0.12, 0.71],
    'Oceania':       [0.26, 0.83, 0.96],
    'Antarctica':    [0.67, 1.00, 0.76],
}
OCEAN_COLOR = [0.15, 0.15, 0.25]


# ─── Icosahedron ──────────────────────────────────────────

def icosahedron():
    """Return vertices and faces of a regular icosahedron on the unit sphere."""
    phi = (1 + np.sqrt(5)) / 2  # golden ratio

    verts = np.array([
        [-1,  phi, 0], [ 1,  phi, 0], [-1, -phi, 0], [ 1, -phi, 0],
        [ 0, -1,  phi], [ 0,  1,  phi], [ 0, -1, -phi], [ 0,  1, -phi],
        [ phi, 0, -1], [ phi, 0,  1], [-phi, 0, -1], [-phi, 0,  1],
    ], dtype=float)
    # Normalize to unit sphere:
    verts /= np.linalg.norm(verts, axis=1, keepdims=True)

    faces = [
        (0,11,5), (0,5,1), (0,1,7), (0,7,10), (0,10,11),
        (1,5,9), (5,11,4), (11,10,2), (10,7,6), (7,1,8),
        (3,9,4), (3,4,2), (3,2,6), (3,6,8), (3,8,9),
        (4,9,5), (2,4,11), (6,2,10), (8,6,7), (9,8,1),
    ]
    return verts, faces


def subdivide(verts, faces, levels=1):
    """Subdivide each triangle into 4, projecting new vertices to the unit sphere."""
    for _ in range(levels):
        edge_midpoints = {}
        new_faces = []

        def get_midpoint(i, j):
            key = (min(i, j), max(i, j))
            if key in edge_midpoints:
                return edge_midpoints[key]
            mid = (verts[i] + verts[j]) / 2
            mid /= np.linalg.norm(mid)  # project to sphere
            idx = len(verts)
            verts.append(mid)
            edge_midpoints[key] = idx
            return idx

        verts = list(verts) if isinstance(verts, np.ndarray) else verts
        for a, b, c in faces:
            ab = get_midpoint(a, b)
            bc = get_midpoint(b, c)
            ca = get_midpoint(c, a)
            new_faces.extend([
                (a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)
            ])
        faces = new_faces

    return np.array(verts), faces


# ─── Continent assignment ────────────────────────────────

def point_in_polygon_latlon(lat, lon, polygon):
    """Ray-casting point-in-polygon for lat/lon coordinates."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def xyz_to_latlon(x, y, z):
    """Convert unit sphere (x,y,z) to (lat, lon) in degrees."""
    lat = np.degrees(np.arcsin(np.clip(z, -1, 1)))
    lon = np.degrees(np.arctan2(y, x))
    return lat, lon


def assign_continent(lat, lon, country_features):
    """Determine which continent a lat/lon point belongs to."""
    for feature in country_features:
        continent = feature['properties'].get('CONTINENT', 'Unknown')
        if continent not in CONTINENT_COLORS:
            continue
        geom = feature['geometry']
        if geom['type'] == 'Polygon':
            if point_in_polygon_latlon(lat, lon, geom['coordinates'][0]):
                return continent
        elif geom['type'] == 'MultiPolygon':
            for poly in geom['coordinates']:
                if point_in_polygon_latlon(lat, lon, poly[0]):
                    return continent
    return 'Ocean'


def build_geodesic_globe(level=2):
    """Build a continent-colored geodesic globe.
    
    Returns:
        verts: (N, 3) array of unit sphere vertices
        faces: list of (i, j, k) triangle index tuples
        cell_data: list of dicts with continent, color, lat, lon per face
    """
    verts, faces = icosahedron()
    verts, faces = subdivide(verts, faces, levels=level)

    # Load country data:
    with open(GEOJSON) as f:
        geo = json.load(f)
    country_features = geo['features']

    # Assign each face to a continent based on its centroid:
    cell_data = []
    for a, b, c in faces:
        centroid = (verts[a] + verts[b] + verts[c]) / 3
        centroid /= np.linalg.norm(centroid)
        lat, lon = xyz_to_latlon(*centroid)
        continent = assign_continent(lat, lon, country_features)
        color = CONTINENT_COLORS.get(continent, OCEAN_COLOR)
        cell_data.append({
            'continent': continent,
            'color': color,
            'lat': lat,
            'lon': lon,
            'centroid': centroid.tolist(),
        })

    print(f"Geodesic globe: {len(verts)} vertices, {len(faces)} faces")
    # Count by continent:
    from collections import Counter
    counts = Counter(d['continent'] for d in cell_data)
    for continent, count in sorted(counts.items()):
        print(f"  {continent:15s}: {count:3d} faces")

    return verts, faces, cell_data


if __name__ == '__main__':
    verts, faces, cell_data = build_geodesic_globe(level=2)

    # Quick matplotlib preview:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    for (a, b, c), data in zip(faces, cell_data):
        triangle = [verts[a], verts[b], verts[c]]
        poly = Poly3DCollection([triangle], alpha=0.8)
        poly.set_facecolor(data['color'])
        poly.set_edgecolor([0.3, 0.3, 0.3])
        poly.set_linewidth(0.3)
        ax.add_collection3d(poly)

    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])
    ax.set_zlim([-1.1, 1.1])
    ax.set_box_aspect([1, 1, 1])
    ax.set_title(f'Geodesic Globe ({len(faces)} faces)')
    plt.savefig('/tmp/geodesic_globe.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved to /tmp/geodesic_globe.png")
