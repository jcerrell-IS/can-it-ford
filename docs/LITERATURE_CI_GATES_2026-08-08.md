# Literature-backed CI gates, 2026-08-08

Citation bank for `.claude/checks/physics_gates_literature.py`, kept here so the
references survive independently of the code. The gate module is imported and
called by `.claude/checks/params_check.py`, which is in turn run by the commit
gate at `.claude/hooks/pretooluse_git_commit_gate.py:19-26`.

Sourced from a 68-paper Undermind review conducted in a separate chat session.

## CITATION STATUS: UNVERIFIED

Every DOI and author string below was carried in from that chat session and
**has NOT been checked against a primary source in this session**. Per the
project rule in `CLAUDE.md` ("a claim cited from another session's confidence
is not a second source, it is the same source cited twice"), none of these may
enter the paper, the poster, or a report to Kumar until each is resolved
against its own record. What IS verified live in this session is the repo-side
behaviour: which gate fires, on what data, and with what result.

Two known holes in the bank itself:

1. `energy_conservation` (Bardenhagen 2002) has **no gate function**. It is a
   citation with nothing calling it.
2. `gate_floor_restitution` has **no entry in `LITERATURE_GATES`**. It is a
   repo-internal check on open item 31, not a literature-derived one. Do not
   cite it as if it were.
3. `gate_sound_speed_cfl` emits the phrase "Monaghan 10x convention" in its
   own failure text, but Monaghan appears nowhere in `LITERATURE_GATES`. The
   convention is load-bearing for the verdict and currently uncited.

## The table

| Key | Citations |
| --- | --- |
| `mass_inertia_cog` | Brannon Kamojjala Sadeghirad 2011; Allen Klyde Rosenthal Smith 2003 SAE 2003-01-0966 |
| `geometry_bbox` | Kamojjala Brannon Sadeghirad Guilkey 2013 doi:10.1007/s00366-013-0342-x |
| `sound_speed_cfl` | Ni Zhang 2020 doi:10.1002/nme.6506; Bai Schroeder 2022 doi:10.1111/cgf.14620; Sun Shinar Schroeder 2020 doi:10.1111/cgf.14101; Isik He 2022 doi:10.1007/s40571-022-00511-8 |
| `energy_conservation` | Bardenhagen 2002 doi:10.1006/JCPH.2002.7103 |
| `resolution_convergence_gci` | Roache 1994 doi:10.1115/1.2910291; Celik Ghia Roache Freitas 2007 doi:10.1115/1.2960953 |
| `manifest_provenance` | Huber et al 2020 doi:10.1038/s41597-020-00638-4; Dhruv Dubey Barba Gesing 2023 doi:10.1109/MCSE.2023.3314288 |

## What each gate closes

- **`gate_mass_declared`** closes the hole where an unreviewed vehicle mass
  reaches a gated run without anyone noticing the override.
- **`gate_inertia_not_read_by_solver`** closes the reverse of the standing
  inertia gap: it blocks if `inertia_tensor` or `cg_height` ever starts
  reaching the solver, which commit `fe91c50` established is a regression, not
  an upgrade.
- **`gate_hull_volume`** closes the case where a hardcoded hull constant drifts
  away from the canonical `yaris_coarse_v1l_watertight.ply` value of 3.542739
  m3 and silently changes every density downstream.
- **`gate_floor_restitution`** is meant to close open item 31, whether the
  floor plane registers as a rigid contact surface rather than acting on water
  only. **It does not actually close it, see the defect below.**
- **`gate_sound_speed_cfl`** closes the case where an artificial sound speed
  sits close enough to the flow speed that the rigid-body outcome could be an
  artefact of compressibility rather than physics.
- **`gate_resolution_convergence_gci`** closes the case where a convergence
  claim or an error band gets reported from data that cannot support one,
  by refusing to emit a GCI number when the refinement ratio is not constant
  or the response is non-monotone.
- **`gate_manifest_completeness`** closes the case where a published run cannot
  be traced back to the code, the mesh, and the environment that produced it.

## Verified live, 2026-08-08

All results below were produced by running the gates against real repo data,
not asserted. Reproduce with `python3 .claude/checks/params_check.py`.

### The CFL formula is exact against the solver

`gate_sound_speed_cfl` computes `c = sqrt(bulk * gamma / rho0)`. This matches
`simulation/validate_coupling_force.py:45-46` exactly, and `gamma = 1.1` traces
to the pinned solver at
`third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_utils.py:43`.
Against the `sound_speed_ms` field already stored in each manifest:

| Run | Gate c (m/s) | `sound_speed_ms` | Delta |
| --- | --- | --- | --- |
| `enh_g96_real` | 1480.9760295 | 1480.9760295 | 0.000e+00 |
| `g64_m1100` | 12.8452326 | 12.8452326 | 0.000e+00 |

### 15 of the 17 gated runs fall below the 10x convention

All 17 use bulk modulus 1.5e5 Pa, giving c = 12.845 m/s. Only the two slowest
velocity-sweep runs clear the convention: v=0.5 at 25.69x and v=1.0 at 12.85x.
The v=1.5 baseline sits at 8.56x and v=3.0 at 4.28x. `enh_g96_real`, which uses
a real-water bulk modulus of 1.9939e9 Pa, clears at 987.32x.

### The GCI gate correctly refuses on the real convergence study

Against the real g48/g64/g96 trio at 1100 kg (displacements 0.350717, 0.658537,
0.268638, confirming the +87.8 percent then -59.2 percent swing recorded in
`CLAUDE.md` item 5), the gate returns False at all three masses. Note **which**
branch fires: the refinement ratio is not constant (r21 = 1.5 from 64 to 96,
r32 = 1.3333 from 48 to 64), so the gate exits there and never reaches its own
non-monotonicity message, which is the more informative finding. Both verdicts
are correct refusals, but the message understates the problem.

The gate's arithmetic is sound. On a synthetic constant-ratio monotone control
(`[25, 50, 100]`, `[0.40, 0.30, 0.25]`) it returns apparent order p = 1.000 and
GCI_fine = 25.0000 percent. The real data genuinely cannot support a band.

### No manifest is traceable

Across 29 manifests: `vehicle_mass`, `grid_density`, `mesh_sha256`,
`solver_git_sha` and `canitford_git_commit` are absent from all 29;
`bulk_modulus` is absent from 3. The first two are partly a naming mismatch,
the runs store `mass_kg` and `n_grid`, but the mesh hash and both git SHAs are
genuinely absent and no run can currently be tied to the code that made it.

## DEFECT: `gate_floor_restitution` passes for the wrong reason

The prompt that commissioned these gates predicted this gate would FAIL against
the real `sim_standing.py`. **It passes, and the pass is a false positive.**
Do not treat open item 31 as resolved by this gate.

The regex is `add_plane\([^)]*restitution\s*=\s*([0-9.]+)`. The `[^)]*` cannot
cross a closing parenthesis, so it cannot reach past a parenthesised tuple
argument. The two `add_plane` calls in `renders/yaris_render_s1/sim_standing.py`:

- **line 140, the FLOOR:**
  `s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction, restitution=0.05)`
  The regex dies on the `)` of `(0, 0, floor)` and never sees `restitution`.
- **line 144, a WALL:**
  `s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)`
  No tuple, so the regex matches here.

The gate therefore reports `floor restitution ['0.05'] confirms floor_friction
registers as rigid contact` on the strength of a **wall** whose friction is
0.0, having never read the floor. It would still return True if the floor plane
were deleted outright, so long as one wall kept a nonzero restitution.

**The underlying physics question is separately settled, by direct source read
rather than by this gate.** The floor plane does carry `restitution=0.05`
(`sim_standing.py:141`), and `mpm_solver_warp.py:1915` gates on
`if restitution != 0.0:` before appending the plane to `rigid_surface_colliders`.
So `floor_friction=0.55` does register as rigid contact. Item 31's substantive
concern is answered; the gate that was supposed to answer it cannot.

Fixing the regex to distinguish floor from wall is deliberately NOT done here,
because the prompt specified the gate module's content exactly. It should be
the next change to this file.

## Severity policy

`params_check.py` splits the gates into blocking and non-blocking on purpose.
The commit gate exits 2 on any nonzero return, so a standing known-open finding
made blocking would wedge every commit in the repo and get worked around rather
than read.

**Blocking**, because they detect a regression from a known-good state:
`gate_inertia_not_read_by_solver`, `gate_hull_volume` on source literals,
`gate_mass_declared`, `gate_floor_restitution`.

**Non-blocking**, because they report conditions that are true today and are
already recorded in `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`:
`gate_sound_speed_cfl`, `gate_resolution_convergence_gci`,
`gate_manifest_completeness`, and `gate_hull_volume` against the realized
`solid_volume_m3`.

On that last one: `solid_volume_m3` is the solidified particle cloud, so it
carries a grid-dependent voxelization offset, measured live at +0.24 percent
for `g64_m1100` (3.551384 m3) and +2.62 percent for `g48_m1100` (3.635710 m3).
The 0.002 m3 tolerance is far tighter than either. Do not feed `hull_m3` to the
gate instead: that field is the canonical constant echoed back, so it passes
tautologically on all 17 runs and checks nothing.

## Wording caveat carried into the code

`gate_mass_declared` describes `(1100, 1609, 2337)` as the "AR&R class set".
Per `CLAUDE.md` item 10, **1609 and 2337 have no source in `vehicle_params.py`**;
the nearest classes there are `midsize_suv` at 1990.0 and `light_pickup` at
2300.0. That tuple is the set actually run, not a cited vehicle class set. The
message text is wrong and the gate should not be quoted as evidence that the
mass sweep spans cited classes.
