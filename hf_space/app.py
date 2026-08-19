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
import speed_surface as SS

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
    """The settled five-seed surface. Cell labels carry n and the seed sd."""
    surf = SS.canonical_surface()
    xs = sorted({c["v_water_ms"] for c in surf})
    ys = sorted({c["v_car_ms"] for c in surf})
    idx = {(c["v_car_ms"], c["v_water_ms"]): c for c in surf}
    z, text = [], []
    for vc in ys:
        zrow, trow = [], []
        for vw in xs:
            c = idx.get((vc, vw))
            if c is None:
                zrow.append(None)
                trow.append("no data")
                continue
            zrow.append(c["F_horiz_mean_N"])
            trow.append(f"{c['F_horiz_mean_N']:.0f} N<br>"
                        f"&plusmn;{c['F_horiz_sd_N']:.1f} ({c['seed_rel_sd_pct']:.2f}%)<br>"
                        f"n={c['n_seeds']} seeds")
        z.append(zrow)
        text.append(trow)
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(v) for v in xs], y=[str(v) for v in ys],
        text=text, texttemplate="%{text}", colorscale="Viridis",
        hoverongaps=False, colorbar=dict(title="|F_horiz| (N)"),
    ))
    fig.update_layout(
        title="Settled load surface, five seeds per cell (window f250-400)",
        xaxis_title="v_water (m/s), broadside flow across the roadway",
        yaxis_title="v_car (m/s), vehicle speed along its own axis",
        height=520, margin=dict(l=10, r=10, t=60, b=40), template="plotly_white",
    )
    return fig


def _split_figure():
    """SPREAD 2, the result. At FIXED |v_rel| the load still varies by ~100 percent."""
    arcs = SS.iso_vrel_arcs()
    fig = go.Figure()
    for a in arcs:
        fig.add_trace(go.Bar(
            x=[f"|v_rel| = {a['v_rel_mag_ms']:g} m/s"],
            y=[a["F_max_N"] - a["F_min_N"]],
            base=[a["F_min_N"]],
            name=f"S = {a['S_spread']:.2f}",
            text=[f"min {a['F_min_N']:.0f} N<br>max {a['F_max_N']:.0f} N<br>"
                  f"S = {a['S_spread']:.2f}"],
            textposition="outside",
        ))
    fig.update_layout(
        title=("At a FIXED relative speed the load is not fixed. "
               "Each bar spans min to max over nine ways of splitting the same |v_rel|."),
        yaxis_title="|F_horiz| (N), min to max across the arc",
        height=520, margin=dict(l=10, r=10, t=80, b=40), template="plotly_white",
        showlegend=True,
    )
    return fig


def _window_figure():
    """SPREAD 3, and the reason a window has to be stated with every number."""
    wc = SS.window_comparison()
    labels = [f"({w['v_car_ms']:g}, {w['v_water_ms']:g})" for w in wc]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[w["transient_f20_60_N"] for w in wc],
                         name="transient f20-60 (published)"))
    fig.add_trace(go.Bar(x=labels, y=[w["settled_f250_400_N"] for w in wc],
                         name="settled f250-400 (five seeds)"))
    fig.update_layout(
        title="Same twenty cells, two measurement windows",
        xaxis_title="(v_car, v_water) m/s",
        yaxis_title="|F_horiz| (N)",
        barmode="group", height=520,
        margin=dict(l=10, r=10, t=60, b=90), template="plotly_white",
    )
    return fig


def surface_notes():
    ts = SS.three_spreads()
    hp = SS.headline_pair()
    rc = SS.resolution_check()
    seed = ts["seed_spread_pct"]
    split = ts["split_spread_S"]
    win = ts["window_spread_pct"]
    return f"""
### Three spreads live in this data, and they are not the same size

| spread | what varies | size | is it an error bar? |
|---|---|---|---|
| **seed** | five seeds, one cell | {seed['min']:.3f} to {seed['max']:.3f} % (median {seed['median']:.3f}) | yes, and it is tiny |
| **split** | how one \\|v_rel\\| divides into v_car and v_water | S = {split['min']:.2f} to {split['max']:.2f}, i.e. {100*split['min']:.0f} to {100*split['max']:.0f} % | **no, this is the result** |
| **window** | f20-60 against f250-400 | {win['min']:.1f} to +{win['max']:.1f} % | no, it means the load is still changing |

The split and window spreads exceed the seed spread by **two to three orders of
magnitude**. A plot with error bars drawn from seed scatter would show almost
nothing and would imply the other two do not exist.

### What a scalar relative speed leaves out

At \\|v_rel\\| = 6.0 m/s the load ranges from
{[a for a in SS.iso_vrel_arcs() if a['v_rel_mag_ms']==6.0][0]['F_min_N']:.0f} N to
{[a for a in SS.iso_vrel_arcs() if a['v_rel_mag_ms']==6.0][0]['F_max_N']:.0f} N
depending only on how that speed is split between the vehicle and the water.
S grows with speed: {', '.join(f"{a['v_rel_mag_ms']:g} m/s -> {a['S_spread']:.2f}" for a in SS.iso_vrel_arcs())}.

### The window matters enough to invert a published comparison

The pair reported in the source write-up, at the **transient** window:
(v_car {hp['cell_lower_vrel']['v_car_ms']}, v_water {hp['cell_lower_vrel']['v_water_ms']})
carries {hp['transient']['lower_N']:.0f} N at \\|v_rel\\| {hp['cell_lower_vrel']['v_rel_mag_ms']:.3f} m/s,
against {hp['transient']['higher_N']:.0f} N at the higher \\|v_rel\\| {hp['cell_higher_vrel']['v_rel_mag_ms']:.3f} m/s,
a ratio of **{hp['transient']['ratio_lower_over_higher']:.3f}**.

The same two cells in the **settled** window, five seeds each:
{hp['settled']['lower_N']:.0f} &plusmn; {hp['settled']['lower_sd_N']:.1f} N against
{hp['settled']['higher_N']:.0f} &plusmn; {hp['settled']['higher_sd_N']:.1f} N,
a ratio of **{hp['settled']['ratio_lower_over_higher']:.3f}**.

The ratio crosses 1, so the direction of that particular comparison reverses.
The seed uncertainty is under 0.35 percent, so the reversal is not seed noise.
**The general claim, that the split matters, survives in both windows and is
strengthened; the specific pair does not.** Both statements are on this page
because reporting only one of them would be choosing the flattering half.

### Resolution

A single-seed n_grid=96 surface differs from this five-seed n_grid=64 surface by
{rc['g96_minus_g64_pct']['min']:.1f} to +{rc['g96_minus_g64_pct']['max']:.1f} percent across
{rc['cells_compared']} cells, median {rc['g96_minus_g64_pct']['median']:.1f}. That is the size of
the resolution effect. It is **not** a convergence claim, and no grid-converged
statement should be read off this page.
"""


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
                "single relative speed. This matrix keeps them as separate axes, and "
                "every cell is a mean over five seeds rather than a single point."
            )
            gr.Plot(_surface_figure)
            gr.Markdown(
                "### The spread at fixed relative speed\n"
                "If a scalar relative speed determined the load, every bar below would "
                "have zero height."
            )
            gr.Plot(_split_figure)
            gr.Markdown(
                "### The same cells, two measurement windows\n"
                "The left bar of each pair is the window the source write-up published."
            )
            gr.Plot(_window_figure)
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
