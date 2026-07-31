---
name: v2-geometry-warped-invalid
description: "v2 sweep geometry is fit_to_bbox-warped truck_trimmed.ply, never visually confirmed, diverges 4.6x from unwarped reference; no v2 figure goes on the poster until the --vehicle yaris real-mesh path replaces it"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa34788-17cf-475b-8c0c-766cdb8cfdc7
  modified: 2026-07-24T03:25:40.583Z
---

DATA VALIDITY RULE (now written in Vista's CLAUDE.md, told by Josie 2026-07-20):
The `data/track1_sweep_v2/` manifest was built by `fit_to_bbox()` **anisotropically
warping** a single generic `truck_trimmed.ply` into sedan/pickup/suv bounding boxes. That
warped geometry has never been rendered or visually confirmed, and it diverges **4.6x** from
a reference run of the unwarped mesh at identical depth/velocity.

Consequence: NO figure drawn from the v2 sweep may go on the poster, not even a provisional
binary FORD/NO-FORD one, because it gets thrown out once the real geometry replaces it. The
fix is to switch the sweep to the `--vehicle yaris` path (real mesh, no anisotropic warping)
before ANY poster figure is generated from this sweep.

CORRECTION 2026-07-23: the "already smoke-tested" claim above was wrong. The `--vehicle yaris`
path could not load its mesh at all: `load_vehicle` branched on the `.ply` suffix alone and
sent the watertight mesh to the 3DGS splat reader, dying on `ValueError: no field of name
opacity`. `--dry-run` did not catch it because preflight exited before ever touching the
loader, so it printed all-OK vacuously. Both fixed and committed 2026-07-23 (mpm-engine
fd390d6 content-based ply dispatch, can-it-ford f4850bc preflight actually loads geometry),
verified on Vista: mesh loads L=4.28 W=1.75 H=1.52 m vs cited bbox (4.30, 1.70, 1.47), and
density at the v2 grid pitch is 143.1 kg/m^3, inside the 100-300 band. Loader is unblocked;
the replacement Yaris sweep itself still needs a GPU run before any figure exists.

CORRECTION 2026-07-25, STALENESS GATE S-1: **the 143.1 kg/m^3 figure above is OBSOLETE.**
It was produced by `solidify_columns`, which bridges every (x,y) column floor to ceiling and
over-filled the body 2.17x (7.70 m3 against a true hull of 3.5427 m3). `solidify_watertight`
(exact vertical ray parity) replaced it and is live in
`/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py:88`, still UNCOMMITTED.
Re-derived live on the Mac 2026-07-25 at n_grid=64, h=0.0736065 m: 8904 particles,
solid volume 3.55086 m3, **fill_ratio 1.0023**, **rho 309.78 kg/m^3** at 1100 kg. Both the
Mac and Vista paths agree to the digit. Do not cite 143 kg/m^3, 7.71 m3 or 2.18x as current;
they describe the retired algorithm only.

Consequence worth carrying: rho 310.5 (= 1100 / 3.5427, the correct pairing) sits ABOVE the
project's 100-300 kg/m^3 plausibility band. The band was only ever satisfied because the
over-fill diluted density. Widen the band or restate it; do not "fix" the vehicle to re-enter
it. See [[solidify-watertight-supersedes-column-fill]].

This is a second, more fundamental blocker on the phase-space poster figure, on top of
[[v2-timeseries-no-velocity-cols]] (which blocks the failure-mode overlay specifically).
`analysis/build_poster_phase_space.py` output paths were fixed 2026-07-20 to write
`figures/phase_space_poster_figure.png/svg`, but it must NOT be run against v2 data; its
L2_CSV source still points at track1_sweep_v2 and needs repointing to the Yaris sweep once
that exists.
