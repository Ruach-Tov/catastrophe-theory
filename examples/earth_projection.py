"""
Earth surface → plane projection — Arnol'd's fold singularity on real data.

Generate ~1000 points per continent, distributed by land area.
Project the sphere to a plane (orthographic projection).
The fold at the equator (the "horizon") is Arnol'd's Figure 1 made real.

Two points on opposite sides of the sphere project to the SAME plane point
at the limb — the fold singularity. Continents on the far side are
"silenced" by the projection, just as neurons are silenced by ReLU.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ─── Generate land surface points by continent ─────────────

# Approximate continent bounding boxes (lat, lon) and relative land areas
# Areas in million km²: Africa 30.4, Asia 44.6, Europe 10.2, 
# North America 24.7, South America 17.8, Oceania 8.5, Antarctica 14.2
CONTINENTS = {
    'Africa':        {'lat': (-35, 37),  'lon': (-18, 52),   'area': 30.4, 'color': '#e6194B'},
    'Asia':          {'lat': (1, 77),    'lon': (26, 180),   'area': 44.6, 'color': '#3cb44b'},
    'Europe':        {'lat': (36, 71),   'lon': (-25, 60),   'area': 10.2, 'color': '#4363d8'},
    'North America': {'lat': (7, 84),    'lon': (-168, -52), 'area': 24.7, 'color': '#f58231'},
    'South America': {'lat': (-56, 13),  'lon': (-82, -34),  'area': 17.8, 'color': '#911eb4'},
    'Oceania':       {'lat': (-47, -10), 'lon': (110, 180),  'area': 8.5,  'color': '#42d4f4'},
    'Antarctica':    {'lat': (-90, -60), 'lon': (-180, 180), 'area': 14.2, 'color': '#ffffff'},
}

TOTAL_POINTS = 7000  # ~1000 per continent

def generate_continent_points(name, info, n_points):
    """Generate points uniformly distributed on the sphere within a lat/lon box."""
    lat_min, lat_max = np.radians(info['lat'])
    lon_min, lon_max = np.radians(info['lon'])
    
    # Uniform distribution on sphere: uniform in longitude, 
    # cos-weighted in latitude (to avoid polar bunching)
    points = []
    while len(points) < n_points:
        # Generate candidates
        n_batch = n_points * 3
        lon = np.random.uniform(lon_min, lon_max, n_batch)
        # For uniform area: sample sin(lat) uniformly
        sin_lat = np.random.uniform(np.sin(lat_min), np.sin(lat_max), n_batch)
        lat = np.arcsin(sin_lat)
        
        # Convert to 3D (unit sphere)
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        
        for j in range(min(n_batch, n_points - len(points))):
            points.append({
                'x': x[j], 'y': y[j], 'z': z[j],
                'lat': np.degrees(lat[j]), 'lon': np.degrees(lon[j]),
                'continent': name, 'color': info['color']
            })
    
    return points[:n_points]


def generate_earth_dataset():
    """Generate the full dataset with ~1000 points per continent."""
    np.random.seed(42)
    
    # Distribute points proportional to area, minimum 500 per continent
    total_area = sum(c['area'] for c in CONTINENTS.values())
    all_points = []
    
    for name, info in CONTINENTS.items():
        n = max(500, int(TOTAL_POINTS * info['area'] / total_area))
        points = generate_continent_points(name, info, n)
        all_points.extend(points)
        print(f"  {name:15s}: {len(points):4d} points")
    
    print(f"  {'TOTAL':15s}: {len(all_points):4d} points")
    return all_points


def orthographic_projection(points, view_lon=0, view_lat=20):
    """Project 3D sphere points to 2D plane (orthographic).
    
    Points on the far side of the sphere (behind the limb) are 
    the FOLD — they project to the same plane region as near-side points.
    This is Arnol'd's Figure 1 made real.
    
    Returns (x2d, y2d, is_visible) for each point.
    """
    # Rotation matrix for the viewing angle
    phi = np.radians(view_lat)    # elevation
    lam = np.radians(view_lon)    # azimuth
    
    results = []
    for p in points:
        x, y, z = p['x'], p['y'], p['z']
        
        # Rotate to viewing angle
        # First rotate around z-axis by -lam (azimuth)
        x1 = x * np.cos(lam) + y * np.sin(lam)
        y1 = -x * np.sin(lam) + y * np.cos(lam)
        z1 = z
        
        # Then rotate around y-axis by -phi (elevation)
        x2 = x1 * np.cos(phi) + z1 * np.sin(phi)
        y2 = y1
        z2 = -x1 * np.sin(phi) + z1 * np.cos(phi)
        
        # Orthographic projection: drop the x2 coordinate (depth)
        # x2 > 0 means the point is on the NEAR side (visible)
        # x2 < 0 means the point is on the FAR side (behind the limb — the fold!)
        is_visible = x2 > 0
        
        results.append({
            **p,
            'proj_x': y2,
            'proj_y': z2,
            'depth': x2,
            'visible': is_visible,
        })
    
    return results


# ─── Main ─────────────────────────────────────────────────

if __name__ == '__main__':
    print("Generating earth surface dataset...")
    points = generate_earth_dataset()
    
    print("\nProjecting sphere → plane (orthographic, Arnol'd Figure 1)...")
    projected = orthographic_projection(points, view_lon=0, view_lat=20)
    
    visible = [p for p in projected if p['visible']]
    hidden = [p for p in projected if not p['visible']]
    print(f"  Visible (near side): {len(visible)}")
    print(f"  Hidden (far side — the fold): {len(hidden)}")
    
    # ─── Figure 1: 3D sphere with continent colors ─────────
    fig = plt.figure(figsize=(16, 6))
    
    ax1 = fig.add_subplot(131, projection='3d')
    for name, info in CONTINENTS.items():
        pts = [p for p in points if p['continent'] == name]
        ax1.scatter([p['x'] for p in pts], [p['y'] for p in pts], [p['z'] for p in pts],
                   c=info['color'], s=2, alpha=0.6, label=name)
    ax1.set_title('Earth (sphere)')
    ax1.set_xlabel('x'); ax1.set_ylabel('y'); ax1.set_zlabel('z')
    ax1.legend(fontsize=6, loc='upper left')
    
    # ─── Figure 2: Projection — visible only ───────────────
    ax2 = fig.add_subplot(132)
    for name, info in CONTINENTS.items():
        pts = [p for p in projected if p['continent'] == name and p['visible']]
        if pts:
            ax2.scatter([p['proj_x'] for p in pts], [p['proj_y'] for p in pts],
                       c=info['color'], s=3, alpha=0.7, label=name)
    # Draw the limb (unit circle — the fold line)
    theta = np.linspace(0, 2*np.pi, 100)
    ax2.plot(np.cos(theta), np.sin(theta), 'r-', linewidth=1.5, label='limb (fold)')
    ax2.set_title('Orthographic projection\n(near side only)')
    ax2.set_aspect('equal')
    ax2.legend(fontsize=6)
    
    # ─── Figure 3: Projection — both sides overlaid ────────
    ax3 = fig.add_subplot(133)
    # Far side first (lighter, the "dashed first pass"):
    for name, info in CONTINENTS.items():
        pts = [p for p in projected if p['continent'] == name and not p['visible']]
        if pts:
            ax3.scatter([p['proj_x'] for p in pts], [p['proj_y'] for p in pts],
                       c=info['color'], s=2, alpha=0.15)
    # Near side on top (heavier, the "solid second pass"):
    for name, info in CONTINENTS.items():
        pts = [p for p in projected if p['continent'] == name and p['visible']]
        if pts:
            ax3.scatter([p['proj_x'] for p in pts], [p['proj_y'] for p in pts],
                       c=info['color'], s=3, alpha=0.7, label=name)
    ax3.plot(np.cos(theta), np.sin(theta), 'r-', linewidth=1.5, label='limb (fold)')
    ax3.set_title('Both sides overlaid\n(far side = light, the fold)')
    ax3.set_aspect('equal')
    ax3.legend(fontsize=6)
    
    plt.tight_layout()
    plt.savefig('/tmp/earth_arnold_projection.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("\nSaved to /tmp/earth_arnold_projection.png")
    
    # ─── Statistics ────────────────────────────────────────
    print("\n── Fold statistics (Arnol'd Figure 1) ──")
    for name in CONTINENTS:
        total = len([p for p in projected if p['continent'] == name])
        vis = len([p for p in projected if p['continent'] == name and p['visible']])
        print(f"  {name:15s}: {vis:4d}/{total:4d} visible ({100*vis/total:.0f}%)")
    print(f"\n  Points LOST to the fold: {len(hidden)} ({100*len(hidden)/len(projected):.0f}%)")
    print("  These are the 'silenced' points — same as silenced neurons.")
    print("  The projection cannot distinguish near from far at the limb.")
