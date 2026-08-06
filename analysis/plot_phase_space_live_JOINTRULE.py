import csv
import os
import plotly.graph_objects as go
import pandas as pd
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_CSV = os.path.join(REPO, 'data', 'scenario_sweep.csv')
L2_CSV = os.path.join(REPO, 'data', 'phase_space_results.csv')
OUT_DIR = os.path.join(REPO, 'figures')

JOINT_DEPTH_CAP = 0.30
JOINT_VEL_CAP = 3.0
JOINT_PRODUCT_CAP = 0.30
BARE_PRODUCT_CAP = 0.60

EXPECT_ROWS = 70
EXPECT_JOINT_FORD = 14
EXPECT_BARE_FORD = 37
EXPECT_RECLASS = 23


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

print('L1 JOINT RULE AUDIT, source data/scenario_sweep.csv')
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
df['l1_verdict'] = verdicts
df['l1_source'] = sources
df['l1_haz'] = (df['depth_m'] * df['velocity_ms']).round(6)

print(f'  L2 rows {len(df)}, L1 from sweep {sources.count("sweep")}, '
      f'L1 derived {sources.count("derived")}')

v = np.linspace(0.1, 3.5, 300)
fig = go.Figure()

fig.add_hline(y=0.15, line=dict(color='gray', dash='dot', width=2),
              annotation_text='L0: d = 0.15m', annotation_position='top right')
fig.add_hline(y=JOINT_DEPTH_CAP, line=dict(color='green', dash='dot', width=2),
              annotation_text='L1 joint rule depth cap: d = 0.30m',
              annotation_position='bottom right')

joint_depth = np.minimum(JOINT_PRODUCT_CAP / v, JOINT_DEPTH_CAP)
joint_depth = np.where(v <= JOINT_VEL_CAP, joint_depth, np.nan)
fig.add_trace(go.Scatter(x=v, y=joint_depth, mode='lines',
    name='L1 joint rule: d ≤ 0.30 m AND D×V ≤ 0.30 m²/s AND v ≤ 3.0 m/s',
    line=dict(color='green', width=3)))

fig.add_trace(go.Scatter(x=v, y=BARE_PRODUCT_CAP / v, mode='lines',
    name='bare hazard rule for contrast: D×V ≤ 0.60 m²/s only',
    line=dict(color='darkorange', dash='dashdot', width=2)))

fig.add_trace(go.Scatter(x=v, y=JOINT_PRODUCT_CAP / v, mode='lines',
    name='AR&R small passenger product cap: D×V = 0.30 m²/s',
    line=dict(color='goldenrod', dash='dot', width=1.5)))

for _, row in df.iterrows():
    color = '#cc0000' if row.verdict == 'NO-FORD' else '#009900'
    symbol = 'x' if row.verdict == 'NO-FORD' else 'circle'
    if row.l1_source == 'derived':
        symbol = symbol + '-open' if symbol == 'circle' else symbol
    fig.add_trace(go.Scatter(
        x=[row.velocity_ms], y=[row.depth_m], mode='markers',
        marker=dict(size=18, color=color, symbol=symbol,
                    line=dict(width=2, color='black')),
        name=f'L2: ({row.depth_m}m, {row.velocity_ms}m/s) → {row.verdict}',
        hovertemplate=f'd={row.depth_m}m, v={row.velocity_ms}m/s<br>'
                      f'L1 joint rule: {row.l1_verdict} '
                      f'(D×V={row.l1_haz}, source {row.l1_source})<br>'
                      f'L2: <b>{row.verdict}</b><extra></extra>'
    ))

fig.update_layout(
    title=dict(
        text='Can It Ford? — L0/L1/L2 phase space, L1 read from data/scenario_sweep.csv<br>'
             f'<sub>L1_verdict is the joint rule. {reclass} of {bare_ford} bare-rule FORD '
             f'cells become NO-FORD; {reverse} go the other way.</sub>',
        font=dict(size=15)
    ),
    xaxis=dict(title='Flow Velocity (m/s)', range=[0, 3.5], dtick=0.5,
               gridcolor='rgba(0,0,0,0.08)'),
    yaxis=dict(title='Water Depth (m)', range=[0, 0.65], dtick=0.1,
               gridcolor='rgba(0,0,0,0.08)'),
    template='plotly_white',
    legend=dict(x=0.02, y=0.98, bordercolor='black', borderwidth=1,
                bgcolor='rgba(255,255,255,0.92)'),
    width=960, height=640,
)

os.makedirs(OUT_DIR, exist_ok=True)
fig.write_html(os.path.join(OUT_DIR, 'phase_space_interactive_JOINTRULE.html'))
fig.write_image(os.path.join(OUT_DIR, 'phase_space_JOINTRULE.pdf'), width=1920, height=1280)
fig.write_image(os.path.join(OUT_DIR, 'phase_space_JOINTRULE.png'), width=1920, height=1280, scale=2)
print('Saved: figures/phase_space_interactive_JOINTRULE.html + _JOINTRULE.pdf + _JOINTRULE.png')
