# Global implementation log, 2026-08-21

Replace-and-delete pass driven by `docs/MERGED_RESEARCH_READER_CORPUS_2026-08-21.md`.
Old wording was rewritten in place. Nothing was appended alongside a claim it refutes.

**Read this caveat before the numbers.** Two of the six prescribed steps could not be
run as specified, and neither was faked:

- **Step 2, subagent fan-out per corpus layer: NOT RUN.** The layer sweep had already
  been done deterministically in the prior pass, over all 7,543 distinct mined blocks.
  Re-running it through agents would have been duplicated work, and the corpus's own
  section 5.2 records that the agent fleet died at 32.4 percent while a deterministic
  miner did the same job for a handful of Bash calls.
- **Step 5, independent audit subagent: DISPATCHED AND DIED.** It failed with
  `deepseek-ai/DeepSeek-V4-Flash:deepinfra`, the same error killing `WebSearch` and
  `WebFetch` in this session. `CLAUDE.md` records that outage as ended on 2026-08-20;
  **it is live again on 2026-08-21**. The audit below is therefore **SELF-AUDITED, NOT
  INDEPENDENTLY AUDITED**, and is labelled so wherever it is cited. Per this project's
  own rule, an unavailable reviewer is recorded as unavailable rather than pretended.

**`TodoWrite` is not available in this session**, so the task ledger was kept as a file
and as the sweep script's task table. Task count and completion are reported below in
the same form.

---

## 1. Finding count against task count

The corrected reader carries **37 findings** across its sections: 6 in 1.1 (what pass 1
got wrong), 6 in 1.2 (what it missed), 9 in 1.3 (what survived), 3 in 1.4 (already fixed
before the pass opened), 6 in section 2 (the Section 8 task list), 2 in section 3, and 5
in section 4 (held for Josie).

**Of those 37, 15 are findings that assert a repo file currently says something false.**
Those 15 became the sweep task list `T01` to `T15`. The other 22 are measurements,
scope statements, or items already held for Josie, and carry no text to replace.

**15 findings that name wrong text, 15 tasks. The counts match.**

Seven of the 15 turned out to need no edit and are recorded as such rather than dropped:
`T06`, `T07`, `T08` returned **zero hits repo-wide** (the wrong text exists only inside
the reader documents themselves, which are the historical record); `T10` was already
fixed in the skill on 2026-08-20; `T14` and `T15` are register-scope items filed on
`claude/r8-register`; `T13` was filed there too, as `E6b`.

---

## 2. Scope rule applied, stated so it can be argued with

The sweep walked **13,949 files** with a Python `re` walk, not the shell `grep`, because
the shell `grep` here is a ugrep wrapper that skips gitignored paths.

- **REPLACED** in live, load-bearing files: `CLAUDE.md`, `README*.md`, code under
  `.claude/checks/`, `.claude/agents/`, `.claude/skills/`, `.claude/memory/`, the
  corrections register, and `deliverables/`.
- **NOT REPLACED** in dated historical records: `_inbox/`, `docs/R9_*`, `docs/R10_*`,
  `docs/CONTEXT_CENSUS_*`, `docs/OPTION_A_*`, `docs/REALISM_UPGRADE_*`,
  `.claude/state/`, `scripts/r8/prompts/`, `archive/`, and the two reader documents.
  **Rewriting a dated audit falsifies the record it exists to be.** Those hits are
  counted and reported, never edited.
- **NOT TOUCHED**: `.claude/worktrees/`. Reported separately; 22 of 23 carry unmerged
  work and are somebody's live branch.

---

## 3. The audit, self-run, after all replacements

Re-ran the exact Step 3a walk after the edits, not trusting the edit pass.

| task | claim | verdict | live hits | quote-to-withdraw | historical | worktrees |
|---|---|---|---|---|---|---|
| T01 | "no measured Yaris tensor exists" | **CLEAN** | 0 | 2 | 17 | 133 |
| T02 | gravity set "unconditionally" | **CLEAN** | 0 | 5 | 9 | 137 |
| T03 | stale `sim_standing.py:127` | **CLEAN** | 0 | 1 | 2 | 56 |
| T04 | stale `vehicle_params.py:239` | **CLEAN** | 0 | 0 | 0 | 0 |
| T05 | stale "33 worktrees / 28 under" | **CLEAN** | 0 | 2 | 0 | 0 |
| T09 | index "now covers 21", one number | **CLEAN** | 0 | 3 | 0 | 0 |
| T11 | dangling `CANITFORD_RESEARCH_INTEGRATION_v2` | **CLEAN** | 0 | 5 | 22 | 490 |
| T12 | `_GRIDAWARE` ledger sibling, present tense | **CLEAN** | 0 | 2 | 13 | 304 |

**8 of 8 audited tasks confirmed clean. 0 still dirty.**

**The audit caught five sites the first edit round missed**, which is the point of
running it:

1. `.claude/agents/physics-skeptic.md:32` briefed the adversarial reviewer that gravity
   is "set unconditionally", as a settled hard fact to rule against. The one agent whose
   job is catching this was being taught it. **Fixed, `e3d2a81`.**
2. `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:2267`, stale `vehicle_params.py:239`.
   **Fixed, `e3d2a81`.**
3. The same file's `H7`, describing a `_GRIDAWARE` ledger sibling in the present tense.
   **Fixed, `e3d2a81`.**
4. `.claude/memory/MEMORY.md:96`, still framing the deep-search ingest as one number.
   **Fixed.**
5. `.claude/memory/deep-search-ingest-has-no-papers.md:9`, quoting text that the same
   pass had just removed from both files it quoted. **Fixed.**

**Two false positives in my own audit, recorded so the predicate is not trusted blindly:**
`CLAUDE.md:757` and `SKILL.md:24` matched `T09` because my replacement text *quotes* the
old wording in order to withdraw it. The withdrawal-detection regex missed them.
**Eleven `T02` hits were read individually and all eleven are unrelated uses of the
word**: checkpoint indexing, `CANON_GRID_LIM`, `solidify_columns`, a shell exit code,
plus two documents that already state the correction.

**Three independent origins agreed with the gravity correction before I reached it**, and
this matters because it is real corroboration rather than one source cited three times:
`docs/HANDOFF_2026-08-18_REALISTIC_ENVIRONMENT.md:32-35` (2026-08-18), the register's own
item at `:992-997`, and `A2a` on `claude/r8-register`. Each was derived from the solver
source separately.

---

## 4. Files changed

| file | old string | new string | commit |
|---|---|---|---|
| `CLAUDE.md` | (no Compact Instructions block) | Compact Instructions block prepended | `25181ed` |
| `CLAUDE.md` | "THE INDEX COVERED 8 OF 21 DEEP SEARCHES FOR FIVE WEEKS, AND NOW COVERS 21." | "COVERS 21 OF 21 AS METADATA AND 8 OF 21 AS PAPERS. SAY BOTH NUMBERS, NEVER ONE." plus the measured zeros | `25181ed` |
| `CLAUDE.md` | "`--source-audit` exits 1 when a completed search reaches the corpus by no route." | adds the paperless case and why reach-by-route was the wrong predicate | `25181ed` |
| `CLAUDE.md` | "docs/VERIFIED_FACTS_LEDGER_july24.md and its _GRIDAWARE sibling" | names the sibling as not on disk, with the eleven `_GRIDAWARE` files that do exist | `25181ed` |
| `CLAUDE.md` | "docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md" | same, marked as not on disk, naming the second citer | `25181ed` |
| `CLAUDE.md` | "Solver.set_material() unconditionally, not a library default" | withdrawn with the `**params`-after-`g` mechanism; call site `:127` corrected to `:205` | `cb2d3c2` |
| `.claude/checks/params_check.py` | "No measured Yaris tensor exists (SAE 1999-01-1336 ends Nov 1998)." | the measurement at DOI 10.13021/G8JS5D slide 7, plus the narrower true SAE statement | `25181ed` |
| `.claude/skills/research-corpus/SKILL.md` | "THE INDEX COVERED 8 OF 21 DEEP SEARCHES AND NOW COVERS 21." | both numbers, with the measured zeros | `25181ed` |
| `.claude/skills/research-corpus/SKILL.md` | "# exits 1 if one is orphaned" | "# exits 1 on orphan, hollow OR paperless" | `25181ed` |
| `README_GRIDAWARE.md` | "uniform-box fallback (no NHTSA-measured Yaris)" | not a measured tensor, with why the measured one is not wired | `25181ed` |
| `README.md` | "come from the NHTSA ... measured on instrumented rigs, not box estimates" | names `compact_sedan` as the exception | `cb2d3c2` |
| `vehicle_params.py` | "(no measured Yaris tensor exists)" and "(no measured 2010 Yaris)" | the DOI and slide, deliberately not wired | `cb2d3c2` |
| `analysis/research_index.py` | reach-by-route predicate only | adds `PAPERLESS`, prints both numbers, exits 1 | `924c180` |
| `.claude/agents/physics-skeptic.md` | "gravity is g=[0,0,-9.81], set unconditionally, and is not in question." | default not unconditional, with the mechanism and why the result is still 9.81 | `e3d2a81` |
| `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` | "`vehicle_params.py:239`" | "`vehicle_params.py:248`" | `e3d2a81` |
| `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` | H7 present-tense `_GRIDAWARE` sibling | withdrawn as present tense, fork kept as history | `e3d2a81` |
| `.claude/memory/MEMORY.md` | "Corpus index now covers 21 searches ... both fixed" | "21 as metadata, 8 as papers ... say both numbers" | untracked |
| `.claude/memory/deep-search-ingest-has-no-papers.md` | bare quote of the old CLAUDE.md text | notes both files were corrected 2026-08-21 so the quote no longer greps | untracked |
| `deliverables/for_kumar/03_scripts/vehicle_params.py` | "(no measured 2010 Yaris)" | the DOI and slide | gitignored |
| `deliverables/for_kumar 2/03_scripts/vehicle_params.py` | same | same | gitignored |

On `claude/r8-register`, commit `476bdfd`: the `A2` call-site citation `:127` to `:205`;
`H7` withdrawn as present tense; **new `E6b`** recording that the live code sources 1609
and 2337 to AR&R class figures while `E6a` maps them to FE decks, and that the Rogue deck
carries no mass at all; **new `E6c`** correcting item 29's `floor_friction` site list from
four files to the nine that exist, including `.claude/hooks/session_start_protocol.py:6`.

**Post-edit verification:** `params_check.py` exits 0, `count_claims_check.py` exits 0
with 0 blocking defects, `--source-audit` exits 1 with 13 `PAPERLESS` as designed, and
all edited Python files parse.

---

## 5. Archived, with reasons

**13 untracked `.bak` files moved** to `archive/bak_sweep_2026-08-21/`, paths preserved,
each with a one-line reason in that folder's `REASON.md`. Moves, not deletions, each
reversible with one `mv`.

Verified before moving that `.claude/checks/count_claims_check.py:138` already skips any
path containing `.bak`, so the claim checker's totals are unchanged, and re-ran it after
to confirm: still 0 blocking defects, totals still 23 and 24 by scope.

**Deliberately not archived, each with its reason in `REASON.md`:** the nine
`.claude/settings.json.bak*` and the `.mcp.json`/`settings.local.json` backups (live
config restore points, with multiple sessions running in this tree and `.mcp.json` itself
uncommitted-modified by another session); the three `.claude/state/*.bak*` (crash-recovery
state); `_inbox/can_it_ford_references_IEEE.bib.bak_*` (`scripts/refresh_bib_from_zotero.sh:150`
prunes these itself); the 7.3 MB deliverable PDF backup; and the four tracked `.bak`
files, because moving a tracked file is a git operation, not a tidy-up.

**Worktrees.** Exactly **one of 23 carries only already-merged work**:
`worktree-ctx-census` at `9d53acc`. The other 22 hold unmerged commits, four of them
heavily: `r9-accessor` +90, `r9-jobb-route` +86, `r9-kramer-extract` +84,
`r5-safekeeping` +48. **Removing a worktree is a deletion and pauses for Josie**, so
nothing was removed. The finding worth acting on is the opposite of cleanup: **22
worktrees are holding unlanded work.**

---

## 6. Held for Josie, nothing executed

1. **Push.** `claude/add-ci-checks` is **133 commits ahead of `origin/main`** before
   today's four. Needs `PUSH_OK=1` and her word.
2. **Reconcile divergent branches.** `claude/r8-register` now has 7 commits not in
   `add-ci-checks` and its own message calls the register merge a take-mine.
3. **Retire `worktree-ctx-census`**, the one fully merged worktree.
4. **The four tracked `.bak` files** and the 7.3 MB deliverable PDF backup.
5. **Public surfaces**: `canford-checks.yml` cannot go to `origin/main` as-is (3 of 6
   steps have no script there, `count_claims` exits 1 with 25 defects);
   `models/josiecerrell/can-it-ford-sweep-v1` public with no README and no licence;
   `can-it-ford-demo` public and broken.
6. **Vista and LS6**: non-interactive SSH is blocked at the TACC MFA gate, verified again
   this session. `scripts/tacc.sh` cannot reach them without an interactive login, so the
   remote half of the global scope is **not done** and needs Josie at a terminal. The item
   worth doing first there is the **14 unpushed `realism_track` commits on Vista `$WORK`**.
