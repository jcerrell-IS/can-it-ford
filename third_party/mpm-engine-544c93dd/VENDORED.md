# VENDORED SOURCE, kks32/mpm-engine

Fetched 2026-07-25 by Claude Code for the Can It Ford render work.
Nothing here is modified. Local reimplementations live in the project tree,
not in this directory.

- Repo: https://github.com/kks32/mpm-engine
- Pinned SHA: `544c93dd02cb9c7ead89e1155a62967243244fce`
- License: **MIT**, confirmed by fetching `LICENSE` at the pinned SHA
  ("Copyright (c) 2026 The mpm-engine authors (see AUTHORS.md)")
- Raw URL pattern:
  `https://raw.githubusercontent.com/kks32/mpm-engine/<SHA>/<path>`

| local file | upstream path | fetched at |
|---|---|---|
| `examples/common.py` | `examples/common.py` | main (unpinned, first pull) |
| `examples/dough_surface_render.py` | `examples/dough_surface_render.py` | main (unpinned, first pull) |
| `examples/flood_vehicle.py` | `examples/flood_vehicle.py` | main (unpinned, first pull) |
| `splats/appearance.py` | `src/warpmpm/splats/appearance.py` | main (unpinned, first pull) |
| `tests/test_vehicle.py` | `tests/test_vehicle.py` | main (unpinned, first pull) |
| `vehicle_main.py` | `src/warpmpm/vehicle.py` | **544c93dd** |
| `nclaw_geom_render.py` | `examples/recovery/nclaw_geom_render.py` | **544c93dd** |
| `LICENSE` | `LICENSE` | **544c93dd** |

## Provenance caveat

The first five files were fetched from `main` before a SHA was pinned, so they
are reproducible only if `main` has not moved. The three marked **544c93dd**
are pinned. Re-fetch the first five at the pinned SHA before any of them is
cited in the paper or committed.

## Divergence from upstream that matters

`vehicle_main.py` (upstream @ 544c93dd) differs from the copy that actually ran:

| | upstream 544c93dd | local `vehicle_live.py` / Vista `fd390d6` |
|---|---|---|
| PLY dispatch | `if path.suffix.lower() == ".ply":` (L121) | `... and is_gaussian_ply(path):` (L221) |
| solid fill | `solidify_columns(pos, h)` always | `solidify_watertight(oriented, h)` when watertight |

Upstream would route a watertight mesh PLY into `load_gaussians_ply` and fail.
The runs used the patched local copy. `solidify_watertight` is exact vertical
ray parity, which is why mesh containment of the solid particles is 100.00%,
not the partial value that `solidify_columns` would give.
