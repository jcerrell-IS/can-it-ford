# ROUND 3, D5 THREE-CLASS-MATCHED

Read `ROUND3_SHARED.md` first.

## The retraction was the right call and it has been propagated

`59d3283` retracted the headline "removing the resolution confound flips the
large_4wd verdict" as FALSE, because register J15 already published that flip
from plain shared-n_grid refinement, and your matched arm at dx 0.0849 sits 16.9
percent finer than the g128 where it was already known. Corrected form:
refining dx below roughly 0.10 m flips it; matching dx makes the three
comparable, it is not what produced the flip. Section 2's confound measurement
is unaffected and stands.

I had relayed your original causal framing onward as a headline result. I have
corrected it to Josie and it is corrected here. The `headroom_x 1.0447` figure
(safety factor about 3.5, not 40) and the "passthrough rises with refinement"
retraction are both carried forward too.

Your finding that **resolution-dependence is itself friction-dependent** has been
routed to D1, which owns the commit answering J15, with instructions to
establish which mu each J15 rung actually ran at. If J15's flip does not
reproduce at the 0.3 convention, your corner result inherits the qualifier and
so does D9's.

## Two housekeeping corrections

**Your unpushed count.** You reported six (f53066a to 59d3283). `git rev-list
--count <branch> --not --remotes=origin` says **five**, measured at 22:34.
Re-check before quoting it; one of the six is probably already on a remote.

**Job 3364582 needs no action, and cannot get any.** LS6 is unreachable
non-interactively: the ControlMaster socket is cold and demands a TACC token at
an interactive prompt. Both node allocations have expired. The job is moot
either way, so leave it. Do not queue further work behind LS6.

## The retracted-hull guard hole: do NOT edit the driver. Build the checker beside it.

You found that `sim_standing.py`'s retracted-hull guard matches on **filename**,
so both retracted hulls stay reachable from the pool directory under different
names. You wrote the sha256 fix into the doc and did not apply it, because
changing the driver mid-experiment would invalidate the sha256 stamping your
runs, and other dispatches share the file. That reasoning is correct and stands.

The way out is not to edit the driver at all. Write a **standalone preflight
checker** that reads the pool directory, hashes every candidate hull, and fails
loudly on any digest matching a retracted hull, regardless of filename. It runs
before the driver, changes no stamped sha256, and touches no shared file.

Then hand the in-driver sha256 fix to D4 as a register entry with the note that
it should be applied only once the matched-dx set is final. Name the two
retracted digests explicitly in your document so the guard cannot be rebuilt
from a filename list again.

## Your open task, and what to add to it

Your task list still shows **"Classify and write up three-class results"** open.
Finish it. Two additions:

1. **Carry mu into every verdict row.** Your own finding makes an unlabelled
   verdict incomplete: STUCK for the large_4wd needs mu at or above roughly
   0.40, and 0.55 is the value D11 traced to a lab rubber mat (Azhar, Pauwels &
   Bui 2023, spring balance, citing Wong). A verdict table without a mu column
   invites exactly the misreading you just retracted.
2. **State the P-2 non-commensurability inside the write-up, not as an aside.**
   The gate's geometric baseline is 0.0905 to 0.1041 and the 0.10 limit sits
   inside that spread. This has been routed to D4 because CLAUDE.md item 7
   publishes a seven-run P-2 failure list that may be partly measuring hull
   geometry. Give D4 your baseline numbers with their source so it can verify
   rather than take them on your word.

## Corroboration you did not have

D9, on a completely different scene and coupling path (SDF collider, driven not
stationary, COLLIDER_FRICTION 0.4), found the same corner structure you found on
the stationary Silverado: the failure lives in the under-resolved, low-friction,
light-vehicle corner. Two independent origins, which is worth stating as such,
carefully: different scene, different coupling, same corner shape.

## Skills and state

Call `mpm-technical-deep-reference` for the classification, and run
`physics-skeptic` before finalising any percentage or verdict count; it caught
the last headline. Five commits unpushed, held pending Josie's per-branch check.
Vista queue empty at 641 SU if you need a batch job; LS6 offline.
