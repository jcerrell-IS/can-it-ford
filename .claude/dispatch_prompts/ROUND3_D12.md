# ROUND 3, D12 PROTOCOL-AND-RECHECK

Read `ROUND3_SHARED.md` first.

## The clamp-disabled comparison is yours. Ownership decided, take it.

You wrote: "The clean comparison is the one I declined an hour ago, and this
makes it more valuable: re-run the canonical scene with the clamp disabled and
nothing else changed. That converts 0.321-vs-0.702 from an uninterpretable pair
into a held-fixed comparison. Owner: this dispatch or D9, by agreement."

**Owner: you.** It is your confound, you framed the held-fixed design, and D9's
scene differs on four axes at once (SDF collider, COLLIDER_FRICTION 0.4, band of
one dx, driven rather than stationary), which is exactly what makes D9 the wrong
place to run a one-variable comparison.

Your own constraint holds and is the design: the forked driver must first
reproduce the canonical baseline before the clamp is touched, otherwise the
comparison inherits the driver difference you already identified as the bound on
your own answer. Run the reproduction as a gate, not as a formality: if the fork
does not reproduce 0.321 to a stated tolerance, stop and report that instead.

Note the driver constraint from D5, which affects how you fork: `sim_standing.py`
is shared across dispatches and its sha256 stamps runs, so **do not edit it in
place.** Fork it, and record both digests.

Your refusal to tabulate 0.321, 0.702 and 0.93 as a monotone progression was
right, and the reason is worth keeping in the write-up verbatim: reading it as a
progression would attribute to scene physics exactly what your own document
identifies as the bound on its own answer.

## Caution 2 is corrected, and a second instance just arrived to support you

You withdrew "your own crossed control says dx is the controlling variable"
after the adversarial review. Result 2 now correctly reads: the data exclude
depth-in-cells but do not establish dx, because dx is fully confounded with dt,
substeps, h and particle count, and the response is non-monotone.

**D9 has a second non-monotone instance, from a different scene and a different
coupling path.** The at-rest gate error is monotone for the Rogue (94.4, 46.8,
43.7) and the Silverado (157.1, 86.9, 27.2) but non-monotone for the Yaris:
**63.3, 37.1, 52.3**, improving then worsening. D9 also warns that the
smoothly-falling ratio (3.755, 1.695, 0.832) must not be mistaken for
convergence of the physics, and ties it to CLAUDE.md item 5 and Steffen 2008
(L-5) at fixed PPC = 8.

That strengthens your withdrawal rather than weakening it. Two independent
origins for non-monotonicity is a result in its own right. And it confirms your
instinct not to place D9's point on a dx axis: doing so would re-import the
over-claim you removed. Say why explicitly in the document, so the next session
does not helpfully re-add it.

## Your one dirty file

`data/slide_verdict_fragility_2026-08-13.csv` is modified in your worktree,
measured at 22:34, and you flagged "the truncated CSV restore still awaiting
you". Resolve it this turn rather than carrying it further:

- Diff it against the last committed version and state exactly what truncated
  and when.
- Restore from the committed blob if the committed version is the good one, or
  regenerate it if it is not, and say which you did.
- Commit it path-limited: `git commit -m "..." -- data/slide_verdict_fragility_2026-08-13.csv`.
  A bare `git commit -m` can sweep in another session's staged entries.

An uncommitted file does not survive a context compaction with its reasoning
intact, and this one has been pending across turns.

## Friction now enters your convergence result

D5 established that **resolution-dependence is itself friction-dependent**: at mu
= 0.30 a 37 percent refinement moves the margin from 10 to 11 frames, and the
large_4wd STUCK verdict requires mu at or above roughly 0.40. Register J15's
flip therefore needs a mu label, which D1 is establishing.

For you this means the confounded-variable list is longer than you wrote it. dx
is confounded with dt, substeps, h and particle count, and **the response to all
of them is friction-dependent**. If your clamp-disabled comparison holds
everything fixed except the clamp, state the mu it ran at, because a
held-fixed comparison at an unstated mu is only held-fixed within that mu.

## Skills and state

Call `flood-mpm-debugging-reference` and `mpm-technical-deep-reference`. Run
`physics-skeptic` before finalising any number; it is what caught D5's headline
and your own Caution 2.

Eight commits unpushed plus the one dirty CSV. Held pending Josie's per-branch
check; do not re-ask each turn. Vista queue empty at 641 SU if the fork needs a
batch run; LS6 unreachable non-interactively, so do not queue behind it.
