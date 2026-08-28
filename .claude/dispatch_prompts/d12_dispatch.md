### DISPATCH 12, Mac, the measurement protocol, and a canonical result that needs re-checking

```
SCOPE DECLARATION
MACHINE: Mac, plus one small LS6 BATCH instrumentation run.
BRANCH: new, claude/fork-protocol-<slug>, off main.
MAY WRITE TO: that branch, analysis/ and docs/ within it.
NEVER TOUCH: main; the canonical stores; the register; any other fork branch.

PART A. THE MEASUREMENT PROTOCOL, ALREADY SETTLED BY A 68-PAPER SEARCH AT 91% COVERAGE
There is NO universal frame count and NO universal force-settling threshold. Stop
looking for one. The defensible protocol, which this dispatch implements:
  1. Detect and EXCLUDE initial and final transients.
  2. DEMONSTRATE stationarity for the specific observable being reported.
  3. Attach uncertainty computed from CORRELATED samples, not from raw sample count.
Implement using: automated equilibration detection (Chodera 2015,
DOI 10.1101/021659) and correlated-data error estimation by blocking
(Flyvbjerg and Petersen 1989, DOI 10.1063/1.457480). Both are from molecular
dynamics, which has the most rigorous practice on exactly this question.
FOR A FINITE MOVING PASSAGE: report a PRESPECIFIED constant-speed interior window,
its mean, its filter and window sensitivity, and correlated uncertainty. This is a
PROTOCOL, not a transferable run length. Acceleration waves and force oscillations
can persist inside that window. Towing-tank practice is the source; see also
Brouwer et al. 2019 (DOI 10.1016/J.OCEANENG.2019.04.068) on random uncertainty of
statistical moments, Jentzsch et al. 2021 (DOI 10.1007/s00348-021-03151-5) on steady
and unsteady towing-tank velocities, and Thomas et al. 2007
(DOI 10.1080/14484846.2007.11464528) on water stilling, where the FIRST SLOSHING MODE
governs inter-run offset time.
IF THERE IS NO STEADY STATE, SAY SO AND REPORT SOMETHING ELSE. Slamming, water entry
and impact loading generally have no steady force; the accepted practice is to report
peak distributions, impulses, envelopes, or cycle and event statistics with repeat-run
uncertainty. Our own moving scene shows Fz oscillating by a factor of two or more at
150 frames with no steady value, so this is the likely outcome. An impulse is a
legitimate result; a fabricated steady force is not.
FOR THE VERDICT ITSELF: incipient motion is PROBABILISTIC and RECORD-LENGTH DEPENDENT.
The literature defines a movement probability or activity rate with detection
uncertainty, NOT a single critical stress. Our criterion is a joint condition held for
3 consecutive frames, and register item 15 records a canonical arm at margin_frames 0
and another one frame from flipping. Reframe the verdict as a probability with a
stated record length. This is the single most defensible upgrade available to the
project's headline result.

PART B. NON-DETERMINISM, CONFIRMED AS A REAL MECHANISM
The search confirms that non-associative, order-dependent reductions can produce small
drift OR ALTER DISCRETE GATES. That is our exact symptom: three runs at identical
configuration, geometry and seed gave settle_vmax_final 0.865234, 0.861557 and
0.594807 against a peak identical to four decimals, with two failing the settle gate
and one meeting it at 974 frames. Mitigations named: fixed-order or sorted reductions,
reproducible reductions, and higher-precision accumulation. Practice: report OUTCOME
SPREAD and GATE-PASS FREQUENCY across repeats; no universal repeat count exists, and
independent-start ensembles are the stronger convergence check.
ALSO FIX, cheap and high-value: the SDF cache never hits because load_vehicle draws
60,000 RANDOM surface samples, so back-to-back loads differ by 2.22e-16 m, one ULP,
which changes build_sdf_cached's content hash and forces a rebuild every run. Seed
that sampling. Note this is the same 60,000-sample mechanism as register E2.

PART C. THE CANONICAL RE-CHECK, AND THIS IS WHY THIS DISPATCH EXISTS
A 16-paper search at 99 percent coverage found NO paper reporting the 0.93 to 1.01 dx
floor-penetration plateau we measured, and NO defensible minimum cell count across a
shallow water layer. So our measurement appears to be novel, and it is unanchored.
MEASURED: penetration saturates at 0.93-1.01 dx in the MOVING scene.
MEASURED LIVE: canonical g64 has realized_depth_m / dx = 0.2944294473 / 0.1472147237
  = EXACTLY 2.000 cells across the water depth (CLAUDE.md L-3).
INFERRED AND UNTESTED: if that penetration is a property of the enforced plane BC
  rather than of one scene, the corrupted fraction of about 1/depth_cells implies
  roughly 50 PERCENT of the canonical water column sits in a boundary-corrupted layer.
DO NOT ASSERT THIS. MEASURE IT. Instrument the existing canonical scene for particle
z-position relative to the floor plane, report penetration in dx, and state plainly
whether it transfers. Both answers are publishable and the question is cheap.
MECHANISM HYPOTHESIS TO TEST: this is likely a kernel-support effect. With a quadratic
or cubic B-spline a particle influences nodes 1.5 to 2 cells away, so a particle can
sit about a cell below a node-enforced plane and still be seen. If so, penetration
scales with basis-function support width. The anchor for that analysis is Steffen et
al. 2008 (DOI 10.3970/CMES.2008.031.107), which systematically varies basis functions,
boundary treatments and GIMP smoothing length; it is the strongest mechanistic anchor
found and it does NOT establish our plateau, so this is an open question we can close.
RELATED, and useful: Schulz and Sutmann 2019 report that traditional grid-based
boundary treatment distorts stress MULTIPLE GRID LENGTHS into the body and propose
image particles to reduce it. Baumgarten and Kamrin 2023 (DOI 10.1002/nme.7217)
analyse and mitigate MPM spatial integration errors. Neither is validated for
free-surface water; label them as mechanistic evidence only.
NO PAPER REPORTS AN ACCEPTED CORRECTION for a smeared near-wall layer, so a
calibration is NOT established practice. Do not invent one and call it standard.

DEFINITION OF DONE
An implemented, tested stationarity-and-uncertainty module used by Dispatch 9's
outputs; a written protocol doc citing the sources above; the seeded-sampling fix with
a demonstrated cache hit; and the canonical floor-penetration measurement reported in
dx with a clear yes or no on whether the 2.000-cell canonical scene is boundary
corrupted. If it is, flag it to a human rather than editing any canonical claim
yourself, because it bears on a published result and that is outside this scope.
```

OPERATING PROTOCOL, applies to you in full:

```
OPERATING PROTOCOL:

Before starting: check git log, .remember/ files, and the research
citations you were given, in that order. Do not duplicate work already
done elsewhere in this bundle.

When you hit an obstacle: try a fix. If it doesn't work, try a second,
genuinely different approach, not a variation of the same one. Before
concluding you're stuck, check whether an available connector or subagent
resolves it:
  - DeepWiki, for any question about how a library/repo actually behaves.
    Treat its answer as a hypothesis to verify against source, not fact.
  - The physics-skeptic subagent, before finalizing any claim involving a
    percentage, force, verdict count, or distance. If it's unavailable this
    session, say so explicitly and mark the claim unreviewed, do not fake
    the review.
  - Wolfram, for any physical parameter, unit conversion, or equation
    before it becomes a stated claim.
  - Scite, for any citation, DOI, or threshold before it's written as
    settled.
  - register_integrity.py (or the project's equivalent), before any commit.

Prefer proceeding on a clearly-labeled, reversible assumption over
stopping. State the assumption explicitly, in the commit message or the
write-up, so it can be revisited later without re-deriving it from
scratch.

Tag every factual claim by its source: read directly, recalled from
context, or inferred. Tag every solver/engine claim by which engine it
applies to. Never state a number from memory when you could check it live.

Keep working on everything else in your scope even if one specific thing
below is blocked, do not let one blocker stop the whole session.

Flag, rather than silently proceed past, only these four things:
1. You are about to discard, overwrite, or force-push over uncommitted
   work you did not create and cannot verify is safe to lose.
2. You've found two independently-reported results that genuinely
   disagree about the same physical quantity, not just different framing
   of the same thing, and resolving which is correct requires a judgment
   call, not just more data you can go get yourself.
3. You are about to edit a canonical file outside your declared scope.
4. A genuine hard-stop case: real financial cost, an exposed credential,
   a destructive/irreversible action, or anything matching the project's
   existing standing hard rules.

When you flag one of these: write it clearly to a named file (not just an
inline comment), keep working on everything else in your scope that isn't
blocked by it, and do not treat the flag as ending the session.

Write with an engineer/scientist's discipline throughout: state
assumptions before acting on them, prefer a falsifiable test over a
plausible-sounding claim (a no-forcing control, a held-fixed comparison,
a second seed), and write up a result the same way whether it confirms or
overturns something already published.

Before any push: confirm the target branch, stage explicit paths only,
never a blanket add, and confirm the push actually landed afterward,
don't just assume the command succeeding means the remote updated.
```
