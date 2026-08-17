# D4: what survives, what was withdrawn, and what is still unreviewed

2026-08-17. Branch `claude/r5-physics`, **35 commits, unpushed and held**. Index current
as of `0449091`.

This branch's documents carry correction boxes stacked on correction boxes, because **five**
adversarial review passes found real errors in almost every headline I produced. That is
the process working, but it has made the branch hard to read. **This file is the index: it
states what a reader may rely on, what is retracted, and what has not been checked.**

Rule used throughout: a claim is listed as surviving only if it was checked by a route
independent of the one that produced it, or is true by construction from source.

---

## 1. Survives, CORRECTED 2026-08-17 by a fifth review that attacked this list

**A fifth pass targeted the survivors rather than the withdrawals, on the reasoning that
the dead claims cannot mislead anyone and these are what propagate. It broke seven of
ten.** All are corrected in place below; none is deleted, because the direction of most
survived and only the wording or the warrant failed.

Every row is **WARPMPM** (`renders/yaris_render_s1/_incoming/sim_standing.py`, solver
`third_party/mpm-engine-544c93dd-solver-core`). No Genesis path appears anywhere in this
branch's evidence chain. The engine tag was missing from every row and is added here.

**Citation hazard affecting five earlier references, found by the same pass:** my scripts
and docs cite line numbers in the **tracked top-level** `sim_standing.py`, but the 17 runs
were produced by `_incoming/sim_standing.py`, which register D4a makes canonical and which
has a different md5. Line numbers below are the `_incoming/` copy.

| claim, as corrected | what changed | basis |
|---|---|---|
| **The canonical scene has no outflow BC.** `n_water` fixed at `:123`, floor plus four slip walls `:132-137`, `add_domain_walls()` `:137`, `_sustain_inflow` `:190-198` writes velocity onto EXISTING particles, and `:264` prints `SCENARIO=STANDING_WATER_SUSTAINED_INFLOW`. | **unchanged, could not be broken** | read live |
| **The water is still spinning down at the end of every run.** Bulk mean speed falls median **-66.3%** from frame 8 to 89, range -87.4 to -41.3, **0 of 17 gain**. | **"never reaches a steady state" WITHDRAWN.** That restates the stationarity claim I already retired as "17/17 undecidable at this length"; a monotone decay is consistent with asymptotic approach. Magnitude is window-specific: -73.0% at settle 0, -34.4% at settle 45. **Always state the window.** | `spin_down.py` |
| **A near-vehicle shell falls HARDER than the bulk**, median -78.5%, 17/17 negative, still falling frames 30-89. And the clamped inflow band empties: **7 particles left at v3p0**, against 1846 at v0p5. | **NEW, from the review.** Kills the obvious alternative that a steady near-vehicle shear hides under a decaying bulk mean, and independently corroborates the no-recycling row from rollout data rather than source. | review-measured |
| **`particle_selection` is writable at runtime (`mpm_solver_warp.py:1679`) and gates six kernels, TWO of them P2G**, so a deactivated particle stops depositing mass to the grid while remaining in the array, frozen. **A grid-transfer sink, not a deletion.** | **"gates P2G at six sites" was still wrong here** after I corrected it elsewhere, and **"the register's own B7 wording" is a MIS-ATTRIBUTION**: B7 is about the pressure field. The real source is my own `OPTION_A_SESSION1_FINDINGS.md` F-6, which tabulates four sites correctly. | read live |
| **There is no grid-level pressure array and no Poisson solve, so a Dirichlet pressure BC is not expressible.** Per-particle pressure IS computed inside the EOS (`mpm_utils.py:22,43,68`) and is exported (`:1794`, `:1799`). | **"no pressure field, 0 across 3,181 lines" WITHDRAWN as worded.** 3,181 is ONE file of four; `mpm_utils.py` has 19 hits including the EOS. My own source file `inflow_outflow.py:18-19` states the qualifier and my survivors row compressed it away. **The control variable is readable but not settable.** | read live |
| **No run holds its labelled depth.** At a spanwise vehicle-free station the deviation is **+8.8% to +30.0%**; at an upstream vehicle-free station it is **-58.2% to +28.8%**. | **"+13% to +28%" WITHDRAWN: it has no derivation in any committed script**, which is the exact provenance defect that made me write `spin_down.py`. **The sign is station-dependent**; only the mislabelling itself is robust. | review-measured |
| **P-2 is overwhelmingly bounding-box void, not passthrough.** Under the driver's own carve test, void is **78.8 to 98.5%**, median in-hull share 6.26%. | Direction unthreatened. But the figures are **convention-dependent**: a centred rather than floor-anchored cell moves the median in-hull share to **9.79%** (+56% relative) and void to 74.9-98.6%. Quote the convention. "79" was 78.84 rounded up. | `p2_decompose.py` |
| **Kramer 2021 Table 1** and the corrected constants: `rho_w` 998.2, `m` 7.056 kg, `g` 9.82, buoyancy **69.2180 N**. | unchanged | read from the PDF |
| **The STUCK mechanism.** Speed gate shuts frame 8, drift gate opens frame 37, **zero overlapping frames**. | **unchanged, not re-attacked and previously confirmed digit-for-digit** | measured |
| **Brake state cannot flip a SLIDE verdict.** Worst run needs T3 + delta >= ssf = 1.42; T3 = 0.721 and the buoyancy-corrected friction ceiling is **0.215 g**, giving 0.935 against 1.42. | **"on a bound: 0.578 g" WITHDRAWN.** It is not a bound (removing friction changes the trajectory, so it is a linearised ceteris-paribus ESTIMATE) and `mu*(1+e)` assumed **zero buoyancy**. Corrected, the margin is 52% headroom rather than 9.4%, so **the conclusion strengthens**. **Carry the caveat that `vehicle_params.py:150` says `ssf: 1.42 # estimate ... CONFIRM before use`.** | re-derived by review |

## 2. Withdrawn. Do not cite these.

| withdrawn claim | why |
|---|---|
| "41% of series hit the transient cap **is the finding**" | a pure ramp with no transient hits the cap at n=91 AND n=400; 10 of 14 hits were `dmag`, a cumulative series that should never have been blocked |
| "14/17 never reach a stationary window" | the rule's own false-positive rate was **40.4%**; corrected to **17/17 undecidable at this length** |
| "converged 34/34" as reassurance | plateau block size 1-4 against tau up to 4.5; on the module's own criterion **0 of 17** qualify, so every blocked SE is a lower bound |
| "the BC was validated 3/3 then the level did not hold" | **the event never happened.** `inflow_outflow.py:2-5`: "NOT run against the GPU solver. No gated run uses it." The string exists only in my dispatch prompt |
| "total water volume is fixed by construction" | `core/solver.py:589-591` returns `_vol0 * J`. **Mass** is fixed, not volume |
| "the public cuboid wrapper does not exist" | `add_box` **is** it, and I enumerated it while denying it |
| "the velocity sweep varies depth 2.6x" then "1.81x" | my fixed station is not vehicle-free; occupancy correlates with the reading at **-0.951**. Vehicle-free controls give **1.13x to 1.37x**, non-monotone |
| "depth explains 15% of the P-2 trend, so item 7 survives" | slope CI **[-5.95, +17.93]**, p=0.164, includes zero; LOO collapses to 3.5%; and the lever was **structurally invalid** because `lim` is depth-independent so the fraction is analytically invariant to uniform depth |
| "`local_depth_footprint` reads high in proportion to drift" | the bias is **negative in 12 of 17** and changes sign; r = -0.019 without high-drift runs |
| "the 0.140 g rounding is something real" | it is 54x inside Kramer's own +/-1 g uncertainty |
| "group velocity is the right reflection speed" | Kramer section 3.5 uses **phase** celerity and says why; my domain bought 1.06 periods, not 2.12 |

## 3. Reviewed and WITHDRAWN, fourth pass

All three of the items previously listed here as "unreviewed" were withdrawn on review:

- **"Report the in-hull fraction instead of P-2"** is refuted four ways: 56-86% of its rise
  is cells the hull did not occupy at frame 0 (hull moving into water, not water entering
  hull); 84-100% of it sits in a one-cell skin at h = 0.0736 m, at or below the stencil
  width; it correlates better with drift (0.916) than velocity (0.782); and it is
  **non-monotone across g48/g64/g96 at two of three masses**, the same defect item 5
  forbids quoting for displacement.
- **"The null exceeds the gate limit in 17/17"** is withdrawn. My null was the loosest of
  three: undisturbed-lattice gives **14/17**, empirical tiled gives **7/17**, and my
  denominator co-varies with the treatment. A change that moves 14/17 to 17/17 is not a
  sharpening.
- **"Most runs read below their own null"** inverts under an empirical null: median
  **+0.32 pp, 9/17 above**, six runs at the 100th percentile of all vehicle-free placements.

Also withdrawn: **"~9 pp of near-constant void"**. Void rises +55% and carries **57%** of
the P-2 trend, so the dilution framing was backwards.

**Method error worth recording:** I declined to reconstruct the vehicle pose, citing a
0.0613 m residual as too coarse, while calling it "constant across frames" in the same
sentence. A constant residual is a rigid translation; removing it leaves 6e-7 m of scatter
and reproduces the driver's own value to 0.00e+00 in 17/17. My stated reason refuted itself.

## 3b. WITHDRAWN by my own check, and replaced by something stranger

I put "5-21% of water sits below the floor plane, an ungated leakage channel" on the board
after a reviewer raised it. **I then derived it myself and it is wrong.**

`_project_water` (`sim_standing.py:250-267`) clamps water to `floor - 0.25*dx` **by design**
and counts anything beyond as `leaked`. So "below the floor plane" is mostly the designed
tolerance band. Measured at frame 89, N=17:

| | median | range |
|---|---|---|
| below the floor plane | 10.73% | 0.00 to 19.47% |
| **below the clamp band** (`floor - dx/4`) | **0.38%** | 0.00 to 2.18% |

The minimum z sits at **-0.258 dx** below the floor in every g64 run, i.e. essentially
exactly at the clamp limit. **It is the containment working, not a leak**, and the driver
already stores an escape counter (`leaked_particle_frames`, 6,345 to 207,415 across runs).
"Ungated" was wrong too.

**What is real, and I did not expect it: the below-floor population is a g64 phenomenon
only.**

| grid | dx | below floor | min z minus floor, in dx |
|---|---|---|---|
| g48 | 0.1963 | **0.00%** | **+0.113** (above the floor) |
| g64 | 0.1472 | **10.0 to 19.5%** | **-0.258** (at the clamp limit) |
| g96 | 0.0981 | **0.00%** | **+0.031 to +0.047** (above the floor) |

g48 and g96 keep every water particle above the floor. g64 drives 10-19% of it down to the
clamp. Resolution-specific and non-monotone, on **the grid 13 of the 17 canonical runs use**.

**Narrowed by a follow-up check, which changed the framing again.** It is **not** a dynamic
leak that accumulates: it is already **4.8 to 5.8% at recorded frame 0**, jumps to ~15% by
frame 5, then oscillates 8-19%. And recorded frame 0 is **not** initialisation: the 8
settle frames run inside `__init__` before recording begins (`sim_standing.py:235-237`).
The lattice itself cannot place a particle below the floor, since it starts at
`floor + dx/4` and the jitter is only +/-0.1 dx.

**So the water settles into the clamp band during the 8 UNRECORDED settle frames, at g64
and not at g48 or g96.** Mechanism beyond that is unresolved and I am not proposing one.

One consistency check that did pass: the hull rests at exactly 0.0000 m above the floor at
frame 89 on every grid, and `g48_m1100` starts at +0.0418 m and ends at 0.0000, i.e. it
sank during the run. That matches the register's own P-3 note that all three g48 runs show
a negative z rise near -0.05 m. **[unreviewed]**

## 3c. A challenge to L-3 that FAILED, and one precision that came out of it

Following the settle-phase result I checked whether the unrecorded settle invalidates
CLAUDE.md L-3's "realized_depth_m / dx is exactly 2.000" and "water_layers is 4". The
measured free surface at recorded frame 0 came out **5 to 25% below nominal depth**, which
looked like a settling deficit.

**It was my own convention error and the challenge fails.** The lattice is
`arange(floor + 0.5h, floor + depth, h)`, so the top particle **centre** sits `h/2` below
the nominal **surface**. Predicting the top layer centre and comparing:

| | result |
|---|---|
| measured surface within one jitter (+/-0.2h) of the predicted top layer centre | **13/17** |
| the 4 exceptions | all **ABOVE** prediction by 0.0004 to 0.005 m, i.e. a slight rise |
| runs sitting **below** prediction | **0 of 17** |

There is no settling deficit. **L-3 stands as written**: `realized_depth_m = layers * h =
4 * 0.0736 = 0.2944 = exactly 2.000 dx` at g64, by lattice construction, which is what L-3
says.

**The precision that did come out of it, and L-3 does not say this: 4 layers is the g64
value, not a universal one.** Measured layer counts are **g48 = 3, g64 = 4, g96 = 6**, and
the depth sweep gives 3, 5, 6 for the 0.25 / 0.35 / 0.45 runs.

So **the g48 rung carries only 3 particle layers, i.e. 1.5 grid cells** against L-3's
stated 4 layers and 2 cells. L-3 already flags 4 layers as a resolution limitation. **The
g48 runs are thinner than the limitation as stated, and g48 is one of the three rungs in
item 5's grid-convergence study.** Anyone quoting L-3 alongside item 5 should say which
rung they mean.

**CORRECTED 2026-08-17. Both of my verification claims here were wrong, and the counts
were never new.**

**(a) `water_layers` is already column 6 of `data/all_runs_inventory.csv`**, the very file
L-3 cites, reading 3/3/3, 4/4/4, 6/6/6, 3/5/6. And route 1 was not independent:
`_incoming/sim_standing.py:260` computes `layers` with that same `arange` and writes it to
`summary.json`. I re-derived the driver's own stored output and called it a new precision.

**(b) "The two methods agree in 17 of 17" is false.** Counting non-empty h-wide bins
agrees in **3 of 17**; the counts recover only under mode-counting or an unstated
"row population >= 50% of median" filter. **The bin choice was load-bearing and unstated.**

**(c) "jitter is only +/-0.2h so the rows are separable" is false at g64**, and section 3b
of this same document already said so: 4.8% of water sits a full row below the bottom
lattice row at recorded frame 0, inter-row minima are 300-500 against peaks of 2500. I
justified a frame-0 measurement with a property of the unrecorded initial condition that my
own section 3b says does not hold there.

The counts themselves stand:

| grid | layers | **cells = layers*h/dx** |
|---|---|---|
| g48 | 3 | **1.500** |
| g64 | 4 | **2.000** (L-3's stated values) |
| g96 | 6 | 3.000 |
| sweepD 0.25 / 0.35 / 0.45 | 3 / 5 / 6 | **1.500** / 2.500 / 3.000 |

**"L-3's stated resolution floor" was my misquote.** `CLAUDE.md:431-433` gives the floor as
**"roughly 10 particles per flow depth"**; the "4 particle layers and 2 grid cells" is
L-3's *description of the g64 baseline*, offered as the limitation. **Against L-3's actual
stated floor, 17 of 17 runs fail, not 4 of 17.**

Corrected: four of the seventeen are resolved more thinly than the g64 baseline L-3 quotes,
and **all seventeen are far below the ~10-particles-per-depth rule of thumb L-3 states**.
That still matters for item 5, because g48 is one of its three rungs, but the honest
framing is that the whole set is under-resolved by L-3's own criterion rather than that
four runs are exceptional. Note also the water is the **same physical depth**, 0.2944294 m,
on every grid: it is the resolution that is coarser, not the water that is thinner.

## 3d. Code delivered, all dry-run tested, none GPU-validated

| module | what it is | state |
|---|---|---|
| `sphere_heave.py` | the Kramer 2021 sphere scene, Option B | geometry-tested and **dry-run tested against a stub solver**: trap contract T1/T2 and call ordering verified at runtime, integrator checked against a hand computation |
| `outflow_deactivate.py` | depth-keyed retirement, Option A | **NOT an outflow**, see below. Six constraints, each asserted with a deliberately constructed failure |
| `blocking.py` | transient exclusion, stationarity, blocked SE | selftest passes the controls that refuted its own predecessor |
| `spin_down.py`, `depth_station.py`, `p2_decompose.py` | analysis on existing artifacts | run provenance fixed; **ghost guard added and verified to fire** |
| `prestage_jobs.sh` + `R5_PHYSICS_BATCH_MANIFEST.md` | the GPU queue | criteria fixed in advance, including one arm logged INDETERMINATE beforehand |

**Three things a reader must know about `outflow_deactivate.py` before running it:**

1. **Deactivation FREEZES a particle in place; it does not remove it.** Advection is inside
   `g2p_particle` behind the gate. I claimed "its mass leaves the simulation" and that was
   wrong, against a primary-source finding I had already made myself.
2. **It is a mass sink upstream of a closed wall, not an outflow.** The +x face is closed
   twice and my own F-7 says an outflow must skip that.
3. **Frozen ghosts pin every depth statistic.** Nothing in the driver filters them. My
   analysis scripts now do, verified: on a synthetic archive the ghosts pinned a reading
   0.1992 m high and the guard removes exactly that. A retirement run that does not dump a
   `retired` mask is **unanalysable**.

## 3e. Three assertions I shipped that could not fail

Recorded together because the pattern matters more than any one of them. In each case a
check passed, I reported it as evidence in a commit message, and it was incapable of
failing:

- the SDF margin guard, fed inputs it was right to accept;
- "the smallest planned domain buys two clean periods", which passed only on my own
  wave-speed convention;
- the retirement drift-back check, whose guard was False so **it never executed at all**
  while the commit message said it was asserted.

All three are now falsifiable. The lesson is narrower than "test more": **a check that
cannot fail is worse than no check, because it is reported as evidence.**

## 4. Nothing on this branch has been run on a GPU

TACC has been cold the entire session, re-checked live at 17:04 BST and still
`Permission denied (keyboard-interactive)`. `R5_PHYSICS_BATCH_MANIFEST.md` and
`prestage_jobs.sh` are ready to fire, with pass criteria fixed in advance. Job A (brake
sweep, ~45 s of compute) is the one item that converts an INFERRED claim into a
measurement, and it is never the one to drop.

## 5. The pattern, stated plainly because it is the useful part

Every headline number I produced without review was wrong in magnitude, and **three times
the error was structural rather than noise**: a lever that could not measure what I pointed
it at, an explanation for an event that never occurred, and a module that would have
reported a held level made entirely of dead water.

The corrections came from adversarial review and from checking my own load-bearing
quantities against source, not from more measurement. **The measurements were rarely wrong;
the framing around them usually was.**

Two sharper sub-patterns, both of which cost real time:

- **I regressed against my own prior findings twice.** The freeze-not-delete semantics and
  the closed +x face were both already written down, by me, in
  `OPTION_A_SESSION1_FINDINGS.md`. Re-deriving beats recalling, but *checking the project's
  own record first* beats both.
- **A licence status and a fetch status are different things.** Three documents were
  recorded or assumed to be behind an access barrier when all were openly licensed and
  merely bot-blocked, and one was served by the publisher's backend while its front end
  refused.
