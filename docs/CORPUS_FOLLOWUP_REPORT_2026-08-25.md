> **NOT ABSORBED, AND DELIBERATELY SO.** This file carries no ABSORBED banner because it is a
> SUCCESSOR to `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, not an input to it: it was
> written at 20:57 against the master's 20:51 and it MODIFIED the master (the 5.2 conclusion)
> `[READ]`. The nine banner-stamped documents predate the consolidation; this one postdates it.
> The master remains the single master; this is the record of the pass that followed.
> The full corpus map is `docs/CORPUS_INVENTORY_2026-08-25.md`.

---

# Corpus follow-up report, 2026-08-25

Read-only except the four files named in "What was written". Nothing staged, committed or
pushed. Every claim tagged `[READ]` (command output or file bytes this session), `[RECALLED]`
(carried from a document, not re-derived) or `[INFERRED]`.

---

## Where this prompt's own stated facts were wrong

Listed first, because two of them would have caused duplicated work.

1. **"HEAD moved past 3fbb81e to at least 57db739, possibly further."** Understated. Live HEAD
   is **`9f18fc2`**, 2026-08-25 04:30:59, **470 commits ahead of `origin/main`** `[READ]`.
   `57db739` and `c82adb7` are both already ancestors.
2. **"The F-bar/locking finding has not been folded into FINAL.md as of the last check."**
   **FALSE.** The prescribed grep returns **five hits at lines 239, 241, 248, 254 and 262**
   `[READ]`. Section 5.2 was written earlier in this same session and already carries both the
   finding and job 923239's refutation. Step three therefore became a scoping fix, not a fold.
3. **"grep -i undermind .mcp.json"** is the wrong availability test. It returns nothing, yet
   Undermind **is** live as a claude.ai connector and the query ran. See step five.
4. The step-four `find` commands arrived **LaTeX-mangled** (`−𝑖𝑛𝑎𝑚𝑒"∗.𝑝𝑑𝑓"`). I used their
   stated intent. Also, `-newer` against `MERGED_RESEARCH_READER_CORPUS_FINAL.md` is
   self-defeating once that file is edited, so I used the fixed baseline 2026-08-25 04:33.

Correct in the prompt and confirmed: the merge, `a83a38b`, `c82adb7`'s skip of this file, and
the `+0.0596` slope.

---

## Step zero, sanity

`Josephines-MacBook-Air.local`, `/Users/josie/can-it-ford`, branch `claude/add-ci-checks`,
HEAD `9f18fc2 2026-08-25 04:30:59 Audit: P-2 flips under a corrected mass distribution, and six
claims withdrawn`, **470 commits ahead of `origin/main`** `[READ]`. No leftover background jobs.

**DONE.**

---

## Step one, section 1 staleness confirmed and corrected

`git merge-base --is-ancestor de18180 HEAD` returns **true** `[READ]`. The merge landed
**2026-08-24 17:56:42** via **`a83a38b`**.

**The commit-message mismatch, measured rather than asserted** `[READ]`. `a83a38b` carries
**4,548 insertions across 7 files**. Only `docs/SUBMISSION_STATUS.md`, at **+4 lines**, matches
its subject "Record poster and paper submission status per direct human confirmation". The
other six files, roughly 4,544 lines, are the corpus-bib merge: `research-corpus/SKILL.md`,
`analysis/research_index.py`, two `data/deep_searches/*.json`, `data/r9_bib_corpus_census.tsv`
and `docs/R9_CORPUS_BIB_GAP_2026-08-18.md`.

Three stale OPEN verdicts confirmed still present in the file before the edit, at `:44`, `:71`
and `:270` `[READ]`.

**Appended** a dated correction block to the END of
`docs/CORPUS_LINEAGE_STATUS_2026-08-23.md`, 316 to **357 lines**. Sections 2, 3 and 4 untouched
`[READ]`. It states the corrected fact, cites `a83a38b` and `c82adb7`, and records explicitly
that **this file was the one document `c82adb7`'s own session named as skipped**, which is why
the stale OPEN survived an extra day.

**DONE.**

---

## Step two, the ranking update

**BLOCKED. Named blocker: `CLAUDE.md` is dirty under a concurrent session**, `+41/-17`,
mtime 2026-08-25 04:18:08 `[READ]`. Three other sessions were active in this repo during this
work. The standing rule forbids two sessions touching one file without sequencing, and the
prompt says not to force it.

**One thing worth knowing for when it clears:**
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` **is clean** `[READ]`. The blocker is
CLAUDE.md alone. Because the instruction requires both edits in the same commit, I did not
update the register on its own, which would have split the change. **The register edit is ready
the moment CLAUDE.md is committed or reverted.**

Replacement ranking text is already drafted in
`docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` section 8, item 1.

---

## Step three, the finding was already folded, so I fixed its scoping instead

The prescribed grep is **not empty**, see the corrections above.

Section 5.2 already carried the locking finding and the refutation together. **What it did not
do is state the conclusion in the terms this prompt asks for**, so that was added `[READ]`:

- **Job B's +34 to +64 percent over-prediction is NOT explained by volumetric locking**, given
  the +0.0596 log-log PPC slope against a required -2.
- **This eliminates one candidate, it does not identify the mechanism.** A flat slope is
  *consistent with* velocity-projection bias, which is not the same as establishing it. No
  positive test has been run.
- **The over-prediction remains OPEN and unexplained.** Explicit instruction added not to cite
  the section as a diagnosis and never to write that Job B is understood.

FINAL.md 691 to **703 lines**.

**DONE.**

---

## Step four, bounded sweep

`~/Desktop` and `~/Documents`, `-maxdepth 3`, newer than 2026-08-25 04:33, matching
`*.pdf`, `*.md`, `*.tsv` or `*can*ford*`, excluding `SENSITIVE_DO_NOT_SHIP` and `DO-NOT-PUSH`:

**Zero results from both roots** `[READ]`. No new material has appeared since the master was
written. Clean negative, nothing to triage, which is why this step took minutes rather than the
predicted long tail.

**`~/Documents/CANITFORD_D10_CROSSSLOPE_2026-08-14/` EXISTS and IS already reflected**
`[READ]`. It holds 9 files, 3.8 MB: eight run JSONs (`S000_rep0`, `S000_rep1`, `S002`, `S006`
and four `STILL_` variants) plus `SHA256SUMS.txt`.

It is covered by **corrections register item D22**, which sources it by that exact path and
carries a substantive verdict:

> **the run set applies NO cross-slope. It is a longitudinal grade study, and it says nothing
> about camber.** A cross-slope is a lateral tilt, and no lateral tilt was ever applied. The
> register adds: do not cite this run set as a camber, cross-slope, or superelevation result
> under any circumstances.

So the directory is **misnamed**, and the register already says so. The individual run files
`STILL_S000` and `S000_rep0` are not named anywhere in the repo `[READ]`, but the run set as a
whole is triaged. **Nothing further is owed here.**

**DONE.**

---

## Step five, Undermind

**The wiring test in the prompt gives the wrong answer.** `grep -i undermind .mcp.json` returns
nothing; `.mcp.json` declares only deepwiki, scite, wolfram, canford-corpus, canford-tacc and
wandb `[READ]`. **Undermind is nonetheless live as a claude.ai connector**, so I ran the query
rather than stopping on a technicality.

Used `search_papers` against workspace "Can it ford"
(`17299f2a-8dc8-438b-8c84-5abf19395e2c`, 27 deep searches) rather than `launch_deep_search`,
which takes 2 to 5 minutes. Saved to
**`docs/undermind/2026-08-25_force-overprediction-mechanisms.md`**, with the query verbatim.

**Four candidate mechanisms, none of them in this project's corpus**, verified by DOI lookup
against `data/research_corpus_index.json` `[READ]`:

| cite key | DOI | bearing | PDF |
|---|---|---|---|
| `Gis19b` | `10.1145/3284980` | Interlinked SPH Pressure Solvers for Strong Fluid-Rigid Coupling. Addresses the "no pressure field" half directly. | no |
| `Ben23` | `10.2312/vmv.20231244` | Consistent SPH Rigid-Fluid Coupling. Argues prior coupling is inconsistent and quantifies it. | **yes** |
| `Raz23` | `10.1145/3606924` | Momentum-conserving hybrid particle/grid contact iteration. | no |
| `Jia16` | `10.1016/j.jcp.2017.02.050` | APIC, the canonical treatment of information lost in PIC velocity projection. 112 citations. | **yes** |

Three further hits are **already in the corpus** and serve as a check that the search reached
the right literature, not as new finds: `Wal07` `10.3970/cmes.2007.019.223`, `Zha22d`
`10.1002/nme.7347`, `Yun21` `10.1145/3476576.3476674`, plus `Bau23` `10.1002/nme.7217` `[READ]`.

**The most useful single result:** `Wal07` is the Wallstedt and Guilkey paper whose two claims
`ac0f0d8` withdrew as misattributed, and **a PDF is available in the workspace**. Those claims
could now be checked against the source instead of remaining withdrawn-and-unverified.

**What this establishes and what it does not.** It does not answer the mechanism question:
metadata only, nothing read, nothing verified against a primary source. **What it does
establish is that the surviving hypothesis has a literature.** After the flat PPC slope
eliminated locking, velocity-projection bias is the remaining candidate, and `Jia16` and
`Gis19b` are its two standard treatments. Both have been outside this corpus the whole time.

**DONE.**

---

## What was written

| file | change |
|---|---|
| `docs/CORPUS_LINEAGE_STATUS_2026-08-23.md` | appended correction block, 316 to 357 lines, sections 2-4 untouched |
| `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` | 5.2 conclusion added, 691 to 703 lines |
| `docs/undermind/2026-08-25_force-overprediction-mechanisms.md` | new, 69 lines |
| `docs/CORPUS_FOLLOWUP_REPORT_2026-08-25.md` | this file |

No `.tex` file was touched. Nothing staged, committed or pushed. No em-dashes.

## Standing caveat

**Nothing in this report was checked by the physics-skeptic path.** Three sessions were live in
this repo throughout, so any state here can have moved since it was measured. Re-run rather
than cite.

---

## Status appended 2026-08-26, consolidation session

Written by the session that produced `docs/CORPUS_INVENTORY_2026-08-25.md`. Nothing here was
committed or pushed; the working tree is left staged-and-clean for Josie to review.

**The premise that sent me looking was not confirmed.** The task was framed around the last two
sessions undercounting their own working-tree footprint by 6 to 8 files. **This pass did not.**
All six banner edits are `+7 / -0`, byte-identical, mtimes inside one second, with zero
deletions anywhere in the corpus set `[READ]`. The consolidation session recorded its own
footprint in the master's section 8 and stopped short of two edits it judged unsafe. That is a
clean handoff.

**What was actually wrong was smaller and more specific.**

1. **The master contradicted itself.** Section 8 said `research_index.py` "still has no
   `fulltext_path` field"; section 6.14 said it does. Live measurement agrees with 6.14, so
   section 8 was stale, written before a third pass in the same session wired the full text.
   **Corrected in place**, tagged and dated, nothing deleted.
2. **CLAUDE.md's ranking block was false in both halves**, and three consecutive sessions had
   deferred the fix because the file was dirty. **Applied on Josie's explicit go-ahead**, after
   confirming the unrelated `+41 / -17` does not touch the ranking block (0 overlapping hits)
   and was 21 hours stale rather than a live edit `[READ]`. The three report counts were
   re-derived live before being written into the constitution, not carried from the draft:
   `10.1016/j.cma.2022.114809` 7, `10.1016/j.jcp.2016.10.064` 7,
   `10.1007/s00466-019-01783-3` 4 `[READ]`.
3. **Two near-identically-named merge reports had no cross-reference.** They share 9 unique
   non-blank lines out of 278 and 167, 6 of which are the banner, and their headings are
   disjoint `[READ]`. Reciprocal scope pointers added to both.
4. **Four corpus documents were untracked**, including this one and
   `CORPUS_LINEAGE_STATUS_2026-08-23.md`. Staged, not committed.

**What is still open, and must not be read as done.**

- **`--source-audit` still exits 1 with 17 problems.** 17 searches reach the corpus as metadata
  only, representing **1244 papers as an integer and nothing more** `[READ]`. The reader is not
  complete and no document should say otherwise. Route proven, two traps: address a search by
  `name` not `slug`, and paginate past 50.
- **The corrections register still does not name the master.** 0 hits against 2 for
  `CORPUS_MERGE_FINAL`, register clean and unedited `[READ]`. This is the one half of the
  master's held-for-Josie item 2 that remains unwritten.
- **Nothing here has been adversarially reviewed.** The physics-skeptic path was not invoked.
- **Nothing is committed.** Staged files sit in a shared index while other sessions are live, so
  a plain `git commit` from another session would sweep them. Commit soon or unstage.
