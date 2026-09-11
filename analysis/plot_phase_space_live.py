import plotly.graph_objects as go
import pandas as pd
import numpy as np

df = pd.read_csv("data/phase_space_results.csv")
df['l1_haz'] = df['depth_m'] * df['velocity_ms']
df['l1_verdict'] = df['l1_haz'].apply(lambda h: 'FORD' if h <= 0.60 else 'NO-FORD')
v = np.linspace(0.1, 3.5, 300)

fig = go.Figure()

fig.add_hline(y=0.15, line=dict(color="gray", dash="dot", width=2),
              annotation_text="L0: d = 0.15m", annotation_position="top right")

fig.add_trace(go.Scatter(x=v, y=0.60/v, mode="lines",
    name="L1: d·v = 0.60 m²/s (Large 4WD, AR&R)",
    line=dict(color="darkorange", dash="dash", width=2.5)))

fig.add_trace(go.Scatter(x=v, y=0.30/v, mode="lines",
    name="L1: d·v = 0.30 m²/s (Small sedan, AR&R)",
    line=dict(color="goldenrod", dash="dot", width=1.5)))

for _, row in df.iterrows():
    color  = "#cc0000" if row.verdict == "NO-FORD" else "#009900"
    symbol = "x"      if row.verdict == "NO-FORD" else "circle"
    fig.add_trace(go.Scatter(
        x=[row.velocity_ms], y=[row.depth_m], mode="markers",
        marker=dict(size=18, color=color, symbol=symbol,
                    line=dict(width=2, color="black")),
        name=f"L2: ({row.depth_m}m, {row.velocity_ms}m/s) → {row.verdict}",
        hovertemplate=f"d={row.depth_m}m, v={row.velocity_ms}m/s<br>"
                      f"L1: {row.l1_verdict} (haz={row.l1_haz})<br>"
                      f"L2: <b>{row.verdict}</b><extra></extra>"
    ))

fig.add_annotation(
    x=1.50, y=0.30,
    text="<b>DIVERGENCE ZONE</b><br>L1: FORD (haz=0.45)<br>L2: NO-FORD<br><i>persistent lateral drag</i>",
    showarrow=True, arrowhead=2, arrowcolor="#cc0000",
    bgcolor="rgba(255,220,220,0.95)", bordercolor="#cc0000", borderwidth=2,
    font=dict(size=12), ax=90, ay=-55
)

fig.update_layout(
    title=dict(
        text="Can It Ford? — L0/L1/L2 Abstraction Ladder Phase Space<br>"
             "<sub>At d=0.30m, v=1.5m/s: L1 scalar criterion misses "
             "persistent lateral drag captured by Genesis SPH Pilot (L2)</sub>",
        font=dict(size=15)
    ),
    xaxis=dict(title="Flow Velocity (m/s)", range=[0,3.5], dtick=0.5,
               gridcolor="rgba(0,0,0,0.08)"),
    yaxis=dict(title="Water Depth (m)", range=[0,0.65], dtick=0.1,
               gridcolor="rgba(0,0,0,0.08)"),
    template="plotly_white",
    legend=dict(x=0.02, y=0.98, bordercolor="black", borderwidth=1,
                bgcolor="rgba(255,255,255,0.92)"),
    width=960, height=640,
)

fig.write_html("figures/phase_space_interactive.html")
fig.write_image("figures/phase_space.pdf", width=1920, height=1280)
fig.write_image("figures/phase_space.png", width=1920, height=1280, scale=2)
print("Saved: figures/phase_space_interactive.html + .pdf + .png")
