---
name: git-history-rewrite
description: Standing gotchas for rewriting this repo's git history with git filter-repo. Use before any filter-repo run, any path removal or --replace-text scrub, or any force-push of rewritten history, and when a rewrite appears to have done nothing or a push appears to have stalled.
---

# git filter-repo standing note

Moved out of the root CLAUDE.md on 2026-08-05: it is task-specific, so it
loads on demand instead of costing context in every session.

- `--path` / `--invert-paths` and `--replace-text` are independent passes.
  filter-repo does not combine them automatically. Run them as separate
  passes.
- A rewrite touching an existing repo (not a fresh clone) requires
  `--force`, or it aborts safely rather than doing nothing. "Nothing
  happened" usually means the missing `--force`, not a failed match.
- After any filter-repo rewrite, `--force --all` pushes the FULL pack
  again, not a diff. Large repos with binary history take real time, and a
  cutoff mid-transfer in a terminal paste does not mean it failed. Check
  the remote before re-running.

Per the Multi-Pane Standing Rules in the root CLAUDE.md, any git push,
force-push, file delete, or overwrite of an existing file requires explicit
confirmation in chat before execution. That applies to every command here.
