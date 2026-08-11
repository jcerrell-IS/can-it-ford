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

## Coupling architecture, added 2026-08-08

The 17 canonical runs use the material-8 free-rigid path (mass-weighted grid
velocity average, no force accumulator). Hu et al 2018, ACM TOG,
doi:10.1145/3197517.3201293 (Compatible Particle-In-Cell, colored distance
field, two-way rigid coupling) and Pazouki, Jayakumar and Negrut 2016
(point-cloud force coupling) describe real two-way MPM/SPH rigid coupling as
requiring accumulated contact force, not velocity averaging. The SDF collider
path (job 894731, **7.3 to 7.7 percent** vs analytic buoyancy) matches this
architecture and is the validated path. This does not change any of the 17
runs' verdicts. It reclassifies the coupling defect from an unexplained
numerical patch to a documented architecture choice with a literature-backed
alternative for future work.

**CORRECTED ON ENTRY, 2026-08-08.** The text that commissioned this section
gave the SDF error range as "1.6 to 7.7 percent". That is wrong and was not
written in. The on-disk numbers from `c1sdf_894731.out`, transcribed at
`docs/CONTEXT_CENSUS_2026-08-07.md:1043-1053` against
`F_buoy_analytic = 31298.444315169316`, are `err_steady_vs_analytic_pct` of
-7.6682435536478435 (`c1sdf_sdf_g64`) and +7.280446501465449
(`c1sdf_sdf_g96`), so 7.28 to 7.67 percent by magnitude.
`docs/REGIME_LADDER_DISPATCH_2026-08-07.md:22-23` independently states
"within 7.3-7.7% of analytic buoyancy". The stray "1.6" appears to be a
conflation with the **free-rigid** late-window fit of "+1.5% and +0.7-0.8% of
analytic buoyant acceleration at g64/g96"
(`REGIME_LADDER_DISPATCH_2026-08-07.md:20-21`), which is a different
measurement on the path being criticised, not the validated one. Do not merge
the two ranges.

The material-8 identity is verified live against the pinned solver, not taken
on the citation's word: `kernels/mpm_utils.py:1366` is commented
"Rigid body kernels (material == 8)", `:1090` reads
`elif mat == 7 or mat == 8:  # stationary / rigid, no deformation`, and
`kernels/mpm_solver_warp.py:853` selects the body's particles with
`np.where((mat_np == 8) & (rid_np == b))`.

Carry the caveat with the claim: `REGIME_LADDER_DISPATCH_2026-08-07.md:28-33`
records that the SDF result does **not** clear the 17 published verdicts, for
three reasons, different restitution (the 17 runs use 0.05 on floor and walls,
C1 used 0.0 everywhere), 2-grid-cell depth resolution, and self-consistency
not being validation.

## Watertightness, added 2026-08-08

Kramer, Terheiden and Wieprecht 2016, doi:10.1016/J.IJDRR.2016.04.003, and
Azhar, Bui and Pauwels 2026, doi:10.1111/jfr3.70181, independently confirm
watertightness assumptions materially shift flotation depth. Cite alongside
the solidify_watertight fix, not as a standalone caveat.

**Overlap and tension, flagged on entry.** Neither citation is new to the
project. `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:228` already
records the Kramer 2016 prototype finding that model-scale watertight vehicles
float too shallow, and `CLAUDE.md:367` already carries Azhar 2026 for a
different claim (unsteady flow raising drag 40 to 50 percent), without the DOI.
What is new here is the two DOIs and the pairing.

More importantly, the instruction to cite these "alongside the solidify_watertight
fix" runs into register **E2** at line 183: FloodScene `vehicle.py:162` samples
the mesh down to 60,000 surface points before solidifying, so the source mesh's
watertightness **does not survive that step**. The measured fill_ratio result
stands, but watertightness does not propagate through the pipeline. Pairing a
watertightness citation with the solidify fix therefore risks implying a
property the pipeline does not preserve. Resolve E2 before this pairing goes
into the paper.

## Class-specific geometry, added 2026-08-08

Smith, Modra and Felder 2019; Martinez-Gomariz et al 2017; Arrighi et al 2015
jointly establish buoyancy, drag/lift lever arms, and sliding/float/roll
thresholds depend on displaced volume, underbody shape, wheelbase, track and
CoM, not mass alone. Allen et al 2003 SAE 2003-01-0966 gives a citable
regression method for provisional CoM/inertia by class, explicitly flagged
in that paper as provisional, not validation.

**Partial overlap, flagged on entry.** Smith, Modra and Felder and Arrighi et
al 2015 are both already in the register, at lines 226, 189 and 270, in
adjacent contexts (how buoyancy was historically inferred from displaced
volume, the three real Yaris masses, and buoyancy reducing the normal force in
`F_F = mu(W - B - L)`). Martinez-Gomariz et al 2017 and Allen et al 2003 are
new, as is the framing that the thresholds depend on geometry rather than mass
alone. That framing is the load-bearing part; the two already-cited references
are not independent support for it.

This limitation bites directly on `gate_mass_declared`, which keys entirely on
mass. See the wording caveat above: two of the three masses in the sweep are
unsourced, and the geometry that this section says actually governs the
thresholds is not gated at all.

## Output sensitivity, added 2026-08-08

`gate_output_sensitivity` (Song et al 2026, doi:10.48550/arXiv.2605.09360,
PDE-grounded intent verification) closes the case where a parameter is changed,
the run completes, and the output is byte-identical, meaning the output never
depended on that input in the first place.

This gate is added but **not yet called from `params_check.py`**, because it
needs a baseline and a perturbed value from two runs and `params_check.py` is a
static check over source and stored manifests. It is the natural harness for
the open item at `CLAUDE.md` item 15: set `failure_modes.py:14` from 9.80665 to
9.81, re-run `analysis/classify_failure_modes.py`, and confirm the verdicts are
byte-identical. Note the polarity carefully before using it there. Item 15 wants
the verdicts to be unchanged, which this gate reports as a FAILURE by design,
since an unchanged output is exactly the condition it flags. That is the correct
reading for a sensitivity probe and the wrong reading for a regression check.
Do not wire it to item 15 without inverting the interpretation in the caller.

## Tacit defaults and hidden assumptions, added 2026-08-11

Both citations below were carried in from the dispatch that commissioned this
section and have NOT been checked against a primary record. The blanket
CITATION STATUS at the top of this file applies to them unchanged.

JutulGPT (Lie et al, arXiv:2603.00214) frames the failure mode in which a
modelling choice is never made explicitly by anyone, but is resolved tacitly by
whatever the simulator happens to default to, and is therefore invisible to the
assumption log because it was never written down as a decision. That is the
shape of the inertia, CG and SSF defect recorded at `CLAUDE.md` August 4 audit
item 4: `inertia_kg_m2`, `cg_height_m` and `ssf` are tabulated in
`vehicle_params.py` and never reach the solver, so the tensor actually in force
is whatever the solidified particle cloud implies. Nobody chose the
cloud-derived tensor. It arrived as a default. The project's own resolution of
item 4, that the default is the better value and must not be overwritten, does
not weaken the point, because the value was still never logged as an assumption
until an audit went looking for it.

PhyNiKCE (Fan et al, arXiv:2602.11666) frames physical correctness as
constraint satisfaction, a set of conditions a candidate result must jointly
meet, rather than a single fidelity score to be maximised. That is the framing
under which `.claude/checks/physics_gates_literature.py` exists as a project at
all: each gate is one named constraint, checked independently against source
and stored manifests, and a run is not more converged or less converged but
either satisfies a stated condition or does not. It is also why the honest
output of that file is a list of named warnings rather than an aggregate score.
