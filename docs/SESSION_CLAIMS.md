# SESSION CLAIMS LEDGER

Protocol: append one block on start, update on every claim, mark DONE on exit.
Read the whole file before your first write.
Rules: never edit a path another session holds EXCLUSIVE. Only ONE session
submits Vista jobs at a time; claim VISTA here before sbatch. CLAUDE.md and the
corrections register are APPEND-ONLY unless held EXCLUSIVE.

---

## KNOWN LIMIT OF THIS FILE, read before relying on it

This ledger is a CONVENTION, not a lock. It is a note on a fridge, not a bolt on a
door. It prevents nothing mechanically. Two specific holes, both observed live on
2026-08-07:

1. NO ENFORCEMENT. A session that never opened this file behaves identically to one
   that read it and obeyed. Nothing re-reads it after startup. Sessions cannot query
   each other (peers are reply-only), so the file is the only channel and it is
   advisory.
2. TOCTOU ON THE VISTA CLAIM. Read-then-write on markdown is not atomic. Two sessions
   can both read `VISTA: none`, both append `VISTA: mine`, and both sbatch. Neither
   did anything wrong.

3. THIS FILE IS GITIGNORED, AND THAT ALONE BREAKS THE PROTOCOL. `.gitignore:25` is
   `session_*.md`. Git sets `core.ignorecase=true` on macOS case-insensitive volumes
   (confirmed live: `git config core.ignorecase` returns `true`), so a lowercase rule
   silently swallows `SESSION_CLAIMS.md`. The rule is pre-existing at HEAD, not
   something a session added today.

   The consequence is fatal to the design. An untracked file does not propagate to
   worktrees: each worktree has its own working directory. Verified live, both of
   these return "No such file or directory":
     .claude/worktrees/ctx-census/docs/SESSION_CLAIMS.md
     .claude/worktrees/c1-triage/docs/SESSION_CLAIMS.md
   So Sessions A, B, C and D, all of which are specified to run in worktrees and all
   of which are instructed to "read docs/SESSION_CLAIMS.md in full" as their FIRST
   action, would each find nothing there, or would each create their own private copy
   that no other session can see. The ledger cannot coordinate anyone.

   This file was therefore committed with `git add -f` on its explicit path. That
   forces it into the index without touching `.gitignore`, which was deliberately not
   modified because another session holds an uncommitted edit to it. Two sibling files
   are swallowed by the same rule and remain untracked: docs/SESSION_DISPATCH_2026-07-25.md
   and docs/SESSION_INDEX_2026-07-25_SHIPv3.md.

For real enforcement this has to become an atomic primitive (`mkdir` or `flock`), not
a text file. `.claude/hooks/gate_concurrent_write.sh` exists untracked in the tree as
of 2026-08-07 and appears to be an unfinished attempt at exactly this.

Keep writing this file: it is useful for a human to read. Do not mistake it for a control.

---

## SESSION 0: total context census, sections A through H

started: 2026-08-07T13:07:00+0100   worktree: main   pid: 59741
CLAIMS:
  - docs/CONTEXT_CENSUS_2026-08-07.md    EXCLUSIVE
  - docs/SESSION_CLAIMS.md               EXCLUSIVE (created it)
READS-ONLY:
  - everything else in the repo, plus ~/can-it-ford-demo, ~/can-it-ford-audit,
    ~/can-it-ford-rescue, ~/can-it-ford-BACKUP-*, ~/.claude/
  - Vista and LS6 via scripts/tacc.sh, read-only commands only
VISTA: none. No job submitted. No SU consumed by this session.
STATUS: DONE 2026-08-07T13:40:00+0100

NOTES, and they matter for whoever reads this next:

- This session ran in the MAIN TREE, not in `.claude/worktrees/ctx-census`. That is
  deliberate and correct: this protocol's own rule puts the ledger in the main tree,
  "never in a worktree." The ctx-census worktree sits on branch `worktree-ctx-census`
  at 04913f9, five commits behind main.

- SESSION 0'S PRECONDITION WAS NOT MET. The prompt says "No other session should be
  running. Confirm that first." It was false. At 13:08 there were 7 claude sessions
  rooted in this repo; by 13:31 there were 10. Two of them (pid 5275 on ttys012, pid
  25056 on ttys013) were themselves running `claude --worktree ctx-census`, that is,
  two other sessions were also trying to be Session 0. After 43 and 39 minutes
  respectively they had produced neither deliverable and their worktree was clean.

- THE TREE MUTATED DURING THE CENSUS. Between 13:08 and 13:26 another session wrote
  Session C's deliverables into the MAIN TREE rather than a `sim-physics` worktree:
  analysis/bingham_cfl_crossover.py, analysis/verify_cpic_ground_clearance.py,
  docs/UNEXPLORED_AREAS_ASSESSMENT_2026-08-07.md, a .gitignore edit, and +261 lines
  in simulation/validate_coupling_force.py. Census sections B, D and E are accurate as
  of their own sample times, not as of now.

- NOT TOUCHED BY THIS SESSION, and not mine: .gitignore,
  simulation/validate_coupling_force.py, scripts/c1sdf.sbatch,
  .claude/hooks/gate_concurrent_write.sh, analysis/bingham_cfl_crossover.py,
  analysis/verify_cpic_ground_clearance.py, docs/UNEXPLORED_AREAS_ASSESSMENT_2026-08-07.md.
  Only the two files claimed above were staged, by explicit path. `git add -A` was
  never run.

- A PROCESS-VISIBILITY DEFECT WORTH KNOWING: pid 59741 (this session) is alive and
  accumulating CPU but is INVISIBLE to `pgrep -x claude` and `pgrep -f "MacOS/claude"`,
  while `ps -ax` sees it. Any concurrency check built on pgrep will undercount. The
  prescribed loop in the Session 0 prompt reported 8 sessions where 9 existed.


## CHAT SESSION: cross-session flag + regime-ladder dispatch

started: 2026-08-07T19:03:40+0000   surface: claude.ai chat, not a terminal
  session, no pid, real read/write access to this working tree via Desktop
  Commander MCP, confirmed live this session (earlier notes claiming chat
  surfaces cannot reach this repo are stale as of today)
CLAIMS:
  - docs/FLAG_topple_accel_risk_2026-08-07.md          EXCLUSIVE (created it)
  - docs/REGIME_LADDER_DISPATCH_2026-08-07.md           EXCLUSIVE (created it)
READS-ONLY:
  - docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md, docs/C1_ROOT_CAUSE_2026-08-07.md,
    docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md, simulation/failure_modes.py,
    analysis/classify_failure_modes.py, git log/status/branch, SESSION_CLAIMS.md itself
VISTA: none. No job submitted, no SU consumed.
GIT: pushed two commits directly to origin/main, both single-file, both new
  untracked files staged by explicit path, neither commit touched any file
  another session had modified. 5d8827f (the flag file), 9b52fa7 (the
  dispatch file). Did not run git add -A or git commit -a at any point.
  Confirmed via git status before each commit that the three files another
  session has modified (.claude/checks/params_check.py,
  docs/C1_ROOT_CAUSE_2026-08-07.md, simulation/validate_coupling_force.py)
  were untouched by either commit.
STATUS: DONE 2026-08-07T19:40:00+0000

WHAT THIS SESSION FOUND, for whoever reads this next:

1. TOPPLE classification (data/failure_modes_by_run_classified.csv, produced
   by the failure-mode-classifier session per CONCURRENT_SESSION_NOTICE.md)
   gates on surge_accel_g (failure_modes.py:170,182), which C1_ROOT_CAUSE.md
   section 8 names as a forbidden back-computed-force quantity on the
   free-rigid coupling path. Neither session referenced the other. Full
   detail in FLAG_topple_accel_risk_2026-08-07.md. Not fixed, only flagged.

2. Independently re-verified C1_ROOT_CAUSE.md section 2's polyfit closed-form
   claim (slope = 6*dV/(dt*(N+1)*(N+2)) for a step at sample 1) symbolically
   via Wolfram Language for N=1 through 8. Exact match, zero residual every
   time. The "measurement artifact, not a sinking body" reframing rests on
   this formula and it now has independent confirmation, not just internal
   consistency.

3. Wrote docs/REGIME_LADDER_DISPATCH_2026-08-07.md, a self-contained prompt
   for a fresh Claude Code session to run rungs (b), (c), (d) of section 8's
   own prescribed regime ladder, plus the two small fixes section 9 already
   specified (C3's estimator, the P2G guard's axis/material report). Read it
   before starting that work, it has the concurrency rules this ledger's own
   header says are advisory only, restated as hard requirements for that
   specific dispatch.

4. This ledger's own gitignore problem (section near the top, "THIS FILE IS
   GITIGNORED") appears at least partially resolved: this session read the
   file via a direct path, not via a worktree copy, and appended successfully.
   Did not independently re-verify the worktree-visibility claim from SESSION 0.


## CODE SESSION: execute the regime-ladder dispatch, rungs (b)(c)(d) + Fix A + Fix B

started: 2026-08-07T20:35:00+0100   worktree: main (NOT a worktree)   surface: Claude Code
CLAIMS:
  - simulation/validate_coupling_force_ladder.py        EXCLUSIVE (new file, created it)
  - docs/REGIME_LADDER_RESULTS_2026-08-07.md            EXCLUSIVE (new file)
  - scripts/ladder.sbatch                               EXCLUSIVE (new file)
READS-ONLY, will not edit any of these:
  - simulation/validate_coupling_force.py   (held by another session, M in the tree)
  - .claude/checks/params_check.py          (held by another session, M and BROKEN)
  - docs/C1_ROOT_CAUSE_2026-08-07.md, docs/REGIME_LADDER_DISPATCH_2026-08-07.md,
    docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md, docs/SESSION_CLAIMS.md (append only),
    renders/yaris_render_s1/sim_standing.py, data/all_runs_inventory.csv,
    third_party/mpm-engine-544c93dd-solver-core/ (pinned, never edited)
VISTA: RELEASED 2026-08-07T21:1x. Jobs 895648 (COMPLETED 00:01:44), 895652 (cancelled
  while PENDING, 2 h walltime was not backfilling on a gh partition at 192 running /
  60 pending; resubmitted at 20 min), 895653 (COMPLETED 00:01:38, exit 0:0, all 8 steps
  rc=0). Batch only, no idev. Total cost about 0.056 node-hours. taccinfo read 669 SU
  before and after. Queue empty of my jobs on exit.
STATUS: DONE 2026-08-07T21:1x

DELIVERED: docs/REGIME_LADDER_RESULTS_2026-08-07.md. Rungs (b)(c)(d) at g64 and g96,
Fix A confirmed against the one stored C3 artifact at zero SU, Fix B confirmed live
against the real Solver class on real particle arrays. Two arms (b_g64, c_g64) are
DISCARDS: they hit the 1200-frame settle cap without meeting the gate. Do not quote them.
Newly raised and not inherited from any prior doc: the g64 settle is non-deterministic at
fixed configuration, three identical settle phases gave 1200/not-met, 1200/not-met and
974/met, so a g64 arm's discard status is not reproducible. Detail in section 5.5 of the
results doc.

ORDERING NOTE, stated because the dispatch asks for this block BEFORE any write:
simulation/validate_coupling_force_ladder.py was created a few minutes before this
block was appended. Nothing else was written first, and no Vista job was submitted
before this claim. The file is new and unclaimed by anyone else, so the race this
protocol guards against could not have occurred, but the ordering was still wrong.

FOUR THINGS FOUND DURING THE DISPATCH'S OWN SECTION 7 PRE-CHECKS, all live:

1. THE SDF CODE IS COMMITTED. REGIME_LADDER_DISPATCH section 1 rule 6 and
   C1_ROOT_CAUSE section 9 both say run_c1_sdf, cube_mesh, sdf_margin_cells and
   build_box_sdf "exist in NO COMMIT". They now exist in 6593404 on branch
   worktree-c1-triage, which is also pushed to origin/worktree-c1-triage. They are
   NOT on main: `git merge-base --is-ancestor 6593404 main` is false. The working
   tree carries a further +8/-2 on top of that branch. So the project's only
   externally-validated force measurement is preserved in git and on the remote,
   but it is invisible to anyone reading main. Reconciling it onto main is still
   owned by another session and was not done here.

2. THE COMMIT GATE IS BROKEN AND BLOCKS EVERY SESSION. .claude/hooks/
   pretooluse_git_commit_gate.py:8 fires on any Bash command containing both "git"
   and "commit", and runs .claude/checks/params_check.py, which currently raises
   ValueError: could not convert string to float: 'length' at its line 85. That file
   is M in the tree, i.e. mid-edit by another session. Until that session finishes,
   no `git commit` can succeed here. Two incidental traps: the substring test also
   fires on the word "uncommitted", and the hook resolves its own script path
   relative to the tracked cwd, so a single `cd` into a subdirectory bricks every
   subsequent Bash call in the session. Do not `cd` in this repo.

3. C1_ROOT_CAUSE_2026-08-07.md is no longer dirty; it was landed in 371971b. The
   dispatch lists it as one of three protected modified files. Two of the three are
   still modified, that one is clean.

4. VISTA HAS 669 SU AND AN IDLE INTERACTIVE JOB WAS BURNING THEM. Live taccinfo:
   669 SU on BCS20003, expiring 2026-09-30. squeue showed 895536 idv98837 on gh-dev
   RUNNING. sacct for 2026-08-06 onward shows six idev jobs today (894519, 894585,
   894603, 894705, 895446, 895536), five of them TIMEOUT at 00:30:00, against
   00:07:38 for job 894731, the c1sdf job that produced the only externally-validated
   result in the project. Not this session's job and not killed by this session.

INCIDENTAL DEFECT SPOTTED, NOT FIXED, NOT MINE: the in-flight edit to
simulation/validate_coupling_force.py duplicates the com_frame print inside run_c2's
frame loop, so every frame is emitted twice. Whoever owns that edit should collapse
it, and anyone counting com_frame lines in a c2 log should dedupe first.


## CONSOLIDATION SESSION: J.1 coupling validation, consolidate and extend

started: 2026-08-07T21:51:36+0100   worktree: main (NOT a worktree)   surface: Claude Code, Mac
CLAIMS:
  - docs/SESSION_CLAIMS.md        APPEND-ONLY (this block, written with >> not read-modify-write)
READS-ONLY, will not edit any of these:
  - simulation/validate_coupling_force.py   (READ-ONLY per dispatch, already patched, M in tree,
    held by another session; not re-edited here)
  - docs/COUPLING_VALIDATION_J1_2026-08-07.md  (see NOTE below: dispatch expected to possibly
    write this; it was already merged by another session at 21:47, so this session does NOT write it)
  - docs/COUPLING_VALIDATION_J1_VISTA_2026-08-07.md  (Vista-only, does not exist on Mac)
  - coupling_validation output JSONs, wherever they live (Task 3 is read-only by dispatch)
VISTA: not claimed as a compute resource. No job submitted, no SU consumed. Read-only
  commands only via scripts/tacc.sh if used at all.
STATUS: IN PROGRESS

NOTE ON CONCURRENCY, recorded at claim time because it is a live hazard, not a retrospective:
  Four claude sessions alive at claim time (ps -ax, since pgrep undercounts per SESSION 0):
  started 20:35:15, 20:45:13, 21:51:36, 21:51:39. Mine is one of the 21:51 pair, so ANOTHER
  session began within 3 seconds of this one and may hold the same dispatch. The 20:45 session
  is the likely owner of both the in-flight simulation/validate_coupling_force.py edit and the
  21:47 write to docs/COUPLING_VALIDATION_J1_2026-08-07.md (that file and its .bak-premerge
  sibling share mtime 21:47:58). This session therefore treats that doc as ANOTHER SESSION'S
  LIVE WORK and does not write it.

FIREWALL RESTATED: this is diagnostic work on the standalone harness
simulation/validate_coupling_force.py. It is NOT the canonical pipeline. Nothing in this
session reads, writes, or concludes into data/all_runs_inventory.csv,
gates_results_all_runs.json, renders/yaris_render_s1/sim_standing.py, or any of the 17 gated
runs. Nothing found here changes the published NO-FORD verdict, which came from raw
displacement threshold crossing, not from the force accessor being validated here.

STATUS: DONE 2026-08-07T22:35:54+0100   (supersedes the IN PROGRESS line in this block)

TWO-LINE SUMMARY:
  Tasks 1 and 2: the Mac-doc merge had ALREADY been done by another session at 21:47:58, so
  Task 1 was DONE on arrival and this session wrote nothing to it; the Vista-only doc got a
  prepended MERGED notice that also names two facts the merge did NOT carry over.
  Task 3: F_buoy_from_a is emphatically NOT flat across the four densities, it runs +16020.6,
  +2820.0, -6988.9, -42985.3 N and changes sign, so the fixed-absolute-error hypothesis is REFUTED.

FINDINGS, in the order they were established, all live-verified:

1. TASK 1 WAS ALREADY DONE, NOT BY THIS SESSION. docs/COUPLING_VALIDATION_J1_2026-08-07.md
   contains both marker strings ("four matched density points" at line 272, "-90.99" at
   line 284). It and its .bak-premerge sibling share mtime 21:47:58, four minutes before this
   session started at 21:51:36. This session did not write that file: its md5 was
   8612fe62a383c67c032e8b333f6cfdda when first read and byte-identical at exit.

2. TASK 2 PRECONDITION FAILED, AND THE PREPEND SAYS SO. Every NUMERIC result in the Vista doc
   is represented in the Mac doc, but two non-numeric facts are not: (a) that the
   divide-by-zero guard was originally added for run_c3 and generalizes to run_c1, and (b)
   that the com_frame instrumentation has not yet been exercised on a crash. Rather than
   assert a clean merge, the prepended line names both. Vista file 32 -> 34 lines; backup at
   .bak-preprepend, md5 a4e0281215b24b05e8cea3ba9589d1cc, matching the pre-write original.

3. THE TASK 3 PREMISE IS FALSE: THERE ARE NO FOUR JSON FILES. Only the rho=600 point was ever
   persisted as JSON (data/coupling_validation/c1_g64.json). The 700, 800 and 1000 points
   exist NOWHERE as machine-readable artifacts. Verified by content search on BOTH machines:
   the strings -90.99 and -237.34 appear only in the two markdown docs, in no JSON and no log.
   Cause: validate_coupling_force.py:868-870 writes JSON only when --out is passed, and
   line 864 otherwise prints to stdout. Those three runs were evidently run without --out.
   CONSEQUENCE: three of the four published density points rest on hand-transcribed 2 dp
   numbers with no raw trace. They are not reproducible without re-running.

4. THE DISPATCH'S CONFIRMATION FIELDS DO NOT ALL EXIST. rho_box is stored as
   geometry.rho_box_requested / rho_box_realized; settle_frames=900 is stored as
   settle.settle_frames_cap (the CAP, not the count: settle_frames_run was 444 for rho=600);
   depth_cells is geometry.water_depth_cells. box_bottom_cells is NOT STORED AT ALL. It was
   recovered by inverting validate_coupling_force.py:652, z_b0 = floor + box_bottom_cells *
   DX_CANON, against the stored z_b_nominal_at_spawn, floor and grid_lim (DX_CANON = LIM/64,
   line 16). Every c1-family run recovers box_bottom_cells = 3.00 exactly.

5. TASK 3 RESULT, F_buoy_from_a IS NOT FLAT. F_buoy_analytic = RHO_W * V * G
   (line 697) carries NO rho_box dependence and is 31298.444 N in every run, so
   F_buoy_from_a = F_analytic * (1 + err_F_pct/100) exactly. That inversion was validated
   against the one real JSON to a residual of 1.8e-12 N before being applied.
       rho_box   F_buoy_from_a (N)   a_meas (m/s2)   a_ideal (m/s2)
          600         +16020.596          -1.4410          6.5400
          700          +2819.990          -8.5473          4.2043
          800          -6988.943         -12.5482          2.4525
         1000         -42985.283         -23.2831          0.0000
   Spread 59005.9 N, i.e. 1.885x the analytic buoyant force, and it CHANGES SIGN. A fixed
   absolute error would have held F_buoy_from_a near one number; it does not. Nor is the
   force error constant (-15278, -28478, -38287, -74284 N), nor is error/mass constant
   (-7.98, -12.75, -15.00, -23.28). The 2 dp rounding on the published err_F_pct moves F by
   only +/-1.6 N, immaterial against a 59006 N spread, so this conclusion is robust to the
   fact that three rows are derived rather than read.
   SHARPEST STATEMENT: at rho_box=1000, exact neutral buoyancy, where physics requires
   a = 0 identically, the harness measures a = -23.28 m/s2, i.e. the body is driven DOWNWARD
   at 2.37 g, more than twice free fall. The defect worsens monotonically toward neutral
   buoyancy rather than holding a fixed force offset.

FIREWALL HELD: nothing here read, wrote, or concluded into data/all_runs_inventory.csv,
gates_results_all_runs.json, renders/yaris_render_s1/sim_standing.py, or any of the 17 gated
runs. The published NO-FORD verdict came from raw displacement threshold crossing, not from
the force accessor examined here, and is untouched by all of the above.

NOT DONE, out of scope per the dispatch, each needs its own claim and dispatch:
vehicle_params.py mass sourcing, the failure_modes_result.json miscitation, DRIFT_THRESHOLD
sourcing. No Vista job submitted, no SU consumed; the only remote calls were read-only plus
the single authorized prepend.
