# Corpus global audit, 2026-08-26

Single output file for the whole pass. One section appended per phase, nothing
overwritten. Every claim tagged [READ] (direct file or command output this
session), [RECALLED] (from context, not re-verified), or [INFERRED].

Started 2026-08-26 11:25 BST on branch `claude/add-ci-checks`, HEAD `436a5f0`.

---

## Phase 0, contention check

**CLAUDE.md is DIRTY. The register is CLEAN.** [READ]

```
$ git -C /Users/josie/can-it-ford status --short CLAUDE.md
 M CLAUDE.md
$ git -C /Users/josie/can-it-ford status --short docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
(no output, clean)
```

Consequence, applied for the whole pass: **neither CLAUDE.md nor the register is
edited by this session**, regardless of what Phases 1 to 5 find. Phase 5's
CLAUDE.md task is blocked before it starts. This is the third consecutive
session to hit this block.

### The blocking edit is not a stranger, it is the edit Phase 5 wanted to make

`git diff --stat CLAUDE.md` reports **68 insertions, 35 deletions, 1 file**. [READ]
mtime is **Aug 26 08:53:20 2026**, roughly 2.5 hours before this pass began,
so it is not an active mid-write. [READ]

Reading the uncommitted diff, the working-tree CLAUDE.md **already contains the
research-corpus reader ranking block naming FINAL.md the single master**: [READ]

```
$ /usr/bin/grep -n "THERE IS NOW ONE LINE, NOT TWO" CLAUDE.md
671:**RESEARCH-CORPUS READER RANKING, reset 2026-08-25. THERE IS NOW ONE LINE, NOT TWO.**
$ git show HEAD:CLAUDE.md | /usr/bin/grep -n "THERE IS NOW ONE LINE, NOT TWO"
(no match)
```

It also carries the dated withdrawal of the prior form of that block, at line
681, `withdrawn 2026-08-26`. [READ]

So the substantive Phase 5 content **exists on disk and is uncommitted**. The
open question is not "write it" but "whose working-tree change is this and may
it be committed", which is a decision for Josie, not for this pass. Recorded
here and carried to Phase 5.

Other Phase 0 observations:

- No git lock files present (`.git/index.lock` absent). [READ]
- The session-start hook reported 1 other session active in this repo within
  3 minutes. A `ps` sweep for `claude` returned Claude **Desktop** and its MCP
  helper processes only, no second Claude Code CLI in this working tree that I
  can identify from process args alone. Treating a concurrent session as
  POSSIBLE and honouring the no-touch rule regardless. [READ] for ps, [INFERRED]
  for the conclusion.
- `find -maxdepth 1 -newer /tmp -name "*.md"` returned all 19 top-level markdown
  files, which means the predicate is useless here: `/tmp` on this Mac is older
  than every file it was meant to filter. Substituted a real mtime listing.
  Only three top-level .md files were touched in the last 24 h: `CLAUDE.md`
  (Aug 26 08:53), `RESUME_EXTRACTION_2026-08-25.md` (Aug 25 23:19) and
  `README.md` (Aug 25 23:17). [READ]

Proceeding to Phase 1.

---

## Phase 1, global discovery

**Headline: no, the known 14 plus 37 is not the whole thing.** Four separate
things turned up that no corpus report has named, and one of them is a session
from ten hours ago that already worked the FINAL master. Detail below.

### 1.1 Branches

`git branch` reports **95 local**, `git branch -a` reports **194 including
remotes**. [READ] Filtering on corpus / research / literature / paper / read /
bib / cite gives 12 local names: [READ]

```
claude/bibliography-formatting-fix-4c3864     claude/r9-corpus-bib
claude/figure-verification-citations-f36b1c   claude/r9-reader
claude/overleaf-gci-citations-2026-08-08      claude/semi-empirical-citations-fcc6f3
claude/r5-research                            paper/close-for-submission
paper/final-graft                             paper/mark-superseded
paper/submission-close                        push-ready-2026-08-04
```

Containment measured with `rev-list --left-right --count HEAD...<branch>`: [READ]

| branch | commits it has that HEAD lacks | verdict |
|---|---|---|
| `claude/r9-reader` | **0** | fully absorbed into HEAD, nothing stranded |
| `claude/r9-corpus-bib` | **0** | fully absorbed into HEAD, nothing stranded |
| `claude/r5-research` | **82** | **NOT absorbed, 44 unique `docs/` files** |
| `fix/ccsa-acknowledgement` | **7** | **NOT absorbed, 16 unique files, newest branch in repo** |

The two branches whose names say "reader" and "corpus-bib" are the two that are
already merged. **The two carrying stranded corpus work are named neither.**
That is the Phase 1 finding in one line: name-based branch triage would have
missed both.

### 1.2 `claude/r5-research`, 82 commits and 44 stranded docs

52 unique paths against HEAD, 44 of them under `docs/`, every one prefixed
`R5_RESEARCH_`. [READ] A sample of what is stranded, by filename alone:

```
R5_RESEARCH_MPM_METHOD_CITATION_GAP_2026-08-18.md
R5_RESEARCH_MPM_FOUNDATIONS_UNCITED_2026-08-18.md
R5_RESEARCH_BIB_DOI_SUPPLEMENT_2026-08-17.md
R5_RESEARCH_AUTHOR_SWEEP_2026-08-16.md
R5_RESEARCH_ELICIT_AND_CATALOG_MINE_2026-08-16.md
R5_RESEARCH_KRAMER_CONFIRMED_MODE_DEPENDENT_2026-08-17.md
R5_RESEARCH_NIHEI_ROUTES_AND_AUTHOR_TRAP_2026-08-16.md
```

Their commit subjects are a numbered unit series running to at least unit 72,
and several are self-retractions in the project's own house style
(`unit 65: RETRACT unit 64 in full`, `unit 72: RETRACT unit 71`). [READ]
This is a whole parallel literature audit that the corpus reader chain does not
cite and, from the current branch, cannot see.

**This is a human decision, not a fold-in.** 44 documents is larger than the
entire corpus reader family. Naming it here; not merging it.

### 1.3 `fix/ccsa-acknowledgement`, and the session that beat this one to it

**This is the most recently committed branch in the repository**, tip
`51effcd`, **2026-08-26 01:41:22 +0100**, which is 35 minutes NEWER than the
current branch's HEAD (`436a5f0`, 01:06:07). [READ]

Its tip commit is titled *"The corpus master forces a correction to my own
headline, and the hero shot is mislabelled"*. Read in full, that commit:
[READ]

- worked `MERGED_RESEARCH_READER_CORPUS_FINAL.md` as the authority, which is
  the exact status this pass's Phase 5 was going to grant it;
- **retired 332 by direct measurement**, recording the corpus live at
  **382 papers / 211 abstracts / 164 cited**, and explicitly noting the
  works-figure 319 has no replacement because the duplicate census has not
  been re-run. That matches the standing CLAUDE.md rule exactly;
- retracted its own grid-invariance overclaim;
- recorded `xie2023physgaussian` performs no physics validation, read directly;
- recorded Al-Qadami 2023 read in full, mesh 0.05 m and 0.025 m against our
  finest dx 0.05889.

16 files differ from HEAD, including four that exist neither on disk nor in
HEAD: [READ]

```
A docs/CANONICAL_FACTS.md              A docs/BRANCH_INVENTORY_2026-08-26.md
A docs/RESULTS_SUMMARY.md              A docs/branch_inventory_2026-08-26.tsv
A docs/VIDEO_REALISM_2026-08-26.md     A docs/REPRODUCE.md
A docs/PAPER_PRIOR_ART_PATCH_2026-08-26.md   A docs/CCSA_LICENCE_DECISION_2026-08-26.md
A CONTRIBUTING.md  A Makefile  A THIRD_PARTY_NOTICES.md  A requirements.txt
A docs/CCSA_PERMISSION_REQUEST_DRAFT.md
M CITATION.cff  M LICENSE  M README.md
```

**`docs/BRANCH_INVENTORY_2026-08-26.md` already did Phase 1's branch work
today, and did it better.** It walks `refs/remotes/origin`, classifies by
`git branch -r --contains` rather than by name or date, and reports **97 refs,
94 unmerged, 92 with clean names, 39 superseded and 53 unique**, with its own
warning not to quote 92, 94 or 97 without saying which was counted. [READ]
Its TSV is 93 rows including header. [READ]

I did not re-derive those numbers. They are [READ] from that branch's file,
which makes them a single origin, not corroboration of anything I measured.

**`docs/CANONICAL_FACTS.md` is a second thing to flag.** A file by that name is
a competing authority surface next to the register and the corpus master. It is
not on this branch and I have not read its body. Named for Phase 5's framing
question.

### 1.4 `citations/` EXISTS, is tracked, and the corpus reader chain cannot see it

Live: **`citations/` is present, 24 directory entries, 38 files tracked by
git.** [READ] It is not gone, not moved and not folded elsewhere. Contents
include the primary sources this project's rules keep pointing at:

- `ARR_Project_10_Stage2_Report_Final.pdf` (1.1 MB) and
  `ARR table 1 - guidelines and recommendations for limits for vehicle stability.png`
- `Smith-Modra-Felder/` (19 entries, screenshots)
- `WRL reports technical and Research/` (6 entries)
- two full journal PDFs, Dasallas 2025 and Wang and Marsooli 2021
- `Elicit - Flood-Crossing Tire-Ground Friction and Speed Evidence.bib`
- `Elicit - extract-results-review-...csv` (347 KB)
- `vehicle_mpm_coupling_reference.md` (34 KB), `drift_threshold_grounding.md`

**Measured, and this is the finding:** across the five central corpus reader
documents, references to `Elicit` = **0**, to `Connected Papers` = **0**, to the
string `citations/` = **0**, except `CORPUS_MERGE_FINAL_2026-08-22.md` which
mentions `citations/` twice. [READ]

So the directory holding the project's actual primary-source PDFs and the
Elicit export is **invisible to the corpus reader chain**. The reader chain
indexes deep-search output; `citations/` holds hand-collected primary sources.
They have never been joined.

### 1.5 `.bib` files: 11, and the two research artifacts both resolve

`find -maxdepth 5` excluding `.git`, worktrees and `third_party/` returns
**11 `.bib` files**. [READ]

```
citations/Elicit - Flood-Crossing Tire-Ground Friction and Speed Evidence.bib
paper/prior_art_additions.bib              paper/can_it_ford_references_IEEE.bib
paper/canonical_2026-08-02/can_it_ford_references_IEEE.bib
_inbox/can_it_ford_references_IEEE.bib     _inbox/2026-07-30_...IEEE.bib
_inbox/2026-07-31_...IEEE.bib              deliverables/refs.bib
deliverables/paper/overleaf/refs.bib       overleaf_sync/can_it_ford_references_IEEE.bib
docs/overleaf_staging/mpm_foundations_additions.bib
```

- **Elicit output: IS in the repo**, tracked, at `citations/`. [READ]
- **ConnectedPapers output: is NOT in the repo as a `.bib`.** A case-insensitive
  grep for `connectedpapers|connected papers` across `docs/`, `citations/`,
  `scripts/`, `analysis/` returns exactly **two prose hits**, in
  `HANDOFF_2026-08-18_REALISTIC_ENVIRONMENT.md` and
  `RESEARCH_BRIEFS_REALISTIC_ENV_2026-08-14.md`. [READ] No file. The
  "ConnectedPapers output exists as a research artifact" belief is
  **unsupported on this checkout**; it is named in prose and nowhere else.
  Scope stated: I searched those four directories, not the whole tree, and not
  other branches.
- Neither `.bib` is referenced anywhere in the corpus reader chain (0 hits,
  above). Both are stranded from it in the same way `citations/` is.

### 1.6 `.remember/` exists and has 22 corpus-touching files

`/Users/josie/can-it-ford/.remember/` is live, 47 entries, mode `drwx------`.
[READ] `grep -rli "corpus|literature|research reader"` returns **22 files**,
mostly `today-*.done.md` dailies from 08-14 through 08-26 plus four
`logs/memory-*.log`. [READ] `now.md` and `today-2026-08-26.md` both match, and
`now.md` has an mtime of 11:26 today, which is one minute into this pass, so
something is writing it live. Not read further; these are session dailies, not
deliverables, and reading 22 of them is not what this phase is for.

Separately `.claude/memory/` holds **126 files**, of which **32 mention corpus
or literature**. [READ] That is the index already loaded at session start.

### 1.7 Cross-branch commit history

```
$ git log --all --oneline -i -E --grep=corpus --grep=literature \
      --grep="research.*paper" --grep=citation | wc -l
404
$ git log --all --not HEAD --oneline -i -E ...same... | wc -l
199
```
[READ]

**199 of 404 matching commits are unreachable from the current branch.**
Roughly half the project's corpus and citation history is not on
`claude/add-ci-checks`. The bulk are the `R5-D1 unit NN` series
(`claude/r5-research`) and the R9 fan-out tips; the newest are the seven on
`fix/ccsa-acknowledgement`.

### 1.8 Corpus artifacts on disk beyond the known 14

`find -maxdepth 3` on `*corpus*` / `*literature*` / `*papers*`, excluding
`.git`, worktrees and `third_party/`, returns 30 paths. [READ] Removing the 14
already inventoried and this audit file itself, **nine are new to the corpus
family**:

| path | note |
|---|---|
| `docs/COUPLING_MECHANISM_LITERATURE_INDEX_2026-08-23.md` | its own literature index, built 08-23 |
| `docs/LITERATURE_CI_GATES_2026-08-08.md` | the citation bank CLAUDE.md's August 8 addendum points at |
| `docs/R10_LITERATURE_IMPLEMENTATION_2026-08-20.md` | carries the L-4 counter-example working |
| `docs/R9_CORPUS_BIB_GAP_2026-08-18.md` | predates the whole CORPUS_* series |
| `docs/r10/corpus_revision.md` | in a subdirectory, so every flat `docs/*.md` sweep missed it |
| `data/r9_bib_corpus_census.tsv` | the census the 3-of-15 figure rests on |
| `.claude/tooling/corpus_mcp.py` | **a live MCP server**, see Phase 3 |
| `.claude/tooling/corpus_mcp.py.bak-portability` | untracked backup |
| `.claude/skills/research-corpus/` | the skill, currently dirty |

Two more real corpus surfaces the name pattern could not catch: [READ]

- **`data/deep_searches/` holds 29 files**, 28 searches plus `MANIFEST.json`.
  This is the tracked two-phase ingest store the build blocker document
  describes. Sizes range 2.5 KB to 15 KB; the three largest
  (`vehicle-mesh-assets.json` 15 KB, `grid-converged-force-deficit.json`
  14.6 KB, `buoyancy-overestimation.json` 12.9 KB) are the ones carrying a
  `papers` array.
- **`docs/undermind/` holds exactly one file**,
  `2026-08-25_force-overprediction-mechanisms.md`, 4.7 KB, created 08-25 20:56,
  untracked. Carried into Phase 3.

### 1.9 Phase 1 verdict

Genuinely new, in descending order of consequence:

1. **`fix/ccsa-acknowledgement` tip `51effcd`, 2026-08-26 01:41.** A session ten
   hours ago already worked the FINAL master, retired 332 to 382 by live
   measurement, and produced 8 new `docs/` files including a branch inventory
   and a `CANONICAL_FACTS.md`. **Unmerged. Not on disk.**
2. **`claude/r5-research`, 82 commits, 44 stranded `R5_RESEARCH_*` docs.** A
   parallel literature audit the corpus chain does not cite.
3. **`citations/` is alive, tracked, 38 files of primary sources, and the
   corpus reader chain references it essentially zero times.** The two halves of
   this project's literature work have never been joined.
4. **Nine further corpus documents plus `data/deep_searches/` (29) and
   `docs/undermind/` (1) sit outside the inventoried 14.**

Also settled: `claude/r9-reader` and `claude/r9-corpus-bib` are fully merged and
strand nothing. ConnectedPapers output does not exist as a file on this
checkout.

---

## Phase 2, the full r8 sweep

**Headline: `d20-reader.md` is NOT an unexecuted plan, so it does not override this
phase. The real finding is `docs/r10/`, a 42-file tracked acquisition layer holding
the single largest corpus document in the repository, which the corpus inventory
does not mention once.**

### 2.1 The mtime cluster: real content, and the premise is now stale

The six files no longer share one mtime. Live: [READ]

```
CORPUS_MERGE_FINAL_2026-08-22.md          Aug 25 04:31:00
CORPUS_BIB_MERGE_RESOLUTION_2026-08-25.md Aug 25 04:31:01
CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md Aug 25 04:31:01
R9_CORPUS_READ_2026-08-19.md              Aug 25 04:31:01
CORPUS_FINAL_MERGE_REPORT_2026-08-23.md   Aug 26 08:54:12   <- moved
CORPUS_FINAL_MERGE_REPORT_2026-08-25.md   Aug 26 08:54:12   <- moved
```

**Verdict: real content diffs, NOT a git-mechanics artifact.** [READ] Every one of the
six carries an added `ABSORBED 2026-08-25 into ...FINAL.md` block quote. Four carry it
alone (+9 lines each); the two `CORPUS_FINAL_MERGE_REPORT_*` files carry it plus a
second reciprocal `NEAR-IDENTICAL NAME, DIFFERENT DOCUMENT` paragraph (+16 each).
Total 68 insertions, 0 deletions across the six. The shared 04:31 mtime is one script
run stamping four banners, exactly as it looks.

**The inventory's own figures are already a day stale.** `CORPUS_INVENTORY_2026-08-25.md`
records `+7 / -0` for all six. Live it is `+9` for four and `+16` for two. [READ] Whoever
edited CLAUDE.md at 08:53 today also edited these two at 08:54, one minute later. Same
session, and the same session this pass is locked out of CLAUDE.md by.

### 2.2 The near-duplicate reports: resolved, and independently re-measured

The 08-23 versus 08-25 question was **already answered at 08:54 today** by the
reciprocal banner, which claims 9 shared unique non-blank lines out of 278 and 167,
6 of them the banner. [READ]

I did not take that at face value. Re-measured here with `sort -u` over non-blank
lines and `comm -12`: [READ]

| | 08-23 | 08-25 | shared |
|---|---|---|---|
| their measure | 278 | 167 | 9 (6 = banner) |
| **my measure** | **269** | **158** | **10 (7 = banner)** |

Both differ by exactly one on every column, which is a line-counting convention, not a
disagreement. **The conclusion is identical and robust: these are two separate session
reports, not revisions of one another.** 08-23 is the corpus-lineage, bounded-sweep and
proposed-bibliography session; 08-25 is the landing-plan, flag-collision and
terminal-merge session. Roughly 3 percent overlap, most of it the banner.

The third pair is even more separate. `CORPUS_FINAL_MERGE_REPORT_2026-08-25.md` versus
`CORPUS_FOLLOWUP_REPORT_2026-08-25.md`: 158 and 167 unique non-blank lines, **3 shared**,
and all three are boilerplate (`## Standing caveat`, `**DONE.**`, `---`). [READ]
**Effectively zero overlap.** Same date, adjacent names, unrelated documents.

**So the "near-duplicate reports" framing is wrong on all three pairs.** Nothing needs
deduplicating. What they need, and two of the three now have, is a banner saying they
are not each other.

### 2.3 `d20-reader.md`: EXECUTED, and it is a different kind of "reader"

**Plainly: no, it is not an unexecuted plan, and it is not the thing this thread is
trying to do.** [READ]

- Its declared deliverable is `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md`. That file
  is **on disk at 47,683 bytes, mtime Aug 20 02:05, and IS IN HEAD**.
- Its branch `claude/r9-reader` is **0 commits ahead of HEAD**, fully merged.

More important, its subject is not literature. d20-reader's job was to read **nine live
Claude Code session JSONL transcripts** under `~/.claude/projects/`, plus every commit on
nine branches, and produce a contradictions table. Its own words: *"Nobody has read all
of it. That is your entire job."*

**"Reader" means two unrelated things in this project.** The
`MERGED_RESEARCH_READER_CORPUS_*` family is a literature reader. `d20-reader` is a
cross-session transcript reader. They share a word and nothing else. Carried to Phase 5.

### 2.4 `d14-corpusbib.md`: executed, and it CLOSED an item CLAUDE.md still calls open

d14's unit was, verbatim: *"The corpus is NOT a superset of the bibliography ... Whether
that is a sourcing gap or a dropped merge is unresolved and belongs to whoever owns the
index build. That is your unit: resolve it."* [READ]

It resolved it. `docs/R9_CORPUS_BIB_GAP_2026-08-18.md` exists, is in HEAD, and its title
is *"The corpus is not a superset of the bibliography: the builder cannot reach the layer
that holds the missing works, and the gap is one paper wide rather than eleven"*. [READ]
Its answer, including a dated self-retraction of its own first title:

- **not a dropped merge**, `DROPPED_IN_MERGE` is 0;
- **an ingestion gap, not a sourcing gap** (title corrected 2026-08-19, original
  retracted in its section 22);
- **the gap is one paper wide, not eleven**: `shah2018` is the single in-scope absence,
  and it appears in three deep searches, one of them 25 days older than the index build.
  It is absent only because the builder cannot see that search;
- its section 8 is headed *"The index can now report this about itself"*, which was
  requirement 2 of the dispatch.

**The live CLAUDE.md still carries this as `SEPARATE AND OPEN`.** [READ] That is a real
staleness, and it is exactly the kind Phase 5 would have fixed. **Blocked by Phase 0.**
Recorded here instead, and it is the strongest single argument for unblocking CLAUDE.md.

### 2.5 `bodies/`: 11 files, and a complete non-finding

`ls -la` shows 13 lines because two of them are `.` and `..`. **There are 11 files.** [READ]

| file | bytes | first line |
|---|---|---|
| d11-accessor.md | 3902 | `## YOUR SLOT: d11-accessor, branch claude/r9-accessor ...` |
| d12-kramerdata.md | 3069 | `## YOUR SLOT: d12-kramerdata, branch claude/r9-kramer-extract ...` |
| d13-renders.md | 2962 | `## YOUR SLOT: d13-renders, branch claude/r9-renders ...` |
| d14-corpusbib.md | 3359 | `## YOUR SLOT: d14-corpusbib, branch claude/r9-corpus-bib ...` |
| d15-settle.md | 3349 | `## YOUR SLOT: d15-settle, branch claude/r9-settle ...` |
| d16-landing.md | 3563 | `## YOUR SLOT: d16-landing, branch claude/r9-landing ...` |
| d17-moving.md | 7669 | `## YOUR SLOT: d17-moving, branch claude/r9-moving-vehicle ...` |
| d18-platform.md | 4528 | `## YOUR SLOT: d18-platform, branch claude/r9-platform ...` |
| d19-priorcode.md | 4184 | `## YOUR SLOT: d19-priorcode, branch claude/r9-priorcode ...` |
| d20-reader.md | 3821 | `## YOUR SLOT: d20-reader, branch claude/r9-reader ...` |
| d21-jobb.md | 4432 | `## YOUR SLOT: d21-jobb, branch claude/r9-jobb-route ...` |

**Tested, not assumed:** for d14, d20 and d17, `diff <(sed -n '/^## YOUR SLOT/,$p'
dNN.md) bodies/dNN.md` is **byte-identical, 3 of 3**. [READ] `bodies/dNN.md` is exactly
the slot-specific tail of the full prompt. The full prompt is shared-preamble plus body.
**Nothing in `bodies/` is unique content.** Never opening it cost nothing.

There is a second, earlier convention: **`scripts/r8/prompts/_body_d1-safe.md` through
`_body_d10-licence.md`**, flat rather than in a subdirectory. [READ] Same assembly
pattern, r8 era. So the directory is a naming evolution, which is a small irony given
that `d8-naming` is one of the slots.

### 2.6 Header skim, all 23

All 23 have a branch. `d1`, `d2`, `d4`, `d5`, `d7` name theirs in `_body_*` prose rather
than a `## YOUR SLOT` heading, which is why the heading grep missed them.

| prompt | lines | bytes | branch | merged into HEAD? |
|---|---|---|---|---|
| d1-safe | 228 | 12908 | (r8 era, CLAUDE.md + check_claims owner) | n/a |
| d2-persist | 212 | 12036 | (r8 era) | n/a |
| d3-force | 243 | 14199 | `claude/r8-force` | **MERGED** |
| d4-bcmerge | 215 | 12097 | (r8 era) | n/a |
| d5-priorart | 227 | 12852 | (r8 era) | n/a |
| d6-tooling | 216 | 12387 | `claude/r8-tooling` | **MERGED** |
| d7-register | 213 | 12202 | `claude/r8-register` | (see note) |
| d8-naming | 223 | 12526 | `claude/r8-naming` | **MERGED** |
| d9-kramer | 226 | 13098 | `claude/r8-kramer` | **MERGED** |
| d10-licence | 214 | 11990 | `claude/r8-licence` | **MERGED** |
| d11-accessor | 225 | 14346 | `claude/r9-accessor` | **MERGED** |
| d12-kramerdata | 219 | 13513 | `claude/r9-kramer-extract` | **MERGED** |
| d13-renders | 220 | 13406 | `claude/r9-renders` | **MERGED** |
| d14-corpusbib | 225 | 13803 | `claude/r9-corpus-bib` | **MERGED** |
| d15-settle | 225 | 13793 | `claude/r9-settle` | **14 COMMITS STRANDED** |
| d16-landing | 215 | 14007 | `claude/r9-landing` | **MERGED** |
| d17-moving | 257 | 18113 | `claude/r9-moving-vehicle` | **MERGED** |
| d18-platform | 226 | 14972 | `claude/r9-platform` | **16 COMMITS STRANDED** |
| d19-priorcode | 226 | 14628 | `claude/r9-priorcode` | **MERGED** |
| d20-reader | 232 | 14265 | `claude/r9-reader` | **MERGED** |
| d21-jobb | 231 | 14876 | `claude/r9-jobb-route` | **MERGED** |
| d22-gapscan | 96 | 6678 | `claude/r9-gapscan` | **MERGED** |
| d23-overleaf | 77 | 5443 | `claude/r9-overleaf` | **MERGED** |

**Every dispatch branch exists. None of the 23 is an unexecuted plan.** [READ] 16 of 18
checkable branches are fully merged; two are not.

**`claude/r9-settle`, 14 stranded commits, 8 unique files.** The CODE landed:
`analysis/stationarity.py`, `analysis/settle_audit.py`,
`analysis/classify_failure_modes.py` and `analysis/probabilistic_verdict.py` are all on
disk AND in HEAD, so the CLAUDE.md section citing them is sound. [READ] What is stranded
is the WRITE-UP, `docs/R9_SETTLE_FRAMES_2026-08-18.md`, absent from disk and from HEAD,
plus two sbatch files and `analysis/r9_vista_stationarity_pass.py`. Commit subjects
include *"A check that cannot fail is not a check: stationarity reported records it never
ran"* and *"Section 19 was false: 35 comparable long records already existed"*.

**`claude/r9-platform`, 16 stranded commits, 14 unique files.** Same shape: `hf_space/`
is on disk and in HEAD, but `docs/R9_PLATFORM_ROI_2026-08-19.md` and
`.claude/checks/board_splice_check.py` are stranded. Commit subjects include
*"A PUBLIC EMPTY DATASET ALREADY SITS ON THE HUB UNDER THIS PROJECT'S NAME"* and
*"I overwrote a published physics fix on a PUBLIC page"*.

**The pattern is consistent and worth naming: on both stranded branches the code merged
and the document did not.** That is the worst half to lose, because the code cannot say
why it exists.

### 2.7 The eight full reads

**`d3-force`.** Owns `analysis/r8_noforcing_control.py` and
`docs/R8_FORCE_ROUTE_2026-08-18.md`. Its body is mostly a trap warning: `M * dv_cm/dt` is
NOT a force on the free-rigid material-8 path because `v_cm` is overwritten, not
integrated, verified from the pinned solver at `mpm_utils.py:920-923`, `:935-941`,
`:1402-1409`, `:1434`. It names the retracted quantity as already shipped on disk in
`data/failure_modes_by_run.json` (`peak_surge_force_n`, `peak_surge_accel_g`), gives the
plausibility check that should have stopped it (32552 N at g48 is 1.42x vehicle weight
and 36 to 58x a drag anchor of 566 N), and permits only the sign-only monotone-decreasing
observation. **Already reflected**: register D6f condemns `peak_surge_accel_g` by name,
and CLAUDE.md's A-1 carries the material-8 architecture finding. **Not corpus work.**

**`d11-accessor`.** The two-accessor defect in `simulation/r5_physics/sphere_heave.py`:
`fz_over_analytic_measured` (denominator 32.33 N) versus `fz_over_analytic_nominal`
(69.2180 N), which **disagree on sign**, -29.11 to -9.67 percent against nominal versus
+49.36 to +50.29 against measured. **Already reflected** in memory
(`two-force-accessors-differ-by-half`) and in the register. **Not corpus work.**

**`d9-kramer` and `d12-kramerdata`.** The Kramer 2021 supplementary
`energies-14-00269-s001.zip`, 78 entries: 28 experimental extracted, **44 numerical and
4 descriptions never extracted**. d12 inherits d9's `kramer_benchmark.py` and
`docs/R8_KRAMER_INTERCODE_2026-08-18.md`, and is told to check whether conclusions
survive the full set. **Already reflected** in memory
(`kramer-supplementary-eleven-codes`), which independently records 11 codes, 6 groups,
RANS4/RANS5 reversed radial order and 20x row-count spread. Both explicitly forbid
committing Kramer files into the repo (register E8, public repo). **Not corpus work, but
it is literature work**, and it is the clearest case of literature that deliberately
lives OUTSIDE the corpus at `/Users/josie/can-it-ford-refs/`.

**`d7-register`.** Three non-containing register lineages measured live: origin/main 656
lines, `claude/fork-register-reconcile` 1455, `claude/add-ci-checks` 2186 with 542
unpushed. Carries the verbatim warning *"A ZERO-CONFLICT MERGE IS NOT EVIDENCE OF A
CORRECT MERGE"* and instructs re-derivation rather than carrying D3's 104-line figure.
**Directly relevant to Phase 5**, which would have written to the register. **Blocked by
Phase 0 anyway**, though note the register itself is clean; the lock is CLAUDE.md's.

**`d8-naming`.** `sim_standing.py:389` computes `det_ok` from particle count and grid
limit, which is not determinism, yet `all_runs_inventory.csv` reads
`determinism_identical = True` on 17 of 17 while all 20 A2 repeats are bit-different by
the first frame. The field value and "false in practice" do not contradict; **the NAME
does**. The publication-facing half is worse: `make_poster_figures.py:167`, `:565`,
`:602` print *"1100 kg, all runs deterministic"*, and that caption reached the presented
poster PDF. Three scopes disagree on the site count (23 / 4+2 / 5+7) and the prompt says
**re-derive and state your scope** rather than pick one. **Not corpus work, and it is the
most publication-critical item in the whole set.** Not verified live by me.

**`d22-gapscan`.** **This is the corpus-relevant one, and see 2.8.** Its stated purpose:
*"You are the only one whose job is to go and GET what it does not have."* Its
"WHY YOU EXIST" block is now **stale in three figures**: it says the index holds 332
records with 110 lacking abstracts and is built from 8 of roughly 21 deep searches. Live
today those are 382, and 28 searches with 11 ingested as papers. The **structural** claim
survives untouched: the index holds no full text, its largest text blob is 3,477
characters, and it is a discovery instrument rather than a reading one.

**`d23-overleaf`.** Owns the paper. Carries the Overleaf no-common-ancestor hazard, the
three-candidate question of which `.tex` is the paper, four defects in the submitted
paper, and **the live bib key collision**: `alqadami2022` resolves to
`10.1111/jfr3.12828` in `paper/...IEEE.bib` and to `10.3390/su151713262` in
`overleaf_sync/...IEEE.bib`. **Already reflected** in memory
(`overleaf-tex-is-canonical`, `zotero-bib-keys-diverge-from-overleaf`) and in CLAUDE.md's
warning never to quote Al-Qadami's D x V bare. **Not touched this pass**: no `.tex` file
was opened, per the rules.

### 2.8 THE FINDING: `docs/r10/`, 42 tracked files, and the largest corpus document

`d22-gapscan`'s output did **not** land where its own dispatch said. The dispatch names
`data/r10_acquired/` as the PDF store. **That directory does not exist, 0 files.** [READ]
It landed in **`docs/r10/`** instead: **42 files, all 42 tracked by git.** [READ]

```
corpus_revision.md              50504    <- see below
connector_revision.md           33546
connector_revision_AUDIT_d20.md 14785
want_list_deep_searches.tsv     26080    want_list_deep_searches_resolved.tsv  31401
unpaywall_manifest.tsv          26395    disk_resolution.tsv                   25524
all_oa_manifest.tsv             13873    acquisition_manifest.tsv              11634
priority_manifest.tsv            9662    stragglers_resolved.tsv  50 rows
acquired_verified.tsv           41 rows  quote_verification.tsv   31 rows
verified_manifest.tsv            7 rows  reaim_manifest.tsv        1 row
fou19_still_water_read.md        4472    schulz2019_image_particles_read.md     5789
+ 12 scripts and 6 logs (fetch_*, resolve_*, verify_*, scan_new, pdftext.swift)
```

**`docs/r10/corpus_revision.md` is 50,504 bytes. `MERGED_RESEARCH_READER_CORPUS_FINAL.md`,
the declared master, is 44,970 bytes.** [READ] The largest corpus document in this
repository is not the master, and it is in a subdirectory.

Cross-reference count for the string `r10/`: [READ]

| document | references to `r10/` |
|---|---|
| `CORPUS_MERGE_FINAL_2026-08-22.md` | 8 |
| `MERGED_RESEARCH_READER_CORPUS_FINAL.md` | 2 |
| `CORPUS_INVENTORY_2026-08-25.md` | **0** |
| `CORPUS_LINEAGE_STATUS_2026-08-23.md` | **0** |
| `CORPUS_FOLLOWUP_REPORT_2026-08-25.md` | **0** |

**The document whose job was to inventory the corpus, and which is headed "Inventory,
all 14 targets, measured live", references `docs/r10/` zero times.** The master mentions
it twice out of 44 KB. This is not a small omission: `docs/r10/` holds the want list, the
disk resolution, the Unpaywall and OA manifests, a 41-row verified-acquisition table, a
31-row quote-verification table, two full-text reads, and 12 re-runnable scripts. It is
the only place in the repo where the project actually **acquired and verified** full
texts rather than indexing metadata.

Two file names in it point straight at Phase 3: `connector_revision.md` (33.5 KB) and
`connector_revision_AUDIT_d20.md` (14.8 KB). **A connector audit already exists.**
Phase 3 reads it rather than re-deriving from scratch.

### 2.9 Phase 2 verdict

1. **`docs/r10/` is the omission.** 42 tracked files, the largest corpus document in the
   repo, invisible to the inventory that claimed to map the corpus.
2. **No dispatch is unexecuted.** All 23 have branches; 16 of 18 merged. `d20-reader`
   specifically ran and produced a 47 KB deliverable that is in HEAD.
3. **Two branches strand their write-ups while their code merged**: `claude/r9-settle`
   (14 commits) and `claude/r9-platform` (16 commits).
4. **`d14-corpusbib` closed an item CLAUDE.md still marks open**, and answered it more
   precisely than the open item asked: an ingestion gap, one paper wide, `shah2018`.
5. **The mtime cluster is real content**, and the near-duplicate framing is wrong on all
   three pairs (3 percent, 3 percent, and effectively 0 percent overlap).
6. **`bodies/` is a non-finding**, verified 3 of 3 byte-identical to the prompt tails.

---

## Phase 3, connector usage audit

**Headline: the project-level `.mcp.json` wires six servers, and NOT ONE of them is a
literature-discovery connector. Every connector the corpus actually depends on
(Undermind, Elicit, Consensus, Zotero, Scholar Sidekick) lives in a different config
layer. And no Scite retraction check has ever been run on the master's DOIs, so I ran
the equivalent live: 26 checked, 0 retracted, 1 erratum, 1 unresolvable, 1 entry that
turns out to be a one-page editorial.**

### 3.1 `.mcp.json`, read live

786 bytes, mtime Aug 22 22:39. **Six servers, all six with no `headers` block.** [READ]

| server | transport | endpoint / command |
|---|---|---|
| `canford-corpus` | stdio | `/usr/bin/python3` (`.claude/tooling/corpus_mcp.py`) |
| `canford-tacc` | stdio | `/usr/bin/python3` |
| `deepwiki` | http | `https://mcp.deepwiki.com/mcp` |
| `scite` | http | `https://api.scite.ai/mcp` |
| `wandb` | stdio | `scripts/wandb_mcp_launch.sh` |
| `wolfram` | http | `https://agenttools.wolfram.com/mcp` |

**Expected and present:** deepwiki, scite, wolfram. All three confirmed. [READ]

**Present and NOT anticipated by the prompt, worth naming:**

- **`canford-corpus`** is a project-local MCP server exposing `corpus_search`,
  `corpus_read`, `corpus_resolve`, `corpus_inventory`, `corpus_headings`,
  `corpus_cited_status`. **The corpus has its own MCP interface** and no corpus report
  in the inventoried 14 mentions it. Its source is `.claude/tooling/corpus_mcp.py`, and
  `.claude/tooling/` is the untracked directory that has previously blocked every Bash
  call from a worktree.
- **`canford-tacc`** and **`wandb`**, neither literature-related.

**MISSING from `.mcp.json`, and this is the structural finding:** [READ]

| connector | in `.mcp.json`? | mentions across `docs/` + `scripts/r8/` + `citations/` |
|---|---|---|
| **Undermind** | **NO** | **220 hits in 64 files** |
| **Crossref** | NO | 186 hits in 49 files |
| **Unpaywall** | NO | 189 hits in 26 files |
| Scite | **yes** | 186 hits in 63 files |
| Zotero | **NO** | 140 hits in 34 files |
| DeepWiki | **yes** | 114 hits in 46 files |
| Wolfram | **yes** | 76 hits in 48 files |
| Semantic Scholar | NO | 71 hits in 26 files |
| Elicit | **NO** | 63 hits in 18 files |
| Scholar Sidekick | **NO** | 37 hits in 21 files |
| Consensus | **NO** | 27 hits in 14 files |
| Connected Papers | NO | **8 hits in 3 files** |

**The single most-referenced connector in this project's writing, Undermind at 220 hits,
is absent from the project's own MCP config.** It reaches sessions through the
claude.ai / Claude Desktop connector layer instead. That is not a bug, but it has a hard
consequence the corpus documents already describe from the other end: `research_index.py`
is pure stdlib and cannot call an MCP connector, so ingest has to be two-phase, an agent
turn writing `data/deep_searches/<slug>.json` and the builder reading them. **The
absence from `.mcp.json` is the reason that design exists.**

**This was already found and written up.** `docs/r10/connector_revision.md`, 33,546
bytes, dated 2026-08-20, opens with the heading *"0. The finding that reframes everything
else: there are FOUR config layers, not two"* and carries a 20-plus-heading audit
including *"2b. Scite is dead as a server and alive as content, by two independent
routes"*. [READ] A companion `connector_revision_AUDIT_d20.md` (14,785 bytes) audits it.
**I did not re-derive that document's conclusions; the table above is my own live read of
`.mcp.json` plus my own counts, which is a separate origin arriving at the same
structural point.**

### 3.2 Are the mentions real tool output, or just the word in a sentence?

Sampled, two or more per connector. **Real output, not prose.** [READ]

- **Scite, real.** `LIT_QUEUE_2026-07-30.md:56` carries an actual tally,
  *"total 51, supporting 1, contrasting 0, mentioning 49, across 42 citing"*;
  `:255` quotes a full-text excerpt yielding an analytic flotation formula;
  `SUBMISSION_MANIFEST_2026-07-31.md:150` records `smithmodrafelder2019` with
  *"Scite tally 51 total, 1 supporting, 0 contrasting"*. These are returned values.
- **Undermind, real.** `docs/undermind/2026-08-25_force-overprediction-mechanisms.md:3`
  records *"Run 2026-08-25 via the Undermind connector, workspace 'Can it ford'"*;
  `CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md:128` cites content *"read live from
  Undermind workspace"*.
- **DeepWiki, real but correctly demoted.** `COUPLING_MECHANISM_LITERATURE_INDEX_2026-08-23.md:16`
  is headed *"SPRINT 1 IS CLOSED. The DeepWiki hypothesis is REFUTED."* and
  `VERIFIED_FACTS_LEDGER_july24.md:449` states the standing rule that DeepWiki output is
  a hypothesis, never a source. **DeepWiki is used, then adversarially checked, and in the
  one recorded case it lost.** That is the correct use of it.

**Connected Papers is the exception: 8 hits across 3 files, all prose, no output, no
file.** Consistent with Phase 1.5. There is no ConnectedPapers artifact on this checkout.

### 3.3 The retraction question, answered by measurement rather than by absence

**Stated plainly first: I found NO evidence that any Scite retraction check has ever been
run on any DOI in `MERGED_RESEARCH_READER_CORPUS_FINAL.md`.** [READ] The only retraction
audit on record covers something else:

- The master's own lines 209 to 211 record *"9 of 9 DOI-bearing entries matched at high
  confidence, 0 mismatch, 0 ambiguous, 0 not_found, 0 retracted"* **and the master tags
  that `[RECALLED]`, not `[READ]`.** By its own tagging it did not run it.
- That audit covers the **shipped bibliography**, 9 of 15 entries, not the master's own
  corpus. Its own scope caveat names the 6 that carry no DOI in any field:
  `thorpe2026pvwm`, `hsiao2025nerfmpm`, `shand2011arr`, `nws_tadd`, `genesis2024`,
  `fred2026`.
- **The instrument was Scholar Sidekick, not Scite.** `R8_PRIOR_ART_2026-08-18.md:696`:
  *"Scholar Sidekick `auditBibliography` in two batched calls plus one `verifyCitation`"*.
  The vocabulary `matched / mismatch / ambiguous / not_found` is Scholar Sidekick's.
  `docs/r10/connector_revision.md:53` separately records the Scite **server** as
  OAUTH-gated and dead headless, with Scite *content* reachable by two other routes.
  So "run it through Scite" was not available as stated.

**So rather than report an absence, I ran the check.** All 26 distinct DOIs in the master
were extracted and each was passed to `checkRetraction` (Crossref `updated-by`, which
mirrors Retraction Watch), one call per DOI, 2026-08-26. [READ]

**Result: 25 of 26 resolved. 0 retracted. 0 expressions of concern. 1 erratum.
1 unresolvable.**

Three things worth carrying forward:

1. **The erratum reproduces, from a separate origin.** `10.1016/j.joes.2018.05.002`
   (*"Water entry and exit of axisymmetric bodies by CFD approach"*) carries
   `hasCorrections: true`, notice type erratum, erratum DOI `10.1016/j.joes.2020.11.003`,
   dated 2021-03-01. The master **already knows this**, at its item 4: *"An unactioned
   erratum ... Nothing cites the paper yet, so nothing is wrong today, but the pairing
   must travel with it if it is ever cited."* My call is an independent Crossref read,
   so this is genuine corroboration, not the same source twice. **The erratum itself is
   administrative**, a missing Declaration of Competing Interest statement, not a
   substantive correction. Note that the master carries BOTH the paper and its erratum as
   separate DOI entries, which is why 26 counts two.
2. **`10.3970/cmes.2008.031.107` returns `result: null`.** No DOI could be resolved into
   the retraction graph. This is the Tech Science Press CMES record. **It is not
   "clean", it is UNCHECKED**, and it must not be reported as passing.
3. **NEW DEFECT: `10.1111/jfr3.12048` is not a research article.** The master lists it at
   its line 594 as `(Balmforth)`, grouped with Albano on floating bodies and Wang and
   Marsooli. `resolveIdentifier` returns: Balmforth, David; 2013; *Journal of Flood Risk
   Management* 6(2); **title literally "Journal of Flood Risk Management"; pages 69 to
   69.** [READ] A one-page item titled after its own journal is an editorial or masthead
   entry, not a source. The author attribution is right and the work is not usable. This
   is the first substantive defect this audit found in the master's own corpus, and it
   was found only because the retraction sweep resolved every title.

### 3.4 The four Undermind keys: 2 of 4 reached the index, 0 of 4 reached the master

`Gis19b`, `Ben23`, `Raz23`, `Jia16`, traced across `docs/` and `data/`: [READ]

| key | in `FINAL.md` | in `research_corpus_index.json` | in `data/deep_searches/` | files total |
|---|---|---|---|---|
| `Gis19b` | **0** | **yes** | yes (2 files) | 6 |
| `Jia16` | **0** | **yes** | yes (2 files) | 6 |
| `Ben23` | **0** | **NO** | **NO** | 2 |
| `Raz23` | **0** | **NO** | **NO** | 2 |

**None of the four reached the master.** All four appear in exactly two documents:
`docs/undermind/2026-08-25_force-overprediction-mechanisms.md` (the raw Undermind report,
untracked) and `docs/CORPUS_FOLLOWUP_REPORT_2026-08-25.md`.

**`Ben23` and `Raz23` are stranded in the Undermind report only.** They reached no index,
no deep-search export, and no reader-facing corpus document. `Gis19b` and `Jia16` did
reach the index by way of `free-body-load-transfer.json` and
`free-body-load-transfer-expanded.json`.

So the honest answer to "did any make it into FINAL.md or stay stranded in the Undermind
report only" is: **half were ingested to the index and half were not, and all four are
stranded from the master.** The master is not a superset of the index, exactly as the
index is not a superset of the bibliography. That is the same defect one rung further up.

### 3.5 Connector matrix, wired versus actually used here

| connector | wired in `.mcp.json` | reachable this session | evidenced in project writing | verdict |
|---|---|---|---|---|
| deepwiki | **yes** | yes | 114 hits, used then refuted | wired and used, correctly demoted to hypothesis |
| scite | **yes** | server OAuth-gated | 186 hits, real tallies and excerpts | **wired but dead as a server**; content reachable by other routes |
| wolfram | **yes** | yes | 76 hits | wired, lightly used |
| canford-corpus | **yes** | yes | **0 hits in the inventoried 14** | **wired and undocumented** |
| canford-tacc | yes | yes | n/a | wired, not literature |
| wandb | yes | yes | n/a | wired, not literature |
| **Undermind** | **NO** | yes (session layer) | **220 hits, the most-used of all** | **used heavily, unwired; forces two-phase ingest** |
| Unpaywall | NO | via `docs/r10/` scripts | 189 hits | used via scripts, unwired |
| Crossref | NO | via Scholar Sidekick | 186 hits | used indirectly |
| Zotero | NO | yes (session layer) | 140 hits | used, unwired |
| Semantic Scholar | NO | via other servers | 71 hits | used indirectly |
| Elicit | NO | yes (session layer) | 63 hits, plus a tracked `.bib` and CSV | used, unwired, **output not in the reader chain** |
| Scholar Sidekick | NO | yes (session layer) | 37 hits, **is the actual retraction instrument** | used, unwired |
| Consensus | NO | yes (session layer) | 27 hits | used, unwired |
| Connected Papers | NO | no | **8 prose hits, no artifact** | **named, never used, no output on disk** |

**Six wired, three of them literature-capable, and the three heaviest literature
connectors in the project's history are none of them.**

---

## Phase 4, fold-in

No new dated file was created. Everything folded into
`docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` as a new **section 10, "Global audit
fold-in, 2026-08-26"**, roughly 205 lines.

**Placement note.** It was appended AFTER the existing `## Standing caveat` rather than
inserted before it. That is deliberate: the master was carrying another session's
uncommitted edits (mtime 08:53:56 today), and a pure append cannot damage them, whereas an
insert rewrites the whole file. The new section says so in its own first paragraph and
states that the caveat still governs it.

### 4.1 Folded in

| section | content |
|---|---|
| 10.1 | `docs/r10/` is 42 tracked files and holds the largest corpus document; reference counts showing the inventory misses it entirely |
| 10.2 | `citations/` exists, 38 tracked files, and the reader chain references it and Elicit essentially zero times |
| 10.3 | `.mcp.json` wires 6 servers, none of them literature-discovery; `canford-corpus` is undocumented; Undermind's absence is why two-phase ingest exists |
| 10.4 | **the live retraction sweep**: 26 DOIs, 25 resolved, 0 retracted, 1 erratum corroborated from a separate origin, 1 unresolvable and therefore UNCHECKED, and one new defect |
| 10.5 | the four Undermind keys: 2 of 4 in the index, 0 of 4 in the master, and the superset defect one rung up |
| 10.6 | `d14-corpusbib` closed the corpus-versus-bibliography item; CLAUDE.md still calls it open |
| 10.7 | `claude/r9-settle` and `claude/r9-platform` strand their write-ups while their code merged |
| 10.8 | the three near-duplicate pairs are not duplicates; `bodies/` holds no unique content; "reader" names two unrelated things |

**`docs/CORPUS_LINEAGE_STATUS_2026-08-23.md` needed no action: it is already staged (`A `)
in the index.** [READ] Phase 4's `git add` instruction was already satisfied by an earlier
session. `CORPUS_FOLLOWUP_REPORT_2026-08-25.md` and `CORPUS_INVENTORY_2026-08-25.md` are
staged the same way. No `git add -A` was run at any point this pass.

### 4.2 NOT folded in, needs a human decision, recorded as section 10.9

1. **`fix/ccsa-acknowledgement`, 7 commits, 8 new `docs/` files.** Needs a **MERGE
   decision and an AUTHORITY decision**: `docs/CANONICAL_FACTS.md` would be a third
   authority surface beside the register and the master.
2. **`claude/r5-research`, 82 commits, 44 stranded `R5_RESEARCH_*` docs.** Needs a
   **SCOPE decision**: merge, index, or leave. Merging 44 documents into a corpus already
   fighting near-identical names may make it worse.
3. **The two stranded write-ups (10.7).** Needs a **CHERRY-PICK decision**: the two
   documents alone, or the whole branches.
4. **`10.1111/jfr3.12048` removal.** Needs a **COUNT decision**: dropping it changes a
   published figure, and this session did not recompute the 382 / 211 / 164 ladder and
   should not have.

---

## Phase 5, close out

### 5.1 CLAUDE.md: BLOCKED, plainly

```
$ git -C /Users/josie/can-it-ford status --short CLAUDE.md
 M CLAUDE.md
```
[READ], re-checked at 11:41, unchanged since Phase 0.

**This is blocked again, and it is the third consecutive session to be blocked on it.**
CLAUDE.md was NOT edited and the register was NOT edited.

The register itself is CLEAN, so it was technically available. It was still left alone,
because Phase 0's instruction was categorical and because the two are edited as a pair.

**What the block cost, specifically.** The corpus ranking edit Phase 5 was to make **is
already written in the dirty working tree** and merely uncommitted: line 671 of the live
CLAUDE.md already reads *"RESEARCH-CORPUS READER RANKING, reset 2026-08-25. THERE IS NOW
ONE LINE, NOT TWO"* and names FINAL.md the single master, and line 681 carries the dated
2026-08-26 withdrawal of the prior form. None of that is in HEAD. **The task is done and
unlanded, not undone.**

**What is still genuinely missing from CLAUDE.md**, and could not be added:
`SEPARATE AND OPEN: the corpus is NOT a superset of the bibliography` should be closed
and repointed at `docs/R9_CORPUS_BIB_GAP_2026-08-18.md`, per section 2.4 above.

### 5.2 The commit: ONE file, and why not more

**Committed: `docs/CORPUS_GLOBAL_AUDIT_2026-08-26.md` only.**

**NOT committed: `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, and this is a deliberate
refusal.** Measured live before deciding [READ]:

```
$ git diff --stat docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md
 1 file changed, 911 insertions(+), 269 deletions(-)
```

My section 10 is about 205 of those insertions. **The remaining ~706 insertions and all
269 deletions are another session's uncommitted wholesale rewrite**, mtime 08:53:56 today:
it rewrites the title block, the provenance key, section 0's absorbed-file table and the
naming-hazard passage. It looks complete rather than mid-write, but it has not been
reviewed by anyone.

Staging that file by explicit path would still commit ~706 unreviewed lines of another
session's work under this session's message. That is precisely the failure CLAUDE.md
records for 2026-08-07, and a path-limited commit does not prevent it, it only limits
which files are swept, not whose work is inside them.

**So the fold-in is written to disk and left uncommitted, on purpose.** Once the other
session's rewrite is reviewed, the whole file lands in one commit:

```bash
git -C /Users/josie/can-it-ford commit docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md -m "message"
```

The three already-staged files (`CORPUS_LINEAGE_STATUS_2026-08-23.md`,
`CORPUS_FOLLOWUP_REPORT_2026-08-25.md`, `CORPUS_INVENTORY_2026-08-25.md`) were left staged
and uncommitted for the same reason: another session staged them, and this session did not
review them.

### 5.3 Is "the corpus reader" still the right frame

**No. It is at least four separate things that share a word, and treating them as one is
what has kept this loop open.** They have different inputs, different outputs, different
instruments, and none is a superset of the next.

1. **A metadata index.** `data/research_corpus_index.json`, 382 records, built by
   `analysis/research_index.py` from `data/deep_searches/`, queryable through the
   `canford-corpus` MCP server. Holds no full text; its largest text blob is 3,477
   characters. **A discovery instrument.**
2. **An acquisition and verification layer.** `docs/r10/`, 42 tracked files: want list,
   disk resolution, Unpaywall and OA manifests, a 41-row verified-acquisition table, a
   31-row quote verification, two full-text reads, 12 scripts. **This is the only place
   the project actually obtained and checked full texts**, and the corpus inventory names
   it zero times.
3. **A hand-collected primary-source shelf.** `citations/`, 38 tracked files: the AR&R
   report and its Table 1, Smith-Modra-Felder, the WRL reports, two journal PDFs, the
   Elicit `.bib` and CSV. Referenced by the reader chain essentially zero times. Plus a
   deliberate off-repo annex at `~/can-it-ford-refs/` for Kramer, because register E8 is
   open.
4. **A consolidation narrative.** The `MERGED_RESEARCH_READER_CORPUS_*` and `CORPUS_*`
   family, which is mostly documents about the other three rather than about literature.

And a fifth that is not literature at all: **`d20-reader`**, the cross-session transcript
reader, whose deliverable `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md` is 47,683 bytes in
HEAD. It shares the word "reader" and nothing else.

**The diagnostic that settles it.** Each layer fails to contain the next, and every one of
these was measured this session:

```
the paper cites            14 works, 11 absent from the index      (one is a real gap, shah2018)
the index holds           382 records, 0 of the 4 Undermind keys reaching the master
the master holds           26 DOIs, and does not reference docs/r10/ or citations/
docs/r10/ verified         41 acquisitions the master's ladder does not count
citations/ holds           38 primary-source files the chain never cites
```

**Every arrow points the wrong way.** The thing called "the corpus" is the smallest of the
five, and the two layers holding actual readable sources are the two least referenced.

**What follows from that.** The next pass should not be another merge. Four more
consolidation documents will not make `citations/` visible to the index or put
`docs/r10/`'s 41 verified acquisitions into the ladder. What is missing is a **join**: one
table keyed on DOI with a column per layer, saying for each work whether it is in the
index, in `docs/r10/` as verified full text, on the shelf in `citations/`, and cited in
the paper. That is a script, not a document, and `analysis/research_index.py` already owns
four of the five inputs. **The corpus reader was never the deliverable. The join is.**

### 5.4 Done, and still open

**Done this pass:**
- Every phase read-only work completed, Phases 0 through 3.
- The mtime cluster, the three near-duplicate pairs, `bodies/`, and the `d20-reader`
  question are all settled and will not need re-deriving.
- A live retraction sweep on all 26 master DOIs, which had never been run.
- One new substantive defect found in the master, `10.1111/jfr3.12048`.
- Section 10 written into the master, on disk.
- This audit file committed.

**Still open, in priority order:**
1. **CLAUDE.md is uncommitted and blocking.** Its corpus ranking edit is written and
   unlanded, and its `SEPARATE AND OPEN` corpus-versus-bib item is stale. Needs whoever
   holds it to commit or discard.
2. **The master's 911-line uncommitted rewrite**, including this pass's section 10, needs
   review and one commit.
3. **The four decisions in section 10.9**: the ccsa branch and `CANONICAL_FACTS.md`
   authority question, r5-research's 44 documents, the two stranded write-ups, and the
   `10.1111/jfr3.12048` count change.
4. **The join table**, per 5.3.

### 5.5 What this pass did not do

- No `.tex` file was opened or edited.
- `docs/R9_CORPUS_READ_2026-08-19.md` was read but not edited.
- CLAUDE.md and the register were not edited.
- No `git add -A`, no `git add .`, no `git commit -a`, no force push.
- **Nothing here has been adversarially reviewed.** The `physics-skeptic` path was not
  invoked, so every claim above is UNREVIEWED. The counts are re-derivable from the
  commands quoted inline; the judgements in 5.3 are not, and are marked as judgements.

---

## Addendum, the push, appended after the audit commit

`69d2a53` was committed path-limited (1 file, 1003 insertions), leaving the three
already-staged corpus documents staged and uncommitted, confirmed by
`git diff --cached --name-status`. [READ]

Push range checked before pushing, per the standing rule that a path-limited commit
protects the commit and not the push:

```
$ git rev-list --count origin/claude/add-ci-checks..HEAD
1
$ git diff --name-status origin/claude/add-ci-checks..HEAD
A  docs/CORPUS_GLOBAL_AUDIT_2026-08-26.md
```
[READ] Exactly one commit, one file, nobody else's work in the range.

**THE FIRST PUSH FAILED AND DID NOT LAND.** [READ]

```
error: RPC failed; curl 56 Connection died, tried 5 times before giving up
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date
```

**Note the trailing `Everything up-to-date` on a FAILED push.** Read alone, that line
says the push succeeded. It did not. `git ls-remote` immediately afterwards returned
`436a5f0` for `refs/heads/claude/add-ci-checks` while local HEAD was `69d2a53`, so the
remote was unchanged. This is a concrete instance of the standing rule that a command's
own output is not evidence the remote updated, and it is a worse case than the usual one,
because the misleading line is a success message rather than a silent exit 0.

Retried once. Second attempt:

```
To https://github.com/jcerrell-IS/can-it-ford.git
   436a5f0..69d2a53  claude/add-ci-checks -> claude/add-ci-checks
```

**Confirmed landed by `ls-remote`, not by exit code:** remote
`refs/heads/claude/add-ci-checks` is now `69d2a5352a7824c1cd0d8b2df93f03a27d46c5dc`,
equal to local HEAD. [READ] No force push at any point.
