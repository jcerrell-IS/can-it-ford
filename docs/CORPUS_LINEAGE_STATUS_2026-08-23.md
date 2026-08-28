> **ABSORBED 2026-08-25 into `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, the single
> corpus master.** This file is kept verbatim below and nothing in it was deleted or
> rewritten. Cite it only with its date, never as current: several of its counts (the
> 332-record index, the 27-metadata / 8-papers split, the open-item list) were measured
> before the 2026-08-25 ingest fix and are stale. The master carries the live figures and
> the current status of every open item.

---

# Corpus lineage status, 2026-08-23

Scope: four questions only, read-only session. Nothing was merged, staged, committed or
pushed. Every claim is tagged `[READ]` (direct command output or file content this
session), `[RECALLED]` (carried in from the session brief, not re-derived), or
`[INFERRED]` (reasoning over read facts).

Main checkout `/Users/josie/can-it-ford`, branch `claude/add-ci-checks`, HEAD `3fbb81e`
`[READ]`.

---

## 1. What the corpus-bib conflict actually is

**It is a live three-file git merge conflict between `claude/add-ci-checks` and
`claude/r9-corpus-bib`. It does NOT involve a `.bib` file.** `[READ]`

`git merge-tree --write-tree --name-only origin/claude/add-ci-checks
origin/claude/r9-corpus-bib` run live this session names exactly three files `[READ]`:

| file | conflict type |
|---|---|
| `.claude/skills/research-corpus/SKILL.md` | content |
| `analysis/research_index.py` | content |
| `data/deep_searches/vehicle-mesh-assets.json` | add/add |

No `.bib`, no `.tex`, no `docs/` file is in the conflict set `[READ]`. The branch name
refers to its SUBJECT, the shipped 15-entry bibliography measured against the corpus, not
to a bibliography file being merged `[INFERRED]`. This is worth stating because the name
invites the opposite reading.

**The branch is `claude/r9-corpus-bib`, tip `de18180`, and it IS pushed.** `[READ]`
`origin/claude/r9-corpus-bib` exists.

**It has NOT been resolved anywhere reachable from `origin/claude/add-ci-checks`.**
`git branch -a --contains de18180` returns only `claude/r9-corpus-bib` and
`origin/claude/r9-corpus-bib` `[READ]`. The live merge-tree above still reports the same
three conflicts today `[READ]`.

**The non-resolution is deliberate and post-dates `e9e80ad`.** `git log --all --grep`
returns one later commit, `c7db789` (2026-08-23), whose message states: "r9-corpus-bib is
pushed and unmerged by a documented decision, not an oversight." `[READ]` `e9e80ad` is
also the last commit to touch `docs/CORPUS_MERGE_FINAL_2026-08-22.md` at all `[READ]`.

Why `e9e80ad` called it substantive rather than mechanical, three reasons from its own
section 7 `[READ]`:

1. `--source-audit` is declared on BOTH sides with different predicates, ours exiting FAIL
   with 13 problems and the branch's naming 11. A union raises `argparse.ArgumentError` on
   the duplicate flag, so one side must be chosen and one of the two documents describing
   it then becomes false.
2. Neither side is a superset. `--searches` exists only on `add-ci-checks`; `--bib-audit`,
   `--coverage`, `--identifier-audit`, `--ingest-check`, `--against-slug` and `--out` exist
   only on the branch.
3. The branch's own Part 5 landing plan is stale: it predicts a conflict in `SKILL.md`
   "AND ONLY THERE" and asserts `research_index.py` is untouched. Both are false live.

**Effect on the 138-DOI accounting: none, measured.** `R9_CORPUS_BIB_GAP_2026-08-18.md` is
a clean add carrying zero occurrences of "138" and zero of "G25", so its content was read
without merging `[READ, quoting e9e80ad]`.

**OPEN.** The conflict is diagnosed and unresolved by a recorded decision; three named
questions in section 7.5 still require Josie, chief among them which `--source-audit`
survives.

---

## 2. Reachability of the three R9_CORPUS_READ commits, and whether its findings were folded in

**Reachability: all three are on `origin/claude/add-ci-checks`.** `[READ]`

| commit | date | subject | on `origin/claude/add-ci-checks` |
|---|---|---|---|
| `dd44e2f` | 2026-08-19 | Six papers read from full text, and one of them predicts Job B's number, sign and refinement behaviour | YES |
| `754af7f` | 2026-08-19 | The solver has no locking mitigation at all, and its fluid update is the exact line F-bar replaces | YES |
| `ac0f0d8` | 2026-08-19 | I relayed a subagent's reasoning as the paper's finding, one hour after writing up that exact failure | YES |

`dd44e2f` and `754af7f` are additionally on `origin/claude/r9-gapscan` and
`origin/claude/r9-overleaf`; `ac0f0d8` on `origin/claude/r9-overleaf` `[READ]`. So the six
commits confirmed in the brief plus these three make nine, all reachable `[INFERRED]`.

**Folding: the solver-locking / F-bar finding and the Job B prediction have NOT been folded
into any of the other three files.** `[READ]`

`/usr/bin/grep -i -E 'F-bar|Fbar|locking'` counts, with every hit inspected rather than
counted blind:

| file | raw hits | real topical hits |
|---|---|---|
| `docs/R9_CORPUS_READ_2026-08-19.md` | 14 | 14 (the source) |
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` | 1 | 0, substring inside "blocking defects" |
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-21.md` | 1 | 0, substring inside "blocking defects" |
| `docs/CORPUS_MERGE_FINAL_2026-08-22.md` | 2 | 1, and it is an appendix ROW only |
| `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` | 0 | 0 |

The one real hit is `CORPUS_MERGE_FINAL_2026-08-22.md:808`, appendix row 69,
`10.1016/j.cma.2018.01.010` "Overcoming volumetric locking in material point methods",
status `INDEX`, meaning catalogued and reaching neither prose nor bibliography `[READ]`.
That is a related DOI listed as uncited, not the finding.

A search for the two source papers behind the finding returns zero real hits in all four
other files: `2209.02466` / Choo (Zhao, Jiang and Choo, CMAME 2023) and Wallstedt and
Guilkey 2007 are absent. The single apparent `Choo` hit in `CORPUS_MERGE_FINAL` line 617
is the substring inside the word "choosing" `[READ]`.

**Job B: also not folded in.** A grep for `job b|jobb|918043` returns nothing in the 08-20
file, nothing in the 08-21 file, nothing in `..._FINAL.md`, and in `CORPUS_MERGE_FINAL`
only lines 160 to 161, which are about a DIFFERENT document
(`docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md`) moving a citation from `MANIFEST` to `PROSE`
status `[READ]`. That is bookkeeping about reach, not the prediction.

The prediction itself, live in `R9_CORPUS_READ_2026-08-19.md` lines 12 to 44 `[READ]`:
explicit MPM volumetric locking systematically over-predicts force transmitted to a rigid
body (strip footing, analytic 5.14 against roughly 7.5 to 8.0, so 45 to 55 percent over),
is NOT fixed by refinement, and its remedy is F-bar. Job B measures +34 to +64 percent, does
not improve with refinement, same sign and overlapping magnitude. The file labels this
"NOT A DIAGNOSIS YET" and names a PPC sweep as the discriminator, because locking predicts
error RISING with PPC while velocity-projection bias predicts FLAT.

Section 8 of the same file separately records, from a live read of the pinned solver, that
there is no F-bar, no J-averaging, no pressure smoothing and no locking mitigation of any
kind in the vendored tree `[READ, as that file's own claim]`. This session did not re-run
that solver search, so it is relayed rather than re-derived `[RECALLED]`.

**OPEN.** Reachability is settled and needs no re-check; the locking/F-bar finding and the
Job B prediction reach none of the other three files, so a terminal merge must pull them in
deliberately rather than assume the 08-22 lineage already carries them.

---

## 3. What `ac0f0d8` corrected

**`ac0f0d8` is itself the correction commit, not the error.** `[READ]` Its subject is "I
relayed a subagent's reasoning as the paper's finding, one hour after writing up that exact
failure". It withdraws two claims from section 2 of `R9_CORPUS_READ_2026-08-19.md`, both
attributed to Wallstedt and Guilkey 2007 ("Wal07"), both caught by session d21-jobb reading
the PDF directly instead of accepting the relay (commit `d826c8a` on
`claude/r9-jobb-route`) `[READ]`.

**What was misattributed:**

- **(a)** "For a body held fixed the projection error becomes a CONSTANT SYSTEMATIC BIAS
  rather than noise." **Not in the paper.** The paper says accuracy "is strongly dependent
  on particle density and location", and its section 2 carries the opposite emphasis, that
  particles "move into a less favorable configuration" as a simulation evolves. The sentence
  came from a PDF-reading subagent's own "Application to a Fixed Rigid Body" reasoning
  section, which is the subagent's analysis and not the paper's text `[READ]`. It would not
  have applied here in any case: the body is fixed, the WATER particles are not.
- **(b)** The plateau's "O(h)" scaling is **not a stated result**. The plateau is real and
  was quoted correctly; the scaling was read off Figure 10 by eye, while the paper's own
  analytic reference, Vshivkov 1996, has an `h^2` grid term. Say GRID-SET, never O(h)
  `[READ]`.

**Did it reach a committed document? YES.** The uncorrected text shipped in
`docs/R9_CORPUS_READ_2026-08-19.md:54` at both `dd44e2f` and `754af7f`, verified by
`git grep` at each of those two SHAs `[READ]`. The commit message also records it was
relayed onward "to two sessions and to a board the user reads" `[READ]`.

**Does it need correcting anywhere still live? NO in any tracked document.** A `git grep`
of the tracked tree for both withdrawn phrasings returns hits only in files that are
themselves recording the withdrawal `[READ]`:

- `docs/R9_CORPUS_READ_2026-08-19.md:51-66`, the withdrawal block, live in the file today
- `docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md:976, :985-993, :1389`
- `docs/R9_PROPAGATION_MEASUREMENT_2026-08-19.md:150, :154-156, :238-239`
- `docs/R9_PROVENANCE_AUDIT_2026-08-19.md:85-87`, verdict "CONTRADICTED, corrected at the
  root, carrier file updated rather than only the chat"
- `docs/R9_SESSION_HANDOFF_2026-08-20.md:491-492, :1510-1512`
- `docs/CANDIDATE_PAPER_SCOPE_TEST.md:20-21, :76`

One untracked file carries the claim in its ORIGINAL uncorrected form:
`.claude/state/r8_send_log.md:13723` `[READ]`. It is an append-only archive of dispatch
text as sent on 2026-08-19, it is untracked (`git ls-files --error-unmatch` errors on it),
and rewriting a send-log would falsify the record of what was actually sent `[READ +
INFERRED]`. The five `.claude/state/r8_digests/*.md` files and `r8_board.md:324` carry the
d21-jobb row, which states the withdrawal correctly `[READ]`.

**What replaced the withdrawn claims is stronger**, because it is measured on this
project's own solver rather than argued by analogy: d21 read the accessor from source,
`core/solver.py` "force = sum m*(v_free - v_new) / dt", so both inputs are outputs of the
mass-weighted P2G projection and the force is NOT a pressure integral over the wetted
surface; their PPC sweep at fixed grid over 3.375 to 64 particles per cell gives k_fit
0.687, 0.726, 0.727, 0.829 and a log-log slope of +0.0596, where PPC^-2 would predict a
98.4 percent fall `[READ, from the commit message, not re-derived here]`.

**DONE.** The misattribution is withdrawn at its root file and recorded in six tracked
documents; the only surviving uncorrected copy is an untracked historical send-log that
should stay verbatim.

---

## 4. The two Phase 1 checks

**Both files exist.** `[READ]`

```
-rw-r--r--  1 josie  staff  29128 Aug 22 14:43  docs/CLAUDE_MD_OPEN_ITEMS_STATUS_2026-08-22.md
-rw-r--r--  1 josie  staff  23149 Aug 22 14:28  docs/PRIOR_DISPATCH_VERIFICATION_2026-08-22.md
```

**The unpushed-branch sweep returns 24 local branches with no `origin/` counterpart**
`[READ]`:

```
claude/amazing-kowalevski-9df04d          claude/ieee-paper-citations-thresholds-2cc8e8
claude/analysis-failure-modes-83d6e2      claude/paper-data-audit-dd9118
claude/audit-gaps-lit-queue-768cda        claude/phillips-hall-redesign-c902c6
claude/audit-git-root-sources-65e03e      claude/render-realism-vehicle-water-f9127a
claude/can-it-ford-audit-5cb6df           claude/slide-resolution-dependence-reconcile-a5bf74
claude/concurrent-session-safety-570b39   claude/warpmpm-flood-vehicle-investigation-1b62fa
claude/console-setup-optimization-4eb410  claude/wizardly-pike-17658c
claude/credential-exposure-2026-08-13-DO-NOT-PUSH   correction/pass
claude/eloquent-easley-3ca1ff             task-r7-merge
claude/git-worktree-topology-cf6cda       task-readme-fix
claude/honest-results-figure-f2be3f       worktree-ctx-census
claude/ieee-citation-corrections-e22c26   claude/ieee-conference-final-pass-f025d8
```

**No branch matching "corpus-bib" is in that list, so it does NOT explain item 1.**
`[READ]` `git branch -a` returns `claude/r9-corpus-bib` AND `origin/claude/r9-corpus-bib`,
so the branch is pushed. The item 1 conflict is a genuine content disagreement between two
pushed branches, not a visibility artifact of an unpushed branch `[INFERRED]`.

Two of the 24 are relevant to sections 1 and 2 above: `task-r7-merge` and `task-readme-fix`
both contain all three R9_CORPUS_READ commits `[READ]`, so they are unpushed branches
carrying already-pushed history rather than unpushed findings.

`claude/credential-exposure-2026-08-13-DO-NOT-PUSH` is unpushed by design and its name says
so `[READ]`. The other 23 were not investigated; that was outside this session's scope.

**DONE.** Both files are present, the unpushed list is enumerated, and the corpus-bib branch
is confirmed absent from it.

---

## Standing caveat

No claim in this document was checked by the physics-skeptic path or by any adversarial
reviewer. Per the CLAUDE.md rule that a dated infrastructure claim must not age into a
fact, that path was not probed this session either, so its availability is unknown rather
than assumed dead `[INFERRED]`.

---

## Re-verification, 2026-08-24

This document was re-dispatched as if unwritten. It already existed (13,344 bytes, 241
lines, mtime 2026-08-23 02:53), so rather than overwrite it, every load-bearing claim in
sections 1 to 4 was re-measured live and this block records the outcome. **Nothing was
rewritten. No claim above changed.** Tree state unchanged: HEAD still `3fbb81e` on
`claude/add-ci-checks`, 1 unpushed `[READ]`.

**Section 1, re-measured `[READ]`.** `git merge-tree --write-tree
origin/claude/add-ci-checks origin/claude/r9-corpus-bib` still exits 1 and still names the
same three files with the same conflict types. The add/add blobs re-hash to exactly the
values `e9e80ad` recorded on 2026-08-22: `3e192cb7e9706a555bfc66cf7365c256` at 3,020 bytes
against `1d1567868e887cd1225de0b281402cc3` at 12,085. `git merge-base --is-ancestor
de18180 origin/claude/add-ci-checks` returns false, and `git log
e9e80ad..origin/claude/add-ci-checks` restricted to the three conflicting paths returns
**empty**, so neither side has moved on those files in two days. `e9e80ad` is confirmed the
last commit to touch `docs/CORPUS_MERGE_FINAL_2026-08-22.md` at all. Still **OPEN**, and
now with a measured statement that it is stable rather than merely unresolved.

**Section 2, re-measured `[READ]`.** All three commits still return
`origin/claude/add-ci-checks` under `git branch -a --contains`. The folding grep was rerun
with a word-boundary form, `(^|[^b])locking`, to separate genuine hits from the substring
inside "blocking": 08-20 gives 0, 08-21 gives 0, `..._FINAL.md` gives 0, and
`CORPUS_MERGE_FINAL_2026-08-22.md` gives exactly 1, appendix row 69. `F-bar` in any spelling
is 0 in all four and 4 in `R9_CORPUS_READ_2026-08-19.md`. Still **OPEN**, unchanged.

**One thing worth adding to section 2, and it is not a correction.** The PPC sweep that
section 1 of `R9_CORPUS_READ` pre-registers as the discriminator **was run, and it came out
against locking.** `ac0f0d8`'s own message records job 923239 sweeping 3.375 to 64 particles
per cell at fixed grid, giving a log-log slope of `+0.0596` where `PPC^-2` would demand
`-2`. Flat, which is the velocity-projection signature, not the rising signature locking
predicts `[READ, from the commit message]`. So the Job B locking hypothesis is not merely
unfolded, it has a recorded negative result sitting in a different commit from the document
that raised it. Anyone folding section 1 forward must carry that result with it, or they
will re-import a hypothesis its own discriminator already answered.

**Section 3, re-measured `[READ]`.** The uncorrected phrase ships at both `dd44e2f` and
`754af7f`, one occurrence each, confirmed by `git grep -c` at those SHAs. A whole-tree
`/usr/bin/grep -rniE "constant systematic bias"` across md, py, tsv, txt, tex and json,
excluding `third_party/`, `.claude/worktrees/` and `.git/`, returns 14 hits: 13 are files
recording the withdrawal, and the single uncorrected survivor is
`.claude/state/r8_send_log.md:13723`, untracked and append-only, exactly as section 3
states. Still **DONE**, unchanged.

**A tooling note that nearly produced a false negative here, worth keeping.** The first
run of that whole-tree grep was written with unquoted `--include=*.md`. zsh tried to
glob-expand the pattern, failed with `no matches found`, and the command returned **zero
hits**, which would have read as "the withdrawn claim survives nowhere" when in fact the
search never ran. Quote every `--include` pattern. This is the same class as the H0 rule in
CLAUDE.md: a search that did not execute is not evidence of absence.

**Section 4, re-measured `[READ]`.** Both files still present at the same sizes and mtimes.
The unpushed sweep still returns 24 branches and still contains no `corpus-bib` entry;
`claude/r9-corpus-bib` and `origin/claude/r9-corpus-bib` both resolve to `de18180`, the same
SHA on both sides, which is precisely why it cannot appear in an unpushed list. Still
**DONE**, unchanged.

**Net result: zero corrections to sections 1 through 4.** The 2026-08-23 pass holds in full
on re-measurement. The only additions are the stability measurement in section 1, the
negative PPC result flagged for section 2, and the zsh glob trap above.

No claim in this block was checked by the physics-skeptic path either, so the standing
caveat above applies unchanged.

---

## Correction, 2026-08-25: section 1's OPEN verdict is FALSE and is withdrawn

**Appended, not overwritten. Sections 2, 3 and 4 are untouched and still stand.**

**`claude/r9-corpus-bib` IS MERGED.** `git merge-base --is-ancestor de18180 HEAD` returns
true against HEAD `9f18fc2` `[READ]`. It was merged on **2026-08-24 17:56:42** by
**`a83a38b`**.

**Every OPEN verdict about the conflict in this file is therefore stale**, specifically the
":44" claim that it "has NOT been resolved anywhere reachable from
`origin/claude/add-ci-checks`", the section 1 closing **OPEN**, and the 2026-08-24
re-verification block's "still exits 1 and still names the same three files". All three were
true when written and are false now. They are left in place as the record of what was
believed, per this project's practice of dating a correction rather than deleting the
original.

**WHY NOBODY NOTICED, and this is the part worth keeping.** `a83a38b`'s message is "Record
poster and paper submission status per direct human confirmation" and it never mentions the
corpus. Measured `[READ]`: the commit carries **4,548 insertions across 7 files**, and only
`docs/SUBMISSION_STATUS.md`, at **+4 lines**, matches its own subject. The other six files,
about 4,544 lines, are the corpus-bib merge: `.claude/skills/research-corpus/SKILL.md`,
`analysis/research_index.py`, two `data/deep_searches/*.json`, `data/r9_bib_corpus_census.tsv`
and `docs/R9_CORPUS_BIB_GAP_2026-08-18.md`. **A merge landed inside a commit named for
unrelated work, so no document learned of it and three assertions stayed false for a day.**

**THIS FILE WAS THE ONE DOCUMENT THE CORRECTING SESSION NAMED AS SKIPPED.** `c82adb7`
(2026-08-25 02:23) corrected the same false assertion in
`docs/CORPUS_MERGE_FINAL_2026-08-22.md` and in
`docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` at `:57` and `:265` `[READ]`. It did not
correct this file. That omission is why the stale OPEN survived a further day, and it is the
reason this block exists.

**The flag collision that section 1 called the blocking question was resolved by RENAME, not
by choosing a winner** `[RECALLED, from `c82adb7`'s message, not re-derived here]`. The
branch's reachability report became `--ingest-audit`; `--source-audit` kept its name for the
CI gate that CLAUDE.md and the corrections register cite, so no external citation broke.

**Section 1 status: CLOSED.** Sections 2, 3 and 4 unchanged.
