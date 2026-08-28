> **ABSORBED 2026-08-25 into `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, the single
> corpus master.** This file is kept verbatim below and nothing in it was deleted or
> rewritten. Cite it only with its date, never as current: several of its counts (the
> 332-record index, the 27-metadata / 8-papers split, the open-item list) were measured
> before the 2026-08-25 ingest fix and are stale. The master carries the live figures and
> the current status of every open item.

---

# corpus-bib merge: there is no conflict, it landed on 2026-08-20

Date 2026-08-25. Commissioned as "resolve the 3-file merge conflict between
`claude/add-ci-checks` and `claude/r9-corpus-bib`", with the resolution to be written
to `docs/CORPUS_BIB_MERGE_RESOLUTION_2026-08-24.md` before any commit. That file name
is used here with today's date instead, because 2026-08-24 is not the date of anything
measured: nothing was resolved that day, and the merge itself predates it.

**The premise is false. The merge already happened.** Nothing was resolved by this
session, because there was nothing left to resolve.

## What was measured, live, 2026-08-25

The commissioned first command was run exactly as given:

```
git merge-tree --write-tree --name-only origin/claude/add-ci-checks origin/claude/r9-corpus-bib
```

It prints a single tree oid, `5d613e00e7d1dedbc7bcb32704dee6de20df48bc`, and exits **0**
with no `Conflicted files` section. `merge-tree` reports conflicts by exiting non-zero
and naming the paths, so a bare tree oid at exit 0 is the clean-merge result. **Zero
files conflict.**

The reason is direct:

```
git merge-base --is-ancestor de18180 origin/claude/add-ci-checks   ->  true
```

`de18180`, the tip of `claude/r9-corpus-bib` named in the dispatch and confirmed live as
its tip, **is an ancestor of `origin/claude/add-ci-checks`**. It was brought in by merge
commit `a83a38b` (parents `72cfbdb` and `de18180`), "Record poster and paper submission
status per direct human confirmation". The branch is already merged, so re-merging it is
a no-op.

## The three named files differ, and that is not a conflict

All three do differ between the two branch tips:

| file | add-ci-checks blob | r9-corpus-bib blob |
| --- | --- | --- |
| `.claude/skills/research-corpus/SKILL.md` | `9660392` | `fc3948d` |
| `analysis/research_index.py` | `3ba8c58` | `9b1ac5d` |
| `data/deep_searches/vehicle-mesh-assets.json` | `68a0d35` | `b089f66` |

A differing blob on a branch that already CONTAINS the other branch is the expected
shape of "merged, then moved on". It is not evidence of an unresolved conflict, and
reading it as one is what kept this item open. The direction is checkable: on
`analysis/research_index.py`, the add-ci-checks side carries 11 `source-audit`
references against the corpus-bib side's 6, so the merged file is a superset rather
than one side overwriting the other.

## The sticking point was resolved, and the resolution is in the source

The dispatch names the sticking point precisely: "a `--source-audit` flag declared on
both sides with different predicates, where neither side's declaration is a superset of
the other's". That is correct, it was real, and it was already decided. The decision is
recorded in `analysis/research_index.py` in `build()`, at the returned index dict:

```
# The deep-search block is read by --source-audit and --searches, and
# the per_search block by --coverage and --ingest-audit. NEITHER SIDE
# WAS A SUPERSET, so both are kept rather than one chosen.
"deep_searches": searches,
```

**Neither side won. Both blocks are kept**, `deep_searches` for `--source-audit` and
`--searches`, `papers_per_search` / `source_searches` for `--coverage` and
`--ingest-audit`. The same commit range also kept the corpus-bib branch's fix for the
hardcoded `built` date, annotated in place as "a hardcoded date here is the same class
of defect as a hardcoded search list".

## What this does not say

This does not say the merged code was correct. It was not: a separate, real defect in
`discover_search_exports` meant `--build` could not run at all from 2026-08-23 onward.
That is a different finding, fixed and written up in
`docs/CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md`. A clean merge and a working build are
independent claims, and only the first was ever in question here.

## Standing note

An unresolved-conflict claim ages badly, because the branches keep moving underneath it.
This one was true when it was written and was already false by the time it was
re-dispatched. Re-run the `merge-tree` command before acting on any conflict claim in
this repo; it costs one command and it is the whole answer.
