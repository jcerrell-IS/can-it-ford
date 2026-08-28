# ROUND 3, D1 PUSH-ORPHANED-g128

Read `ROUND3_SHARED.md` first. Answers to what you asked, then your next scope.

## Your open questions, answered

**Push for 641ac75: hold, and stop re-asking each turn.** Josie's standing
position is "authorize, but I verify each first", so every commit waits for a
per-branch go-ahead through `pushcheck`. You were right that the earlier
authorization did not carry forward. It still does not, and it will not, so
treat "held pending Josie" as the steady state rather than a question to reopen.
Your branch is at 1 unpushed commit, measured live at 22:34.

**register_integrity.py: not yours, and now assigned.** You identified the exact
fix (catch PermissionError, emit a distinct unchecked class) and correctly did
not apply it. D8 owns it now, with its own four-point patch. D11 measured the
same defect as a 10-to-0 swing with the register file unchanged. Three sessions
finding it and all three declining was the deadlock; it is broken.

## One correction you need to make to your own document

You wrote that 65474f37, 5e706c91, c963203d, a1fd6fdc, d50d614c and the
perplexity directory are "unreadable from here regardless", and warned that
whoever picks them up needs Downloads access first.

**That warning is false and it will misdirect the next session.** All six are
readable right now, outside `~/Downloads`, verified at 22:38. See shared section
1 for the paths. 65474f37 in particular is the mu = 0.55 provenance audit and
its TL;DR reads: mu = 0.55 is Azhar, Pauwels & Bui (2023)'s own spring-balance
laboratory measurement of their experimental rubber mat.

Correct that sentence in your document. Do not widen into friction or engine
choice, you were right that they are out of scope. Just stop the false warning
propagating.

## Your next scope: J15 needs its friction label

This is squarely yours and it is now load-bearing for two other dispatches.

You own `a6e42c1`, which answers register Section J item 15. J15 published the
Silverado SLIDE-to-STUCK flip from shared-n_grid refinement, quoted as "SLIDE at
g64 and g96 and STUCK at g128".

Since you wrote it, D5 has established that **resolution-dependence is itself
friction-dependent**: at mu = 0.30 a 37 percent refinement moves the margin from
10 to 11 frames, and the large_4wd STUCK verdict requires mu at or above roughly
0.40. D5 also retracted its own causal headline because J15 had already
published that flip.

So: **J15 as written does not record the mu its flip was measured at.** A reader
takes it as a resolution result when it is a resolution-at-a-specific-friction
result, and that friction (0.55) is the one D11 traced to a lab rubber mat.

Do this:
1. Read the runs behind J15 live and establish the mu each rung actually used.
   Do not infer it from the default.
2. Confirm or refute that J15's flip reproduces at the 0.3 convention. If the
   flip is mu-dependent, J15 needs a qualifier and D5's and D9's corner results
   both inherit it.
3. Write the finding into your own doc, name D4 as the owner of the register
   edit, and do not edit the register yourself.

## Skills and verification

Call `provenance-audit` for step 1 and 2. Run the `physics-skeptic` subagent
before you state any percentage or verdict count; if you cannot, mark the claim
UNREVIEWED rather than faking the review.

Machine state: Vista queue empty, 641 SU. LS6 unreachable non-interactively.
Neither is needed for this task.
