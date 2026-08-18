# Discrepancy register, 2026-08-19

Method: `directory-provenance-audit` (content identity, never mtime or size) plus
`research-corpus` (query the index before asserting). Every row was checked live at
the time of writing. Nothing was deleted, moved, renamed or edited by this audit.

Scope statement, per the project's own rule that a bare count is wrong: file counts
below are for `/Users/josie/can-it-ford` INCLUDING `.claude/worktrees/`, which is why
they are large. Copies in other clones on this machine are NOT covered and their
absence here is not evidence of absence.

---

## Class A. Citations, resolved against Crossref primary records

| DOI | resolved title | year | verdict |
|---|---|---|---|
| `10.1007/s11069-021-04949-6` | Full-scale experimental investigations on the response of a flooded passenger vehicle under subcritical conditions | **2021** | **MISCITED BY ME** as "Al-Qadami 2022" in the d17-moving dispatch |
| `10.1111/jfr3.12828` | A numerical approach to understand the responses of passenger vehicles moving through floodwaters | 2022 | correct; **numerical**, not experimental |
| `10.3390/su151713262` | Understanding the Stability of Passenger Vehicles Exposed to Water Flows through 3D CFD Modelling | 2023 | correct |
| `10.1111/jfr3.12657` | Hydrodynamic effect on non-stationary vehicles at varying Froude numbers under subcritical flows on flat roadways | **2020** | correct; two prior instructions to relabel it 2021 were both wrong |
| `10.1051/matecconf/201820307003` | Instability Criteria for Vehicles in Motion Exposed to Flood Risks | 2018 | correct |
| `10.1016/j.trd.2017.06.020` | The impact of flooding on road transport: A depth-disruption function | 2017 | correct |

**A1. Three distinct Al-Qadami papers exist, three years, three methods.** The moving-vehicle
one is the 2022 NUMERICAL paper. The full-scale EXPERIMENTAL one is 2021 and its title does
not announce vehicle speed as a swept variable. I attached a vehicle-speed drag claim to the
2021 DOI in a live dispatch; that claim is now marked UNVERIFIED and was corrected to the
session in writing.

**A2. None of these six papers is in the 332-paper corpus index.** `--query "Al-Qadami"`
returns zero. The index cannot answer questions about this project's own closest prior art,
which corroborates the open finding that the corpus is not a superset of the bibliography.
Owned by d14-corpusbib.

---

## Class B. Claim discrepancies between files

| # | discrepancy | evidence | status |
|---|---|---|---|
| B1 | `research-corpus/SKILL.md:11` still asserts "256 are cited nowhere" | CLAUDE.md line 760 WITHDREW it 2026-08-18 as a conflation of *reach* with *cited* | **OPEN, UNOWNED.** The skill is loaded as authority by every session |
| B2 | Criterion 3 names 69.2180 N (nominal); the source comment designates the measured accessor; `r7_jobb_bcfix_ab.py:208-209` calls measured "THE DESIGNATED ACCESSOR" | manifest `:222`, `sphere_heave.py:669-670`, r7-collect grader | owned d11-accessor |
| B3 | `kramer_benchmark.py` `CODE_META` is hand-transcribed, while the doc's line 7 and the module docstring both claim "nothing is transcribed" | reported by d12 from source | owned d12-kramerdata |
| B4 | Settle audit reported as "25 of 25 runs"; actually 22 distinct records, one of them a model-scale truck | reported by d15 from the audit inputs | owned d15-settle |
| B5 | "64 commits ahead of origin/main" omits that it is also **5 behind** (merged PRs #10-#14, tip `c7f0a16`, several touching CI) | `git rev-list --left-right --count` returns `5 64` | owned d16-landing |
| B6 | `assets/DaySkyHDRI002A_1K_HDR.exr` is `required=True` at `render_multigeom_shaded.py:353` with four committed manifests, shipping ungated in a PUBLIC repo; d10-licence's audit returns zero hits for `assets/`, `hdri`, `ambientcg`, `CC0`, `texture` across all 11 sections | reported by d13, verified by grep | **OPEN, UNOWNED. Josie's decision** |
| B7 | `analysis/classify_failure_modes.py:30` still states "G 9.80665, failure_modes.py:14"; live that line is `9.81`, unified by `e495b56` | direct read | **OPEN, UNOWNED, trivial fix** |
| B8 | A handoff asserts `scripts/check_claims.py` Rule C6 is stale because it "asserts 9.80665 appears at TWO sites" | live, `check_claims.py:151` reads "exactly ONE site" and `:164` explicitly forbids the two-site claim | **RESOLVED: the handoff is stale, the checker is correct** |

**B9. CLAUDE.md item 15 SURVIVES, and the way it survives matters.** A file-level grep for
`9.80665` in tracked Python (excluding `third_party/`, `.claude/worktrees/`, `archive/`,
`__pycache__/`) returns FOUR files, which looks like a refutation of "exactly ONE site".
It is not. Exactly one is an ASSIGNMENT (`analysis/viability_dashboard_scaffold.py:11`,
`G = 9.80665`); the other three are a stale comment (B7), a correct historical note, and the
checker rule itself. The claim is true for assignments and false for occurrences, which is
the same scope sensitivity the file documents for `DRIFT_THRESHOLD`. Do not "correct" it.

---

## Class C. File provenance by content hash

| file | copies | distinct contents | verdict |
|---|---|---|---|
| `sphere_heave.py` | 5 | **1** | **NO FORK.** The accessor dispute is purely specification, not divergent code |
| `failure_modes.py` | 35 | 2 | the single `G = 9.80665` variant is in `.claude/worktrees/ctx-census`, a worktree frozen at its branch point. Explicable, not a live fork |
| `openchannel_bc.py` | 14 | 3 | `9a94e247` (x2, r8-persistence) carries ONLY `RecyclingChannelBC`; main carries all three classes; r8-bc-merge carries work in progress |
| `make_phase_space.py` | 70 | 2 | 35 read `FORD' if h <= 0.60`, 35 read `NO-FORD" if haz > 0.60`. **These are the SAME rule inverted.** No operator fork exists inside this repo |
| `sim_standing.py` | 71 | 3 | all three variants carry `settle_frames=8`; the divergence is elsewhere |

**C1. The `openchannel_bc.py` hashes independently confirm d4-bcmerge's refutation.** I claimed
an add/add conflict from two separate writes. The hash shows the short copy is a strict
ancestor state (one class where the tip has three), not a rival lineage. Confirmed by content
identity, which is the signal the audit method says to trust.

**C2. The 0.60 boundary fork is NOT visible from inside this repo.** CLAUDE.md records seven
copies at `h <= 0.60` against two pre-history-purge trees at `h < 0.60`. Inside this repo all
70 copies express the same boundary. The `h < 0.60` copies live in other clones, so this
search cannot see them and does not refute the claim. Say which view you searched.

---

## Class D. Method failures in this audit itself, recorded because they are the pattern

Five checks in one session that could not evaluate but returned an answer anyway:

1. `pgrep -f round5_autodispatch` matched a Claude session whose 12 KB PROMPT quotes the
   script name. No such process existed. It blocked an entire launch wave. Guard now
   subtracts claude PIDs from the match set.
2. `ps -eo pid,command` truncated at terminal width, so a grep for a long command line found
   nothing and I read that as "no watcher running". It was running.
3. `git bundle create "$BUN" $REFS` passed sixteen ref names as ONE argument: zsh does not
   word-split unquoted variables. Loud only because git happened to reject it.
4. `while IFS= read -r h path` clobbered `$PATH`, because zsh ties `path` to it. Every
   external command then reported "command not found" while builtins kept working.
5. `grep -rln ... --include=*.py` unquoted: zsh tried to glob `--include=*.py`, the command
   failed, and the pipeline returned **0**. A false zero that looks exactly like a true zero.

Items 3 and 4 are the same zsh property in two costumes, and item 5 is a third. A sibling
session independently hit the identical class in the same hour, comparing two empty strings
and printing agreement. **A check that cannot distinguish "equal" from "could not evaluate"
is worse than no check.**

---

## Recommended next human decisions, none taken by this audit

1. **B6, the ungated HDRI in a public repo.** Josie's call, and it joins the existing licence
   items rather than replacing them.
2. **B1, the stale skill file.** One line, but it is authority for every session that loads it.
3. **B7**, a one-line stale comment.
4. Whether `sphere_heave.py` having exactly one content everywhere changes the urgency of the
   accessor respecification. It should make it easier, not harder.
