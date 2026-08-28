## YOUR SLOT: d14-corpusbib, branch `claude/r9-corpus-bib`, worktree `.claude/worktrees/r9-corpus-bib`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d14-corpusbib` first.

### The finding you are extending, and the correction that came with it

`CLAUDE.md` carries a section headed "THE RESEARCH CORPUS IS NOW QUERYABLE FROM INSIDE THE REPO". Read it live at `/Users/josie/can-it-ford/CLAUDE.md`, by that absolute path, because your worktree copy is frozen at your branch point. It records this ladder:

```
332  papers in the corpus
 76  DOI-shaped string anywhere in the tracked tree   (cited_in_repo)
 43  DOI-shaped string in a reader-facing directory   (cited_reader_facing)
  4  hold an entry in the SHIPPED bibliography
  3  are \cite'd, and therefore print in the reference list
```

A previously published figure, "256 are cited nowhere", was WITHDRAWN because it took the complement of *reach* and reported it as *cited*. Do not reintroduce that conflation. The field names `cited_in_repo` and `cited_reader_facing` are what mislead; the data is internally consistent.

### The open item, stated in CLAUDE.md as unresolved and assigned to nobody

**The corpus is NOT a superset of the bibliography.** Of the 14 works the paper cites, 11 are absent from the 332 entirely, including `shah2018` (`10.1051/matecconf/201820307003`), which is flood-vehicle literature the paper already cites. So corpus coverage cannot answer what the paper cites, and the index cannot report this about itself. Whether that is a sourcing gap or a dropped merge is unresolved.

That is your unit: **resolve it.**

### How to resolve it without producing another scope-sensitive number

1. Determine, for each of the 11 absent works, whether it was never ingested or was ingested and lost in a merge. Those are different defects with different fixes, and the answer may differ per paper. `analysis/research_index.py` builds the index from eight Undermind reports; the reports are the evidence.
2. Make the index able to report this about itself. A checker whose corpus excludes the bibliography it is meant to audit is the same defect class slot d6-tooling named last night as "a checker whose corpus includes its own output". Read `docs/R8_TOOLING_PROVENANCE.md` on `claude/r8-tooling` before designing the fix, so you build the opposite error rather than the same one.
3. EVERY count you publish must state its scope. `.claude/worktrees/` MUST be excluded: a first version of this index included it and reported 269 of 332 as cited, because another session's `r5_citation_xref.tsv` carries 489 DOIs. State the scope in the same sentence as the number, every time.

### Also true and worth checking rather than assuming

Slot d5-priorart established last night that the four prior-art works are on `claude/add-ci-checks` with 42 bib entries and 6 keys, NOT on origin/main or round-5, which carry 21 entries and 0. The bib you are comparing against depends on which ref you read, so name the ref every time you quote a bibliography count. The SHIPPED bibliography is on `overleaf/main` and has 15 entries, 14 cited, one entry (`xiong2024`) never cited so BibTeX drops it.

Do not push to Overleaf. Do not edit the paper or the bib in this unit; d5-priorart owns those paths. You own the index and your own document.

No GPU. `uv` for numpy if you need it.
