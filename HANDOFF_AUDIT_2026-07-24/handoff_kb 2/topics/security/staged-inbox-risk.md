---
id: 20260724-staged-inbox
title: Staged raw session exports in the backup repo
tags: [security, git]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-secrets-env, 20260724-personal-sweep, 20260724-worktrees-backup]
summary: Three 600KB+ raw session-transcript exports are staged (git add'ed, not yet committed) in the backup repo and are not covered by its .gitignore rules — content itself is clean, but the mechanism matches the project's documented prior leak incident.
---

# Staged raw session exports in the backup repo

> Summary: the one live, current risk this audit found. Content is clean; the mechanism is the risk.

## Findings
`git status --short` on `~/can-it-ford-BACKUP-before-history-purge` (confirmed unchanged on a live re-check, same session) shows, among other changes:

```
A  _inbox/export_canitford_0_0_20260723_054340.md
A  _inbox/export_canitford_5_5_20260723_054343.md
A  _inbox/export_canitford_5_5_20260723_054351.md
```

The `A` in the first column means these are staged additions, not just untracked files sitting on disk — one `git commit` away from entering permanent history. Each is 600-650KB, a raw session-transcript export. `_inbox/LIVE_SESSION_LOG.md` itself (2.4MB) IS covered by `.gitignore` and is not at risk; these three specific export filenames are not covered by the same rule.

## Content check
Grepped all three for personal/health-shaped keywords (`therap`, `medicat`, `diagnos`, `prescription`, `mental health`, `panic attack`, `social security`): 0 real hits in any of them (see `20260724-personal-sweep` for the methodology and why raw counts alone aren't trustworthy here). Content is clean as of this audit.

## Why this is still worth flagging
This is exactly the mechanism (raw, unreviewed session dump entering the git index) that produced this project's one documented prior incident, per its own CLAUDE.md. Clean content today doesn't mean the pattern is safe to leave in place — the next export could contain something that matters, and nothing currently stops it from being committed.

## Recommended human decision (not executed)
Unstage these three files (`git restore --staged _inbox/export_canitford_*.md`) and either delete them, gitignore the pattern, or explicitly review-then-commit them one at a time, before any bulk `git commit` runs in this repo.

## Related
- [Secrets and .env files](secrets-and-env.md)
- [Personal/health content sweep result](personal-content-sweep.md)
