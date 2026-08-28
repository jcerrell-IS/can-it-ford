# Finalization prompt II: what the first pass missed, 2026-08-26

Successor to `docs/FINALIZATION_PROMPT_2026-08-25.md`. That prompt is still valid; this one
supersedes its Phase 1 (done) and adds what a second audit plus a read of the project's own
research-reader corpus turned up. Paste the fenced block into a fresh Claude Code session.

---

```
Continue finalizing Can It Ford for public presentation to employers and graduate admissions.
A previous session produced docs/FINALIZATION_PROMPT_2026-08-25.md; read it, because Phases 2
through 8 there are still live. This prompt records what changed since, and adds gaps that
audit missed.

## STANDING RULES

Same as the prior prompt, and they matter more now because up to 4 sessions run concurrently:
verify live and tag claims [CONFIRMED]/[DOC]/[INFERRED]; the shell `grep` is ugrep and skips
gitignored paths, so use /usr/bin/grep or git grep; never `cd`; never `git add -A`; re-check
`git status` immediately before every commit; confirm before any push, delete or overwrite;
no em-dashes anywhere. Read CLAUDE.md and docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
before asserting any physics number.

## STATE CHANGE SINCE THE FIRST PROMPT, verify each before relying on it

- **PR #16 MERGED.** Commit 30218a8 is on origin/main. The three false statements (dead demo,
  ODC-By-1.0 licence, "no NHTSA-measured Yaris") are GONE from the public default branch.
  Phase 1 of the prior prompt is COMPLETE. Do not redo it.
- **PR #17 is OPEN**, "Meet the CCSA acknowledgement, and give the repo a ...". Another session
  is already executing Phase 2. Coordinate, do not duplicate.
- **PR #15 still open** (Zotero bib refresh). PR #9 no longer appears in the top 5; check
  whether it was closed or merged.
- origin/main is now 2 ahead / 474 behind the working branch. The divergence is still the
  headline structural problem.

---

## PRIORITY 1: the Weights and Biases project is PRIVATE and the README links to it

**This is the most damaging single defect currently on the public repo, and the first pass
missed it entirely because it only ever queried runs while authenticated.**

Measured live 2026-08-26 [CONFIRMED]:
- Authenticated GraphQL: `project.access` = **PRIVATE**.
- Anonymous GraphQL for the same project returns **`{"data":{"project":null}}`**.
- `README.md` line 6 carries a W&B badge linking to
  `https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford`.

So a badge on the first screen of a public repository resolves to nothing for every visitor
who is not Josie. Note the trap: the URL returns **HTTP 200**, because W&B serves a single-page
app shell, so a naive link checker reports it healthy. The anonymous API null is the decisive
evidence. Use that method for any other gated service.

Tasks:
a. Confirm the above independently before acting.
b. Ask Josie whether to make the project public. If yes, make it public and re-verify
   anonymously. If no, REMOVE the badge, because a badge to a private resource is worse than
   no badge.
c. The project `description` field is **empty**, exactly the gap that GitHub had. Set it to
   match the GitHub description so the surfaces agree.
d. **Run-count discrepancy, unresolved: `project.totalRuns` returns 174 while
   `project.runs.totalCount` returns 108, from the same API in the same session.** Do not
   publish either number until you know what each counts. The 108 decomposes cleanly into four
   tagged cohorts (70 L0/L1, 9 Genesis pilot, 17 gated warpmpm, 9 untagged, 3 admin); the
   remaining 66 are unaccounted for and may be deleted or cross-project runs.
e. `views` is non-empty, so at least one report or view object exists. Find out whether any
   published W&B report exists. If none, a single well-made report over the 17 gated runs is
   one of the highest-value-per-hour artifacts available, and the connector can create it.

## PRIORITY 2: nothing in the repo records what was actually submitted

From the project's own terminal research reader, `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`
section 6.10, and independently worth re-verifying:

`docs/SUBMISSION_STATUS.md` is 8 lines and **both status lines are blank**. Verified with
`cat -e`: the poster line and the paper line each end `: $`. There is no YES, no NO, no venue.
Three commits touched it; the last, named "Fill in actual poster and paper submission status",
**deleted the `[YES/NO]` placeholders and put nothing in their place**, so a visible unanswered
question became a blank that reads as answered.

**Nothing in this repository records whether the poster was uploaded or the paper submitted.**

That is unacceptable for a job-application artifact: Josie cannot describe her own summer
output precisely. Ask her directly, record the answer in the file with a date and a venue, and
make it the single source other surfaces cite. Also resolve which poster PDF was submitted:
`deliverables/poster/Cerrell_TACC_42x56.pdf` (6,102,270 bytes, MD5
89240d2336bccbfceb8bf8b4f135279e) sits beside a `.pptx` and a `...dup.pdf`.

## PRIORITY 3: acquisition is already done for 31 papers and they are not in the index

Reader section 6.16, all measured 2026-08-25. Re-verify, then act, because this is the
cheapest research win available: **the PDFs are already on this computer.**

- **31 papers have full text on disk and are absent from the index.** Of 107 full-text files,
  50 yield a DOI, 19 are in the corpus, **31 are not.** Among them
  `10.1051/matecconf/201820307003` (**shah2018, which the paper already cites**), three Ceccato
  papers on MPM soil-fluid coupling, and `10.1016/j.cma.2020.113119` (**Negrut**, whose group's
  work is the literature-backed alternative coupling architecture named in CLAUDE.md item A-1).
  Ingest them, then re-run `analysis/research_index.py --stats` and `--source-audit`.

- **Five Perplexity reports have no ingest route at all.** The builder reads 8 hardcoded
  markdown REPORTS plus `data/deep_searches/` JSON; there is no Perplexity path. Two reach no
  document by any route: `physgaussian-bridge-findings` and `citation-verification-report`.
  **Read `drift-threshold-citation-research` FIRST**: it is a citation hunt for the unsourced
  0.05 DRIFT_THRESHOLD, which is open GitHub issue #5, and it cites
  `10.1080/00221686.2011.616318`, the Xia 2011 incipient-velocity paper this project has
  repeatedly failed to retrieve. **Closing issue #5 may already be done and merely unread.**

- **17 of 28 deep searches reach the corpus as metadata only**, representing 1244 papers as an
  integer. `--source-audit` exits 1 with 17 problems. The recovery route is proven, two calls
  per search against the live Undermind workspace:
      inspect_deep_searches(workspace_id=..., names=[<the search NAME, not the slug>],
                            papers_only=True, detail_level='standard', limit=50)
      get_paper_info(workspace_id=..., cite_keys=[...], detail_level='compact', show_doi=True)
  Two documented traps: **address the search by `name`, not `slug`**, or you get "Search not
  found"; and **paginate**, because the tool pages at 50 and four searches exceed it
  (`free-body-load-transfer-expanded` 119, `free-body-load-transfer` 118,
  `load-transfer-portability` 114, `moving-vehicle-open-source` 105). A partly-paged export is
  unusable. This route recovers title, year, DOI and link but **not abstracts**, so records
  ingested this way must never be described as read.

- Two clean negatives, recorded so nobody re-opens them: the 283 `compass_artifact_*` files
  deduplicate to 38 ids of which 36 already reach the index, and a curated triage TSV already
  exists on the Desktop. Do not re-audit these.

## PRIORITY 4: every physics claim in the reader is UNREVIEWED

Reader section 6.9: no claim in the terminal reader has been checked by the physics-skeptic
path or any adversarial reviewer. That path was dead fleet-wide on 2026-08-19 and the outage
ended 2026-08-20, but availability is unknown rather than assumed either way. **Probe it once,
cheaply, then either run the review or record explicitly that the claims remain unreviewed.**
Do not let a dated infrastructure claim age into a fact, and do not fake the review.

## PRIORITY 5: the presentation surfaces, in the order a stranger meets them

The prior prompt's Phases 3, 5, 6, 7 cover most of this. Additions and sharpenings:

a. **Link-check every public surface with a method that survives SPAs.** The W&B case proves
   HTTP 200 is not evidence a link works. For each link in README, the paper, the Vercel site
   and all four Hugging Face cards, verify the destination anonymously and check the CONTENT,
   not just the status code.
b. **Hugging Face Space is SLEEPING.** Measure the cold-start latency yourself and then either
   say so beside the badge or fix it. Do not describe it as "live" if a visitor waits.
c. **Cut a tagged release.** Still 0 tags, 0 releases. Consider wiring Zenodo so the release
   mints a citable DOI, which also gives the paper something to cite for the software.
d. **`deliverables/` is 114 MB, 20+ documents, and zero files of it are on main.** It contains
   UNDERSTANDING_AND_DEFENDING_THIS_PROJECT.md, TALK_SCRIPT.md, EXPLAIN_IT_SIMPLY.md,
   WALKTHROUGH.md and ERRATA.md. **Read these before drafting any new explainer prose**; the
   employer-facing layer may already be written and merely unpublished.
e. **92 remote branches, 2 merged.** Inventory what each unmerged branch uniquely holds before
   proposing deletion. `find` cannot see them; use `git branch -r --contains` and `git ls-tree`.

## PRIORITY 6: routes nobody has tried

These are unexplored, not cleared. Report on each even if the report is "opened, nothing to do".

- **DesignSafe PRJ-6388** is "staged, awaiting co-PI sign-off" per the README and nobody has
  verified its state. A minted dataset DOI is apparently one approval away and would be the
  single strongest citable artifact this project could add.
- **arXiv.** No preprint exists as far as anyone has checked. Decide whether to post, noting
  the CCSA licensing question may bear on it.
- **ORCID, Google Scholar, Semantic Scholar.** No author identity links the paper, the datasets,
  the repo and the Space into one body of work. That linkage is what makes three surfaces read
  as one project rather than three hobbies.
- **A short demo video or GIF.** `figures/yaris_flood.gif` exists and appears on no public
  surface. A 20-second clip of water hitting the hull is the single most persuasive artifact
  this project owns and it is currently invisible.
- **The solver Poiseuille comparison.** `tests/test_physics_gates.py` prints "SKIPS ARE NOT
  PASSES" and names the one missing file, `tests/data/poiseuille_profile.csv`. This is the
  cheapest genuine validation result still available and it is one solver run away.
- **Secret scan across working tree AND history**, since the repo is public and project memory
  says the exposure grows on its own. A `github_pat_` leaked into a transcript on 2026-08-25
  and needs rotating regardless.
- **Correspondence connectors** (Gmail, Calendar, Otter, Drive) remain unopened and may hold
  deadlines, mentor decisions, and the CCSA or DesignSafe threads. **Ask before reading any.**

## HOW TO FINISH

Work priority order, not phase order. After each priority, report what changed, what you
verified live, and what you could not. If something is blocked, finish everything else and say
plainly what you left and why.

The goal is not a longer repository. It is that a stranger with 90 seconds sees one coherent
project across GitHub, Hugging Face, W&B and the paper, with no dead links, no false claims,
no empty descriptions, and a clearly stated boundary between what was built and what was
designed. The honesty about the unbuilt reconstruction front end is a strength; state it the
same way everywhere rather than hiding it on some surfaces and disclosing it on others.
```
