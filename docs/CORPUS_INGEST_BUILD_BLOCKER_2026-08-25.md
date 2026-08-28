> **ABSORBED 2026-08-25 into `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, the single
> corpus master.** This file is kept verbatim below and nothing in it was deleted or
> rewritten. Cite it only with its date, never as current: several of its counts (the
> 332-record index, the 27-metadata / 8-papers split, the open-item list) were measured
> before the 2026-08-25 ingest fix and are stale. The master carries the live figures and
> the current status of every open item.

---

# The corpus ingest was not missing, it was aborting: `--build` died on MANIFEST.json

Date 2026-08-25. Commissioned as "the corpus ingest is structurally broken: every JSON
under `data/deep_searches/` has `n_relevant_papers` as an integer with no `papers`
array, so `--doi` and `--query` return nothing for the ~270 paper-slots that only exist
as a count. `--stats` still reports `papers=332` because it's summing the integer
field. Find the ingest phase that should populate the papers array."

The symptom was real. **Every part of the stated mechanism was wrong**, and the ingest
phase was not missing. It existed, it was correct, and it was crashing.

## Four claims in the dispatch, each measured

**1. "Every JSON has no papers array" is false.** Live count of
`data/deep_searches/`: 29 files, one of which is `MANIFEST.json`, leaving 28 searches.
**Two already carried a full `papers` array** before this session:
`buoyancy-overestimation.json` (32 papers) and `vehicle-mesh-assets.json` (36). Both
declare `"schema": "canford.deep_search/1"` and carry `cite_key`, `rank`, `title`,
`year`, `doi` and `link` per paper. Both were exported on 2026-08-19 by slot
`d14-corpusbib`. So the export format, the export path and two real exports all
already existed.

**2. "~270 paper-slots" is false, and low by nearly 5x.** `--source-audit` read live
before any change: **19 paperless searches representing 1317 papers as an integer
only.** Not 270.

**3. "`--stats` reports 332 because it's summing the integer field" is false.** The
count is `"n_papers": len(merged)` in `build()`, the length of the merged paper-record
dict. The only place `n_relevant_papers` is summed is the `--source-audit` reporting
line, which sums it over the PAPERLESS searches specifically to say how much is
missing. The 332 was a real record count from a real build; it was simply a **stale**
one, dated 2026-08-20.

**4. "Find the ingest phase that should populate the papers array" presumes it is
absent. It is present.** `build()` has carried the MCP-sourced ingest path for some
time, annotated in place:

```
# THE MCP-SOURCED INGEST PATH. The builder cannot call Undermind: it is
# pure stdlib and runs outside any MCP session. A session that HAS the
# connector writes `data/deep_searches/<slug>.json` ... and this reads them.
for p in discover_search_exports(export_dir or SEARCH_EXPORT_DIR):
    recs = parse_search_export(p)          # raises on a gate failure
```

## The actual defect

`discover_search_exports` globbed **every** `.json` in the directory. `parse_search_export`
raises on a gate failure by design, which is the correct behaviour for a malformed
export. Together they meant the builder handed non-exports to a gate built to reject
them. Running `--build` live on 2026-08-25, before any change:

```
ValueError: data/deep_searches/MANIFEST.json: schema is None, expected
'canford.deep_search/1'; missing required field `workspace_id`; ... `papers`
```

`MANIFEST.json` is a manifest, not an export. It was written on 2026-08-23. **Every
`--build` from 2026-08-23 onward died on it**, before merging anything at all. The
sibling function `load_deep_searches` had always skipped the manifest explicitly; only
this glob did not, so two functions in the same file disagreed about what a `.json` in
this directory means.

Skipping the manifest exposed a second, same-shaped blocker: **two file shapes live in
this directory and only one is an export.**

- a real export declares `"schema": "canford.deep_search/1"` and carries `papers`
- a **metadata stub**, written by the 2026-08-20 metadata fix, carries `name`,
  `n_relevant_papers`, `status`, `reached_index_before_2026_08_20`, and **no `schema`
  key at all**

Measured live: 2 exports against 26 stubs. The stubs hit the same gate and aborted the
build on `dynamic-vehicle-traction.json`.

**The fix**, in `discover_search_exports` only: skip `MANIFEST.json`, and treat a file
as an export if and only if it carries a `schema` key. The discriminator is deliberately
the schema KEY and not the presence of a papers array, so the gate keeps its teeth: a
file that claims to be an export and is malformed still raises, while a stub that never
claimed to be one is left to `load_deep_searches` to read as metadata. A file that
cannot be read or parsed at all is handed to the gate rather than skipped, so a corrupt
export is reported and not swallowed.

This is why `--source-audit` reported `vehicle-mesh-assets` PAPERLESS while that exact
file held a 36-paper array on disk: the audit reads `idx.get("deep_searches")` from the
index in preference to the live directory, and the index could not be rebuilt.

## The rebuild, measured against a held-fixed control

`--build` warns that the published rungs are in CLAUDE.md and to "use `--out` to measure
the change first". That was done. Three builds, the middle one a control with
`--export-dir` pointed at an empty directory, which isolates the code delta from the
new exports:

| metric | index on disk (2026-08-20) | control, no exports | after fix, 3 exports |
| --- | --- | --- | --- |
| papers | 332 | **319** | 382 |
| with abstract | 222 | 211 | 211 |
| cited in repo | 116 | 116 | 164 |
| reader-facing | 107 | 107 | 129 |
| no DOI, undiffable | 60 | 47 | 67 |
| `source_searches` | absent | `{}` | 3 searches |

**The control lands on exactly 319**, which is the distinct-works count CLAUDE.md
already records for this corpus: "332 records are 319 DISTINCT WORKS. Eleven Semantic
Scholar ids appear under twenty-four record keys with byte-identical titles." The
-13 papers and -11 abstracts in the control column are that documented duplication
collapsing, not a regression, and the -11 abstracts matches the eleven duplicated ids
one for one. The 332 on disk was the pre-dedup number, frozen because the build could
not run.

So the ladder should now be read as: **332 was stale and duplicated, 319 is the deduped
corpus, 382 is the deduped corpus plus three ingested searches.**

## What was ingested, and what it recovers

A third search was exported this session to prove the path end to end, chosen because it
bears directly on the open coupling question:
`grid-converged-force-deficit`, 37 papers, "Grid-converged force deficit in partially
submerged free-rigid MPM coupling", read live from Undermind workspace
`17299f2a-8dc8-438b-8c84-5abf19395e2c` via `inspect_deep_searches` plus `get_paper_info`,
the same two-call route the 2026-08-19 exports used.

That one search contains **all three** of the DOIs CLAUDE.md's reader-ranking section
argues about:

- `10.1016/j.cma.2022.114809` (Li, Lian and Zhang 2022, IFEMP)
- `10.1016/j.jcp.2016.10.064` (Zhang et al 2017, incompressible MPM for free surface flow)
- `10.1007/s00466-019-01783-3` (González Acosta et al 2019)

`--doi 10.1016/j.cma.2022.114809` returned nothing before this fix. It now returns the
record, and reports the IFEMP paper appearing in **seven** reports. CLAUDE.md records 4
from the 2026-08-14 catalogue TSV and 5 from the built index, and states the rule that
matters here: **the count is instrument-dependent, the ranking is not.** Seven is a
third instrument reading, not a correction of the other two, and it is a further reason
to quote the ranking rather than any bare count. It remains the case that N report
appearances are N deep searches by one retrieval system, so this is a relevance signal
and not seven independent sources.

## What is still open

`--source-audit` still exits 1, correctly, with **17 problems**: 17 searches remain
metadata-only, representing **1244 papers as an integer only**. That is down from 19 and
1317. Searches reaching the corpus as papers went from 8 of 27 to **11 of 28**.

The remaining 17 are recoverable, and the route is now proven rather than assumed. The
Undermind workspace is live, holds every one of them, and the export is two calls per
search:

```
inspect_deep_searches(workspace_id=..., names=[<the search NAME, not the slug>],
                      papers_only=True, detail_level='standard', limit=50)
get_paper_info(workspace_id=..., cite_keys=[...], detail_level='compact', show_doi=True)
```

Two traps for whoever finishes this. **Address the search by its `name`, not its
`slug`**: `inspect_deep_searches(names=["grid-converged-force-deficit"])` returns
"Search not found", and the name is in each stub's `name` field. And **paginate**:
`inspect_deep_searches` pages at 50, and four of the remaining searches exceed that
(`free-body-load-transfer-expanded` 119, `free-body-load-transfer` 118,
`load-transfer-portability` 114, `moving-vehicle-open-source` 105); a partially-paged
export is unusable and the gate is written to say so.

The precedent exports carry no abstracts, so this route recovers title, year, DOI and
link, which is what `--doi` and `--query` join on. It does not recover abstracts, and
those records should not be described as read.

## Standing note

`--build` is the only thing that moves a new JSON into the index; a new export is inert
until it runs. It is now also true that `--build` can fail closed on a file that is not
an export, which is the safer direction, but it failed **silently enough** that the
index sat two days stale while three separate documents described its contents as
current. Run `--build` and read its exit, do not infer the index is current from the
presence of the files that should have gone into it.
