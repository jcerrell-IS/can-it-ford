# Audit of the deep-search prompt, what the corpus already answers, and the plan

Written 2026-08-18, superseding `docs/DEEP_SEARCH_PROMPT_2026-08-18.md` where they
conflict. Every number here was measured live this session.

---

## PART 1: AUDIT OF WHAT I JUST WROTE. Four faults.

**Fault 1, the big one: it never asked about a moving vehicle.** All nine questions
assume a stationary hull. The actual goal is a car that drives into floodwater at
different speeds. That omission alone makes the prompt low-value for the real target.

**Fault 2: I inferred gaps from tag COUNTS, not from content.** I reported
`inflow-outflow` has 2 papers and concluded the area was thin. I did not read what
the other tags hold. When I did, several of my nine questions turned out to be
partly answered already, listed in Part 2. That is the same error the project's own
claim-discipline rule forbids: a count is not a reading.

**Fault 3: it was literature-only.** It asks what is known and never asks what is
runnable. It does not mention warpmpm, Vista, LS6, Chrono, GNS, or any existing
script in this repo, so nothing it returns would shorten the path to a simulation.

**Fault 4: it ignored the compute constraint entirely**, which turns out to be the
binding one. See Part 3.

A note on the search tool itself: `analysis/research_index.py --query` is a LITERAL
matcher, not semantic. It returned 0 for every phrase I tried, including topics the
corpus demonstrably covers. **Use `--method <tag>` for real coverage questions.** A
zero from `--query` is not evidence of absence.

---

## PART 2: WHAT THE CORPUS ALREADY ANSWERS. Do not commission these again.

Measured with `--method`, reading the entries rather than counting them.

**Moving and non-stationary vehicles are ALREADY COVERED, 8 papers.** This is the
single most important correction to my prompt.

| DOI | What it is | status |
|---|---|---|
| `10.1007/s11433-023-2137-5` | **3D large-scale SPH vehicle wading with GPU acceleration**, 2023 | **UNCITED** |
| `10.1111/jfr3.12657` | Hydrodynamic effect on **non-stationary** vehicles at varying Froude | in paper |
| `10.1016/j.rineng.2019.100032` | Partially submerged **non-stationary** vehicle on low-lying roadway | in paper |
| `10.1115/1.4071177` | Vehicle-water interaction in shallow water, simulation **plus experimental validation**, 2026 | in paper |
| `10.1115/detc2015-47142` | **Coupled multibody dynamics and SPH** for vehicle water crossing (this is Chrono) | in paper |
| `10.4271/2022-01-0768` | Transient 3D CFD **moving-mesh** vehicle water wading | in paper |
| `10.4271/2014-01-0936` | Wading simulation, challenges and solutions | **UNCITED** |
| `10.1177/0954407020942005` | Vehicle wading performance | repo-only |

**Adaptive refinement is covered, 7 papers**, including `10.1002/cav.70024` (adaptive
boundary MPM with surface particle reconstruction, 2025), `10.1002/nag.3731` (mapped
MPM for sharp gradients, 2024) and `10.1061/(asce)em.1943-7889.0000981` (dynamic
adaptive refinement for free-surface MPM). My question 3 and 6 partly duplicate this.

**Added mass and unsteady drag are covered, 6 papers**, including Grift et al 2019
`10.1017/jfm.2019.102` (drag on an accelerating submerged plate) and
`10.1080/17445302.2019.1615705` (surge added mass of planing hulls). My question 7
should not re-ask this.

**Grid convergence methodology is covered**: Celik 2007, Roache 1994, Stern 2001.

**Genuinely thin, so keep asking**: particle recycling in fixed-allocation codes
(question 1, still zero), image particles (question 4, Schulz & Sutmann not indexed),
free-overfall resolution floor (question 3), sub-grid road roughness (question 6),
bounded-domain artefact (question 9).

---

## PART 3: THE COMPUTE REALITY, AND WHAT IT UNLOCKS

Measured live 2026-08-18:

| machine | SUs left | arch | GPU | warpmpm present |
|---|---:|---|---|---|
| Vista | **616** | aarch64 | GH200 | yes, `$WORK/mpm-engine` |
| LS6 | **9,539** | **x86_64** | A100 | **no venv, no mpm-engine, no warpmpm** |

**LS6 holds 15.5 times Vista's remaining budget and is doing nothing.** Vista is
nearly exhausted; tonight's short jobs alone have been drawing it down. Standing
warpmpm up on LS6 is therefore the highest-leverage infrastructure task available,
worth more than any single physics improvement.

**And LS6 being x86_64 retires a standing engine decision.** Project note L-8 says
"do not switch engines, DualSPHysics ships x86-only static libraries, a hard aarch64
blocker on GH200". **That blocker does not exist on LS6.** Every x86-only package
previously ruled out is available there. The engine decision was correct for Vista
and was never re-examined for LS6.

**Chrono is already known to build on GH200** in 94 s (four gotchas recorded), and
the corpus contains the Chrono vehicle-wading paper `10.1115/detc2015-47142`. Chrono
brings multibody dynamics, which is exactly what a moving car with wheels and
suspension needs and what a solidified particle hull cannot express.

---

## PART 4: THE HIGHEST-LEVERAGE MOVES, USING WHAT ALREADY EXISTS

Ordered by value per unit effort. Each names the asset that already exists, because
none of this is greenfield.

1. **Stand up warpmpm on LS6.** Unlocks 15.5x the compute. x86_64 makes the install
   easier than Vista's, not harder. Validate by reproducing one canonical g64 run and
   diffing the summary against `data/g128_2026-08-18/`.
2. **Run the moving vehicle. The API already exists and is unused.**
   `add_sdf_collider`, `set_sdf_pose`, `reset_sdf_force`, `sdf_wrench` are all at
   `third_party/mpm-engine-544c93dd-solver-core/core/solver.py:324-362`, and five
   files in this repo already call them: `simulation/validate_coupling_force.py`,
   `simulation/coupling_force/coupler.py`, `simulation/coupling_force/rung_b_coupled.py`,
   `realism_track/diag_wrench_fixed_pose.py`, `simulation/sim_road.py`. **No solver
   change is needed for a moving car.** The known blocker is a non-zero centre-of-mass
   offset, which `RigidBody6DOF` refuses; the Yaris cloud CG sits 0.6312 m above the
   floor against a bbox mid-height of 0.7427 m.
3. **Harvest `claude/fork-three-class` before redoing anything.** It carries **85
   files and 3,565 insertions** not on the current branch, including matched-dx
   three-vehicle work.
4. **Reconsider Chrono::FSI on LS6** for the moving-vehicle arm specifically, keeping
   warpmpm for the stationary canonical runs. Two engines answering the same question
   is corroboration; one engine answering it twice is not.
5. **Only then** the realism stack: real road texture, resolved free surface, and the
   inlet/outlet condition that item 32 showed is still unsolved.

---

## PART 5: THE PROMPTS. Three, each self-contained.

Split deliberately: one deep search per theme ranks better than one search for
everything. Each carries its own exclusion list so nothing already held is returned.

---

### PROMPT A: a moving vehicle at speed, on a GPU, at realistic scale

I simulate a passenger vehicle in floodwater with a GPU material point method. Every
run so far has held the vehicle **stationary** in a flow. I now need it to **drive
into the water at a prescribed or solved speed**, and I need to know exactly how
published work does this before I build it.

**Already in hand, do not return**: `10.1007/s11433-023-2137-5`, `10.1111/jfr3.12657`,
`10.1016/j.rineng.2019.100032`, `10.1115/1.4071177`, `10.1115/detc2015-47142`,
`10.4271/2022-01-0768`, `10.4271/2014-01-0936`, `10.1177/0954407020942005`,
`10.1016/j.jfluidstructs.2015.06.010`, `10.1111/jfr3.12527`, `10.1111/jfr3.70181`,
`10.3390/su151713262`, `10.1016/j.rineng.2025.107189`, `10.1063/5.0276643`.

For each published vehicle-in-water simulation where the vehicle MOVES, tell me:

1. **Is the motion prescribed or solved?** A kinematically driven body and a body
   free under hydrodynamic load are different simulations. Which did they do, and if
   solved, what rigid-body integrator and how was the hydrodynamic wrench obtained
   from the fluid solver?
2. **How is the wheel contact handled?** My vehicle is a watertight hull with no
   wheels, no suspension and no rolling degree of freedom. Full-scale experiments
   report an order-of-magnitude difference between locked-wheel friction (~0.30) and
   free-rolling resistance (~0.024), so this is not a detail. Did anyone model
   wheels explicitly, and what did it change?
3. **What entry speeds and depths** were simulated, and is there any published
   speed-depth map for a vehicle DRIVING IN rather than being parked in a flow?
4. **What is the centre-of-mass and inertia treatment?** I have a hard blocker where
   the collider rotates about its geometric centre while the real CG is offset.
5. **GPU scaling numbers**: particle count, cell count, wall-clock per physical
   second, GPU model, and whether multi-GPU. I need to size a run, not admire one.
6. **Which of these has runnable public code?** Repository URL, licence, and whether
   it builds on x86_64 with CUDA and an A100.

Flag any paper that reports a moving-vehicle simulation FAILING to match experiment,
and say what they attributed it to.

---

### PROMPT B: the realism ladder, ranked by whether it changes a verdict

My simulation produces a binary engineering verdict: does the vehicle move or not. I
want to know which physical realism improvements actually change that verdict and
which only improve appearance, because I have limited compute and I would rather
spend it on effects that matter.

**Already in hand, do not return**: `10.1017/jfm.2019.102`, `10.1111/jfr3.70181`,
`10.1016/j.jfluidstructs.2015.06.010`, `10.1002/cav.70024`, `10.1002/nag.3731`,
`10.1061/(asce)em.1943-7889.0000981`, `10.1002/nag.70048`, `10.1016/j.jcp.2016.10.064`,
`10.1016/j.cma.2022.114809`, `10.1002/nme.7217`, `10.1063/5.0276643`.

Rank these by measured effect on an incipient-motion or flotation threshold, with
the number and its source, and say plainly where no one has measured it:

1. **Road surface geometry.** Camber, crown, gutter, kerb, longitudinal grade. Has
   anyone shown a crowned or cambered road changes a vehicle stability threshold
   versus a flat plane? My cell is 0.147 m and a road texture depth is a few
   millimetres, one fiftieth of a cell, so I need sub-grid or effective-roughness
   treatments, not resolved micro-texture.
2. **Free-surface fidelity.** Air entrainment, spray, surface tension, turbulence
   closure. Which of these has been shown to move a force coefficient on a bluff
   body in shallow flow by more than the scatter between existing experiments?
3. **Water compressibility.** I run a reduced bulk modulus giving a numerical sound
   speed of 12.85 m/s, below the common ten-times-max-velocity guideline. Is there a
   documented case where a discrete outcome flipped on sound speed alone, and does
   the ten-times rule have a primary derivation or is it convention?
4. **Inlet and outlet.** I need a free-surface outlet that is not a wall and not a
   deletion plane. Kinematic outlets do not hold a discharge in my closed-mass
   domain: measured decay to 0.25 to 0.29 of initial in every configuration tried,
   including with a 42 percent spare-particle reservoir. **What is the minimum
   sufficient outlet condition for a particle method, and is a pressure- or
   traction-controlled outlet actually necessary?**
5. **Vehicle watertightness and underbody detail.** Sealed hull versus a body that
   floods through the cabin. Which published work models ingress, and how much does
   flotation depth move?

For each, I want: the effect size, the threshold quantity it moved, and whether the
finding is from simulation, experiment, or both.

---

### PROMPT C: engine and HPC strategy for two TACC machines

I have two allocations. **Vista**: aarch64, GH200, 616 service units left, warpmpm
installed. **LS6**: x86_64, A100, 9,539 service units, nothing installed. I need to
decide what to run where, and whether to add a second solver alongside my existing
NVIDIA-Warp-based MPM code.

1. **Which open-source particle solvers for free-surface flow with a moving rigid
   body actually build and run on each architecture?** I specifically need to know
   the aarch64 status of DualSPHysics, Chrono::FSI, CB-Geo MPM, SPlisHSPlasH,
   PySPH and Taichi/Genesis, because one of my constraints was recorded as
   "DualSPHysics is x86-only, blocked on GH200" and that constraint does not apply
   to my x86 machine. Which are genuinely multi-GPU?
2. **Published strong and weak scaling numbers** for GPU MPM or SPH free-surface
   simulations: particles per GPU, achieved throughput, and where the scaling breaks.
   I want to know whether a 10 to 50 million particle flooded-roadway run is a
   single-node job or a multi-node one, on A100 and on GH200 separately.
3. **Is a machine-learned surrogate worth it here?** Graph network simulators trained
   on MPM rollouts are used in this group. What is the published accuracy of a GNS-
   style surrogate on a rigid-body-in-fluid incipient-motion problem specifically,
   and has anyone shown a surrogate preserving a discrete threshold rather than just
   a trajectory? If the surrogate cannot preserve the verdict, it is useless to me
   and I want to know that now.
4. **Two-engine cross-validation.** For a vehicle-in-floodwater problem, has anyone
   published the same case in two independent solvers and reported the spread? I want
   to know the realistic disagreement between MPM and SPH on a force coefficient
   before I treat agreement as validation.
5. **Practical**: which of these has containerised builds (Apptainer or Docker) that
   work on a TACC-like system without root, and what are the known build failures on
   CUDA 12.x with an ARM host compiler?

Prefer sources that report wall-clock and hardware. A method paper with no timing is
of limited use for this question.
