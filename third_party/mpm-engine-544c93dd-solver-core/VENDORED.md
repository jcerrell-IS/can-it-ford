# VENDORED SOURCE, kks32/mpm-engine SOLVER CORE

Fetched 2026-08-07 by Claude Code for the Option A in/outflow boundary condition
work (`docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md`, Session 1 task 1).
Nothing here is modified. Local reimplementations live in the project tree,
not in this directory.

This is a SEPARATE, independently-provenanced vendoring from
`third_party/mpm-engine-544c93dd/`. That directory is a partial pull for render
work and its own `VENDORED.md` states it does not contain the solver core.
This directory holds the solver core and nothing else. Do not merge the two,
and do not edit either in place: both provenance tables are load-bearing.

- Repo: https://github.com/kks32/mpm-engine
- Pinned SHA: `544c93dd02cb9c7ead89e1155a62967243244fce`
- License: **MIT**, `LICENSE` fetched at the pinned SHA
  ("Copyright (c) 2026 The mpm-engine authors (see AUTHORS.md)")
- Raw URL pattern:
  `https://raw.githubusercontent.com/kks32/mpm-engine/<SHA>/<path>`

Every file below was fetched at the pinned SHA, then verified by re-fetching and
comparing sha256. All five matched.

| local file | upstream path | bytes | sha256 |
|---|---|---|---|
| `core/solver.py` | `src/warpmpm/core/solver.py` | 32,679 | `57810f1b56de04eec1694711ca1c72d880faf237a2cc63bb42af505f53bf9b9f` |
| `kernels/mpm_solver_warp.py` | `src/warpmpm/kernels/mpm_solver_warp.py` | 156,443 | `285139395097a914b883fe114e8633cf8c8cf8ccc3a3afbbb57c7e3aa1f12128` |
| `kernels/mpm_utils.py` | `src/warpmpm/kernels/mpm_utils.py` | 66,538 | `dd39397486d446010336a3237dfac0088e831a61f3954ff086741e95c18e4c61` |
| `materials/__init__.py` | `src/warpmpm/materials/__init__.py` | 8,660 | `987f12b5a517741059569422c704a41262492354b2418dc2b286cde115b8d16c` |
| `LICENSE` | `LICENSE` | 1,096 | `0df6b3bb5b29429d68a96b1cb2dafda884a28e48d4e1d5051d29b5db55c05cbb` |

## Path correction against the Session 1 plan

`docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md` task 1 names three files to fetch.
Two of the three do not exist at the pinned SHA and return HTTP 404:

| plan file path | HTTP | actual path |
|---|---|---|
| `src/warpmpm/core/solver.py` | 200 | unchanged |
| `src/warpmpm/core/mpm_solver_warp.py` | **404** | `src/warpmpm/kernels/mpm_solver_warp.py` |
| `src/warpmpm/materials.py` | **404** | `src/warpmpm/materials/__init__.py` (a package, not a module) |

`kernels/mpm_utils.py` is not named in the plan file at all and was added here
deliberately: it holds the actual P2G/G2P transfer kernels, and the
`particle_selection` activation gate and the `periodic_x` wrap are readable
ONLY in this file. A vendoring limited to the three named paths would have
missed both.

## License caveat, carried over

`src/warpmpm/kernels/` is the upstream warp-mpm core. The project's
`flood-mpm-debugging-reference` skill records that this subtree has no license
file of its own, distinct from the group's MIT-licensed code. The MIT `LICENSE`
above is the repository's. Cite `kernels/` rather than treating it as freely
re-licensable.

## Why these four

Session 1 needed to answer whether a real grid-face boundary condition is
reachable in warpmpm, or whether an in/outflow BC has to be a particle-level
trick. Findings are in `docs/OPTION_A_SESSION1_FINDINGS.md`. Briefly:

- `core/solver.py` is the typed call surface every scene uses, including all
  four entry points `renders/yaris_render_s1/sim_standing.py` calls. It also
  hardcodes gravity, which had been recorded project-wide as unknown.
- `kernels/mpm_solver_warp.py` holds collider and BC registration
  (`set_velocity_on_cuboid`, `add_bounding_box`, `add_surface_collider`) and the
  particle import/export surface.
- `kernels/mpm_utils.py` holds the transfer kernels and the activation gate.
- `materials/__init__.py` defines `newtonian()`, needed to confirm nothing
  shadows the gravity term.
