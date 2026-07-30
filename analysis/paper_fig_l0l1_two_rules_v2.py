import csv
import os
from pathlib import Path

REPO = Path('/Users/josie/can-it-ford')
os.chdir(REPO)
SRC = REPO / 'data' / 'scenario_sweep.csv'
OUTDIR = REPO / 'paper' / 'figures_review'
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / 'l0l1_two_rules_v2.svg'

rows = list(csv.DictReader(open(SRC)))
assert len(rows) == 70, f"expected 70 rows, got {len(rows)}"
print(f"source: {SRC}  rows={len(rows)}")
print("columns read as-is: L0_verdict, L1_haz_product_only, L1_verdict")
print("no verdict in this figure is recomputed from an inline threshold")

DEPTHS = sorted({float(r['depth_m']) for r in rows})
VELS = sorted({float(r['velocity_ms']) for r in rows})
assert len(DEPTHS) * len(VELS) == len(rows), "grid is not complete"
print(f"grid: {len(DEPTHS)} depths x {len(VELS)} velocities = {len(rows)}")

PRODUCT_CAP = 0.60


def binding_caps(col):
    ford = [r for r in rows if r[col] == 'FORD']
    return (max(float(r['depth_m']) for r in ford),
            max(float(r['depth_m']) * float(r['velocity_ms']) for r in ford))

BARE_DCAP, BARE_PCAP = binding_caps('L1_haz_product_only')
JOINT_DCAP, JOINT_PCAP = binding_caps('L1_verdict')
assert abs(BARE_DCAP - max(DEPTHS)) < 1e-9, "the bare column does bound depth, relabel the left panel"
assert abs(BARE_PCAP - PRODUCT_CAP) < 1e-9, "the bare column product cap is not the labelled value"
CLASS_MATCH = sum(1 for r in rows if r['L1_verdict'] == r['L1_verdict_small_passenger'])
assert CLASS_MATCH == len(rows), "L1_verdict is no longer the small-passenger column"
print(f"\nL1_verdict agrees with L1_verdict_small_passenger on {CLASS_MATCH}/{len(rows)} rows")
print(f"bare column  : no depth cap binds (max FORD depth {BARE_DCAP:.2f} m = grid max), "
      f"D*V cap {BARE_PCAP:.2f} m^2/s")
print(f"joint column : depth cap {JOINT_DCAP:.2f} m, D*V cap {JOINT_PCAP:.2f} m^2/s")
print("the two panels therefore sit on DIFFERENT AR&R vehicle classes, "
      "which the panel subtitles now state outright")

PANELS = [
    ('L1_haz_product_only', 'Bare rule (D&#215;V only)',
     f'L1 = FORD when D&#215;V &#8804; {BARE_PCAP:.2f} m&#178;/s, no depth cap'),
    ('L1_verdict', 'Joint rule (depth, velocity, and D&#215;V)',
     f'L1 = FORD when depth &#8804; {JOINT_DCAP:.2f} m and D&#215;V &#8804; {JOINT_PCAP:.2f} m&#178;/s'),
]


def classify(r, col):
    l0, l1 = r['L0_verdict'], r[col]
    if l0 == 'FORD' and l1 == 'FORD':
        return 'both'
    if l0 == 'NO-FORD' and l1 == 'FORD':
        return 'l1only'
    if l0 == 'FORD' and l1 == 'NO-FORD':
        return 'l0only'
    return 'neither'


stats = {}
for col, _, _ in PANELS:
    c = {k: 0 for k in ('both', 'l1only', 'l0only', 'neither')}
    for r in rows:
        c[classify(r, col)] += 1
    stats[col] = c
    print(f"\n{col}:")
    print(f"   both permit                    : {c['both']}")
    print(f"   L1 permits, L0 refuses         : {c['l1only']}   <-- the highlighted count")
    print(f"   L0 permits, L1 refuses         : {c['l0only']}")
    print(f"   both refuse                    : {c['neither']}")
    print(f"   total L1 FORD                  : {c['both'] + c['l1only']}")

print(f"\nL0_verdict FORD total: {sum(1 for r in rows if r['L0_verdict'] == 'FORD')}")

print("\nlabel check, inferred from the data instead of assumed:")
for col, _, _ in PANELS:
    ford = [float(r['depth_m']) * float(r['velocity_ms']) for r in rows if r[col] == 'FORD']
    noford = [float(r['depth_m']) * float(r['velocity_ms']) for r in rows if r[col] == 'NO-FORD']
    depths_ford = [float(r['depth_m']) for r in rows if r[col] == 'FORD']
    print(f"  {col}")
    print(f"     max D*V among FORD    : {max(ford):.4f} m^2/s")
    print(f"     min D*V among NO-FORD : {min(noford):.4f} m^2/s")
    print(f"     max depth among FORD  : {max(depths_ford):.2f} m")

bare_ford = [float(r['depth_m']) * float(r['velocity_ms'])
             for r in rows if r['L1_haz_product_only'] == 'FORD']
bare_noford = [float(r['depth_m']) * float(r['velocity_ms'])
               for r in rows if r['L1_haz_product_only'] == 'NO-FORD']
assert max(bare_ford) <= PRODUCT_CAP + 1e-9, "bare-rule FORD rows exceed the labelled D*V cap"
assert min(bare_noford) > PRODUCT_CAP - 1e-9, "bare-rule NO-FORD rows fall under the labelled D*V cap"
print(f"  the {PRODUCT_CAP:.2f} m^2/s printed on the left panel separates that column exactly")

HI = stats['L1_haz_product_only']['l1only']
LO = stats['L1_verdict']['l1only']
DROP = HI - LO
TOT_HI = stats['L1_haz_product_only']['both'] + HI
TOT_LO = stats['L1_verdict']['both'] + LO
assert HI == 30, "bare-rule highlight count moved off 30"
assert LO == 7, "joint-rule highlight count moved off 7"
assert TOT_HI == 37, "bare-rule total L1 permits moved off 37"
assert TOT_LO == 14, "joint-rule total L1 permits moved off 14"
print(f"\nhighlighted counts {HI} and {LO} match the values reported to the user")
print(f"totals {TOT_HI} of {len(rows)} and {TOT_LO} of {len(rows)} match the values reported to the user")
print(f"reduction drawn between the panels: {HI} -> {LO}, a drop of {DROP}")
assert TOT_HI - TOT_LO == DROP, "totals and highlighted counts disagree on the size of the drop"
print(f"the totals fall by the same {DROP}, so the drop is one number, not two")

L0_ONLY = {col: stats[col]['l0only'] for col, _, _ in PANELS}
NEVER_L0_ONLY = all(v == 0 for v in L0_ONLY.values())
print(f"\nL0 permits and L1 refuses, per column: {L0_ONLY}")
if NEVER_L0_ONLY:
    FINDING = 'L0 permits and L1 refuses never occurs in this dataset.'
    print("  zero rows in both columns, so the figure states the finding line")
else:
    FINDING = (f'L0 permits and L1 refuses occurs in '
               f'{max(L0_ONLY.values())} of {len(rows)} scenarios.')
    print("  NON-ZERO, the finding line is replaced by the measured count")

PW, PH = 268, 300
GAP = 136
ML, MT = 74, 102
MB, MR = 118, 20
W = ML + PW * 2 + GAP + MR
H = MT + PH + MB

BW, BH = 112, 148
BX = ML + PW + (GAP - BW) / 2
BY = MT + (PH - BH) / 2
BCX = BX + BW / 2

INK, MUTE, GRID = '#1a1a1a', '#5c5c5c', '#dcdcdc'
C_BOTH, C_L1, C_NEITHER, C_L0 = '#2e7d32', '#e07b00', '#c9c9c9', '#6a1b9a'
C_L1_DARK, C_L1_TINT = '#7a4300', '#fff4e6'

s = []
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
s.append(f'<rect width="{W}" height="{H}" fill="white"/>')


def panel(idx, col, title, subtitle):
    x0 = ML + idx * (PW + GAP)
    y0 = MT

    def cx(v):
        return x0 + (VELS.index(v) + 0.5) * (PW / len(VELS))

    def cy(d):
        return y0 + PH - (DEPTHS.index(d) + 0.5) * (PH / len(DEPTHS))

    s.append(f'<rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" fill="none" '
             f'stroke="{INK}" stroke-width="1.2"/>')
    for i in range(1, len(VELS)):
        gx = x0 + i * (PW / len(VELS))
        s.append(f'<line x1="{gx:.1f}" y1="{y0}" x2="{gx:.1f}" y2="{y0+PH}" '
                 f'stroke="{GRID}" stroke-width="0.7"/>')
    for i in range(1, len(DEPTHS)):
        gy = y0 + i * (PH / len(DEPTHS))
        s.append(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x0+PW}" y2="{gy:.1f}" '
                 f'stroke="{GRID}" stroke-width="0.7"/>')

    for r in rows:
        d, v = float(r['depth_m']), float(r['velocity_ms'])
        k = classify(r, col)
        X, Y = cx(v), cy(d)
        if k == 'l1only':
            s.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="7.6" fill="{C_L1}" '
                     f'stroke="{C_L1_DARK}" stroke-width="1.7"/>')
        elif k == 'both':
            s.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="6.0" fill="{C_BOTH}" '
                     f'stroke="white" stroke-width="1.2"/>')
        elif k == 'l0only':
            s.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="6.6" fill="{C_L0}" '
                     f'stroke="white" stroke-width="1.2"/>')
        else:
            s.append(f'<line x1="{X-3.6:.1f}" y1="{Y-3.6:.1f}" x2="{X+3.6:.1f}" y2="{Y+3.6:.1f}" '
                     f'stroke="{C_NEITHER}" stroke-width="1.9"/>')
            s.append(f'<line x1="{X-3.6:.1f}" y1="{Y+3.6:.1f}" x2="{X+3.6:.1f}" y2="{Y-3.6:.1f}" '
                     f'stroke="{C_NEITHER}" stroke-width="1.9"/>')

    for v in VELS:
        s.append(f'<text x="{cx(v):.1f}" y="{y0+PH+17}" font-size="9.5" fill="{MUTE}" '
                 f'text-anchor="middle">{v:.1f}</text>')
    if idx == 0:
        for d in DEPTHS:
            s.append(f'<text x="{x0-8}" y="{cy(d)+3.5:.1f}" font-size="9.5" fill="{MUTE}" '
                     f'text-anchor="end">{d:.1f}</text>')

    c = stats[col]
    s.append(f'<text x="{x0+PW/2:.1f}" y="{y0-38}" font-size="12.5" fill="{INK}" '
             f'font-weight="bold" text-anchor="middle">{title}</text>')
    s.append(f'<text x="{x0+PW/2:.1f}" y="{y0-23}" font-size="9.8" fill="{MUTE}" '
             f'text-anchor="middle">{subtitle}</text>')
    s.append(f'<text x="{x0+PW/2:.1f}" y="{y0-7}" font-size="10.5" fill="{C_L1_DARK}" '
             f'font-weight="bold" text-anchor="middle">'
             f'{c["l1only"]} scenarios: L1 permits, L0 refuses</text>')
    s.append(f'<text x="{x0+PW/2:.1f}" y="{y0+PH+34}" font-size="10" fill="{MUTE}" '
             f'text-anchor="middle">Flow velocity (m/s)</text>')
    s.append(f'<text x="{x0+PW/2:.1f}" y="{y0+PH+50}" font-size="9.6" fill="{INK}" '
             f'text-anchor="middle">total L1 permits: '
             f'{c["both"]+c["l1only"]} of {len(rows)}</text>')


for i, (col, t, sub) in enumerate(PANELS):
    panel(i, col, t, sub)

s.append(f'<rect x="{BX:.1f}" y="{BY:.1f}" width="{BW}" height="{BH}" rx="9" '
         f'fill="{C_L1_TINT}" stroke="{C_L1}" stroke-width="1.6"/>')
s.append(f'<text x="{BCX:.1f}" y="{BY+18:.1f}" font-size="9" fill="{MUTE}" '
         f'text-anchor="middle">L1 permits,</text>')
s.append(f'<text x="{BCX:.1f}" y="{BY+30:.1f}" font-size="9" fill="{MUTE}" '
         f'text-anchor="middle">L0 refuses</text>')
s.append(f'<text x="{BCX:.1f}" y="{BY+74:.1f}" font-size="32" fill="{C_L1_DARK}" '
         f'font-weight="bold" text-anchor="middle">&#8722;{DROP}</text>')
s.append(f'<text x="{BCX:.1f}" y="{BY+90:.1f}" font-size="9.5" fill="{MUTE}" '
         f'text-anchor="middle">scenarios</text>')
s.append(f'<line x1="{BCX-40:.1f}" y1="{BY+104:.1f}" x2="{BCX+40:.1f}" y2="{BY+104:.1f}" '
         f'stroke="{C_L1}" stroke-width="0.9"/>')
s.append(f'<text x="{BCX-27:.1f}" y="{BY+120:.1f}" font-size="8.5" fill="{MUTE}" '
         f'text-anchor="middle">bare</text>')
s.append(f'<text x="{BCX+27:.1f}" y="{BY+120:.1f}" font-size="8.5" fill="{MUTE}" '
         f'text-anchor="middle">joint</text>')
s.append(f'<text x="{BCX-27:.1f}" y="{BY+136:.1f}" font-size="13" fill="{INK}" '
         f'font-weight="bold" text-anchor="middle">{HI}</text>')
s.append(f'<text x="{BCX:.1f}" y="{BY+136:.1f}" font-size="13" fill="{C_L1_DARK}" '
         f'text-anchor="middle">&#8594;</text>')
s.append(f'<text x="{BCX+27:.1f}" y="{BY+136:.1f}" font-size="13" fill="{INK}" '
         f'font-weight="bold" text-anchor="middle">{LO}</text>')

s.append(f'<text x="20" y="{MT+PH/2:.1f}" font-size="11.5" fill="{INK}" text-anchor="middle" '
         f'transform="rotate(-90 20 {MT+PH/2:.1f})">Water depth (m)</text>')
s.append(f'<text x="{ML}" y="26" font-size="14" fill="{INK}" font-weight="bold">'
         f'Which L1 formula matters: bare hazard scalar vs. joint depth-and-velocity rule</text>')
s.append(f'<text x="{ML}" y="43" font-size="10" fill="{MUTE}">'
         f'All {len(rows)} scenarios of data/scenario_sweep.csv. Verdict columns read as-is; '
         f'no threshold recomputed in this figure.</text>')

ly = MT + PH + 70
lx = ML


def legitem(dx, swatch, label):
    s.append(swatch)
    s.append(f'<text x="{lx+dx+15}" y="{ly+4}" font-size="10" fill="{INK}">{label}</text>')


legitem(0, f'<circle cx="{lx+5}" cy="{ly}" r="6.0" fill="{C_BOTH}" stroke="white" stroke-width="1.2"/>',
        'both permit')
legitem(131, f'<circle cx="{lx+133}" cy="{ly}" r="7.6" fill="{C_L1}" stroke="{C_L1_DARK}" stroke-width="1.7"/>',
        'L1 permits, L0 refuses')
legitem(300, f'<line x1="{lx+301.4}" y1="{ly-3.6}" x2="{lx+308.6}" y2="{ly+3.6}" stroke="{C_NEITHER}" stroke-width="1.9"/>'
             f'<line x1="{lx+301.4}" y1="{ly+3.6}" x2="{lx+308.6}" y2="{ly-3.6}" stroke="{C_NEITHER}" stroke-width="1.9"/>',
        'both refuse')
if not NEVER_L0_ONLY:
    legitem(410, f'<circle cx="{lx+415}" cy="{ly}" r="6.6" fill="{C_L0}" stroke="white" stroke-width="1.2"/>',
            'L0 permits, L1 refuses')

s.append(f'<text x="{ML}" y="{ly+22}" font-size="10" fill="{INK}">{FINDING}</text>')
s.append(f'<text x="{ML}" y="{H-6}" font-size="9" fill="#8a8a8a">'
         f'source: data/scenario_sweep.csv, columns L0_verdict, L1_haz_product_only, L1_verdict</text>')
s.append('</svg>')

OUT.write_text("\n".join(s), encoding='utf-8')
print(f"\nwrote {OUT}  ({OUT.stat().st_size} bytes)  svg {W} x {H}")
