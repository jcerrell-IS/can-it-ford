# Corpus document inventory, mapped before touching anything

Written 2026-08-26 02:05 BST (dated 2026-08-25 to match the prompt's filename spec).
Branch `claude/add-ci-checks`, HEAD `436a5f0`, main tree `/Users/josie/can-it-ford`.

**Provenance key.** `[READ]` I ran the command or read the bytes this session.
`[INFERRED]` computed from something tagged `[READ]`. `[RECALLED]` carried from another
document and NOT re-derived.

**Why this file exists.** The last two sessions' "what I changed" reports undercounted their
own working-tree footprint by 6 to 8 files. This maps the corpus document set completely,
once, before any write.

---

## 1. Inventory, all 14 targets, measured live

All 14 exist. None is missing. `[READ]`

| file | bytes | mtime | git state |
| --- | --- | --- | --- |
| `docs/R9_CORPUS_READ_2026-08-19.md` | 12871 | 08-25 04:31:01 | M, tracked |
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` | 23089 | 08-23 01:03:17 | clean, tracked |
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` | 20894 | 08-23 01:03:17 | clean, tracked |
| `docs/CORPUS_MERGE_FINAL_2026-08-22.md` | 66563 | 08-25 04:31:00 | M, tracked |
| `docs/CORPUS_LINEAGE_STATUS_2026-08-23.md` | 20615 | 08-25 20:50:02 | **UNTRACKED** |
| `docs/CORPUS_FINAL_MERGE_REPORT_2026-08-23.md` | 20447 | 08-25 04:31:01 | M, tracked |
| `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` | 41833 | 08-25 20:51:47 | M, tracked |
| `docs/CORPUS_FOLLOWUP_REPORT_2026-08-25.md` | 9325 | 08-25 20:57:36 | **UNTRACKED** |
| `docs/CORPUS_FINAL_MERGE_REPORT_2026-08-25.md` | 11809 | 08-25 04:31:01 | M, tracked |
| `docs/CORPUS_BIB_MERGE_RESOLUTION_2026-08-25.md` | 4651 | 08-25 04:31:01 | M, tracked |
| `docs/CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md` | 9889 | 08-25 04:31:01 | M, tracked |
| `scripts/r8/prompts/d14-corpusbib.md` | 13803 | 08-19 17:51:31 | **UNTRACKED** |
| `scripts/r8/prompts/d20-reader.md` | 14265 | 08-19 18:24:47 | **UNTRACKED** |
| `data/research_corpus_index.json` | 720501 | 08-25 19:03:50 | M, tracked |

The two blank-status files were confirmed tracked with `git ls-files --error-unmatch`; both
returned their path, so blank means clean and not untracked. `[READ]`
The four marked UNTRACKED each returned `did not match any file(s) known to git`. `[READ]`

**Contention check.** `find -mmin -15` over the repo returns only `.remember/` and
`.claude/memory/` hook files. **No corpus document has been touched in the last 15 minutes**,
and the most recent corpus write is 20:57, roughly five hours before this session. `[READ]`
No file in scope is under a live mid-edit.

---

## 2. The two dispatch prompts, read in full

**Neither describes building the final reader. The premise that one of them might is false.**

**`d20-reader.md`.** Slot `d20-reader`, branch `claude/r9-reader`. "Reader" means the session
that READS the other nine R9 sessions, not the research reader corpus document. Its job is to
parse nine live session transcripts, every commit on nine branches, and every script they
created, and produce `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md` in five sections, of which
section 3 (contradictions and corrections) is named the one that matters. `[READ]`

**It was executed.** `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md` (47683 bytes) and
`analysis/r9_session_reader.py` (17195 bytes) both exist, both dated Aug 20 02:05. `[READ]`
So this is a closed unit, not an unexecuted plan, and PART B does not defer to it.

**`d14-corpusbib.md`.** Slot `d14-corpusbib`, branch `claude/r9-corpus-bib`. Its unit is the
open item "the corpus is NOT a superset of the bibliography": 11 of the 14 works the paper
cites were absent from the 332, and it must determine per work whether each was never ingested
or ingested and lost in a merge, then make the index able to report this about itself. It
explicitly forbids editing the paper or the bib (d5-priorart owns those). `[READ]`

**Conclusion for PART B: neither prompt supersedes it.** PART B's plan stands as written.

---

## 3. The four files no prior report has mentioned

**`CORPUS_BIB_MERGE_RESOLUTION_2026-08-25.md` is a refutation of its own commissioning
premise.** It was commissioned to resolve a 3-file merge conflict between
`claude/add-ci-checks` and `claude/r9-corpus-bib`. There is no conflict:
`git merge-tree --write-tree` exits 0 with a bare tree oid, because `de18180` is already an
ancestor of `origin/claude/add-ci-checks`, merged by `a83a38b`. The three files differ, which
is the expected shape of "merged, then moved on", not an unresolved conflict. `[READ]`

**`CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md` is a fixed crash plus a still-open remainder.**
`--build` had been dying since 2026-08-23 on `MANIFEST.json`, which `discover_search_exports`
globbed and handed to a gate designed to reject non-exports. Fixed by skipping the manifest and
keying on the `schema` key. A held-fixed control (empty export dir) landed on exactly 319, the
distinct-works count CLAUDE.md already records, proving the 332 was stale and duplicated rather
than the fix being a regression. Ladder: **332 stale and duplicated, 319 deduped, 382 deduped
plus three ingested searches.** `[READ]`

**The three reports are three different documents, not copies and not a chain of edits.**
Measured by shared unique non-blank lines: `CORPUS_FINAL_MERGE_REPORT_2026-08-23` (278
non-blank) against `_2026-08-25` (167) share **9 lines**, of which 6 are the ABSORBED banner
and the rest are `**DONE.**`, `---`, and the environment line. `_2026-08-25` against
`CORPUS_FOLLOWUP_REPORT_2026-08-25` (135) share **3**. Their heading structures are disjoint.
`[READ]` They are three separate sessions' reports on the same theme.

**Authoritative: none of the three. `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` is.** All
three are absorbed into it, and it is the only one whose numbers re-derive live (section 5).
The 08-23 and 08-25 merge reports carry the ABSORBED banner; the FOLLOWUP does not, which is
the one real gap in an otherwise complete pass.

---

## 4. Why `R9_CORPUS_READ_2026-08-19.md` is dirty, and why the others are

**The diff is a tagged, dated addition, and it deletes nothing.** `+9 / -0`, a six-line
ABSORBED banner dated 2026-08-25 naming `MERGED_RESEARCH_READER_CORPUS_FINAL.md` and stating
the file is kept verbatim. `[READ]`

It is **not** a content correction in the `ac0f0d8` tradition. `ac0f0d8` withdrew two named
claims from this same file with 13 deletions and said what replaced them. `[READ]` This is a
supersession banner, not a withdrawal. It satisfies the prompt's test (tagged and dated, not an
untagged edit), so it is not flagged, but the distinction is worth keeping.

**It is one of six identical batch edits.** All six dirty corpus documents carry `+7 / -0` of
banner and nothing else, and the banner is byte-identical across all of them (sha1 of the first
8 lines matches on all four checked). Their mtimes cluster at 04:31:00 to 04:31:01. `[READ]`
This is a single coherent absorption pass, entirely additive, with **zero deletions anywhere**.

| file | diff |
| --- | --- |
| `R9_CORPUS_READ_2026-08-19.md` | +7 / -0 |
| `CORPUS_MERGE_FINAL_2026-08-22.md` | +7 / -0 |
| `CORPUS_FINAL_MERGE_REPORT_2026-08-23.md` | +7 / -0 |
| `CORPUS_FINAL_MERGE_REPORT_2026-08-25.md` | +7 / -0 |
| `CORPUS_BIB_MERGE_RESOLUTION_2026-08-25.md` | +7 / -0 |
| `CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md` | +7 / -0 |
| `MERGED_RESEARCH_READER_CORPUS_FINAL.md` | 931 changed, the actual consolidation |

---

## 5. Why `data/research_corpus_index.json` is dirty

**It is NOT the Undermind-DOI additions from the last session.** `[READ]` Diffstat is
`+1154 / -3`, but the headline fields are identical between `HEAD` and the working tree: built
2026-08-25, `n_papers` 382, 28 `deep_searches`, 3 `papers_per_search`, 3 `source_searches`.

A structural comparison shows what actually changed:

- **Two new top-level keys**, `n_with_fulltext` (19) and `fulltext_dirs`.
- **Three new fields on all 382 records**: `has_fulltext`, `fulltext_path`, `fulltext_chars`.
- **`n_cited_reader_facing` 129 to 131**, from exactly two records flipping
  `cited_reader_facing` to true: `10.1007/s00466-019-01783-3` and `10.1504/pcfd.2019.10018820`.
  The first is a DOI CLAUDE.md's ranking block argues about by name.

The code side is `analysis/research_index.py`, also dirty at `+154 / -3`, adding `FULLTEXT_DIRS`,
`load_fulltext_map()` and a `--fulltext` report. `[READ]` Source dirs are
`~/can-it-ford-refs/_fulltext` (70 files) and `_fulltext_desktop` (37), both confirmed present
and **both outside the repo**. `[READ]`

**The index stores a path and a character count, never the text.** Verified per record. `[READ]`
The papers are copyrighted and the repo is public, so this is the correct design and the
extracted text must stay out of the tree.

**This retires a standing memory.** "The corpus holds no full text" is now false: 19 of 382
have extracted full text linked, 14 have both full text and an abstract, 2221860 characters
total. `[READ]`

---

## 6. Live re-derivation of the master's own numbers

`MERGED_RESEARCH_READER_CORPUS_FINAL.md` section 9 lists the commands that re-derive it. I ran
them. **All three reproduce exactly.** `[READ]`

```
--stats         index built 2026-08-25   papers 382   abstracts 211   cited 164
--fulltext      19 of 382 linked, 14 with both, 2221860 characters
--source-audit  EXIT=1, FAIL (17 problems)
```

**The build blocker is an ACTIVE, UNRESOLVED problem.** `--source-audit` still exits 1: 17
searches remain metadata-only, representing 1244 papers as an integer and nothing more. Down
from 19 and 1317, but open. The route is proven (two Undermind calls per search) with two named
traps: address a search by its `name` and not its `slug`, and paginate, because four of the
remaining searches exceed the 50-item page (119, 118, 114 and 105). `[READ]`
**Nothing about the reader may be described as complete while this stands.**

---

## 7. The apparent CLAUDE.md contradiction, resolved

CLAUDE.md's section headed "RESEARCH-CORPUS READER RANKING" states that
`CORPUS_MERGE_FINAL_2026-08-22.md` "is a SEPARATE line and is NOT superseded" and that "FINAL
does not restate it". That file has now been banner-stamped as absorbed, which looks like a
direct conflict. **It is not an error, and it is already documented.** `[READ]`

`MERGED_RESEARCH_READER_CORPUS_FINAL.md` section 4 is headed "The 138-DOI accounting, absorbed
and preserved as authority" and carries the material forward, including the number that matters,
0 of 138 cited in the submitted paper. Its section 6.8 states the CLAUDE.md sentence "is now
false", supplies exact replacement text in section 8, and records that CLAUDE.md **was not
edited** because it was dirty under another session. `[READ]`

So the ranking block is stale, knowingly, with the fix already drafted and deliberately not
applied. That is the correct call under the standing two-sessions-one-file rule.

**One genuine internal contradiction inside the master.** Section 8 says "Nothing in `data/` or
`analysis/` was modified, so `research_index.py` still has no `fulltext_path` field." Section
6.14 says the opposite, and my live measurement (section 5 above) confirms 6.14: the field
exists and 19 records are populated. `[READ]` **Section 8's sentence is stale**, written before
a later pass in the same session wired the full text. It should be corrected in place.

---

## 8. Verdict: is it safe to proceed to PART B

**Partly. Steps 6, 7 and 8 are safe. Step 9 is blocked and step 10 needs Josie.**

Nothing is under live edit, every banner edit is additive with zero deletions, the master's
numbers re-derive exactly, and the four untracked files are genuinely untracked. On the
evidence the prior consolidation session finished cleanly and handed off deliberately rather
than being interrupted, so its work is landable rather than in flight.

**Step 9 is blocked, and this is the third session in a row blocked at exactly this point.**
`CLAUDE.md` is still dirty (`+41 / -17`, mtime 2026-08-25 04:18, roughly 21 hours old, so stale
uncommitted work rather than a live edit). Its dirty diff does **not** touch the ranking block
(0 hits), so the two edits do not textually collide, but the standing rule and the prompt's own
gate both fire on "CLAUDE.md still dirty". The register half is clean and available:
`CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` is untouched since 08-23, and returns **0 hits**
for `MERGED_RESEARCH_READER_CORPUS_FINAL` against 2 for `CORPUS_MERGE_FINAL`, confirming 6.7
exactly. `[READ]` Step 9 requires both in one commit, so the clean half cannot proceed alone.

**Two things need a human decision before any commit.** First, landing this means committing
roughly 931 lines of another session's consolidation under a different author's commit message,
and `.git/hooks/pre-commit` refuses more than 8 staged files, so the 13 candidate paths force a
deliberate split rather than one commit. Second, the repo is public, so the push in step 10
needs Josie's explicit go-ahead and cannot be inferred from the prompt.

---

## 9. What a human needs to decide

1. **CLAUDE.md.** Commit or discard the unrelated `+41 / -17` sitting there for 21 hours, which
   unblocks the ranking-block fix that three sessions have now deferred. Replacement text is
   already drafted in the master's section 8.
2. **Landing another session's work.** Approve committing the consolidation and the six banners,
   split across commits to satisfy the 8-file hook.
3. **The push.** Public repo, explicit confirmation required.

---

## 10. PART B outcome, appended 2026-08-26

Josie authorised steps 6 to 8 without a commit, and authorised the CLAUDE.md ranking fix
despite the dirty-file gate. Both were done. **Nothing was committed and nothing was pushed.**

| step | action | state |
| --- | --- | --- |
| 6 | staged 3 untracked corpus documents | DONE, not committed |
| 7 | corrected the master's self-contradiction in section 8 | DONE |
| 8 | reciprocal scope pointers between the two merge reports | DONE |
| 8 | successor pointer plus status paragraph on the FOLLOWUP | DONE |
| 9 | CLAUDE.md ranking block replaced | DONE, on explicit go-ahead |
| 9 | corrections-register row | **NOT DONE**, still open |
| 10 | commit and push | **NOT DONE**, by instruction |

**The CLAUDE.md edit was made safe rather than assumed safe.** Its unrelated `+41 / -17` was
confirmed to have 0 overlapping hits with the ranking block, and its mtime was 21 hours stale
rather than a live edit `[READ]`. The three report counts in the replacement were re-derived
live with `--doi` before being written into the constitution, rather than carried from the
draft: 7, 7 and 4, which match the draft exactly `[READ]`.

**One scope call worth surfacing.** `scripts/r8/prompts/d14-corpusbib.md` and `d20-reader.md`
are untracked and were in this inventory, but they are 2 of **33** untracked files in
`scripts/r8/prompts/` `[READ]`. Tracking 2 of 33 would create exactly the kind of misleading
partial state this exercise exists to remove, so **they were deliberately left unstaged** and
the whole prompt set is flagged as a separate decision.

**Still open after this session.**

1. **`--source-audit` exits 1, 17 searches, 1244 papers as integers.** The reader is not
   complete. Largest open item by volume.
2. **The corrections register does not name the master.** 0 hits against 2 for
   `CORPUS_MERGE_FINAL`. The register is clean and was not touched.
3. **Nothing is committed.** Three files sit staged in a shared index while other sessions are
   live. A plain `git commit` from another session sweeps them. Commit or unstage soon.
4. **The 33 untracked dispatch prompts.**
5. **No claim in this file or the master has been adversarially reviewed.**
