## Multi-Pane Standing Rules

These apply to every pane in every session automatically, do not
restate them in chat prompts.

- Never fabricate a command, parameter, or claim. Pull from actual
  file content, actual output, or actual verified search results.
  This includes a prior claim from Claude itself, verify independently
  rather than trust at face value.
- Any parameter assigned to a variable (rho, coup_friction, box
  dimensions, mass, thresholds) must trace to a primary source before
  being written into a script or command.
- Do not accept a physical result on intuition. State the formula or
  law used, do a units check, and compare against these anchors: water
  1000 kg/m^3, vehicle effective density 310.494 kg/m^3 for the canonical Yaris hull, the 100-300 band is STALE, sedan
  mass 1000-1600 kg, g=9.81, realistic depth 0-1.0m, velocity
  0-3.0 m/s. coup_friction IS the Coulomb friction coefficient in the
  LegacyCoupler MPM-rigid momentum exchange
  (genesis/engine/couplers/legacy_coupler.py:322), applied as
  |v_t_new| = max(0, |v_t| - mu*|v_n|). The separate numerical
  regularisation parameter is coup_softness, default 0.002. Confirmed
  2026-08-05 by direct source read, superseding all earlier statements
  that coup_friction was numerical-only.
- grid_density >= 96 is NOT the crash threshold and 64 is NOT
  confirmed safe. Replicated bisection 2026-08-05 found gd 80 and 88
  pass 3/3 at 60 steps, gd 90+ fails, non-monotone above the boundary,
  non-deterministic at fixed config. Before citing any grid_density
  as safe, check docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md section C2.
- Before treating any claim in this file as settled: a claim cited
  from another session's confidence, a skill file, or a prior audit's
  conclusion is not a second source, it is the same source cited
  twice. Only a primary-source line, a runtime read, or a replicated
  control counts as verification. Before archiving or superseding any
  dated audit file, pull its VERIFIED-tier findings into
  docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md first, the file can
  go stale, the facts inside it should not disappear with it.
- For any rendered output: water reads as one connected fluid body,
  vehicle position matches its known density, no particles outside
  domain or clipped through geometry, motion continuous across frames.
- rho, coup_friction, box dimensions, mass, and grid resolution are
  coupled. Never flag a value as wrong by pattern-analogy to a
  different script's bug, recompute against the actual script's own
  geometry.
- Never let two panes touch the same file, branch, or process without
  explicit sequencing.
- Any git push, force-push, file delete, or overwrite of an existing
  file requires explicit confirmation before execution.
- Every prescribed task should trace to the poster (July 27), the
  paper (July 31), or a verified rendered physically-plausible MPM
  simulation with a vehicle. Flag anything else as optional/deferred.
- If a specific pane's blocking issue persists unresolved across 3+
  rounds, stop re-prescribing the same diagnostic, escalate to
  Cristian Moran per the 15-minute-stuck rule.
- Prefer event-driven pane signaling over polling: same machine, tmux
  wait-for; same machine automated, a Claude Code Stop hook;
  cross-machine, ntfy.
- Before prescribing idev/GPU allocation, confirm the task actually
  needs GPU. File checks, git operations, and monitoring belong on the
  login node, not inside idev.
- Before asserting any parameter, threshold, citation, mesh property, or
  milestone as fact, read docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md.
  Section I lists claims already proven false. Section E is the vehicle
  asset inventory: there is ONE usable mesh, not three. The July 24
  ledger is historical only and its L1 counts predate the joint-rule fix.

## AUGUST 4 2026 AUDIT, GROUND TRUTH

Vista work August 4 2026, repo verification August 5 2026.

Items 1 to 10 and 12 to 16 were verified by direct read of the live files
named in each item. They supersede any earlier statement in this file, in
a skill file, or in a session summary. Item 11 was verified live on Vista,
not by file read from the Mac, see the item for its evidence path.

1. The 17 gated runs use warpmpm via
   renders/yaris_render_s1/sim_standing.py, NOT Genesis.
   sim_standing.py:10-12 imports warpmpm.core.solver, warpmpm.materials and
   warpmpm.vehicle. Genesis is only the Track 2 box-proxy path
   (simulation/can_it_ford_L2_mpm.py, simulation/can_it_ford_L2.py,
   designsafe-staging/scripts/), which builds the vehicle from
   VEHICLE_SIZE at can_it_ford_L2_mpm.py:26 and :159. No Genesis scene has
   ever loaded the Yaris hull. Do not describe the 17 runs as Genesis in
   any figure, caption, README, poster or paper.

2. Velocity enters as a per-frame Dirichlet clamp on an upstream particle
   slab (sim_standing.py:190-198, called every frame at :202) plus a
   one-shot additive kick applied once after the settle phase (:156-162).
   The clamp overwrites, the kick adds. It is NOT a boundary condition and
   NOT a mass inflow. Particle count is fixed at load (:126) and no
   particle is created or destroyed during a run. Velocity also feeds
   term_advective at :150, but the acoustic term dominates at every point
   in the sweep, so substeps and dt are identical across the whole velocity
   sweep.

3. The vehicle is a free rigid body, registered at :129-131 and never
   written again. Every velocity and position write in the driver is sliced
   to the water range (:161, :183-186, :196). The only constraints are the
   floor plane at friction 0.55 and the four slip walls at friction 0.0
   (:132-137). Gravity is confirmed 9.81 m/s^2 in -z, corrected 2026-08-07
   per docs/OPTION_A_SESSION1_FINDINGS.md F-2, against freshly vendored
   solver core at third_party/mpm-engine-544c93dd-solver-core/.
   core/solver.py:167-169 hardcodes g=[0,0,-9.81] inside
   Solver.set_material() unconditionally, not a library default,
   this wrapper's own hardcoded value. sim_standing.py:127 calls
   set_material(newtonian(...)) and newtonian() carries no g key to
   override it. All 17 gated runs ran at exactly 9.81 m/s^2.
   gates_all_runs.py:12 (G=9.81) matches; failure_modes.py:14
   (G=9.80665) is a 0.034 percent fork, numerically immaterial.

4. inertia_kg_m2, cg_height_m and ssf in vehicle_params.py never reach the
   solver. Only mass does, via vehicle_density = vehicle_mass /
   solid_volume at sim_standing.py:92-94. Inertia and CG are whatever the
   solidified particle cloud implies. Do not claim NHTSA-measured inertia
   or a measured CG height is in effect in any gated run.

5. A grid convergence study exists: g48, g64 and g96 at three masses, depth
   and velocity held fixed, nominal depth identical at 0.2944294 m on all
   three grids. It is non-monotone and unconverged. final_disp_mag_m for
   1100 kg moves +87.8 percent from g48 to g64 then -59.2 percent from g64
   to g96; 1609 kg moves +22.3 then -50.3. The binary verdict is
   grid-invariant, all nine are NO-FORD. Cite the verdict, never the
   displacement magnitude. The same run also carries two disagreeing
   displacement measures, summary.json final_disp_mag_m 0.658537 against
   rollout.npz 0.637019 for g64_m1100, a 3.4 percent gap recorded at
   gates_both_scenarios.py:71-72.

6. No gate is a physics validation. Every gate is a self-consistency or
   numerical-containment check. G-3 at gates.py:80-83 compares against
   RHO_REF = 310.49 at gates.py:13, which is derived from the same
   pipeline, so it cannot fail for a reason external to the code. G-6, P-4
   and P-5 print with no pass criterion at all. The L1 versus L2 agreement
   line at gates.py:197-198 emits AGREE or DIVERGE and gates nothing.
   gates.py:195-196 itself records that DRIFT_THRESHOLD has no
   peer-reviewed source.

7. Seven of the 17 runs fail gate P-2, max water fraction inside the
   vehicle bounding box, limit 0.10 at gates.py:146-148. The failure rate
   rises monotonically across the whole velocity sweep, 7.99 percent at
   0.5 m/s to 15.88 percent at 3.0 m/s. Failing runs are g48_m1100,
   g64_m1100, sweepD_g64_d0p35, sweepD_g64_d0p45, sweepV_g64_v2p0,
   sweepV_g64_v2p5, sweepV_g64_v3p0. All three g48 runs also fail P-3 with
   a negative z rise near -0.05 m, the hull sank into the floor plane.

8. renders/yaris_render_s1/gates_results.json holds 3 dry_start records
   from sim_dump.py and is NOT a 17-run store. It also stores no pass or
   fail field, the gate verdicts exist only in gates.py stdout, which is
   not persisted. The 17-run stores are
   renders/yaris_render_s1/gates_results_all_runs.json, which holds 20
   records, the 17 plus the 3 dry_start, and data/all_runs_inventory.csv,
   which holds exactly the 17.

9. Three incompatible vehicle densities are live in the repo at once:
   115.7 at simulation/can_it_ford_L2_mpm.py:27, 310.49 at
   renders/yaris_render_s1/gates.py:13, and 579.06 at
   simulation/can_it_ford_L2.py:44, can_it_ford_L2_mpm_ytest.py:45 and
   designsafe-staging/scripts/can_it_ford_L2.py:40. The 17 gated runs
   realise a fourth set, 302.55 to 663.58, all of them above the
   100 to 300 band, and gates_both_scenarios.py:59 returns
   density_plausible False for every run it evaluates.

10. 1609 kg and 2337 kg have no source in vehicle_params.py. The nearest
    classes there are midsize_suv at 1990.0 (vehicle_params.py:112) and
    light_pickup at 2300.0 (:134). Two of the three masses in the mass
    sweep are therefore unsourced. Do not describe the mass sweep as
    spanning cited vehicle classes.

11. VERIFIED LIVE ON VISTA AUGUST 4 2026, see $WORK/RECIRC_CHANNEL_V1.md.
    NOT re-verifiable by file read from the Mac. Genesis version on
    Vista is 1.1.1, not 1.2.0. module load tacc-apptainer fails over
    non-interactive ssh, use /opt/apps/tacc-apptainer/1.4.1/bin/apptainer
    directly.

12. CORRECTED 2026-08-07, see register D6a-D6i. Output is NO LONGER
    binary only. simulation/failure_modes.py has been run on all 17
    runs; the canonical stores are data/failure_modes_by_run_classified.csv
    and data/failure_modes_by_run.json, both regenerated by
    analysis/classify_failure_modes.py. Verdicts are 16 SLIDE and 1
    STUCK (sweepV_g64_v0p5). The earlier text here, "never wired into
    the 17-run pipeline," went stale on 2026-08-05. Do not restate it.
    Three traps survive. (a) triggered_* is the verdict, ratio_* is
    peak magnitude; they disagree, and filtering on ratio >= 1 reports
    13 topples that never happened. (b) STUCK is the none-sustained
    case, not a fourth mode scored on its own scale; its winning-mode
    columns are empty by design, not missing. (c) metrics.csv
    pitch_deg/roll_deg are vehicle-body-sense, not raw Euler
    (vehicle_live.py:295-300 swaps two of them), but the classifier
    reads neither, so the gimbal singularity cannot reach a verdict.
    renders/yaris_render_s1/failure_modes_result.json is still
    condemned: 3 entries, no run identifier, written by no script.
    Its two miscitations were repointed by 841d666. The defect that
    survived that repoint was the word "independently," fixed
    2026-08-07: the classifier reads the same metrics.csv the tables
    were built from, so it can never be independent confirmation.

13. DRIFT_THRESHOLD 0.05 m is declared as a literal in 16 places under
    four names, DRIFT_THRESHOLD, DRIFT_THRESHOLD_M, DRIFT_M and
    THRESHOLD, plus two more literals in failure_modes.py:46 and :48.
    There is no single definition and no peer-reviewed source.

14. EXT_REF at gates.py:12 differs from bbox_m at vehicle_params.py:89
    by 3.3 percent in height and 2.7 percent in width, both larger than
    gate G-1's own 2 percent tolerance.

15. WITHDRAWN 2026-08-07. This item used to read "Gravity is UNKNOWN in
    the solver but 9.81 is assumed in post-processing. State both
    separately, never merge them." That instruction existed only
    because the solver value was unknown, and it no longer is. Use
    9.81. See item 3 and register A2 for the primary source and the
    two post-processing constants.

    SELF-CORRECTION, same day, 2026-08-07. An earlier version of this
    item said the 9.80665 at failure_modes.py:14 "has never influenced
    a gated result, because that script was never wired into the
    17-run pipeline." That is FALSE and was written from the stale
    pre-2026-08-05 text of item 12. G IS used, at failure_modes.py:170
    (surge_accel_g) and :174 (weight_n), and the classifier HAS since
    been run on all 17 runs (item 12, register D6 and D6b), so 9.80665
    fed the published 16 SLIDE / 1 STUCK verdicts. The fork is 0.034
    percent and no verdict is known to turn on it, but that has NOT
    been tested. To close: set failure_modes.py:14 to 9.81, re-run
    analysis/classify_failure_modes.py, and confirm the verdicts are
    byte-identical. Do not close it by assertion.

16. gates.py:16-31 forks the AR&R table and L1_verdict instead of
    importing from vehicle_params, while gates_all_runs.py:10 and
    gates_both_scenarios.py:10 import. Values agree today. Fork risk.

### AUGUST 5 2026 LITERATURE REVIEW

Findings from the literature review of August 5 2026. These are
external-source claims, not repo file reads, with the one exception
noted in L-3. Verify each citation against its primary source before
it enters the paper.

L-1. The AR&R and Shand et al. thresholds describe a STATIONARY
     vehicle subjected to flow. That is stated in the primary
     sources, not inferred from them. The tank scenario is therefore
     the correct match for L1. Do not write it up as a scenario
     mismatch. The word "ford" in the project title is what
     mismatches, not the simulation setup.

L-2. The 3.0 m/s velocity cap is administrative. It was set to stay
     below human-stability curves, not derived from vehicle data. Do
     not present it as a vehicle-derived limit.

L-3. No accepted particle force-convergence criterion exists for MPM.
     The rules of thumb are roughly 10 particles per flow depth. The
     g64 baseline has 4 particle layers and 2 grid cells. Verified
     live against data/all_runs_inventory.csv on 2026-08-05:
     water_layers is 4 and realized_depth_m / dx is
     0.2944294473039918 / 0.1472147236519959, exactly 2.000. State
     this as a limitation, not as a converged resolution.

L-4. Coarse resolution usually OVER-predicts peak hydrodynamic force.
     Over-threshold NO-FORD verdicts are therefore conservative.

L-5. Steffen, Kirby and Berzins 2008 is the citable mechanism for MPM
     losing convergence under grid refinement at fixed
     particles-per-cell. Cite it for the g48/g64/g96 non-monotonicity
     recorded in item 5 above.

L-6. The simplest-sufficient-abstraction principle is established
     prior art: VVUQ adequacy-for-purpose, ASME V&V 40, goal-oriented
     error estimation, and Blackwell sufficiency. Do not claim
     novelty for it.

L-7. arXiv 2607.00673 (Low, Hsiao, Li, Thorpe, Topcu, Kumar, July
     2026) covers reconstruction plus MPM plus route feasibility
     without external validation. The novelty for this project is the
     validation step, not the pipeline.

L-8. Engine decision: do not switch. DualSPHysics ships x86-only
     static libraries, a hard aarch64 blocker on GH200.

## git filter-repo standing note
Moved to the `git-history-rewrite` skill (.claude/skills/git-history-rewrite/).
Load it before any filter-repo pass or force-push of rewritten history.

## File provenance, do not cite anything not on this list without checking it live

CANONICAL:
- CLAUDE.md (this file, project root) — Multi-Pane Standing Rules
- vehicle_params.py — mass_kg: 1100.0
- vehicle_geometry_research/yaris_coarse_v1l_watertight.ply — canonical Yaris mesh

DEPRECATED, do not read or cite. The deprecated files are also blocked
mechanically by the Read deny rules in .claude/settings.json, so this list
covers only what those rules do NOT block:
- data/track1_sweep_v2/ — superseded box-proxy sweep (1390 kg box, 4.7352 m3
  solid volume vs the real hull's 3.542739 m3). Not archived, because
  analysis/gp_surrogate.py and analysis/build_poster_phase_space.py still read
  it and .gitignore lines 17-18 explicitly un-ignore it. Do not source a paper
  figure or a density number from it; use data/all_runs_inventory.csv instead.

## Nested ./can-it-ford/ duplicate directory, do not read data from it

There is a second copy of this project nested at ./can-it-ford/ inside the repo
root. It is NOT a synced mirror. Verified live 2026-07-29 by filecmp: paper/
conference_101719.tex and paper/can_it_ford_references_IEEE.bib are byte-identical
between root and nested, but data/scenario_sweep.csv, vehicle_params.py and
scripts/ford_sweep_driver.py all DIFFER. Root is canonical for every one of them.
Always confirm pwd is /Users/josie/can-it-ford, not the nested copy, before
reading a parameter or a verdict count, and exclude ./can-it-ford/ from repo-wide
greps or you will get two conflicting answers and no way to tell which is live.

## AUGUST 5 2026 RESEARCH INTEGRATION V2

- Query reframed, title stays Can It Ford, question is whether it is
  safe for a specific vehicle to attempt a crossing, answered via
  stationary-vehicle stability, verdict is necessary not sufficient.
- NVIDIA Warp is the only engine confirmed for aarch64 plus Hopper,
  do not switch engines.
- Kumar et al 2019 Computers and Fluids published the MPM in/outflow
  boundary conditions this project needs.
- No flood-vehicle study shows resolution moving the stability
  threshold, never cite one as proof that it does.
- Artificial sound speed can qualitatively flip a rigid-body outcome,
  Isik and He 2022, never swept here.
- Unsteady flow raises drag 40 to 50 percent, Azhar 2026.

## Corrections authority, 2026-08-06

docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md is the sole authority for
any factual claim it covers: solver identity, gravity, force accessors,
resolution, thresholds, citations, repo state. It is T1, read from live
source.

Demoted to historical, cite only with a date and never as current:
  docs/VERIFIED_FACTS_LEDGER_july24.md and its _GRIDAWARE sibling
  ~/can-it-ford-audit/2026-08-04/CONFIRMED_FACTS_LEDGER.md
  docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md
Where any of them conflicts with the register, the register wins.


## MacOS-MCP screenshot permission, 2026-08-06

MacOS-MCP `Snapshot` with `use_vision=true` fails with `cannot identify
image file`. Cause: macOS Screen Recording permission not granted to
Claude Desktop / its helper process. Fix: System Settings > Privacy &
Security > Screen Recording > enable Claude, then relaunch the app.
`Snapshot` without vision (accessibility tree: open apps, windows,
interactive elements) works without this permission and needed no fix.
