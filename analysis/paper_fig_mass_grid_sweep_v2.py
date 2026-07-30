"""Build the real-simulation sweep figure for Section IV-C of
paper/conference_101719.tex.

PROVENANCE, read live at run time:
  data/all_runs_inventory.csv   17 rows; this figure uses the 9 sweep=mass_grid rows

DESIGN CONSTRAINT, deliberate and load-bearing:
  The mass-sensitivity MAGNITUDE is not grid-converged. Ratios of displacement
  between the lightest and heaviest vehicle are 1.87x at n_grid=48, 4.86x at 64
  and 3.00x at 96, i.e. non-monotonic in resolution. This script therefore:
    * plots one SEPARATE LINE PER GRID RESOLUTION, so non-convergence is a visible
      geometric fact rather than a prose caveat, and
    * prints NO ratio, NO multiplier and NO "x" figure anywhere in the output.
  analysis/fig2_mass_sensitivity.py (commit 1767d87) does the opposite: it filters
  to n_grid=64 only and renders `spread = disp[0]/disp[-1]` as "4.86x" in both an
  annotation and the title. That figure is not used or adapted here.

Gate flagging: runs whose passthrough_max_frac exceeds 0.10 are FLAGGED, never
dropped, per the 10 percent particle-passthrough limit README.md cites.

Stdlib only: this machine has no matplotlib (import fails on /usr/bin/python3 and
/opt/homebrew/bin/python3).

Output: paper/figures_review/mass_grid_sweep_v2.svg  (NEW file, overwrites nothing)
"""
import csv
import os
from pathlib import Path

REPO = Path('/Users/josie/can-it-ford')
os.chdir(REPO)
SRC = REPO / 'data' / 'all_runs_inventory.csv'
OUTDIR = REPO / 'paper' / 'figures_review'
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / 'mass_grid_sweep_v2.svg'

GATE = 0.10   # particle-passthrough limit, per README.md Status section

allrows = list(csv.DictReader(open(SRC)))
print(f"source: {SRC}  total rows={len(allrows)}")

# gate census across ALL runs, reported in the caption
over = [r for r in allrows if float(r['passthrough_max_frac']) > GATE]
print(f"runs over the {GATE:.0%} passthrough gate: {len(over)} of {len(allrows)}")
for r in over:
    print(f"    {r['run']:20s} sweep={r['sweep']:10s} passthrough={float(r['passthrough_max_frac'])*100:.2f}%")

rows = [r for r in allrows if r['sweep'] == 'mass_grid']
assert len(rows) == 9, f"expected 9 mass_grid rows, got {len(rows)}"
scen = {r['scenario'] for r in rows}
assert len(scen) == 1, f"mixed scenarios: {scen}"
SCEN = scen.pop()
depths = {r['requested_depth_m'] for r in rows}
vels = {r['velocity_ms'] for r in rows}
assert len(depths) == 1 and len(vels) == 1, "mass_grid is not at a single (depth, velocity)"
D_FIX, V_FIX = depths.pop(), vels.pop()
print(f"\nmass_grid: scenario={SCEN}, fixed depth={D_FIX} m, velocity={V_FIX} m/s")

GRIDS = sorted({int(r['n_grid']) for r in rows})
MASSES = sorted({float(r['mass_kg']) for r in rows})
print(f"grids={GRIDS}  masses={MASSES}")

by = {}
for r in rows:
    by[(int(r['n_grid']), float(r['mass_kg']))] = r

print("\nplotted points:")
for g in GRIDS:
    for m in MASSES:
        r = by[(g, m)]
        pt = float(r['passthrough_max_frac'])
        print(f"  g{g:<3d} m{int(m):<5d} disp={float(r['final_disp_mag_m']):.4f}  "
              f"passthrough={pt*100:5.2f}%{'  FLAGGED' if pt > GATE else ''}  "
              f"water_layers={r['water_layers']}")

# direction check, stated qualitatively only
print("\ndirection check, per grid: is displacement monotonically decreasing in mass?")
all_mono = True
for g in GRIDS:
    ds = [float(by[(g, m)]['final_disp_mag_m']) for m in MASSES]
    mono = all(ds[i] > ds[i + 1] for i in range(len(ds) - 1))
    all_mono = all_mono and mono
    print(f"  n_grid={g}: {mono}")
print(f"consistent direction across every resolution tested: {all_mono}")
print("magnitude is deliberately NOT reduced to a ratio in this figure")

# ---------------- SVG ----------------
W, H = 780, 500
ML, MR, MT, MB = 82, 214, 70, 78
PW, PH = W - ML - MR, H - MT - MB
XMIN, XMAX = 1000.0, 2450.0
YMIN, YMAX = 0.0, 0.72

def sx(m): return ML + (m - XMIN) / (XMAX - XMIN) * PW
def sy(d): return MT + PH - (d - YMIN) / (YMAX - YMIN) * PH

INK, MUTE, GRID = '#1a1a1a', '#5c5c5c', '#dcdcdc'
COLORS = {48: '#1f6f9c', 64: '#c0392b', 96: '#2e7d32'}
DASH = {48: '5,3', 64: 'none', 96: '1,0'}

s = []
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')

for i in range(7):
    d = YMIN + (YMAX - YMIN) * i / 6
    y = sy(d)
    s.append(f'<line x1="{ML}" y1="{y:.1f}" x2="{ML+PW}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
    s.append(f'<text x="{ML-9}" y="{y+4:.1f}" font-size="11.5" fill="{MUTE}" text-anchor="end">{d:.2f}</text>')
for m in MASSES:
    x = sx(m)
    s.append(f'<line x1="{x:.1f}" y1="{MT}" x2="{x:.1f}" y2="{MT+PH}" stroke="{GRID}" stroke-width="1" stroke-dasharray="2,3"/>')
    s.append(f'<text x="{x:.1f}" y="{MT+PH+20}" font-size="11.5" fill="{MUTE}" text-anchor="middle">{int(m)}</text>')
s.append(f'<rect x="{ML}" y="{MT}" width="{PW}" height="{PH}" fill="none" stroke="{INK}" stroke-width="1.2"/>')

for g in GRIDS:
    col = COLORS[g]
    pts = [(sx(m), sy(float(by[(g, m)]['final_disp_mag_m']))) for m in MASSES]
    da = '' if DASH[g] in ('none', '1,0') else f' stroke-dasharray="{DASH[g]}"'
    s.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
             f'fill="none" stroke="{col}" stroke-width="2.6"{da}/>')
    for m, (x, y) in zip(MASSES, pts):
        r = by[(g, m)]
        flagged = float(r['passthrough_max_frac']) > GATE
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.4" fill="{col}" stroke="white" stroke-width="1.6"/>')
        if flagged:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="none" stroke="#6a1b9a" '
                     f'stroke-width="2.2" stroke-dasharray="3,2.5"/>')
    # label each line at its right end
    lx, ly = pts[-1]
    s.append(f'<text x="{ML+PW+8:.1f}" y="{ly+4:.1f}" font-size="11.5" fill="{col}" '
             f'font-weight="bold">n_grid = {g}</text>')

s.append(f'<text x="{ML+PW/2:.1f}" y="{H-38}" font-size="13" fill="{INK}" text-anchor="middle">'
         f'Vehicle mass (kg), applied as a mass override to one fixed hull</text>')
s.append(f'<text x="20" y="{MT+PH/2:.1f}" font-size="13" fill="{INK}" text-anchor="middle" '
         f'transform="rotate(-90 20 {MT+PH/2:.1f})">L2 final displacement (m)</text>')
s.append(f'<text x="{ML}" y="26" font-size="14" fill="{INK}" font-weight="bold">'
         f'Coupled-MPM displacement vs. vehicle mass, at three grid resolutions</text>')
s.append(f'<text x="{ML}" y="43" font-size="10.5" fill="{MUTE}">'
         f'{len(rows)} runs, {SCEN.replace("_", " ")}, depth {D_FIX} m, velocity {V_FIX} m/s</text>')
s.append(f'<text x="{ML}" y="58" font-size="10.5" fill="#8a1c12">'
         f'Direction is consistent at every resolution; the magnitude is not. The lines do not '
         f'overlay, so the effect size is not grid-converged.</text>')

# the three lines are labelled inline at their right ends, so no colour legend is
# repeated here; only the gate marker needs explaining
lx, ly = ML + PW + 22, MT + 8
gy = ly + 40
s.append(f'<circle cx="{lx+10}" cy="{gy-4}" r="6.4" fill="#9e9e9e" stroke="white" stroke-width="1.4"/>')
s.append(f'<circle cx="{lx+10}" cy="{gy-4}" r="12" fill="none" stroke="#6a1b9a" stroke-width="2.2" stroke-dasharray="3,2.5"/>')
s.append(f'<text x="{lx+30}" y="{gy}" font-size="11" fill="#6a1b9a" font-weight="bold">gate exceeded</text>')
s.append(f'<text x="{lx}" y="{gy+17}" font-size="10" fill="{MUTE}">particle passthrough</text>')
s.append(f'<text x="{lx}" y="{gy+30}" font-size="10" fill="{MUTE}">above {GATE:.0%}. Flagged,</text>')
s.append(f'<text x="{lx}" y="{gy+43}" font-size="10" fill="{MUTE}">not excluded.</text>')
s.append(f'<text x="{lx}" y="{gy+64}" font-size="10" fill="{MUTE}">{len(over)} of {len(allrows)} runs in the</text>')
s.append(f'<text x="{lx}" y="{gy+77}" font-size="10" fill="{MUTE}">full inventory exceed it.</text>')

s.append(f'<text x="{ML}" y="{H-8}" font-size="9" fill="#8a8a8a">'
         f'source: data/all_runs_inventory.csv, sweep=mass_grid rows; no ratio or multiplier is '
         f'reported because the magnitude is not grid-converged</text>')
s.append('</svg>')

OUT.write_text("\n".join(s), encoding='utf-8')
print(f"\nwrote {OUT}  ({OUT.stat().st_size} bytes)")
