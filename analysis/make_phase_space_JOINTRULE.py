import csv
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_CSV = os.path.join(REPO, 'data', 'scenario_sweep.csv')

EXPECT_ROWS = 70
EXPECT_JOINT_FORD = 14
EXPECT_BARE_FORD = 37
EXPECT_RECLASS = 23

with open(SWEEP_CSV, newline='', encoding='utf-8-sig') as fh:
    sweep_rows = list(csv.DictReader(fh))

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

grid_df = pd.DataFrame([{
    'depth': round(float(r['depth_m']), 4),
    'velocity': round(float(r['velocity_ms']), 4),
    'L0': r['L0_verdict'],
    'L1': r['L1_verdict'],
    'L1_bare': r['L1_haz_product_only'],
} for r in sweep_rows])

print(f'  grid {grid_df["depth"].nunique()} depths x {grid_df["velocity"].nunique()} '
      f'velocities = {len(grid_df)} cells, all read from the CSV, none recomputed')

l2_df = pd.DataFrame({
    'depth':    [0.15, 0.30, 0.60, 0.15, 0.30, 0.45, 0.60, 0.30, 0.30],
    'velocity': [0.0,  0.0,  0.0,  1.5,  1.5,  1.5,  1.5,  1.0,  2.0],
    'verdict':  ['FORD', 'FORD', 'FORD', 'NO-FORD', 'NO-FORD',
                 'NO-FORD', 'NO-FORD', 'NO-FORD', 'NO-FORD'],
})

CATEGORY_ORDER = ['FORD', 'NO-FORD', 'DISAGREE']
CATEGORY_CODE = {n: i for i, n in enumerate(CATEGORY_ORDER)}
CATEGORY_COLOR = {'FORD': '#b7e6a5', 'NO-FORD': '#f4a9a8', 'DISAGREE': '#f5c542'}


def classify(row):
    if row['L0'] != row['L1']:
        return 'DISAGREE'
    return row['L0']


grid_df['category'] = grid_df.apply(classify, axis=1)
grid_df['z'] = grid_df['category'].map(CATEGORY_CODE)

z_grid = grid_df.pivot(index='velocity', columns='depth', values='z').sort_index().sort_index(axis=1)
x_vals = z_grid.columns.tolist()
y_vals = z_grid.index.tolist()

n_cat = len(CATEGORY_ORDER)
discrete_colorscale = []
for i, cat in enumerate(CATEGORY_ORDER):
    discrete_colorscale.append([i / n_cat, CATEGORY_COLOR[cat]])
    discrete_colorscale.append([(i + 1) / n_cat, CATEGORY_COLOR[cat]])

heatmap = go.Heatmap(x=x_vals, y=y_vals, z=z_grid.values, colorscale=discrete_colorscale,
                     zmin=0, zmax=n_cat, xgap=1, ygap=1, showscale=False)
legend_traces = [go.Scatter(x=[None], y=[None], mode='markers',
                            marker=dict(size=16, color=CATEGORY_COLOR[cat], symbol='square'),
                            name=cat, showlegend=True) for cat in CATEGORY_ORDER]

d_range = np.linspace(0.05, max(x_vals), 400)
hyperbola_traces = []
for k, color, dash, label in [(0.30, '#1f77b4', 'dot', 'Sedan'),
                              (0.45, '#9467bd', 'dash', 'Lg. passenger'),
                              (0.60, '#d62728', 'solid', '4WD')]:
    v_curve = k / d_range
    mask = v_curve <= max(y_vals) * 1.05
    hyperbola_traces.append(go.Scatter(x=d_range[mask], y=v_curve[mask], mode='lines',
                                       line=dict(color=color, width=3, dash=dash),
                                       name=f'AR&R d·v={k} ({label})'))

l2_ford = l2_df[l2_df['verdict'] == 'FORD']
l2_noford = l2_df[l2_df['verdict'] == 'NO-FORD']

joint_lookup = {(r['depth'], r['velocity']): r['L1'] for _, r in grid_df.iterrows()}
div_rows = []
for _, r in l2_df.iterrows():
    l1 = joint_lookup.get((round(r['depth'], 4), round(r['velocity'], 4)))
    if l1 is not None and l1 == 'FORD' and r['verdict'] == 'NO-FORD':
        div_rows.append(r)
div_points = pd.DataFrame(div_rows) if div_rows else l2_df.iloc[0:0]
print(f'  L1/L2 divergences under the joint rule: {len(div_points)}')

scatter_ford = go.Scatter(x=l2_ford['depth'], y=l2_ford['velocity'], mode='markers',
                          marker=dict(symbol='circle', size=18, color='black',
                                      line=dict(width=2, color='white')), name='L2: FORD')
scatter_noford = go.Scatter(x=l2_noford['depth'], y=l2_noford['velocity'], mode='markers',
                            marker=dict(symbol='x', size=18, color='black',
                                        line=dict(width=3)), name='L2: NO-FORD')
scatter_div = go.Scatter(x=div_points['depth'], y=div_points['velocity'], mode='markers',
                         marker=dict(symbol='diamond', size=24, color='#BF5700',
                                     line=dict(width=2, color='white')),
                         name='L1/L2 Divergence')

fig = go.Figure()
fig.add_trace(heatmap)
for t in legend_traces:
    fig.add_trace(t)
for t in hyperbola_traces:
    fig.add_trace(t)
fig.add_trace(scatter_ford)
fig.add_trace(scatter_noford)
fig.add_trace(scatter_div)

fig.update_layout(
    title=dict(text='Can It Ford? — L0/L1/L2 Phase Space (L1 joint rule, read from scenario_sweep.csv)',
               font=dict(size=26, color='black')),
    xaxis=dict(title=dict(text='Water depth, d (m)', font=dict(size=24)),
               tickfont=dict(size=20), range=[0, max(x_vals) + 0.05], showgrid=False),
    yaxis=dict(title=dict(text='Flow velocity, v (m/s)', font=dict(size=24)),
               tickfont=dict(size=20), range=[0, max(y_vals) + 0.1], showgrid=False),
    legend=dict(font=dict(size=18), bgcolor='white', bordercolor='black', borderwidth=1),
    font=dict(size=20, color='black'),
    plot_bgcolor='white',
    paper_bgcolor='white',
    width=2400,
    height=1800,
    margin=dict(l=100, r=40, t=120, b=90),
)

fig.write_image(os.path.join(REPO, 'phase_space_poster_figure_JOINTRULE.png'),
                width=2400, height=1800, scale=1)
fig.write_image(os.path.join(REPO, 'phase_space_poster_figure_JOINTRULE.svg'),
                format='svg', width=2400, height=1800, scale=1)
fig.write_html(os.path.join(REPO, 'phase_space_poster_figure_JOINTRULE.html'))
print('Saved: phase_space_poster_figure_JOINTRULE.png / .svg / .html')
