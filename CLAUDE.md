## Multi-Pane Standing Rules

These apply to every pane in every session automatically, do not
restate them in chat prompts.

- DO NOT CITE THIS FILE POSITIONALLY. Quote the section heading and the
  sentence, never `CLAUDE.md:NNN`. Added 2026-08-18 after the rule proved
  itself inside one hour: a session was given corrected line numbers for two
  claims, this file was then edited, and the same two claims moved again, so
  three different line numbers existed for them within the hour. The edit that
  invalidated them was itself the commit fixing a STALE LINE NUMBER elsewhere
  in this file. Line numbers here are cited by other people verbatim and this
  file changes several times a night, so a positional citation is stale on
  arrival. The identical rule already existed for `.gitignore` below; it
  applies to this file for the same reason and more strongly.

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

- WHERE A NEW FINDING GOES, added 2026-08-19. This file is the CONSTITUTION:
  standing rules, hard prohibitions, and environment truth. It is NOT the place
  for a dated finding. A finding from one night goes in `docs/` and gets ONE
  line here only if it changes a standing rule. The reason is measured, not
  stylistic: a worktree carries the CLAUDE.md from ITS branch point, so every
  line added here is a line that silently diverges across every live worktree.
  On 2026-08-19 this file went from 906 to 983 lines in one evening and opened a
  77-line gap against nine live worktrees while they were reading it. A
  constitution that changes rarely is one a worktree freezes harmlessly. See
  docs/R9_COORDINATOR_AUDIT_2026-08-19.md for the measurement.

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
   gates_all_runs.py:12 (G=9.81) matches. failure_modes.py:14 was ALSO
   unified to 9.81 by commit e495b56 on 2026-08-12, so the 0.034 percent
   post-processing fork this line used to record is CLOSED. Corrected
   2026-08-18. The only surviving 9.80665 is
   analysis/viability_dashboard_scaffold.py:11, where G is assigned and
   never read anywhere in that file, so it is dead code and cannot reach
   a verdict.

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
    literals, not two. LINE NUMBERS RE-MEASURED 2026-08-18 and they
    had drifted by two; the ones this item carried from 2026-08-07
    were stale and had already propagated into a downstream analysis
    script that cited them verbatim. Live, by /usr/bin/sed:
      :48 slide_m         = 0.05   metres
      :49 slide_speed_ms  = 0.05   METRES PER SECOND
      :50 float_m         = 0.05   metres
      :52 sustain_frames  = 3      frames, the unsourced one
    The stale form read :46/:47/:48. A file:line citation in this
    document is copied into other people's work verbatim, so a
    two-line drift here becomes a wrong citation everywhere it lands.
    Re-measure before citing rather than trusting this block.
    This item previously named only two of them. slide_speed_ms is a
    SPEED that happens to share the numeral. A naive find-and-replace across
    "0.05" during any deduplication would silently convert a speed
    into a distance and change SLIDE verdicts, which are the 16 of 17
    published outcomes. Deduplicate by NAME and UNIT, never by value.

14. EXT_REF at gates.py:12 differs from bbox_m at vehicle_params.py:131
    by 3.3 percent in height and 2.7 percent in width, both larger than
    gate G-1's own 2 percent tolerance. LINE NUMBER CORRECTED 2026-08-18
    from :89, which is docstring prose and does not contain the value.
    Both percentages were re-derived live the same day and both still
    hold, so the citation was wrong, not the finding.

15. PARTLY WITHDRAWN 2026-08-07. This item used to read "Gravity is
    UNKNOWN in the solver but 9.81 is assumed in post-processing. State
    both separately, never merge them." The UNKNOWN half is withdrawn:
    the solver value is 9.81 and is not in question, see item 3 and
    register A2 for the primary source.
    The OTHER half was retained until 2026-08-18 and is now itself
    WITHDRAWN. It read: "post-processing is forked. 9.80665 at
    simulation/failure_modes.py:14 and
    analysis/viability_dashboard_scaffold.py:11, against 9.81 at five
    sites including gates_all_runs.py:12. TWO sites at 9.80665, not
    one." That was true when written and is now FALSE on both halves.
    Measured live 2026-08-18: failure_modes.py:14 reads G = 9.81,
    unified by e495b56, so exactly ONE 9.80665 site survives,
    analysis/viability_dashboard_scaffold.py:11, where G is assigned and
    never read. It is dead code and cannot reach a verdict. The "five
    9.81 sites" figure is stale too: a /usr/bin/grep for 9.81
    assignments in tracked Python, excluding third_party/,
    .claude/worktrees/, archive/ and __pycache__/, returns 14. State the
    scope with any such count, per item 13's rule.
    Full inventory and the reason this nearly vanished is register A6. The original withdrawal note pointed at register A2
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
    percent and no verdict is known to turn on it.
    CLOSED 2026-08-18, and not by assertion. Commit e495b56 on
    2026-08-12 set failure_modes.py:14 to 9.81 and regenerated
    data/failure_modes_by_run.json and
    data/failure_modes_by_run_classified.csv in the same commit. That
    CSV was re-counted live on 2026-08-18 and still reads 16 SLIDE /
    1 STUCK across 17 rows. That count is THRESHOLD-DEPENDENT and must
    never be quoted bare: it rests on failure_modes.py slide_m=0.05 m,
    slide_speed_ms=0.05 m/s and float_m=0.05 m, which are three literals
    sharing one numeral across two units, exactly the trap item 13
    records. analysis/probabilistic_verdict.py exists because a single
    deterministic cut is not defensible, and its own docstring cites the
    published finding that vehicle stability thresholds "vary over a
    relatively wide range". Quote the thresholds with the count. NOTE the close-out as originally written
    asked for byte-identical artifacts, and that is NOT what happened:
    e495b56 changed 34 lines of the CSV and 104 of the JSON, and its own
    message records "the one figure that moved". The VERDICTS are
    unchanged; the figures are not. Do not write that the artifacts came
    back byte-identical.

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

L-4. NO LONGER A FLAT RULE, amended 2026-08-20. It used to read "Coarse
     resolution usually OVER-predicts peak hydrodynamic force.
     Over-threshold NO-FORD verdicts are therefore conservative." Two
     independent hits, both from the R10 journal, both read-directly:
     a COUNTER-EXAMPLE exists, Smith and Mack 2014 reported in WRL
     2014/07 section 6.3.2, where numerical models at 1 m, 5 m and 10 m
     grids UNDER-predicted peak local velocity around a building
     against both a physical model and observed damage; and the
     register's Section I already lists this sentence for deletion on
     sight, so the constitution and the corrections authority
     disagreed. An under-predicted force makes a NO-FORD verdict LESS
     conservative, not more, so the direction of the error matters.
     State the "usually" with its exception, and never use L-4 alone to
     argue the published verdicts are safe-side. Working in
     docs/R10_LITERATURE_IMPLEMENTATION_2026-08-20.md section 3.3.

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

L-8. Engine decision: do not switch. THE DECISION STANDS AND ITS STATED
     REASON IS UNVERIFIED, separated 2026-08-20. The reason used to read
     "DualSPHysics ships x86-only static libraries, a hard aarch64
     blocker on GH200." The deep search commissioned to test exactly
     that, "GPU particle solver portability scaling and surrogate
     fidelity", 56 papers, returns: "The supplied literature neither
     confirms that the cited SPH package is intrinsically x86-only
     today nor documents an ARM-host CUDA build failure." Separately,
     Chrono::FSI-SPH builds and runs on Vista aarch64 in 94 seconds.
     So do not switch, and do not restate the x86-only claim as
     established. If the engine question reopens, that search names the
     portable options, Kokkos-based Karamelo among them, and the one
     hard Grace Hopper datapoint, a SWIFT SPH prototype at 15 million
     particle-updates per second with near-perfect strong scaling
     across four nodes.

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

## AUGUST 15 2026, THE RESEARCH CORPUS IS NOW QUERYABLE FROM INSIDE THE REPO

**Before asserting that a method is untried, that a result is novel, or that
something needs a citation, QUERY THE INDEX.** Load the `research-corpus` skill
(`.claude/skills/research-corpus/`) or run the tool directly:

    python3 analysis/research_index.py --stats
    python3 analysis/research_index.py --method added-mass -v
    python3 analysis/research_index.py --gaps --method validation-dataset

`data/research_corpus_index.json` holds **332 RECORDS, which are 319 DISTINCT WORKS**, merged
from eight Undermind reports, tagged across 25 method axes, each marked for
whether it reaches a reader-facing document. Built 2026-08-15 by
`analysis/research_index.py`. It reads only the committed index, never
`~/Downloads`, because a prior session lost a pass when Downloads returned EPERM
and a recursive search silently reported zero hits.

**THE INDEX COVERED 8 OF 21 DEEP SEARCHES FOR FIVE WEEKS, AND NOW COVERS 21.**
Fixed 2026-08-20. `REPORTS` is a hardcoded list of markdown files under
`~/Downloads`, so a search entered only if somebody exported it by hand. The
builder is pure standard library and CANNOT call an MCP connector, so the fix is
two-phase: an agent turn pulls the searches to `data/deep_searches/`, now
tracked, and the builder reads them. `--searches` lists and greps them and
`--source-audit` exits 1 when a completed search reaches the corpus by no route.
Four of the thirteen that were invisible answered live project questions,
including the one whose summary states that NO STUDY QUANTIFIES A CROWNED OR
CAMBERED ROAD AGAINST A FLAT PLANE.

**`--query` NOW MATCHES AUTHORS.** It covered title and abstract only, so an
author query could not return a hit and its zero read as coverage. That is how
"none of the six closest prior-art DOIs is in the corpus" was relayed to three
sessions on 2026-08-19. All six were present. A MISS IS NOT AN ABSENCE UNTIL YOU
KNOW WHAT THE PREDICATE SEARCHED.

Headline numbers, measured not estimated. **THE 43 IS INFLATED BY EXACTLY 9,
measured both ways 2026-08-20**: `docs/Dynamic_Vehicle_Traction_in_Floodwater.md`
is a raw connector dump carrying 34 DOI strings, and nine papers had that dump as
their only reader-facing route. The honest ladder is **34 reaching written
project prose, 43 counting the raw dump, 3 actually printing in the paper**. The
builder now excludes the dump, so a rebuild reports the lower figure and the
absolute number moves as new prose is added; the DELTA of 9 is the stable fact.
60 carry no DOI and are undiffable. 222 have an abstract; the other 110 are
metadata-only because each report details its top 50 only, so never describe
those as read.

**"REACH" IS NOT "CITED" AND THIS BLOCK USED TO CONFLATE THEM.** Corrected
2026-08-18. The clause "256 are cited nowhere" is WITHDRAWN: it took the
complement of *reach* and reported it as *cited*, which are different
predicates measured by different means. The full ladder, so the two can never
be collapsed again:

      332  papers in the corpus
       76  DOI-shaped string anywhere in the tracked tree  (`cited_in_repo`)
       43  DOI-shaped string in a reader-facing directory  (`cited_reader_facing`)
        4  hold an entry in the SHIPPED bibliography
        3  are `\cite`d, and therefore print in the reference list

So FORTY papers reach a reader-facing directory without reaching the reader.
43 and 3 are both correct and answer different questions. The field names
`cited_in_repo` and `cited_reader_facing` are what mislead; the data is
internally consistent, so do not go looking for a data bug.

The top of the ladder was re-derived independently 2026-08-18 against
`overleaf/main`: the submitted tex carries **14 distinct `\cite` keys**, the
shipped bib **15 entries**, 14 cited and in the bib, 0 cited but missing, and
exactly one entry never cited, `xiong2024`. BibTeX drops it, so it does not
print. The 3 rests on a census matching those 15 against the corpus rather
than on a search, which is the right method and is the part to re-check first.

SEPARATE AND OPEN: **the corpus is NOT a superset of the bibliography.** Of the
14 works the paper cites, 11 are absent from the 332 entirely, including
`shah2018` (`10.1051/matecconf/201820307003`), which is flood-vehicle
literature the paper already cites. Corpus coverage therefore cannot answer
what the paper cites, and the index cannot report this about itself. Whether
that is a sourcing gap or a dropped merge is unresolved and belongs to
whoever owns the index build.

THE CITED-STATUS COUNT IS SCOPE-SENSITIVE, exactly like the DRIFT_THRESHOLD total
in item 13. `.claude/worktrees/` MUST be excluded. A first version of the index
included it and reported 269 of 332 as cited, because another session's
`r5-research/data/r5_citation_xref.tsv` carries 489 DOIs. State the scope with
any figure.

CORRECTED 2026-08-19 by the cross-session readout, measured live, do not restate the
old forms:

- **332 records are 319 DISTINCT WORKS.** Eleven Semantic Scholar ids appear under
  twenty-four record keys with byte-identical titles. Say "332 records / 319 works", never
  "332 distinct papers".
- **"60 carry no DOI and are undiffable" is WITHDRAWN in that form.** 57 of them carry a
  Semantic Scholar id already sitting in the `link` field; only **3** are unidentifiable.
- **"Four prior vehicle fording or wading simulations exist" UNDERSTATES it.** The
  deep-search layer puts it at eight or nine. Do not cite four.

THREE PRIOR-ART FACTS THAT CONSTRAIN THE PAPER. Four prior vehicle fording or
wading simulations exist and `paper/` cites NONE of them: He et al 2026
`10.1115/1.4071177`, Wasfy et al 2015 `10.1115/DETC2015-47142`, Pazouki et al
(Semantic Scholar `61da26b6`), and Khapane & Ganeshwade 2014 `10.4271/2014-01-0936`,
the last of which is cited nowhere in the repo at all. Al-Qadami et al 2022
`10.1111/jfr3.12828` separately claim a first moving full-scale vehicle
simulation, with critical depth 0.38 m and minimum D x V 0.39 m^2/s.
NEVER QUOTE THAT D x V FIGURE WITHOUT NAMING THE PAPER, added 2026-08-20.
The same group's `10.3390/su151713262` (2023) reports the SAME 0.38 m depth
and a sliding threshold of **0.36 m^2/s**, not 0.39. The depth agrees exactly
and the depth-velocity figure does not, so a bare "Al-Qadami's D x V" is
ambiguous between two of their own papers. The 2023 paper also reports drag
DECREASING with Froude number and flow velocity, which runs against the
intuition behind this project's velocity sweep.

## AUGUST 15 2026, THE FIXED SETTLE LENGTH IS CONTRADICTED BY OUR OWN DATA

`sim_standing.py:154` uses `settle_frames=8`. `analysis/settle_audit.py` applied
`analysis/stationarity.py` to all 25 local runs, no GPU needed since the
15-column `metrics.csv` files are already on disk:

- **25 of 25 runs need MORE than 8 frames discarded.** Min 29, median 48, max 80,
  of 91 total frames.
- **N_eff is 2.9 to 11.0.** A 91-frame record holds roughly 3 to 11 independent
  samples, so any uncertainty computed from N=91 is overstated by about 3x to 5x.
  Use `effective_sample_size`, never the frame count.
- 12 of 25 retained windows are still non-stationary at 5 percent, which reads as
  the run being too short. This reaches D9's 250-frame conclusion by a different
  route: a stationarity statistic on one record, against D9's settle-length sweep
  across arms. Separate origins, so it counts as corroboration.

MSER MINIMISES STANDARD ERROR, WHICH IS NOT STATIONARITY. A settle length chosen
to stabilise a mean is not evidence the record is stationary; a residual trend can
survive inside the MSER-optimal window and only the reverse-arrangement test
catches it. `stationarity.py` reports both and carries a self-test for this trap.

DO NOT REMOVE THE TRANSIENT BEFORE A SLIDE VERDICT. Incipient motion is an EVENT,
not a steady state, and the settling literature wants peak or event statistics for
impact-type loading. Removing it drops SLIDE from 21 of 24 runs to 5 of 24 and
would silently contradict the published 16 SLIDE / 1 STUCK. `probabilistic_verdict.py`
defaults to the full record for that reason; `--stationary-window` is a robustness
diagnostic only.

VERDICT THRESHOLDS ARE A CHOICE. 17 of 24 runs flip verdict somewhere in
p >= 0.01 to 0.50, per Dancey et al 2002's probability-of-movement criterion.
`g96_m2337` returns margin_frames 1, independently matching register J15.

GRID REFINEMENT DOES NOT CONVERGE A TRANSIENT QUANTITY. Syamlal, Celik & Benyahia
2017 `10.1002/AIC.15868`. The non-monotone `final_disp_mag_m` across g48/g64/g96
is the documented expected behaviour for an instantaneous value, not necessarily a
solver defect. If grid convergence is the claim, report a time-averaged observable
over a demonstrated-stationary window with a GCI.

## THE ADVERSARIAL REVIEW PATH WAS DEAD FLEET-WIDE ON 2026-08-19. THE OUTAGE ENDED.

**OUTAGE OVER, measured 2026-08-20 03:40.** A `general-purpose` agent asked to run one
`git log` returned the correct SHA in 6.05 seconds, and a 15-agent workflow ran on the same
path immediately after. The section below is kept verbatim because it was true when written,
nine origins measured it, and the record of a fleet-wide outage is worth keeping. **Do not
delete it and do not act on it as current.**

Two things follow, and the second is the one that matters:

1. **A "do not re-attempt" instruction is advice against a retry LOOP, never a licence to
   carry a dated infrastructure claim as standing fact.** One probe costs six seconds; a
   fan-out launched onto a dead path costs the round. The verification rule at the top of this
   file already covers this, and this section is the worked example of what happens when an
   infrastructure claim is allowed to age into a fact.
2. **THE CLAIMS ARE STILL UNREVIEWED.** Every physics claim from 2026-08-18 and 2026-08-19 was
   marked UNREVIEWED because this layer was unavailable, and sessions d11, d12, d14, d15, d18
   and d19 were right to mark them so. **The path being alive does not review them
   retroactively.** Do not upgrade any of those claims until somebody actually runs the review.

---

### The outage as recorded on 2026-08-19, kept verbatim

Recorded here because it existed in five sessions' transcripts and **zero committed files**,
and a transcript is not a deliverable. Nine independent origins confirm it.

The `physics-skeptic` subagent, and any Agent call, dies with:

    deepseek-ai/DeepSeek-V4-Flash:deepinfra

**An explicit `model` override does NOT reach it.** Measured twice at 18:37 and 18:38: the
`physics-skeptic` agent at default and a `general-purpose` agent with an explicit `opus`
override produced the IDENTICAL error. The agent *launches* and then dies, which is why it
reads as a transient failure and gets retried instead of recorded.

**Consequence for every claim made on 2026-08-18 and 2026-08-19:** the operating protocol
asks for the physics-skeptic before finalising any percentage, force, verdict count or
distance. It was unavailable. Sessions d11, d12, d14, d15, d18 and d19 all correctly marked
their claims UNREVIEWED rather than faking the review. **Those claims remain unreviewed.**
Do not treat any of them as adversarially checked, and do not re-attempt the subagent
expecting a different result until the model id is fixed.


## ENVIRONMENT TRUTH THE PROJECT ALREADY PAID FOR AND FILED WHERE NOTHING READS IT

Added 2026-08-19 from the coordinator audit, finding V7. Both items below are Claude Code
bugs affecting HPC work. The first appears TEN TIMES in `_inbox/LIVE_SESSION_LOG.md` and
ZERO times in this file, the skills, or the register, so every session that needed it had
to rediscover it.

**1. `XDG_RUNTIME_DIR` on SLURM COMPUTE nodes (issue #21026).** The Bash tool can fail on a
compute node with `EACCES ... mkdir '/run/user/...'` because it hard-codes a runtime dir and
ignores `XDG_RUNTIME_DIR`. It works on login nodes. First line on any compute node:

    export XDG_RUNTIME_DIR="/tmp/xdg_runtime_${USER}" && mkdir -p "$XDG_RUNTIME_DIR"

This did NOT apply on 2026-08-19, because every session ran Claude Code on the Mac and
reached Vista through `ssh` and `scripts/tacc.sh`, which is the right architecture for
exactly this reason. Keep it that way.

**2. Interactive mode exiting immediately (issue #12507), and `claude -p` as the
workaround.** Reported cause is stdin being consumed by shell-detection subprocesses.
`claude -p` non-interactive mode is the documented workaround and appears ZERO times in
`scripts/r8/`.

The 2026-08-19 relaunch produced this SYMPTOM exactly: nine windows fell back to a bare zsh
prompt and a sender then pasted 4 KB of markdown into a shell, which executed it line by
line. The recorded MECHANISM was different, session-id reuse, and which one applied has not
been resolved. Two things hold regardless: the documented workaround was unavailable to the
launcher, and **the real defect was that a launcher failure degraded into pasting a prompt
into a shell.** A launcher must verify what it is talking to before it speaks.


## MOVED OUT OF THIS FILE 2026-08-19, with their operative rules kept here

Five sections, 171 lines, were moved VERBATIM to
`docs/CLAUDE_MD_MOVED_SECTIONS_2026-08-19.md`. Nothing was summarised or dropped and the
move was verified line by line. The rules below are what those sections were FOR; read the
moved file for the working behind any of them.

- **Repo-clone sprawl, 2026-08-15.** 28 locations, 31.6 GB, half non-canonical.
  `~/can-it-ford` is canonical. Full working is in the corrections register addendum L1 to
  L7, which is where it was already recorded; that is why the summary could leave this
  file. Three rules survive and are still live: do NOT test clone provenance by asking a
  clone whether its HEAD is an ancestor of origin/main, because that reads the clone's own
  stale cached ref; the claude.ai Project's GitHub sync points at `jcerrell-IS/mpm-engine`
  and does NOT reach this repo, so committing into `docs/` here will not appear in it; and
  `make_phase_space.py` forks on the 0.60 boundary operator, with `designsafe-staging/` the
  publication-bound tree.
- **Gate inventory, 2026-08-08.** `.claude/checks/params_check.py` already runs four
  literature-cited gate categories. DO NOT REBUILD THEM. Trap that has caught an audit
  before: `lit:resolution_convergence_gci` is assembled at runtime, so `grep -F` returns
  nothing and a naive sweep concludes the gate is missing. Run the script and read its
  output instead of grepping for the tag.
- **Overleaf credential, STILL OPEN.** The token is off local disk but NOT revoked, so it
  stays valid server-side until rotated in Overleaf account settings, and a push now
  prompts for credentials. `~/can-it-ford-paper` EXISTS despite an earlier note saying it
  was deleted.
- **Nested `./can-it-ford/` duplicate: GONE.** Verified by `ls -d`. Every exclusion of
  `./can-it-ford/` in this file, in skills and in audit scripts is now a NO-OP rather than
  a load-bearing guard. Do not conclude from a passing grep that the duplicate was handled;
  there is nothing left to handle. Re-run the `ls` before citing it as a live hazard.
- **MacOS-MCP `Snapshot` with `use_vision=true`** fails with `cannot identify image file`
  until macOS Screen Recording permission is granted to Claude Desktop. Without vision it
  works and needs no fix.
- **The refuted novelty claim** is already stated operatively in the research-corpus
  section above: do not cite "four prior vehicle fording or wading simulations", the
  deep-search layer puts it at eight or nine.
