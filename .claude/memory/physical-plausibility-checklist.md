---
name: physical-plausibility-checklist
description: Canonical physics-property decisions locked in CLAUDE.md + flood-mpm skill Part 3; two live code discrepancies still open
metadata: 
  node_type: memory
  type: project
  originSessionId: 968ca9c6-0d28-4487-a369-19d64e80541f
  modified: 2026-07-21T16:19:58.121Z
---

The "make it physically plausible, not just pretty" checklist is now recorded as cited
one-line decisions in BOTH the project CLAUDE.md (new "PHYSICAL PLAUSIBILITY CHECKLIST"
section, added 2026-07-21) and the flood-mpm-debugging-reference skill (Part 3). Keep the
two in sync.

Canonical decisions: vehicle mass 1078kg / rho=304.28 (NCAC, most defensible; MASH nominal
1100kg/rho=310.47 acceptable if labeled). friction=0.55 cite Azhar et al. 2023. SDF colliders
not CDF. Water bulk modulus softened for stability (wave speed not real, state in Limitations).
Failure modes slide/topple/float (Shand 2011), "stuck" is baseline not a 4th mode. DRIFT_THRESHOLD
0.05m is a numerical onset-of-motion tolerance, not a physical criterion (Xia 2014, Shah 2018).

**Why:** these were drifting silently across scripts, which is the exact failure the checklist
guards against. **How to apply:** rho=304.28 presupposes the ~3.543 m3 real-mesh volume, NOT the
12.01 m3 box proxy, so applying it is a coupled edit not a find-replace.

TWO LIVE DISCREPANCIES as of 2026-07-21 grep (verify before trusting):
- Sedan scripts still use rho=115.7 (can_it_ford_L2_mpm.py) and rho=604 (can_it_ford_L2.py,
  _ytest.py), none match the 304.28 decision. full_scale_test.py mass=1930 is the Track-1 truck
  (different vehicle, not a conflict).
- friction=0.55 is live in box_sdf_collider_setup.py:78 and can_it_ford_L2_mpm.py, but
  designsafe-staging/scripts/can_it_ford_L2.py:40,132 still uses coup_friction=0.4.

Not yet propagated: the Vista copy /work/11603/jcerrell0629/vista/CLAUDE.md and the claude.ai
chat project instructions both need the same checklist pasted in. See [[v2-geometry-warped-invalid]].
