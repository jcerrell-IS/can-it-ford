# Session index, SHIP-v3 night, 2026-07-25

What was created this session, where it lives, what its status is, and whether git can see
it. Files were **labelled in place, not moved**: the scripts resolve paths with
`Path(__file__).resolve().parents[N]`, so relocating them would break them.

Desktop snapshot of the same set:
`~/Desktop/CanItFord_SHIPv3_2026-07-25_night/` (see its `00_START_HERE.md`).

Nothing was committed. Nothing was pushed. No pre-existing file was overwritten.

---

## THE GIT EXPOSURE PROBLEM, read this first

Three of the artifacts are invisible to git, and one of them is the primary data output.

| file | git status | why |
|---|---|---|
| `renders/yaris_render_s1/gates_results_both_scenarios.json` | **IGNORED** | `.gitignore:14` `renders/` |
| `renders/yaris_render_s1/gates_both_scenarios.py` | **IGNORED** | `.gitignore:14` `renders/` |
| `data/four_rung_ladder.csv` | **IGNORED** | `.gitignore:10` `data/*` |

`gates_results_both_scenarios.json` is the file every number in the frozen finding and in
Figure 2 is read from, and **git cannot see it.** Right now its only backup is the Desktop
bundle. Decide deliberately: either add a `!` negation for these two paths, or accept that
they are regenerable from the rollouts and treat the generators as the tracked artifact.
Both are defensible. Doing nothing by accident is not.

One thing this rule gets **right**: it also ignores
`renders/yaris_render_s1/common.py`, which is third-party `kks32/mpm-engine` code and must
never be committed. Do not loosen `renders/` without preserving that.

---

## FROZEN, safe to build a poster or a message on

| file | what it is |
|---|---|
| `docs/four_rung_ladder.md` | **The finding.** Section 0 is frozen and every clause is traced to a line number or a JSON field. Also carries the L0 resolution, the two-scenario comparison, the depth-convention sensitivity and citation status. |
| `docs/centre_panel_paragraph.md` | Poster centre-panel and abstract paragraph in plain English, plus the caveats that must survive shortening. |
| `docs/limitations.md` | 10 numbered limitations, L-1 to L-10, each with its establishing artifact. **New file.** |
| `figures/fig2_mass_sensitivity.pdf` and `.png` | Poster centre figure. Vector PDF, white background, legend outside the axes. |
| `renders/yaris_render_s1/gates_results_both_scenarios.json` | 6 rows with `scenario`, `driver` and `physics_recorded`. The data behind everything above. |

## WORKING, correct and reproducible, not the deliverable

| file | what it is |
|---|---|
| `analysis/four_rung_ladder.py` | Generates the ladder CSV, both scenarios, all three depth conventions. |
| `analysis/fig2_mass_sensitivity.py` | Generates Figure 2. Asserts D x V identity at runtime so the figure cannot silently misreport it. |
| `renders/yaris_render_s1/gates_both_scenarios.py` | Generates the gates JSON. Imports `vehicle_params.L1_verdict`, so the authoritative AR&R rule is used. |
| `data/four_rung_ladder.csv` | 6 rows x 34 columns. |

## THIRD PARTY, do not commit, do not redistribute

| file | what it is |
|---|---|
| `renders/yaris_render_s1/common.py` | Copied 2026-07-25 from `vista:/work/11603/jcerrell0629/vista/mpm-engine/examples/common.py`. Krishna Kumar's code. Present only because this Mac has no local clone and `surface_from_cloud` (line 91) is needed for the water isosurface. Currently protected by `.gitignore:14`. Scratch dependency; unnecessary if the render is redone on Vista. |

## PROVENANCE, outside the repo

| file | what it is |
|---|---|
| `~/.claude/handoffs/2026-07-25_CORRECTIONS.md` | 18 corrections, claim / artifact / verdict. Three fix the directive (C10, C11, C16), two fix my own prior output (C13 retracts C7; C18 the Figure 2 layout). |
| `~/.claude/handoffs/2026-07-25_stage1.md` | Stage 1 handoff, items 1-3 addendum, all SELF-CHECK blocks, the Stage 2 blocker record. |

---

## PRE-EXISTING FILES THAT ARE NOW MISLABELLED BY IMPLICATION

Neither was touched. Both need a decision before anything goes to Kumar.

1. **`renders/yaris_render_s1/gates_results.json`** is the **dry-start** run, not a stale
   version of the standing-water run. It records `"large_4wd": {"L2": "FORD"}`, which is
   correct for dry start and wrong for standing water. It reads as though it were the only
   gate output. **Relabel, do not delete.** It was deliberately not overwritten.

2. **`~/Desktop/CanItFord_Kumar_2026-07-25/02_data/SUPERSEDED_dryStart_m1100_summary.json`**
   marks the dry-start run SUPERSEDED. That is not what this session concluded: dry start
   is a real second scenario configuration, not a superseded version of standing water.
   Flagged rather than renamed, since that bundle belongs to an earlier session.

---

## Naming convention going forward

Scenario belongs in the filename, because the same mass under the two drivers gives
different verdicts:

- `*_dryStart_*` for `sim_dump.py` output (`m1100`, `m1609`, `m2337`)
- `*_standing_*` for `sim_standing.py` output (`g64_m1100`, `g64_m1609`, `g64_m2337`)

Never `*_SUPERSEDED_*` for either. Neither supersedes the other. What is genuinely
superseded is the *comparison* between them, which is confounded, per `limitations.md` L-5.
