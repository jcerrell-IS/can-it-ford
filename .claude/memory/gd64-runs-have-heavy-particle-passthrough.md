---
name: gd64-runs-have-heavy-particle-passthrough
description: "The Genesis gd=64 runs that complete have 21-31% of water particles inside the vehicle body, so they fail the project's own plausibility gate"
metadata: 
  node_type: memory
  type: project
  originSessionId: f757b3cb-cd6c-49bc-88dd-9934cd779aea
  modified: 2026-07-24T03:50:01.068Z
---

From the script's own `n_penetrating` diagnostic (counts water particles strictly inside
the vehicle AABB, exact for the axis-aligned box vehicle) in the two runs that completed
on 2026-07-23 at grid_density=64:

- d=0.30m, v=0.0 m/s: 39,239 / 189,000 particles inside the vehicle (20.8%) at t=1.0s,
  rising to 51,056 (27.0%) at t=1.996s, max penetration 7.5 cm.
- d=0.60m, v=2.0 m/s: 89,880 / 378,000 (23.8%) at t=0.9s, rising to 118,792 (31.4%) at
  t=1.996s, max penetration 8.9 cm. J_min drops to 0.153 (severe local compression)
  against a healthy 0.996 at t=0.

Also in the d=0.60/v=2.0 run: the vehicle's front face crosses the padded x+ domain
boundary at t=0.848s (dx > 1.17m), less than halfway through the 2.0s run. The reported
peak x_disp of 1.7658m and the NO-FORD verdict are therefore computed partly with the
vehicle outside the MPM domain.

**Why:** CLAUDE.md's plausibility gate requires "no particles outside domain or clipped
through geometry." These runs complete and write artifacts, but they violate that gate,
so "it runs" is not "it is correct." The verdict column in
`data/phase_space_results_mpm.csv` for these two runs is not yet trustworthy.

**How to apply:** do not put a gd=64 Genesis number or verdict on the poster or in the
paper. Two separate fixes are needed first: raise resolution to stop pass-through (blocked
by [[genesis-p2g-crash-is-grid-density]]) and lengthen the domain downstream in x so the
vehicle cannot exit it within the 500-step horizon.
