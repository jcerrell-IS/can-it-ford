---
name: flood-vehicle-mp4-is-model-scale-truck
description: "The Jul 13 flood_vehicle.mp4 is the bundled model-scale truck splat (1.447m, 28.7kg), not the Yaris and not full scale; reproduces to 0.43 percent but stays UNVERIFIED"
metadata: 
  node_type: memory
  type: project
  originSessionId: ae5a83d3-a745-4e78-b5ae-dbb8b6177c2d
  modified: 2026-07-25T22:42:23.534Z
---

`mpm-engine/out/flood_vehicle/flood_vehicle.mp4` (Jul 13 18:53, 372509 B) was produced by
the pure DEFAULTS of `examples/flood_vehicle.py`: `truck_trimmed.ply`, depth 0.12 m,
velocity 1.5 m/s, n_grid 64, vehicle_density 250. Verified live 2026-07-25 by re-running
and reproducing dx/dmag/yaw to within 0.43 percent over all 91 frames.

The vehicle is the engine's bundled 3DGS demo splat at MODEL SCALE: extent
0.45 x 1.447 x 0.411 m, realized mass 28.7 kg, domain lim 3.1834 m. It is NOT the Yaris,
NOT 1100 kg, NOT 4.28 m. The script's own docstring says Froude scaling (lam=3.8) is
required to read it as a real event. Water is 5 layers, not 4 (the 4-layer and 2.18x
over-fill figures are Yaris numbers at lim=9.42 m, a different scene, see
[[genesis-p2g-crash-is-grid-density]] for the other track).

**Why:** this artifact keeps getting cited as the project's MPM car render. It is a demo
of the pipeline, not a vehicle result, so no ford/float claim can rest on it.

**How to apply:** never quote dx=0.707 m, depth 0.12 m or velocity 1.5 m/s as full-scale
numbers without stating the Froude conversion. Label stays UNVERIFIED: `flood_vehicle.py`
saves no particle positions, so "no particles outside domain" cannot be checked at all,
and vehicle-vs-density cannot be checked because local depth at the vehicle is never
logged. Capturing the grid/lim line does not close either one.

Operational gotcha found the same day, and CORRECTED later that session: `ffmpeg` IS on
PATH at `/usr/bin/ffmpeg` on both login and compute nodes, but it is BROKEN, failing with
`libunwind.so.8: cannot open shared object file`. A shared-library failure exits 127, the
same code as command-not-found, which is why it was first misread as "ffmpeg absent". No
Vista module provides ffmpeg. So `write_mp4` fails on every node every time, after
metrics.csv and the PNG frames are already written. That is why the Jul 13 frames are
18:08 and the mp4 is 18:53: physics succeeded, encode failed, mp4 was assembled
separately later. Do not re-diagnose this as a PATH or module problem.
