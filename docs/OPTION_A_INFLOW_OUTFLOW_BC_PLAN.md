# Option A: In/Outflow Boundary Conditions for warpmpm

Status: planning only, no BC code written yet. Session 1 is verification,
not implementation.

## Corrected citation, 2026-08-07

This is NOT Krishna Kumar's paper. Prior versions of the project docs said
it was. That was wrong and has been corrected in
`_inbox/CAN_IT_FORD_PROJECT_INSTRUCTIONS_v8.md` and
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`.

Zhao, X., Bolognin, M., Liang, D., Rohe, A., Vardon, P. J. (2019).
Development of in/outflow boundary conditions for MPM simulation of
uniform and non-uniform open channel flows. Computers & Fluids, 179, 27-33.
DOI 10.1016/j.compfluid.2018.10.007.

Authors are Cambridge, TU Delft, Deltares. Implemented in Anura3D, a
Delft-lineage MPM code with no relationship to warpmpm or cb-geo/mpm.
This means implementing the method in warpmpm is a full translation job,
not a port, there is no shared codebase to lean on.

## What the paper actually says, verified via Scite full-text search
and cross-confirmed across five independent citing papers, not
reconstructed from a title alone

Method: velocity-controlled inflow BC, pressure-controlled outflow BC,
for MPM. The formulation adds and removes material points at the domain
edges with correct kinematic properties as flow proceeds, rather than
holding the particle count fixed.

Named prior approach they replace: quasi-steady in/outflow using a large
reservoir to supply material points to the domain of interest. This is
structurally what `sim_standing.py`'s tank already does, just without an
active add/remove mechanism at the boundary, it is a recognized precursor
technique in this exact literature, not an ad hoc workaround.

Validation cases: uniform open channel flow, and free overfall, a
transient case caused by a sudden bed-level drop, chosen deliberately as
a stringent test because of the rapid geometry change. Brink depth,
pressure distribution, and velocities all matched analytical solutions
and experimental measurements.

One directly reusable modeling note: they reduce the water bulk modulus
by roughly 100x from the physical value to allow a larger explicit time
step, and state this is valid as long as the resulting numerical sound
speed stays above 10x the maximum flow velocity, citing Liang (a
co-author here). This is the same Monaghan 10x convention already in
this project's own literature base, and gives a second, independent
citation for it.

## What is verified to exist on this machine right now, 2026-08-07

- `renders/yaris_render_s1/sim_standing.py`: the canonical 17-run driver.
  DO NOT EDIT. Imports `from warpmpm.core.solver import GridConfig, Solver`
  and `from warpmpm.materials import newtonian`. These import paths are
  the ground truth for where the real package lives upstream.
- `simulation/sim_dam_break.py`: new file, written 2026-08-07, syntax
  checked only, never run. Reuses the same particle-seeding and
  rigid-body pattern as sim_standing.py with a gravity-driven reservoir
  release instead of a velocity clamp.
- `third_party/mpm-engine-544c93dd/`: a PARTIAL vendoring, pulled
  2026-07-25 for render work only. Contains examples, splats/appearance.py,
  tests/test_vehicle.py, vehicle_main.py, nclaw_geom_render.py, LICENSE.
  Its own VENDORED.md states plainly that vehicle_main.py here is the
  raw upstream copy and differs from vehicle_live.py, the patched copy
  that actually produced the 17 runs, in exactly two ways: PLY dispatch
  and solidify routing. Do not treat this directory as a complete or
  currently-accurate copy of the vehicle loader, and do not treat it as
  containing the solver core at all, it does not.
- Confirmed absent from this machine, full disk search, zero hits:
  `mpm_solver_warp.py`. The solver core that actually defines gravity,
  rigid body state, grid boundaries, and particle loading is not vendored
  anywhere locally right now. Any claim about its exact line numbers in
  this project's memory predates this session and must be re-verified,
  not assumed.

## Session 1 task list, in order

1. Fetch `src/warpmpm/core/solver.py`, `src/warpmpm/kernels/mpm_solver_warp.py`
   (NOT `core/mpm_solver_warp.py`, that path 404s at this SHA), and
   `src/warpmpm/materials/__init__.py` (a package, not a flat file) from
   `https://github.com/kks32/mpm-engine` at pinned SHA
   `544c93dd02cb9c7ead89e1155a62967243244fce` into a new directory,
   `third_party/mpm-engine-544c93dd-solver-core/`, with the same
   VENDORED.md-style provenance table the existing partial vendoring uses.
   Also fetch `src/warpmpm/kernels/mpm_utils.py`, the actual transfer
   kernels live there, not in mpm_solver_warp.py alone.
   DONE 2026-08-07, see docs/OPTION_A_SESSION1_FINDINGS.md.
2. Read `load_particles`, `add_plane`, `add_domain_walls`, and
   `set_material_range` in the fetched solver.py. These are the four
   solver entry points sim_standing.py actually calls. Any BC
   implementation has to slot into this exact call surface, since that
   surface is what stays compatible with the canonical script's pattern.
3. Confirm whether the grid in mpm_solver_warp.py exposes any node-level
   hook where a velocity or pressure Dirichlet condition could be applied
   at a domain face, versus whether it only supports whole-particle
   operations. This determines whether the BC has to be a particle-level
   trick, matching sim_standing.py's existing `_sustain_inflow` pattern
   but made bidirectional, or whether a real grid-face BC is reachable.
4. Only after 1 through 3 are done, write a short findings note, then
   propose (not implement) a design: where particles get added at the
   inflow face, where they get removed at the outflow face, and what the
   pressure-controlled outflow condition maps to given whatever the
   solver actually exposes.
5. Do not write BC implementation code in this session. Session 2 starts
   from the design note.

## Guardrails

Never edit `renders/yaris_render_s1/sim_standing.py`.
Never edit anything under `third_party/mpm-engine-544c93dd/` in place,
that directory's provenance table is load-bearing and editing its files
breaks the SHA pinning it documents.
All new solver-core vendoring goes in a new, separately-provenanced
directory as described above.
All new BC code goes in `simulation/`, new files only.
If a skill named in a Claude Code prompt is not installed, say so and
continue, do not silently substitute.
