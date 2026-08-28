# ROUND 3, D10 SCENE-AND-DOMAIN

Read `ROUND3_SHARED.md` first.

## Your two halves are blocked on each other. Here is the order that breaks it.

You established that a bounded domain cannot measure road-realistic slopes,
because conserving volume in a bounded domain forces redistribution larger than
the effect being measured, and that the correct instrument is an open channel
with a real mass sink, which is the Zhao 2019 BC you wired and never validated.

So the cross-slope sweep is blocked on the BC, and the BC has no validation
case. **Validate the BC first, on a case with a closed-form answer, before it
carries any cross-slope result.** Concretely:

1. Still-water column, no slope, outflow open. Mass leaving per unit time has an
   analytic form. Check that the BC reproduces it, and check that total mass is
   conserved to a stated tolerance across the domain plus the sink.
2. Steady uniform inflow equal to outflow. The free surface must hold a constant
   level. A drifting level is the failure this BC exists to prevent, and it is
   the exact thing a bounded domain hides.
3. Only then run the cross-slope sweep, and report the BC's validated tolerance
   alongside every slope result.

Zhao, Bolognin, Liang, Rohe and Vardon 2019, Computers and Fluids 179, 27-33,
DOI 10.1016/j.compfluid.2018.10.007, implemented in Anura3D. This is a
translation into warpmpm, not a port; that distinction is in CLAUDE.md and it
means their published verification cases are the right targets for step 1 and 2.

## The raw JSON series: do the durable copy now, leave the force-add to Josie

You flagged that the 8 raw JSON series (3.8 MB, no E8 content) are gitignored
under `data/`, exist only on purgeable `$SCRATCH` and in your local scratchpad,
and that this is the exposure register item 16 was written about. You are right
to treat force-adding past `.gitignore` as a deliberate act you will not take
unsanctioned.

Split the decision. The **risk** is that the only two copies are both volatile;
the **question** is whether they belong in git. You can remove the risk without
answering the question:

- Copy them now to a durable, non-purgeable location outside `$SCRATCH` and
  outside the scratchpad. Vista `/work` is at 5.49 percent of a 1024 GB quota,
  so 3.8 MB is free there and it is not purged. A second copy under
  `~/Desktop/` or `~/Documents/` on the Mac is equally valid.
- Record the paths and the sha256 of each file in your document, so a later
  session can verify it has the same bytes.
- Leave the force-add question open for Josie. State it as one line: "8 files,
  3.8 MB, no E8 content, currently gitignored under data/, now duplicated at
  <path>; force-add or not?"

Do not force-add past `.gitignore` without an explicit yes.

## D13's Chrono defect, pinned down since your last turn

D13 traced it further and it changes your rule. The bad value originates in
Bullet's trimesh raycast callback, and it lands on the **NORMAL**, not the
height: Chrono populates it correctly from Bullet
(`ChCollisionSystemBullet.cpp:402-403`), and the returned normal is 0.9998 off
vertical. D13 has marked it UNREVIEWED, correctly: it is a claim against a
third-party library from one session and should reproduce upstream before anyone
cites it as a Chrono bug.

Your operational rule, from D13: on a reconstructed OBJ scene, use **rigid or
FEA tyres** (they go through the contact engine and never consult `GetNormal`),
or use a **heightfield or box patch** instead of a trimesh. D13 has also offered
a CPU-only x86 reproduction to establish whether it is aarch64-specific; that is
approved, so you will get an answer.

## Your pattern observation stands and should be written up as a rule

Five instances of "a wrong configuration that produces a plausible number
instead of an error", three with no engine-side guard, two of them yours. Your
own arms gave you the number that makes it concrete: excursion grows with slope
in the downslope direction, 0.664, 0.937, 1.562 m, so the steeper the slope the
further the vehicle travels toward the nearest patch edge, and a margin sized at
S=0 is wrong by 2.35x at S=0.06. `required_patch_margin_m` now extrapolates
rather than clamps, 31/31 tests pass.

Add the shared addendum's own instances to the tally before you finalise the
count: this round produced five more of the same class, where an absent result
from a partial or blocked view was read as evidence of absence. That is the same
failure with a different surface, and it is worth one sentence distinguishing
them: yours is a silent wrong value, theirs is a silent empty result. Both need
a guard that fails loudly.

## Skills and state

Call `flood-mpm-debugging-reference` for the BC validation and `bug-triage-protocol`
for the pattern write-up. Run `physics-skeptic` before finalising any excursion
or margin number.

Seven commits unpushed, held pending Josie's per-branch check. Vista queue empty
at 641 SU and `/work` is 5.49 percent used, so the durable copy has room. LS6 is
unreachable non-interactively: its socket demands an interactive TACC token, and
both node allocations have expired. Do not plan the cross-slope sweep behind LS6.
