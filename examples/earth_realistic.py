"""
Earth surface → plane projection — realistic coastlines from Natural Earth.

Uses Natural Earth 110m country boundaries (GeoJSON) to scatter
~1000 points per continent WITHIN actual coastline polygons.
Orthographic projection to a plane creates Arnol'd's fold singularity.

The 2D projection shows overlapping continent labels at the fold —
information lost in the projection, just as UMAP loses information
when projecting high-dimensional data to 2D.

Data: Natural Earth (public domain) ne_110m_admin_0_countries.geojson
"""

import json
import numpy as np
import matplotlib.pyplot as plt
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
    'Seven seas (open ocean)': '#808080',
}

POINTS_PER_CONTINENT = 1000


def point_in_polygon(x, y, polygon):
    """Ray-casting point-in-polygon test."""
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
    """Check if a point is inside a GeoJSON geometry (Polygon or MultiPolygon)."""
    if geometry['type'] == 'Polygon':
        # Check outer ring only (ignore holes for simplicity):
        return point_in_polygon(lon, lat, geometry['coordinates'][0])
    elif geometry['type'] == 'MultiPolygon':
        for polygon in geometry['coordinates']:
            if point_in_polygon(lon, lat, polygon[0]):
                return True
        return False
    return False


def bbox_of_geometry(geometry):
    """Get bounding box of a GeoJSON geometry."""
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


def latlon_to_xyz(lat, lon):
    """Convert lat/lon (degrees) to unit sphere (x, y, z)."""
    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    x = np.cos(lat_r) * np.cos(lon_r)
    y = np.cos(lat_r) * np.sin(lon_r)
    z = np.sin(lat_r)
    return x, y, z


def generate_points_in_country(geometry, n_points, continent, color):
    """Scatter n_points uniformly within a country's polygon(s)."""
    bbox = bbox_of_geometry(geometry)
    if bbox is None:
        return []
    
    lon_min, lon_max, lat_min, lat_max = bbox
    points = []
    max_attempts = n_points * 100
    attempts = 0
    
    while len(points) < n_points and attempts < max_attempts:
        # Uniform on sphere: uniform lon, cos-weighted lat
        lon = np.random.uniform(lon_min, lon_max)
        sin_lat = np.random.uniform(np.sin(np.radians(lat_min)), 
                                      np.sin(np.radians(lat_max)))
        lat = np.degrees(np.arcsin(np.clip(sin_lat, -1, 1)))
        
        if point_in_multipolygon(lon, lat, geometry):
            x, y, z = latlon_to_xyz(lat, lon)
            points.append({
                'lat': lat, 'lon': lon,
                'x': x, 'y': y, 'z': z,
                'continent': continent, 'color': color,
            })
        attempts += 1
    
    return points


def load_and_generate():
    """Load Natural Earth GeoJSON and generate continent-labeled points."""
    with open(GEOJSON) as f:
        geo = json.load(f)
    
    # Group countries by continent:
    continent_features = {}
    for feature in geo['features']:
        continent = feature['properties'].get('CONTINENT', 'Unknown')
        if continent not in continent_features:
            continent_features[continent] = []
        continent_features[continent].append(feature)
    
    all_points = []
    for continent, features in sorted(continent_features.items()):
        if continent in ('Seven seas (open ocean)',):
            continue
        color = CONTINENT_COLORS.get(continent, '#808080')
        
        # Distribute points across countries proportional to rough area:
        n_countries = len(features)
        points_per_country = max(5, POINTS_PER_CONTINENT // n_countries)
        
        continent_points = []
        for feature in features:
            geom = feature['geometry']
            name = feature['properties'].get('NAME', '?')
            pts = generate_points_in_country(geom, points_per_country, continent, color)
            continent_points.extend(pts)
        
        # Trim or pad to target:
        if len(continent_points) > POINTS_PER_CONTINENT:
            np.random.shuffle(continent_points)
            continent_points = continent_points[:POINTS_PER_CONTINENT]
        
        all_points.extend(continent_points)
        print(f"  {continent:15s}: {len(continent_points):4d} points from {n_countries} countries")
    
    print(f"  {'TOTAL':15s}: {len(all_points):4d} points")
    return all_points


def orthographic_projection(points, view_lon=0, view_lat=20):
    """Project sphere to plane. Returns list with proj_x, proj_y, visible."""
    phi = np.radians(view_lat)
    lam = np.radians(view_lon)
    
    results = []
    for p in points:
        x, y, z = p['x'], p['y'], p['z']
        
        x1 = x * np.cos(lam) + y * np.sin(lam)
        y1 = -x * np.sin(lam) + y * np.cos(lam)
        z1 = z
        
        x2 = x1 * np.cos(phi) + z1 * np.sin(phi)
        y2 = y1
        z2 = -x1 * np.sin(phi) + z1 * np.cos(phi)
        
        results.append({
            **p,
            'proj_x': y2, 'proj_y': z2,
            'depth': x2, 'visible': x2 > 0,
        })
    return results


if __name__ == '__main__':
    print("Loading Natural Earth coastlines and generating points...")
    np.random.seed(42)
    points = load_and_generate()
    
    print("\nProjecting sphere → plane (orthographic)...")
    projected = orthographic_projection(points, view_lon=20, view_lat=15)
    
    visible = [p for p in projected if p['visible']]
    hidden = [p for p in projected if not p['visible']]
    print(f"  Visible: {len(visible)}, Hidden (fold): {len(hidden)}")
    
    # ─── Three-panel figure ───────────────────────────────
    fig = plt.figure(figsize=(18, 6))
    
    # Panel 1: 3D sphere
    ax1 = fig.add_subplot(131, projection='3d')
    for continent in sorted(CONTINENT_COLORS.keys()):
        if continent == 'Seven seas (open ocean)':
            continue
        pts = [p for p in points if p['continent'] == continent]
        if pts:
            ax1.scatter([p['x'] for p in pts], [p['y'] for p in pts], [p['z'] for p in pts],
                       c=CONTINENT_COLORS[continent], s=1.5, alpha=0.6, label=continent)
    ax1.set_title('Earth (Natural Earth coastlines)', fontsize=11)
    ax1.legend(fontsize=5, loc='upper left', markerscale=3)
    ax1.set_box_aspect([1,1,1])
    
    # Panel 2: Projection — visible only
    ax2 = fig.add_subplot(132)
    for continent in sorted(CONTINENT_COLORS.keys()):
        if continent == 'Seven seas (open ocean)':
            continue
        pts = [p for p in projected if p['continent'] == continent and p['visible']]
        if pts:
            ax2.scatter([p['proj_x'] for p in pts], [p['proj_y'] for p in pts],
                       c=CONTINENT_COLORS[continent], s=2, alpha=0.7, label=continent)
    theta = np.linspace(0, 2*np.pi, 100)
    ax2.plot(np.cos(theta), np.sin(theta), 'r-', linewidth=1.5, label='limb (fold)')
    ax2.set_title('Projection (near side)\nWhat the observer sees', fontsize=11)
    ax2.set_aspect('equal')
    ax2.legend(fontsize=5, markerscale=3)
    
    # Panel 3: Both sides — the fold revealed
    ax3 = fig.add_subplot(133)
    for continent in sorted(CONTINENT_COLORS.keys()):
        if continent == 'Seven seas (open ocean)':
            continue
        pts_far = [p for p in projected if p['continent'] == continent and not p['visible']]
        if pts_far:
            ax3.scatter([p['proj_x'] for p in pts_far], [p['proj_y'] for p in pts_far],
                       c=CONTINENT_COLORS[continent], s=1.5, alpha=0.12)
    for continent in sorted(CONTINENT_COLORS.keys()):
        if continent == 'Seven seas (open ocean)':
            continue
        pts_near = [p for p in projected if p['continent'] == continent and p['visible']]
        if pts_near:
            ax3.scatter([p['proj_x'] for p in pts_near], [p['proj_y'] for p in pts_near],
                       c=CONTINENT_COLORS[continent], s=2, alpha=0.7, label=continent)
    ax3.plot(np.cos(theta), np.sin(theta), 'r-', linewidth=1.5, label='limb (fold)')
    ax3.set_title('Both sides overlaid\nFar side = light (the fold)', fontsize=11)
    ax3.set_aspect('equal')
    ax3.legend(fontsize=5, markerscale=3)
    
    plt.tight_layout()
    plt.savefig('/tmp/earth_realistic_projection.png', dpi=150, bbox_inches='tight')
    plt.show()
    print(f"\nSaved to /tmp/earth_realistic_projection.png")
    
    # ─── Fold statistics ──────────────────────────────────
    print("\n── Fold statistics (Arnol'd Figure 1, real coastlines) ──")
    for continent in sorted(CONTINENT_COLORS.keys()):
        if continent == 'Seven seas (open ocean)':
            continue
        total = len([p for p in projected if p['continent'] == continent])
        vis = len([p for p in projected if p['continent'] == continent and p['visible']])
        if total > 0:
            print(f"  {continent:15s}: {vis:4d}/{total:4d} visible ({100*vis/total:.0f}%)")
    print(f"\n  Information lost to the fold: {len(hidden)} points ({100*len(hidden)/len(projected):.0f}%)")
