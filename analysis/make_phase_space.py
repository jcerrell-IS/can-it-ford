import numpy as np
import pandas as pd
import plotly.graph_objects as go

depths = np.round(np.arange(0.1, 1.0+1e-9, 0.1), 2)
velocities = np.round(np.arange(0.0, 3.0+1e-9, 0.5), 2)
rows = []
for v in velocities:
    for d in depths:
        l0 = "NO-FORD" if d > 0.15 else "FORD"
        haz = round(d*v, 4)
        l1 = "NO-FORD" if haz > 0.60 else "FORD"
        rows.append({"depth":d,"velocity":v,"L0":l0,"L1":l1})
grid_df = pd.DataFrame(rows)

l2_df = pd.DataFrame({
    "depth":   [0.15, 0.30, 0.60, 0.15, 0.30, 0.45, 0.60, 0.30, 0.30],
    "velocity":[0.0,  0.0,  0.0,  1.5,  1.5,  1.5,  1.5,  1.0,  2.0],
    "verdict": ["FORD","FORD","FORD","NO-FORD","NO-FORD","NO-FORD","NO-FORD","NO-FORD","NO-FORD"]
})

CATEGORY_ORDER = ["FORD","NO-FORD","DISAGREE"]
CATEGORY_CODE = {n:i for i,n in enumerate(CATEGORY_ORDER)}
CATEGORY_COLOR = {"FORD":"#b7e6a5","NO-FORD":"#f4a9a8","DISAGREE":"#f5c542"}

def classify(row):
    if row["L0"] != row["L1"]:
        return "DISAGREE"
    return row["L0"]

grid_df["category"] = grid_df.apply(classify, axis=1)
grid_df["z"] = grid_df["category"].map(CATEGORY_CODE)

z_grid = grid_df.pivot(index="velocity", columns="depth", values="z").sort_index().sort_index(axis=1)
x_vals = z_grid.columns.tolist()
y_vals = z_grid.index.tolist()

n_cat = len(CATEGORY_ORDER)
discrete_colorscale = []
for i, cat in enumerate(CATEGORY_ORDER):
    lo = i/n_cat
    hi = (i+1)/n_cat
    discrete_colorscale.append([lo, CATEGORY_COLOR[cat]])
    discrete_colorscale.append([hi, CATEGORY_COLOR[cat]])

heatmap = go.Heatmap(x=x_vals, y=y_vals, z=z_grid.values, colorscale=discrete_colorscale, zmin=0, zmax=n_cat, xgap=1, ygap=1, showscale=False)
legend_traces = [go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=16, color=CATEGORY_COLOR[cat], symbol="square"), name=cat, showlegend=True) for cat in CATEGORY_ORDER]

d_range = np.linspace(0.05, max(x_vals), 400)
hyperbola_traces = []
for k, color, dash, label in [(0.30,"#1f77b4","dot","Sedan"), (0.45,"#9467bd","dash","Lg. passenger"), (0.60,"#d62728","solid","4WD")]:
    v_curve = k/d_range
    mask = v_curve <= max(y_vals)*1.05
    hyperbola_traces.append(go.Scatter(x=d_range[mask], y=v_curve[mask], mode="lines", line=dict(color=color, width=3, dash=dash), name=f"AR&R d\u00b7v={k} ({label})"))

l2_ford = l2_df[l2_df["verdict"]=="FORD"]
l2_noford = l2_df[l2_df["verdict"]=="NO-FORD"]
div_mask = (l2_df["verdict"]=="NO-FORD") & (l2_df["depth"].isin([0.15,0.30])) & (l2_df["velocity"].isin([1.0,1.5]))
div_points = l2_df[div_mask]

scatter_ford = go.Scatter(x=l2_ford["depth"], y=l2_ford["velocity"], mode="markers", marker=dict(symbol="circle", size=18, color="black", line=dict(width=2, color="white")), name="L2: FORD")
scatter_noford = go.Scatter(x=l2_noford["depth"], y=l2_noford["velocity"], mode="markers", marker=dict(symbol="x", size=18, color="black", line=dict(width=3)), name="L2: NO-FORD")
scatter_div = go.Scatter(x=div_points["depth"], y=div_points["velocity"], mode="markers", marker=dict(symbol="diamond", size=24, color="#BF5700", line=dict(width=2, color="white")), name="L1/L2 Divergence")

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
    title=dict(text="Can It Ford? \u2014 L0/L1/L2 Phase Space", font=dict(size=28, color="black")),
    xaxis=dict(title=dict(text="Water depth, d (m)", font=dict(size=24)), tickfont=dict(size=20), range=[0, max(x_vals)+0.05], showgrid=False),
    yaxis=dict(title=dict(text="Flow velocity, v (m/s)", font=dict(size=24)), tickfont=dict(size=20), range=[0, max(y_vals)+0.1], showgrid=False),
    legend=dict(font=dict(size=18), bgcolor="white", bordercolor="black", borderwidth=1),
    font=dict(size=20, color="black"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    width=2400,
    height=1800,
    margin=dict(l=100, r=40, t=100, b=90),
)

fig.write_image("phase_space_poster_figure.png", width=2400, height=1800, scale=1)
fig.write_image("phase_space_poster_figure.svg", format="svg", width=2400, height=1800, scale=1)
fig.write_html("phase_space_poster_figure.html")
print("Done.")
