## Multi-Pane Standing Rules

These apply to every pane in every session automatically, do not
restate them in chat prompts.

- Never fabricate a command, parameter, or claim. Pull from actual
  file content, actual output, or actual verified search results.
  This includes a prior claim from Claude itself, verify independently
  rather than trust at face value.
- `grep` IN THIS ENVIRONMENT IS NOT `grep`. Confirmed live 2026-08-07
  by `declare -f grep`: it is a shell function wrapping ugrep with
  `--ignore-files`, so it SKIPS EVERY GITIGNORED PATH. `data/*` and a
  `renders/*` pair are among the rules, so a
  repo-wide `grep -rn "pattern" .` silently omits most of
  renders/yaris_render_s1/ and most of data/. An absent hit is NOT
  evidence of absence.
  THE OLD "5 hits from `.` and 7 when renders/ was named" MEASUREMENT
  IS WITHDRAWN, 2026-08-12. It never named the pattern, so nobody can
  re-derive it, and the 2026-08-12 carve-out invalidated its premise
  anyway: the shell `grep` now reaches 22 previously-hidden .py files,
  so the gap it measured no longer exists in that form. Re-measure with
  a named pattern before quoting any figure here. For any
  inventory or audit claim, use `/usr/bin/grep -rn`, or name renders/
  and data/ explicitly, and exclude ./third_party/ and
  ./.claude/worktrees/.
  LINE NUMBERS UPDATED 2026-08-12, and the rule they describe CHANGED.
  This clause used to read "`.gitignore:14` is `renders/`". The blanket
  `renders/` was replaced that day by a walk-down carve-out, because it
  was also hiding 24 SOURCE scripts, among them sim_standing.py and
  vehicle_live.py, which this file cites by file:line as the primary
  source for A1, A2, A5 and F5 and which implement the Contribution 1
  code. Those 24 .py files are now UN-IGNORED, so the shell `grep`
  reaches them and the H0 blind spot no longer covers them. Generated
  output under renders/ is still ignored, so the H0 warning still
  applies to metrics.csv, frames and every other artifact.
  DO NOT READ "un-ignored" AS "tracked". Corrected 2026-08-12 after an
  independent check caught this exact conflation here: only 2 of the 24
  are tracked, sim_standing.py and vehicle_live.py, committed in
  00b735c. The other 22, including gates.py, gates_all_runs.py and
  gates_both_scenarios.py, are visible to grep but still UNTRACKED and
  still have no commit history. Verify with
  `git ls-files --cached -- renders/yaris_render_s1/` before citing any
  of them as having provenance.
  The carve-out is also TOP-LEVEL ONLY. A second copy of the driver
  exists at renders/yaris_render_s1/_incoming/sim_standing.py and is
  STILL ignored by the `renders/yaris_render_s1/*` rule, which
  `git check-ignore -v` will locate for you; do not cite its line
  number, see the .gitignore note below. "sim_standing.py is no longer
  hidden" is true only of the top-level copy, and register D4a records
  `_incoming/` as the canonical per-run tree, so check which copy you
  are reading.
  ALSO CORRECTED 2026-08-12, verified live: `./.claude/worktrees/` holds
  2 directories, not 27, so the "multiplies every hit ~20x" figure is
  stale; re-measure before quoting it. And `./can-it-ford/` no longer
  exists, so excluding it is now a no-op, see the section below.
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
  explicit sequencing. ACTIVE BREACH 2026-08-07: two Claude Code
  sessions edited this working tree simultaneously and one committed
  the other's uncommitted edits inside 0797b08 and 3470ff9 without
  either knowing. Read docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md
  before touching scripts/check_claims.py, CLAUDE.md or the register.
  If you see edits appear in a file you did not write, the default
  assumption is ANOTHER SESSION, not a linter and not the user.
- Never run `git add -A`, `git add .`, or `git commit -a` in this repo.
  Stage explicit paths. A shared working tree means -A captures another
  session's in-progress work and commits it unreviewed under your
  message. This is not hypothetical, it happened on 2026-08-07.
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

   EXTENDED 2026-08-08: AND DO NOT WIRE THEM. The absence is correct, not a
   gap. Three reasons, all verified live against source and measured rollout
   data, full working in docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md
   section 1, guard enforced at .claude/checks/params_check.py
   check_inertia_wired():
   (a) It is not measured. compact_sedan's {463.0, 1893.0, 1960.0} reproduces
       EXACTLY from box_inertia(1100, 4.30, 1.70, 1.47), a solid rectangular
       box. No measured Yaris tensor exists anywhere: SAE 1999-01-1336 ends
       Nov 1998. vehicle_params.py:15-19 already says the compact_sedan
       cg/inertia/ssf are estimates.
   (b) The solver already computes a better one, from the real hull particle
       cloud at kernels/mpm_solver_warp.py:859-871. Measured from g64_m1100's
       8905 rigid particles about the true centroid: Ixx 1501.5, Iyy 395.0,
       Izz 1685.4, against the box's axis-corrected 1893.0, 463.0, 1959.8. The
       box overstates every principal moment by +16.3 to +26.1 percent, which
       is geometrically forced: the hull fills only 33.2 percent of its own
       bounding box.
   (c) The axes are transposed. vehicle_params documents (L,W,H) as (x,y,z),
       but the gated scene puts the hull's LONG AXIS ON Y (measured extents
       1.7078, 4.2014, 1.4853). A naive write gives Ixx -69.2 percent and
       Iyy +379.2 percent against the hull truth.
   Free result worth reporting instead: the cloud CG sits 0.6312 m above the
   floor, already below bbox mid-height 0.7427 m and 23.8 percent above the
   0.51 m estimate. A too-high CG biases TOWARD topple, and the 17 runs show
   zero topples, so the no-topple result is conservative.

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

13. DRIFT_THRESHOLD 0.05 m is declared as a literal under FIVE names.
    There is no single definition and no peer-reviewed source.
    FIVE NAMES is settled. THE TOTAL IS NOT, and the number is
    scope-sensitive, so never quote a total without its scope.

    UPDATED 2026-08-12, superseding both this item's earlier "16 places
    under four names" and register D7's "24 places". Full enumeration,
    every site listed, reproduced live 2026-08-12 by a Python walk
    (see below for why not grep):

      DRIFT_THRESHOLD_M  5
      L2_DRIFT_M         7
      DRIFT_THRESHOLD    8 in scope, 9 if archive/ is counted
      DRIFT_M            1
      THRESHOLD          1
      TOTAL             22 in scope, 23 with archive/

    Scope, matching D7's own stated scope: renders/ and data/ included
    explicitly; .git/, third_party/, __pycache__/, archive/, _archive/,
    session_archive/, .claude/worktrees/, the nested ./can-it-ford/ and
    every .bak* excluded; assignments of the literal only, not prose.

    RETRACTION 2026-08-12, SAME DAY, SECOND PASS. An earlier version of
    this item claimed "D7's THRESHOLD 2 cannot be reproduced" and "D7's
    per-name split does not reproduce". BOTH OF THOSE WERE WRONG and are
    withdrawn. D7's 24 is CORRECT. It reproduces exactly, and the
    refutation was itself an assertion nobody re-derived, which is the
    very failure this item is about.

    What the refutation missed is analysis/gp_surrogate.py:14:

      THRESHOLD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05

    That is a genuine fifth-name declaration of the 0.05 default. It is
    CLI-overridable rather than a hard-coded constant, so a strict
    `NAME = 0.05` regex does not match it, which is exactly why a
    strict recount "could not find" D7's second THRESHOLD. Verified
    live 2026-08-12 by three independent methods that now agree: a
    /usr/bin/grep loop, a subagent Python re walk, and
    .claude/checks/count_claims_check.py.

    THERE ARE TWO INDEPENDENT BINARY CHOICES, NOT ONE. That is the real
    finding, and it is why this count has moved three times:
      1. include the archive/ copy, or honour D7's stated exclusion
      2. count only bare literals, or also count the gp_surrogate default
    Two choices give FOUR totals, and 23 is reachable by TWO different
    routes, so two counts can appear to agree while counting different
    things:

      22   bare literals only, archive/ excluded
      23   bare literals only, archive/ included
      23   plus the gp_surrogate default, archive/ excluded
      24   plus the gp_surrogate default, archive/ included   <- D7

    Every one of those is defensible WITH its scope stated. A bare
    number is what is wrong, not any particular value. Do not cite 16.
    Do not cite any total without saying which of the two choices you
    made. `.claude/checks/count_claims_check.py` now enforces this and
    accepts 22, 23 or 24.

    SEPARATE, still true, and NOT part of any total above:
    simulation/can_it_ford_mu_sweep.py.DO_NOT_RUN:60 is code, carries
    DRIFT_THRESHOLD = 0.05, and is deliberately suffixed so no *.py glob
    will ever match it. Count it as +1 on whichever reading you use, and
    say so.

    Prose mentions, correctly excluded from every count above: 122
    further occurrences in .md files, heavily concentrated in
    _inbox/LIVE_SESSION_LOG.md, docs/CONTEXT_CENSUS_2026-08-07.md and
    the duplicated deliverables/for_kumar trees. Plus 17 more in
    .claude/worktrees/ctx-census/ and docs/session_notes/archive/.
    None of those is a declaration site. Do not let a future count sweep
    them in.

    L2_DRIFT_M is a FIFTH name that neither this item nor D7 originally
    named, and it is the second most common at 7 sites. Six of those
    seven are POSTER FIGURE GENERATORS, so the name missing from both
    inventories is the one closest to a formal deliverable. That part of
    D7 stands.

    TOOLING WARNING, this is why the counts kept moving. Three separate
    commands gave three answers on the same tree. A `^`-anchored grep
    missed indented assignments; an ERE `(^|[^A-Za-z0-9_])THRESHOLD`
    form returned ZERO on a line Python matched; and the shell `grep`
    function skips gitignored paths entirely (H0). For any count that
    will be published, enumerate every site with a Python `re` walk and
    print the paths, so the number can be audited instead of trusted.

    CORRECTED 2026-08-07: failure_modes.py carries THREE 0.05
    literals, not two. Verified live by /usr/bin/grep:
      :46 slide_m         = 0.05   metres
      :47 slide_speed_ms  = 0.05   METRES PER SECOND
      :48 float_m         = 0.05   metres
    This item previously named only :46 and :48. :47 is a SPEED that
    happens to share the numeral. A naive find-and-replace across
    "0.05" during any deduplication would silently convert a speed
    into a distance and change SLIDE verdicts, which are the 16 of 17
    published outcomes. Deduplicate by NAME and UNIT, never by value.

14. EXT_REF at gates.py:12 differs from bbox_m at vehicle_params.py:89
    by 3.3 percent in height and 2.7 percent in width, both larger than
    gate G-1's own 2 percent tolerance.

15. PARTLY WITHDRAWN 2026-08-07. This item used to read "Gravity is
    UNKNOWN in the solver but 9.81 is assumed in post-processing. State
    both separately, never merge them." The UNKNOWN half is withdrawn:
    the solver value is 9.81 and is not in question, see item 3 and
    register A2 for the primary source.
    The OTHER half was NOT stale and is retained: post-processing is
    forked. 9.80665 at simulation/failure_modes.py:14 and
    analysis/viability_dashboard_scaffold.py:11, against 9.81 at five
    sites including gates_all_runs.py:12. TWO sites at 9.80665, not
    one. Full inventory and the reason this nearly vanished is
    register A6. The original withdrawal note pointed at register A2
    for these constants and A2 did not contain them; that dangling
    pointer is why A6 exists. Because the classifier has now run on all
    17 runs, 9.80665 fed the published verdicts, so this fork is live,
    not cosmetic. Never write that it has not influenced a gated result.

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
  it and .gitignore explicitly un-ignores it with a `!data/track1_sweep_v2/` pair.
  DO NOT CITE A LINE NUMBER FOR .gitignore. Re-derive it every time:
  `/usr/bin/grep -n track1_sweep_v2 .gitignore`. This clause said ":17-18" until
  2026-08-12, then ":32-33", and both went stale within one session because two
  separate edits inserted lines above them. .gitignore line numbers have now been
  wrong three times in one day; the file is edited too often to cite positionally.
  Do not source a paper
  figure or a density number from it; use data/all_runs_inventory.csv instead.

## Nested ./can-it-ford/ duplicate directory, GONE as of 2026-08-12

**STATUS CHANGE, verified live 2026-08-12 by `ls -d /Users/josie/can-it-ford/can-it-ford`:
the nested duplicate NO LONGER EXISTS.** Every exclusion of `./can-it-ford/` in this
file, in skill files and in audit scripts is now a no-op rather than a load-bearing
guard. Do not conclude from a passing grep that the duplicate was handled; there is
nothing left to handle. The section below is retained as history, because the hazard
returns the moment anyone re-clones into the repo root, and because several committed
scripts still carry the exclusion. Do not cite it as a live hazard without re-running
that `ls` first.

### Historical, when the duplicate existed

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
- The MPM in/outflow boundary conditions this project needs are Zhao,
  Bolognin, Liang, Rohe and Vardon 2019, Computers and Fluids 179,
  27-33, DOI 10.1016/j.compfluid.2018.10.007, implemented in Anura3D.
  NOT Kumar. Implementing this in warpmpm is a translation, not a
  port. Corrected 2026-08-07, see register item 8 and
  docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md.
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

## AUGUST 8 2026 LITERATURE ADDENDUM

Added 2026-08-08 from two further Undermind reviews. Filed as a new section
because the dispatch that commissioned these asked for addenda under "Part
2.4" and "Part 4.3", and **neither exists**: this file has no numbered Part
headers at all, verified by a full live read on 2026-08-08. Nothing existing
was rewritten or deleted. Citation bank and full working:
docs/LITERATURE_CI_GATES_2026-08-08.md.

These are external-source claims, not repo file reads, except where an item
says otherwise. Verify each citation against its primary source before it
enters the paper. None has been checked against a primary record yet.

A-1. COUPLING ARCHITECTURE REFRAME. Not previously covered anywhere: a live
     search of this file and the register on 2026-08-08 returned zero hits
     for CPIC, material-8, Hu 2018, Pazouki, or job 894731. The 17 canonical
     runs use the material-8 free-rigid path, a mass-weighted grid velocity
     average with no force accumulator. Material 8 IS the rigid material,
     verified live against the pinned solver, not on the citation's word:
     kernels/mpm_utils.py:1366 is commented "Rigid body kernels
     (material == 8)", :1090 reads "elif mat == 7 or mat == 8: # stationary
     / rigid, no deformation", and kernels/mpm_solver_warp.py:853 selects
     the body's particles with np.where((mat_np == 8) & (rid_np == b)).
     Hu et al 2018, ACM TOG, doi:10.1145/3197517.3201293 (Compatible
     Particle-In-Cell) and Pazouki, Jayakumar and Negrut 2016 describe real
     two-way MPM/SPH rigid coupling as requiring accumulated contact force,
     not velocity averaging. The SDF collider path matches that architecture
     and is the validated one. This reclassifies the coupling defect from an
     unexplained numerical patch to a documented architecture choice with a
     literature-backed alternative. It does NOT change any of the 17 runs'
     verdicts, and per REGIME_LADDER_DISPATCH_2026-08-07.md:28-33 it does
     not clear them either, for three reasons: the 17 runs use restitution
     0.05 on floor and walls where C1 used 0.0 everywhere, 2-grid-cell depth
     resolution, and self-consistency is not validation.

A-2. THE SDF ERROR RANGE IS 7.3 TO 7.7 PERCENT, NOT 1.6 TO 7.7. The
     commissioning text gave "1.6 to 7.7 percent" and that is wrong. On-disk
     numbers from c1sdf_894731.out, transcribed at
     docs/CONTEXT_CENSUS_2026-08-07.md:1043-1053 against
     F_buoy_analytic = 31298.444315169316, are err_steady_vs_analytic_pct
     of -7.6682435536478435 (c1sdf_sdf_g64) and +7.280446501465449
     (c1sdf_sdf_g96). docs/REGIME_LADDER_DISPATCH_2026-08-07.md:22-23
     independently states "within 7.3-7.7%". The stray 1.6 is a conflation
     with the FREE-RIGID late-window fit, "+1.5% and +0.7-0.8% of analytic
     buoyant acceleration at g64/g96", which measures the path being
     criticised, not the validated one. Never merge the two ranges.

A-3. CLASS-SPECIFIC GEOMETRY, NOT MASS ALONE. Smith, Modra and Felder 2019;
     Martinez-Gomariz et al 2017; Arrighi et al 2015 jointly establish that
     buoyancy, drag and lift lever arms, and sliding/float/roll thresholds
     depend on displaced volume, underbody shape, wheelbase, track and CoM,
     not mass alone. Allen et al 2003 SAE 2003-01-0966 gives a citable
     regression method for provisional CoM and inertia by class, flagged in
     that paper itself as provisional, NOT validation. Partial overlap:
     Smith Modra Felder and Arrighi 2015 are already in the register at
     lines 226, 189 and 270 in adjacent contexts, so they are not
     independent support for the geometry framing. Martinez-Gomariz 2017 and
     Allen 2003 are new. This compounds item 10 above: two of the three
     masses in the sweep are unsourced, and the geometry that actually
     governs the thresholds is not gated at all.

A-4. WATERTIGHTNESS, WITH A STANDING TENSION. Kramer, Terheiden and
     Wieprecht 2016, doi:10.1016/J.IJDRR.2016.04.003, and Azhar, Bui and
     Pauwels 2026, doi:10.1111/jfr3.70181, independently confirm
     watertightness assumptions materially shift flotation depth. Neither is
     new to the project: register line 228 already carries the Kramer 2016
     prototype finding, and line 367 of this file already carries Azhar 2026
     for a different claim (unsteady flow raising drag 40 to 50 percent).
     The two DOIs and the pairing are what is new. Do NOT pair these with
     the solidify_watertight fix until register E2 is resolved: E2 at line
     183 records that FloodScene vehicle.py:162 samples the mesh down to
     60,000 surface points before solidifying, so watertightness does not
     propagate through the pipeline, and the pairing would imply a property
     the pipeline does not preserve.

## AUGUST 8 2026 CLOSED ITEMS AND GATE INVENTORY

Every SHA below was verified live with git log / git show on 2026-08-08, not
carried from a summary. PRJ-3702 is deliberately absent: zero hits in docs/
and in this file, confirmed twice, so there was no open item to remove.

CLOSED
- Rigid-mass citation :851-853 -> :856, commit 35b7ed0. The mass sum is
  kernels/mpm_solver_warp.py:856; 851 and 852 are the np.zeros allocations
  and 853 is the loop header, so the old range cited allocation plus a loop
  header rather than the sum itself. Three sites fixed. Stamped artifacts
  under data/coupling_validation/ still carry the old range by design.
- Failure-mode classifier has run on all 17 canonical runs, commit fae3388.
  841d666 then tracked data/failure_modes_by_run.json and
  data/all_runs_inventory.csv, both silently gitignored until then.
- four_rung_ladder.md and _GRIDAWARE.md no longer cite
  failure_modes_result.json as independent confirmation, commit 841d666.
  Verified live: both now read the claim as a measurement, not a confirmation.
- simulation/validate_coupling_force.py is committed. TWO SHAs, do not
  conflate: 541d832 first ADDED the file, 057b3e9 landed the C1-SDF/C3
  harness content including the working C3 nan-guard.
- Warp MPM figure label, commit b844118. Commit 7390168 makes the IDENTICAL
  change on branch claude/verify-execute-code-changes-d89fd8 and is not an
  ancestor of main, so cherry-picking it returns empty, which is success and
  not a conflict. Do not re-attempt it.

GATE INVENTORY, do not rebuild these from scratch
.claude/checks/params_check.py already runs four literature-cited gate
categories, landed by aa754dc (NOT 720d1e2, which is a later inertia-re-wire
block): lit:geometry_bbox, lit:sound_speed_cfl, lit:resolution_convergence_gci
and lit:manifest_provenance. TRAP: only three exist as literal strings.
lit:resolution_convergence_gci is assembled at runtime by
params_check.py:259 from the gate= argument at :417, so grep -F for it
returns nothing and a naive audit concludes the gate is missing. It is not.
Run the script and read its output instead of grepping for the tag.
SECOND TRAP: four is the count of literature-cited TAGS, not of gates. Six
lit: tags exist (also lit:floor_restitution and lit:mass_inertia_cog), and
the four gate= categories are a DIFFERENT four: floor_restitution,
geometry_bbox, mass_inertia_cog, resolution_convergence_gci. Grepping gate=
returns names that do not match this list; that is expected, not drift.
Line numbers verified live 2026-08-08 by running the script.

STILL OPEN, not closed
- The Overleaf token is off local disk but NOT revoked. ~/can-it-ford-paper
  was deleted 2026-08-08 after confirming local main and overleaf/main were
  both 92ce4de, nothing ahead of the remote, no stashes, so Overleaf retained
  all 5 commits. Verified the same day: no .git/config under ~ contains an
  olp_ string, and this repo's own overleaf remote URL carries no credential.
  Two consequences: a push to overleaf now PROMPTS for credentials, so a
  fresh Overleaf Git authentication token is needed before the next push; and
  the old token stays valid server-side until rotated in Overleaf account
  settings.

## STANDING OPERATING PROTOCOL, adopted 2026-08-13

Applies to every session in this repo on every machine. Adopted from the three
RTFD dispatches of 2026-08-13, which repeated it verbatim; recorded once here so
no future dispatch has to restate it. It does not replace the Multi-Pane Standing
Rules above, it sits under them.

BEFORE STARTING: check `git log`, `.remember/` files, and the research citations
you were given, in that order. Do not duplicate work already done elsewhere.
The point is not ceremony. On 2026-08-13 a dispatch asked for a composite whose
premise had been retracted hours earlier on another branch, and another asked for
a backfill that had already run.

WHEN YOU HIT AN OBSTACLE: try a fix. If it fails, try a second GENUINELY DIFFERENT
approach, not a variation. Before concluding you are stuck, check whether a
connector or subagent resolves it:
  - DeepWiki, for how a library or repo actually behaves. Its answer is a
    hypothesis to verify against source, never a fact.
  - The physics-skeptic subagent, before finalising any claim involving a
    percentage, force, verdict count or distance. If unavailable, say so
    explicitly and mark the claim unreviewed. Never fake the review.
  - Wolfram, for any physical parameter, unit conversion or equation.
  - Scite, for any citation, DOI or threshold before it is written as settled.
  - `.claude/checks/register_integrity.py` before any commit.

PREFER A LABELLED, REVERSIBLE ASSUMPTION OVER STOPPING. State it in the commit
message or write-up so it can be revisited without re-deriving it.

TAG EVERY FACTUAL CLAIM BY SOURCE: read directly, recalled from context, or
inferred. Tag every solver claim by ENGINE. Never state a number from memory when
you could check it live.

KEEP WORKING on everything else in scope even if one item is blocked.

FLAG, rather than silently proceed past, only these four:
  1. About to discard, overwrite or force-push over work you did not create and
     cannot verify is safe to lose.
  2. Two independently-reported results genuinely disagree about the same
     physical quantity, and resolving it needs a judgment call, not more data.
     "Genuinely" excludes one result read twice: see register J18.
  3. About to edit a canonical file outside your declared scope.
  4. A hard stop: real financial cost, an exposed credential, a destructive or
     irreversible action, or anything matching the standing hard rules.
Write the flag to a NAMED FILE, not an inline comment, keep working on everything
else, and do not treat the flag as ending the session.

FALSIFIABLE OVER PLAUSIBLE: a no-forcing control, a held-fixed comparison, a
second seed. Write a result up the same way whether it confirms or overturns
something already published.

BEFORE ANY PUSH: confirm the target branch, stage EXPLICIT PATHS only, never a
blanket add, and confirm the push actually landed. A command exiting 0 is not
evidence the remote updated.

### Specifics verified live 2026-08-13, correcting things stated elsewhere

- **CLAUDE.md IS NOT SYNCED ACROSS MACHINES, despite the session-start banner
  saying "confirmed synced Mac/Vista/LS6/GitHub".** Measured by md5 on
  2026-08-13: Mac and `$SCRATCH/canitford_track1b/can-it-ford` on LS6 both
  `ef341c3e`, 676 lines; `$SCRATCH/can-it-ford` on LS6 is **49 lines**; Vista's
  `/work/11603/jcerrell0629/vista/can-it-ford` is **88 lines** and locally
  MODIFIED. Re-measure before believing any sync claim.
- **VISTA HAS 12 UNPUSHED COMMITS** on `main` (tip `4b38aa3`, a `realism_track:`
  series from `1e4c6d5` through `4b38aa3`), plus 5 modified tracked files and
  ~22 untracked, while sitting 173 behind `origin/main`. Any statement that
  "Vista made no commits to lose" is false. **Do not scp over that tree.**
- **THE "PHANTOM" DECLARATION IN VISTA'S LOCAL CLAUDE.md IS WRONG.** It says
  `docs/REMEDIATION_PLAN_AUDIT_2026-08-12.md` "never existed on disk or in git on
  any branch". It exists: 21,900 bytes on the Mac, committed in **`13187c0`**, and
  present in four working trees. The Vista session reached "never existed" from a
  clone 126 commits behind, where `git log --all` covers only fetched refs. The
  citation to it at the head of `analysis/run_provenance.py` is therefore SOUND.
  **A clone that is behind cannot prove a file never existed.**
- **`.claude/checks/count_claims_check.py` FALSE-BLOCKS FROM A WORKTREE.** From
  `.claude/worktrees/*` it reports 25 blocking defects and totals 16/17, because
  the declaration sites live in untracked and gitignored paths a worktree checkout
  does not carry. From `/Users/josie/can-it-ford` it reports **0 blocking
  defects** and 22/23/24, matching item 13. Always pass
  `--root /Users/josie/can-it-ford`.
- **NEVER HARDCODE AN idev NODE NAME.** It changes every allocation: `c307-006`
  was live at 17:28 on 2026-08-13 and gone by 17:52, replaced by `c305-006`. Read
  it from `squeue` at point of use.
- **PREFER LS6 FOR GPU WORK.** LS6 held 9,615 SUs on 2026-08-13 against Vista's
  651, both expiring 2026-09-30. Submit batch via `scripts/tacc_submit.sh`; do not
  propose idev. `sacct` shows jobs 3362340, 3362386 and 3362478 all ending
  TIMEOUT at 00:30:01 with nobody attached.
- **THE FORCE-COUPLED PATH HAS NO FLOOR FRICTION.**
  `simulation/realism/dynamic_body.py:216-221` is the whole floor treatment, a
  z-position clamp plus a normal-velocity clamp; `friction`, `tangent` and
  `coulomb` appear zero times in that file. `floor_friction=0.55` acts only on the
  canonical path, at `renders/yaris_render_s1/sim_standing.py:210-211`. Do not
  describe the two tracks as combinable without new physics.
- **+0.035% IS NOT A BUOYANCY VALIDATION.** It is `100*a_z/g`, an identity forced
  by `dynamic_body.py:207`, verified to 1.4e-16 (commit `d8a479f`). The
  SDF-collider wrench validation is the real one, 7.3 to 7.7 percent. Never merge
  the two numbers or present 0.035 as agreement with Archimedes.
