import csv
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

JOINT_DEPTH_CAP = 0.30
JOINT_VEL_CAP = 3.0
JOINT_PRODUCT_CAP = 0.30
BARE_PRODUCT_CAP = 0.60

EXPECT_ROWS = 70
EXPECT_JOINT_FORD = 14
EXPECT_BARE_FORD = 37
EXPECT_RECLASS = 23


def first_existing(*paths):
    for p in paths:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError('none of: ' + ', '.join(paths))


SWEEP_CSV = first_existing(
    os.path.join(HERE, 'scenario_sweep.csv'),
    os.path.join(REPO, 'designsafe-staging', 'scenario_sweep.csv'),
    os.path.join(REPO, 'data', 'scenario_sweep.csv'),
)
L2_CSV = first_existing(
    os.path.join(HERE, 'phase_space_results.csv'),
    os.path.join(REPO, 'designsafe-staging', 'phase_space_results.csv'),
    os.path.join(REPO, 'data', 'phase_space_results.csv'),
)
OUT_PNG = os.path.join(HERE, 'can_it_ford_phase_space_v2_JOINTRULE.png')

print(f'sweep CSV : {SWEEP_CSV}')
print(f'L2 CSV    : {L2_CSV}')


def joint_rule(d, v):
    if d <= JOINT_DEPTH_CAP and v <= JOINT_VEL_CAP and round(d * v, 6) <= JOINT_PRODUCT_CAP:
        return 'FORD'
    return 'NO-FORD'


with open(SWEEP_CSV, newline='', encoding='utf-8-sig') as fh:
    sweep_rows = list(csv.DictReader(fh))

sweep_table = {}
for r in sweep_rows:
    sweep_table[(round(float(r['depth_m']), 6), round(float(r['velocity_ms']), 6))] = r['L1_verdict']

joint_ford = sum(1 for r in sweep_rows if r['L1_verdict'] == 'FORD')
bare_ford = sum(1 for r in sweep_rows if r['L1_haz_product_only'] == 'FORD')
reclass = sum(1 for r in sweep_rows
              if r['L1_haz_product_only'] == 'FORD' and r['L1_verdict'] == 'NO-FORD')
reverse = sum(1 for r in sweep_rows
              if r['L1_haz_product_only'] == 'NO-FORD' and r['L1_verdict'] == 'FORD')

print('L1 JOINT RULE AUDIT')
print(f'  rows {len(sweep_rows)}, joint FORD {joint_ford}, bare FORD {bare_ford}, '
      f'reclassified {reclass}, reverse {reverse}')
assert len(sweep_rows) == EXPECT_ROWS
assert joint_ford == EXPECT_JOINT_FORD
assert bare_ford == EXPECT_BARE_FORD
assert reclass == EXPECT_RECLASS
assert reverse == 0

df = pd.read_csv(L2_CSV)
df = df.drop_duplicates(subset=['depth_m', 'velocity_ms'], keep='last')

verdicts = []
sources = []
for _, row in df.iterrows():
    key = (round(float(row['depth_m']), 6), round(float(row['velocity_ms']), 6))
    if key in sweep_table:
        verdicts.append(sweep_table[key])
        sources.append('sweep')
    else:
        verdicts.append(joint_rule(float(row['depth_m']), float(row['velocity_ms'])))
        sources.append('derived')
df['L1_verdict'] = verdicts
df['L1_source'] = sources
print(f'  L2 rows {len(df)}, L1 from sweep {sources.count("sweep")}, '
      f'L1 derived {sources.count("derived")}')


def classify(row):
    if row['verdict'] == 'FORD' and row['L1_verdict'] == 'FORD':
        return 'FORD_AGREE'
    if row['verdict'] == 'NO-FORD' and row['L1_verdict'] == 'NO-FORD':
        return 'NOFORD_AGREE'
    if row['verdict'] == 'NO-FORD' and row['L1_verdict'] == 'FORD':
        return 'DIVERGE'
    return 'OTHER'


df['category'] = df.apply(classify, axis=1)

fig, ax = plt.subplots(figsize=(11, 6.5))
ax.set_facecolor('#fafafa')

d_arr = np.linspace(0.07, 0.75, 500)
joint_v = np.where(d_arr <= JOINT_DEPTH_CAP,
                   np.minimum(JOINT_PRODUCT_CAP / d_arr, JOINT_VEL_CAP), 0.0)
ax.fill_between(d_arr, 0, joint_v, alpha=0.10, color='#4dac26')
ax.fill_between(d_arr, joint_v, JOINT_VEL_CAP, alpha=0.08, color='#d01c8b')
ax.plot(d_arr, joint_v, color='#2d7a16', lw=2.6, zorder=5,
        label='L1 joint rule: depth ≤ 0.30 m AND D×V ≤ 0.30 m²/s AND v ≤ 3.0 m/s')
ax.plot(d_arr, np.minimum(BARE_PRODUCT_CAP / d_arr, JOINT_VEL_CAP),
        color='#e07b00', lw=2.0, linestyle='-.', zorder=4,
        label='bare hazard rule for contrast: D×V ≤ 0.60 m²/s only')

ax.axvline(JOINT_DEPTH_CAP, color='#2d7a16', lw=1.4, linestyle=':',
           label='L1 class depth cap (0.30 m)', zorder=3)
ax.axvline(0.15, color='#333333', lw=1.4, linestyle='--',
           label='L0 depth threshold (0.15 m)', zorder=3)

ford = df[df['category'] == 'FORD_AGREE']
agree_no = df[df['category'] == 'NOFORD_AGREE']
diverge = df[df['category'] == 'DIVERGE']

ax.scatter(ford['depth_m'], ford['velocity_ms'], color='#4dac26', marker='o', s=140,
           zorder=7, label='L2 = FORD  (L1 agrees)', edgecolors='#2d7a16', linewidths=1.3)
ax.scatter(agree_no['depth_m'], agree_no['velocity_ms'], color='#c0392b', marker='X', s=140,
           zorder=7, label='L2 = NO-FORD  (L1 agrees)', edgecolors='#922b21', linewidths=1.3)
ax.scatter(diverge['depth_m'], diverge['velocity_ms'], color='#e07b00', marker='D', s=180,
           zorder=8, label='DIVERGE: L1=FORD, L2=NO-FORD', edgecolors='#333333', linewidths=1.2)

ax.text(0.60, 0.42,
        'L1 verdicts are read from scenario_sweep.csv.\n'
        'Column L1_verdict is the joint rule, not the bare D×V product.\n'
        f'{reclass} of {bare_ford} bare-rule FORD cells become NO-FORD; '
        f'{reverse} go the other way.',
        fontsize=8.5, color='#333333', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.50', facecolor='#fff8e6',
                  edgecolor='#e07b00', alpha=0.96), zorder=10)

ax.set_xlabel('Water Depth (m)', fontsize=12)
ax.set_ylabel('Flow Velocity (m/s)', fontsize=12)
ax.set_title('Can It Ford? -- L2 phase space vs L1 joint rule (AR&R small passenger)',
             fontsize=12, fontweight='bold')
ax.set_xlim(0.05, 0.75)
ax.set_ylim(-0.10, 2.95)
ax.legend(fontsize=8, bbox_to_anchor=(1.01, 1), loc='upper left',
          framealpha=0.93, edgecolor='#cccccc', borderaxespad=0)
ax.grid(True, alpha=0.20, color='gray')

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight')
print(f'Saved: {OUT_PNG}')
