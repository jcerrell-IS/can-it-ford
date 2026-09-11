import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GRID_CSV = os.path.join(ROOT, "data", "scenario_sweep.csv")
L2_CSV = os.path.join(ROOT, "data", "track1_sweep_v2", "manifest.csv")
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)
STEM = os.path.join(OUT, "phase_space_poster_figure")

DRIFT_THRESHOLD = 0.05

PT = 200.0 / 72.0
FONT_BASE = round(24 * PT)
FONT_AXIS = round(28 * PT)
FONT_TITLE = round(34 * PT)
FONT_LEGEND = round(24 * PT)
FONT_ANNOT = round(15 * PT)

FORD_FILL = "#8EC16A"
DISAGREE_FILL = "#F2C14E"
NOFORD_FILL = "#E06B6B"
FORD_MARK = "#2E7D32"
NOFORD_MARK = "#B3261E"
INK = "#111111"

grid = pd.read_csv(GRID_CSV)


def cat_code(row):
    l0 = str(row["L0_verdict"]).upper()
    l1 = str(row["L1_verdict"]).upper()
    if l0 != l1:
        return 1
    return 0 if l0 == "FORD" else 2


grid["code"] = grid.apply(cat_code, axis=1)
piv = grid.pivot_table(index="velocity_ms", columns="depth_m", values="code")
depths = piv.columns.to_numpy(dtype=float)
vels = piv.index.to_numpy(dtype=float)
Z = piv.to_numpy(dtype=float)

colorscale = [
    [0.0, FORD_FILL], [1 / 3, FORD_FILL],
    [1 / 3, DISAGREE_FILL], [2 / 3, DISAGREE_FILL],
    [2 / 3, NOFORD_FILL], [1.0, NOFORD_FILL],
]

fig = go.Figure()

fig.add_trace(go.Heatmap(
    x=depths, y=vels, z=Z,
    zmin=-0.5, zmax=2.5,
    colorscale=colorscale,
    opacity=0.85,
    xgap=1, ygap=1,
    colorbar=dict(
        title=dict(text="L0 vs L1", font=dict(size=FONT_BASE)),
        tickvals=[0, 1, 2],
        ticktext=["FORD", "DISAGREE", "NO-FORD"],
        tickfont=dict(size=FONT_BASE),
        thickness=34, len=0.62, y=0.5, yanchor="middle",
        outlinewidth=1, outlinecolor=INK,
    ),
    hovertemplate="d=%{x:.2f} m<br>v=%{y:.2f} m/s<extra></extra>",
    name="L0/L1 grid",
    showscale=True,
))

dd = np.linspace(depths.min(), depths.max(), 400)
ISO = [
    (0.30, "dot", 4, "Small passenger  D×V=0.30"),
    (0.45, "dashdot", 5, "Sedan (Large passenger)  D×V=0.45"),
    (0.60, "solid", 7, "Pickup (Large 4WD)  D×V=0.60"),
]
for k, dash, lw, label in ISO:
    vv = k / dd
    m = (vv >= vels.min()) & (vv <= vels.max())
    fig.add_trace(go.Scatter(
        x=dd[m], y=vv[m], mode="lines",
        line=dict(color=INK, width=lw, dash=dash),
        name=label, hoverinfo="skip", showlegend=True,
    ))

l2 = pd.read_csv(L2_CSV)
l2 = l2[l2["density_plausible"] == True].copy()
l2["verdict"] = np.where(l2["final_disp_m"] > DRIFT_THRESHOLD, "NO-FORD", "FORD")
dmax = float(l2["final_disp_m"].max())


def msize(d):
    return 26 + (float(d) / dmax) * 34


SYMS = {"sedan": "diamond", "pickup": "square"}
DODGE = {"sedan": -0.006, "pickup": 0.006}
for cls in ["sedan", "pickup"]:
    for verdict, fill, edge in [("NO-FORD", NOFORD_MARK, "#ffffff"), ("FORD", FORD_MARK, "#ffffff")]:
        sub = l2[(l2["vehicle_class"] == cls) & (l2["verdict"] == verdict)]
        if not len(sub):
            continue
        fig.add_trace(go.Scatter(
            x=sub["depth_m"] + DODGE[cls], y=sub["velocity_ms"], mode="markers",
            marker=dict(
                symbol=SYMS[cls],
                size=[msize(d) for d in sub["final_disp_m"]],
                color=fill, opacity=0.95,
                line=dict(color=INK, width=3),
            ),
            name="L2 %s · %s" % (cls.capitalize(), verdict),
            customdata=np.stack([sub["final_disp_m"], sub["final_yaw_deg"]], axis=-1),
            hovertemplate=(cls.capitalize() + "<br>d=%{x:.2f} m  v=%{y:.2f} m/s"
                           "<br>drift=%{customdata[0]:.3f} m  yaw=%{customdata[1]:.1f}°<extra></extra>"),
            showlegend=True,
        ))

fig.update_layout(
    template="plotly_white",
    title=dict(
        text="Can It Ford?  L0 / L1 / L2 Phase Space",
        font=dict(size=FONT_TITLE, color=INK), x=0.5, xanchor="center", y=0.975,
    ),
    font=dict(family="Arial", size=FONT_BASE, color=INK),
    paper_bgcolor="white", plot_bgcolor="white",
    xaxis=dict(
        title=dict(text="Water depth  d  (m)", font=dict(size=FONT_AXIS)),
        tickfont=dict(size=FONT_BASE), range=[depths.min() - 0.05, depths.max() + 0.05],
        showgrid=False, ticks="outside", linecolor=INK, linewidth=2, mirror=True,
    ),
    yaxis=dict(
        title=dict(text="Flow velocity  v  (m/s)", font=dict(size=FONT_AXIS)),
        tickfont=dict(size=FONT_BASE), range=[vels.min() - 0.15, vels.max() + 0.15],
        showgrid=False, ticks="outside", linecolor=INK, linewidth=2, mirror=True,
    ),
    legend=dict(
        font=dict(size=FONT_LEGEND), bgcolor="rgba(255,255,255,0.92)",
        bordercolor=INK, borderwidth=1.5,
        x=0.985, xanchor="right", y=0.985, yanchor="top",
    ),
    margin=dict(l=150, r=60, t=140, b=380),
)

fig.add_annotation(
    x=0.5, y=-0.26, xref="paper", yref="paper", showarrow=False,
    font=dict(size=FONT_ANNOT, color="#555555"), align="center",
    text=("Background: L0 (static depth) vs L1 (D×V) hazard verdicts.<br>"
          "Markers: L2 coupled-MPM runs, v2 sweep, density-plausible rows only (SUV excluded).<br>"
          "Marker area ∝ final drift; NO-FORD = drift > 0.05 m; sedan/pickup dodged ±0.006 m for legibility."),
)

fig.write_image(STEM + ".png", width=2400, height=1800, scale=1)
fig.write_image(STEM + ".svg", width=2400, height=1800, scale=1)

print("grid cells:", grid.shape[0], "| L2 points plotted:", len(l2),
      "| verdicts:", dict(l2["verdict"].value_counts()))
print("PNG:", STEM + ".png")
print("SVG:", STEM + ".svg")
