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
