# SLOT d5-priorart

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-priorart, branch
claude/r8-priorart, branched off claude/can-it-ford-round-5-87a6d6 (NOT off add-ci-checks: the
staged bib lives on the round-5 branch and is absent from add-ci-checks and from origin/main).

You may write ONLY:
  paper/conference_101719.tex
  paper/can_it_ford_references_IEEE.bib
  docs/R8_PRIOR_ART_2026-08-18.md  (new)

NEVER TOUCH: the overleaf remote (no push); the main checkout; any other branch.

## WHERE THIS LEFT OFF, measured live
All four prior vehicle-fording works ARE in the bibliography and NONE is cited in the prose, in
either copy of the paper:
  he2026vehiclewater   10.1115/1.4071177        He et al 2026
  wasfy2015fording     10.1115/DETC2015-47142   Wasfy et al 2015
  khapane2014wading    10.4271/2014-01-0936     Khapane & Ganeshwade 2014
  alqadami2022moving   10.1111/jfr3.12828       Al-Qadami et al 2022
grep -c for each key in paper/conference_101719.tex          -> 0,0,0,0
grep -c for each key in overleaf/main:conference_101719_1.tex -> 0,0,0,0
An uncited bib entry does not appear in an IEEEtran reference list, so the paper does not cite
the prior art at all.

## THREE FURTHER FACTS FROM THE LITERATURE SWEEP, VERIFY EACH BEFORE ACTING
1. A prior-art fix already landed IN A FILE STAMPED DO-NOT-SUBMIT. Find it and establish what it
   contains before writing anything new.
2. The drafted prior-art prose cannot compile against its own paste target: reportedly 17 of its
   19 cite keys do not exist in the Overleaf bibliography. Re-derive that count yourself.
3. The corpus index NOW REPORTS all four papers as IN-PAPER, which has poisoned the project's own
   novelty gate: a document written today already repeats it. Correct the index's cited-status
   derivation in the same pass, or state precisely why it cannot be corrected from your scope.

## TWO TRAPS THAT HAVE ALREADY COST A SESSION
1. THE CANONICAL PAPER SOURCE IS NOT paper/conference_101719.tex. The paper builds from
   conference_101719_1.tex on overleaf/main with FLAT figure paths. The overleaf remote shares NO
   ancestor with origin, so `git push overleaf main` OVERWRITES rather than syncs. The local
   overleaf/main ref is 18 days stale at 6466dfa (2026-07-31). You are staging into paper/ on
   your own branch; a human moves it.
2. THE BIB KEYS DIVERGE between the repo copy and the Overleaf copy for at least six works
   (ccsa2010yaris vs ccsa2016yaris, xia2013 plus xia2010 vs the corrected xia2014). A naive
   auto-export breaks every \cite{}.

## THE RESEARCH
- D1's cross-referenced count supersedes every earlier figure: 15 vehicle-in-water simulations
  exist, 12 uncited. Authority is data/r5_citation_xref.tsv on claude/r5-research. Do not write
  "four" or "five".
- Al-Qadami et al 2022 claims a FIRST moving full-scale vehicle simulation, critical depth 0.38 m,
  minimum D x V 0.39 m2/s. Its mesh-independence detail is UNVERIFIED (MDPI 403, ledger item 18).
- The corpus review's caveat is the honest positioning: "The most detailed flooded-vehicle force
  work is CFD/VOF (Al-Qadami et al., 2023), not particle-based."
- Xia is 2014, not 2013, four authors including Yejiang Wang. An instruction insisting on 2013
  was wrong.

VERIFY EVERY DOI TITLE AGAINST THE RESOLVED RECORD. Scholar Sidekick verifyCitation, or
auditBibliography on the whole .bib in one call.

## FIRST STEP
  git -C /Users/josie/can-it-ford show overleaf/main:conference_101719_1.tex | /usr/bin/grep -n 'cite{' | head -40
Establish what the paper actually cites today before writing one word.

## DEFINITION OF DONE
1. A related-work paragraph engaging all four works, in the tex, stating what this project does
   that they do not.
2. Every bib entry audited for title-versus-DOI agreement, mismatch count stated and each named.
3. A document listing repo-versus-Overleaf key divergences so the human move does not break cites.
4. The corpus novelty-gate poisoning either fixed or precisely characterised.
5. NOTHING pushed to overleaf.
