"""Can It Ford: an interactive view of vehicle stability in floodwater.

The point of this Space is NOT to render one surface. It is to let a viewer see two
things the published literature does not show:

  1. the SPREAD, so a result reads as an ensemble rather than a point;
  2. where a verdict FLIPS as a threshold is moved, so the reader can see that the
     threshold is a choice rather than a measurement.

All logic lives in surface.py so it can be tested without a browser.
"""

from __future__ import annotations

from pathlib import Path

import gradio as gr
import plotly.graph_objects as go

import surface as S
import speed_surface as SS
import arr_verdict as AV

RUNS = S.load_table("canonical_runs.csv")

ASSETS = Path(__file__).resolve().parent / "assets"
HULL_GLB = ASSETS / "yaris_coarse_v1l_watertight.glb"
HULL_PLY = ASSETS / "yaris_coarse_v1l_watertight.ply"
SPLAT_PLY = ASSETS / "drainA_point_cloud_29999_merged_3ranks_preview.ply"


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


SCOPE_STATEMENT = """
## What this project evaluates, stated exactly

> This work evaluates whether a specific vehicle would remain stable if subjected to floodwater of a given depth and velocity, which is the condition a vehicle enters the moment a crossing attempt fails. The published stability criteria used for validation (Shand et al. 2011; Smith, Modra and Felder 2019) were derived exclusively from stationary vehicles restrained in flow, and no depth-velocity curve in that literature was derived for a vehicle driving under its own power. The verdict reported here is therefore a necessary condition for safe crossing rather than a sufficient one.
"""


SAFETY_NOTICE = """
> **This is not a safety tool.** The stability criteria used here are the source
> report's own draft interim figures for stationary vehicles, not an endorsed safety
> standard. Nothing on this site should be used to decide whether to drive into
> floodwater. Turn around, don't drown.
"""


VEHICLE_CLASS_NOTE = """
### The 1609 kg and 2337 kg masses are AR&R class figures, not vehicle measurements

Stated once, permanently, because it has been re-derived in many sessions.

`sim_standing.py:53` sources **1609 kg** to the AR&R `large_passenger` class figure
and `:62` sources **2337 kg** to the `large_4wd` figure, both by way of
`gates_both_scenarios.py`. The corrections register entry E6a associates those two
classes with a **2020 Nissan Rogue** and a **2018 Dodge Ram 1500** in the CCSA and
George Mason finite-element catalogue. Register entry E6b, read from live code on
2026-08-21, records that this is a class pairing and not a measured vehicle mass,
and that it should not be leaned on as provenance.

The deck-derived masses that do exist are **1571.3 kg** for the Rogue, which is
web-sourced because the Rogue LS-DYNA deck header carries no mass at all, and
**2270.0 kg** for the Silverado from its own deck header. Neither is a number this
sweep uses.

Two consequences, stated here so they stop needing to be re-flagged:

1. The multi-geometry **Silverado is a Chevrolet**, a different manufacturer's
   vehicle from the **Dodge Ram 1500** that the 2337 kg figure is associated with.
2. The Ram's test-vehicle designation is **2270P** and the Silverado's deck mass is
   **2270.0 kg**. The digits coincide. The vehicles do not.

All 17 gated runs share **one hull** regardless of the mass label: `hull_m3` is
single-valued at 3.542739 m3 across all 17 rows. The class names denote only which
AR&R limit set was applied.

**Rogue:** companion geometry, not validated. Runs exist through 2026-08-14 and a
2026-08-26 roll result was withdrawn. Unlike the Yaris and the Silverado, the Rogue
has no NCAC or CCSA finite-element provenance.
"""


HULL_NOTE = """
### The geometry all 17 gated runs actually loaded

**Validation status: canonical Yaris.** This is the vehicle the published verdicts
describe. Every one of the 17 gated warpmpm runs loaded this mesh and no other:
`hull_m3` is single-valued at 3.542739 m3 across all 17 rows, so mass varies across
the sweep while the geometry does not.

| property | value |
|---|---|
| vertices | 327,212 |
| faces | 655,308 |
| hull volume | 3.542739 m3 |
| effective density at 1100 kg | 310.494 kg/m^3 |
| sha256 | `b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95` |

Vehicle mesh: Center for Collision Safety and Analysis, George Mason University,
2010 Toyota Yaris coarse finite-element model, DOI
[10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D). The registered creator is CCSA
and the registration year is 2016; 2010 is the vehicle model year.

**What you are looking at is a derived surface reconstruction, not the FE deck.**
The DOI above resolves to the deck's validation report. The mesh pipeline that
produced the PLY is not bit-reproducible, so the sha256 is the provenance anchor
for that exact file rather than for the process that made it.

**The viewer is fed a GLB, and the PLY is the artifact of record.** Gradio renders
`.ply` through its Gaussian-splat path, which cannot parse a triangle mesh, so the
hull is served as a lossless format conversion. The conversion was checked rather
than assumed: vertex count, face count, watertightness and volume all round-trip
unchanged, and the volume reproduces the canonical `hull_m3` of 3.542739 m3 to every
printed digit. Both files ship with this Space.

| file | role | sha256 |
|---|---|---|
| `yaris_coarse_v1l_watertight.ply` | artifact of record | `b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95` |
| `yaris_coarse_v1l_watertight.glb` | what the viewer renders | `d17179acc870bd30ead9864fee16d00f93b628ae436d3ad918cfa1c28feaced0` |
"""


SPLAT_NOTE = """
### Reconstruction, the input end of the pipeline

**Validation status: reconstruction input, not a validated hull.** This is a
Gaussian splat of a real drainage crossing, the scene geometry the pipeline
reconstructs before any physics runs. No verdict on this page is derived from it.

Reconstruction: drainA scene, trained with `gsplat` to 30,000 iterations, merged
from three rank shards (399,491 + 374,677 + 373,526) to **1,147,694 Gaussians**.
Validation at step 29,999: PSNR 22.74, SSIM 0.825, LPIPS 0.311.

**What the viewer loads is a decimated preview, not the full reconstruction.** The
merged artifact is 258.3 MB, which no browser should be asked to fetch and parse.
The preview keeps **350,000 Gaussians**, selected by opacity times footprint after
discarding the 233,999 whose opacity falls below 0.1, and carries spherical-harmonic
degree 0 only. Its bounding box is identical to the full artifact's on all six
bounds, so this is a thinned scene and not a cropped one. It is built by
`analysis/build_splat_preview.py`, and the full 1,147,694-Gaussian file remains the
artifact of record.

Two properties of this asset that are easy to get wrong and are stated here rather
than assumed:

- The point cloud is **gsplat-normalized, not in COLMAP frame.** The COLMAP to PLY
  scale is 0.30827678832280847.
- **Metric scale is not yet established.** The curb inlet top slab front edge
  measures 0.8037 model units and awaits a physical tape measurement. Do not read
  real-world distances off this viewer.
"""


SPLAT_MISSING = """
### Reconstruction, the input end of the pipeline

The decimated preview of the merged 30,000-iteration drainA Gaussian splat is
**not bundled with this Space**, so nothing is rendered here.

Stated rather than hidden, because a viewer should be able to tell the difference
between an asset that is absent and one that failed to load. The 3,000-iteration
checkpoint is a different and much earlier artifact and is deliberately **not**
substituted here.
"""


PRECEDENT = """
## Precedent and novelty

### Attribution, before any claim

The **query-conditioned world model** and **physically viable world model** framing
that situates this project is **not mine.** That conceptual framework belongs to
Thorpe et al., *Physically Viable World Models: A Case for Query-Conditioned
Embodied AI*, [arXiv:2605.30542](https://arxiv.org/abs/2605.30542), co-authored by
**Hassan Iqbal** and **Cheng-Hsi Hsiao** at GeoElements. My contribution is the
applied pipeline and the abstraction-ladder validation experiment, and not the
framework itself.

### The closest prior full pipeline

Low, Hsiao, Li, Thorpe, Topcu and Kumar, *Path Planning in Physically Viable World
Models*, [arXiv:2607.00673](https://arxiv.org/abs/2607.00673), is the closest prior
work to this one. It closes **reconstruction**, **simulation** and **decision** in a
single pipeline.

What it does not carry is an **external empirical validation** step, and that is
precisely where this project's differentiator sits: the verdicts here are checked
against published experimental stability criteria produced outside this pipeline,
by other groups, on physical vehicles in flumes.

That is a narrow claim and it is meant to be. The pipeline is not the novel part.

### Method precedent this work builds on

Every DOI below was resolved and title-checked against two independent registries
before being published here. None carries a retraction, correction, or expression of
concern.

| work | DOI | why it is here |
|---|---|---|
| Gao, Pradhana, Han et al. 2018, *Animating fluid sediment mixture in particle-laden flows* | [10.1145/3197517.3201309](https://doi.org/10.1145/3197517.3201309) | two-way fluid-solid momentum exchange resolved on MPM background grids |
| Chen, Li, Zhou et al. 2024, *Solid-Fluid Interaction on Particle Flow Maps* | [10.1145/3687959](https://doi.org/10.1145/3687959) | accumulates coupling force along a trajectory, the alternative to this project's accumulator-free path |
| Nakamura, Matsumura and Mizutani 2021, *Particle-to-surface frictional contact algorithm for MPM using weighted least squares* | [10.1016/j.compgeo.2021.104069](https://doi.org/10.1016/j.compgeo.2021.104069) | frictional particle-to-surface contact, the mechanism behind the floor and wall constraints here |
| Martinez-Gomariz, Gomez, Russo and Djordjevic 2017, *A new experiments-based methodology to define the stability threshold for any vehicle exposed to flooding* | [10.1080/1573062X.2017.1301501](https://doi.org/10.1080/1573062X.2017.1301501) | twelve car models at three scales, the most comprehensive stationary-vehicle flume campaign |
| Shah, Mustaffa, Martinez-Gomariz and Yusof 2020, *Hydrodynamic effect on non-stationary vehicles at varying Froude numbers under subcritical flows on flat roadways* | [10.1111/jfr3.12657](https://doi.org/10.1111/jfr3.12657) | one of the few **non-stationary** vehicle studies, and therefore the closest thing in the literature to the gap this project's title names |

### Prior vehicle-fording work exists, and this is a floor rather than a total

This project maintains its own research index, 382 records as built on 2026-08-25.
Queried live, **13 records carry the `vehicle-fording` method tag**, of which roughly
11 to 12 are simulations and one is a trafficability-criteria paper.

That is **a floor from one named view, not a total.** 171 of the 382 records carry no
abstract and were matched on title, authors and journal alone, so a zero from that
index is not evidence of absence. Separate catalogue, graph-hop and author-sweep
views each return their own floor, and those floors must not be added together.
"""


CONTRIBUTION = """
## My contribution

Three items. Each is given with the caveat that makes it survive a check, because a
claim that needs the caveat removed to sound good is not worth publishing.

### 1. The mesh-repair fix: `solidify_watertight` and `is_gaussian_ply`

`solidify_columns` filled every (x, y) column from floor to ceiling, bridging the
ground clearance and the wheel wells shut, and it hollowed surface-only splats.
`solidify_watertight(mesh, h)` replaces it with exact vertical ray parity: collect
every z at which the column axis crosses the surface, sort them, and fill only
between successive entry and exit pairs. `is_gaussian_ply()` reads the PLY header
and tests for `opacity` and `f_dc_0`, the properties the splat reader actually
requires, so a watertight mesh routes to the correct fill path instead of being
guessed at from its file suffix.

**The fill_ratio result is grid-dependent and is not a single number.** Across the
grids the 17 canonical runs actually use:

| grid | runs | fill_ratio |
|---|---|---|
| g48 | 3 | 1.026243 |
| g64 | 11 | 1.002440 |
| g96 | 3 | 0.994089 |

The retired column-fill path gave 2.173 at g64 with an effective density of
142.90 kg/m^3. The parity path gives 1.0023 and 309.78 kg/m^3 at the same grid.
Every project figure quoting a 2.17x or 2.18x over-fill, a 7.70 m3 solid volume, or
a 143 kg/m^3 density is reading the retired algorithm.

**The caveat that must travel with this.** The scene samples the mesh down to 60,000
surface points before solidifying, so **watertightness does not propagate through
the pipeline.** The measured fill_ratio result stands. The claim that the pipeline
preserves watertightness does not, and is not made here.

### 2. The grid-resolution study, g48 / g64 / g96

Nine runs: three grids crossed with three AR&R mass classes, at fixed depth
0.2944294 m and velocity 1.5 m/s.

**The finding is that it does not converge.** Displacement is non-monotone in dx for
both 1100 kg and 1609 kg, and the largest single refinement step changes
displacement by **2.4x**. All nine land NO-FORD, by margins of 1.8x to 13x.

**The binary verdict is grid-invariant. The displacement magnitude is not. Cite the
verdict, never the magnitude.** The mechanism is known rather than anomalous:
classic MPM can lose convergence as the grid refines at fixed particles-per-cell
(Steffen, Kirby and Berzins 2008).

On novelty, stated as a floor with its view named rather than as a total: **no record
tagged `vehicle-fording` in this project's 382-record index reports a grid-resolution
study.** The 7 records tagged `amr-refinement` are MPM and GIMP
refinement-method papers, one of them titled *A Multi-Resolution Material Point
Method*, and the 4 tagged `grid-convergence` are CFD verification methodology
(Roache 1994, Stern 2001, Celik 2007, Syamlal 2017). None is a flood-vehicle study. That is one index's answer, and 171 of its 382 records have no
abstract, so it is a floor and not a proof of absence.

### 3. Applying a closed reconstruct-to-decide pipeline to flood traversability

Reconstruction of a real crossing, simulation of the vehicle in floodwater at that
crossing, and a decision, closed end to end and then checked against stability
criteria produced outside the pipeline.

The framework this sits inside is **Thorpe et al.**, and the closest prior full
pipeline is **arXiv:2607.00673**. Both are credited on the Precedent tab. The
contribution claimed here is the application and the external validation step, and
**not** the physically viable world model framework, which is not mine.
"""

MCP_NOTE = """
---
*This calculator is also exposed as an MCP tool endpoint named `arr_verdict`, so an
agent can query the AR&R joint rule directly. **The endpoint has no built-in rate
limiting** and this Space is public. It is the only endpoint on this page intended
for programmatic use.*
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
        gr.Markdown(SAFETY_NOTICE)

        with gr.Tab("AR&R calculator"):
            gr.Markdown(
                "### The AR&R stationary-vehicle verdict calculator\n\n"
                "The **stationary-vehicle** check this page has always served. "
                "All three AR&R conditions must hold for FORD: depth, velocity, "
                "and the depth-velocity hazard product, each against the limit "
                "for the selected class. Pure arithmetic, live.\n\n"
                "This is a *different* experiment from the load surface tab: the "
                "vehicle here is stationary and free, and the verdict has a "
                "validation basis in AR&R. The load surface has a prescribed "
                "body and carries **no verdict at all**."
            )
            with gr.Row():
                arr_depth = gr.Slider(0.0, 1.5, value=0.30, step=0.05,
                                      label="Flood depth D (m)")
                arr_vel = gr.Slider(0.0, 4.0, value=1.5, step=0.1,
                                    label="Flow velocity V (m/s)")
            arr_class = gr.Radio(choices=list(AV.CLASS_BY_LABEL.keys()),
                                 value=AV.DEFAULT_LABEL, label="AR&R vehicle class")
            arr_out = gr.Markdown()
            arr_inputs = [arr_depth, arr_vel, arr_class]
            arr_depth.change(AV.evaluate, arr_inputs, arr_out, api_name="arr_verdict")
            arr_vel.change(AV.evaluate, arr_inputs, arr_out, api_visibility="private")
            arr_class.change(AV.evaluate, arr_inputs, arr_out, api_visibility="private")
            demo.load(AV.evaluate, arr_inputs, arr_out, api_visibility="private")
            gr.Markdown(MCP_NOTE)

        with gr.Tab("My contribution"):
            gr.Markdown(CONTRIBUTION)

        with gr.Tab("Precedent"):
            gr.Markdown(PRECEDENT)

        with gr.Tab("Validated hull"):
            if HULL_GLB.exists():
                gr.Model3D(
                    value=str(HULL_GLB),
                    label="yaris_coarse_v1l_watertight (canonical Yaris)",
                    display_mode="solid",
                )
            gr.Markdown(HULL_NOTE)

        with gr.Tab("Reconstruction"):
            if SPLAT_PLY.exists():
                gr.Model3D(
                    value=str(SPLAT_PLY),
                    label="drainA, 30k iterations, 1,147,694 Gaussians",
                )
                gr.Markdown(SPLAT_NOTE)
            else:
                gr.Markdown(SPLAT_MISSING)

        with gr.Tab("Verdict flips"):
            gr.Markdown(
                "### Where the verdict flips\n\n"
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
            slider.change(on_threshold, slider, [plot, notes], api_visibility="private")
            demo.load(on_threshold, slider, [plot, notes], api_visibility="private")
            gr.Markdown(
                "> **Unit trap.** `slide_m` (0.05 m), `slide_speed_ms` (0.05 m/s) and "
                "`float_m` (0.05 m) share one numeral across two units. They must be "
                "deduplicated by name and unit, never by value."
            )

        with gr.Tab("Load surface"):
            gr.Markdown(
                "### Load surface, `v_car` x `v_water`\n\n"
                "Most published work collapses vehicle speed and flow speed into a "
                "single relative speed. This matrix keeps them as separate axes, and "
                "every cell is a mean over five seeds rather than a single point."
            )
            gr.Plot(value=_surface_figure())
            gr.Markdown(
                "### The spread at fixed relative speed\n"
                "If a scalar relative speed determined the load, every bar below would "
                "have zero height."
            )
            gr.Plot(value=_split_figure())
            gr.Markdown(
                "### The same cells, two measurement windows\n"
                "The left bar of each pair is the window the source write-up published."
            )
            gr.Plot(value=_window_figure())
            gr.Markdown(value=surface_notes())

        with gr.Tab("Repeat spread"):
            gr.Plot(value=_repeat_figure())
            gr.Markdown(REPEAT_NOTE)

        with gr.Tab("Limitations"):
            gr.Markdown(SCOPE_STATEMENT)
            gr.Markdown(DISCLAIMER)
            gr.Markdown(VEHICLE_CLASS_NOTE)
            gr.Markdown(SAFETY_NOTICE)

        gr.Markdown(
            "---\n**Josie Cerrell**, NSF SCIPE REU, GeoElements Lab, UT Austin. "
            "PI Krishna Kumar.\n\n"
            "The physically viable world model framing this project applies is due to "
            "Thorpe et al., arXiv:2605.30542. See the Precedent tab."
        )
    return demo


if __name__ == "__main__":
    build().launch(theme=gr.themes.Soft(), mcp_server=True)
