"""Measure the Yaris hull's underbody ground clearance from the mesh itself.

WHY: the corpus review "Particle Resolution and Force Convergence for Rigid Bodies in
Flood-Type Flows" recommends setting particle spacing from the SMALLEST FORCE-BEARING
FEATURE, naming a vehicle's ground clearance explicitly, NOT from the body length or the
domain. This project sets dx from the domain. So the clearance is the number that decides
whether the grid ladder is adequate, and it is not recorded anywhere in vehicle_params.py.

METHOD: the wheels are at the plan corners and the underbody is the central strip, so a
naive global z-min returns the tyre contact patch, not the clearance. Bin the mesh
vertices in plan, take the per-column minimum z, then read the clearance off the CENTRAL
region only. CLAUDE.md item 4(c) records the hull's LONG axis is Y (extents 1.7078,
4.2014, 1.4853), so x is width and y is length.
"""
import numpy as np, trimesh

P = "/Users/josie/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply"
m = trimesh.load(P, process=False)
v = np.asarray(m.vertices, dtype=float)
lo, hi = v.min(axis=0), v.max(axis=0)
ext = hi - lo
print(f"vertices {len(v)}   extents x{ext[0]:.4f} y{ext[1]:.4f} z{ext[2]:.4f} m")
print(f"z range {lo[2]:.4f} to {hi[2]:.4f}")
ax_len = int(np.argmax(ext))          # long axis = length
ax_wid = [i for i in (0, 1) if i != ax_len][0]
print(f"long axis = {'xyz'[ax_len]} (length), width axis = {'xyz'[ax_wid]}")

z0 = lo[2]                             # ground plane = lowest point = tyre contact
L = v[:, ax_len]; W = v[:, ax_wid]; Z = v[:, 2]
Lc = (L - lo[ax_len]) / ext[ax_len]    # 0..1 along length
Wc = (W - lo[ax_wid]) / ext[ax_wid]    # 0..1 across width

print()
print("per-column minimum z above the ground plane, by plan region:")
for name, lsel, wsel in (
    ("FULL plan (includes wheels)", (0.00, 1.00), (0.00, 1.00)),
    ("central 40% length x 50% width (underbody)", (0.30, 0.70), (0.25, 0.75)),
    ("central 20% length x 40% width (tightest)", (0.40, 0.60), (0.30, 0.70)),
    ("between axles, 30-70% L, full width", (0.30, 0.70), (0.00, 1.00)),
):
    sel = (Lc >= lsel[0]) & (Lc <= lsel[1]) & (Wc >= wsel[0]) & (Wc <= wsel[1])
    if sel.sum() < 10:
        print(f"  {name}: too few vertices ({sel.sum()})"); continue
    # grid the region and take min z per column, then the SMALLEST column-min
    nb = 24
    li = np.clip(((Lc[sel] - lsel[0]) / (lsel[1] - lsel[0]) * nb).astype(int), 0, nb - 1)
    wi = np.clip(((Wc[sel] - wsel[0]) / (wsel[1] - wsel[0]) * nb).astype(int), 0, nb - 1)
    zz = Z[sel]
    colmin = {}
    for a, b, z in zip(li, wi, zz):
        k = (a, b)
        if k not in colmin or z < colmin[k]:
            colmin[k] = z
    vals = np.array(sorted(colmin.values()))
    print(f"  {name}: n_vert {sel.sum():6d} cols {len(vals):4d}   "
          f"min {(vals[0]-z0)*1000:7.1f} mm   5th pct {(np.percentile(vals,5)-z0)*1000:7.1f} mm   "
          f"median {(np.median(vals)-z0)*1000:7.1f} mm")

print()
print("GRID ADEQUACY against the measured underbody clearance:")
GRIDS = {48: 0.19629, 64: 0.14721, 96: 0.09814, 128: 0.07361, 160: 0.058886, 192: 0.049072}
sel = (Lc >= 0.30) & (Lc <= 0.70) & (Wc >= 0.25) & (Wc <= 0.75)
nb = 24
li = np.clip(((Lc[sel] - 0.30) / 0.40 * nb).astype(int), 0, nb - 1)
wi = np.clip(((Wc[sel] - 0.25) / 0.50 * nb).astype(int), 0, nb - 1)
cm = {}
for a, b, z in zip(li, wi, Z[sel]):
    k = (a, b)
    if k not in cm or z < cm[k]:
        cm[k] = z
clear = float(np.percentile(np.array(sorted(cm.values())), 5) - z0)
print(f"  underbody clearance (5th pct of column minima) = {clear*1000:.1f} mm")
print(f"  D/10 rule wants dx <= {clear/10*1000:.2f} mm")
print(f"  {'grid':>5} {'dx (mm)':>9} {'cells across clearance':>23} {'meets D/10?':>12}")
for g, dx in GRIDS.items():
    print(f"  {g:5d} {dx*1000:9.2f} {clear/dx:23.2f} {'YES' if dx <= clear/10 else 'no':>12}")
