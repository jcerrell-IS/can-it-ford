# DRAFT: GitHub README badge row for jcerrell-IS/can-it-ford

Status: DRAFT, nothing pushed, nothing staged. Written 2026-08-23.
Every fact below was read live today, sources named per line.

## What is already there

`README.md` already carries a three-badge row (lines 5-7 as of today, do not
cite those numbers later, the file moves). Live content:

```markdown
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-green.svg)](LICENSE)
[![W&B](https://img.shields.io/badge/W%26B-experiment_tracking-yellow)](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-live_demo-blue)](https://huggingface.co/spaces/josiecerrell/can-it-ford)
```

So this is an ADD-a-build-badge-and-tighten job, not a from-scratch row.

## The build-status badge: the honest options

Measured live with `gh run list --branch main`:

| Workflow | On origin/main? | Latest conclusion on main |
|---|---|---|
| `csv-check.yml` (CSV Schema Check) | YES | success (all 7 most recent) |
| `sync-to-hub.yml` (Sync to Hugging Face Space) | YES | success 2026-08-17, 4 failures before it |
| `physics-consistency-review.yml` | YES | no run in the last 12 on main |
| `canford-checks.yml` | **NO** | n/a |

Consequence, and this is the part that decides the badge: a GitHub Actions
badge renders the state of a workflow file **on the branch you name**.
`canford-checks.yml` does not exist on `origin/main`, so a badge pointing at it
with `?branch=main` renders "no status" grey, not green. Pointing it at
`claude/add-ci-checks` instead would render a branch that is 440 commits ahead
of main and that no visitor can see as the default view.

Separately, per the local memory note, `canford-checks` cannot go on main
as-is: 3 of its 6 steps have no script on main and `count_claims` exits 1.
I did not re-verify that today, so treat it as recalled, not confirmed.

**Recommendation: badge `csv-check.yml`, and label it for what it actually
is.** It is the only workflow that is both present on main and green there.
Calling it "build" would overstate: nothing in this repo builds, and a schema
check is not a test suite.

## Proposed row

```markdown
[![CSV schema](https://github.com/jcerrell-IS/can-it-ford/actions/workflows/csv-check.yml/badge.svg?branch=main)](https://github.com/jcerrell-IS/can-it-ford/actions/workflows/csv-check.yml)
[![License: BSD-3-Clause (code only)](https://img.shields.io/badge/License-BSD--3--Clause_(code_only)-green.svg)](LICENSE)
[![HF Space](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-sm.svg)](https://huggingface.co/spaces/josiecerrell/can-it-ford)
[![W&B](https://img.shields.io/badge/W%26B-experiment_tracking-yellow)](https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford)
```

Changes from what is live now, and why each one:

1. **Added** the `csv-check` Actions badge. Real status, real link, green today.
2. **License badge relabelled** `BSD-3-Clause (code only)`. `LICENSE` opens with
   a SCOPE clause: BSD-3 covers original code and docs and explicitly does NOT
   cover redistributed third-party material, "in several cases, under terms that
   have not been established". A bare `License: BSD-3-Clause` badge on a repo
   that ships a derived Yaris hull of unresolved provenance reads as a clearance
   that has not been given. This is the one change I would not skip.
3. **HF badge swapped** to the official Hugging Face "Open in Spaces" asset
   rather than a hand-rolled shields.io badge that says `live_demo`. Target
   `spaces/josiecerrell/can-it-ford` confirmed public today.
4. **W&B moved last.** Unchanged otherwise, link confirmed as-written.

## Two things to decide before this lands

- `spaces/josiecerrell/can-it-ford` is public and is what the current badge
  points at. `can-it-ford-page` and `can-it-ford-lab` are private. If the
  public-facing Space is meant to become one of those, the badge target changes.
- If `canford-checks` does land on main later, add a second Actions badge then
  rather than pre-pointing at a workflow that is not there.
