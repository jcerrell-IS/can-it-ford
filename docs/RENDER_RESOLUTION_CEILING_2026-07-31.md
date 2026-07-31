# PyVista offscreen render resolution ceiling, measured 2026-07-31

Measured empirically on the Mac against every `probe_*` and `hero_*` PNG in
`renders/yaris_render_s1/`. Not inferred from a driver spec sheet.

## The ceiling

| | Width | Dimensions | Megapixels | Result |
|---|---|---|---|---|
| Highest working | **7168 px** | 7168 x 4032 | 28.9 | real image, 12.65 MB |
| Lowest failing | **7680 px** | 7680 x 4320 | 33.2 | black, 0.09 MB |

The ceiling sits between 28.9 and 33.2 megapixels. Nothing at or below
7168 x 4032 failed; nothing at or above 7680 x 4320 succeeded.

## Failure signature

A failed render is **not** a crash, a traceback, or a non-zero exit. It is a
valid PNG of the correct dimensions containing a single colour:

- exactly 1 unique RGB triple after downsampling
- mean RGB (0, 0, 0), pure black
- file size collapses to roughly 0.09 to 0.42 MB, versus 3 to 13 MB for a real
  render at comparable dimensions

File size alone is the fastest smell test, but unique-colour count is the
reliable one, because a legitimately dark render would still carry thousands of
distinct values.

## Dead files, do not use

| File | Dimensions | Size | Unique colours |
|---|---|---|---|
| `renders/yaris_render_s1/hero_g64_m1100_f45_max.png` | 16384 x 9216 | 0.42 MB | 1 |
| `renders/yaris_render_s1/probe_8192x4608.png` | 8192 x 4608 | 0.10 MB | 1 |
| `renders/yaris_render_s1/probe_7936x4464.png` | 7936 x 4464 | 0.10 MB | 1 |
| `renders/yaris_render_s1/probe_7680x4320.png` | 7680 x 4320 | 0.09 MB | 1 |

`hero_g64_m1100_f45_max.png` is the one most likely to be picked up by mistake:
its name implies it is the best available asset and it is the largest by
dimension, but it is empty.

## Files confirmed real

`hero_probe.png` (1600x900), `probe_3200x1800`, `probe_4096x2304`,
`hero_g64_m1100_f45_4K_2026-07-30` (3840x2160), `probe_6144x3456`,
`probe_6656x3744`, `probe_7168x4032`, `hero_g64_m1100_f45_7168` (7168x4032).
All carry roughly 1850 unique colours and mean RGB (147, 144, 136).

`hero_g64_m1100_f45_7168.png` and `probe_7168x4032.png` are both 12.65 MB at
identical dimensions and are almost certainly the same image under two names.

## The underlying bug: silent success

`render_pv.py`, `render_pv3.py`, and `render_pv_fixed.py` all accept an
unbounded resolution and never check that anything was drawn.

| File | Line | What it does |
|---|---|---|
| `render_pv.py` | 102-103 | `--width` / `--height` as bare `type=int`, no upper bound |
| `render_pv.py` | 148 | passes them straight into `pv.Plotter(off_screen=True, window_size=(a.width, a.height))` |
| `render_pv.py` | 207 | `pl.screenshot(...)` then `print("HERO", ...)` |
| `render_pv3.py` | 115-116, 177, 246 | same pattern |
| `render_pv_fixed.py` | 110-111, 156, 215 | same pattern |

When `window_size` exceeds what the offscreen GL context can allocate, VTK does
not raise. It returns an empty framebuffer, PyVista writes it, and the script
prints its success line and exits 0. This is the **silent success** failure class:
wrong output that looks like right output, with nothing in the log to indicate a
problem. It is the same shape as the argparse positional-mismatch bug of July 12,
which produced plausible-looking numbers from inputs that never reached the
script.

Suggested guard, one check after every `screenshot` call: reopen the written PNG
and reject it if the unique-colour count is 1. That is three lines and it
converts an invisible failure into a loud one.

## Practical guidance

Cap offscreen renders at **7168 x 4032**. That is already far beyond any print
need: IEEE single column at 300 dpi is roughly 1050 px wide and double column is
roughly 2148 px, so 7168 px is over three times the widest a two-column figure
can use. Requesting more than 7168 px buys nothing even when it does not fail.

---

# DO-NOT-MERGE-AS-IS: the C_D = 1.38 attribution

Unrelated to the render ceiling, recorded here because it is the other unmerged
artifact that would fail an audit if it reached the paper.

## Where it lives

| | |
|---|---|
| Branch | `claude/festive-goodall-e08861` |
| Worktree | `.claude/worktrees/amazing-kowalevski-9df04d` |
| File | `analysis/paper_fig_force_balance_v2.py` |
| Line 25 | `C_D = 1.38` |
| Line 37 | `"C_D": "Smith, Modra & Felder 2019, 1:18 scale Toyota Yaris flume measurement"` |

C_D is consumed at line 83 in the drag force and at line 96 in the critical
velocity, so it propagates into both panels of the figure.

## Failure 1, the attribution fails a title check

Crossref `10.1111/jfr3.12527`, queried live 2026-07-31, returns:

> Full-scale testing of stability curves for vehicles in flood waters
> Smith, Grantley P.; Modra, Benjamin D.; Felder, Stefan
> Journal of Flood Risk Management, 2019

The generator credits that DOI's paper with a **1:18 scale flume measurement**.
Full-scale testing and 1:18-scale flume work are different experiments. The
attribution as written cannot be correct.

## Failure 2, the value is unattributed anywhere reachable

`1.38` appears **zero times** in either source that could plausibly carry it:

- Azhar et al. 2023, local full text at `~/Zotero/storage/6Y7VPLP7/`: 0 occurrences.
  Its Table 4 does survey drag coefficients for semi-submerged bodies, citing
  Malavasi and Guadagnini (2003), who worked in subcritical flow only and assumed
  a constant frontal area, and Arslan et al. (2013). No 1.38.
- `vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md`: 0 occurrences.

## Failure 3, applied as a constant across a regime boundary it straddles

The only regime rule available in the repo is Al-Qadami et al. 2023
(`10.3390/su151713262`, *Sustainability*), quoted at
`Simulation_Ready_Vehicle_Mesh_Assets.md` line 303: the drag coefficient is
"less than 1 for supercritical flows and more than 1 for subcritical flows."

Froude numbers at the four depths the figure plots, at the paper's 1.5 m/s test
velocity, Fr = v / sqrt(g d):

| Depth | Fr | Regime | Al-Qadami expects |
|---|---|---|---|
| **0.15 m** | **1.237** | **supercritical** | **C_D < 1** |
| 0.30 m | 0.874 | subcritical | C_D > 1 |
| 0.45 m | 0.714 | subcritical | C_D > 1 |
| 0.60 m | 0.618 | subcritical | C_D > 1 |

1.38 is consistent with the three subcritical depths and inconsistent with the
supercritical one. That single exception is the one that matters: buoyancy zeroes
the normal force at every depth at or beyond roughly 0.20 m, so 0.15 m is the
**only** plotted depth where friction is non-zero and therefore the only depth
where C_D changes the answer at all. The figure applies a subcritical-regime
coefficient at the one point that is supercritical.

## Verdict

**DO NOT MERGE AS IS.** Not fixed here, because this generator is not shipping
and inventing a replacement coefficient would repeat the original error with
better arithmetic. Before it is ever used: source 1.38 to a real measurement, or
replace it with a Froude-dependent C_D, and correct the line 37 attribution.

## Incidental find worth keeping

The same Al-Qadami abstract states the vehicle "experienced the floating
instability mode once the flow depth reached 0.38 m". That is the origin of the
0.38 m figure the paper previously carried as an unverified placeholder. It is
citable as `10.3390/su151713262`, but note it is a **CFD numerical** result on a
full-scale medium-size passenger vehicle, not a physical measurement, so
"measured critical flow depth" would be the wrong phrasing for it.
