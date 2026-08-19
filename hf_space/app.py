"""Can It Ford: an interactive view of vehicle stability in floodwater.

The point of this Space is NOT to render one surface. It is to let a viewer see two
things the published literature does not show:

  1. the SPREAD, so a result reads as an ensemble rather than a point;
  2. where a verdict FLIPS as a threshold is moved, so the reader can see that the
     threshold is a choice rather than a measurement.

All logic lives in surface.py so it can be tested without a browser.
"""

from __future__ import annotations

import gradio as gr
import plotly.graph_objects as go

import surface as S

RUNS = S.load_table("canonical_runs.csv")


# ---------------------------------------------------------------------------
# Panel 1, verdict flips
# ---------------------------------------------------------------------------

def _verdict_figure(rows, slide_m):
    rows = sorted(rows, key=lambda r: r["max_surge_drift_m"])
    ids = [r["run_id"] for r in rows]
    drift = [r["max_surge_drift_m"] for r in rows]
    colors = ["#c0392b" if r["disagrees_with_published"] else
              ("#2c7fb8" if r["published_mode"] == "SLIDE" else "#7f8c8d") for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=drift, y=ids, orientation="h", marker_color=colors,
        hovertemplate="%{y}<br>peak surge drift %{x:.4f} m<extra></extra>",
    ))
    fig.add_vline(x=slide_m, line_width=2, line_dash="dash", line_color="#e67e22",
                  annotation_text=f"slide_m = {slide_m:.4f} m",
                  annotation_position="top")
    fig.update_layout(
        title="Peak surge drift per run, against the distance threshold",
        xaxis_title="peak surge drift (m)", yaxis_title="",
        height=560, margin=dict(l=10, r=10, t=60, b=40),
        template="plotly_white", showlegend=False,
    )
    return fig


def on_threshold(slide_m):
    rows = S.reclassify(RUNS, slide_m)
    return _verdict_figure(rows, slide_m), S.flip_summary(rows, slide_m)


# ---------------------------------------------------------------------------
# Panel 2, the load surface
# ---------------------------------------------------------------------------

def _surface_figure():
    lat = S.surface_lattice()
    st = S.surface_status()
    xs = S.PREREG_V_WATER
    ys = S.PREREG_V_CAR
    z, text = [], []
    for vc in ys:
        zrow, trow = [], []
        for vw in xs:
            cell = next(c for c in lat
                        if c["v_car_ms"] == vc and c["v_water_ms"] == vw)
            zrow.append(cell["F_horiz_mean_N"])
            if cell["n_repeats"]:
                trow.append(f"{cell['F_horiz_mean_N']:.1f} N<br>"
                            f"spread {cell['spread_pct']:.1f}%<br>"
                            f"n={cell['n_repeats']}")
            else:
                trow.append("planned,<br>no data")
        z.append(zrow)
        text.append(trow)

    fig = go.Figure(go.Heatmap(
        z=z, x=[str(v) for v in xs], y=[str(v) for v in ys],
        text=text, texttemplate="%{text}", colorscale="Viridis",
        hoverongaps=False, colorbar=dict(title="|F_horiz| (N)"),
    ))
    title = ("Load surface: PRE-REGISTERED MATRIX, NO DATA YET"
             if not st["populated"] else
             f"Load surface, {st['n_rows']} records across {st['n_cells']} cells")
    fig.update_layout(
        title=title,
        xaxis_title="v_water (m/s), broadside flow",
        yaxis_title="v_car (m/s), vehicle speed along its own axis",
        height=520, margin=dict(l=10, r=10, t=60, b=40), template="plotly_white",
    )
    return fig


def surface_notes():
    st = S.surface_status()
    _, msg = S.iso_vrel_spread()
    if not st["populated"]:
        return (
            "### No load-surface data yet\n\n"
            "The grid above is the **pre-registered matrix**, committed before the first "
            "GPU run so the result cannot be graded against a target chosen after seeing "
            "it. Every cell reads *planned, no data*.\n\n"
            "**Nothing is drawn from zero data on purpose.** A smooth interpolated "
            "surface over an empty table would look exactly like a result, and that is "
            "the most damaging thing this page could show.\n\n"
            f"**Pre-registered criterion C2.** {msg}\n\n"
            "**When it is populated, note what it is not.** The vehicle in those runs is "
            "*prescribed*, held on a path, not free. It cannot be swept away, because "
            "being swept away is the degree of freedom that scene removes. **No FORD or "
            "NO-FORD verdict is derivable from the load surface.** Torque is reported "
            "about the collider centre, not the centre of gravity."
        )
    return (
        f"### Load surface, {st['n_rows']} records\n\n"
        f"**Pre-registered criterion C2.** {msg}\n\n"
        "The vehicle is *prescribed*, not free, so no FORD verdict follows from this "
        "panel. Torque is about the collider centre, not the centre of gravity."
    )


# ---------------------------------------------------------------------------
# Panel 3, repeat spread
# ---------------------------------------------------------------------------

def _repeat_figure():
    rs = S.repeat_spread_table()
    fig = go.Figure()
    for r in rs:
        lo = min(r["draw_1_final_disp_m"], r["draw_2_final_disp_m"])
        hi = max(r["draw_1_final_disp_m"], r["draw_2_final_disp_m"])
        fig.add_trace(go.Scatter(
            x=[lo, hi], y=[r["config"], r["config"]], mode="lines+markers",
            line=dict(width=8), marker=dict(size=12),
            name=r["config"],
            hovertemplate=f"{r['config']}<br>range {r['abs_range_m']:.6f} m "
                          f"({r['rel_range_pct']:.2f}%)<extra></extra>",
        ))
    fig.update_layout(
        title="Two independent draws of the same configuration (n=2, a range not a distribution)",
        xaxis_title="final displacement magnitude (m)", yaxis_title="",
        height=320, margin=dict(l=10, r=10, t=60, b=40),
        template="plotly_white", showlegend=False,
    )
    return fig


REPEAT_NOTE = """
### What the repeats show

Three configurations were run twice, independently. The range between the two draws:

| config | range (m) | range (%) |
|---|---|---|
| `g96_m1100` | 0.001456 | 0.54 |
| `g96_m1609` | 0.000099 | 0.06 |
| `g96_m2337` | 0.003944 | **4.51** |

**The widest spread lands on `g96_m2337`, which is also the run with the tightest verdict
margin**, satisfying its published condition for exactly one frame more than required.
The run closest to flipping is the run whose repeat draw moves the most. That is the
argument for reporting ensembles rather than points, made from this project's own data.

**n = 2 is a range, not a distribution.** No standard deviation is quoted from two draws,
and none should be. A real distribution needs more draws, which is a compute request, not
a plotting choice.
"""


DISCLAIMER = """
## Read this before the numbers

- **Engine: warpmpm**, a material point method solver. These runs are **not Genesis**.
  Genesis was an earlier box-proxy path that never loaded the vehicle hull.
- **The simulated scenario is a stationary vehicle in flow.** That matches the validated
  stability criterion. The word "ford" implies motion; it is the title that mismatches.
- **Resolution is not converged.** The water column is resolved by about 2 grid cells and
  4 particle layers, against a rule of thumb of roughly 10 particles per flow depth.
  Displacement magnitude is non-monotone under refinement, so cite the verdict and not
  the magnitude.
- **No gate in this pipeline is a physics validation.** They are self-consistency and
  numerical containment checks; several compare against a reference derived from the same
  pipeline and so cannot fail for a reason external to the code.
- **`sustain_frames = 3` has no published source.** No vehicle-stability criterion
  reviewed for this project uses a persistence count at all. It gates every verdict here.
- The canonical vehicle mass is **1100 kg** and the canonical hull effective density is
  **310.494 kg/m^3**. Older material quoting 1390 kg or 115.7 kg/m^3 refers to a
  superseded box proxy, not the hull used here.
"""


def build() -> gr.Blocks:
    with gr.Blocks(title="Can It Ford") as demo:
        gr.Markdown(
            "# Can It Ford?\n"
            "**Vehicle stability in floodwater: the spread, and where the verdict flips.**\n\n"
            "The literature publishes thresholds and single points. This page shows the "
            "ensemble behind a point, and lets you move the threshold that decides a "
            "verdict so you can see which results depend on it."
        )

        with gr.Tab("Where the verdict flips"):
            gr.Markdown(
                "Drag the distance threshold. Bars turning **red** disagree with the "
                "published label on the distance test."
            )
            slider = gr.Slider(
                0.005, 0.30, value=S.DEFAULT_SLIDE_M, step=0.005,
                label="slide_m, the distance threshold (metres)",
                info="Published default 0.05 m. This is a CHOICE, not a measurement.",
            )
            plot = gr.Plot()
            notes = gr.Markdown()
            slider.change(on_threshold, slider, [plot, notes])
            demo.load(on_threshold, slider, [plot, notes])
            gr.Markdown(
                "> **Unit trap.** `slide_m` (0.05 m), `slide_speed_ms` (0.05 m/s) and "
                "`float_m` (0.05 m) share one numeral across two units. They must be "
                "deduplicated by name and unit, never by value."
            )

        with gr.Tab("Load surface (v_car x v_water)"):
            gr.Markdown(
                "Most published work collapses vehicle speed and flow speed into a "
                "single relative speed. This matrix keeps them as separate axes."
            )
            gr.Plot(_surface_figure)
            gr.Markdown(surface_notes)

        with gr.Tab("Repeat spread"):
            gr.Plot(_repeat_figure)
            gr.Markdown(REPEAT_NOTE)

        with gr.Tab("Limitations"):
            gr.Markdown(DISCLAIMER)

        gr.Markdown(
            "---\nJosie Cerrell, NSF REU, GeoElements Lab, UT Austin. PI Krishna Kumar.\n\n"
            "*No rendered imagery appears on this page: asset provenance for this "
            "project's render inputs is an open licence question, so only derived "
            "numbers are shown.*"
        )
    return demo


if __name__ == "__main__":
    build().launch(theme=gr.themes.Soft())
