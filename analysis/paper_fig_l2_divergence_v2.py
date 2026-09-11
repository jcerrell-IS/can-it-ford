"""Build the REAL L1-vs-L2 divergence figure for paper/conference_101719.tex,
replacing the SCHEMATIC placeholder at fig:l2schematic.

PROVENANCE, read live at run time, nothing hardcoded:
  data/l2_results_from_wandb.csv   9 rows, one per (depth, velocity) condition

RULES THIS SCRIPT OBEYS:
  * Verdicts are READ from the l1_verdict / l2_verdict columns. This script does
    NOT recompute an L1 verdict from an inline threshold. That inline-recompute
    pattern is the known defect in analysis/make_phase_space_v2.py:9,
    analysis/plot_phase_space_live.py:7 and
    designsafe-staging/scripts/make_phase_space.py:9.
  * The iso-hazard threshold drawn is read from the l1_threshold column, not
    typed in as a literal.
  * No point is interpolated, estimated or added. Exactly the 9 rows present.
  * Stdlib only. This machine has no matplotlib (verified: import fails on both
    /usr/bin/python3 and /opt/homebrew/bin/python3), so the figure is emitted as
    hand-written SVG rather than via a plotting library.

Output: paper/figures_review/l2_divergence_real_v2.svg  (NEW file, overwrites nothing)
"""
import csv
import os
from pathlib import Path

REPO = Path('/Users/josie/can-it-ford')
os.chdir(REPO)
SRC = REPO / 'data' / 'l2_results_from_wandb.csv'
OUTDIR = REPO / 'paper' / 'figures_review'
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / 'l2_divergence_real_v2.svg'

rows = list(csv.DictReader(open(SRC)))
assert len(rows) == 9, f"expected 9 rows, got {len(rows)}"

# ---- integrity checks, printed so they land in the session record ----
print(f"source: {SRC}  rows={len(rows)}")
thresholds = {r['l1_threshold'] for r in rows}
assert len(thresholds) == 1, f"multiple l1_threshold values: {thresholds}"
THRESH = float(thresholds.pop())
print(f"l1_threshold column: single value {THRESH} m^2/s (drawn as the iso-hazard curve)")

print("\n--- which L1 rule does the l1_verdict column actually implement? ---")
bare_ok = joint_ok = True
DEPTH_CAP_4WD = 0.50   # AR&R large-4WD depth cap, per analysis/four_rung_ladder.py:18
for r in rows:
    d, v = float(r['depth_m']), float(r['velocity_ms'])
    dv = d * v
    bare = 'FORD' if dv <= THRESH + 1e-9 else 'NO-FORD'
    joint = 'FORD' if (dv <= THRESH + 1e-9 and d <= DEPTH_CAP_4WD + 1e-9) else 'NO-FORD'
    if bare != r['l1_verdict']:
        bare_ok = False
    if joint != r['l1_verdict']:
        joint_ok = False
print(f"  matches BARE product rule (D*V <= {THRESH})              : {bare_ok}")
print(f"  matches JOINT rule (D*V cap AND depth cap {DEPTH_CAP_4WD} m) : {joint_ok}")

print("\n--- anomaly scan: does l1_haz_score equal depth*velocity on every row? ---")
anomalies = []
for r in rows:
    d, v = float(r['depth_m']), float(r['velocity_ms'])
    haz, dvp = float(r['l1_haz_score']), float(r['dv_product'])
    if abs(haz - d * v) > 1e-6:
        anomalies.append((r['name'], d, v, d * v, dvp, haz))
if anomalies:
    for nm, d, v, prod, dvp, haz in anomalies:
        print(f"  ANOMALY {nm}: depth*vel={prod:.4f}  dv_product={dvp:.4f}  "
              f"l1_haz_score={haz:.4f}  <-- haz disagrees")
else:
    print("  none")
print("  NOTE: this figure plots dv_product, which is internally consistent, and\n"
      "        never l1_haz_score. The anomalous cell is annotated in the figure.")

# ---- classify, straight from the two verdict columns ----
pts = []
for r in rows:
    d, v = float(r['depth_m']), float(r['velocity_ms'])
    l1, l2 = r['l1_verdict'], r['l2_verdict']
    diverge = r['divergence'].strip().lower() == 'true'
    if diverge:
        kind = 'diverge'
    elif l1 == 'FORD':
        kind = 'agree_ford'
    else:
        kind = 'agree_noford'
    pts.append(dict(d=d, v=v, l1=l1, l2=l2, kind=kind,
                    dv=float(r['dv_product']), name=r['name'],
                    anom=any(a[0] == r['name'] for a in anomalies)))

n_div = sum(1 for p in pts if p['kind'] == 'diverge')
n_af = sum(1 for p in pts if p['kind'] == 'agree_ford')
n_an = sum(1 for p in pts if p['kind'] == 'agree_noford')
agree_pct = 100.0 * (len(pts) - n_div) / len(pts)
print(f"\nclassification: agree-FORD={n_af}  agree-NO-FORD={n_an}  diverge={n_div}  "
      f"agreement={agree_pct:.1f}%")

dirs = {(p['l1'], p['l2']) for p in pts if p['kind'] == 'diverge'}
print(f"divergence directions present: {sorted(dirs)}")
assert dirs == {('FORD', 'NO-FORD')}, "unexpected divergence direction"
print("  -> every disagreement is L1 permissive / L2 restrictive. No reverse cases.")

# ---------------- SVG ----------------
W, H = 760, 500
ML, MR, MT, MB = 78, 232, 46, 62
PW, PH = W - ML - MR, H - MT - MB
VMAX, DMAX = 2.20, 0.70
DTICK, VTICK = 0.10, 0.50
DTICKS = [round(i * DTICK, 6) for i in range(int(DMAX / DTICK + 1e-9) + 1)]
VTICKS = [round(i * VTICK, 6) for i in range(int(VMAX / VTICK + 1e-9) + 1)]
print(f"\ndepth ticks  (step {DTICK:g} m):    {DTICKS}")
print(f"velocity ticks (step {VTICK:g} m/s): {VTICKS}")

def sx(v): return ML + (v / VMAX) * PW
def sy(d): return MT + PH - (d / DMAX) * PH

INK, MUTE, GRID = '#1a1a1a', '#5c5c5c', '#d8d8d8'
C_FORD, C_NOFORD, C_DIV = '#2e7d32', '#c62828', '#e07b00'

s = []
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')

# grid + axes
for d in DTICKS:
    y = sy(d)
    s.append(f'<line x1="{ML}" y1="{y:.1f}" x2="{ML+PW}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
    s.append(f'<text x="{ML-9}" y="{y+4:.1f}" font-size="12" fill="{MUTE}" text-anchor="end">{d:.1f}</text>')
for v in VTICKS:
    x = sx(v)
    s.append(f'<line x1="{x:.1f}" y1="{MT}" x2="{x:.1f}" y2="{MT+PH}" stroke="{GRID}" stroke-width="1"/>')
    s.append(f'<text x="{x:.1f}" y="{MT+PH+20}" font-size="12" fill="{MUTE}" text-anchor="middle">{v:.1f}</text>')
s.append(f'<rect x="{ML}" y="{MT}" width="{PW}" height="{PH}" fill="none" stroke="{INK}" stroke-width="1.2"/>')

# iso-hazard curve d*v = THRESH, from the l1_threshold column
seg = []
steps = 400
for i in range(steps + 1):
    v = 0.001 + (VMAX - 0.001) * i / steps
    d = THRESH / v
    if d > DMAX:
        continue
    seg.append(f'{sx(v):.2f},{sy(d):.2f}')
s.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="{INK}" '
         f'stroke-width="2" stroke-dasharray="7,4"/>')
# the curve is identified in the legend, not by an inline label, so that nothing
# overlaps the legend column or the markers

# markers
def marker(p):
    x, y = sx(p['v']), sy(p['d'])
    if p['kind'] == 'diverge':
        r = 9.5
        return (f'<polygon points="{x:.1f},{y-r:.1f} {x+r:.1f},{y:.1f} {x:.1f},{y+r:.1f} '
                f'{x-r:.1f},{y:.1f}" fill="{C_DIV}" stroke="#7a4300" stroke-width="2"/>')
    if p['kind'] == 'agree_ford':
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="{C_FORD}" stroke="white" stroke-width="1.6"/>'
    r = 7.0
    return (f'<rect x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" '
            f'fill="{C_NOFORD}" stroke="white" stroke-width="1.6"/>')

for p in pts:
    s.append(marker(p))
for p in pts:
    if p['anom']:
        x, y = sx(p['v']), sy(p['d'])
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="none" '
                 f'stroke="#4527a0" stroke-width="1.8" stroke-dasharray="3,3"/>')
        # annotate below-left, clear of the iso-hazard curve and the legend column
        s.append(f'<text x="{x-19:.1f}" y="{y+31:.1f}" font-size="11" fill="#4527a0" '
                 f'text-anchor="end">&#8225; haz cell, see caption</text>')

# axis titles
s.append(f'<text x="{ML+PW/2:.1f}" y="{H-16}" font-size="13.5" fill="{INK}" '
         f'text-anchor="middle">Flow velocity (m/s)</text>')
s.append(f'<text x="18" y="{MT+PH/2:.1f}" font-size="13.5" fill="{INK}" text-anchor="middle" '
         f'transform="rotate(-90 18 {MT+PH/2:.1f})">Water depth (m)</text>')
s.append(f'<text x="{ML}" y="{MT-18}" font-size="14.5" fill="{INK}" font-weight="bold">'
         f'L1 hazard scalar vs. coupled L2 simulation, {len(pts)} measured conditions</text>')

# legend
lx, ly = ML + PW + 20, MT + 6
def leg(dy, swatch, text):
    s.append(swatch)
    s.append(f'<text x="{lx+22}" y="{ly+dy+4}" font-size="12" fill="{INK}">{text}</text>')

leg(0, f'<circle cx="{lx+8}" cy="{ly}" r="7.5" fill="{C_FORD}" stroke="white" stroke-width="1.6"/>',
    f'Agree, both FORD ({n_af})')
leg(26, f'<rect x="{lx+1}" y="{ly+19}" width="14" height="14" fill="{C_NOFORD}" stroke="white" stroke-width="1.6"/>',
    f'Agree, both NO-FORD ({n_an})')
leg(52, f'<polygon points="{lx+8},{ly+42.5} {lx+17.5},{ly+52} {lx+8},{ly+61.5} {lx-1.5},{ly+52}" '
        f'fill="{C_DIV}" stroke="#7a4300" stroke-width="2"/>',
    f'Disagree ({n_div})')
s.append(f'<text x="{lx+22}" y="{ly+72}" font-size="11" fill="{MUTE}">L1 says FORD,</text>')
s.append(f'<text x="{lx+22}" y="{ly+86}" font-size="11" fill="{MUTE}">L2 says NO-FORD</text>')

# iso-hazard curve as a legend entry, so no inline label can collide
s.append(f'<line x1="{lx}" y1="{ly+106}" x2="{lx+17}" y2="{ly+106}" stroke="{INK}" '
         f'stroke-width="2" stroke-dasharray="7,4"/>')
s.append(f'<text x="{lx+22}" y="{ly+110}" font-size="12" fill="{INK}">'
         f'L1 iso-hazard</text>')
s.append(f'<text x="{lx+22}" y="{ly+125}" font-size="11" fill="{MUTE}">'
         f'D&#215;V = {THRESH:g} m&#178;/s</text>')

s.append(f'<line x1="{lx}" y1="{ly+144}" x2="{lx+200}" y2="{ly+144}" stroke="{GRID}" stroke-width="1"/>')
s.append(f'<text x="{lx}" y="{ly+164}" font-size="12" fill="{INK}" font-weight="bold">'
         f'Agreement: {agree_pct:.1f}%</text>')
s.append(f'<text x="{lx}" y="{ly+181}" font-size="11" fill="{MUTE}">{len(pts)-n_div} of {len(pts)} conditions</text>')
s.append(f'<text x="{lx}" y="{ly+205}" font-size="11" fill="{MUTE}">All {n_div} disagreements run</text>')
s.append(f'<text x="{lx}" y="{ly+219}" font-size="11" fill="{MUTE}">one way: L1 permits,</text>')
s.append(f'<text x="{lx}" y="{ly+233}" font-size="11" fill="{MUTE}">L2 refuses. No reverse</text>')
s.append(f'<text x="{lx}" y="{ly+247}" font-size="11" fill="{MUTE}">cases in this dataset.</text>')

s.append(f'<text x="{ML}" y="{H-2}" font-size="9.5" fill="#8a8a8a">'
         f'source: data/l2_results_from_wandb.csv (9 rows), verdict columns read as-is; '
         f'threshold from l1_threshold column</text>')
s.append('</svg>')

OUT.write_text("\n".join(s), encoding='utf-8')
print(f"\nwrote {OUT}  ({OUT.stat().st_size} bytes)")
print("\nper-point table as plotted:")
for p in sorted(pts, key=lambda p: (p['d'], p['v'])):
    print(f"  d={p['d']:.2f} v={p['v']:.2f} dv={p['dv']:.3f} L1={p['l1']:8s} "
          f"L2={p['l2']:8s} {p['kind']}{'  [haz anomaly]' if p['anom'] else ''}")
