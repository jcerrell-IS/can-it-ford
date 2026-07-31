# Brief closure: "fix figures, captions, and repo-sync gaps"

Closes out the pasted fix-list brief. That brief was produced by a forensic audit
against a **stale PDF and a stale public repo**, and several of its facts marked
VERIFIED do not survive a live check. This file marks every item terminal so no
pane re-runs dead work.

Verified 2026-07-31 against `overleaf/main@32b0d12`, `origin/main@1767d87`,
`main@270005d`. Skills run: `directory-provenance-audit`, `provenance-audit`.
Connectors: GitHub (`get_commit`), Wolfram Language, unauthenticated `curl`.

---

## Status table

| Brief section | Status | Evidence | Reproduce |
|---|---|---|---|
| §1 repo-sync premise | **REFUTED** | `paper/conference_101719.tex` and `overleaf/main:conference_101719_1.tex` have **no common ancestor**. Not an older draft, a separate lineage. 161-line diff. | `git merge-base overleaf/main HEAD` (exits 1) |
| §1 residual | **OUTSTANDING** | `paper/conference_101719.tex` **is** tracked on `origin/main` as a stale parallel draft contradicting the submitted paper. | `git ls-tree -r --name-only origin/main \| grep paper/` |
| §2 "captions baked into pixels" | **REFUTED** | All 7 captions extract as real text from a scratch build of the current remote. | `pdftotext conference_101719_1.pdf - \| grep -oE 'Fig\. [0-9]+\.'` |
| §2 "every figure is a flattened raster" | **REFUTED** | 4 of 7 are true vector PDFs with 0 raster objects. | `pdfimages -list <fig>.pdf` |
| §2 residual | **OUTSTANDING** | Exactly 2 figures are wrongly raster: Fig 3 and Fig 4. Fig 7 is correctly raster. | `pdfimages -list conference_101719_1.pdf` |
| §2d vectors never pushed | **CLOSED** | All 4 `paper/figures_review/` PDFs are md5-identical to `overleaf/main`. Resolved. | see §2d below |
| §3 mass provenance | **CLOSED** | Deck header literally reads `1100 kg`. `1078` never appears as a mass. | see §3 below |
| §4 DRIFT_THRESHOLD citation | **CLOSED** | Table I reads as a solver-internal detector, cites `shah2018` + `xia2014`. Zero "Eq. 6". | see §4 below |
| §5.1 duplicate filename | **CLOSED** | Removed in `bf76b1a` after blob-hash determination. | `git show bf76b1a --stat` |
| §5.2 README FORD counts | **CLOSED** | Line 55 reads 14, 19, 26; recomputed from CSV. | see §5.2 below |
| §5.2 residual | **OUTSTANDING** | README still carries contradictions listed below. | `grep -nE 'SPH\|box proxy\|1390' README.md` |
| §6 brief's own Wolfram claim | **REFUTED** | The advertised "Wolfram re-derivation" missed the defect it should have caught. | see §6 below |

---

## §2 per-figure state, `overleaf/main@32b0d12`

| # | File | Kind | Correct? |
|---|---|---|---|
| 1 | `pipeline_diagram_v2.pdf` | vector | yes |
| 2 | `l0l1_two_rules_v2.pdf` | vector | yes |
| 3 | `L1_three_class_corrected.png` | **JPEG** (misnamed `.png`) | **no**, a categorical verdict plot should be vector |
| 4 | `force_balance.jpg` | **JPEG** | **no**, an analytical plot should be vector |
| 5 | `l2_divergence_real_v2.pdf` | vector | yes |
| 6 | `mass_grid_sweep_v2.pdf` | vector | yes |
| 7 | `l2_render_g64_m1100_f0045.png` | PNG raster | yes, an MPM render is legitimately raster |

Rasters in the built PDF: p3 `1568x560` jpeg 450 ppi; p4 `1568x672` jpeg 450 ppi;
p6 `1541x664` non-jpeg 442 ppi.

Two verbatim captions, refuting the baked-in-pixels claim:

> Fig. 2. L0 (fixed depth threshold) versus L1 (AR&R depth-velocity criterion) across all 70 (depth, velocity) scenarios of data/scenario_sweep.csv.

> Fig. 5. L1 hazard scalar versus coupled L2 simulation, 9 measured conditions from data/l2_results_from_wandb.csv.

### §2d

All four built 2026-07-30 14:47 to 14:55, all 0 raster objects, all md5-identical
to `overleaf/main`. `l0l1_two_rules_v2.pdf` is 103,854 B locally and on the remote,
confirming the earlier byte-match observation and that the push has since landed.

---

## §3 evidence, CLOSED

    yaris-coarse-v1l.key      line 28: $- Version 1l, 1100 kg
    set-yaris-coarse-v1l.key  line 28: $- version 1l, 1100 kg
    combine.key               line 28: $- version 1l, 1100 kg

`1078` matches 1455 times in `yaris-coarse-v1l.key` but **never as a mass**: every
hit is a node ID substring (`2341078`, `2101078`, `2410787`). Zero hits in any `$-`
comment line, zero within a `kg`/`mass`/`weight` context. The paper's phrasing,
which quotes the header string directly, is correct as written.

---

## §4 evidence, CLOSED

Table I, L2 row, `overleaf/main:conference_101719_1.tex:125`:

> L2 & MPM & Genesis rigid-MPM simulation; NO-FORD when lateral drift exceeds 0.05 m. That value is an internal numerical detector for onset of motion, set conservatively above the solver's own displacement noise floor, and is not itself an empirical stability criterion. The sliding physics it stands in for, drag overcoming tyre-road friction on a partially submerged vehicle, is established independently \cite{shah2018,xia2014}.

`grep -cin 'eq\. *6\|equation 6'` returns **0**. No `smith` citation in the L2 row.

---

## §5.1 determination, CLOSED

`directory-provenance-audit` workflow, executed on `docs/`:

- 7 copies exist across the main checkout and 3 worktrees.
- **All 7 hash to one blob**, `71600c4aa7730d5224be6622c9aa15dd46301f48`.
- Both paths on `origin/main` resolve to that same blob, so neither is "newer".
- The paper tex references **neither** filename.
- `docs/POSTER_ASSET_TABLE.md` and `docs/v3_invalidation_status.md` reference the
  clean name; three files referenced the bad name descriptively and are unaffected.

Canonical: `docs/track1_v3_sweep_invalid_hollow_vehicle.md`. Duplicate removed in
`bf76b1a`. `docs/` history files untouched.

---

## §5.2 README

Line 55 reads 14, 19, 26. Recomputed from `data/scenario_sweep.csv`: small 14,
large 19, 4WD 26. **Matches.**

`41dc623` and `e1633a4` already fixed the SPH-variant description, the
`paper_draft.md` supersession notice, the bbox-vs-hull paragraph, and the data
table. **What they missed**, still outstanding:

- L1 in the ladder table is given as the bare `D x V <= 0.60` Large 4WD cap; the
  paper's canonical rule is the joint Small Car rule (depth <= 0.30 **and** D x V <= 0.30).
- "across all three AR&R vehicle classes" overclaims; the hull fails AR&R's length
  criterion for both upper classes, so it is mass-sensitivity on one geometry.
- The bbox paragraph sits **inside** the vehicle table, so the `midsize_suv` and
  `light_pickup` rows do not render as table rows.
- "currently crashing" contradicts "functionally proven" in the same file.
- The Running section documents the Genesis path; paper results are kks32/mpm-engine.
- `data/all_runs_inventory.csv` is documented as primary source but is **untracked**,
  so a fresh clone will not contain it.

---

## §6 the brief's own arithmetic, REFUTED

The brief advertised "a Wolfram Language re-derivation of Fig 4's buoyancy
arithmetic" as VERIFIED. Re-derived independently in Wolfram Language:

| Quantity | Value |
|---|---|
| weight, 1100 kg at 9.81 | **10.791 kN** |
| buoyancy at 0.30 m, spec box 4.30 x 1.70, 0.75 footprint | **16.1350 kN** |
| buoyancy at 0.30 m, measured mesh 4.2826 x 1.7464 | **16.5083 kN** |
| the caption's quoted value | **15.99 kN**, matching neither |
| effective plan area 15.99 implies | **5.43323 m2** (footprint **7.24431 m2**) |
| flotation depth, spec box | 0.200638 m |

15.99 kN is 0.90% below the spec-box model and 3.14% below the measured-mesh model.
It is not a rounding of either. Resolved on the remote by `32b0d12`, which names the
plan area the plotted model actually uses.

**Read future briefs with this in mind:** a VERIFIED marking in that brief was not
reliable. The re-derivation confirmed the arithmetic it chose to check while missing
that the caption's own number belonged to neither candidate model.

---

## Two security findings surfaced during closure, both outside the brief

1. **W&B key, commit `50eff29`.** Purged from branch history by filter-repo
   (2026-07-23) and unresolvable locally, but **GitHub still serves it** at
   `.../commit/50eff29d92ad25eba92387bdf3752ceb1200844f.patch` with no auth. The key
   sits on the deletion line of `analysis/wandb_backfill.py`. Rotation is confirmed
   by hash (exposed and live differ; `~/.netrc` matches live, so it is **not** stale).
   **Open action: revoke the old key on wandb.ai.** Unreachable is not deleted.

2. **Personal-profile content in public history.** `_inbox/LIVE_SESSION_LOG.md` at
   `4db2789` carries 7 ADHD occurrences, and `SESSION_STATE.md` at `ca91b12` flags it
   as "STILL PUBLIC". Both commits are ancestors of `origin/main`. Current HEAD is
   clean, history is not. A path-only scan misses this; the content scan finds it.
   Three further copies under `docs/session_notes/archive/` are gitignored and
   untracked, so they were never public.

`scripts/validate_state.sh` matching `adhd` is a **false positive**: line 5 is a
guard that greps CLAUDE.md for those keywords. `figures/phase_space_interactive.html`
is base64 payload coincidence.
