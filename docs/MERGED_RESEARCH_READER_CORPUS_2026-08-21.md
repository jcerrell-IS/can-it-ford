# The Merged Research Reader Corpus, second pass

> **SUPERSEDED 2026-08-23 by `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`.** This file is the pass-2 record and is kept verbatim. FINAL carries what pass 2 could not have had: six Undermind deep searches that existed upstream and reached no file in this repo, the resolution of the coupling-defect DOI question in favour of `10.1016/j.cma.2022.114809`, and a primary-source read of `10.1016/j.jcp.2017.06.047`. Note also that `docs/CORPUS_MERGE_FINAL_2026-08-22.md` is a SEPARATE line and remains authoritative on the 138 catalogued-but-never-cited DOIs. Nothing here has been deleted or edited.

**Supersedes `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md`.** That file remains on
disk as the pass-1 record. Where the two disagree, this one wins, and every disagreement
is named in section 1 rather than left for a reader to discover.

Built 2026-08-21 by a verify-then-implement session working from the pass-1 reader, the
machine bundle `~/can-it-ford-workflow-archive/MERGED_READER_CORPUS.json`, and the
salvaged working tree `/private/tmp/canford-gapclose/`.

**Provenance key, applied to every claim below:** `[R]` read directly by me this session,
`[I]` inferred from something I read this session, `[X]` relayed from pass 1 or another
document and NOT re-checked. Nothing here is `[R]` unless I personally ran the command.

---

## 0. The dispatch's premise was false, and that shapes everything below

The pass-2 dispatch said to run "under a working WebSearch/WebFetch backend (the first
pass's model routing was broken, verify this is fixed before starting)". I verified first,
as instructed. **It is not fixed.** `[R]`

- `WebSearch` -> `There's an issue with the selected model
  (deepseek-ai/DeepSeek-V4-Flash:deepinfra).`
- `WebFetch` on `https://api.crossref.org/works/10.1115/1.4071177` -> the identical error.
- `WebFetch` on a second URL returned `HTTP 404 Not Found`. **That is not evidence the
  tool works.** The transport reached Crossref and reported a status before the
  summarising model was invoked. It is exactly the half-dead mode pass 1 recorded at its
  section 5.6: status and redirect detection survive while content extraction dies. **A
  status code from WebFetch must never be read as a successful fetch.**

Same model id `CLAUDE.md` records from 2026-08-19. Two days on, still live.

**Everything network-shaped below was therefore done with `/usr/bin/curl` and
`urllib`, which work.** `[R]`

---

## 1. THE DIFF: what pass 1 got wrong, what it missed, what survived

### 1.1 Wrong

**a. "All 11 DOIs asserted anywhere in `CLAUDE.md` resolve at Crossref."** `10.13021/G8JS5D`
returns **HTTP 404 at Crossref** and resolves at **DataCite**: "2010 Toyota Yaris Finite
Element Model Validation Coarse Mesh", George Mason University, 2016. `[R]` The DOI is
genuine and the finding built on it stands. The **method claim** is wrong: registration
agency was never checked, so "resolves at Crossref" was asserted of a DOI that does not.
Same predicate-error class pass 1 catalogues in its own section 0.

**b. "`~/.claude/projects/` holds 98 directories, 88 of them can-it-ford."** Live today:
**17 directories, 15 can-it-ford.** `[R]` The worktree-specific project directories were
cleaned between 2026-08-20 and now. Consequence, and it is the serious half: **the 3,148
DOIs pass 1 attributed to "the 87 other project dirs" are no longer re-derivable from
source.** That evidence is gone.

**c. "`.remember/now.md` is zero lines."** It is **2 lines** `[R]`, and it holds a note
timestamped 00:26 tonight from a *different* live session recording that it began this
same corpus-verification task and did not finish it.

**d. `vehicle_params.py:239` for the D×V rounding defence.** Live it is **`:248`** `[R]`,
nine lines off. `gates.py:29` was correct. Positional citation decayed inside 24 hours,
which is the rule `CLAUDE.md` states about itself, holding corpus-wide.

**e. The bundle understates its own salvaged work by half.** `gapclose_salvage.what_survived`
records "268 of 3,433 blocks read; 24 candidate live+novel findings in notes_a.md". The live
`notes_a.md` shows **blocks 0 to 468 read and candidates c1 through c49** `[R]`. Twenty-five
findings the bundle does not know it has.

**f. My own pass-2 error, recorded in place.** My first contamination regex matched `_bibNN`,
`_refNN` and `_bNN` and **missed `_bbNNNN`**, the exact anchor form pass 1 names in its
section 0 as the one inflating the second population. It scored 343 anchors from a single
review article as "candidate real work". Caught and re-run before any number was reported.
`[R]`

### 1.2 Missed

**a. `README.md` contradicted itself about the Yaris tensor, one paragraph below the table
that gets it right.** Pass 1 flagged `README.md:61`; live, `:61` was already correct and the
defect had moved to the prose below it, which asserted without qualification that
CG heights and measured tensors "come from the NHTSA Light Vehicle Inertial Parameter
Database ... measured on instrumented rigs, not box estimates". False for `compact_sedan`.
`[R]` **Fixed this session, commit `cb2d3c2`.**

**b. `vehicle_params.py` still carried the refuted claim in two places pass 1 did not name**,
at `:149-150` and `:157`, while notes 2 and 3(a) of the same file already refuted it. `[R]`
**Fixed, `cb2d3c2`.**

**c. `CLAUDE.md` has two dangling pointers in its corrections-authority section.** `[R]`
`docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md` does not exist, and is cited both
there and at `scripts/semi_empirical_baseline.py:56`. The "`_GRIDAWARE` sibling" of
`VERIFIED_FACTS_LEDGER_july24.md` does not exist either; only the base file does.

**d. Both `floor_friction` and `coup_friction` are literally `0.55` in live code**, in
different files: `floor_friction=0.55` at **9 sites**, `coup_friction=0.55` at **6 code
sites** plus 4 in a cache. `[R]` Register line 117 warns "Both have appeared as 0.55 in this
project's documents. Never conflate." That warning is load-bearing and now measured.

**e. The register's site list for `floor_friction` is incomplete.** Item 29 names
`sim_standing.py`, `sim_dam_break.py`, `box_sdf_collider_setup.py` and the Genesis Track 2
files. Live walk finds **9 sites and `box_sdf_collider_setup.py` is not among them**, while
six unnamed ones are, including **`.claude/hooks/session_start_protocol.py:6`** `[R]`. A
hook is asserting a physics parameter into every session start.

**f. 1609 kg and 2337 kg have two different provenance stories in live files.** The register
at line 219 says "1609 kg = 2020 Nissan Rogue" and its resolved-claims table calls the
"unsourced" finding closed. But `sim_standing.py:53` sources 1609 to "AR&R large_passenger
class figure (gates_both_scenarios.py:22)", and `scripts/class_specific_2026-08-08.sbatch:52-56`
states plainly that **the Rogue LS-DYNA deck header carries no mass at all** and that 1571.3
is web-sourced from cars.com. `[R]` `gates_both_scenarios.py:19-20` confirms 1609/2337 are
paired with AR&R class names, not with vehicles. **The register's "resolved" row is not
safe to lean on.**

### 1.3 Survived a second check

Re-verified against primary sources this session, not relayed:

- **The measured Yaris tensor and the DO-NOT-WIRE conclusion.** `[R]` via DataCite.
- **The D×V floating-point defence.** `round(depth_m * velocity_ms, 6)` live at
  `gates.py:29` and `vehicle_params.py:248`. `[R]`
- **He et al. 2026, `10.1115/1.4071177`.** Crossref returns "Predicting Vehicle-Water
  Interaction in Shallow Water: Simulations and Experimental Validation", He, Hao, *Journal
  of Computational and Nonlinear Dynamics*, 2026-03-11. `[R]` Adverse to the L-7 novelty
  framing, exactly as pass 1 said.
- **The deep-search false pass, in full.** 21 search JSONs, **zero** carrying a `papers`
  array, **780** papers as an integer only, index still **332**, and `--source-audit`
  printing `reaching the corpus by NO route: 0` / `OK (0 problem(s))` / exit 0. `[R]`
  **Fixed this session, commit `924c180`.**
- **CI is greener than it is true, every clause.** 2 of 6 steps carry `continue-on-error`;
  the workflow is absent from `origin/main`; against a clean `origin/main` extract,
  `params_check` exits 0, `register_integrity` exits 0, **`count_claims` exits 1 with 25
  blocking defects**, and **3 of 6 steps have no script on main**. `[R]`
- **The register contradicts itself on `floor_friction`.** G4a and the resolved-claims table
  say sourced; item 29 says "IS UNSOURCED" and "nothing sources it". `[R]` **Already filed
  upstream as R1 on `claude/r8-register`** `[R]`, so it needs a merge, not another edit.
- **`/usr/bin/ls` and `/usr/bin/cat` do not exist; `/bin/` has them.** `[R]`
- **`pdftotext` exists**, `/opt/homebrew/bin/pdftotext`, poppler 26.07.0. `[R]`
- **`SESSION_STATE.md` is 108 lines.** `[R]`
- **`sphere_heave.py` is a stale path, not a lost file**: present on `claude/r5-physics`
  and on `origin/claude/r5-physics`. `[R]`

### 1.4 Already fixed before pass 2 opened, so do not act on them

- `CLAUDE.md` item 4 leg (a): the string "No measured Yaris tensor exists" returns **zero
  hits**; the file already carries the correction. `[R]`
- `flood-mpm-debugging-reference` on LS6: the skill already says **LS6 is x86_64**, confirmed
  on compute node job 3378048, node c301-003. `[R]`
- `CLAUDE.md` on worktree counts: the "2 directories" text is gone. Its replacement, "33
  worktrees, 28 under `.claude/worktrees/`", is **itself now stale**: live is **24 entries
  and 19 under `.claude/worktrees/`** `[R]`. The clause's own instruction, re-measure rather
  than quote, is the correct handling, so I did not restate a number there.

---

## 2. Section 8 of pass 1, worked as the task list

### 2.1 The unread mined blocks

**The pool is 7,682 blocks across 9 layers, 7,543 distinct after hashing, 138 duplicated.**
`[R]` Pass 1 states 7,675 and 7,712 in different places and the dispatch says 7,622; mine is
`len(blocks)` summed over `mined_layers[*].blocks`, stated with its method as the corpus's
own rule requires.

**The finding that changes what this bundle IS.** The blocks cite **915 distinct source
files. 745 of them, 81.4 percent, no longer exist on disk.** `[R]` Under the worktree project
directories specifically, **213 referenced and 12 alive**. For four fifths of its sources
the mined text in this bundle is **the only surviving copy**. It is not a distillate of a
readable corpus any more; for most of its content it is primary.

**A novelty predicate that failed, reported rather than used.** I first tested novelty by
asking whether a 120-character shingle of each block appears in the reader documents. It
returned **7,358 of 7,543 "novel"** `[R]`, which is not a finding, it is a broken predicate:
transcripts almost never reproduce document prose verbatim. **I discarded it** rather than
report 7,358 novel findings, and pivoted to extracting checkable assertions instead. This is
the same class of error the corpus catalogues, caught inside my own pass.

**What assertion-level extraction returns.** Regexing `parameter <op> number` across all
7,543 blocks gives **367 distinct (parameter, value) pairs** `[R]`. The consequential ones,
each then checked against live source:

| assertion in the blocks | count | live check |
|---|---|---|
| `coup_friction` = 0.55 | 215 | **live at 6 code sites** `[R]`, distinct from `floor_friction` |
| `floor_friction` = 0.55 | 127 | **live at 9 sites** `[R]`, register's list of 4 is incomplete |
| `floor_friction` = 0.025 / 0.0250 | 5 | **no live site** `[R]`; these are Nihei discussion, not code |
| `G` = 9.80665 | 148 | historical; one dead-code site survives |
| `grid_density` = 128 | 43 | live at `can_it_ford_L2_mpm_ytest.py:32,:137` `[R]`, deprecated Genesis path |
| `mass_kg` = 1571.3 | 1 | **live at 18 sites** `[R]`, web-sourced, deck states no mass |
| `mass_kg` = 2270.0 | 1 | **live at 17 sites** `[R]`, deck-sourced, Silverado header line 28 |

**Coverage, stated plainly:** I triaged all 7,543 distinct blocks by signal class and
extracted assertions from all of them; I did **not** read 7,543 blocks in prose, and neither
did pass 1. The 49 candidates in `notes_a.md` cover blocks 0-468. **7,075 blocks have been
machine-triaged and never read.** That is the honest number.

### 2.2 The 768 base64 PDF page images

**Not decoded.** The 148.4 MB sit inside agent transcripts whose parent directories are part
of the 745 that no longer exist `[I]`, so the decode target is smaller than pass 1's figure
and I did not establish how much smaller. **Carried forward, unclosed.**

### 2.3 The 73 reference PDFs

**Pass 1's extraction did not land, and the bundle says so about itself:** `G3` reports "all
73 PDFs inventoried and extraction attempted; manifest has 73 entries but **ZERO carry
extracted text**". `[R]` So pass 1's "read to 4-12 pages each" describes an earlier round,
not the salvaged manifest. **Not re-extracted this session. Carried forward, unclosed.**

### 2.4 The DOI contamination check: CLOSED, and it is the strongest result here

Two independent methods, run separately, agreeing.

**Structural filter over all 3,848 DOIs absent from the committed corpus** `[R]`:

| class | n |
|---|---|
| reference anchors (`_bbNN`, `_bibNN`, `_bNN`, `_brNN`, `_sbrefNN`, `_chNN`) | **807** |
| Crossref **funder** ids, not papers | 29 |
| truncated legacy SICI DOIs, cut at a colon | 15 |
| Zenodo deposits | 12 |
| truncated or malformed | 8 |
| arXiv DOIs | 33 |
| supplementary sub-DOIs | 3 |
| **candidate real works** | **2,941** |

**The one-document inflation test pass 1 demanded, now run:** the **807 anchors come from
just 15 parent documents**, and **343 of them from a single review article**,
`10.1016/bs.aams.2019.11.001`. `[R]` Pass 1 asserted this qualitatively; it is now counted.

**Validation, two ways.** A seeded random sample of 60 candidates resolved at Crossref at
**90.0 percent** `[R]`. Independently, the pass-1 Crossref cache of 3,360 records resolves at
**66.9 percent overall**, but **88.0 percent once the 807 anchors are excluded** `[R]`, and
**only 1 of 807 anchors resolves**, which is the proof that they are not works. Two methods,
separate origins, 88.0 and 90.0. **So roughly 2,600 real works sit outside the committed
corpus**, derived structurally rather than by carrying a rate between populations.

**The contamination answer itself.** Of 54 sampled DOIs whose titles I fetched, **29 (53.7
percent) are off-topic** `[R]`: Monte Carlo methods in *Physical Review D*, friction stir
forming, a paleoclimate loess profile in Romania, "Lost Branches on the Tree of Life" in
*PLoS Biology*, electric-vehicle battery switching, nepheloid layers over continental
shelves. These were swept from shared directories, not from this project's literature.
**Caveat on my own classifier, stated because it cuts against my number:** it keys on title
words, so it misfiled `10.4271/2015-26-0188`, *State of the Art Water Wading Simulation
Method to Design Under-Body Components*, as off-topic. That paper is **directly relevant
prior art on vehicle water wading and is cited nowhere in this repo** `[R]`. The true
on-topic share is therefore **higher than 46.3 percent**, and the sweep's real yield includes
prior art the project has not seen.

### 2.5 Vista and LS6

**Blocked, not skipped.** Non-interactive SSH to both hosts fails at TACC's MFA gate `[R]`:

    ssh -o BatchMode=yes vista -> "At the TACC Token prompt, enter your 6-digit code"
    ssh -o BatchMode=yes ls6   -> "Permission denied (keyboard-interactive)"

Every remote claim carried by pass 1, namely Vista 591 SUs, LS6 9,536 SUs, `/home1` at 89.52
percent, **the 14 unpushed `realism_track` commits**, and the re-measured 93.8 percent idev
burn, is therefore **`[X]` relayed and unverified in this session**. **This needs an
interactive session.** The 14 commits are the item worth doing first: fourteen commits of
physics existing only on Vista is an unbacked-up single point of failure.

### 2.6 `~/Desktop` and `~/Documents`

**Scoped and measured, not swept.** `~/Desktop` holds **187,951 files** and `~/Documents`
**11,641** `[R]`. Exhaustive sweeping is not a session-sized task and saying otherwise would
be the same over-claim pass 1 warns about. What is worth naming now: `~/Desktop` carries
`CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/`, `CAN_IT_FORD_MASTER_2026-07-26/`,
`CanItFord_Kumar_2026-07-26/`, `CANITFORD_MESH_INTAKE_2026-07-26/`,
`CANITFORD_RENDER_FIX_2026-07-26/` and `MyLibrary_zotero-export_23-works_NOT-the-paper-bib.bib`
`[R]`. **Carried forward, unclosed, with the target list built.**

---

## 3. Live findings this pass added, with their fixes

Three commits, each path-limited, each on a claim refuted against a primary source in the
same session.

**`cb2d3c2`** `[R]`
- `CLAUDE.md` item 3 said `core/solver.py:167-169` hardcodes gravity "unconditionally".
  Read at the pinned solver `544c93dd`: `:166` is `params = {**params, **overrides}` and
  `:167-169` is `set_parameters_dict({"material": name, "g": [0,0,-9.81], **params})`, so
  **`**params` expands after the `g` key and a caller-supplied `g` wins**. It is a default,
  not a constant, and **no engine patch is needed to change it**. The conclusion is
  unchanged: `newtonian()` carries no `g` key at `materials/__init__.py:125-130` and the
  driver passes no override, so all 17 gated runs did run at exactly 9.81. The same item
  cited the call site as `sim_standing.py:127`; live it is **`:205`**.
- `vehicle_params.py` and `README.md`, as in 1.2a and 1.2b.

**`924c180`** `[R]`. `--source-audit` could not go red. Both its predicates were metadata
predicates. Neither asked whether a single **paper** from a search entered the index. Joining
`papers[].reports` against the deep-search slugs shows **21 of 21 reach as metadata, 8 of 21
reach as papers**, the other 13 standing for 780 papers. Added a `PAPERLESS` class, printed
the two numbers separately, named all 13 with their paper counts, counted them into the
failure total. **Now exits 1 with 13 problems.** `--source-audit` is not a step in
`canford-checks.yml`, so nothing in CI changes.

---

## 4. Held for Josie, not done

Nothing in this list was executed.

1. **Push.** Three commits sit unpushed on `claude/add-ci-checks`, which was already 130
   commits ahead of `origin/main` before them. Any push needs `PUSH_OK=1` and her word.
2. **Merge `claude/r8-register`.** The `floor_friction` contradiction is already filed there
   as R1 and the branch's own message calls the merge a take-mine, 975 insertions. Editing
   the register on the integration branch instead would widen the only conflict still
   growing. **This is a branch decision, not an edit.**
3. **`canford-checks.yml` on `origin/main`.** Three of its six steps have no script there and
   `count_claims` exits 1 with 25 defects, so it cannot be merged as-is. Public-surface
   change, held.
4. **Public surfaces.** `models/josiecerrell/can-it-ford-sweep-v1` public with no README and
   no licence, and `can-it-ford-demo` public and broken, both `[X]` from pass 1 and both
   write operations. Held.
5. **Deletions.** None proposed. Nothing was deleted or archived this session.

---

## 5. What is still NOT in this corpus

Pass 1's section 8 with this pass's results folded in, so the list stays honest.

- **7,075 of 7,543 distinct mined blocks are machine-triaged and unread in prose.** Assertion
  extraction covers all of them; reading does not.
- **The 768 base64 PDF images are still undecoded**, and their source transcripts are
  partly among the 745 files now gone.
- **The 73 reference PDFs still have zero extracted text**, by the bundle's own manifest.
- **The contamination check is closed** and is the one Section 8 item this pass finished.
- **Vista and LS6 remain unswept**, now with the reason measured: MFA blocks non-interactive
  SSH from this session.
- **`~/Desktop` and `~/Documents` remain unswept**, now with the target directories named
  and the scale measured.
- **The provenance warning still governs.** Of 3,291 atomic findings in the bundle, **3,289
  have a single origin** `[R]`. Where this pass reports agreement between two methods, it
  says so explicitly and names both.

---

## 6. Where everything lives

| artifact | what it is |
|---|---|
| this file | the pass-2 reader, supersedes the 2026-08-20 one |
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` | pass 1, retained as the record |
| `~/can-it-ford-workflow-archive/MERGED_READER_CORPUS.json` | the machine bundle |
| `/private/tmp/canford-gapclose/notes_a.md` | **c1-c49, the 49 candidates pass 1 did not know it had** |
| `/private/tmp/canford-gapclose/g4_crossref_cache.jsonl` | 3,360 cached Crossref resolutions |
| `/private/tmp/canford-gapclose-v2/pass2/` | this pass's scripts and checkpoints |
