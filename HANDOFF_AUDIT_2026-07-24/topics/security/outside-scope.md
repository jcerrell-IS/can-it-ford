---
id: 20260724-outside-scope
title: Findings outside the four target directories
tags: [security, personal-content]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-personal-sweep]
summary: A folder named "Health docs" is granted to this Cowork session (currently empty) and a separate old Mac-migration Documents folder contains real grade-report PDFs — neither is part of Can It Ford, noticed while disambiguating ~/Claude/reu, not acted on.
---

# Findings outside the four target directories

> Summary: two things noticed while mapping the granted folders to figure out where `~/Claude/reu` actually lives. Neither is inside the audited project directories. Not acted on.

## Findings
- A folder literally named `Health docs` is granted to this Cowork session at the home-directory level. Its top-level listing is currently empty (0 items) — nothing was read inside it. Flagging its existence as a granted folder is worth a conscious decision: revoke access if Cowork doesn't need it for this project, rather than leaving broad access granted by default.
- `~/Documents - Josie's MacBook Air - 1/` (one of three overlapping "Documents"-named folders that look like leftovers from old Mac account migrations) contains actual grade-report PDFs (report cards, semester summaries) sitting loose, unrelated to Can It Ford.

## Why this is in the KB at all
Neither of these came from the four target directories in the original ask. They surfaced because confirming where `~/Claude/reu` physically lives required listing sibling mount points, and these were sitting right next to it. Recording them here rather than silently dropping them, per the "don't assume it can't happen again" instruction — even though they're a different risk shape (broad folder access / stray personal documents) than the git-history-leak incident this project has already had.
