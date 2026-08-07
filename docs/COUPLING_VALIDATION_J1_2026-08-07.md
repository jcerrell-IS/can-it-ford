# Register J.1: coupling-force validation, method and results

Date: 2026-08-07. Owner: the coupling-validation session.
Status: method fixed and verified; C0 control PASSED on two platforms; C1/C2/C3
submitted to Vista as job `894628`.

This file exists because the docs survey of 2026-08-07 confirmed there is **no
document anywhere in this tree recording a completed coupling-force, buoyancy or
Archimedes validation**. Register J.1 specifies the test, register C13 records
that no such validation exists in the Genesis repository either. Register D5 and
CLAUDE.md item 6 already settle what the gates are and are not; this file does not
revisit that, it supplies the missing check they describe. This is the first such
result in the project.

Deliberately NOT written into `CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`:
another session owned that file at the time of writing (see
`CONCURRENT_SESSION_NOTICE_2026-08-07.md`). Promote from here when ownership is
settled.

## Why the test has this shape

Register A3 is the binding constraint: `rigid_state()` returns exactly
`com`, `v`, `omega`, `R`, and no force, impulse or torque accumulator exists on
the 17-run path. **The coupling force cannot be read. It can only be inferred
from motion**, as `m dv/dt`. Everything below follows from that.

Verified live against `third_party/mpm-engine-544c93dd-solver-core/` at pinned
SHA `544c93dd`. Nothing here is from a skill file or a summary.

| mechanism | source | consequence for the test |
|---|---|---|
| `v_cm_new = rigid_linear_mom / M`, no force term | `kernels/mpm_utils.py:1416-1459` | body velocity is the mass-weighted mean of grid velocity at its own particles |
| momentum gathered by B-spline from `grid_v_out` | `kernels/mpm_utils.py:1370-1412` | coupling is entirely a grid transfer |
| gravity applied per grid node | `kernels/mpm_utils.py:940` | a DRY box must free-fall at exactly -9.81, giving a free control |
| `g = [0,0,-9.81]` hardcoded | `core/solver.py:167-169` | register A2 |
| `F = I` and no stress branch for material 8 | `kernels/mpm_utils.py:1090-1091` | rigid particles deposit mass and momentum, never stress |
| `if restitution != 0.0` gates rigid contact | `kernels/mpm_solver_warp.py:1915` | planes at `restitution=0.0` are invisible to the body, isolating the coupling |
| `pressure = -bulk*(J**-gamma - 1)`, `gamma=1.1` | `kernels/mpm_utils.py:28-54` | confirms `c = sqrt(1.1 K/rho)`, and moves the Archimedes target |

## Scene

Cube, uniform density, free rigid body, still water, nothing else. No Yaris hull,
no `vehicle_params.py`, no inflow, no floor friction. All planes
`friction=0.0, restitution=0.0`, which is a deliberate, stated deviation from
`sim_standing.py:132-137` (which uses `restitution=0.05`, so the 17 runs DO have
floor and wall contact on the vehicle).

Canonical numerics are matched exactly, not approximately: `grid_lim`
9.421742313727737 m, `n_grid` 64 and 96, `dx` 0.1472147236519959 and
0.0981431491013306 m, `h = dx/2` (8 particles per cell), `bulk_modulus` 1.5e5,
`rho_w` 1000, `eta` 1e-3. The substep counts fall out at **11 and 16**, matching
the g64 and g96 rows of `data/all_runs_inventory.csv`. That is a check that the
scene is at canonical numerics rather than merely canonical-looking.

Cube side `L = 10 * dx_canonical = 1.4721472365199588 m`, fixed in metres, so
geometry is invariant across the refinement step and only the grid refines. The
lattice owns exactly `L^3`: `n_side^3 * h^3 == L^3` to 1e-12 at both resolutions
(20^3 and 30^3 particles). A cube, not a sphere, because the draft law
`d = L rho_box / rho_w` is exact and independent of cross-section, and the
displaced volume carries zero geometric error.

## Analytic targets

Incompressible Archimedes, and the EOS-exact correction derived from the
verified `gamma = 1.1` EOS by hydrostatic integration:

```
s(zeta) = (1 + b zeta)^(1/(gamma-1)),   b = (gamma-1) rho_w g / (gamma K)
d_compressible = ((1 + 11 b L rho_box/rho_w)^(1/11) - 1) / b
```

For `rho_box = 600`:

| quantity | value |
|---|---|
| mass | 1914.28 kg |
| volume | 3.190463 m^3 |
| draft, incompressible | 0.883288 m (6.000 dx coarse, 9.000 dx fine) |
| draft, EOS-compressible | 0.860914 m (5.848 dx, 8.772 dx) |
| compressibility shift | **-2.53 %** |
| one particle layer | **8.33 %** of draft coarse, 5.56 % fine |
| C1 `a_ideal = g(rho_w/rho_box - 1)` | 6.5400 m/s^2 |
| C1 `F_buoy = m(a+g)` | 31298.4 N, identically `rho_w V g` |
| added-mass asymptote, Ca approx 0.67 | 3.0898 m/s^2 |
| acoustic transit `L/c` | 0.11461 s = 37.8 substeps coarse, 55.0 fine |

The closed form was checked against an independent Simpson-plus-bisection solve
of the buoyancy integral and agrees to ~1e-13. It is a derivation, not a
transcription.

**Stated in advance: at canonical resolution one particle layer (8.33 % of
draft) is over three times the physical compressibility correction (2.53 %), so
C2 cannot resolve its own EOS correction at g64.** That is a resolution-cost
finding, not an excuse assembled afterwards.

## Results so far

**C0, dry drop. PASSED on both platforms.** The rigid integrator and the
grid-gravity path are correct.

| platform | a measured | error vs -9.81 |
|---|---|---|
| Apple M5, warp 1.16.0 CPU | -9.809986697775976 | +0.00014 % |
| Vista GH200, warp 1.15.0 CUDA | -9.810047354016985 | -0.00048 % |

CPU and CUDA agree to ~6e-6 relative. The residual is float32 reduction ordering.
`rho_box_realized` = 599.9999999999999 against 600 requested, satisfying the
project's coupled-variables rule.

**Cross-platform determinism.** The identical 158-frame settle at 254,171
particles reproduced to all reported digits on both platforms:
`settle frames 158`, `vmax peak 8.1059`, `vmax final 0.6294`,
`draft after settle 0.789370`. Wall clock 364 s on CPU against 5.0 s on the
GH200, about 73x.

**C1, C2, C3: submitted as Vista job `894628`.** Results pending.

## Findings produced by building the test

1. **The cold-start transient is violent and this is structural.** At `t=0`,
   `F = I` everywhere, so `J = 1`, so `pressure = -K(1 - 1) = 0`. There is no
   pressure field, therefore no buoyancy, and a body released at `t=0` free-falls
   at exactly `-g` regardless of density. The water column collapses dam-break
   style before hydrostatic pressure establishes. Measured: `vmax` peaks at
   **8.1059 m/s**, `c/vmax = 1.58`, and it takes **158 frames (5.27 s)** to decay
   to `c/vmax = 20`. For most of that settle the 10x sound-speed criterion is
   violated, worse than the 4.28 minimum register B8 records for the canonical
   runs. **Consequence: C1 cannot be measured from a cold start**, and any future
   scene that starts water at rest inherits this transient.
2. **The 10x criterion is a settle-phase problem too, not only a sweep problem.**
   Register B8 covers the canonical runs' velocity sweep. This adds that the
   initialization transient alone drives the ratio to 1.58.
3. **Volume bookkeeping against an assumed tank area is not safe.** A rind of
   water up to ~1.04 dx thick sits outside the wall planes (6.8 % of particles
   beyond a 0.5 dx tolerance), so the true footprint exceeds the nominal
   `A_tank` by roughly 7 %, comparable to the 8.33 % measurement floor. The draft
   estimator was changed to a per-column median of `vol()/bin_area` over free
   columns, which uses only measured quantities and is immune to the rind. The
   assumed-area result is retained as a labelled cross-check.
4. **The P2G edge guard bounds the usable resolution from below.** With the wall
   inset fixed in metres so geometry stays invariant under refinement, the guard
   (`1.5 dx` low, `LIM - 2.5 dx` high) fails at `n_grid = 32`. 48, 64 and 96 pass.
5. **A false-pass mode exists for C2 and must be controlled.** A coupling broken
   in the "frozen" direction, where the body simply holds whatever grid velocity
   it sits in, would pass a C2 started at the analytic draft. C2 therefore runs
   from two initial drafts, the analytic value and analytic + 2 dx, and requires
   both to converge. Without that control C2 is not a valid test.
6. **C1's headline must be the earliest window.** On the first substeps after
   release the body has not moved, so the fluid has not been forced to accelerate
   around it and there is no added-mass reaction; the measured acceleration
   should sit near `a_ideal`. Added mass then develops over `L/c`, about 38
   substeps coarse and 55 fine, relaxing toward roughly `a_ideal/(1 + Ca rho_w/rho_box)`.
   Reporting a late-window acceleration against `a_ideal` would show an apparent
   50 % error that is real physics, not a solver defect.

## Repo defects found while surveying, not yet in the register

Verified live 2026-08-07. These are recorded here because the register was owned
by another session; promote them when ownership is settled.

- **Register item 13 undercounts DRIFT_THRESHOLD.** 17 declaration sites under
  the four listed names, not 16. The likely missed one is
  `docs/session_notes/archive/mu_sweep_recovered_from_staging.py:60`. Plus
  `simulation/can_it_ford_mu_sweep.py.DO_NOT_RUN:60`, which a `.py` filter misses.
- **A fifth, undocumented name exists: `L2_DRIFT_M = 0.05`, 7 further sites**
  across `analysis/make_poster_figures*.py` and three `deliverables/` copies.
- **`simulation/failure_modes.py` has three `0.05` literals, not two.** `:46`
  `slide_m` and `:48` `float_m` are metres; **`:47` `slide_speed_ms` is m/s**. A
  naive find-and-replace would silently convert a speed into a distance.
- **`scripts/check_claims.py:154` asserts five `9.81` sites; there are 7.** The
  two `9.80665` sites are correct. Unifying on 9.81 is the consistent direction
  since the solver hardcodes it.
- **`grep -r <pattern> .` silently skips `renders/` in this sandbox.** Any prior
  audit using recursive-grep-from-dot has undercounted that subtree. Use
  `find ... -print0 | xargs -0 grep`.
- **`renders/yaris_render_s1/failure_modes_result.json` is untracked by git**, in
  addition to the defects register D6h already records.
- The register's claim that `four_rung_ladder*.md:136` still miscite that file is
  **stale**; commit `841d666` repointed both, and register line 147 already says so.
- **`check_claims.py` rule C13 has no agreement exemption.** It fired three times
  on this file for sentences that RESTATE its authority correctly, not contradict
  it, because it substring-matches the claim text. Verified live against
  `CLAUDE.md:150` and register `D5` at `:126`; both agree with what was written.
  The hook's own message says to leave text that quotes a claim in order to
  correct or retire it, but agreeing restatements hit the same matcher. Worth an
  exemption for lines that also cite the authority. Flagged for the rule's owner
  rather than edited, since `check_claims.py` belongs to another session.

## Reproduce

```
sbatch scripts/run_coupling_validation.sbatch
```

Analytic layer, no GPU required, exercises the real module with stubbed
device imports: see the verifier described in the commit message. Asserts the
lattice identity, the canonical substep counts 11 and 16, geometry invariance
across the refinement step, and both draft formulas against an independent
numerical solve.
