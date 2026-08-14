# Register items 17, 18 and 19 are branch-only, 2026-08-14

Written under DISPATCH 1, whose definition of done requires this note. **No merge was
performed and none should be performed from this branch.** Register reconciliation is
owned by DISPATCH 4, which reconciles all three divergent states together. This file
exists so that decision is taken deliberately rather than by whichever branch merges
first.

Every number below was measured live on 2026-08-14 in the worktree
`/Users/josie/can-it-ford/.claude/worktrees/rtfd-test-phase-1-4-569130`. Nothing here is
carried from a session summary.

## The register exists in three divergent states

`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` is declared by CLAUDE.md as "the sole
authority for any factual claim it covers". It currently disagrees with itself three ways.

| Ref | Lines | Adds |
|---|---|---|
| `origin/main` | 656 | baseline |
| `claude/rtfd-test-phase-1-4-569130` (this branch, as committed) | 681 | Section J items **17, 18, 19** |
| `claude/rtfd-test-phase-1-4-569130` (this branch, after today's edit) | 689 | item 18 correction, Al-Qadami verification |
| `claude/friction-resolution-reconcile-84465d` | 817 | D8c, D9, A6b |

Measured with `git show <ref>:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md | wc -l`.

## Items 17, 18 and 19 exist on this branch only

Tested by grepping each item's headline string against the other two register states.
All three return **0** on both:

| Item | Headline string tested | `origin/main` | `friction-resolution-reconcile-84465d` |
|---|---|---|---|
| 17 | `THE g64 SETTLE GATE IS NON-DETERMINISTIC` | 0 | 0 |
| 18 | `TWO INDEPENDENT RESOLUTION-DEPENDENCE` | 0 | 0 |
| 19 | `ITEM 15's DIRECT TEST HAS NOW BEEN RUN` | 0 | 0 |

So the three items are not duplicated anywhere and cannot be recovered from another
branch if this one is lost. That is the reason DISPATCH 1 treats the push as urgent
rather than as housekeeping: register item 16 records six canonical margins becoming
permanently unverifiable when job 866887 overwrote the g48/g96 run directories on
2026-07-26 with no tracked copy anywhere.

## What changed in the register today, and what did not

**Changed, item 18.** Its standing consequence was strengthened from "one commit is one
source" to "one **measurement** is one source". The old phrasing was too narrow: two of
this measurement's three write-ups are not the commit. The three are `ed8bf8e`'s commit
body, the table at `docs/SESSION_TRACK1B_2026-08-13.md:233-235`, and the primary store
`data/rogue_silverado_slide_classification_2026-08-13.csv`. All three `rs_silverado_*`
rows carry one `source_job`, **3362208** on LS6 A100. One job, one measurement, three
write-ups.

**Also changed, item 18's closing sentence.** It read "Item 15 is unaffected and remains
the open item: the direct g128 canonical test still has not been run." That was true when
written and was superseded within the same branch by item 19. It is now marked superseded,
with the scope stated: **8 of the 17** canonical configurations remain untested at g128
(3 `sweepD` and 5 `sweepV`, including `sweepV_g64_v0p5`, the only STUCK run). Verified
against `data/all_runs_inventory.csv` on main, read-only: 17 rows, 9 mass/grid plus 3
`sweepD` plus 5 `sweepV`.

**Added to item 19.** The Al-Qadami 2023 verification, below.

**Deliberately NOT changed.** Item 17's scope statement, that item 15's test "should be
run at g96 and above, or repeated at several seeds", is preserved verbatim as DISPATCH 1
requires. Steffen, Kirby and Berzins 2008 needed no addition: it was already cited in the
register at two places, line 79 and inside item 19, not only in the commit body.

## A correction to the dispatch's own supporting evidence

DISPATCH 1 instructed: correct item 18's phrase "one finding in one commit" to "one
measurement", because the same table "also appears in `docs/SESSION_TRACK1B_2026-08-13.md`,
added by `b62d554`, 44 minutes before `ed8bf8e`."

**The conclusion is right. The evidence given for it is wrong in three ways**, all
verified live:

1. **The phrase does not exist.** `grep -n "one finding in one commit"` on this branch's
   register returns nothing. The actual phrase was "one commit is one source, however many
   sections it has".
2. **`b62d554` did not add the table.** `git show b62d554:docs/SESSION_TRACK1B_2026-08-13.md`
   contains **zero** occurrences of 6.9669, 1.8105 or 1.5557. `git log -S` across all refs
   names the sole introducing commit as **`1a868f3`**.
3. **The direction and the interval are both wrong.** `ed8bf8e` is 2026-08-13 06:34:52
   -0500; `1a868f3` is 06:54:07 -0500. That is **19 minutes AFTER**, not 44 minutes before.
   `ed8bf8e` is an ancestor of `1a868f3`. Author and committer timestamps are identical on
   both commits, so this is not rebase distortion.

This is recorded rather than quietly fixed because it is item 18's own failure mode
recurring inside the fix for item 18: a confidently specific claim, carried forward,
that does not survive a live check. The lesson item 18 states is the one that caught it.

## Al-Qadami 2023, moved from UNVERIFIED to verified, with two limits

DISPATCH 1 flagged this citation as absent from the 115-row research corpus manifest and
required Scite or Consensus before it could be cited. Retrieved via Scite full text:

**Al-Qadami et al. 2023**, *Understanding the Stability of Passenger Vehicles Exposed to
Water Flows through 3D CFD Modelling*, `10.3390/su151713262`, *Sustainability* 15(17):13262,
gold OA, CC-BY, **no editorial notice**, tally 2 total / 0 supporting / 0 contrasting.
BibTeX was already in-repo at `docs/LIT_QUEUE_2026-07-30.md:276`, so the paper was known
to the project; what was unverified was the claim made about its content.

The mesh-independence study is confirmed verbatim from the full text: *"The
mesh-independent study was performed by testing a total of four mesh blocks with cell
sizes of 0.1, 0.075, 0.05, and 0.025 m."* Cell size 0.05 m was selected on three stated
criteria.

**Two limits on use, both of which must survive into any write-up:**

- The superlative in the project notes, that this is the field's **only** mesh-independence
  study for a flood-vehicle result, is **not verified** and should not be written down.
- It is **FLOW-3D, finite-volume VOF**, not MPM. Steffen 2008's fixed-particles-per-cell
  mechanism therefore does not apply to it, and its converged cell-size selection neither
  corroborates nor contradicts item 19's non-monotone MPM ladder. It is a precedent for
  **how to report** a refinement study. The contrast is the contribution: their study
  converged and selected a cell size, this project's does not converge.

## Ownership overlap, declared rather than left to be discovered

A standing ops addendum issued 2026-08-14 17:30 lists
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` as **DISPATCH 4 only**. This session
edited that file before the addendum was issued, because DISPATCH 1's own definition of
done required it: *"Correct register item 18's phrase ... to 'one measurement'."*

**This is not a collision on disk.** The edit is confined to
`claude/rtfd-test-phase-1-4-569130`. DISPATCH 4 writes the register on its own new branch
off main, and its concrete first step is to `git show` this branch's copy read-only. No
shared file, no shared index, no shared worktree. Main's register is untouched, verified
live: `git diff origin/main -- <register>` in the main checkout returns empty, and the main
tree's dirty set is unchanged at 26 entries.

**The one thing that changed for DISPATCH 4** is the baseline. Its three-way diff will now
see this branch at **689** lines, not the 681 its brief quotes. The delta is exactly the two
changes described above: the item 18 strengthening plus its correction notice, and the
Al-Qadami paragraph in item 19. Nothing else in the register was touched. If DISPATCH 4
prefers to reconcile from the pre-edit state, that is `658ecfa:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`
at 681 lines.

## What DISPATCH 4 needs to decide

1. Whether items 17, 18 and 19 merge into the reconciled register, and in what order
   relative to the friction branch's D8c, D9 and A6b.
2. Whether item 18's strengthened standing consequence should be promoted out of Section J
   into the register's general claim-discipline guidance, since it is not specific to the
   resolution finding.
3. D8c's refusal must be preserved through any merge. The gated driver is sha256
   `5215c38b`, 389 lines, and `:132-133` IS its floor plane, so CLAUDE.md item 3's
   `(:132-137)` was correct and the 2026-08-13 repoint to `:210-211` was reversed. A
   careless merge can silently re-apply a refused repoint.
