### DISPATCH 7, no repo, research corpus Sprint 2 and the citations the figures need

```
SCOPE DECLARATION
MACHINE: Mac, no GPU, no repo access needed.
MAY WRITE TO: ~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/ ONLY, and its
_BUILD_LOG/ subdirectory.
NEVER TOUCH: the git repo at /Users/josie/can-it-ford in any way; any file
outside the corpus tree; any original source file (this tree is symlinks, keep it
non-destructive); anything credential-related.

WHERE THIS THREAD LEFT OFF
PROGRESS_LOG.md, last entry: steps 5, 6 and 7 extraction are COMPLETE. 1,477
Sprint-2-only multi-member clusters covering 9,314 files (one representative
each) and 4,401 true singletons were extracted, 5,878 representative reads, zero
read errors, saved to step6_extract_batch1-3.txt and step7_extract_batch1-5.txt.
Step 5 resolved 326 real Sprint-1 duplicates and correctly re-tagged 592
zero-byte matches as empty-file rather than letting them inherit an unrelated
verdict. It is STOPPED, waiting on a serial-versus-parallel decision, with the
extraction cost already paid. That makes it the highest-leverage idle item in the
project.

THE DECISION IS MADE: PROCEED SERIALLY IN BATCHES
Work the extracted snippets in order, appending verdicts. Do not re-extract, do
not re-checksum. Checkpoint to PROGRESS_LOG.md every ~500 snippets so an
interruption costs at most one batch.

FOUR TARGETED QUESTIONS TO ANSWER ON THE WAY, each currently blocking other work
1. THE refs.bib CLUSTER, blocking any bibliography work. The corpus's own Phase C
   found THREE distinct versions across six locations: {6a5958, overleaf_fresh}
   match; {canitford_tex_backup} is its own; {files (3)} is its own;
   {deliverables root, deliverables/paper/overleaf} match and are a third. Per
   memory overleaf-tex-is-canonical.md the paper builds from Overleaf, so
   deliverables/paper/overleaf/ is the default, but confirm before calling the
   others stale. This is live: a BibTeX key collision was caught this week
   (akinci2012 already used for a DIFFERENT 2012 Ihmsen/Akinci paper, renamed
   akinciN2012coupling), and a separate docs/PENDING_BIB_ENTRIES_2026-08-13.md
   exists on its own branch. Produce a definitive table: which version is
   canonical, what each other version uniquely contains, and whether any unique
   entry is cited anywhere.
2. IS Al-Qadami 2023 IN THE CORPUS ANYWHERE? It is cited in project dispatches as
   the field's only mesh-independence study for a flood-vehicle result, and a
   search of the 115-row Sprint 1 manifest returns ZERO hits. Search the full
   Sprint 2 corpus. If it genuinely is not there, say so plainly: a citation
   load-bearing for a planned write-up has no retrievable source on this machine.
3. THE OPTICS COEFFICIENTS, directly unblocking Dispatch 6's figures. Search the
   corpus for full text (not abstracts) of Stewart, Fox and Harnett 2013 and
   2014, and Guillen et al. 2000. Dispatch 6 needs the real
   attenuation-coefficient-per-mg/L regression; without it that coefficient stays
   labelled "tuned" and the render cannot be called citable. Report hit or miss
   with the path.
4. THE THREE VEHICLE-CLASS PAPERS. Confirm whether Martinez-Gomariz et al. 2017
   and Allen et al. 2003 (SAE 2003-01-0966) exist anywhere in the corpus as full
   text. CLAUDE.md A-3 flags these two as the NEW ones (Smith/Modra/Felder and
   Arrighi 2015 already appear in the register in adjacent contexts, so they are
   not independent support). Dispatch 5's contribution framing rests on them.

ALSO FLAG WHEN YOU MEET IT
- 01_.../2026-08-07_critical-finding_coupling-defect-force-accessor-route-forward_STALE.md
  is correctly tagged STALE (its -14.794 m/s2 and -9541 N are retracted) and is
  still being cited elsewhere. List every place in the corpus pointing at it.
- 00_BRIEFING.md says .claude/hooks/ has 14 files and that stop_signal_and_check.sh
  is absent. A live LS6 session fires stop_signal.sh, a different name. Reconcile
  the hook inventory.
- The corpus's Sprint 2 inventory marks 9 folders "cached only, path unverified
  live", including can-it-ford-main (848 files, most recently touched). Re-verify
  those paths live before any verdict that depends on them.

CONCRETE FIRST STEP
Answer questions 3 and 4 FIRST, before any bulk verdict work. They are two
targeted searches, they unblock two other dispatches, and they take minutes
rather than sessions. Then start batch verdicts at
_BUILD_LOG/step6_extract_batch1.txt.

DEFINITION OF DONE
This is explicitly a MULTI-SESSION item; do not fake completion. Done for THIS
session means: questions 1 to 4 answered with the search method stated, at least
1,000 snippets given verdicts appended to 00_RESEARCH_MANIFEST.tsv in the
existing 9-column schema, and PROGRESS_LOG.md updated with an exact resume point
(file and line). Report counts honestly, including how many remain.
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
