# EVERY ERROR FROM ROUNDS 3-4, AND THE MECHANISM THAT PREVENTS IT
Read this before you do anything. Each row is a mistake that was actually made,
with the thing that now stops it. Where the fix is a tool, use the tool; where
it is a rule, the rule is stated as a check you can run rather than an
intention.

**The meta-lesson: in every case the coordinator had the correct rule written
down, in its own context, and sometimes had just told another session to follow
it. Instructions did not work. Only typed returns and exit codes worked.**

---

## A. COORDINATION ERRORS

| # | What happened | What prevents it now |
|---|---|---|
| A1 | Byte-identical prompts sent to 13 sessions, six times. Josie diagnosed it before the coordinator did. | `round5_autodispatch.py` sha256s every outgoing message and **refuses any hash already sent to anyone**. Also `dispatch_uniqueness.py` on the initial four files before sending. |
| A2 | ~25 commit confirmations handled by hand; sessions sat 15+ min at Yes/No prompts. Largest single loss of session time. | `commit_autoapprove.py`, wired into `settings.json`. Auto-grants a path-limited commit of ≤8 safe files; prompts otherwise. |
| A3 | Sessions idled at empty prompts because no human was watching. | `round5_autodispatch.py --watch` speaks to any session idle >4 min, with a follow-up built from that session's own git state. |
| A4 | Two relays lost load-bearing qualifiers; recoverable only from the source commit body. | Relay a **commit SHA**, never a summary. The autodispatcher quotes each session's real last commit. |
| A5 | Sessions duplicated each other's work with no awareness. | `.claude/state/round5_board.md`: append-only, read before starting a unit, one row per finished unit. The autodispatcher injects siblings' last commits into every follow-up. |
| A6 | 13 panes tiled in one window on a 66-column client; unreadable, and a stalled session looked like a working one. | `round5_launch.sh`: one window per dispatch, a colour per dispatch on border + title + status, heavy border lines, `pane-border-status top` always on. |

## B. VERIFICATION ERRORS

| # | What happened | What prevents it now |
|---|---|---|
| B1 | Ran three repeats specifically to avoid a single-draw claim, then quoted **one ratio** from them. | Report **N and spread**, never a point value. Never quote a ratio whose denominator is itself measured: the determinism floor spans 0.52-1.69 m across identical runs, so ratios invert with run length. |
| B2 | Measured the mirror control **inside the transient it had diagnosed an hour earlier** and published it. Three sessions retracted it. | Every simulation number must state the **settle length** it was measured at. `R7_FRAMES` defaults to 20; the stack rings with a ~100-frame period; use 200. |
| B3 | Drifted its own clock ~1 hour and time-boxed sessions against a deadline that did not exist. | `tacc_alloc_status` returns `remaining` from `squeue -o %L`. **Never estimate elapsed time.** |
| B4 | `import warpmpm` succeeded against a **6-line stub** raising RuntimeError; reported "environment verified" to all sessions. | `tacc_env_probe` returns `module_lines`, `symbols` and **`is_stub`**. An import succeeding is not an environment working. |
| B5 | Called mu=0.55 an anomalous lab value and pushed that to six sessions. Martinez-Gomariz 2017 measured 0.52-0.62 by the same method. | Before characterising any value as anomalous, run `corpus_search` and `corpus_cited_status`. The corpus usually already contains the answer. |
| B6 | Claimed a "three-way fork" of a script by counting paths. It was two files, no fork. | Establish file identity by **sha256**, not by counting locations. |
| B7 | An instantaneous `nvidia-smi` 0% was read as an idle node; polls had landed between 24 consecutive runs. | `tacc_gpu` returns the sample with an explicit caveat. A single sample is not an occupancy measurement. |

## C. RESEARCH-COVERAGE ERRORS

| # | What happened | What prevents it now |
|---|---|---|
| C1 | **Never searched for Elicit reports at all.** They contain a fifth fording simulation, a 2025 full-scale experiment, and a 1,345-row extraction CSV with depth-velocity and friction columns. | The find command in the bootstrap covers `*elicit*`. Use `corpus_search`, which walks every root. |
| C2 | Two whole Desktop trees never opened (`CAN_IT_FORD_MASTER_2026-07-26`, `_ARCHIVE_2026-07-26`). The "128 artifacts" figure is an undercount; the real total is ~400. | `corpus_inventory` reports per-root counts and readability. Do not quote a corpus size you did not measure. |
| C3 | Read report **summaries** instead of their **paper catalogs**. Reading two catalogs surfaced four uncited fording papers; two catalogs (68 and 78 papers) remain unmined. | Dispatch R5-1 exists for exactly this. Mine catalogs, not summaries. |
| C4 | Five sessions independently reported artifacts "unreadable" because each checked `~/Downloads` only, where macOS TCC intermittently denies access. | `corpus_resolve` returns every readable copy across all roots. **A zero result from one root is a broken probe, not an absence.** |

## D. OPERATIONAL AND TOOLING ERRORS

| # | What happened | What prevents it now |
|---|---|---|
| D1 | `srun --jobid=` into a live idev hung and died; `--overlap` was unknown. ~40 min of dead GH200 time. | `tacc_submit` auto-injects `--overlap` when an idev is detected, and always passes both `-p` and `-t`. |
| D2 | 13 sessions on one SSH ControlMaster hit the server session limit; **every session lost LS6 at once** and running steps died after writing ~1.8 GB. | `canford-tacc` pools one connection. Do not open your own ssh in parallel. |
| D3 | Long probes killed by `tacc.sh`'s `TACC_TIMEOUT=60` default. | The MCP server sets its own per-tool timeouts, and `tacc_submit` detaches with `setsid nohup ... </dev/null &` so a socket drop cannot kill a run. |
| D4 | The two new MCP servers were registered with `${CLAUDE_PROJECT_DIR}`, which resolves to the **worktree**; `.claude/tooling/` exists only in the main checkout, so they died with `-32000` in every dispatch session. | `.mcp.json` now uses **absolute paths**. Verified by launching both from inside a worktree. |
| D5 | A setup guide used repo-relative paths; a viewer resolved them against the guide's own directory and produced a path that did not exist. | All guide paths are absolute. |
| D6 | Told the user to run `git commit -- <path>` on an **untracked** file. Pathspec error. | A new file needs `git add -- <path>` first. `git commit -- path` only matches tracked files. |
| D7 | Gave a shell command without its directory; the user ran it in a worktree where the file did not exist. | Every command in a handoff carries `cd <absolute dir> && ...`. |
| D8 | The monitor re-alarmed every poll on an unresolved condition; the same paths alarmed four times in three minutes, training a real alarm into noise. | The monitor now alarms on **change**: a new path fires loudly, an unresolved one drops to a quiet aged line. |
| D9 | A session wrote `CLAUDE.md` and the register directly in the **main checkout** while D4 held 22 unpushed register commits, creating a silent divergence (752 vs 1455 lines). | Sequence before either moves. Never `git checkout`/copy a shared doc over another tree. The board records who is editing what. |

## E. STANDING RULES THAT WERE ALREADY WRITTEN AND STILL GOT BROKEN

These are in `CLAUDE.md`. They were violated anyway, which is why they are
repeated here with their enforcement:

- **No bulk staging.** `banned_phrase_guard.py` blocks `git add -A`, `git add .`,
  `git commit -a` at the hook level.
- **No push without explicit per-branch go-ahead.** `pushcheck` first; a git
  hook requires `PUSH_OK=1`. The repo is **PUBLIC**.
- **Absolute `/Users/josie/can-it-ford/...` writes from a worktree land in the
  MAIN checkout.** `gate_concurrent_write.sh` plus the monitor's main-tree
  baseline.
- **`grep` here is a ugrep wrapper that skips gitignored paths.** Use
  `/usr/bin/grep` for any absence or inventory claim.
- **E8:** derived NCAC/CCSA geometry must not reach the public repo. Note that
  the canonical hull is **already public**, which is an open exposure, not a
  hypothetical.
- **physics-skeptic before any percentage, force, verdict count or distance.**
  If unavailable, mark UNREVIEWED; never fake the review.
