# ROUND 3, D11 MOVING-VALIDATION

Read `ROUND3_SHARED.md` first.

## Your provenance chain is confirmed against the primary artifact

You reported mu = 0.55 as a spring-balance measurement of a lab rubber mat,
chaining out to a 1969 GM tyre brake-force study, general automotive and not
submerged, raising T_avail by 83 percent against the 0.3 convention.

Independently confirmed at 22:39 by reading the artifact's own TL;DR:

> "mu = 0.55 in Azhar et al. (2023) is a laboratory measurement of their own
> experimental rubber-mat surface, NOT a value copied wholesale from a prior
> paper. They measured it with a spring balance on the rubber mat used as their
> road-surface proxy, and cite Wong, *Theory of Ground Vehicles*"

Full paper: Azhar, Pauwels & Bui (2023). The artifact is
`/Users/josie/Claude/reu/compass_artifact_wf-65474f37-43a9-5ab0-817a-2b78217ff50f_text_markdown.md`,
readable right now, outside the TCC-blocked `~/Downloads`. Read it directly and
check your chain against it rather than leaving your version as the only record;
in particular verify the Wong link and the 1969 GM step, since those are the two
hops most likely to have drifted.

D4 has the register entry and it names you as the source of the chain. Send D4 a
one-paragraph confirm-or-correct on your own line only.

## Your register_integrity.py observation is now actioned

You flagged that the tool moved from "10 research-artifact, 1 unresolved" to "0
research-artifact, 11 unresolved" inside one session with the register file
unchanged, that 10 + 1 = 11 exactly, that only `185968e0` was genuinely
unresolved in both runs, and that someone running it cold would reasonably raise
a data-loss alarm over ten sources that are simply unreadable.

D1 and D8 found the same defect independently and all three of you declined to
fix it on ownership grounds. That deadlock is broken: **D8 owns it**, applies its
four-point patch, and D4 re-runs afterwards. A fifth point has been added to the
patch: the probe searches `~/Downloads` only, and every id it fails on is
readable elsewhere, so the resolver will search the mirrors and report which
root resolved each id. That removes the cause rather than relabelling the
symptom.

## Your Xia verification is settled, stop re-verifying it

You verified it a third time: print 2014-01, online 2013-10-11, four authors
including Yejiang Wang, and your Tier 1 already said 2014 in both the row and
the year-trap table. Your deeper point is the better one and it is the record
now: **Xia 2011 and Xia 2014 are different papers, not a year error**, so "Xia
2014" is not necessarily a miscitation. That is settled. Do not spend a fourth
pass on it.

## Your three biases all run the same direction. Quantify the combination.

This is your next scope and it is the highest-value thing in your lane.

You have three, each traced and each pointing the same way:

1. mu = 0.55 against the 0.3 convention: **T_avail up 83 percent**, makes
   NO-SLIDE easier to reach.
2. Unsteady flow raises drag **40 to 50 percent** (Azhar 2026), not modelled.
3. Yaw dependence spans **0.26 to 0.57**, a 2.2x spread in the one parameter the
   margin is linear in.

Individually each is a caveat. Together they are a directional error budget, and
nobody has composed them. Do that:

- State the margin expression the three enter, explicitly, with a units check.
- Propagate each bias through it and give the combined effect on the margin, with
  the sign, under a labelled and reversible assumption about how they compose
  (independent, or worst-case aligned, and say which you chose and why).
- State which published verdicts the combined budget could move, and which it
  cannot. 16 of 17 gated verdicts are SLIDE, and bias 1 pushes away from SLIDE,
  so the conservative and optimistic directions are not symmetric across the set.
- Do not propose changing any run. You were right that the correct ask is that mu
  be reported with its provenance and the 0.3 convention named beside it. Extend
  that to all three.

Two inputs you did not have:

- **D5:** resolution-dependence is itself friction-dependent. At mu = 0.30 a 37
  percent refinement moves the margin from 10 to 11 frames, and the large_4wd
  STUCK verdict needs mu at or above roughly 0.40. So bias 1 is not a simple
  offset, it interacts with resolution, and your composition assumption has to
  say whether it treats them as separable.
- **D9:** the moving scene runs `COLLIDER_FRICTION 0.4`, a fourth live value,
  sitting essentially on D5's 0.40 boundary. D9 is tracing its provenance.

## On the bare 0.3 unit collision

Your observation that a bare 0.3 keeps merging across quantities is correct and
it just cost this project a relay. Write the disambiguation once, as a table
with units attached to every 0.3 in the project, and make it the thing people
cite instead of the number.

## Skills and state

Call `provenance-audit` for the artifact check and `mpm-technical-deep-reference`
for the margin expression. Run `physics-skeptic` on the combined error budget
before you state any percentage; if it is unavailable, mark UNREVIEWED and say
the connector was unavailable rather than faking it.

Your branch has 0 unpushed. No GPU needed. Vista queue empty at 641 SU, LS6
unreachable non-interactively.
