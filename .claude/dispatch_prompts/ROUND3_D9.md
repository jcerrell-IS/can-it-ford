# ROUND 3, D9 MOVING-DRIVER

Read `ROUND3_SHARED.md` first.

## Your non-monotone Yaris is the most important thing in this round. It is routed.

You flagged it rather than letting the tidy table carry it: the at-rest gate
error is monotone for the Rogue (94.4, 46.8, 43.7) and the Silverado (157.1,
86.9, 27.2) but **non-monotone for the Yaris: 63.3, 37.1, 52.3**, improving then
worsening, with the smoothly-falling ratio (3.755, 1.695, 0.832) not to be
mistaken for convergence.

That has gone to D12, which owns convergence, with the reason it matters there:
D12 withdrew its own claim that "dx is the controlling variable" after an
adversarial review, on the grounds that dx is fully confounded with dt,
substeps, h and particle count and the response is non-monotone. **Your Yaris is
a second non-monotone instance, on a different scene and a different coupling
path, and it supports that withdrawal.** Two independent origins.

You were right to tie it to CLAUDE.md item 5 and Steffen 2008 (L-5) at fixed
PPC = 8. Keep that framing.

## Two artifacts you asked for are readable. You do not need them moved.

You wrote: "~/Downloads remains unreadable to this process, so the mu=0.55
provenance audit and the PLY-loading analysis have not reached me directly, move
them and I'll read them."

They do not need moving. Both exist outside `~/Downloads`, verified at 22:38:

    /Users/josie/Claude/reu/compass_artifact_wf-65474f37-43a9-5ab0-817a-2b78217ff50f_text_markdown.md
      "Citation Provenance Audit: The mu = 0.55 Friction Coefficient in
       Azhar, Pauwels & Bui (2023)"
    /Users/josie/Claude/reu/compass_artifact_wf-82c51733-4a8b-559a-b300-fe37294b3009_text_markdown.md
      "Code-Level Analysis: PLY Loading in kks32/mpm-engine (splats module &
       load_vehicle)"

Mirrors under `~/Documents/Claude/reu/` and in the Desktop corpus. To resolve any
8-hex id: `find /Users/josie/Claude /Users/josie/Documents /Users/josie/Desktop
-maxdepth 5 -name '*<id>*'`.

## The friction number in your own scene is unreconciled, and it is a fourth value

Your moving scene uses `COLLIDER_FRICTION 0.4`. The canonical floor is 0.55. The
guideline convention is 0.3. Smith 2019 swept 0.3 and 0.78. That is four live
values across the project and yours is the only one nobody has traced.

Establish where 0.4 came from, live, from the driver and its history, not from
memory. If it is an unsourced choice, say so plainly, which is the same finding
D5 recorded for two of the three sweep masses. Then send D4 a one-paragraph
confirm-or-correct on your own line of the consolidated mu entry (shared
section 3), covering the 0.4 only. Do not restate the whole finding.

This matters to your own result: D5 established that the STUCK verdict for the
large_4wd requires mu at or above roughly 0.40, so your scene is sitting
essentially on that boundary.

## Run physics-skeptic. Your percentages are still marked UNREVIEWED.

You correctly marked them rather than faking the review. Now run it. The
standing rule is that a percentage, force, verdict count or distance gets the
`physics-skeptic` subagent before it is finalised, and it caught D5's headline
this afternoon, which is the strongest argument for running it on yours. If it
is unavailable, keep the UNREVIEWED marks and say the connector was unavailable.

## What survives from your last turn, unchanged

The corner structure result stands and is corroborated: the failure lives in the
under-resolved, low-friction, light-vehicle corner, and D5 found the same corner
shape on the stationary Silverado from a different scene and coupling path.
State that as two independent origins, carefully: different scene, different
coupling, same corner.

The seeded-cache mechanism stands: the Yaris rungs cost 6.0 s and 8.6 s only
because the SDF was already cached from the 35-minute first build, the same
mechanism that made the Rogue's finest rung the cheapest run in the set. That is
worth keeping as a stated result, not a footnote, because it is what made the
third ladder affordable at all.

## Skills and state

Call `flood-mpm-debugging-reference` and `mpm-technical-deep-reference`. Run
`physics-skeptic` before finalising. Ten commits unpushed, zero binaries in the
branch, videos and frames correctly withheld under E8 at
`figures/moving_vehicle_d9/`. Held pending Josie's per-branch check; do not
re-ask each turn. Vista queue empty at 641 SU; LS6 unreachable non-interactively,
so do not plan anything behind it.
