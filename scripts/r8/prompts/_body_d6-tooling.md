# SLOT d6-tooling

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-tooling, branch claude/r8-tooling
(off claude/add-ci-checks).

You may write ONLY, inside YOUR worktree:
  .claude/tooling/**            (to TRACK it, contents unchanged)
  .gitignore                    (only if it is what hides .claude/tooling/)
  docs/R8_TOOLING_PROVENANCE.md (new)
You MAY also stop stale background processes on the machine, after the checks below.

NEVER TOUCH: .claude/settings.json (d1-safe owns it); .claude/hooks/; the main checkout's
working tree; any other branch; any tmux pane belonging to a live session.

## WHERE THIS LEFT OFF: NOWHERE. Unowned infrastructure debt that is currently running.
MEASURED LIVE:
  PID 54804, 2 days: python3 .claude/tooling/round5_autodispatch.py --watch --interval 90
    Targets tmux canford5 panes D1, D2, D3. THE D1 PANE NO LONGER EXISTS.
    .claude/state/round5_autodispatch.log logs three lines every 90 s, all
    "composed message is a DUPLICATE, refusing to send". THE SCRIPT IS UNTRACKED BY GIT.
  PID 98633, 4 days: bash .claude/worktrees/concurrent-session-safety-570b39/scripts/canford_monitor.sh watch 20
    That worktree has an UNCOMMITTED +17/-3 edit to canford_monitor.sh, so a 4-day-old process
    runs a script whose on-disk version has since changed. D3 flagged on 2026-08-16 that this is
    THE ONLY COPY of the safety tool and asked whoever is live there to commit it. Nobody has.
    Snapshotted to can-it-ford-bundles/2026-08-16/uncommitted-worktrees-snapshot/, same disk.
  PID 44782, 15 h: bash ~/can-it-ford-bundles/watch_register_merge.sh
  .claude/tooling/ holds 19 untracked files: corpus_mcp.py, tacc_mcp.py, commit_autoapprove.py,
    round5_launch.sh, round5_autodispatch.py, two .bak-portability files, and more.

NOTE: the R8 launcher refuses to start while round5_autodispatch.py is alive, so stopping it is
a precondition for the rest of this round.

FIVE OTHER CLAUDE SESSIONS ARE LIVE in tmux canford5. Killing the autodispatcher does not touch
them; VERIFY that with `ps` before and after, and do not send keys to any pane.

BEFORE STOPPING ANY PROCESS establish what it would break, and write the reasoning down for each
of the three. A monitor nobody reads is still a monitor someone may rely on.

## WHY TRACKING MATTERS, from CLAUDE.md
"Hooks must fail open... hooks wired to $CLAUDE_PROJECT_DIR/.claude/tooling/, which is untracked
and therefore absent from every worktree, error on every Bash call made from a worktree. Before
adding a hook, check whether its script is tracked by git; an untracked script cannot be seen by
a worktree." An untracked tool is invisible from all 21 worktrees.

## FIRST STEP
  git -C /Users/josie/can-it-ford check-ignore -v .claude/tooling/round5_autodispatch.py || true
  ps -eo pid,etime,command | /usr/bin/grep -E 'round5_autodispatch|canford_monitor|watch_register' | /usr/bin/grep -v grep || true
Gitignored versus never-added need different fixes.

## DEFINITION OF DONE
1. .claude/tooling/ tracked on YOUR branch, contents byte-unchanged, verified by
   `git diff --stat` showing only additions.
2. Each of the three processes has a written verdict: stopped and why, or left running and why.
   If stopped, confirm with `ps` and confirm the five live sessions are unaffected.
3. A named file recording that scripts/canford_monitor.sh in concurrent-session-safety-570b39 is
   still the single uncommitted copy of the safety tool, if you could not get it committed. You
   may NOT commit on that session's behalf.
4. .claude/settings.json unedited.
