# D4: what survives, what was withdrawn, and what is still unreviewed

2026-08-17. Branch `claude/r5-physics`, 20 commits, **unpushed and held**.

This branch's documents carry correction boxes stacked on correction boxes, because three
adversarial review passes found real errors in almost every headline I produced. That is
the process working, but it has made the branch hard to read. **This file is the index: it
states what a reader may rely on, what is retracted, and what has not been checked.**

Rule used throughout: a claim is listed as surviving only if it was checked by a route
independent of the one that produced it, or is true by construction from source.

---

## 1. Survives, and I would defend it

| claim | basis | where |
|---|---|---|
| **The canonical scene has no outflow BC.** Domain closed by floor + 4 slip walls + `add_domain_walls`; `_sustain_inflow` clamps velocity on a band of EXISTING particles; nothing creates, deletes or recycles. `SCENARIO=STANDING_WATER_SUSTAINED_INFLOW` names a BC the code does not implement. | read live from `sim_standing.py` | `R5_PHYSICS_OPTION_A_FEASIBILITY.md` |
| **The water spins down hard and never reaches a steady state.** N=17, settle 8: bulk mean speed falls median **-66.3%**, range -87.4 to -41.3. **0 of 17 gain.** | measured, script committed | `spin_down.py` |
| **Zhao's outflow cannot be ported because warpmpm has no pressure field.** `grep -ci pressure` returns 0 across 3,181 lines at the pinned SHA. The BC's control variable does not exist. | primary source, `inflow_outflow.py:14-21` | `R5_PHYSICS_OPTION_A_FEASIBILITY.md` |
| **A mass-sink hook DOES exist**, contradicting that file's own premise: `particle_selection` gates P2G at six sites and is writable at runtime, so deactivation removes mass at fixed allocation. That is the register's own B7 wording. | read live | same |
| **The runs are not at their labelled depths.** Survived every control including vehicle-free: **+13% to +28%** of label. | measured, multiple stations | `R5_PHYSICS_DEPTH_CONFOUND.md` |
| **P-2 does not measure passthrough.** 77-97% is bounding-box void; median share genuinely in-hull **6.50%**. | re-derived independently | `p2_decompose.py` |
| **Kramer 2021 Table 1**, and the corrected constants: `rho_w` 998.2, `m` 7.056 kg, `g` 9.82, buoyancy **69.2180 N**. The engine's 9.81 is irreducible; equilibrium draft unaffected, period biased +0.051%. | read from the PDF | `R5_PHYSICS_KRAMER2021_TESTCASE.md` |
| **The STUCK mechanism.** `sweepV_g64_v0p5` is STUCK because it decelerated: speed gate shuts frame 8, drift gate opens frame 37, **zero overlapping frames**. Confirmed digit-for-digit by review. | measured, then confirmed | `R5_PHYSICS_BRAKE_STATE.md` |
| **Brake state cannot flip a SLIDE verdict**, on a bound: max friction-removal acceleration 0.578 g against 0.721 needed for the worst run's TOPPLE trigger. | review-supplied bound | same |
| **The two-Steffen distinction**, and that neither DOI appears in any `.bib` or `.tex`. | measured | `R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md` |

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

## 3. Unreviewed, and currently with a reviewer

- The in-hull fraction rising **0.28 to 3.47 pp** across the velocity sweep, a factor of 12,
  and the proposal to report it instead of P-2.
- The null baseline **11.30-14.90%** and "exceeds the gate limit in 17/17".
- "Most runs read below their own null, median -3.38 pp."

**These are percentages, so per the dispatch they stay UNREVIEWED until that pass lands.**
Given that three of three prior passes found magnitude errors in my headlines, treat them
as provisional.

## 4. Nothing on this branch has been run on a GPU

TACC has been cold the entire session. `R5_PHYSICS_BATCH_MANIFEST.md` and
`prestage_jobs.sh` are ready to fire, with pass criteria fixed in advance. Job A (brake
sweep, ~45 s of compute) is the one item that converts an INFERRED claim into a
measurement, and it is never the one to drop.

## 5. The pattern, stated plainly because it is the useful part

Every headline number I produced without review was wrong in magnitude, and twice the error
was structural rather than noise: a lever that could not measure what I pointed it at, and
an explanation for an event that never occurred. The corrections came from adversarial
review and from checking my own load-bearing quantities against source, not from more
measurement. **The measurements were rarely wrong; the framing around them usually was.**
