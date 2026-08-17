# R6: the N=1 problem measured, and Job B's decay explained

2026-08-18. Branch `claude/can-it-ford-round-5-87a6d6`, whose HEAD `1a868f3` is the J15/J16
register commit. Everything here bears directly on those two items.

**Not folded into the register on purpose.** The register merge (side A on
`claude/add-ci-checks`, side B on `claude/r5-safekeeping`) has not landed. Editing the
register here would create a third side of a two-side merge. Fold these findings in AFTER
that merge, not before.

---

## 0. What is new, in one paragraph

Job 917797 was recorded as "A1, 23 of 23 rc=0". It was not A1. `prestage_jobs.sh`'s `job_a()`
deliberately FUSES A1 and A2 into one script, because A1 is about 45 seconds of compute
against 80 to 120 seconds of warpmpm import startup. The 23 runs are 3 brake arms plus 10 + 10
repeats. **A2 had therefore already run and had never been analysed.** The Round-6 handoff
lists A2 as queued and ready; it was queued, ready, and done. Analysing it costs zero SU and
answers the N=1 problem directly.

---

## 1. The 17 canonical runs are single draws from a genuinely non-deterministic process

**MEASURED.** All 20 repeat trajectories are bit-different. Twenty distinct sha256 over
`metrics.csv`, ten per configuration, at fixed configuration with no seed change (there is no
seed flag; settle is constructor-only at the canonical 8).

Provenance, so these are comparable to the published runs: `jobA.out` stamps the driver at
`4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9`, which is the canonical
published driver sha, and the hull is
`can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`.

Divergence onset is **frame 0**, and the first column to differ is `yaw_deg`. Position holds
to frame 1 and differs from frame 2. So the runs differ in ORIENTATION at the first recorded
frame, before any fluid has done anything.

### 1a. `determinism_identical` measures something adjacent to its own name

**MEASURED, then confirmed at primary source.** `determinism_identical` is `true` in all 20
`summary.json` files while every one of the 20 trajectories differs.

```
renders/yaris_render_s1/sim_standing.py:389
renders/yaris_render_s1/_incoming/sim_standing.py:243
    det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
```

It is a particle count and a grid limit, and nothing else. A different random surface sample of
the same watertight hull preserves both while placing every particle differently, which is
exactly what produces the frame-0 `yaw_deg` difference. The flag therefore returns `true` BY
CONSTRUCTION for runs whose trajectories diverge immediately.

This is the eighth instance of the round's core pattern, and the worst-placed one: unlike the
other seven it is stamped into the summary of every published run.

**Verified, not assumed.** `renders/yaris_render_s1/gates_results_all_runs.json` holds 20
records, the 17 gated plus the 3 dry_start, exactly as CLAUDE.md item 8 says. **17 of 17 gated
runs carry `determinism_identical: true`.** The 3 dry_start records carry the literal
`"ABSENT"`. So the flag reads true on every published run, and none of those runs has ever had
a repeat to compare against.

**Distinguish carefully from what was already known.** The handoff already recorded that this
field is a load-time hull check and not a trajectory check, and named the same line number.
That part is not new. What is new is that nobody had measured whether the trajectories actually
diverge, so nobody knew the flag is not merely weak but FALSE IN PRACTICE for all 17 published
runs.

---

## 2. The verdicts are reproducible. The margins are not.

Run with the project's own published classifier, `simulation/failure_modes.py` at `ssf = 1.42`
(vehicle_params `compact_sedan`) and `G = 9.81`, and with `margin_frames` re-implemented exactly
as `a6a707c` defines it: the longest run of consecutive frames holding the joint SLIDE
condition, minus the 3 the classifier requires.

| | published, N=1 | measured, N=10 |
|---|---|---|
| `g96_m2337` verdict | SLIDE | **SLIDE 10 of 10** |
| `g96_m2337` joint frames | 4 | 3 or 4, **3 in two draws** |
| `g96_m2337` margin | **1** | **1 in eight draws, 0 in two** |
| `v0p5` verdict | STUCK | **STUCK 10 of 10** |
| `v0p5` joint frames | 0 | 0 in all ten |
| `v0p5` margin | -3 | -3 in all ten, no spread |

**Both boundary verdicts are reproducible at 10 of 10.** This is the first repeat-based
evidence the project has for any verdict, and the STUCK control has zero spread.

**J15's "ONE-FRAME margin" is a single-draw value and is not stable.** Across ten draws the
margin spans 0 to 1, and in two of ten the joint condition holds for exactly 3 frames, which is
exactly `sustain_frames`. Those two draws sit precisely on the flip threshold with zero margin.

Restate the claim as: **zero to one frame from STUCK, N=10, two of ten at zero.** That is a
stronger statement of J15's own finding, not a weaker one. The heaviest vehicle at the finest
grid is sometimes exactly at the boundary rather than one frame off it.

### 2a. What this does NOT overturn

J15's refinement trend survives. The `m2337` series collapses 11 to 10 to 4 across g48/g64/g96,
a drop of 7 frames, against a measured run-to-run spread of 1 frame at the one point where
repeats exist. A 7-frame collapse is far outside a 1-frame noise band, so the trend is not a
noise artifact.

**Tag this honestly: transferring the g96 spread to the g48 and g64 points is an ASSUMPTION.**
There are no repeats at those two grids. It is a falsifiable test that came out confirming, and
it is written up the same way it would have been if it had overturned.

### 2b. J16, partially addressed

J16 records that six margins are not independently checkable, because job 866887 overwrote the
g48/g96 directories on 2026-07-26, and that the most fragile verdict in the set is one of the
six. These repeats do not recover the original run and cannot. They do give, for the first time,
an independent N=10 measurement of the margin AT that configuration. The original single draw
stays unrecoverable; the quantity it was measuring is now known with an error bar.

---

## 3. The noise floor does not transfer between statistics, demonstrated on one dataset

Same 20 runs, same frames, four statistics:

| statistic | spread across 10 repeats |
|---|---|
| `margin_frames` | 0 to 1 frame, and IDENTICAL at the 91 and 250 frame windows |
| `dmag` at frame 91 | 3.84 % of mean (`v0p5`), 2.38 % (`g96_m2337`) |
| `dmag` at frame 250 | 9.56 % (`v0p5`), 4.48 % (`g96_m2337`) |
| `leaked_particle_frames` | 489,722 to 490,044, a range of 0.066 % |

The 250-frame window inflates the `dmag` spread by about 2.5x on `v0p5` through wall-reflection
contamination (first reflection predicted at frame 112.3, observed at 112, 125, 126), while
leaving `margin_frames` completely unchanged, because the joint SLIDE condition fires early.

**Operationally: `margin_frames` may be quoted off the 250-frame runs. `dmag` may not.** Always
name the statistic beside any spread, and name the frame window beside any magnitude.

---

## 4. Job B, job 918043: the decay is the tank draining, and the pre-registration proved it

Submitted by `sbatch` on partition `gh`, NOT idev. COMPLETED, 00:06:45, ExitCode 0:0, rc=0,
`ALLDONE`, 200 frames. Roughly half of 917909's 13:55, from the SDF cache fix in `d9ff5f7`.

The run used the measured-surface build staged at `$WORK/d4_scene/sphere_heave.py`,
sha256 `f74223122ae868c1a1e95c4e061eac55e649ccbdf47da49782460b9833e10118`, byte-identical to the
local file at branch HEAD. The criterion was committed at `ae08cce` BEFORE any run had ever
produced the field, so it cannot have been tuned to this result.

**Nominal grade: NOT GRADEABLE**, correctly, and for the right reason now that `68731f7` fixed
the tuple-parsing bug that previously reported PASS at -9.806 percent. Late-window mean
53.5913 N against the 69.2180 N target.

### 4a. The mechanism fired

Under the project's own `blocking.stationarity`, late window frames 100 to 199:

| series | halves_stationary | trend_stationary | slope, blocked sigma |
|---|---|---|---|
| `fz_N` | False | False | 8.52 |
| `fz_over_analytic_nominal` | False | False | 8.52 |
| **`fz_over_analytic_measured`** | **True** | **True** | **0.15** |

The 8.52 reproduces `grade_job_b.py`'s own reported figure exactly, which is the cross-check
that the harness here is the same one the grader uses.

Normalising the reaction by the closed form at the surface that actually exists converts a
decisively non-stationary series into a stationary one, 8.52 sigma to 0.15. **That settles the
question 917909 could not answer: the decay is the tank draining, not the coupling failing.**

All sigmas here are blocked, not OLS. It matters in both directions: blocking DEFLATES the
`fz_N` figure (a naive OLS gives 23.28) and it also deflates the measured ratio's (naive 0.24
to blocked 0.15). The stationarity conclusion is robust either way, since both readings sit far
below any threshold, but quote the blocked ones.

### 4b. The level is wrong, on the opposite side

Stationary ratio **1.6308 ± 0.0082**, blocked SE, converged, plateau at block size 8 with 12
blocks, inflation over naive 1.548, tau_int 2.396 frames. That is **+63.1 percent**, outside the
pre-registered 25 percent FAIL band. The nominal ratio was 0.774, i.e. -22.6 percent, outside it
in the other direction. The true reaction sits BETWEEN the two targets and neither is right.

The estimator is not arithmetically at fault. Recomputing the spherical cap independently from
`surface_z_measured_m`, with `ref_radius_m` 0.15 and sphere centre fixed at z = 0.575, reproduces
the reported `submerged_cap_m3` to six decimals at every frame checked.

### 4c. The surface fall, measured rather than inferred

Design waterline is z = 0.575 m (`floor_m` 0.075 plus `depth_m` 0.5), and the sphere centre is
fixed at exactly that height, half submerged, `ref_density_kg_m3` 499.11 against water 998.2.

| frame | surface z, m | drop from design | `fz_N` | measured ratio |
|---|---|---|---|---|
| 0 | 0.561534 | 1.347 cm | -0.0666 | -0.0011 |
| 50 | 0.539878 | 3.512 cm | 51.5764 | 1.1373 |
| 100 | 0.526719 | 4.828 cm | 64.6597 | 1.7498 |
| 150 | 0.519832 | 5.517 cm | 51.9991 | 1.5876 |
| 199 | 0.514445 | **6.055 cm** | 47.8245 | 1.6168 |

Monotone, and still falling at frame 199: `blocking.stationarity` on `surface_z_measured_m`
over the late window gives `trend_stationary=False` at **19.98 sigma**. (A naive OLS slope test
gives 58 sigma on the same series; use the blocked figure, because OLS assumes independent
residuals that an autocorrelated series does not have.) The handoff's 3.09 cm was back-derived
from a force deficit on a shorter run; the direct measurement is roughly double it and has not
converged. **This confirms the handoff's call that more frames alone will not fix it.**

### 4d. The volume budget: compression is bounded, the fall is not

The tank's plan area is not in the config, so derive it. `n_water` 598,505 particles at spacing
`h_m` 0.009375 gives a particle volume of h^3 = 8.2397e-7 m3 and a water volume of
**0.493153 m3**. Adding the 8,292 carved particles (0.006832 m3, against the sphere's analytic
half-volume of 0.007069, a 3.4 percent discretisation shortfall as expected) and dividing by
`depth_m` 0.5 gives a plan area of **0.999971 m2**, which closes on exactly 1.0 m2 to 0.003
percent. So the tank is 1.0 x 1.0 m of water inside a 1.2 m grid. DERIVED, not read.

Compression, computed independently from the sound speed rather than taken from the docstring:
bulk modulus K = rho c^2 = 998.2 x 12.8568^2 = 165,000 Pa; mean hydrostatic pressure over the
column rho g d / 2 = 2448.1 Pa; strain **1.4837 percent**, so the column shortens **0.7418 cm**.
`sphere_heave.py`'s own docstring says 1.497 percent and 0.74 cm. Independent agreement, from a
different starting point.

| surface drop | source | volume lost | compression explains | UNEXPLAINED |
|---|---|---|---|---|
| 3.090 cm | 917909, back-derived from a force deficit | 6.27 % of the water | 24.0 % | 76.0 % |
| **6.055 cm** | **918043, measured directly** | **12.28 % of the water** | **12.3 %** | **87.7 %** |

The 24.0 percent reproduces the handoff's 23.9 percent, which is real corroboration because it
was reached from the sound speed rather than copied.

**The decisive point is the trend, not the level.** Compression is a ONE-TIME 0.7418 cm: once
the column reaches hydrostatic equilibrium it contributes nothing further. The surface has
fallen 6.055 cm and is still falling at 19.98 sigma at the last frame. So every additional
centimetre beyond the first 0.74 is 100 percent unexplained, and the unexplained fraction has
grown from 76.0 to 87.7 percent purely because the run got longer. **The mechanism is ongoing
and it is not compression.** Roughly 0.0531 m3 is unaccounted for, about 64,500 particles' worth
of volume.

### 4e. One hypothesis tested and largely refuted, by reading the code

The obvious unifying explanation for both anomalies, the +63 percent ratio and the missing
volume, is that the surface estimator samples where the sphere depresses the surface, which
would under-report the waterline and inflate the ratio while inventing a volume loss.

**`sphere_heave.py:605-629` already guards against exactly that.** It excludes every particle
within `2.0 * self.radius` of the sphere axis, on the stated grounds that the annulus carries
the meniscus and any splash and is a local deformation rather than the tank's free surface, and
it takes the 99th percentile rather than the max so a single ejected particle cannot define a
surface. The simple version of the hypothesis is therefore refuted at source, and the mystery
deepens rather than resolving. Name the mechanism, then check it fires; this one does not.

What survives as candidates are the two named in `f5e2f30`: particles leaving through the floor
or wall bands, and the jittered seed lattice settling denser than it was created. Both are
volume questions, not mass questions, since the particle count is fixed at load.

**The instrumentation that would settle it in one run:** record per frame the count of particles
below the floor plane and outside the wall bands, and the mean local packing density. If the
count is flat and the density rises, it is settling; if the count grows, it is leakage. Neither
is currently recorded, and both are cheap.

### 4f. The caveat that must travel with this

The measured ratio is flat because numerator and denominator are falling together in proportion.
That confirms the decay MECHANISM. It does NOT mean the system reached equilibrium, and the run
is a transient throughout, so **+63 percent is not a validation number and must never be quoted
as one.**

What Job B bought is the conversion of "we cannot distinguish a broken coupling from a draining
tank" into "it is the draining tank, measured", plus a sharper question: where does 6 cm of water
column go, when the particle count is fixed at load and no particle is created or destroyed
during a run, and compression accounts for well under a quarter of it.

---

## 5. Closed, with evidence

**CLAUDE.md item 15 and Round-6 handoff section 4 item 5 are CLOSED, not started.**

Commit `e495b56`, 2026-08-12, set `simulation/failure_modes.py:14` to 9.81, regenerated
`data/failure_modes_by_run_classified.csv` and `data/failure_modes_by_run.json` via
`analysis/classify_failure_modes.py`, and recorded the outcome: verdicts unchanged at 16 SLIDE
and 1 STUCK, all 17 run-to-mode pairs and all triggered flags byte-identical, exactly 3 of 33
columns moved, all direct functions of G. That is precisely the closure procedure item 15
demanded, including the instruction not to close it by assertion.

`git merge-base --is-ancestor e495b56 origin/main` returns true, so it is published.

On Vista, `can-it-ford-track1-6dof` (the tree holding the published driver) and `d5_seedpolicy`
both carry `G = 9.81`. The only remaining 9.80665 copies are under `can-it-ford-OLD-pre-purge`
and `home_archive`, which safekeeping already decided not to re-import as history. The handoff
conflated a stale pre-purge copy with an open task.

---

## 6. What to do next

1. **Restate J15's margin** as zero to one frame, N=10, two of ten at zero. J15's headline ask,
   run the canonical set at g128, is unchanged and is still the highest-value open item.
2. **Fix or retire `determinism_identical`.** It cannot be left reading `true` on every published
   run while every trajectory differs. Either rename it to what it measures, hull load
   reproducibility, or make it compare trajectories.
3. **Job B's open question is where the water goes, and section 4d sharpens it.** Compression is
   a bounded one-time 0.7418 cm against a 6.055 cm fall that is still going at 19.98 sigma, so
   the mechanism is ongoing and cannot be compression. Add the two per-frame counters named in
   4e (particles below the floor and outside the wall bands, plus mean packing density) and one
   short run settles leakage against settling. Candidates named in `f5e2f30`: particles
   leaving through the floor or wall bands, or the jittered seed lattice settling denser than it
   was created. The particle count is fixed at load, so this is a volume question, not a mass one.
4. **The grader short-circuits before the companion.** `grade_job_b.py` refuses on the nominal
   stationarity test and never reports `fz_over_analytic_measured`, although `ae08cce` specifies
   it be reported ALONGSIDE the nominal and that the tool say so out loud when they differ. The
   measured series is present in the output JSON for all 200 frames. Report both, then refuse.

## 7. Reproducing everything above

Every number in this document is regenerated by one script, which prints its enumeration
rather than a bare total:

```
/opt/homebrew/bin/uv run --with numpy python3 analysis/r6_repeat_stats.py \
    --jobA <extracted d4_jobA dir> --jobB <sphere_fixed_g64.json>
```

`blocking.py` lives in `simulation/r5_physics/` on `claude/r5-physics` and is NOT on every
branch, including this one. The script locates it across sibling worktrees and fails with a
message naming the branch rather than an ImportError. Override with `--blocking-dir`.

`--windows` defaults to 91, 111 and 250 and the output flags any window at or past the first
observed wall reflection at frame 112.

### The data


Metrics for all 23 runs of job 917797 were pulled as a 914 KB tarball, `metrics.csv` plus
`summary.json` only, leaving the 8.2 GB of `rollout.npz` on Vista:

```
ssh vista "cd /work/11603/jcerrell0629/vista && tar czf d4_jobA_light.tgz \
  d4_jobA/*/metrics.csv d4_jobA/*/summary.json d4_jobA/jobA.out d4_jobA/jobA.err d4_jobA/run_jobA.sh"
scp vista:/work/11603/jcerrell0629/vista/d4_jobA_light.tgz .
```

Job B's result is `/work/11603/jcerrell0629/vista/d4_jobB_918043/sphere_fixed_g64.json`, 122 KB,
200 rows carrying `fz_over_analytic_measured`, `surface_z_measured_m`, `surface_drop_m`,
`submerged_cap_m3` and `analytic_buoyancy_at_measured_surface_N`.

There is no numpy on any system python on this Mac. Use `/opt/homebrew/bin/uv`, for example
`uv run --with numpy python3 <script>`.

One incidental shell trap, because it cost real time: in zsh, `while read -r a b path` clobbers
`$PATH`, since `path` is tied to it. Every external command then fails with "command not found"
while builtins keep working, which reads as a broken tool rather than a broken variable name.
