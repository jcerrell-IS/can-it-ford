---
name: geoelements-tech-reference
description: Technical encyclopedia for Josie's GeoElements REU 'Can It Ford' project: gsplat, Genesis, MPM, kks32/mpm-engine, PhysGaussian, GNS, papers, tutorials, TACC Vista/LS6 setup, and pipeline concepts.
---

# GeoElements Tech Reference (the project encyclopedia)

## Purpose
Be the single source of truth for the **technology, code, papers, tutorials, repos, and supercomputer setup** of Josie's REU project. When she asks "what is X," "what does the paper say about Y," "where is that line from," or "help me run Z," answer from here — grounded, specific, and in her learning style. The companion skill `reu-research-log` tracks *progress*; the companion skill `mpm-render-pipeline` is the hands-on production workflow for actually running kks32/mpm-engine and rendering; this skill holds *knowledge*.

**Authoritative source, corrected July 8:** no single file is fully current — `Can_It_Ford_SOURCE_OF_TRUTH.md` is referenced by multiple other docs as the top authority but **does not exist in the project files or Drive**, confirmed by direct search. Until that's resolved, the most current sources are: (1) your own memory record, (2) `kks32_mpm_engine_complete_reference_July7.md` and `Slack_Links_Reality_Check_July7.md`, (3) whatever the live GitHub repo actually says, verified fresh, not recalled. `GeoElements_Project_Brain.md` (the previous authoritative pointer) is itself flagged moderately stale in `00_MASTER_CORRECTIONS_INDEX.md` — use `08_GeoElements_Project_Brain_UPDATED.md` if you need it at all.

**Supersedes the dead framing:** the old Deep Brief / Playbook / "Claude_response_form_previous_project" describe GNS-surrogate-modeling and CV post-disaster damage assessment as if they might be the project. **They are not.** Do not use them.

---

## THE ACTUAL PROJECT: "Can It Ford?" (this section was missing before July 8 — it should never have been)

Given a real flooded road, can a specific vehicle ford it, and what's the simplest physical abstraction sufficient to answer that correctly? This is the concrete, current project — not just the general PVWM background below, which explains the framework it sits inside.

**Abstraction ladder:**
- **L0** — static NWS depth threshold (~0.15m). Over-conservative in still water.
- **L1** — AR&R hazard scalar, hazard = depth × velocity (m²/s), where velocity is the FLOOD's flow rate, not the car's speed. Ignores vehicle weight entirely. Thresholds by class (small passenger 0.30, large passenger 0.45, **Large 4WD 0.60** — not generic "4WD," confirmed against the actual report text). Source: Shand, Cox, Blacka & Smith (2011), AR&R Project 10 Stage 2, Report P10/S2/020 — the report itself calls these values "draft, interim, informal," not a validated safety boundary.
- **L2** — full coupled particle simulation. NO-FORD when lateral drift exceeds `DRIFT_THRESHOLD = 0.05m`. **It has no peer-reviewed source and must not be given one.** Corrected 2026-08-12: an earlier version of this line proposed Smith, Modra and Felder (2019), DOI:10.1111/jfr3.12527, as the candidate citation. Register D7 records that attribution as a MISATTRIBUTION, because that equation contains no such criterion, and register Section I lists it for deletion on sight. The `provenance-audit` skill already documented it as a false attribution, so the two skills were in direct conflict until this fix. Correct framing: it is a conservative internal numerical onset-of-motion tolerance, exactly as `gates.py:195-196` states in its own print statement. Register D7 also records that the tolerance is declared at 24 sites under FIVE names (`DRIFT_THRESHOLD`, `L2_DRIFT_M`, `DRIFT_THRESHOLD_M`, `THRESHOLD`, `DRIFT_M`), so deduplicate by name and unit, never by value.

**Citation backbone for the L0/L1/L2 "simplest sufficient model" framing:** this structure is established methodology, not novel as a general principle. Cite Oberkampf & Roy (2010, *Verification and Validation in Scientific Computing*), the NASEM VVUQ report (2012), and ASME V&V 40-2018 (context-of-use/model-risk framing) for the engineering backbone; Blackwell sufficiency and Li-Walsh-Littman (2006, MDP state abstraction) for the formal "coarsest model that preserves the decision" backbone. Novelty claim belongs at the specific-application level (this three-tier hazard-traversability problem), not the principle level: a reviewer familiar with VVUQ will otherwise flag it as reinventing adequacy-for-purpose. Source: `docs/research_2026-08/Task-Conditioned_Model_Fidelity_Selection-_Is_There_Established_Prior_Art_.md`.

**Current build target for L2, as of Kumar's July 7 Slack instruction: `kks32/mpm-engine`, not Genesis's `MPM.Liquid`.** See the dedicated section below — this is a real pivot, not a footnote.

**What's closed, don't reopen unprompted:** an earlier synthetic-geometry SPH pilot study (flat plane, box-morph water, box-morph vehicle, Genesis's SPH solver) produced a 23-pair/16-divergence finding. This was a methods rehearsal, not the paper's dataset, and is explicitly closed. **Do not default to discussing SPH or the synthetic pilot unless Josie explicitly asks about it.**

---

## kks32/mpm-engine: the current MPM target (pointer only — full detail lives elsewhere)

**Current build target for L2, per Kumar's July 7 Slack instruction: `kks32/mpm-engine`, not Genesis's `MPM.Liquid`.** Two live, unresolved disputes exist about its exact API surface — full sourced detail, contradictions, and citations live in the **`mpm-technical-deep-reference`** skill, not here. Hands-on commands to actually run it live in the **`mpm-render-pipeline`** skill. This skill stays high-level: know that the pivot happened and why, defer to those two skills for anything more specific.

**Standing rule:** never restate a prior session's claim about this repo's API surface as settled fact without checking the live source first. This project has hit that exact failure shape at least twice.

---

## Engine choice, checked against alternatives (2026-08-05)

A structured comparison of Genesis/warp-mpm-family engines against coupled
rigid-fluid alternatives (DualSPHysics+Chrono, Chrono FSI-SPH, Kratos,
preCICE+OpenFOAM, CB-Geo, Taichi MLS-MPM) on five criteria (native through-
flow, two-way coupling, experiment-validated FSI force output, confirmed GH200
aarch64+CUDA build, time-to-first-case) found no candidate satisfies all five.
DualSPHysics is the best-validated alternative (native open boundaries,
repeatedly experiment-validated FSI forces) but ships x86-only precompiled
static libraries with zero documented ARM build, a real blocker, not a
documentation gap. **This applies to the MPM/Warp-lineage family broadly
(both Genesis's own solver and kks32/mpm-engine sit in this family), not
specifically to choosing Genesis over kks32/mpm-engine**: the comparison is
against a different axis (coupled rigid-fluid engines outside the MPM family
entirely), not a re-litigation of the July 7 kks32/mpm-engine pivot.

**Recommendation carried into this project:** validate the current pipeline
against physical/empirical fording benchmarks rather than porting to a new
engine. The three-part rule for when a switch WOULD be justified: (i) the
current pipeline structurally cannot represent a decision-dominant effect
(e.g., sustained through-flow, see the dedicated section in
`flood-mpm-debugging-reference`), AND (ii) the candidate engine has direct
experimental validation for that exact effect, AND (iii) it can run on
project hardware within a bounded fraction of the deadline. Absent all three:
validate what's running, don't switch.

Source: `docs/research_2026-08/Coupled_Rigid-Body_Fluid_Simulation_Engines_vs__Genesis_MPM_on_GH200-_An_Evidence-Based_Comparison.md`.

---

## THE PROJECT IN ONE BREATH (general PVWM background — still accurate, kept)
Build **physically-correct world models** so robots can learn physics in simulation before acting in reality. Today's video-generation world models look photorealistic but **break physics** — Krishna's anchor example: an AI lunar-rover video where the scoop digs backward, soil leaps onto the scoop, and there's scraping *sound* on the airless Moon. The group fixes the physics. Can It Ford is one concrete instantiation of this: query-conditioned "what happens if this road floods" reasoning.

### The pipeline (the arrow chain — memorize this)
```
real video/images
  -> GAUSSIAN SPLAT      represent the world as 3D colored Gaussians (static scene)
  -> MPM SIMULATION       simulate it (MPM = solver for sand/fluid/granular; kks32/mpm-engine is the current target)
  -> RENDER -> video
  -> compare to real hardware        = the SIM-TO-REAL gap
  -> calibrate MPM params            friction, wet vs dry sand, steel vs plastic, water vs honey
  -> APPLICATIONS:  navigation | manipulation | benchmark-dataset generation | Can It Ford (this project)
```
- **Represent** = Tutorials 1 & 2. **Simulate** = Tutorial 3, now extended into the actual Can It Ford scripts. The papers explain **why** each step works.

---

## THE STACK (names she'll actually touch)
| Thing | What it is | Where | Notes |
|---|---|---|---|
| **Python + PyTorch** | language + DL library (GPU parallelization) | — | NOT TensorFlow. ML background NOT required. |
| **gsplat** | the Gaussian Splatting **trainer** (Tutorials 1–2 use it) | github.com/nerfstudio-project/gsplat | nerfstudio project. Runs on **LS6**. |
| **Genesis** | a simulator with many solvers, including MPM and SPH | genesis-world.readthedocs.io | Was the earlier build target; the SPH pilot study used this. Runs on **Vista**. |
| **kks32/mpm-engine** | **current MPM build target**, per Kumar's July 7 instruction | github.com/kks32/mpm-engine | Warp-MPM, not Taichi-native. See dedicated section above and the `mpm-render-pipeline` skill. Runs on **Vista**. |
| **MPM (Material Point Method)** | the **solver** for particle systems (sand, fluid, granular flow) | inside Genesis / kks32/mpm-engine / Taichi / Warp | She does NOT need its internals for most tasks. |
| **Taichi MPM** | the MPM implementation used in **Tutorial 3**'s original framing | (Taichi) | Historical/tutorial context; the live Can It Ford scripts moved to Genesis then to kks32/mpm-engine. |
| **Newton** | Stepan's repo (started Newton, switched to Genesis, kept the name) | newton-physics.github.io | Also containerized on Vista as a fallback if Genesis hits a wall; not the current plan. |
| **GNS** | Graph Network Simulator (Kumar's own GNN surrogate, Choi & Kumar 2023) | github.com/geoelements/gns | Confirmed Kumar-authored. **OPTIONAL / under-the-hood** for Can It Ford, but its visualization conventions (viridis, particle-first, side/top/aerial cameras) are the closest match to "what Kumar's own figures look like" — see `mpm-render-pipeline` for the full checklist. |
| **LearnMPM** | MPM textbook | geoelements.org/LearnMPM | OPTIONAL. |
| **Vista** | TACC GH200 (ARM64) supercomputer — **now her primary machine for Genesis/MPM simulation work**, corrected July 8 | vista.tacc.utexas.edu | **This directly contradicts an earlier version of this skill, which said "NOT Vista, ARM64 dependency risk." That was wrong as of at least early July and should not be repeated.** |
| **LS6 (Lonestar6)** | TACC A100 supercomputer, used for **gsplat training** | ls6.tacc.utexas.edu | Not the Genesis/MPM machine — that's Vista. |
| **Slurm + idev** | job scheduler + the command to grab an interactive GPU node | on LS6 and Vista | `idev` borrows a GPU; never run heavy work on the login node. |
| **SSH / Slack / Google Drive** | how she reaches the clusters / comms / project mgmt | — | — |

---

## ACCOUNT & PATHS (copy-paste ready)
**TACC account** (accounts.tacc.utexas.edu):
- Username **`jcerrell0629`** · Status Active · Shell `/bin/bash`
- Home `11603/jcerrell0629` · UID 910303 · Default GID 819066
- MFA: TOTP paired. DesignSafe username assumed same (`jcerrell0629`, unconfirmed — flagged in the July 6 corrections index and never resolved since).

**Login flow:** `ssh jcerrell0629@ls6.tacc.utexas.edu` or `ssh jcerrell0629@vista.tacc.utexas.edu` → `Password:` (TACC pw, invisible as you type) → `TACC Token:` (6-digit TOTP). **If it never reaches the token prompt = allocation/membership issue, not a password problem.**

**Vista session checklist (Genesis/MPM work):** `idev` → `module load tacc-apptainer` → `export GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif` → `cd /work/11603/jcerrell0629/vista/`. Use `python3`, not `python`, inside the Genesis container. For kks32/mpm-engine specifically, environment is a separate Python 3.12 venv, not the Genesis container — see `mpm-render-pipeline`.

**Luke's shared resources on LS6** (Tutorial 1 reads from here):
- Env: `/scratch/10386/lsmith9003/python-envs/gsplat_env`
- Garden data: `/scratch/10386/lsmith9003/src/nerf_studio/gsplat/examples/data/360_v2/garden/`
- **Permission error on these → Slack Luke Smith. Do NOT debug it yourself.**

**Luke's resources on Vista:**
- `GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif`
- `NEWTON_PATH=/work/10386/lsmith9003/vista/containers/newton_container.sif`

---

## THE 3 TUTORIALS (her readable Drive docs = the pipeline, in order)
| # | Title | Stage | Status |
|---|---|---|---|
| 1 | Running gsplat / NeRF Studio on LS6 (garden scene) | REPRESENT (training wheels) | Complete as of ~June 12. |
| 2 | Custom dataset for Gsplat on LS6 (her OWN video) | REPRESENT (her own) | Complete as of ~June 12 (`bench.mov`). Full workflow in the `splat-dataset-prep` skill. |
| 3 | Running Taichi MPM with trained Gsplat on LS6 | SIMULATE | Complete as of ~June 12; evolved into the actual Can It Ford scripts, now targeting kks32/mpm-engine on Vista rather than the original LS6/Taichi framing. |

### Tutorial 1 — corrected runbook (3 phases, by machine location)
**PHASE A — LS6 login node:**
```
ssh jcerrell0629@ls6.tacc.utexas.edu
cd $SCRATCH
git clone --recurse-submodules https://github.com/nerfstudio-project/gsplat.git
ls            # confirm gsplat/ is there
```
**PHASE B — GPU compute node:**
```
idev -N 1 -n 1 -p gpu-a100-dev -t 2:00:00      # wait for prompt to change to a node name
module load cuda/12.2
source /scratch/10386/lsmith9003/python-envs/gsplat_env/bin/activate
cd gsplat/examples
CUDA_VISIBLE_DEVICES=0 python3 simple_trainer.py default \
  --data_dir /scratch/10386/lsmith9003/src/nerf_studio/gsplat/examples/data/360_v2/garden/ \
  --max_steps 3_000 --eval_steps 3_000 --save-ply
pwd                                  # SAVE this path
ls results/garden/videos/            # confirm the mp4 exists
```
**PHASE C — back on the Mac:**
```
exit        # twice (compute node, then login node)
scp jcerrell0629@ls6.tacc.utexas.edu:<PWD_PATH>/results/garden/videos/traj_2999.mp4 ~/Desktop/
```
**Three known errors in the official doc (already corrected above):**
1. scp path says `results/videos/` but the real save path is `results/garden/videos/`.
2. `<path_to_gsplat>` is undefined in the doc → use `$SCRATCH/gsplat` or the `pwd` from training.
3. If `--max_steps 3_000` errors on the underscore, use `3000`.

---

## READINGS — what each is, the must/optional split, and WHERE specific concepts live
**Hassan's split:** MUST = the World-Models paper + the navigation/path-planning paper + a Gaussian-splatting paper. HOBBY (only if curious) = GNS, LearnMPM, digging/excavation paper.

### 1. "Path Planning in Physically Viable World Models", CONFIRMED Kumar-lab paper, arXiv 2607.00673
**In the project as** `CoRL_2026___Physically_Viable_Planning.pdf` (the anonymized double-blind review copy). **Authorship confirmed 2026-08-05** via direct arXiv fetch of the public posting (arXiv:2607.00673, submitted 1 Jul 2026, listed for CoRL): **Su Ann Low, Cheng-Hsi Hsiao, Xingjian Li, Adam J. Thorpe, Ufuk Topcu, Krishna Kumar**, all @utexas.edu. Cheng-Hsi Hsiao is a direct mentor-meeting contact on this project. The "anonymous, not confirmed" hedge in earlier versions of this file is resolved: this is safe to cite as Kumar-lab work. Anchor facts + section map:
- **Core idea (Abstract / §1):** augment a reconstructed **3D Gaussian splat** scene with **MPM physics simulation** to generate *physically modified* "what-if" versions of the same environment (flooding, terrain collapse, debris) **without recollecting sensor data or rebuilding the map**, then plan a route and check if it stays feasible *before* the robot commits.
- **PVWM = Physically Viable World Model (§1):** "transforms a reconstructed scene into query-conditioned environments generated by specified physical interventions" — answers *what would happen under a given intervention.*
- **§3.1 Scene Reconstruction & Terrain Model:** Gaussian primitives `{(µ_i, Σ_i, c_i, α_i)}`. Ground/obstacle/floater classification via orientation. 2D DEM + obstacle mask → occupancy map G0.
- **§3.2 Intervention Simulation:** MPM over surface/subsurface material points, "extending PhysGaussian [38] to support multi-material interactions and long-horizon rollouts." Fluids for flooding, granular for landslides, elastic for trees. Defines wading threshold `τ_wade`, impassable mask `M_i`, navigation surface `h_nav`.
- **§3.3 Traversability-Aware Planning:** builds on FOCI — Gaussian-overlap collision integral + B-spline trajectory optimization.
- **Three eval scenarios:** Central Texas field site (rising flood severity), Alaska village scene (fixed geometry, add floodwater), sandbox scene (landslide runout).
- **Why it matters to Josie:** her splat + MPM sim are exactly the two ingredients this paper combines. Can It Ford is a concrete instance of exactly this framework, applied to vehicle fording specifically rather than general robot path planning.

**Validation gap, confirmed by independent prior-art search:** an external reconstruction-to-decision pipeline review found this paper satisfies reconstruction → physics sim → route-feasibility decision, but explicitly does NOT validate against independent empirical criteria: the authors state the eval environments "exist only in simulation" and this "limits the applicability of hardware validation." A broader search across defense/off-road/disaster-response domains found no published pipeline that closes reconstruction → sim → a specific vehicle's fording go/no-go → validation against independent fording criteria (e.g., FM 90-13's 1.5 m/s current-velocity limit, published D×V thresholds, or a physical test). This is the specific gap Can It Ford's empirical-comparison work could fill, so position it as closing this paper's stated limitation, not as a competing pipeline. Source: `docs/research_2026-08/Reconstruction-to-Decision_Pipelines-_Prior-Art_Assessment_for_Sensor-Reconstruction_Physics-Simulation_Validated_Feasibility_Safety_Verdict.md`.

### 2. "Physically Viable World Models" — standalone team paper (arXiv 2605.30542)
Thorpe et al., co-authored by **Hassan Iqbal and Cheng-Hsi Hsiao** (confirmed). THE point paper; read first. Attribution boundary: this framework belongs to the lab/paper, not to Josie — never say her work "contributes to their broader program," state her contribution (the closed reconstruct-to-decide pipeline + abstraction-ladder experiment) directly instead.

### 3. 3D Gaussian Splatting — Kerbl et al. 2023 (arXiv 2308.04079)
What Tutorials 1–2 actually produce.

### 4. PhysGaussian — Xie, Zong, Qiu, Li et al. (arXiv 2311.12198)
The **splat + MPM bridge**. Integrates Newtonian dynamics into 3D Gaussians via a custom MPM; "what you see is what you simulate (WS²)" — same Gaussian kernels for both simulation and rendering, no meshing needed. **No detected license in GitHub metadata** — check before committing any derived code (e.g. `gs_simulation.py`-derived extraction logic) to the public `can-it-ford` repo.

### 5. GNS — Choi & Kumar 2023 (arXiv 2305.05218). **Confirmed Kumar-authored, OPTIONAL/under-the-hood for Can It Ford.**
- GNN learns local interaction laws; nodes = particles; predicts next state via Euler explicit integration.
- Its **visualization conventions are the closest confirmed match to "what Kumar's own figures look like"** — see `mpm-render-pipeline` for the full checklist derived from this paper plus Kumar & Vantassel 2023 (CB-Geo MPM, DOI:10.21105/joss.05025) and Abram et al. 2022 (Galaxy in-situ viz, DOI:10.1109/MCSE.2022.3155074).

### 6. DeepMind GNS — arXiv 2002.09405. **OPTIONAL.** Ancestor of the Choi–Kumar paper.

### 7. LearnMPM (geoelements.org/LearnMPM). **OPTIONAL** textbook.

---

## VOCABULARY
- **World model** = a learned simulator of how a scene evolves. **"Physically viable"** = obeys real physics, not just looks real.
- **Gaussian splat** = a 3D scene stored as a cloud of colored, fuzzy 3D blobs (Gaussians) you can rotate and render from any angle. Static.
- **MPM (Material Point Method)** = tracks material as particles carrying mass/velocity on a background grid. Great for sand, water, mud, granular flow.
- **SPH (Smoothed Particle Hydrodynamics)** = a different particle-based fluid solver, used in the now-closed pilot study. Don't confuse with MPM; the two aren't interchangeable and this project's abstract distinguishes them.
- **Constitutive model** = the material law describing how a substance responds to force.
- **DEM (digital elevation model)** = a 2D height map of the ground, derived from the splat.
- **Sim-to-real gap** = difference between simulated behavior and real hardware; closed by tuning material parameters.
- **DRIFT_THRESHOLD** = 0.05m lateral vehicle displacement, the current NO-FORD trigger for L2. Still uncited.
- **D×V (hazard scalar)** = depth times velocity, the L1 metric, m²/s.
- **FOCI** = the Gaussian-collision + B-spline planner the CoRL paper builds on.

---

## HOW TO TEACH / EXPLAIN THIS TO JOSIE (Feynman protocol, one concept per turn)
- **Method:** explain → give the method → let HER try → verify. No math until she asks. Lead with a physical analogy (granular flow, friction, buoyancy, fluids — she has a physics background).
- **Device tags:** "On MacBook" = terminal/code/SSH/this chat. "On iPad" = GoodNotes diagrams/notes. Never tell her to type notes on the Mac.
- **One concept per turn. Wait for her attempt before the next.**

## HOW TO HELP HER CODE ON THIS PROJECT
- **I CAN:** write/debug Python for this project, read repos live (GitHub), read the papers, interpret terminal errors, explain what any command does and what success looks like.
- **I CANNOT:** run her GPU jobs, reach into Vista/LS6 directly (only via her running Claude Code/SSH), or see her live Slack/Drive unless a connector surfaces it. **She runs; I diagnose.**
- **No inline comments or docstrings in any code, any language, ever** — this is a hard, standing rule, not a style suggestion.
- **Always give:** the command + what it does + what success looks like. Catch known traps (sign / reciprocal / unit / **path** errors).
- **15-minute stuck rule:** Cristian first, then group Slack. For permission errors on Luke's shared paths → Slack Luke Smith, don't debug blind.

## READING PROJECT FILES (so future Claude can quote exact lines)
Project `.pdf` files are often **ZIP archives** of numbered `.txt` + `.jpeg` page files, not real PDFs — `pdftotext` fails on these. To pull exact lines:
```
unzip -o -q "<name>.pdf" -d /tmp/x/<name>
cat /tmp/x/<name>/*.txt
```
`.docx` and extensionless files are plain UTF-8 → just `cat`.

---

## CRITICAL RULES
1. **The concrete project is Can It Ford: vehicle flood-traversability, L0/L1/L2 abstraction ladder, currently targeting kks32/mpm-engine.** GNS/CV-damage = dead framing; never use it. The SPH pilot study is closed — don't reopen unprompted.
2. **She runs; I diagnose.** Never claim to have run her jobs without a fresh, live check backing the claim.
3. **Never restate a prior session's claim about API/solver/parameter status as current fact without checking the live source first.** This has caused real, documented errors in this project at least twice.
4. **Never hand her homework/answers.** Feynman protocol, one concept per turn.
5. **Ground claims in the source.** Name the paper + section, pull the exact line if needed.
6. **ML background is not required.** Keep it encouraging, not gatekept.
7. **Permission/env errors on Luke's shared paths → Slack Luke, don't debug. Allocation errors → wait on Krishna.**
8. **Keep it short (ADHD):** answer first, one path, device-tagged steps, one check-in.
9. **No em-dashes ever, no inline code comments, no docstrings.**

---

## REFRESH — this is a LIVING encyclopedia (update it constantly)
Trigger: Josie says **"refresh the tech reference,"** **"update my project encyclopedia,"** or new material arrives. Edit this SKILL.md in place, keep her voice/format, echo a 2-line diff.

**What to watch for and add:**
- [ ] **Resolution of the two live kks32/mpm-engine disputes** (SDF collider real-or-stub; render stack) — update `mpm-render-pipeline` once verified on Vista, then remove the "unresolved" framing here.
- [ ] **Whether `Can_It_Ford_SOURCE_OF_TRUTH.md` gets created** — update the authoritative-source pointer once it exists and is confirmed current.
- [ ] **New papers / transcripts** — add anchor facts + section map to READINGS.
- [ ] **DRIFT_THRESHOLD citation** — currently uncited, candidate is Smith et al. 2019 Eq. 6.
- [ ] **DesignSafe username** — still unconfirmed as of last check.
- [ ] **New repos / commands** from Hassan/Cheng-Hsi/Luke/Kumar — add URL + one-line purpose.
- [ ] **Concept-teaching progress** — track what's been taught.

**How to refresh:** ask only what changed → edit the affected section(s) → mark anything unconfirmed `(unconfirmed)` → echo the diff.
