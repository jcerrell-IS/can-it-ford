> **ABSORBED 2026-08-25 into `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, the single
> corpus master.** This file is kept verbatim below and nothing in it was deleted or
> rewritten. Cite it only with its date, never as current: several of its counts (the
> 332-record index, the 27-metadata / 8-papers split, the open-item list) were measured
> before the 2026-08-25 ingest fix and are stale. The master carries the live figures and
> the current status of every open item.
>
> **NEAR-IDENTICAL NAME, DIFFERENT DOCUMENT.** `CORPUS_FINAL_MERGE_REPORT_2026-08-23.md`
> is a SEPARATE session report, not an earlier draft of this one: the two share 9 unique
> non-blank lines out of 167 and 278, and 6 of those 9 are this banner (measured 2026-08-26).
> THIS file is the landing-plan, flag-collision and terminal-merge session. THAT one is the
> corpus-lineage, bounded-sweep and proposed-bibliography session. Read both, or read neither
> and read the master instead.

---

# Corpus final merge report

**THE DISPATCH ASKED FOR THIS AT `docs/CORPUS_FINAL_MERGE_REPORT_2026-08-23.md`. THAT NAME
WAS ALREADY TAKEN** by a 346-line committed report from the 2026-08-23 dispatch (`c7db789`),
a different session answering different questions `[READ]`. I overwrote it before checking,
which was a mistake; it was restored byte-identical from the HEAD blob and verified clean,
and this report took the correct date instead. Nothing from the 08-23 report was lost. This
session ran 2026-08-25 02:08 to 02:20 BST `[READ, from `date`]`.

**HEADLINE: Phases 0.5 through 5 were already complete before this session started. The
merge landed 2026-08-24 17:56 and nothing recorded it, so three documents went on asserting
the opposite for a day. Correcting those three is the only write this session made to
existing files.**

Every claim is tagged `[READ]` (live command output this session), `[RECALLED]` (carried in
from the dispatch or a prior session, not re-derived) or `[INFERRED]`.

Main checkout `/Users/josie/can-it-ford`, branch `claude/add-ci-checks`, HEAD `a6467d3` at
session start `[READ]`.

---

## Three of the dispatch's "confirmed facts" were false on checking

Stated up front because two of them would have caused wasted or harmful work.

1. **"If r9-corpus-bib is local-only, back it up to origin. This is not optional, do it
   first."** It was never local-only. `claude/r9-corpus-bib` and
   `origin/claude/r9-corpus-bib` both resolve to `de18180`, the same SHA `[READ]`. No push
   was needed and none was made.
2. **"SKILL.md says 19 completed deep searches."** Already fixed. Live it reads "built when
   the workspace held twenty-one" and adds "It is now SHORT OF THE LIVE SET, which is 28"
   `[READ]`. The live number is 28, not 21, so the dispatch's replacement value was also
   stale.
3. **"It credits df52bee for adding tests/test_physics_gates.py."** Already fixed. Live it
   reads "added by `50b70c0`" and credits `df52bee` only for extending it `[READ]`. Both
   were corrected by `72cfbdb`, "Both skill numbers were stale, and the attribution was
   wrong on the verb as well as the SHA".

---

## Step Zero

`Josephines-MacBook-Air.local`, `/Users/josie/can-it-ford`, branch `claude/add-ci-checks`
`[READ]`. `claude/r9-corpus-bib` = `de18180`; `origin/claude/r9-corpus-bib` = `de18180`
`[READ]`.

**A concurrency hazard was found and it governs the rest of this report.**
`analysis/research_index.py`, one of the three files the dispatch asks to integrate, was
modified at `02:09` while the clock read `02:09:14` `[READ]`, so another session was writing
it within seconds of the check. Its uncommitted diff is +36/-2 and substantive: it fixes
`--build` aborting on `MANIFEST.json` and on metadata stubs. **This session did not read that
file as authority and did not write it at all.** Where the landed state mattered, the
committed blob was extracted with `git show HEAD:...` and tested in the scratchpad instead
`[READ]`.

**DONE.**

---

## Phase 0.5, backup before touching anything

Conditional on Step Zero finding the branch local-only. It did not.

**The branch had a remote backup before this session and still does.** `git ls-remote` and
`git rev-parse` agree on `de18180` for both `claude/r9-corpus-bib` and
`origin/claude/r9-corpus-bib` `[READ]`. `git log main..claude/r9-corpus-bib` was therefore
not the deciding measurement and no push was issued.

**DONE, as a no-op.** Explicitly: this branch was never at zero remote backup, so the
"not optional, do it first" instruction had nothing to act on.

---

## Phase 1, re-measure the landing plan

**The plan is not merely stale, it is obsolete: the merge already happened.**

`git merge-tree --write-tree claude/add-ci-checks claude/r9-corpus-bib` **exits 0** and names
no conflicting file `[READ]`. The merge base is `de18180`, which is r9-corpus-bib's own tip
`[READ]`. `git merge-base --is-ancestor de18180 claude/add-ci-checks` and the same against
`origin/claude/add-ci-checks` both return true `[READ]`.

The merge commit is **`a83a38b`, parents `72cfbdb` and `de18180`, 2026-08-24 17:56:42 +0100**
`[READ]`. All three files the dispatch lists as clean adds now exist on both sides `[READ]`.

**The single most useful finding in this report: `a83a38b`'s message is "Record poster and
paper submission status per direct human confirmation".** It says nothing about the corpus
merge `[READ]`. A merge landed inside a commit named for unrelated work, so no document
learned of it, and `CORPUS_MERGE_FINAL_2026-08-22.md` and
`MERGED_RESEARCH_READER_CORPUS_FINAL.md` kept asserting "NOT merged" for a full day
`[INFERRED, from the message text and the three stale assertions]`.

**DONE.**

---

## Phase 2, the two free fixes

**Both were already fixed, by `72cfbdb`, before this session.** See the three-false-facts
section above for the live text `[READ]`. No commit was made, because making one would have
meant re-editing correct text.

One thing the dispatch could not have known: the count has moved again. SKILL.md now says the
catalogue table is "SHORT OF THE LIVE SET, which is 28" and directs the reader to
`--ingest-audit` and `--source-audit` for the live split rather than trusting the table
`[READ]`. So the 19-versus-21 question is closed and superseded, not merely closed.

**DONE, by a prior session, verified live here.**

---

## Phase 3, resolve the flag collision

**Already resolved on 2026-08-24, by rename, exactly as decision 1 required.** The rename is
documented in the source itself at `analysis/research_index.py`, in a comment reading
"RENAMED FROM `--source-audit` ON 2026-08-24" `[READ]`.

The resolution matches the decision on every point:

- The branch's version took the new name **`--ingest-audit`**, chosen because it "has no
  external citers" and because it follows the branch's own `--<noun>-audit` convention and
  pairs with `--ingest-check` `[READ]`. The dispatch guessed `--source-audit-unreachable` and
  told me to check for an existing convention first; the existing convention won.
- **`--source-audit` kept its name for the CI gate**, which is the one CLAUDE.md and the
  corrections register already cite `[READ]`. That is the dispatch's instruction verbatim.
- Neither side was dropped.

**DONE, by a prior session, verified live here.**

---

## Phase 4, integrate

**Already done, and functionally verified this session rather than taken on trust.**

The committed blob was extracted to the scratchpad and executed, so the concurrent
working-tree edit could not contaminate the result `[READ]`:

- `python3 <HEAD blob> --help` **exits 0 with no `argparse.ArgumentError`**, which is the
  specific failure a naive union would have produced `[READ]`.
- All nine flags coexist: `--searches` (ours only), `--bib-audit`, `--coverage`,
  `--identifier-audit`, `--ingest-check`, `--against-slug`, `--out` (branch only),
  `--source-audit` (CI gate, name kept) and `--ingest-audit` (renamed) `[READ]`.

That is precisely the neither-side-supersets reconciliation the dispatch specified.

**On `vehicle-mesh-assets.json`: the add/add no longer exists, so the "do not default to the
larger file" instruction has nothing to decide.** The merge resolved it. I did not re-open a
settled resolution to re-adjudicate a file that is no longer in conflict `[INFERRED]`. If the
resolution needs auditing, that is a separate question from the one asked, and it should be
asked against `a83a38b` rather than against a conflict that no longer exists.

**DONE, by a prior session, verified live here.**

---

## Phase 5, land

**Already landed and already pushed.** `de18180` is an ancestor of
`origin/claude/add-ci-checks` `[READ]`. `main` was not touched and no `.tex` file was touched
`[READ]`.

No push was issued by this session. The two local commits ahead of origin at session start
(`6a371bd`, `a6467d3`) belong to another session and were left alone `[READ]`.

**DONE, by a prior session, verified live here.**

---

## Phase 6, the terminal merge

**`docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` already exists**, 18,460 bytes, committed by
`c7db789` on 2026-08-23 `[READ]`. Both dated readers already carry SUPERSEDED banners
pointing to it `[READ]`. So the "create it" instruction was already satisfied.

**What was genuinely outstanding, and what this session fixed.** Three assertions were
factually false as of the 2026-08-24 merge, and all three are now corrected in place, with
the original wording preserved and dated rather than deleted, per house style `[READ]`:

| file | what it claimed | fix |
|---|---|---|
| `CORPUS_MERGE_FINAL_2026-08-22.md` top banner | "DELIBERATELY NOT RESOLVED ... no merge was made" | dated RESOLVED block added above it, old text kept and marked historical |
| `MERGED_RESEARCH_READER_CORPUS_FINAL.md:57` | "`de18180` pushed, **NOT merged**, deliberately" | corrected to MERGED by `a83a38b`, old wording quoted |
| `MERGED_RESEARCH_READER_CORPUS_FINAL.md:265` | "still unmerged ... It needs a human" | corrected, and names which human decision was taken |

**ONE INSTRUCTION WAS DELIBERATELY NOT FOLLOWED, and this is the part to read.** The dispatch
asks to supersede `docs/CORPUS_MERGE_FINAL_2026-08-22.md` with a banner pointing to FINAL.
**That would reverse a decision recorded one day earlier in two places.** CLAUDE.md's
RESEARCH-CORPUS READER RANKING block, set 2026-08-23, states it "is a SEPARATE line and is
NOT superseded ... FINAL does not restate it" `[READ]`, and FINAL.md's own header states "It
does NOT supersede `docs/CORPUS_MERGE_FINAL_2026-08-22.md`" `[READ]`. The two documents
answer different questions: FINAL is the reader lineage, CORPUS_MERGE_FINAL is the 138-DOI
accounting. Banner-superseding it would make both of those statements false and would point
readers away from the only authority on the 138. **Not done, deliberately. If Josie wants it
superseded anyway, that is a decision to take explicitly, against CLAUDE.md, not as a side
effect of this dispatch.**

**The 138-DOI accounting stands unaffected by the conflict**, unchanged and re-affirmed
`[RECALLED, per the dispatch's own confirmed-facts block; not re-checked, as instructed]`.

**Two items remain and are named rather than quietly dropped:**

1. **CLAUDE.md was not edited.** It is dirty with another session's uncommitted work (+4/-2)
   `[READ]`, and the standing rule forbids two sessions touching one file without
   sequencing. It already names FINAL the terminal reader, so nothing is lost by waiting.
2. **The corrections register does not name FINAL authoritative.** A grep returns only
   `CORPUS_MERGE_FINAL` references, none for `MERGED_RESEARCH_READER_CORPUS_FINAL` `[READ]`.
   This is a real gap and it is left open rather than filled, because the register is the
   corrections authority and adding a row to it while three sessions are live is exactly the
   class of edit that produced the 2026-08-07 breach.

**BLOCKED on two named items: CLAUDE.md (concurrent session owns the file) and the register
row (deferred by concurrency policy). The corrections that were safe to make were made.**

---

## Standing caveat

No claim in this document was checked by the physics-skeptic path. Three sessions were live
in this repo throughout, so any state here can have moved since it was measured; re-run
rather than cite.
