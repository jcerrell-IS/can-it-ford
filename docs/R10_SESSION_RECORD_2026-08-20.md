# SESSION RECORD, 2026-08-20, 02:30 to 11:55 BST

The complete record of one session: 19 commits on `claude/add-ci-checks` plus 1 on
`claude/r8-register`, all pushed, 31 files created, 12 modified. Written so a successor
needs nothing else to continue.

**Every number below was measured live in this session.** Where something is relayed from
another session or from a document, it says so. Where something could not be checked, it
says that instead of guessing.

Base of the session: `b0f1eda`. Tip: `96393ca`, pushed and verified equal to the remote.

---

## 0. THE FIVE THINGS THAT MATTER MOST

1. **The adversarial panel judged 20 claims, not 7.** 3 survived, **17 were refuted**, and
   the record kept 4. Three of the thirteen unrecorded refutations are claims the handoff
   carries forward as leads, all lost 0-3 with the voter having read the primary PDF.
2. **The corpus index could see 8 of 21 deep searches.** It now sees 21, they are tracked,
   and four of the thirteen that were invisible answered live project questions.
3. **The reproducibility record is the unclaimed contribution.** Three deep searches say no
   study publishes it in one place. Measured: **17 of 17 gated runs, 10 of 10 provenance
   fields complete, zero provenance failures.** Now emitted and verified by a script.
4. **Six literature candidates have died on the scope test, five on ONE structural ground.**
   The SPH boundary-treatment literature cannot supply a mechanism for this solver's floor.
5. **I shipped a false pass and an adversarial verifier caught it six hours later**, in the
   tool built to stop exactly that. Recorded in full in section 6, because the mistake is
   more useful than the fix.

---

## 1. EVERY COMMIT, IN ORDER

| time | sha | subject |
|---|---|---|
| 02:42 | `1613c80` | Three claims the handoff carries forward were refuted 0-3, and the panel judged twenty of them not seven |
| 02:57 | `de891a9` | The corpus could not see 13 of its 21 searches, and the first gate that can fail for an outside reason |
| 02:57 | `2819b99` | Deep-search records 1 of 3 |
| 02:58 | `cd5b9c0` | Deep-search records 2 of 3 |
| 02:58 | `0d7def2` | Deep-search records 3 of 3 |
| 03:02 | `fd53992` | Four standing rules amended from searches the corpus could not see |
| 03:05 | `8a3f37b` | Both skills that load before Methods text were telling sessions wrong things |
| 03:20 | `bb8ead1` | Seventeen hooks could turn a guardrail bug into a hard stop |
| 03:37 | `de0f9d0` | The closest published analogue to Job B is an SDF-coupled SPH sphere |
| 03:42 | `67b8fac` | The adversarial review path is alive again |
| 04:08 | `0de4091` | The closest analogue refutes itself in its own Section 6 |
| 04:09 | `ae49f35` | The review-path outage ended, and the claims it stranded are still unreviewed |
| 11:16 | `3400e2b` | The tool I built to stop a false pass shipped with one |
| 11:16 | `95160b4` | The eight hollow records backfilled |
| 11:35 | `85c247f` | Two guards tested for a keyword and for a checkout |
| 11:38 | `1150679` | The thing this project is best at is the thing three deep searches say nobody publishes |
| 11:43 | `5a2424f` | A2 meant two things 2100 lines apart, and one of them said gravity was retracted |
| 11:45 | `610efa6` | Three licences for one project is refuted |
| 11:53 | `96393ca` | The data licence is now one licence |

On `claude/r8-register`: `d34f24b`, the register port that makes that copy a superset.

---

## 2. SCRIPTS WRITTEN, WITH WHAT THEY DO AND HOW TO RUN THEM

### `analysis/cm_floor_check.py` — the first gate that can fail for an external reason

Method from Baumgarten, Couchman and Kamrin `10.1002/nme.7217` equation 73. For a fluid of
fixed volume above a floor:

    z_cm >= z_bottom + (A_tank - A_hull) * depth / (2 * A_tank)

No tolerance is chosen by anybody. **Their `2/3 m` is their geometry; the METHOD transfers and
the number does not.** Runs on `rollout.npz`, no GPU.

    /opt/homebrew/bin/blender -b --python analysis/cm_floor_check.py

**Verified result, all 17 canonical runs present locally: 11 violate over the full record,
4 survive the settle transient.** The structure is the finding:

| group | margin / depth | frame of min | particles below clamp |
|---|---|---|---|
| g48 x3 | **-0.068** | **0** | **0** |
| g64 baseline x3 | -0.0006 to +0.0011 | 3 | 296 to 609 |
| g96 x3 | -0.018 | 1 | 0 |
| sweepV v0.5 to v3.0 | **-0.012 to +0.020, monotone** | 3 to 4 | 0.5 to 4.6 pct, monotone |
| m1100/m1609/m2337, **NOT canonical** | **-0.20** | **89** | **17.8 pct** |

**g48 violates at frame 0 with zero particles below the clamp**, so it is the initial
condition and not dynamics, and those are the same three runs item 7 flags for gate P-3.
Two gates now flag the same three from opposite directions.

**MY FIRST PASS FAILED 23 OF 23** and it was my instrument, three bugs all pushing toward a
false failure: voxelising frame 0 overcounted volume by 18.4 percent at g64; the hull plan
area was ignored, another 11 percent; and the `floor` scalar is not the bottom of the water,
because the driver clamps at `floor - 0.25*dx` and 2334 of 48367 particles sit below `floor`
at rest.

**Unexplained and recorded, not resolved:** at g64 about 2300 to 2800 water particles sit
below the `floor` scalar at frame 0; at g48 and g96 the count is **zero**. Nobody has read the
initialisation path to explain a resolution-dependent difference of that shape.

### `scripts/verdict.py` — the typed return

`claude -p --output-format json --json-schema`, which had **zero hits across `scripts/`** for
any of `--output-format json`, `--json-schema`, `--bg`, `claude agents`, `claude -p`. CLI
2.1.234 carries all five, confirmed from `--help`.

Schema forces `verdict` as a three-valued enum plus REQUIRED `predicate` (what was actually
run) and `scope` (what it could not see). **Exit codes 0 / 1 / 2**, and every wrapper failure
returns 2, never 0.

    python3 scripts/verdict.py --allow-tools "<claim>"

**Tested on all three branches, live:** `exit=0 VERIFIED` on a claim I had measured,
`exit=1 REFUTED` on the same claim with a wrong number, `exit=2 COULD-NOT-EVALUATE` on a claim
needing a live LS6 read behind MFA. The third refused to substitute Vista's socket for LS6's,
refused a cached static-facts tool, and declined to let its own general knowledge decide.

**A caution from testing it:** my first exit-code test piped to `head`, so `$?` was head's
status and every branch looked like 0. The tool was right and the harness was wrong.

### `analysis/reproducibility_manifest.py` — the unclaimed contribution

    python3 analysis/reproducibility_manifest.py

**Verified: 17 of 17 runs readable, 10 of 10 provenance fields complete on every one, ZERO
provenance failures.** Every recorded `canitford_git_commit` resolves in the live object store;
every recorded `mesh_sha256` matches the live canonical mesh `b379fa44`.

Absent and NAMED rather than dropped: GPU model, wall-time-per-simulated-second, multi-GPU
scaling. A search of `data/` and `renders/` for wall, elapsed, GPU, GH200, A100, jobid and
slurm returns **zero files**; they are in Slurm accounting on Vista.

---

## 3. THE CORPUS TOOL, FOUR DEFECTS CLOSED AND ONE I INTRODUCED

`analysis/research_index.py`:

1. **The index saw 8 of 21 deep searches** for five weeks, because `REPORTS` is a hardcoded
   list of markdown files under `~/Downloads`. Fixed with the two-phase ingest the corpus
   revision prescribes: an agent turn writes `data/deep_searches/`, the shell builder reads it.
   New `--searches` and `--source-audit`.
2. **`parse_report` returned `{}` silently on a missing path.** Seven of eight REPORTS paths
   live under `~/Downloads` and none inside the repo.
3. **`cited_reader_facing` was inflated by EXACTLY 9.** `docs/Dynamic_Vehicle_Traction_in_Floodwater.md`
   is a raw connector dump carrying 34 DOI strings. Measured both ways; the delta is 9. Honest
   ladder: **34 prose / 43 with the dump / 3 printing.**
4. **`--query` matched title and abstract and NEVER authors.** That is how "none of the six
   closest prior-art DOIs is in the corpus" reached three sessions. All six were present.
   Live now: `--query Al-Qadami` returns **5**, Shah 7, Kramer 2, Steffen 4.

**And the one I introduced.** `--source-audit` tested only that a record existed with a
non-empty summary. Eight records carried a PLACEHOLDER summary and an EMPTY goal, so
`--searches --query` could grep **13 of 21** while the audit printed **OK, 0 problems**. Fixed
two ways: `HOLLOW` is now a distinct failure from `ORPHAN`, and `--searches --query` prints
`searched N of M records`. Verified at **21 of 21, 0 hollow**.

---

## 4. THE LITERATURE, EVERY VERDICT

### 4.1 The panel, recovered from the journal

62 votes, all joined to a claim by parsing `## Claim under review` out of each voter's own
`agent-<id>.jsonl`. **20 distinct claims, 3 survived, 17 refuted, 115 of 135 never adjudicated.**

**Three the handoff carries forward, all 0-3:**

- **`arXiv 2210.10377`**: every number verbatim correct, but **Table III is a Reynolds sweep,
  not a grid-refinement study.** Re rises 500x while resolution rises 24x. The paper's actual
  fixed-Re convergence test is Fig 8b and shows MEA converging. The handoff calls this claim
  UNVERIFIED because "its verifiers all died" and says it **prompted building the third
  accessor**. The verifiers did not die.
- **`10.1002/fld.2353`** (Han and Cundall): contradicted on direction by Mei, Yu, Shyy and Luo
  2002, and fails the scope test on discretisation and regime independently.
- **`arXiv 1909.13655`**: the benchmark is a momentum identity (free block resting under
  gravity, `n` fixed at 2601, so the target is a constant) and **there is no fluid anywhere in
  the paper.**

**Read "refuted" correctly:** the voter prompt ends "Default to refuted=true if uncertain". In
every case the voters verified the quoted material as verbatim and refuted the INFERENCE.

### 4.2 The two MDPI papers, read at source via the browser

I had assigned these to Josie as "the highest-value human minute" because WebFetch returned
403. **I have browser tools and MDPI serves OA full text as HTML.** Both read in under a
minute. A full-disk search across **2,590 PDFs in five stores** found neither.

**`Was26`, `10.3390/math14111845`** — matched Job B on four axes and **fails three of five
scope questions.** Its buoyancy is Equation 17, `F = -n_colliding * s_buoyancy * m_i * g`, a
**particle count times a scale factor auto-calibrated to hit a target submergence.** Section 6
verbatim: it *"prioritizes GPU efficiency and real-time performance over exact hydrostatic
accuracy, which is acceptable for interactive applications but may not satisfy the
requirements of engineering-grade simulations"*, and their own future work is to replace it.

**Two things transfer and both beat the headline.** They bound parallel impulse-accumulation
non-determinism at `O(N_c * eps_mach)` with `eps_mach = 1.19e-7`, giving relative force error
of order **1e-3** — so **atomic non-determinism cannot explain 35 percent.** And Equation 17
is a defect worth checking here: I ran it, **zero hits**, this project integrates rather than
counts.

**`Tao21b`, `10.3390/jmse9040416`** — a fictitious-particle method whose ghosts carry a
hydrostatic pressure correction. This solver's floor **writes a velocity onto a grid node,
never a pressure, and has no boundary particle of any kind.** Re-verified: a search of the
vendored core's `kernels/` and `core/` for dummy, ghost, mirror and fictitious particle
returns **zero files**.

### 4.3 THE RULE THAT REDIRECTS THE ACQUISITION EFFORT

Six candidates dead on the scope test, **five on one structural ground**: every one is SPH,
every one's mechanism needs boundary particles or pressure extrapolation, and this solver has
neither. Its whole floor BC is five lines projecting out a normal velocity component.

> **The SPH boundary-treatment literature cannot supply a MECHANISM for this floor, only a
> precedent.** Any paper whose fix is a dummy particle, a pressure extrapolation or a gauge
> offset fails question 2 before it is read.

**Stop paying for SPH wall papers.** Ada12, Val15b and Mon09 will fail identically. Aim at
MPM/PIC grid-node boundary conditions: `10.1002/nme.70054` and `10.2312/egs.20241022`, neither
read.

### 4.4 What the invisible searches were carrying

- **"Physics Simulation Validation Protocol"** (81 papers, 15 July): report a **signed
  discrepancy and a validation interval** rather than inherit a band. And *"a NO-FORD claim
  may be issued whenever uncertainty spans or exceeds that boundary"* while a FORD claim may
  not. **All 17 gated runs are NO-FORD.**
- **"which realism effects change a verdict"**: *no study quantifies a crowned or cambered
  road against a flat plane* — the crown novelty, independently confirmed. The
  ten-times-flow-speed sound-speed rule **has no primary derivation.**
- **"moving vehicle open source"**: a **body-following refinement window for MPM appears
  unreported.**
- **"Small Data Surrogates"**: N_eff is the 36 conditions, not the 90 frames — the settle
  result from a separate origin.
- **"Reliable AI Scientific Software"**: *model self-review is insufficient; self-validated
  analysis success overstates manually verified success.* Bears directly on the self-reviewed
  exoneration.

---

## 5. CLAUDE CODE, AUDITED LIVE AND HARDENED

- **18 hooks made fail-open.** 17 of 18 invoked their script bare, so a missing script exits
  127 and a PreToolUse hook exiting non-zero blocks every matching tool call. **Control
  measured: 127 unguarded against 0 guarded.**
- **`disableClaudeAiConnectors: true` IS SET AND DOES NOT TAKE EFFECT.** The full claude.ai
  connector set was in the live manifest anyway, including every tool the deny list names.
  18 alias rules added, 43 to 61. Confirmation was immediate: four
  `plugin_desktop-commander` write tools dropped out of the manifest within one turn.
  **This is a patch: the UUID changes on reconnect.** I deliberately did NOT write a check,
  because a plain-shell script cannot see the tool manifest.
- **Two deny rules are inert rather than protective**: no `zotero_delete_*` and no
  `tacc_submit` exist at all, so those rules read as coverage and provide none.
- **Section 11's own claims corrected**: there are 18 hooks not 14, 12 already carry a
  matcher, and its recommended fix `Bash(git commit*)` is **permissions syntax, not hooks
  syntax**.
- **The adversarial path is alive again.** One probe, 6.05 seconds, correct SHA. The CLAUDE.md
  section is kept verbatim under a subheading with the outage marked ended. **The claims it
  stranded are still unreviewed; the path being alive does not review them retroactively.**
- **Two guards rewritten to test the condition, not a keyword.** `stale_csv_guard` measured
  header columns (7 tests pass); `count_claims_check` gained **NOT-EVALUABLE** (worktree
  derives 16/17 and emitted 25 phantom defects; it sees 0 of 24 declaration sites).

---

## 6. EVERYTHING I GOT WRONG, AND HOW EACH WAS CAUGHT

Recorded in full because the failures are the transferable part.

| # | what | how it was caught |
|---|---|---|
| 1 | `cm_floor_check` failed **23 of 23** on first run | uniform result distrusted; three estimator bugs found, all pushing one way |
| 2 | Shell DOI scan returned a **false zero** on a file that exists with 34 DOIs | malformed bracket expression; caught by re-running in python |
| 3 | `git add $batch` passed 22 paths as **one argument** | zsh does not word-split; the memory entry existed |
| 4 | Assigned two MDPI PDFs to Josie as a human task | I had browser tools all along |
| 5 | **Shipped a false pass**: `--source-audit` OK while `--query` grepped 13 of 21 | **the workflow's adversarial verifier**, six hours later |
| 6 | Exit-code test piped to `head`, so every branch read as 0 | re-ran without the pipe |
| 7 | Wrote that the register id collision **did not reproduce** | my grep used `^**A2.`; it appears as `**A2 is RETRACTED.**` |
| 8 | Wrote that **both** public Spaces were unlicensed | `can-it-ford` declared it in its README; I read the Hub **tag listing** as the front matter |
| 9 | `grep -c ... \|\| echo 0` producing `0\n0` in my own credential scan | instrument failure #2 from the table I was citing |
| 10 | Two `PARTIAL` rows in the manifest that were my own key-naming bug | it **understated** the project, the rarer direction |

**Five of ten were caught by an instrument I built or by re-running my own check. One was
caught by the adversarial layer. That ratio is the argument for keeping the layer.**

---

## 7. THE REGISTER COLLISION, WHICH WAS THE MOST DANGEROUS SINGLE FINDING

Three ids meant two things each, ~2,100 lines apart in one file:

| id | canonical item, lines 18-90 | R9 discrepancy row, line 2196+ |
|---|---|---|
| **A2** | **"Gravity is -9.81 and was never unknown"** | "…is RETRACTED" |
| B1 | two depth-resolution numbers, both correct | "…is CLOSED" |
| B7 | no pressure field anywhere in warpmpm | "…is RE-SCOPED" |

Anyone quoting "register A2 is retracted" reopens the gravity claim that item 15 spent two
corrections killing, and this file is cited verbatim by other people. All three prefixed
`R9D-`, with a table in place. **Verified: zero bare `A2 is / B1 is / B7 is` lines remain in
either copy.**

The two register copies had diverged to 2232 and 3216 lines against a shared merge-base at
`0efe4f3`, with **neither a superset.** r8-register is now a superset (**zero missing
headings**), so that merge is a take-mine.

---

## 8. PLATFORMS, MEASURED LIVE

Account `josiecerrell`, **PRO**, write token. Eight repos: 3 datasets (2 public), 4 Spaces
(2 public), 1 model.

**"Three licences for one project" is REFUTED.** BSD-3-Clause for code and an open-data
licence for data is correct separation; `CITATION.cff` line 4 reads `type: dataset`. The R10
proposal to change it to BSD was **killed by its own verifier, correctly.**

**Resolved this session, on the authors' decision:**
- Data is **CC-BY-4.0 everywhere.** Both `CITATION.cff` copies changed from ODC-By-1.0. This
  direction re-licenses nothing already published, since all three Hub datasets already
  advertised cc-by-4.0.
- `can-it-ford-demo` now declares `license: bsd-3-clause`. One line, diff shown first,
  **verified by re-downloading the live README** rather than trusting the upload's exit code.
  Space commit `59f1b98`.

**Still open:** `can-it-ford-sweep-v1` is **public, has 30 downloads, and its own README says
it has never contained any data file.**

---

## 9. WHAT IS OPEN

1. **PHASE 2-3 of the workflow plan**: 14 register rows and 12 CLAUDE.md corrections, in
   commit-sized path-limited groups.
2. **115 of 135 deep-research claims and roughly 350 of 399 R10 findings remain unrouted.**
   The extraction commands are in `docs/R10_JOURNAL_AUDIT_2026-08-20.md` section 8.
3. **Vista and LS6 sockets are cold** and need Josie's MFA. Blocks the two ABSENT manifest
   rows and the Azhar flotation ladder.
4. **`can-it-ford-sweep-v1`**: delete, privatise, or populate.
5. **The three targeted sessions** (`r9-overleaf`, `d18-platform`, `d22-gapscan`) have
   verified non-overlapping work waiting.
6. **The CI `continue-on-error` mask can now come off**, and only now, because removing it
   before the NOT-EVALUABLE branch would have failed every worktree-rooted run on phantom
   defects.
7. **No external PDF was read from its own text except the two MDPI papers.** The acquisition
   slot's measured **15 percent scrape error rate** applies to anything else quoted at second
   hand.

---

## 10. COMMANDS WORTH KEEPING

```bash
# the corpus, now covering all 21 searches
python3 analysis/research_index.py --searches --query <term>
python3 analysis/research_index.py --source-audit          # exits 1 on orphan OR hollow
python3 analysis/research_index.py --query <author>         # authors now match

# the external falsifier (numpy only exists inside Blender on this Mac)
/opt/homebrew/bin/blender -b --python analysis/cm_floor_check.py

# the provenance record
python3 analysis/reproducibility_manifest.py

# a typed verdict whose exit code cannot confuse a failed check with a passing one
python3 scripts/verdict.py --allow-tools "<claim>"          # 0 verified 1 refuted 2 cannot-evaluate

# the guard that now measures instead of demanding a keyword
printf '%s' '{"tool_name":"Read","tool_input":{"file_path":"<path>"}}' \
  | python3 .claude/hooks/stale_csv_guard.py
```

**Environment facts measured this session:** `/usr/bin/cat` does not exist on this Mac,
`/bin/cat` does. numpy exists only inside Blender 5.2 (`2.3.4`); all five system interpreters
fail `import numpy`. `pdftotext` **is** present at `/opt/homebrew/bin/pdftotext` (poppler
26.07.0, since 2026-07-15), contradicting the R10 report's foundational constraint. `hf` CLI is
at `/Users/josie/.local/bin/hf`. Claude Code is **2.1.234**.
