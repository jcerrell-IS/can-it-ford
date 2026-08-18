# HANDOFF, CAN IT FORD, ROUND 7

Paste this whole file as the first message of a fresh Claude Code session in
`/Users/josie/can-it-ford`. It assumes you have read nothing.

Every number below was read live from a command output, a file, or a commit body during
Round 6 on 2026-08-18. Where something is inferred or unverified it says so. **Nothing in
this file is a summary of a summary.**

---

## 0. THE ONE RESULT THAT CHANGES THE PROJECT

**At g160 the heaviest vehicle's verdict flips from SLIDE to STUCK, in 5 of 5 repeats.**

```
job 918350   g160_m2337   5 repeats   90 frames   canonical driver
verdicts     STUCK x5     joint frames [0,0,0,0,0]     margin [-3,-3,-3,-3,-3]
dx 0.05889 m   water_layers 10   n_water 906806   all 5 metrics.csv bit-distinct
```

| grid | water layers | verdict (N=5) | margin |
|---|---|---|---|
| g48 | 3 | SLIDE 5/5 | 8 |
| g64 | 4 | SLIDE 5/5 | 6 |
| g96 | 6 | SLIDE 5/5 | 0 to 1 |
| g128 | 8 | SLIDE 5/5 | 0 |
| **g160** | **10** | **STUCK 5/5** | **-3** |

g160 is the first grid reaching ~10 particle layers across the flow depth, which is the only
depth-based convention in the literature (Reis et al. 2021,
`10.1016/j.engstruct.2021.113280`, verified matched). **The prediction was written into
918350's own sbatch header BEFORE the run.**

**So the published 16 SLIDE / 1 STUCK headline does not survive refinement to the resolution
the literature asks for**, at least for m2337, which J15 already flagged as the most fragile
case.

**AND IT IS CONFOUNDED. Read section 2 before repeating any of the above.**

---

## 1. VERIFY BEFORE YOU TRUST. Run these first.

```bash
git -C /Users/josie/can-it-ford log --oneline -5 claude/can-it-ford-round-5-87a6d6
```
```bash
bash /Users/josie/can-it-ford/scripts/tacc.sh --status
```
```bash
for w in r5-research r5-exposure r5-safekeeping r5-physics; do printf "%-16s %s\n" "$w" "$(git -C /Users/josie/can-it-ford/.claude/worktrees/$w log --oneline -1)"; done
```

R6's deliverable is `docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md` on branch
`claude/can-it-ford-round-5-87a6d6` (pushed to origin). Two runnable scripts regenerate every
number in it: `analysis/r6_repeat_stats.py`, `analysis/r6_a1_caveats.py`, plus
`analysis/r6_hull_clearance.py`. **All three were verified by running them, not by inspection.**

---

## 2. THE CONFOUND. Nothing about resolution is safe until this is closed.

**The refinement ladder is a sequence of DIFFERENT TANKS, not one tank at several resolutions.**

`sim_standing.py:81` sets the domain independently of the grid:
```
lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
```
and 2.2 x 4.2826 = 9.4217, exactly the observed `grid_lim`, so the long-axis term binds.
But `:86` and `:100` set the offsets IN CELLS:
```
floor = 3.0 * dx        wall = 4.0 * dx
```
so the water span is `lim - 8*dx` and it GROWS under refinement. Measured from run summaries:

| grid | span | plan area | water volume |
|---|---|---|---|
| g48 | 7.8515 m | 61.645 m2 | 17.199 m3 |
| g128 | 8.8329 m | 78.020 m2 | 22.478 m3 |
| g160 | 8.9506 m | | |
| change g48 to g128 | +12.5 % | +26.6 % | **+30.7 %** |

`span = lim*(1 - 8/n)` is exact and independent of `lim`, so those percentages are structural.

**The tank is LARGEST exactly where the verdict flips.** Tank growth lowers the blockage ratio
and pushes toward STUCK. Resolution pushes toward STUCK. They are co-directional and no run in
existence separates them.

**Until the control below runs, say "the verdict flips under a refinement that also enlarges
the tank", NEVER "the verdict flips under refinement".**

**The floor offset is NOT part of the confound.** `floor = 3.0*dx` moves collider, water base
and vehicle placement together and never enters the horizontal footprint. Only the walls
confound. Getting this wrong sends someone chasing a vertical effect that does not exist.

### THE CONTROL, and it is the highest-priority experiment in the project

Pin the interior span in METRES and re-run the ladder. **Do not edit `sim_standing.py`**: its
sha256 `4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9` stamps every
published run. Precedent is D5, which injected settle and seed by **wrapper subclass**.

Pin by choosing `lim` per grid, `lim_n = S / (1 - 8/n)`, reachable by presenting a vehicle
whose `extent[1]` is `lim_n / 2.2`. `extent` is read at `:81`, `:236`, `:239`, `:240` and
written to summary at `:337`, so the override propagates consistently AND is self-documenting
in the output, which is what you want.

At S = 7.85145 m (the g48 span):

| n | lim | dx | vs current dx at same n |
|---|---|---|---|
| 48 | 9.4217 | 0.19629 | unchanged |
| 64 | 8.9731 | 0.14020 | finer |
| 96 | 8.5652 | 0.08922 | finer |
| 128 | 8.3749 | 0.06543 | finer |
| 160 | 8.2647 | 0.05165 | finer |
| 192 | 8.1928 | 0.04267 | finer |

**Every dx is FINER at the same n because the domain shrinks, so the control is CHEAPER than
the confounded experiment it replaces.** Run 5 repeats per grid on m2337 at 90 frames.

- **Success:** the flip survives at the pinned span. The resolution finding is real and the
  headline verdict is an under-resolution artifact.
- **Failure:** the flip weakens or moves. Then tank growth was doing some or all of the work.
- **Write it up identically either way.**

---

## 3. WHAT ELSE IS MEASURED. All from tonight, all reproducible.

### 3a. The 17 canonical runs are single draws from a non-deterministic process
All 20 A2 repeats bit-different, at every grid. Divergence by the first recorded frame.
**Row 0 is NOT the initial condition:** `sim_standing.py:235-237` runs 8 settle frames first,
which is 128 solver substeps at g96 and 88 at v0p5. The divergence is located INSIDE the
settle phase and nothing yet says whether seeding or the solve caused it.

### 3b. `determinism_identical` is false in practice on all 17 published runs
`sim_standing.py:389`: `det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)`.
A particle count and a grid limit. It reads `true` on 17 of 17 gated runs in
`gates_results_all_runs.json` while every trajectory differs. **Five writer files** assign it
and **seven poster-figure generators print "all runs deterministic" from it.** Rename to
`hull_load_identical`; do NOT delete it, because hull loading genuinely IS bit-identical and
that is what localises the nondeterminism to the solve.

### 3c. `sustain_frames = 3` is unsourced and gates the verdicts in both directions
`failure_modes.py:52`. At 30 fps that is 0.1 seconds. Sweeping it against the same runs:

| grid | sf=3 | sf=4 | sf=5 |
|---|---|---|---|
| g48, g64 | 5 SLIDE | 5 SLIDE | 5 SLIDE |
| g96 | 5 SLIDE | 2S/3K | 0S/5K |
| g128 | 5 SLIDE | **0S/5K** | 0S/5K |
| g160 | 0S/5K | 0S/5K | 0S/5K |

The fragility is entirely a fine-grid phenomenon and **it VANISHES at g160**, where 0 joint
frames give STUCK at any threshold. Register D6f also records the same constant as "the only
thing keeping TOPPLE from firing on all 13".

**The literature does not support persistence at all.** Verified against primary sources:
every published criterion is an instantaneous force inequality or a single observed motion
event. Bonham & Hattersley 1967 and Gordon & Stone 1973 restrained their models "by fine
threads both vertically and laterally", so no motion time series existed and a duration was
NOT MEASURABLE IN PRINCIPLE. Martinez-Gomariz 2017 (UPCommons postprint, primary): instability
is "if the model vehicle moved". **Recommendation: remove persistence from the verdict, or
report gate-pass FREQUENCY over repeats instead of pass/fail.**

### 3d. The underbody clearance is 177 mm and no reachable grid resolves it
Measured by `analysis/r6_hull_clearance.py` from 327,212 hull vertices, per-column minima
between the axles (a global z-min returns the tyre contact patch). 5th pct 177.4 mm, min
160.5, median 201.9. Cells across it: **0.90** at g48, 1.21, 1.81, 2.41, 3.01, 3.61 at g192.
**At g48, dx is LARGER than the ground clearance.** `dp <= D/10` wants 17.7 mm, about g810 on
this domain, unreachable. This is the review's "resolve the smallest FORCE-BEARING feature"
criterion and the project has never applied it.

### 3e. Job B FAILS its pre-registered criterion
Job 918240, graded on `fz_over_analytic_measured`, the accessor `sphere_heave.py:669-670`
designates: **+50.06 percent**, FAIL at every window from last-20 to last-200, stationary at
0.15 sigma so window-robust. `MANIFEST:214`: "Any FAIL stops the ladder."

`grade_job_b.py` returns NOT GRADEABLE by rejecting the series for non-stationarity, which is
**the exact ground manifest criterion 5 calls "expected, not disqualifying"**. Do not repeat
NOT GRADEABLE as the verdict. Note the symmetry: the first grader wrongly PASSED at -9.806
percent, the fixed grader now wrongly REFUSES.

The nominal accessor cannot yield a verdict at all: -29.11 FAIL / -22.58 PARTIAL / -9.67 PASS
across the same 200 frames, because criterion 3 names no window. **That is a second defect and
it must be fixed before Job C is graded on the same template.**

### 3f. The water leaks through the floor, and it is not the domain
`water_budget()` in `sphere_heave.py`, job 918240: by the last frame **4.505 percent of water
sits BELOW the floor plane** with the lowest particle 2.4 cm underneath, and 2.410 percent
outside the wall bands, counts still GROWING while occupied volume is flat after frame 50. So
leakage, not compaction.

Domain control, job 918251 at lim 2.2 / n_grid 117 (dx held to 0.28 percent, 4x plan area):

| | lim 1.2 | lim 2.2 | ratio | predicted |
|---|---|---|---|---|
| below floor | 4.505 % | 3.796 % | 1.19 | 1.00 if area-distributed |
| outside walls | 2.410 % | 1.231 % | **1.96** | **2.00** if perimeter-driven |
| `fz_over_analytic_measured` | 1.4790 | 1.4654 | **1.01** | |

The wall leak halves as perimeter/area predicts. The floor leak does not. **Quadrupling the
domain moves the graded ratio by 1 percent, so Job B's FAIL is NOT a bounded-domain artifact.**

### 3g. The floor BC is a grid-node velocity projection, NOT a repulsive layer
`Dirichlet_collider`, `mpm_solver_warp.py:1955`: `if dotproduct < 0.0:` then
`v -= min(normal_component,0)*n`. So the DualSPHysics mDBC framing does NOT transfer; there is
no repulsive layer to under-resolve. Diagnosed in `daf64f7` on `claude/r5-physics`.

**Mechanism (hypothesis matching three measured signatures, UNREVIEWED):** the B-spline
half-width is 1.5 dx, so a near-wall particle has support on nodes both sides; the nodes below
carry no particle mass, so P2G leaves them mass-deficient and the particle sees a density
deficit underneath with a pressure gradient pointing INTO the boundary. That predicts
penetration rather than compaction, an area-distributed floor leak, and a perimeter-scaled
wall leak. **All three match.** It makes the wall and floor leaks ONE mechanism with two
geometries.

**The right remedy is GHOST PARTICLES** (missing mass, not missing constraint). mDBC does not
apply: the half-space below is already fully constrained. **And it is blocked**: `core/solver.py`
exposes no pin/freeze/set_particle_*/ghost API, material 7 (stationary) is not reachable
through `set_material_range`, and the only freezing path makes a free material-8 body that
falls under gravity.

**Job 918450 is the partial fix, already running.** A COPY of the engine at
`$WORK/mpm-engine-bcfix-src` with exactly one line changed, `dotproduct < 0.0` to `<= 0.0`,
verified by `diff` to be one line. The pinned engine is untouched so all provenance holds.
This addresses defect 2 only (the node lying exactly on the plane is unconstrained, and
FLOOR = 0.075 is exactly 4dx at g64, so the highest constrained node sits a full cell low),
worth about 1.8 cm of the ~6 cm fall. **Prediction stated in advance in the run script:
`n_below_floor` should FALL but not vanish; if it is unchanged the hypothesis is refuted; if
it vanishes entirely the mass-deficiency story was wrong and that is more interesting.**

---

## 4. WHAT WAS REFUTED. Do not reinstate any of these.

1. **"Job B is NOT GRADEABLE."** It FAILS. See 3e.
2. **"The margin collapse is a clean resolution result."** Confounded. See 2.
3. **"The ground-clearance mechanism explains the collapse."** Co-directional with the
   confound; the data cannot separate them. I asserted this prematurely.
4. **"mDBC / multi-layer boundaries are the fix."** The BC is not repulsive. See 3g.
5. **"Cite Steffen 2008 for the direction of the collapse."** The abstract is
   direction-agnostic AND **the engine already implements Steffen's own remedy**, the
   quadratic B-spline basis, at `mpm_utils.py:837`, `:958`, `:1393`. Citing his pathology as
   the mechanism for code that applies his fix is self-undermining. Still citable for "MPM can
   lose convergence under refinement at fixed PPC", not for the sign.
6. **"The 10-particles rule has no source."** It does: Reis et al. 2021,
   `10.1016/j.engstruct.2021.113280`, verified matched. But it is ~10 per WAVE HEIGHT for a
   tsunami bore on an elevated structure, calibrated on free-surface elevation with force
   inferred. Cite as a borrowed cross-regime convention, never as a criterion you met.
7. **"There is no force-convergence criterion, full stop."** Say "not found in the
   peer-reviewed flood-vehicle literature". The corpus report that supplies the negative
   explicitly forbids the flat phrasing.
8. **`g96_m2337` as a headline cell.** It is one of six runs whose frozen values do not
   reproduce after the 2026-07-26 job-866887 overwrite (frozen 1.80047 vs live 1.74225).
9. **CLAUDE.md L-4 as written.** Coarse over-prediction is "a documented tendency with clear
   exceptions, not a consistently validated law", with a recorded inversion where over-fine
   resolution broke the wave early and UNDER-predicted. Conservatism survives for SAFETY, not
   for the scientific claim.
10. **CLAUDE.md item 15 as open.** CLOSED by `e495b56`, on origin/main, with the re-run and
    byte-identical comparison both recorded. One residual 9.80665 site remains at
    `analysis/viability_dashboard_scaffold.py:11`, so `scripts/check_claims.py` Rule C6, which
    asserts "TWO sites", is now stale and prescribes completed work.

---

## 5. THE REAL-WORLD EXTENSION. This is where the project should go.

From `/Users/josie/Claude/reu/compass_artifact_wf-045982be-1f56-5c57-9f47-d78a05d7e156_text_markdown.md`.
SECONDARY (an AI research report), so verify any DOI before citing.

**The citable negative finding: no peer-reviewed paper or design guide outputs a graded safe
crossing speed as a function of BOTH depth and flow velocity.** The whole vehicle-stability
field is threshold-based.

- Closest existing thing is **depth-only**: Pregnolato et al. 2017,
  `10.1016/j.trd.2017.06.020`, open access CC BY,
  `v(w) = 0.0009w^2 - 0.5529w + 86.9448` (w mm, v km/h, R^2 0.95). Driver-control advisory,
  not stability, and it declares 30 cm impassable so it collapses to a binary exactly where
  stability matters.
- **Two literatures must not be conflated**: vehicle STABILITY (sweep-away, D x V, usually a
  STATIONARY vehicle) versus driver VISIBILITY/BRAKING/AQUAPLANING (speed-dependent but about
  tire-road traction and mm-scale films).
- **The frontier stops short.** Al-Qadami 2022 full-scale (`10.1007/s11069-021-04949-6`) found
  drag "increased significantly with the increment of flow velocity, Froude number, and vehicle
  speed", the clearest evidence that vehicle speed raises destabilising load. Output is forces
  and a ~0.38-0.40 m critical depth, D x V near 0.36-0.39 m2/s. Not a speed function.
- **AV work inherits the binary framing**, including the 2026 arXiv "physically viable world
  models" line (MPM plus Gaussian splats, Kumar's group), which outputs feasible/infeasible and
  explicitly flags depth, current velocity and vehicle mass as unresolved. **No conformal or ML
  paper outputs a calibrated safe-speed surface for flood fording.**

**Why this project is placed to fill it, and this is the reframe that matters:** the field
publishes single points on a boundary. This project publishes DISTRIBUTIONS. N=5 to N=10
ensembles, non-deterministic runs, a threshold proven tunable, a margin that does not converge.
Those are not embarrassments to disclose, **they are exactly the argument for replacing a
binary line with a calibrated probability of instability**, which is what an AV planner or a
driver advisory actually needs.

Construction: hard boundary from the stability curves (Xia, Shu, Martinez-Gomariz,
Milanesi-Pilotti); penalise speed near it using Al-Qadami's drag-vs-vehicle-speed finding;
add Ong-Fwa aquaplaning as an independent bound at shallow depth. **Treat floodwater velocity
and vehicle speed relative to water as SEPARATE terms** — the literature conflates or omits the
second and separating them is itself a contribution.

**Honest constraint: none of this survives contact with reality until the solver is validated.
Job B fails by +50 percent with 4.5 percent of the water leaking through the floor. A
calibrated probability surface on an unvalidated solver is WORSE than a binary threshold,
because it looks authoritative. Fix the boundary first.**

---

## 6. INLET / OUTLET INSTEAD OF REFLECTING WALLS

The current tank is closed on four slip walls plus a floor, and the first wall reflection
arrives at frame 112.3 predicted, 112/125/126 observed, which truncates every run.

**The translation already exists.** `simulation/openchannel_bc.py` on `claude/add-ci-checks`
translates Zhao et al. 2019 (Computers and Fluids 179, 27-33,
`10.1016/j.compfluid.2018.10.007`, Anura3D) add/remove inflow-outflow into an engine that
cannot add or remove a particle: **one-in-one-out recycling inside a fixed pool.** A recycled
particle keeps its (y, z) deliberately, because for a fluid the solver overwrites F every
substep with `J^(1/3) I` (`mpm_utils.py:1086-1089`), so the only carried state is J, the
hydrostatic head is a function of z alone, and re-inserting at the same depth re-inserts at
the same head. F has no setter, so this is the only consistent route.

**Measured, commit `be1b138`, g64, 90 frames, water only:**

| bc | grade | free-surface slope | drained bins | stationary |
|---|---|---|---|---|
| closed | 0 deg | +0.09268 +/- 0.00161 | 2 of 12 | yes |
| closed | 3 deg | +0.16946 +/- 0.00224 | 4 of 12 | no |
| recycle | 0 deg | -0.00284 +/- 0.00029 | 0 of 12 | yes |
| recycle | 3 deg | +0.00596 +/- 0.00086 | 0 of 12 | no |

**At ZERO grade the closed box manufactures +0.0927 m/m of free-surface slope.** A 3 degree
road is tan(3 deg) = 0.0524 m/m, so the artifact is 1.77x the entire signal. Recycling leaves
33x less and never drains a bin.

**Do this: port the recycling BC to the VEHICLE scene.** It is the single change that most
improves physical realism, it is already written and measured for the channel, and it removes
the reflection window that currently caps every run at ~91 usable frames.

`periodic_x` is documented "Incompatible with CDF colliders and rigid bodies" (`solver.py:93`),
which the gated vehicle is, so periodic is NOT the route. Recycling is.

---

## 7. RENDERS. What is real, what is stale, what is inverted.

Verified in R6 against live source. Two of four alleged defects are real:

- **REAL: the vehicle has no material model.** `analysis/render_multigeom_rollout.py:208` was
  one line, `sh = clip(n @ LIGHT,0,1)*0.6 + 0.4`. **FIXED in commit `109220b`**: it now takes
  optional `view_dir`, `sky`, `sun` and adds HDRI ambient via `sample_env`, Lambert plus sky,
  Schlick clearcoat Fresnel at F0 0.05, an HDRI mirror term and a GGX lobe at roughness 0.25,
  every block lifted from the water path in the same file. **It degrades EXACTLY to the old
  one-liner when no HDRI is passed**, verified by `np.allclose`, so no existing figure changed.
- **REAL: the asphalt PBR set is tracked and referenced by no live code.**
  `assets/Asphalt015_1K-JPG_Color.jpg`, `_NormalGL.jpg`, `_Roughness.jpg`, a complete ambientCG
  CC0 set. Five separate zeros across the main tree and all sibling worktrees.
- **STALE: the water-invisibility defect.** The `urban_road_flood` optics preset was fixed on
  2026-08-15 in commit `7d43b97`; the default is `moderate_flood`. Residue remains: the
  preset's own source note still calls 13000 mg/L "the defensible default".
- **INVERTED: the caption is 23.5 percent of frame height, not 70.** 0.710 is the PLOT band.
  The real layout problem is that the 3D hero is only 33.6 percent of the frame. Add a
  `--hero` flag rendering `gs[:, 0]` alone and drop the caption loop at `:522-526`.
- **`pysplashsurf` aarch64 exclusion is FALSE.** Wheels exist for every release since 0.11.0.0,
  so the SplashSurf to Blender chain is reproducible on the laptop today.

**Hard constraint on any asphalt work:** `_incoming/sim_standing.py:132-137` has ONE floor
plane at friction 0.55 and four slip walls at 0.0. There is no friction field and no per-cell
mu. **Any road texture is pixels only and the legend must say so**, copying the precedent at
`render_multigeom_shaded.py:335` which already begins "WATER SHADING IS DISPLAY ONLY".

**Trap, confirmed live:** a divergent copy of the optics module sits at
`/Users/josie/Downloads/d/flood_water_optics.py`, 4030 bytes, md5
`65a26cacd8165437c9774d1c0a9b18a3`, with ZERO occurrences of `urban_road_flood`,
`SEDIMENT_CSTAR_M2_PER_G` or `LINEAR_REGIME_MAX_SSC_MG_L`. Anyone told to "recover the file"
who grabs that one gets a module without the preset machinery every optics number depends on.
Recover only with
`git -C /Users/josie/can-it-ford show claude/fork-render-3class:analysis/flood_water_optics.py`
and confirm md5 `216e4005b2d90294bcb6d57b9341feef`.

---

## 8. INFRASTRUCTURE. Exact state, verified.

### Overleaf, WORKING for git, one step from working for MCP
- Remote is `https://git@git.overleaf.com/6a5958d10484feadf65a934e`. **The username must be the
  literal `git` with the TOKEN AS PASSWORD.** With no username in the URL, git asks for two
  things and pasting the token at the `Username:` prompt fails with the server's own 401 hint.
- Keychain now holds `acct=git, srvr=git.overleaf.com`; `git fetch overleaf` returns rc=0.
- **`~/.config/overleaf-mcp/token` is still 0 BYTES. That is the only thing blocking the MCP.**
  Write it with `cat > ~/.config/overleaf-mcp/token` then Ctrl-D, so it never enters shell
  history. Claude Desktop is already wired to the same file.
- `mcp__overleaf__list_projects` works WITHOUT a token because it only reads local config, so
  **it is not a valid test.** `status_summary` clones, so it is.
- **NEVER `git push overleaf main`.** `git merge-base overleaf/main origin/main` returns
  NOTHING; the histories share no ancestor. Forced, it destroys all 29 Overleaf commits
  including web-editor edits that exist nowhere else. The Overleaf tree is FLAT
  (`conference_101719_1.tex`, figures as bare filenames) while the repo nests them.
- A repo hook forbids editing `paper/` without explicit go-ahead. It is correct; `paper/`
  mirrors Overleaf.

### The paper
The live Overleaf bib has **15 entries and zero MPM method papers**, confirmed by
`git show overleaf/main:can_it_ford_references_IEEE.bib`. Four entries are staged in
`docs/overleaf_staging/mpm_foundations_additions.bib`, three DOI-verified title-against-record
(`sulsky1994particle`, `steffen2008quadrature`, `hu2018mlsmpm`), the fourth
(`bardenhagen2004gimp`) explicitly recorded as NOT verifiable with its page-range end omitted
because no source attests a last page. **No key collides with the 15.** Pushing the repo bib
instead would break **17** `\cite` commands, not 5, because `shand2011arr` alone is cited 11
times.

### TACC
- **Vista 617 SU, LS6 9539 SU**, both expiring 2026-09-30. Measured rate ~20 SU/node-hour, so
  617 SU is roughly 30 node-hours.
- **Use `gh`, never `gh-dev` for scripted work.** `gh` has 576 nodes and `qgh` allows
  MaxJobsPU=20 / MaxSubmitPU=40 / 96 nodes. `gh-dev` has 20 nodes and an idev holds a per-user
  slot there, which is what left job 918235 PD.
- **idev discipline.** On 2026-08-17 idev `917886` ran 2:00:06 to TIMEOUT while every science
  job combined took ~36 minutes. Interactive has historically burned 98.5-99.1 percent of this
  project's Vista node-hours. **Never infer idleness from `squeue`** — I called 917886 idle
  twice and it was running the g128 canonical set.
- **Every output path MUST carry `${SLURM_JOB_ID}`.** `run_s2.sh` still writes FIXED paths
  `g${GRID}_m${MASS}`, which is the exact hazard that destroyed six margins on 2026-07-26 and
  made register J16's runs permanently unverifiable. Use `r6_rep.sh` as the pattern instead.
- PYTHONPATH for every job:
  `/work/11603/jcerrell0629/vista/mpm-engine/src:/work/11603/jcerrell0629/vista/.venv/lib/python3.12/site-packages`.
  Neither Vista venv has trimesh; the shared venv does, trimesh 4.12.2. **Do not install into
  it, other sessions are live on it.**
- Engine roots: `$WORK/mpm-engine/src` is the RUNTIME one (627367e). `can-it-ford/mpm-engine/src`
  is STALE and lacks `solidify_watertight`. `$WORK/mpm-engine-bcfix-src` is the R6 one-line
  boundary variant.

### Weights & Biases, Hugging Face, Gradio
**All three are UNVERIFIED in this round. Check before building on any of them.**
- W&B: memory records the key ending `iNbz` as DEAD (401) with the live one ending `ipS9`, and
  `~/.netrc` plus `.zshrc:62` held the dead one until 2026-08-17. **Verify with a real API call
  before wiring runs**, and prefer `WANDB_MODE=offline` for GPU jobs so a bad key cannot fail a
  run that already cost SU.
- Hugging Face: memory records a Space sync where a stale secret AND a never-created Space both
  contributed, and that `hub-sync` mirrors all 407 MB including licence-unresolved NCAC models.
  **Push `hf_space/` only.** The Space should stay private until the README claims are corrected.
- Gradio: nothing exists yet. The obvious first artifact is a **depth x velocity traversability
  explorer** that shows the AR&R / NWS thresholds, the Pregnolato depth-only curve, and this
  project's ensemble as a PROBABILITY rather than a line. That is the section 5 contribution
  made tangible, and it is the right demo for an AV or public-safety audience.

### Credentials, still open and still only yours
**12 credentials, ZERO rotated.** Rows 1 and 2 are GitHub fine-grained PATs with WRITE on a
PUBLIC repo, row 2 exported at `~/.zshrc:750`. The rotation list is at line 123 of the
**1196-line** copy on `claude/credential-exposure-2026-08-13-DO-NOT-PUSH`; the main-tree copy
is 118 lines and has no list. `~/.claude/backups/` gains token-shaped material about once a
minute, so deletion cannot win, only revocation.

---

## 9. HOW TO DEPLOY DAUGHTER SESSIONS

**The rule that matters most: ONE session per worktree.** In R6 I edited `sphere_heave.py`
inside another session's live worktree and they committed my uncommitted work inside their own
commit `7c9e0af` without either of us knowing. That is the same failure as `0797b08`/`3470ff9`
on 2026-08-07.

Create a worktree per task:
```bash
git -C /Users/josie/can-it-ford worktree add .claude/worktrees/<name> -b claude/<name>
```

**tmux dispatch trap, cost real time in R6:** `send-keys` with a long prompt does NOT submit.
The text becomes a `[Pasted text #N]` block and the trailing Enter is consumed. **Send Enter a
SECOND time as a separate call**, then verify with `capture-pane` that the input box is empty
and the status line shows "esc to interrupt".

Task-to-directory map, all four currently live:

| task | worktree / dir | why there |
|---|---|---|
| pinned-span control (section 2) | own worktree | writes a wrapper + runs GPU |
| boundary fix, ghost particles (3g) | `r5-physics` | owns `sphere_heave.py` |
| force-convergence curve (section 10) | `r5-research` | read-only over run outputs |
| threshold provenance (3c) | `Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13` | corpus is not the repo |
| renders (section 7) | own worktree | touches `analysis/render_*` |
| paper / bib (section 8) | own worktree | `paper/` is hook-guarded |

**Corpus notes for any research session:** `mcp__canford-corpus__corpus_search` is LITERAL
substring, not semantic, so multi-word natural-language queries return ZERO and that reads as
absence. Use single distinctive terms. One root
(`/Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13`) is **PARTIAL/TCC-DENIED, 308
of 387 files readable**, so a zero there is a broken probe. **Never use
`corpus_cited_status`**: it calls itself the novelty guard and returns "cited" for papers that
appear only in `docs/` notes and never in the paper. It is a check that cannot fail.

---

## 10. THE WORK LIST, ranked

1. **Pinned-span ladder control.** Section 2. Decides whether the g160 flip is physics or
   geometry. Cheaper than what it replaces. **Nothing else about resolution can be published
   until this lands.**
2. **Collect job 918450**, the boundary-fix A/B, and grade it against the prediction written in
   its own run script.
3. **Collect job 918351 (g192)** and extend the ladder table.
4. **Port the recycling inflow-outflow BC to the vehicle scene.** Section 6. Biggest single
   gain in physical realism, already written and measured for the channel.
5. **Force-vs-resolution curve.** The corpus review's recommendation 3 says explicitly that a
   multi-resolution force-convergence curve for a vehicle "is currently rare and would
   materially improve the literature", and recommendation 6 says it would REPLACE the field's
   rules of thumb. **The project has the dataset and reports verdicts instead of forces.** This
   is the most likely publishable contribution.
6. **Rename `determinism_identical`** at five writers and fix seven poster captions.
7. **Remove persistence from the verdict**, or report gate-pass frequency.
8. **Renders**: wire the asphalt PBR set with a DISPLAY-ONLY legend, add `--hero`.
9. **The AV traversability surface.** Section 5. The long game.
10. **Register merge.** Both sides are in git history so neither can vanish. Merge the CURRENT
    tip, re-derived at the moment of merging, NEVER `790d999`, which is a clean zero-conflict
    merge that silently drops 126 lines. Verify with `git rev-parse HEAD^2` equalling the
    pinned SHA, not with a line count.

---

## 11. A SELF-AUDITING LOOP, honestly scoped

You can automate the CHECKING. You cannot automate the JUDGEMENT, and R6 is the evidence:
five of five headlines were overturned by adversarial passes, two of them mine, and every one
needed a human-legible argument rather than a threshold.

**What to automate, all of which already exists or is one script away:**
- `scripts/check_claims.py`, `.claude/checks/params_check.py`, `count_claims_check.py`,
  `register_integrity.py`. Run them on every commit via the existing hooks. **Note Rule C6 is
  currently STALE** (asserts "9.80665 appears at TWO sites"; there is one, at
  `analysis/viability_dashboard_scaffold.py:11`) and prescribes work `e495b56` completed.
- A nightly job that re-runs `analysis/r6_repeat_stats.py`, `r6_a1_caveats.py` and
  `r6_hull_clearance.py` and diffs against the committed numbers. Any drift is a real event.
- A queue watcher that collects finished TACC jobs and files their outputs, so results never
  sit uncollected as A2 did for a full round.

**What must stay human:** any claim entering the paper, any push, any credential action, any
edit to the pinned engine or `sim_standing.py`, and the Job B ladder decision.

**Use `/loop` for genuinely periodic work** (collect jobs, re-run checks) and schedule it with
a long interval, 1200 s or more, since harness-tracked work notifies on completion and polling
is waste. Use a Workflow for fan-out with an adversarial verify stage. **The pattern that
worked all round: find, then attack, then only publish what survives.** Roughly a quarter to a
third of findings were refuted at every stage, which is the base rate to expect.

---

## 12. HOW TO BEHAVE

- **A check must measure the thing that would hurt you, not a proxy.** Eight instances found
  and counting. The newest: `grade_job_b.py` refuses on a ground its own manifest calls
  "expected, not disqualifying".
- **Compute from the tree, print the enumeration, check the sum.** Every hand-derived figure on
  this project has been wrong at least once.
- **A secondary source is not a primary one.** The corpus is largely AI-generated research
  reports. "Report X says paper Y reports N" is not "paper Y reports N".
- **Verify a DOI title against the resolved record**, never just that the link resolves. A real
  DOI with an invented title is the dominant fabrication pattern.
- **Name the mechanism that would refute you, then show it does not fire.** An argument that
  reaches the right answer without engaging the refuting mechanism is not verified.
- **Never infer idleness from a queue listing.**
- **Relay a commit SHA, never a summary.**
- Stage explicit paths, commit path-limited, never bulk-stage. Never push without a per-branch
  go-ahead. **The repo is PUBLIC.** No em-dashes anywhere.
