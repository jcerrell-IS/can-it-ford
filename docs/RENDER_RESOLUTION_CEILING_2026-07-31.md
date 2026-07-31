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
