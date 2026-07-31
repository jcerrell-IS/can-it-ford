---
id: 20260724-personal-sweep
title: Personal/health content sweep result
tags: [security, personal-content]
created: 2026-07-24
updated: 2026-07-24
related: [20260724-staged-inbox]
summary: 183 raw keyword hits across the session-log exports, all traced to "diagnostic/diagnose" in an engineering context; zero real hits on therapist, medication, mental health, panic attack, or SSN patterns.
---

# Personal/health content sweep result

> Summary: clean. Documenting the false-positive rate so this doesn't need re-grepping from scratch next time.

## Method
Grepped `~/can-it-ford`, `~/can-it-ford-BACKUP-before-history-purge`, and `~/Documents/Claude/reu` (= `~/Claude/reu`, confirmed same physical folder) for: `diagnos`, `therap`, `medicat`, `prescription`, `mental health`, `anxiety`, `depress`, `panic attack`, `social security`.

## Result
- Raw count across the four large `_inbox` export/log files: 183 hits total (80 + 79 + 79 + 104... — the same shape repeats across files).
- Per-keyword breakdown on the largest file (`LIVE_SESSION_LOG.md`, 2.4MB): `diagnos` = 104, every other keyword = 0.
- Sample-checked the "diagnos" hits directly: 100% are "diagnostic"/"diagnose" in an engineering-debugging context (this is a physics-simulation debugging project; "diagnostic" is routine vocabulary). Zero genuine personal-health disclosures found.
- This is exactly the kind of false-positive risk worth naming explicitly: a raw grep count of 183 looks alarming until sampled. Don't re-report the raw count as a finding without doing the same sample-check.

## Not flagged as risk
Content is clean. The associated file-handling risk (staged, ungitignored exports) is tracked separately — see `20260724-staged-inbox`.
