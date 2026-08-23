# The Merged Research Reader Corpus

> **SUPERSEDED 2026-08-23 by `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`.** This file is the pass-1 record and is kept verbatim. It was already superseded by the 2026-08-21 pass 2, which names six specific pass-1 errors in its own section 1. Read FINAL first; read this only for the pass-1 history. Nothing here has been deleted or edited.

**Built 2026-08-20 by a concurrent second-eyes session.** This is the reader. The machine
bundle is `~/can-it-ford-workflow-archive/MERGED_READER_CORPUS.json`; the chronological
working log is `docs/SECOND_EYES_AUDIT_2026-08-20_1200.md`. This file is the one to read.

---

## 0. How to read any number in this file

Three rules, all of which this corpus violated at least once before they were adopted.

**Every number carries its method or it is not a number.** The same quantity measured two
defensible ways gives two answers, and both are correct. Worked examples from this corpus:

| quantity | answer A | answer B | why both are right |
|---|---|---|---|
| DOIs in the committed corpus | **273** | **540** | A counts the `doi` field of 332 records; B regexes the whole file, catching `link` fields and abstracts |
| DOIs on disk | **414** | **4,388** | A is 4 layers, per-record; B is 13 layers plus 88 project dirs, whole-file regex |
| agent results in the journals | **398** | **321** | A double-counts one run that exists as two partial copies (97 union keys, 74 shared) |
| workflow agent transcript files | **1,284** | **642** | A counts `.jsonl` + `.meta.json`; B counts `.jsonl` only. The 642 are **472 unique agents** (170 byte-identical duplicates) |
| deep-search papers | **780** | **1,206** | A sums `n_relevant_papers`; B sums total paper slots |
| DRIFT_THRESHOLD declaration sites | **22 / 23 / 24** | | two independent binary scope choices give four totals |

**A validation rate does not travel between populations.** Two random 40-DOI samples checked
against Crossref: the first population validates at **90 percent**, the second at **70
percent**. Carrying the first rate to the whole set would have over-counted by ~370. The
second population is worse because it is dominated by `_bbNNNN` reference anchors scraped from
**one** review article, `10.1016/bs.aams.2019.11.001`. **When a regex yield jumps, look for a
single document inflating it.**

**A zero from a tool you wrote is a claim about the tool first.** Every zero in this project's
history that turned out to be a predicate bug: a shell `grep` that skips gitignored paths; a
`--query` that was author-blind; a glob that missed a session-uuid level (0 where there were
2,818); a glob that missed `.meta.json` (642 where the table said 1,284); a paragraph splitter
fed a minified JSON (0 where there were 392); a regex matching mid-word (`REFERENCE.md` →
`ENCE.md`); a resolver trying only one root (2,217 "unresolved" of which 923 resolve).

**And the provenance warning that belongs on every use of this corpus:** of 3,291 atomic
findings, **3,265 have a single origin**. Under this project's own rule that one source cited
twice is not two sources, essentially nothing here is corroborated. Where two origins do exist,
this file says so explicitly.

---

## 1. The verified spine

Everything below was checked by me against a primary source or live state, not relayed.

### 1.1 A measured 2010 Yaris inertia tensor exists, and the solver already matches it

`10.13021/G8JS5D`, the CCSA/NCAC Yaris FE validation report, read directly from
`~/Downloads/2010-toyota-yaris-coarse-validation-v1.pdf` (5,035,861 bytes) with
`/opt/homebrew/bin/pdftotext -layout`. **Slide 7, "Inertia Comparisons":**

```
                         Actual Vehicle    FE Model
Weight, kg                    1078           1101
Pitch inertia, kg-m^2         1498           1545
Yaw inertia, kg-m^2           1647           1718
Roll inertia, kg-m^2           388            396
Vehicle CG X, mm              1022           1025
Vehicle CG Y, mm               -8.3           -3.0
Vehicle CG Z, mm               558            557
```

Mapping through the known axis transposition (the hull's long axis is Y, so measured
roll ↔ Iyy, pitch ↔ Ixx, yaw ↔ Izz):

| axis | measured | solver particle cloud | error | `vehicle_params` box | error |
|---|---|---|---|---|---|
| roll | 388 | **395.0** | **+1.8%** | 463.0 | +19.3% |
| pitch | 1498 | **1501.5** | **+0.2%** | 1893.0 | +26.4% |
| yaw | 1647 | **1685.4** | **+2.3%** | 1959.8 | +19.0% |

The measured vehicle is 1078 kg against the canonical 1100 kg, **+2.0 percent**, and inertia
scales roughly linearly with mass. **The residual is the mass difference.**

CG height: measured **0.558 m**; solver particle cloud 0.6312 m (**+13.1%**);
`vehicle_params` estimate 0.510 m (**−8.6%**); hull bbox mid-height 0.7427 m (+33.1%).

**This is the first external validation anchor the project has for its rigid-body
representation**, and it arrived from a PDF sitting in `~/Downloads`.

### 1.2 A floating-point verdict flip, already defended against

`0.1 * 3.0 = 0.30000000000000004`, which exceeds a 0.30 D×V cap. Across the depth-velocity
grid: **2 cells flip at the 0.30 cap, 0 at 0.45, 2 at 0.60** — four across the three AR&R class
caps, matching the claim in `deliverables/paper/overleaf/sections/results.tex:7`.

**The canonical path is already protected.** `vehicle_params.py:239` and
`renders/yaris_render_s1/gates.py:29` both read
`if round(depth_m * velocity_ms, 6) > lim["haz_m2s"]`. This is a real defence, in place, and
documented nowhere a reader would find it.

### 1.3 Vista and LS6, live

Vista `login2`, **591 SUs** expiring 2026-09-30; LS6 **9,536 SUs**, same expiry; queues empty
on both. Vista `/home1` at **89.52 percent** of 23.3 GB — independently corroborated by a
different session at the same figure, one of the only genuinely two-origin numbers here.

GPU model closed from primary source: a two-minute probe, Slurm job **924230**, node
**c611-021**: `NVIDIA GH200 120GB, 97871 MiB, driver 590.48.01, compute capability 9.0`. That
is a direct measurement of the `gh` partition **today** and an **inference** for the July runs.

**Vista `$WORK` is 14 commits ahead of `origin/main` and 174 behind**, with 4 modified tracked
files including `CLAUDE.md`. The 14 are a `realism_track` series carrying real physics with
retractions in their own messages, plus `868302e` committing `validate_coupling_force.py`,
"untracked since first use". **Fourteen commits of physics exist only on Vista.**

### 1.4 Citation integrity

All **11 DOIs asserted anywhere in `CLAUDE.md`** resolve at Crossref and match the asserted
first author and year. No fabricated citation. One resolved title matters:
`10.1115/1.4071177` is He et al. 2026, *Predicting Vehicle-Water Interaction in Shallow Water:
**Simulations and Experimental Validation***. The constitution's L-7 says this project's
novelty is the validation step; a 2026 paper doing vehicle-water interaction with experimental
validation is adverse to that framing, and `paper/` cites none of the four prior fording works.

---

## 2. Corrections owed to the constitution and the register

Each is measured. None is applied, because `CLAUDE.md` and the register are files other live
sessions are in.

**2.1 `CLAUDE.md` item 4 leg (a) is false.** It reads "No measured Yaris tensor exists
anywhere: SAE 1999-01-1336 ends Nov 1998." See §1.1. The **conclusion is unchanged and now
better supported**: do not wire `vehicle_params` inertia. Only the reason changes, from an
argument from absence to an argument from measurement.

**2.2 The same false claim sits in two more files.** `README.md:61` says "uniform-box fallback
(**no NHTSA-measured Yaris**)" and links `https://doi.org/10.13021/G8JS5D` **in the same table
cell** — the document that refutes it. `vehicle_params.py` note 3 carries it too. **Three files
carry the claim; one supplies its own refutation.**

**2.3 `CLAUDE.md` says `.claude/worktrees/` "holds 2 directories, not 27".** Measured:
`git worktree list` returns **33 worktrees**, 28 under `.claude/worktrees/`. The grep-exclusion
advice that depends on this is load-bearing again.

**2.4 `CLAUDE.md` and the `research-corpus` skill both say the index "now covers 21" deep
searches.** True of metadata, false of papers. See §3.

**2.5 A live challenge to `CLAUDE.md` item 3** sits in `simulation/fork_scene/runner.py:101`:
*"No engine patch is needed. CLAUDE.md item 3's word 'unconditionally' is wrong."* Item 3 says
`core/solver.py:167-169` hardcodes `g=[0,0,-9.81]` unconditionally. **Unresolved.**

**2.6 Register self-contradiction on `floor_friction = 0.55`.** Item 29 (2026-08-18) says it is
UNSOURCED and "nothing sources it"; G4a (2026-08-07) and the submitted paper both source it to
a spring-balance measurement in Azhar et al 2023. Two rows of the same authority, opposite
verdicts, eleven days apart. Relayed, single origin, not re-verified by me.

**2.7 The floating-point rounding of §1.2 belongs in the register.** The verdict boundary is a
product of two floats and must be rounded before comparison, or four cells of the published
phase space flip on representation alone.

---

## 3. The research corpus: what it covers, and the false pass

`CLAUDE.md` and `.claude/skills/research-corpus/SKILL.md` both state: *"THE INDEX COVERED 8 OF
21 DEEP SEARCHES AND NOW COVERS 21. Fixed 2026-08-20."* `--source-audit` prints
`reaching the corpus by NO route: 0` and `OK (0 problems)`, exit 0. Measured live:

    21   deep-search JSONs in data/deep_searches/
     0   of them carry a `papers` array
     0   paper records ingested from them
   780   papers those searches represent, present as an INTEGER only
   332   papers in the index, UNCHANGED

`docs/r10/corpus_revision.md` proposed schema `canford.deep_search.v1` with a per-paper array
carrying DOI, title, authors, abstract, relevance and PDF availability, and its dry run
predicted the index going **332 → ~572** from six on-disk exports alone. What landed is a
metadata stub. `load_deep_searches()` returns those blobs into a sidecar list; they never merge
into `papers`.

**Say two numbers, never one:**

- **21 of 21** searches reach the index **as metadata**, greppable by `--searches --query` over
  goal and summary text. That part is real and is what was fixed.
- **8 of 21** reach it **as papers**. `--query`, `--doi` and `--method` cannot match a single
  one of the other 13 searches' 780 papers, because no record exists.

`--source-audit` returns green because it measures reach-by-route, and a metadata stub is a
route. **This is the third iteration of the same failure on this one tool**; the memory note
`corpus-index-now-covers-21-searches` records the second, where the audit tested only that a
record existed with a non-empty summary and 8 were hollow. Each fix passed a predicate that was
not the question.

**Live confirmation of scope:** the Undermind workspace holds **exactly 21 completed searches,
none created since 2026-08-19 17:47**. Zotero holds **28 items, 18 with a PDF, 64.3 percent
coverage** — a shortlist, not a corpus.

### 3.1 The identifier arithmetic

| layer | unique DOI-shaped strings |
|---|---|
| workflow agent transcripts | 1,072 |
| tool-result spills | 689 |
| session transcripts | 623 |
| `~/Downloads` | 602 |
| **committed corpus** | **540** |
| d22-gapscan acquisition tree | 482 |
| workflow journals | 171 |
| reader-facing prose | 154 |
| **the 87 other project dirs** | **3,148** |
| **UNION, all sweeps** | **4,388** |

**3,848 absent from the committed corpus; ~3,090 of those are real** after the two-population
validation of §0. Plus **151 arXiv ids and 97 Semantic Scholar ids**, identifier classes a
DOI-only sweep structurally misses — the corpus itself records that 57 of its 60 DOI-less
papers carry an S2 id.

### 3.2 What d22-gapscan actually did, the only pass that fetched papers

The 21 searches carry **1,206 paper slots**; 313 top-ranked rows inspected, deduplicating to
**230 distinct works**. Of those: **198 with a verified identifier**, 4 flagged NEEDS_HUMAN
rather than guessed, 6 rejected as wrong matches, 28 unresolved. Full text **76 reachable, 154
with none**; **38 acquired with identity confirmed against the file's own text**, 2 quarantined
as wrong, **22 net new**. **Read end to end: four.** Its own sentence: *"Acquiring is not
reading."*

---

## 4. Adjudication: what the project's own adversarial layer actually returned

From `docs/R10_JOURNAL_AUDIT_2026-08-20.md`, and it is the strongest skeptical result in the
corpus:

    verdict votes                       62
    distinct claims put to the panel    20
      survived                           3
      refuted                           17
    claims extracted overall           135
    claims NEVER put to any panel      115

**Three claims the R9 handoff carries forward as leads were refuted 0–3**, each by voters who
fetched and text-extracted the primary PDF, and in all three *"the numbers were transcribed
correctly and the inference from them was inverted."* The pattern to carry: a refutation there
means the claim did not survive, **not** that the paper says nothing. Quote the papers; do not
quote the inferences.

**The same assertion appears twice in one handoff, once refuted and once printed as a finding**
— sections 5.2 versus 7C.5 on the DBC gap and the +h gauge offset. 5.2 is right; 7C.5 should be
struck.

And from the recovered checkpoint: in the largest deep-research run, **107 of 169 voter agents
(63.3 percent) died without voting, and 30 claims had all three voters die** against the 5 the
handoff records. **Twenty-five verified-source claims lost every voter and then vanished from
the deliverable.**

---

## 5. Infrastructure, tooling and Claude Code

**5.1 The output surface is 88 project directories, not one.** `~/.claude/projects/` holds 98
directories, **88 of them can-it-ford** — every worktree gets its own. The main one is 3,155
files / 1.22 GB in six classes; the other 87 hold 788 files / 556 MB and **3,148 DOIs, more
than the main directory's 1,867**.

**5.2 Workflow agents die at 32.4 percent.** Measured across 472 unique agents: **153 produced
no result, 109 killed outright by account limits.** Two of my own workflow attempts here: one
burned **1,148,968 subagent tokens for 0 results**; the second returned **1 result from 12
agents**. A deterministic miner did the remaining work for a handful of Bash calls.

**5.3 The synthesis stage dies last and takes the product.** Three recorded instances: the R10
run (three agents lost to a monthly spend limit, `connector_revision_AUDIT_d20.md`); the
237-agent `deep-research` run, which **never produced its report**; and my own first attempt.
**The fix is to checkpoint each stage to disk before returning**, and it is validated: my second
attempt died too, and the one layer that had finished **survived**.

**5.4 `/usr/bin/ls` and `/usr/bin/cat` do not exist on this Mac.** They are at `/bin/`.
`/usr/bin/grep` and `/usr/bin/sed` do exist. Agents over-generalising the project's
`/usr/bin/grep` rule made 38 failed calls; I made several more in this very session.

**5.5 Half of one 300 MB layer is base64 PDF page images** — 768 blocks, 148.4 MB, from
`Read(pdf, pages=)` calls. **A single false line in one workflow prompt cost 125.3 MB** by
telling agents to read PDFs that way instead of with `pdftotext`, which **exists**
(`/opt/homebrew/bin/pdftotext`, poppler 26.07.0, installed 2026-07-15). A separate R10 pass
asserted the machine had no `pdftotext` and spent part of a night writing a Swift replacement.

**5.6 Other measured tool behaviour.** `WebFetch` has a hard **10 MiB** response cap and
persists fetched PDFs to `tool-results/webfetch-*.pdf` where `pdftotext` can read them.
`StructuredOutput` silently fails to parse large payloads. Claude Code's `auto` permission mode
depends on a separate model; when it is down, **every Bash call is blocked**. During the R10
night `WebSearch` was dead, `WebFetch` was *half* dead (redirect detection worked so `doi.org`
looked fine while content failed), DuckDuckGo silently returned zero, and the arXiv API ignored
queries when `sortBy` was set — **four findings were withdrawn rather than reported**, which is
the correct handling.

**5.7 CI is greener than it is true.** `canford-checks.yml` sets `continue-on-error: true` on
`register_integrity` and `count_claims`, so **2 of 6 steps cannot turn a run red**. And the
workflow **does not exist on `origin/main`**, so the default branch — the one the public reads,
the Space syncs from and Vercel builds from — gets **no `params_check`, no physics gates, no
stationarity self-test**. Measured against a clean `origin/main` checkout: `params_check` exits
0, `register_integrity` exits 0, `count_claims` **exits 1 with 25 blocking defects**, and three
steps have no script on main at all.

**5.8 Positional citations are measurably dead.** Of **7,445** distinct `file:line` citations in
the mined corpus: 5,204 resolve at repo root, 923 under solver/venv/subdirs, 919 nowhere, and
**24 point at a real file past its current end**. Thirteen of the 24 are `SESSION_STATE.md`
lines 111–302 in a file that is **108 lines**; three are past the end of `README.md`; three are
in `.remember/now.md`, which is **zero lines**. `CLAUDE.md` forbids positional citation of
itself for exactly this reason. Nobody had measured that it applies corpus-wide.

**5.9 Public surfaces.** `can-it-ford.vercel.app` is live, is the repo's declared homepage, and
**its physics is correct** — warpmpm named, L1 as the joint rule, an explicit safety
disclaimer, both outbound links 200. Vercel preview deploys return **404**, so they are not
public. `spaces/josiecerrell/can-it-ford` is `RUNNING`; `spaces/.../can-it-ford-demo` is
**public with stage `NO_APP_FILE`**, broken since 2026-08-18, but **nothing links to it**.
`models/josiecerrell/can-it-ford-sweep-v1` is **public with 37 real files, no README, no
licence**, and is the superseded box-proxy lineage with `density_plausible=False` on all 36
rows.

**5.10 The Hugging Face Spaces licence trap.** The Hub **does not emit a `license:` tag for
Spaces** as it does for datasets and models. Reading the tag array and concluding "unlicensed"
is a false negative produced by the predicate. Both Spaces carry `cardData.license:
bsd-3-clause`.

**5.11 W&B carries a 0-second trap.** All 17 gated runs are in W&B, but **backfilled from the
Mac on 2026-08-17 at 21:30**: `host: Josephines-MacBook-Air.local`, `gpu: None`, `_runtime: 0`.
The dashboard shows **0 seconds runtime for 17 GPU simulations**. Across all 106 runs, not one
records a GPU string. This independently corroborates, from a separate system, that
`wall_time_per_simulated_second` is unrecoverable: **17 of 17 `summary.json` files carry no
job id, host or timing key**, so there is no join key to Slurm accounting.

---

## 6. Physics and paper findings carried forward

Relayed, single-origin, **not re-verified by me**, and listed so they are not lost:

- **The class labels were derived from a hull that never ran.** The class audit grades a hull
  scaled by lambda, lengths 4.90 m and 5.20 m; no such hull entered any run.
- **`xie2023physgaussian` performs zero physics validation** — its entire quantitative
  evaluation is rendering PSNR on synthetically deformed scenes. If it is cited near a physics
  claim, move it.
- **The idev burn figure 98.5–99.1 percent is stale**; re-measured **93.8 percent**.
- **`flood-mpm-debugging-reference` states LS6 is aarch64. LS6 is x86_64**, and that skill loads
  before Methods or Limitations text is written.
- **The MCP deny list is bypassable by alias** — nine exact-name UUID aliases plus four
  capability aliases under differently-named servers. Two rules hold; two are inert because the
  tools they name do not exist.
- **`sphere_heave.py` is not at risk.** The `r5-physics` worktree is gone and 26 citations point
  into it, but the file is committed on `claude/r5-physics` **and pushed to
  `origin/claude/r5-physics`**, and present in five live worktrees. A stale path, not a lost file.

---

## 7. My own errors, recorded

Seven, all caught and corrected in place, listed because the same classes recur:

1. **398 agent results** — double-counted one run existing as two partial copies. True: **321**.
   The document recording that duplication was one I had already read.
2. **"netrc key found: NONE"** — my parser assumed a 40-char token; the live key is 86 chars.
3. **`can-it-ford-results` called empty** — read from a storage column, not the file list. It has
   **120 files**.
4. **A glob is not a walk, twice.** 642 vs 1,284 agent files; then 0 vs 2,818, ten minutes after
   writing the rule into memory.
5. **`workflow_runfiles` returned 0** because a `.json` is one object, not paragraphs. True: 392.
6. **A leaky citation regex** that both invented files (`REFERENCE.md` → `ENCE.md`) and lost real
   ones (dropped leading slashes).
7. **A resolver trying one root**, calling 2,217 citations unresolved when **923 resolve**.

And the one that is not an arithmetic slip: **I published a stamp saying "zero writes to HF or
GitHub" after closing four GitHub issues.** Corrected.

---

## 8. What is NOT in this corpus

Stated plainly rather than implied.

- **The prose inside the transcripts is read only at the top.** 7,675 novel blocks are mined,
  ranked and addressable; roughly the top 90 have been read. The **citations** inside all of them
  are checked; the **surrounding prose** is not.
- **148.4 MB of base64 PDF page images** inside the agent transcripts were counted, never decoded.
- **The 73 reference PDFs were read to 4–12 pages each**, so a DOI or result printed later is
  missed.
- **No contamination check** separates DOIs belonging to unrelated work from project ones.
- **Remote machines were not swept.** Vista `$WORK` and LS6 hold outputs; only `sacct`, quota and
  a git status were queried.
- **`~/Desktop` and `~/Documents` were not swept.**
- **115 of 135 deep-research claims and roughly 350 of 399 R10 findings remain unrouted.** The
  merge is the substrate for clearing that backlog, not the clearing of it.

---

## 9. Where everything lives

| artifact | what it is |
|---|---|
| `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md` | this file, the reader |
| `~/can-it-ford-workflow-archive/MERGED_READER_CORPUS.json` | the machine bundle, ~13 MB |
| `~/can-it-ford-workflow-archive/mined/` | per-layer ranked distillates |
| `~/can-it-ford-workflow-archive/CITATION_CHECK.json` | all 7,445 citations classified, re-runnable |
| `~/can-it-ford-workflow-archive/layer_checkpoints/` | the one workflow layer recovered from a dead run |
| `~/can-it-ford-workflow-archive/WORKLIST.json` | the 4,031-file work-list, by layer |
| `docs/SECOND_EYES_AUDIT_2026-08-20_1200.md` | the chronological working log, nine rounds |

The archive sits **outside the repository** deliberately: it is 26 MB of unreviewed agent output
and the repository is public.
