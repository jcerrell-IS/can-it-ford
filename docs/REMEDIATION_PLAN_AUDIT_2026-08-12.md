# Audit of the pasted "Claude Code Configuration and Remediation Plan"

**Date:** 2026-08-12
**Subject:** a 592-line plan proposing 7 configuration features and an 18-item
remediation punch list, authored in a chat session that states in its own caveats
that it had **no live read access to this repo**.
**Subject file, recorded 2026-08-13 so this audit is re-derivable:**
`~/Downloads/compass_artifact_wf-aae75abf-0f67-59aa-8289-cee140b44819_text_markdown.md`,
artifact id `aae75abf`, 42,709 bytes, sha256
`4b2469e7020c2b60773a4ee9971d6a9fad1136a04a13a375a99423dddd4dbdb8`.
The id appeared nowhere in the repo until this line, so this audit could not be checked
against its own subject. Register K0 establishes the practice being followed here: the
8-hex ids are real files at `~/Downloads/compass_artifact_wf-<id>-*_text_markdown.md`,
recorded so any claim can be re-verified against the report it came from. K0 scopes that
to ids cited *in the register*; extending it to this audit is a deliberate application of
the same rule, not a claim that K0 already covered this file.
The file is 591 newlines with **no trailing newline**, hence 592 lines; that
off-by-one is why a `wc -l` check reports 591 against the "592-line" subject above.
Identity confirmed by content, not filename alone: it opens with
"Claude Code Configuration and Remediation Plan for \"Can It Ford?\"", and its TL;DR
states the 18-item punch list and the no-live-read-access caveat.
**Method:** every claim re-derived against live files, plus a 12-agent parallel audit
(6 documentation researchers, 5 item verifiers, 1 adversarial completeness critic).

---

## Headline

The plan is **substantially stale**. Of its 18 remediation items, **9 rest on premises
that live state refutes** (items 1, 4, 5, 8, 12, 13, 14, 16, 17), and 2 of those would
have damaged the repo if executed. A 10th, item 2, asks you to verify something that
is already settled. Counted 2026-08-12 from the verdict column of the table below; an
earlier draft of this line said 6, which was simply wrong. Its
7 configuration features were **already implemented, in better form, on 2026-08-11**,
except for the permissions block, which was genuinely missing and is the one part worth
adopting.

The plan's single most useful contribution was **Item 7**, which this audit initially
and wrongly marked refuted. See "Correction to this audit" below. That error is the
most instructive result here.

---

## Correction to this audit, recorded because it is the whole lesson

Item 7 claimed `mu_wet = 0.3` survived at lines 36 and 112 of the
flood-mpm-debugging-reference skill. A first pass ran
`/usr/bin/grep -rn "mu_wet" --include="*.md"` and got no hit in that file, and marked
the item REFUTED.

**That was wrong.** The file writes it with a **Greek mu**, `μ_wet`. So does register
Section I, at `:342`. An ASCII sweep for `mu_wet` returns nothing and reports the file
clean. The plan's line numbers, 36 and 112, were **exactly right**.

Worse, the second attempt also failed. `/usr/bin/grep -rnE "(mu|μ|µ)_wet..."` on this
macOS **did not match the multibyte character either**, while Python's `re` on the same
line returned True. Verified directly: `xxd` shows the byte pair `cebc` (U+03BC), and
the same pattern matched in Python and not in `/usr/bin/grep -E`.

**Two rules follow, and they extend register H0.**

1. `/usr/bin/grep` fixes the gitignore blind spot but has a **separate non-ASCII blind
   spot** on this machine. For any claim sweep involving Greek letters or symbols, use
   a Python `re` walk, not grep. A grep miss is still not evidence of absence.
2. The register's own delete-on-sight table uses `μ`. Any tool that enforces that table
   by ASCII matching enforces nothing.

`.claude/hooks/banned_phrase_guard.py` now matches `mu`, `μ` and `µ`.

---

## Item-by-item verdicts

| # | Plan claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Pull TACC job 895378, highest priority | **REFUTED** | Completed 2026-08-07. Summaries on local disk under `renders/yaris_render_s3_enhanced/`; `data/coupling_validation/ladder_d_g64.{log,json}`. `session_start_protocol.py:7` says do not re-propose as untested. Re-running burns from ~673 SUs expiring 2026-09-30. |
| 2 | Floor restitution vs friction gate unverified | **ALREADY DONE** | `restitution=0.05` satisfies the `mpm_solver_warp.py:1915` gate, so `floor_friction=0.55` registers. Already asserted at `session_start_protocol.py:3`. |
| 3 | C2 crash root cause unconfirmed | **STILL OPEN** | Genuinely open. |
| 4 | Hardcoded `bulk_modulus` at `:355`, KeyError at `:302`/`:333` | **REFUTED** | `bulk_modulus` is a parameter with default at `:153`, threaded through `:206`, `:225`, `:231`, `:513`. It appears nowhere else. `:302` is `p.add_argument("--label", ...)`, `:333` is a `canonicalize(load_vehicle(...))` call, `:355` is an f-string. The frames guard is `f_check = min(45, a.frames - 1)` at `:442`. All three line numbers are wrong. |
| 5 | Cherry-pick `7390168` | **REFUTED, would have damaged the repo** | `git merge-base --is-ancestor b844118 main` exits 0. The change is already on main and live at `analysis/paper_fig_pipeline_diagram_v2.py:92`. `7390168` and `f302ce0` are not ancestors. Register **H5 says explicitly do not cherry-pick either**. A cherry-pick yields an empty commit git refuses, or a conflict against b844118. |
| 6 | Collapse five corrections ledgers | **PARTIAL, mis-scoped** | Four exist at depth 3, not five. One of them, `reference_docs/briefing_vault/00_MASTER_CORRECTIONS_INDEX.md`, is in `permissions.deny` as a `Read` rule, so it **cannot be read in order to be merged**, and deny beats allow at every scope. CLAUDE.md's own rule also requires pulling VERIFIED-tier findings into the register *before* superseding a file; the plan inverts that order. |
| 7 | `mu_wet = 0.3` at skill lines 36 and 112 | **CORRECT, and now fixed** | See the correction above. Fixed at both sites. |
| 8 | Classifier has never run on the 17 runs | **REFUTED** | `data/failure_modes_by_run_classified.csv` holds 17 rows, 16 SLIDE / 1 STUCK, regenerated 2026-08-11. Register D6 marks the "never run" text stale since 2026-08-05. Re-running it *before* unifying the `G = 9.80665` fork at `failure_modes.py:14` would destroy the only clean before/after comparison that can close the item. |
| 9 | Credit `solidify_watertight` in the paper | **STILL OPEN, with an unstated blocker** | Neither `sim_standing.py` nor `vehicle_live.py` is tracked (`.gitignore:14: renders/`), so there is no commit history to date an authorship claim from. |
| 10 / 16 | Implement Zhao 2019 BCs; check cb-geo/mpm | **16 REFUTED** | Register J8 closed it 2026-08-07 as a false premise: the BCs were implemented in Anura3D by a Cambridge/TU Delft/Deltares team, unrelated to cb-geo. Register B7 adds that a warpmpm outflow BC **cannot** be pressure-controlled, because no pressure field exists. Item 10 remains real, downstream of that. |
| 12 | Deploy the `.zshrc` cleanup | **REFUTED as a re-run** | The delivered block is already present byte-for-byte; re-running appends a duplicate marker pair and breaks future marker-delimited replacement. |
| 13 | Fix miscitation at `four_rung_ladder*.md:136` | **REFUTED** | Line 135 of both files already carries the retraction. Repointed by `841d666`; the surviving "independently" overclaim was fixed separately. Register D6h says do not re-report it. Editing there would most likely delete the disclaimer D6i installed. |
| 14 | 1609 and 2337 kg unsourced | **REFUTED** | Register E6a traces them to CCSA / George Mason FE decks: 1609 kg = 2020 Nissan Rogue, 2337 kg = 2018 Dodge Ram 1500. Section I lists the flat "unsourced" phrasing for deletion. |
| 15 | Retrieve Xia 2011 / Shu 2011 | **PARTIAL** | A T2 transcription exists (G10a). Publisher PDFs still required before citing coefficients. |
| 17 | Prune 32 worktrees, one prunable | **REFUTED** | `git worktree list` returns **4**. `git worktree prune --dry-run -v` returns nothing. |
| 18 | Reconfigure Filesystem/GitHub connector scopes | **OUT OF SCOPE** | A claude.ai chat-surface concern. `.claude/settings.json` sets `disableClaudeAiConnectors: true`; `.mcp.json` carries deepwiki, scite and wolfram over http. |

---

## Configuration features: what was already there

| Feature | Status |
|---|---|
| 1. CLAUDE.md restructured with `@import` | **Rejected, see below** |
| 2. Four hook classes | 3 of 4 already existed and were wired on 2026-08-11 |
| 3. physics-skeptic subagent | Already existed, and is **stronger** than the plan's version. Adopting the plan's text would have been a downgrade. |
| 4. Four slash commands | `session-start` is redundant with two SessionStart hooks that already fire |
| 5. `.mcp.json` | Already exists. The proposed `filesystem` and `memory` servers duplicate native file tools and `autoMemoryDirectory`. |
| 6. Permissions block | **Genuinely missing. Adopted, with corrections.** |
| 7. Skill distribution via git | **Structurally incomplete, see below** |

### Why Feature 1 was rejected

`@import` does not reduce context; imported files are loaded too. It buys modularity
only. CLAUDE.md is confirmed synced across Mac, Vista, LS6 and GitHub and is edited by
concurrent sessions, so splitting 544 lines into 7 files multiplies the sync surface
sevenfold and creates 7 files that can drift. In a repo whose dominant failure mode is
duplicate sources diverging, that is a net loss. The plan's 6 proposed rule files also
restate CLAUDE.md content verbatim, which is the same defect.

### Why Feature 7 is structurally incomplete

Git-based skill distribution **cannot reach user-level skills**. Verified live:
`~/.claude/skills/panel-audit-dispatch/SKILL.md`, dated 2026-07-24 and loaded in every
project, still carried two claims from register Section I at `:234` and `:235`, the
stale density band and the refuted "coup_friction is a numerical stability
coefficient". The repo copy was maintained; the user-level copy silently drifted for
19 days. Both are now corrected.

Also outside every repo-scoped sweep:
`~/.claude/_shadowing_backup_2026-08-05/flood-mpm-debugging-reference/SKILL.md:112`
carries the REFUTED note **and** still asserts the refuted claim on the same line. It
is not currently an active skill, so it is a restore-from-backup landmine, not a live
defect. **Left untouched**, flagged here.

---

## Defects found and fixed

**In the corrections register itself,** by the new checker:
- `fd390d6` was cited as a verification anchor with no indication it is an **upstream
  `kks32/mpm-engine` SHA**. It does not resolve in this clone. Now documented, with its
  real source: `renders/yaris_render_s1/geom_live.py:12`.
- `track1_sweep_v2/manifest.csv` was cited bare; the file lives under `data/`.

**In CLAUDE.md item 13 and `scripts/check_claims.py` rule C8:** both carried the stale
"16 places under four names". The fact-enforcement tool was itself carrying a stale
fact.

**Then this audit got the replacement wrong too, and that is worth recording.** A first
pass wrote register D7's "24 sites under five names, `THRESHOLD` 2" into four files as
settled. **D7's split does not reproduce.** Full enumeration, Python walk, assignments
only, D7's own stated scope:

| name | sites |
|---|---|
| `DRIFT_THRESHOLD_M` | 5 |
| `L2_DRIFT_M` | 7 |
| `DRIFT_THRESHOLD` | 8 |
| `DRIFT_M` | 1 |
| `THRESHOLD` | **1** |
| **total** | **22** |

Two defects in D7's count: its `DRIFT_THRESHOLD` 9 counts
`docs/session_notes/archive/mu_sweep_recovered_from_staging.py:60`, inside an
`archive/` directory **D7's own scope statement excludes**; and its `THRESHOLD` 2 is
unreproducible, since exactly one bare-`THRESHOLD` assignment exists at
`scripts/plot_hailuo_comparison.py:7`.

Likely reconstruction of the 24, unproven: 22 + the `archive/` copy + a third
code-shaped site that **no `*.py` glob will ever match**,
`simulation/can_it_ford_mu_sweep.py.DO_NOT_RUN:60`.

**Five names is settled. No bare total is safe to quote.** All four files now carry the
enumeration and its scope instead of a number. Separately, 122 prose mentions exist in
`.md` files and 17 more under `.claude/worktrees/ctx-census/`; none is a declaration
site, and a future count must not sweep them in.

**Tooling note, and the reason the count moved three times.** Three commands gave three
answers on one tree: a `^`-anchored grep missed indented assignments; an ERE
`(^|[^A-Za-z0-9_])THRESHOLD` form returned **zero** on a line Python matched; and the
shell `grep` function skips gitignored paths (H0). For any published count, enumerate
every site with a Python `re` walk and print the paths.

**In skill files:**
- `panel-audit-dispatch` (repo **and** user-level): stale density band; refuted
  `coup_friction` claim; misattributed friction range.
- `geoelements-tech-reference:24` and `:258`: proposed Smith, Modra and Felder 2019
  Eq. 6 as the DRIFT_THRESHOLD citation. Register D7 records that as a misattribution
  and Section I lists it for deletion. The `provenance-audit` skill already documented
  it as false, so **two skills directly contradicted each other**.
- `flood-mpm-debugging-reference:36` and `:112`: the `μ_wet` claim.

**In `.claude/settings.json`:**
- `Bash(grep*)` pre-approved the shell function CLAUDE.md bans, while the mandated
  `/usr/bin/grep` matched no allow rule and prompted. The permission layer was biased
  toward the wrong tool. Fixed by allowing `/usr/bin/grep*`.
- `Read(data/track1_sweep_v3/**)` denies a directory that **does not exist**, while
  `data/track1_sweep_v2/`, the one CLAUDE.md:372 deprecates, was unguarded. Added.
  Note the deny blocks the Read tool only; `analysis/gp_surrogate.py:12` and
  `analysis/build_poster_phase_space.py:9` still read it programmatically, as intended.

---

## What was built

- **`.claude/checks/register_integrity.py`** — checks the register for duplicate item
  ids (the E7/E8 collision class), dangling cross-references (the A6 class), unresolved
  cited paths, and unresolved cited hex tokens. Classifies hex four ways: git object,
  upstream pinned SHA, research artifact under `~/Downloads/compass_artifact_wf-*`, or
  unresolved. Resolution sources are read live from `third_party/*/PINNED_SHA.txt` and
  `*/geom_live.py`, so the list cannot go stale. Current: **0 blocking defects**.
- **`.claude/hooks/audit_integrity_guard.py`** — asks on a root-scoped recursive grep
  that would silently skip `renders/` and `data/` (register H0); denies value-keyed
  substitution of the literal `0.05` (register D7a, where `failure_modes.py:47`
  `slide_speed_ms` is metres per **second**). Verified against 11 true and false
  positives, including the `perl -pi` and escaped-dot `0\.05` evasions.
- **`/audit-facts`** — runs the whole local verification stack and separates new
  findings from the six known-explained warnings.
- **`/engine-audit`** — Genesis/warpmpm conflation sweep, mandating `/usr/bin/grep`.
- **Permissions hardening** — bulk-staging forms denied outright, which also overrides
  the conflicting `Bash(git add *)` allow in `settings.local.json`, since deny beats
  allow; `Bash(idev:*)` denied; six `ask` rules added. `ask` **rules** survive
  `bypassPermissions` where a hook does not, so this is a real second layer.
- **`defaultMode: acceptEdits` was deliberately NOT set**, against the plan's advice.
  In a working tree where two sessions already clobbered each other on 2026-08-07,
  auto-accepting edits removes the prompt that is the last line of defence.

---

## Still open, unchanged by this audit

1. **Run provenance.** `params_check.py` reports across 32 manifests that
   `canitford_git_commit`, `grid_density`, `mesh_sha256`, `solver_git_sha` and
   `vehicle_mass` are missing in **all 32**, `bulk_modulus` in 3. No run traces to code
   plus data plus environment. This is an **open gap**, not a disclosed limitation, and
   it is the largest single obstacle to a reproducibility claim.
2. **The `G = 9.80665` fork** at `failure_modes.py:14` fed the published verdicts. Set
   it to 9.81, regenerate, byte-compare. Do not close by assertion.
3. Items 3, 9, 10 and 15 above.
4. `stop_signal_and_check.sh` exists in `.claude/hooks/` but is wired to no event.
5. `check_claims.py` C5 and C8 fire on any line that quotes a banned phrase in order to
   retire it. Several such false positives were hit while writing these corrections.
   The rules are per-line and cannot distinguish an assertion from a retraction.

---

## STEP 5 CLAUDE.md accuracy pass, 2026-08-12 continuation

### RETRACTION, and it is the important part

An earlier section of this document, and commit `950d654`, claimed **register D7's
count of 24 "does not reproduce"**. That claim was **WRONG** and is withdrawn. D7's 24
is correct.

What the refutation missed is `analysis/gp_surrogate.py:14`:

```python
THRESHOLD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
```

That is a genuine fifth-name declaration of the 0.05 default. It is CLI-overridable
rather than a hard-coded constant, so a strict `NAME = 0.05` regex cannot see it. The
recount then declared D7's second `THRESHOLD` unreproducible on the strength of a
check that was structurally incapable of finding it. **A refutation is an assertion
too, and this one was not re-derived before being trusted.** Found by an independent
read-only subagent tasked with re-deriving the count in Python rather than grep.

**There are TWO independent binary choices, not one.** That is why the number has
moved four times now:

| reading | total |
|---|---|
| bare literals only, `archive/` excluded | 22 |
| bare literals only, `archive/` included | 23 |
| plus the gp_surrogate default, `archive/` excluded | 23 |
| plus the gp_surrogate default, `archive/` included | **24, register D7** |

**23 is reachable two different ways**, which is exactly how two counts can appear to
agree while counting different things. Every total above is defensible *with its scope
stated*. A bare number is what is wrong, not any particular value.

Separately and not in any total: `simulation/can_it_ford_mu_sweep.py.DO_NOT_RUN:60` is
real code carrying the literal, and no `*.py` glob will ever match it.

Three independent methods now agree: a `/usr/bin/grep` loop, a subagent Python `re`
walk, and `.claude/checks/count_claims_check.py`.

### Structural guard added

`.claude/checks/count_claims_check.py` re-derives the count live and denies any edit to
CLAUDE.md, `check_claims.py` or `audit_integrity_guard.py` that asserts a total outside
the defensible set. It handles the two traps this session actually hit: it accepts the
whole set rather than one hardcoded number, and it steps aside for a line that quotes a
number in order to retire it. Wired as a PreToolUse hook on `Edit|Write`. Verified
against 10 cases.

While being built it counted **its own docstring** as a sixth declaration site, because
it quotes the gp_surrogate line as documentation. Fixed by skipping comment lines and
its own file. A counting tool counting its own prose about a declaration is the exact
failure class it exists to catch.

### Claims checked, one falsifying command each

| claim | verdict | evidence |
|---|---|---|
| `vehicle_params.py` `mass_kg` is 1100.0 | CONFIRMED | `:125` reads `"mass_kg": 1100.0` |
| `data/all_runs_inventory.csv` holds 17 runs | CONFIRMED | csv parse: 18 rows incl header |
| `failure_modes.py:14` is `G = 9.80665` | CONFIRMED | direct read |
| `gates.py:12` EXT_REF, `:13` RHO_REF 310.49 | CONFIRMED | direct read |
| `.gitignore:14` is `renders/`, `:10` is `data/*` | **CONTRADICTED** | `data/*` is still `:10`, but `renders` is now `:26`/`:28`. **Self-inflicted** by this session's carve-out. Fixed. |
| nested `./can-it-ford/` duplicate exists | **CONTRADICTED** | does not exist. An entire CLAUDE.md section and every `./can-it-ford/` grep exclusion is now a no-op. Marked as history. |
| `.claude/worktrees/` holds 27 stale copies | **CONTRADICTED** | holds 2. The "multiplies every hit ~20x" figure is stale. |

Bounded pass: 7 checkable claims, not the whole file. The remaining numbered items were
either pure narrative or cite `sim_standing.py` line numbers already verified earlier in
this session.

### Not done, and why

`stop_signal_and_check.sh` could **not** be wired as instructed. It is **staged for
deletion by another session** and is absent from disk. See ACTION REQUIRED.

### Independent verification of the STEP 5 diff, and what it caught

A second read-only subagent was dispatched to re-verify **only the CLAUDE.md diff**,
using different methods than grep. It confirmed 4 claims and contradicted 4. Three of
the four contradictions were **introduced by the accuracy pass itself**, which is the
finding that matters: a pass intended to remove stale claims added new ones.

| claim | verdict | reality |
|---|---|---|
| `.gitignore` line numbers for `data/*` and `renders` | CONFIRMED (then immediately stale) | see below |
| `.claude/worktrees/` holds 2, not 27 | CONFIRMED | 2 |
| nested `./can-it-ford/` is gone | CONFIRMED | gone |
| `gp_surrogate.py:14` verbatim | CONFIRMED | character-for-character |
| all four DRIFT_THRESHOLD readings | CONFIRMED | 22 / 23 / 23 / 24, 23 reachable twice |
| "those .py files are now TRACKED" | **CONTRADICTED** | **2 of 24 tracked.** Un-ignored is not tracked. 22 still have no history, `gates.py` among them |
| carve-out covers `sim_standing.py` | **CONTRADICTED** | top-level only; `_incoming/sim_standing.py` still ignored, and D4a calls `_incoming/` canonical |
| "501 generated artifacts" | **CONTRADICTED** | 881 non-`.py` at any depth. The 501 was a `-maxdepth 2` count over four extensions |
| "5 hits from `.` and 7 with renders/" | **UNVERIFIED** | never named its pattern, so never re-derivable; carve-out invalidated the premise |

### The `.gitignore` line-number reference broke three times in one day

1. `:14 is renders/` went stale when the carve-out replaced the blanket rule.
2. The replacement `:26 / :28` went stale when a comment was added above them.
3. `":32-33"`, written specifically to fix (2), was **already wrong at the moment it
   was written**, because the same commit inserted five lines above it.

Each fix was verified live and each was invalidated by the next edit to the same file.
The conclusion is not a better number. **Every positional `.gitignore` citation in
CLAUDE.md has been replaced with a re-derivation command**, keeping one quotation as
history. A file edited this often cannot be cited by position.

This is the same shape as the count problem: an assertion that was true when written,
trusted afterwards without re-derivation. The guard for counts is
`count_claims_check.py`; the guard for line numbers is to not cite them.

### Concurrency note

The verifier reported the repo changing under it mid-audit: `CLAUDE.md` went from
dirty to committed, and `sim_standing.py` from untracked to tracked, between two of its
own commands. Two other sessions were active. **Any audit of this repo must pin a
commit first.**
