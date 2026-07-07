# Can It Ford — Project File Map

Last updated: 2026-07-07

## 1. Canonical repo

**Path (Mac):** `/Users/josie/can-it-ford`
**GitHub:** https://github.com/jcerrell-IS/can-it-ford (remote `origin`, branch `main`)

This is the only location that should be edited going forward. Everything else below is either archived or lives on a remote system.

## 2. Canonical repo tree

`.git/` and the 70 ephemeral `wandb/run-*/` local-logging subfolders are omitted below for length — they're gitignored and not part of the project's actual content.

```
can-it-ford/
├── .claude/settings.local.json
├── .env
├── CITATION.cff
├── PROVISIONAL_STATUS.md
├── README.md
├── environment.yml
├── qr_github.png
├── wandb_backfill.py            (untracked — newest rewrite, reads data/scenario_sweep.csv)
├── analysis/
│   ├── build_phase_space_plotly.py
│   ├── make_phase_space.py
│   ├── make_phase_space_v2.py
│   ├── plot_abstraction_ladder.py
│   ├── plot_phase_space_live.py
│   ├── viability_audit.py
│   └── wandb_backfill.py        (tracked — earlier version, fixed to read key from env var)
├── citations/
│   ├── ARR table 1 - guidelines and recommendations...png
│   ├── ARR_Project_10_Stage2_Report_Final.pdf
│   └── Smith-Modra-Felder/      (12 screenshots + instability table)
├── data/
│   ├── mu_sweep_results.csv
│   ├── phase_space_results.csv
│   └── scenario_sweep.csv
├── designsafe-staging/
│   ├── MANIFEST.txt
│   ├── data/
│   ├── docs/README_designsafe.md
│   ├── figures/ (5 files)
│   └── scripts/ (3 files)
├── figures/
│   ├── can_it_ford_pipeline_diagram.svg
│   ├── hailuo/ (3 videos + 3 frame images)
│   ├── mu_sweep_friction_invariant.html
│   ├── phase_space.pdf / .png
│   ├── phase_space_poster_figure.png / .svg
│   ├── pipeline_diagram_canva.svg
│   ├── poster_exports/ (empty)
│   ├── qr_codes/ (qr_github.png, qr_gradio.png)
│   ├── qr_github.svg / qr_gradio.svg
│   └── validation.png
├── logs/ (empty)
├── scripts/
│   ├── autopull_ford.sh
│   ├── export_plotly_poster.py
│   ├── gen_scenario_sweep.py
│   ├── log_l2_run.py
│   ├── make_manifest.sh
│   ├── plot_hailuo_comparison.py
│   ├── pull_vista_phase_space.sh
│   ├── smoke/ (genesis_metal_smoke.py, taichi_metal_smoke.py)
│   ├── sync_and_plot.sh
│   └── thresholds.py
├── simulation/
│   ├── can_it_ford_L0.py
│   ├── can_it_ford_L1.py
│   ├── can_it_ford_L2.py        (current L2 script — this is the one that matters)
│   └── can_it_ford_mu_sweep.py
├── tests/
│   └── test_csv_schema.py
└── wandb/
    ├── debug-internal.log
    ├── debug.log
    └── run-*/  (70 local W&B run-logging folders, gitignored)
```

## 3. Duplicate audit + archive outcome

Archive folder: **`/Users/josie/Archive/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07/`**

(Note: the task asked for the archive directly at `/Users/josie/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07`. My tools only have write access to folders you've explicitly connected — `/Users/josie/` itself isn't one of them, but `/Users/josie/Archive/` is, so the archive landed there instead. Drag it up a level in Finder if you want it literally at the home folder root.)

| Original location | Git? | Last commit | Verdict | Archived to |
|---|---|---|---|---|
| `Desktop/NEW_FORD_FILES/can-it-ford` | Yes, same origin as canonical | `5ff4ff8` "add Canva-ready pipeline diagram SVG", 2026-07-01 | **Copy failed — see note below. Original untouched.** | `.../Desktop_NEW_FORD_FILES_can-it-ford` (partial/corrupted, do not trust this copy) |
| `Downloads/NEW_FORD_FILES/can-it-ford` | Yes, same origin as canonical | `5ff4ff8`, 2026-07-01 (identical history to the Desktop copy) | Safe to discard — fully superseded, verified copy in archive | `.../Downloads_NEW_FORD_FILES_can-it-ford` (verified complete, 856/856 files) |
| `can_it_ford` (underscore) | No (not a git repo) | n/a — plain scratch folder, files dated 2026-07-03 | Safe to discard — byte-identical to files already in canonical `data/` and superseded by `analysis/` scripts | `.../can_it_ford` (verified complete, 7/7 files) |

### What Task 1 found, in detail

**Desktop copy and Downloads copy are the same clone.** Both point to the canonical GitHub remote and stop at the same commit (`5ff4ff8`), well before canonical's current HEAD (`6564662`). Neither has any commit the canonical repo doesn't already have.

**Files that exist in the duplicates but not in canonical (uncommitted, local-only scratch files):**
- `paper_draft.md` — a real draft of the abstract/paper ("Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability"). **This does not exist anywhere in the canonical repo or its git history.** Flagged for manual review — you may want to pull this into the canonical repo before writing the final paper, since it looks like real prior work.
- `viability_audit.py`, `README_designsafe.md`, `can_it_ford_L2.py` + 2 older variants, `can_it_ford_mu_sweep.py`, `make_phase_space.py`, `wandb_backfill.py`, `scenario_sweep.csv`, `phase_space_results.csv` — all confirmed superseded by newer versions already living in canonical's `analysis/`, `simulation/`, `designsafe-staging/`, and `data/` folders. Safe to discard.
- Figures (`baseline_comparison.png`, `baseline_comparison_v2.png`, `phase_space_interactive.html`, `phase_space_poster_figure.html`, etc.) and a `gradio_app/` git submodule checkout — all older renders/exports, superseded by what's in canonical `figures/`.

**Security note (unrelated to the duplicate cleanup, but found during the audit):** `wandb_backfill.py` in both duplicate folders contains a hardcoded Weights & Biases API key in plaintext. Digging into canonical's own git history, that same key was committed to the canonical repo too (commit `50eff29`) before a later commit fixed it to read from an environment variable instead. If that commit was ever pushed to GitHub, the key is still sitting in the public history there even though it's gone from the current files. **Recommend rotating that W&B API key regardless of anything else in this task** — I did not touch git history per your instructions, so this is still live.

**`can_it_ford` (underscore) folder:** not a git repo at all, just 6 loose files (2 build scripts, 2 PNGs, 2 CSVs) dated 2026-07-03. Both CSVs are byte-identical to canonical's `data/phase_space_results.csv` and `data/scenario_sweep.csv`. The two build scripts are clearly earlier drafts of what became `analysis/make_phase_space.py`, `make_phase_space_v2.py`, and `build_phase_space_plotly.py` (same core logic, timestamps 2-3 hours earlier the same morning). Nothing unique here.

### The one thing that didn't go cleanly: Desktop copy

Copying the Desktop folder repeatedly failed partway through with "resource deadlock" errors on about 90% of its files — most likely something on your Mac (iCloud Desktop sync, Spotlight, or an app) currently has files in that folder open or locked. **Your original Desktop folder is fully intact and completely untouched** — verified file count, sizes, and zero corrupted files. But the copy attempt left a broken, mostly-empty duplicate sitting inside the archive folder, and my tools don't have permission to delete files on your actual Mac, so I can't clean that broken copy up myself either.

## 4. Other known project locations (reference only — not touched)

| Location | Path / URL |
|---|---|
| LS6 (gsplat, A100) | `jcerrell0629@ls6.tacc.utexas.edu`, `/scratch/11603/jcerrell0629` |
| Vista (Genesis MPM, GH200) | `jcerrell0629@vista.tacc.utexas.edu`, `/work/11603/jcerrell0629/vista/` |
| GitHub | https://github.com/jcerrell-IS/can-it-ford |
| Hugging Face Space | https://huggingface.co/spaces/josiecerrell/can-it-ford |
| Weights & Biases | project `can-it-ford`, tag `l0-l1-pilot` |
| DesignSafe | PRJ-6388 (not yet published) |
