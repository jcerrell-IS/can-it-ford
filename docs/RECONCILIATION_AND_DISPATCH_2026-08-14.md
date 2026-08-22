# Reconciliation and Dispatch, 2026-08-14

Run of the Phase 1-4 meta-prompt against: the `js3.rtfd` bundle (Mac, 55,114 lines
after `textutil` conversion), `claude_export_2026-08-13/` (10 LS6 sessions, 9.7 MB),
`claude_transcripts_export_2026-08-13/` (6 Vista sessions, 1.24 MB), and the
research corpus at `~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/`.

**Method note, stated because it changes how much you should trust this.** Every
git fact below was re-derived live against `/Users/josie/can-it-ford` and, where
marked, against Vista over `scripts/tacc.sh`. No number here is carried from a
session summary or a commit message without a live check, and where a commit
message and live state disagree, both are shown. Transcript content is quoted as
what a session *said*; live checks are labelled `[live]`.

**Three bundles, three machines.** This was not obvious and is worth stating: the
two exports do not overlap. `claude_transcripts_export_2026-08-13/` is **Vista**
(cwds under `/work/11603/jcerrell0629/vista/`), `claude_export_2026-08-13/` is
**LS6** (cwds under `/scratch/11603/jcerrell0629/`), and the RTFD is the **Mac**.
A reconciliation that treated them as one machine would double-count.

---

## PHASE 1, session reconciliation

### Session inventory

| # | Machine | Session / worktree | Branch | Commits | Pushed? |
|---|---|---|---|---|---|
| M1 | Mac | `rtfd-test-phase-1-4-569130` | `claude/rtfd-test-phase-1-4-569130` | 9 | **NO, zero remote** |
| M2 | Mac | `provenance-writer-reconcile-489192` | same | 2 | yes, `1ff79b9` |
| M3 | Mac | `friction-resolution-reconcile-84465d` | same | 2 (+5 merged) | yes, `109ae87` |
| M4 | Mac | `render-realism-vehicle-water-ad1490` | same | 4 | yes, `e22737d` |
| M5 | Mac | `retire-coupling-module-f20ad4` | same | 2 | yes, `b46a6ce` |
| M6 | Mac | `semi-empirical-citations-fcc6f3` | same | 1 | yes, `fb0a48b` |
| M7 | Mac | `orphan-rescue-token-rotate-d72f90` | same + `credential-...-DO-NOT-PUSH` | 1 + 2 | partly, by design |
| M8 | Mac | `warpmpm-continue` | same | 1 new (`4924940`) | **NO** |
| L1 | LS6 | `6d948d88` 04:37-08:31, `canitford_track1b` | main | 4 | yes, all in `origin/main` |
| L2-L10 | LS6 | nine further sessions | n/a | **0** | n/a |
| V1 | Vista | `182b19e6` 04:37-05:15, `can-it-ford-track2-realism` | `track2/coupled-realism-explore` | yes | yes, `origin/track2/...` |
| V2 | Vista | `a891ab3d` / `72edb538` (resume pair, one thread) | main | yes | to `origin/vista-realism-track-2026-08-13` |
| V3 | Vista | `180e63ae` memory/safety config | main | 1 (`0736dc3`) | **NO** |

`a891ab3d` and `72edb538` share a title, a start timestamp of 04:36:35, and a
prompt. `72edb538` is the resumed superset (446 records against 128). They are
**one thread**, not two, and counting them separately would inflate the Vista
side.

LS6 session `6576705a` has **0 records**. It is an empty artifact, not a session.

### Starting beliefs, tested

M1 began by executing three dispatches inherited from a prior Phase 1-4 report.
It tested their premises before acting, which was correct: **three of them were
false.** Recorded in commit `e431877`, re-verified live here.

| Premise as written | Live state | Verified |
|---|---|---|
| Force-coupled path "validated to **+0.035%** vs analytic buoyancy on the real Yaris hull" | The 0.035% is a **residual-acceleration identity**, not a buoyancy validation | `[live]` commit `d8a479f` on `realism-exploration` exists, titled exactly that |
| Two *independent* resolution-dependence findings need reconciling | **One measurement**, written up three times | `[live]` see below |
| Provenance backfill `--write` "still deferred" | **Already run** 2026-08-12/13, all 32 manifests | `[live]` `100242d` body records the timestamp `2026-08-13T00:03:08` |

**On the +0.035%.** `d8a479f` shows `dynamic_body.py:207` integrates
`dv = J/(M + m_add) + g*dt`; setting `dv = 0` rearranges to `J/dt = M*g` exactly,
so `Fz_err_pct` **is** `100*a_z/g`, verified to machine precision on all 8 runs,
max `|diff|` 1.4e-16. It certifies the body came to rest. It does not show the
fluid reproduces Archimedes. The non-circular number from the same commit is
settled displacement against the 1.100 m3 the hull's mass requires: **+2.4 /
+16.9 / +26.6 %** (band = dx) and **+10.7 / +16.9 / +22.1 %** (band pinned),
monotone and **worsening** with refinement. `[live]` I confirmed `0.035` appears
nowhere in `docs/`, `analysis/` or `simulation/` as a buoyancy figure.

**On the "two findings".** `[live]` I tested this independently of M1's
conclusion and reached the same answer by a different route, with one correction
to M1's evidence. M1 and register item 18 say the two findings are "one finding
in one commit `ed8bf8e`". `ed8bf8e`'s commit **body** does tabulate the sweep
(`rs_silverado_g64` 6.9669, `g96` 1.8105, `g128` 1.5557), so that is right. But
the same table also appears in `docs/SESSION_TRACK1B_2026-08-13.md:233`, which
was added by a **different commit**, `b62d554`, 44 minutes earlier. So the
measurement appears in **three** places (two commits plus one CSV), not one.
This strengthens item 18 rather than weakening it: three write-ups of one
measurement are still one source. But "one commit" is the wrong phrasing and
should be corrected to "one measurement".

### A. Unpushed work, by branch, with exposure

`[live]`, tested with `git rev-list <branch> --not --remotes=origin`, which is
the only test that distinguishes "no upstream branch" from "content exists
nowhere on the remote".

| Branch | Orphan commits | Exposure |
|---|---|---|
| **`claude/rtfd-test-phase-1-4-569130`** | **9** | **SEVERE. Single filesystem, no remote, no bundle.** |
| `warpmpm-continue` | 1 (`4924940`) | Moderate. Other 5 commits are on `origin/warpmpm-continue`. |
| `claude/credential-exposure-2026-08-13-DO-NOT-PUSH` | 1 (`253b904`) | Deliberate. Repo is public; must not be pushed. |
| `claude/warpmpm-gravity-provenance-435363` | **0** | **None.** All 3 commits reachable from `origin/warpmpm-continue`. |
| Vista `$WORK/can-it-ford` | 1 (`0736dc3`) + 11 dirty | Moderate. `$WORK` is not a remote, allocation expires 2026-09-30. |

**The severe one, in detail.** `claude/rtfd-test-phase-1-4-569130` carries 9
commits and **29 tracked artifact paths** that exist on no remote:

- `a6e42c1`, which **answers register Section J item 15**, the project's own
  "single highest-value open item: RUN THE CANONICAL SET AT g128".
- `data/g128_canonical_2026-08-13/` with `metrics.csv` and `summary.json` for
  `canon_g128_m1100`, `m1609`, `m2337`, plus `00_provenance.txt`.
- `analysis/classify_g128_canonical.py` and its output CSV.
- Register items **17, 18 and 19**, which exist on no other branch. `[live]`
  confirmed: `grep` for them in main's register returns 0.

The artifacts were force-added past `.gitignore:10` **specifically because**
register item 16 records six canonical margins becoming permanently unverifiable
when job 866887 overwrote the g48/g96 run directories on 2026-07-26 with no
tracked copy anywhere. **The exact failure mode item 16 documents is currently
live again for this new data**, one laptop disk away from repeating.

**Also unpushed and untracked, not on any branch:** `[live]`
`/Users/josie/can-it-ford/docs/CREDENTIAL_EXPOSURE_2026-08-13.md`, 118 lines,
md5 `2bbd337f`. This is a *different file* from the 268-line version
(md5 `727cc81b`) committed on the DO-NOT-PUSH branch. One of the two is unsaved
work, and nothing identifies which.

**Resolved since the commit messages were written, and now stale.** M1's commit
`68e4a30` states "Vista's ... is 12 ahead / 173 behind origin/main. The 12 are
the realism_track series `1e4c6d5` through `4b38aa3` ... they exist on one
filesystem." `[live] 2026-08-14`: Vista is now **1 ahead / 5 behind**, and
`1e4c6d5` and `4b38aa3` **no longer resolve on Vista at all**. This looked like
loss. It is not: both are on the Mac, and `origin/vista-realism-track-2026-08-13`
= `4b38aa3` with **12 commits ahead of main**, and
`origin/track2/coupled-realism-explore` = `3e66d8a`. The work was pushed and
Vista was then re-synced. **The memory file `vista-unpushed-realism-commits.md`
and commit `68e4a30` are both stale on this point and should be corrected.**

### B. Resolved errors, with before, after, and the fixing commit

| Before | After | Commit |
|---|---|---|
| "+0.035% is a buoyancy validation" | Residual-acceleration identity; may not be cited as agreement with Archimedes | `d8a479f` |
| "Two independent resolution-dependence findings" | One measurement, three write-ups | `ed8bf8e` body + register item 18 |
| "Provenance `--write` still deferred" | Already run on all 32 manifests | `100242d` |
| `run_provenance.py` dirty, "ownership unclear", "prior session's unrelated work" | **Not ambiguous**: tracked, added by `6d6544f` on the same branch, diff is a coherent continuation | `4924940` |
| Coupling note: "no force is ever formed", "no torque ever computed" | **Falsified.** `mpm_solver_warp.py:887 _apply_rigid_restitution` runs at `:1362`, applies normal impulse `:960` and Coulomb friction impulse `:975`, increments `v_cm`/`omega` at `:963-964`/`:976-977`. Live in all 17 runs via `restitution=0.05` | `b46a6ce` |
| Vista's 12 realism_track commits exist on one filesystem | On `origin/vista-realism-track-2026-08-13` | `[live]` |
| LS6 `trimesh` missing, blocking `sim_standing.py` | Installed with `--no-deps` in session L1 | LS6 transcript |
| `G = 9.80665` vs `9.81` fork | Unified to 9.81, stores regenerated, verdicts byte-identical | `6ea4329` |
| CLAUDE.md item 3 floor-friction cite `:132-137` "should be `:210-211`" | **Repoint REFUSED on evidence.** Gated driver is sha256 `5215c38b`, 389 lines, and `:132-133` IS its floor plane. The 2026-08-13 "fix" had already propagated `:210-211` into `rung_e_floor_friction.py`; reversed | `109ae87` (D8c) |
| 33 citations across 18 files | main's `e495b56` silently repointed them onto real but wrong lines; 28 of 33 restored, 5 listed for owners | `109ae87` (A6b) |

### C. Still-open, self-flagged, not fixed anywhere in the bundle

1. **Register item 15 is still OPEN with scope narrowed.** `a6e42c1` ran the
   direct test for 3 of 17 canonical configurations. In its own words: *"all
   three stay SLIDE. The Silverado flip does not reproduce on the Yaris mass
   sweep. SCOPE, stated every time: 3 of the 17 canonical configurations. The 3
   sweepD and 5 sweepV runs, including the only STUCK run, have no g128
   counterpart."* The finding is the **margin**: `g128_m2337` has
   `margin_frames` **0**, `k_crit` moves 0.8721 to 0.9759, so the weakening
   needed to flip falls from 12.8% to **2.4%**.
2. **A gate fails on the arm with the largest number.** `canon_g128_m1100`
   fails P-2 at passthrough **0.11159** against the 0.10 limit, reproduced at
   0.11155. That is the +76.3% arm. Containment-failed, not a result.
3. **The confound is cleared one way only.** Realized depth is exactly invariant
   at 0.2944294473 across grids, but `wall = 4.0*dx` grows the tank +2.27% per
   side and water volume **+5.64%**, so this is not a pure refinement. Settle is
   fixed-duration, not gated; initial conditions are not matched.
4. **Credentials, third mention and still live.** `[live] 2026-08-14` on Vista:
   `~/.bashrc` mode 700 with 1 matching export line; **`~/.env_mcp` mode 644**
   with 1 matching export line. `253b904` is diagnosis only: *"Nothing rotated,
   nothing revoked, no export line removed."* The exposure is **8 files**, not
   2, including two `.bashrc` backups and three Claude Code transcript artifacts
   containing values verbatim.
5. **Three divergent copies of the corrections register.** `[live]` main **656**
   lines, `claude/rtfd-test-phase-1-4-569130` **681**, and
   `claude/friction-resolution-reconcile-84465d` **817**. This file is declared
   by CLAUDE.md as "the sole authority".
6. **`origin/vista-realism-track-2026-08-13`, 12 commits, never merged or
   reviewed.** Safe on origin, but no decision has been taken on it.
7. **Non-determinism the determinism flag cannot see.** From `a6e42c1`: all six
   `metrics.csv` differ at identical config, node and driver, *while every run's
   `determinism_identical` flag reports True*. The flag does not detect it.
8. **Three findings recorded open in the provenance writer** (`1ff79b9`): the
   mtime guard is unreachable on the already-backfilled population; cross-repo
   reconstruction is not disclosed per manifest; `CANONICAL_YARIS_PLY` resolves
   against the writer's tree rather than `--root`.
9. **Zero manifests carry a recorded `canitford_git_commit`.** All 59 are
   reconstructed. From `1ff79b9`: *"params_check's warning shrank from five
   missing fields to one WITHOUT a single run becoming reproducible."*
10. **Research corpus Sprint 2 is stalled mid-pass.** 5,878 representative
    snippets extracted, zero read-and-verdict done, explicitly awaiting a
    decision on serial versus parallel execution.
11. **`analysis/run_provenance.py --write` on the coupling-validation family has
    still never been run.** `1ff79b9`: *"--write still NOT run."*

### D. Dangerous crossovers

**D-1. The orphaned answer to the project's top open item.** Nine commits and
29 artifacts answering register item 15, on one disk, no remote, while the
register entry justifying their preservation cites the exact prior incident
where equivalent data was lost. Highest-stakes item on this list.

**D-2. Same filename, two branches, different content.**
`[live] docs/LIMITATION_COUPLING_KINEMATIC_VS_FORCE_2026-08-13.md`:

- `claude/warpmpm-flood-vehicle-investigation-1b62fa`, **untracked**, 108 lines,
  md5 `d4b16d19`
- `claude/retire-coupling-module-f20ad4`, **committed and pushed**, 361 lines,
  md5 `ab91df68`

The 361-line version has been through adversarial review and had three blocking
errors corrected (`b46a6ce`). The 108-line untracked version has not, and is
almost certainly the pre-review draft carrying the falsified "no force is ever
formed" framing. **If anyone commits the 108-line copy, a refuted claim
re-enters the repo under a filename that already resolves to the corrected one.**

**D-3. Three-way collision on `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`.**
`[live]` 118 lines untracked in the main worktree, 268 lines untracked in
`orphan-rescue-token-rotate-d72f90`, 268 lines committed on the DO-NOT-PUSH
branch (byte-identical to the second). The repo is **public**. Per memory
`can-it-ford-github-repo-is-public.md`, GitHub served a removed W&B key by SHA
even after `filter-repo`. A careless `git add docs/` on main publishes it.

**D-4. The register's three states.** Any two sessions committing register edits
from different branches will produce a merge whose result nobody has reviewed,
in the file that is supposed to settle disputes. Note `109ae87` already had to
resolve this once by hand and recorded *"neither side was taken wholesale."*

**D-5. Uncommitted `.mcp.json` on main in a shared tree.** `[live]` `M .mcp.json`
adds the `github` stdio server with `"GITHUB_PERSONAL_ACCESS_TOKEN":
"${GITHUB_PERSONAL_ACCESS_TOKEN}"`. The value is an env reference, not a literal,
so this is not itself a leak. The hazard is structural: per memory
`shared-index-sweeps-plain-commit.md`, a bare `git commit -m` from another
session in the main worktree sweeps it in unreviewed. Same applies to the ~22
untracked `renders/yaris_render_s1/*.py`.

**D-6. Three buoyancy-agreement numbers for three different things.** These are
routinely quoted near each other and must never be merged:

| Number | Engine and path | Status |
|---|---|---|
| **7.3 to 7.7%** | warpmpm, SDF collider | Canonical, register-backed |
| **+0.035%** | force-coupled `DynamicSDFBody` | **Not a buoyancy figure at all**, residual-acceleration identity |
| **-105.8% / -39.9%** | Genesis `LegacyCoupler` | **Failures**, Vista V1 |

Vista V1's own document states this defensively: *"No 'X% agreement with
analytic buoyancy' claim is made for Genesis ... neither should ever be quoted
alongside warpmpm's 7.3-7.7%."* The `-39.9%` is *"an artifact of fitting an
acceleration to a decelerating descent and must not be quoted as a buoyancy
agreement figure."*

**D-7. A near-miss already recorded, worth keeping visible.** `109ae87`: a merge
resolved `warpmpm-continue` by **branch name** and silently carried commit
`4924940`, which another live session had just written. Caught by checking the
merge commit's second parent against the SHA. The lesson is already in memory as
`merge-sha-not-branch-name.md`.

---

## PHASE 2, cross-reference against the research corpus

Corpus read: `00_BRIEFING.md`, `00_RESEARCH_MANIFEST.tsv` (115 rows),
`PROGRESS_LOG.md`, `01_Sprint2_Folder_Inventory.tsv`, and the ten facet
directories.

### Open item to research document

| Open item | Document | Bearing |
|---|---|---|
| C-1 register item 15, g128 canonical | `04_.../2026-08-07_report_external-literature-census-findings_CURRENT.md`; CLAUDE.md L-5 (Steffen, Kirby, Berzins 2008) | Steffen 2008 is the citable mechanism for MPM losing convergence under refinement at fixed particles-per-cell. `a6e42c1` records PPC **constant at 8**, which is exactly that paper's case. Already cited in the commit; not yet in the register or the paper. |
| C-1, how to write it up | Al-Qadami 2023 (named in the inherited Dispatch 2, **not present in the corpus index**) | The field's only mesh-independence study for a flood-vehicle result. `[live]` zero hits in the 115-row manifest, so this citation has never been filed and cannot currently be verified from the corpus. |
| C-2 P-2 passthrough gate failure | `01_.../2026-08-02_reference_vehicle-physics-pitfalls_CURRENT.md`; memory `gd64-runs-have-heavy-particle-passthrough.md` | Passthrough of 21-31% was already known on gated runs. 0.11159 at g128 is far better than that yet still fails the 0.10 gate, so the gate, not the run, may be the thing to examine. |
| C-4 credentials | `07_.../2026-07-24_security-note_secrets-env-credential-handling_CURRENT.md` and `..._staged-inbox-risk_CURRENT.md` | Existing project policy documents. `253b904` cross-references `docs/SECURITY_ACTIONS_2026-07-31.md` and records its transferable lesson: **rotation without revocation left the W&B key live. Deleting an export line is not revocation.** |
| D-6 coupling architecture | `01_.../2026-08-07_critical-finding_coupling-defect-force-accessor-route-forward_STALE.md` | Flagged **STALE** in the manifest itself: its numbers (sign inversion, -14.794 m/s2, -9541 N) are retracted. It keeps being cited. The corpus is right and the citation should be dropped, not refreshed. |
| D-6 | `01_.../2026-08-07_report_upstream-kks32-census-findings_CURRENT.md` | Named in the manifest as the likely source of the force-accessor finding. Read this before any further coupling claim. |
| C-5 register divergence | `07_.../2026-07-24_provenance-note_claude-md-provenance-tracking_CURRENT.md`, `..._worktrees-and-backup_CURRENT.md` | Pre-existing project guidance on exactly this hazard, written 2026-07-24, never operationalized into a check. |
| Citation hygiene generally | `04_.../2026-07-07_perplexity-report_drift-threshold-citation-research_CURRENT.md` | Directly relevant to the DRIFT_THRESHOLD count saga, which CLAUDE.md records moving three times in one day. |

### The three vehicle classes, assembled from the corpus and verified live

This is the single largest block of already-paid-for research sitting unused. All
three cited classes have a converged, watertight, sha256-anchored hull, and a
render path that can place it correctly. Nobody has run them together.

| AR&R class | Vehicle, source | Converged hull | Volume | rho | Mass and its provenance |
|---|---|---|---|---|---|
| `compact_sedan` | 2010 Toyota Yaris, NCAC | `yaris_coarse_v1l_watertight.ply` | 3.542739 m3 | **310.494** | **1100 kg**, deck header line 28 |
| `midsize_suv` | 2020 Nissan Rogue, CCSA | `rogue_g96_pd8_coarse_watertight.ply` sha `c0b778e2...06c310b2` | **4.9503 m3** | **317.4** | 1571.3 kg **web-sourced only, the deck states no mass**; AR&R reference 1609 kg |
| `large_4wd` | 2007 Chevrolet Silverado, CCSA | `silverado_g96_pd8_coarse_watertight.ply` sha `46fba11e...f7d466d7f9` | **7.9621 m3** | **285.1** | **2270 kg**, deck header line 28; the multigeom run used **2337 kg**, recorded in its own `summary.json` as `mass_source = "AR&R large_4wd class figure (gates_both_scenarios.py:23)"` |

Corpus facet 02 holds the three mesh READMEs. `~/can-it-ford-meshes-qualified/`
holds obj and stl exports of all three plus `MANIFEST.md` and six `phase*.json`
qualification stages.

**This partly closes CLAUDE.md item 10.** That item says 1609 kg and 2337 kg
"have no source in `vehicle_params.py`", which remains true, but both now have a
source elsewhere: 1609 is the Rogue AR&R reference mass per the mesh README, and
2337 is the AR&R `large_4wd` class figure per `gates_both_scenarios.py:23`. The
correct statement is that they are AR&R **class** figures, not vehicle deck
masses, and the two are not interchangeable.

**Six traps that will silently ruin a three-class result.** Every one is
already-measured project knowledge, and every one is easy to walk into.

1. **Do not use anything in `vehicle_meshes/candidates/`.** By sha256 those two
   files are duplicates of pool files, and they are the **two worst hulls by
   volume convergence**, 47.5% and 31.1% below converged, giving densities of
   **605 and 415.6 kg/m3**. They were selected on `euler_number` closest to 2,
   which selects for coarseness, which erodes volume, which feeds buoyancy
   directly. `candidates/SUMMARY.md` printed those densities and still called
   them plausible.
2. **`euler_number` cannot be a gate on this geometry at all.** The canonical
   Yaris sits at **-442**. Rank hulls by distance from converged volume.
3. **Fixed `n_grid` is NOT fixed resolution across vehicles.** `grid_lim`
   follows the loaded hull's extent, so at `n_grid` 96 the cell size is Yaris
   **0.0981**, Rogue **0.1088**, Silverado **0.1361**, and the realized water
   depth differs too. A cross-vehicle run at one `n_grid` is neither the same
   resolution nor the same depth, and must never be described as either.
4. **The mesh pipeline is not bit-reproducible.** Same effective arguments give
   different sha256, and at g96 even different topology (72520 vs 72524 faces).
   Cite the **sha256 of the artifact**, never the command. Do not regenerate a
   shipped hull to "verify" it; you will get a different file and it proves
   nothing.
5. **Decimate with Open3D, never trimesh.**
   `trimesh.simplify_quadric_decimation` breaks watertightness on the canonical
   Yaris at **every** level from 320k to 10k, producing 49 to 172 non-manifold
   edges. Open3D 0.19.0 preserves watertightness and genus (euler stays -442).
6. **Watertightness does not propagate into the sim.** Register E2:
   `FloodScene vehicle.py:162` samples the mesh down to 60,000 surface points
   before solidifying.

**The literature that makes this a contribution rather than three more runs.**
CLAUDE.md addendum A-3: Smith, Modra and Felder 2019; Martinez-Gomariz et al.
2017; and Arrighi et al. 2015 jointly establish that buoyancy, drag and lift
lever arms, and sliding/float/roll thresholds depend on **displaced volume,
underbody shape, wheelbase, track and CoM, not mass alone**. The three hulls
above differ in displaced volume by **2.25x** (3.54 to 7.96 m3) while their
densities span only 285 to 317 kg/m3, which is exactly the regime where a
mass-only account and a geometry-aware account diverge. A-3 also notes the
compounding defect that the geometry governing the thresholds **is not gated at
all**. Allen et al. 2003, SAE 2003-01-0966, gives a citable provisional CoM and
inertia regression by class, flagged in that paper as provisional, not
validation.

**And the thing not to do with it.** CLAUDE.md item 4 is explicit: do **not**
wire `inertia_kg_m2` or `cg_height_m` into the solver. The solver already
computes a better tensor from the real hull particle cloud
(`kernels/mpm_solver_warp.py:859-871`); the box tensor overstates every
principal moment by +16.3 to +26.1% because the hull fills only **33.2%** of its
own bounding box, and the documented axis convention is transposed relative to
the gated scene. The free result worth reporting instead is that the measured
cloud CG sits 0.6312 m above the floor, below bbox mid-height, so the no-topple
result is **conservative**.

### Research findings sitting idle, not operationalized anywhere

1. **The corpus's own Sprint 2 is the largest.** 14,633 files checksummed,
   5,928 clusters, 5,878 representative snippets extracted, and **zero** read
   and given a verdict. It is stopped waiting on a serial-versus-parallel
   decision. Highest-leverage because the extraction cost is already paid.
2. **The `refs.bib` cluster is unresolved and a live correctness risk.** The
   corpus found **three distinct versions across six locations**. Per memory
   `overleaf-tex-is-canonical.md`, the paper builds from Overleaf, so
   `deliverables/paper/overleaf/refs.bib` is the default, but the corpus
   explicitly says confirm before treating the others as stale. Meanwhile
   `docs/PENDING_BIB_ENTRIES_2026-08-13.md` was added by `c4aea86` on a
   *different* branch, and `b46a6ce` had to fix a **BibTeX key collision**
   (`akinci2012` already used for a different 2012 Ihmsen/Akinci paper, renamed
   `akinciN2012coupling`). Nobody is reconciling bibliography across branches.
3. **Kramer 2016 (doi:10.1016/J.IJDRR.2016.04.003) and Azhar 2026
   (doi:10.1111/jfr3.70181) on watertightness**, per CLAUDE.md addendum A-4,
   are paired and confirmed but explicitly **must not** be paired with the
   `solidify_watertight` fix until register E2 resolves, because
   `FloodScene vehicle.py:162` samples to 60,000 surface points before
   solidifying, so watertightness does not propagate.
4. **Allen et al. 2003, SAE 2003-01-0966** (CLAUDE.md A-3) gives a citable
   provisional CoM/inertia regression by class. Untouched, and it bears on the
   two unsourced masses (1609, 2337) in the mass sweep.
5. **The capability inventory has drifted.** The corpus lists `.claude/hooks/`
   as 14 files and notes `stop_signal_and_check.sh` is absent. `[live]` the LS6
   session fires `stop_signal.sh`. Different name, so the corpus's "worth a
   quick confirm" is still open.

### Where a research document loses to a direct measurement

The inherited Phase 1-4 report is confidently written and **three of its
load-bearing premises are false**, each refuted by a direct code read or a live
git check (see Phase 1). Per the meta-prompt's own rule, the direct measurement
wins. The relevant discrepancy to record: that report was produced against a
capture it *itself* flagged as containing a duplicated block, and register item
18 identifies that duplication as the likely cause of the "two independent
findings" error. **A duplicated transcript is a citation-inflation machine.**

---

## PHASE 3, angle check, all six lenses

**Physics and validation.** The composite experiment is still the gap, but it is
now a *different* gap than the inherited report described. That report proposed
combining a "validated force-coupled path" with the friction result. There is no
validated force-coupled buoyancy path: the +0.035% is an identity, and Genesis
failed outright. The real open cross-check is narrower and cheaper: **register
item 15 at the 8 configurations that have no g128 counterpart** (3 sweepD, 5
sweepV, including the only STUCK run). Second, unexamined by anyone: the
`+5.64%` water-volume growth from `wall = 4.0*dx` means the g96-to-g128
comparison is not a pure refinement, and nobody has run it with the tank held
fixed.

**Software engineering and reproducibility.** Two findings nobody has acted on.
First, `determinism_identical` returns **True on six runs that differ**, so it is
a check that cannot fail, in the same class as register item 6's observation
about G-3. Second, **zero of 59 manifests carry a recorded
`canitford_git_commit`**, so `params_check`'s presence gate improved while
reproducibility did not change at all.

**Literature positioning and novelty.** This lens **inverts** relative to the
inherited report, which proposed strengthening the novelty claim because
+0.035% is tighter than 7.5%. That comparison was invalid. The genuinely
citable contribution moved elsewhere: the project now has a **resolution-
dependent verdict flip** (Silverado SLIDE to STUCK between g96 and g128) plus a
canonical arm at **`margin_frames` 0**, with Steffen 2008 as the mechanism and
PPC constant at 8 matching that paper's case. That is a real, defensible,
negative-result contribution, and it is written in commit bodies and one
register item, nowhere in the paper.

**Visualization and communication.** This is the lens with the largest gap
between what is possible today and what exists, and it is now fully unblocked.

*What is already built and pushed*, on `claude/render-realism-vehicle-water-ad1490`
(`e22737d`, 1,949 insertions across 6 files):
`analysis/vehicle_mesh_transform.py` loads the real qualified `.ply` and places
it using the tracked `com` and `R` from `rigid_state()`;
`analysis/flood_water_optics.py` replaces a brute-force multiplier with an
SSC-driven Beer-Lambert coefficient with nine real citations;
`analysis/make_hdri_cache.py`; and a heavily extended
`analysis/render_multigeom_shaded.py`.

*Why the current renders look wrong, in that work's own words*: the rogue-hull
render "marching-cubes an isosurface from 9135 rigid particles, because the
render script never reads a `.ply`. That's why the car reads as an
unrecognizable blocky shape." That is called out as **the single
highest-leverage fix, and it does not touch physics.** The registration is
already solved and verified against `g64_yaris_regression`: yaw 90 degrees,
because the body long axis lies on **body Y** while the mesh long axis lies on
**mesh X**, with `t[0]` sitting 0.5948 m below.

*What is honestly not yet derived*, stated by that work rather than discovered
later: the attenuation-coefficient-per-mg/L slope is **tuned for visual
plausibility**, not read off a published regression; the clear-water and
sediment RGB values are a qualitative color consistent with the cited spectral
peaks, not a colorimetric conversion; and `floor_boost` encodes the direction of
the Brisbane finding but not its magnitude. Stewart, Fox and Harnett (2013,
2014) and Guillen et al. 2000 have the real coefficients, but only abstracts
were reachable that session. **That is a closable gap and it is the difference
between a plausible render and a citable one.**

*Two results still sitting as raw numbers* that would land far better as
figures, both now computable: the `margin_frames` collapse 11 to 10 to 4 across
g48/g64/g96 for m2337, and the Silverado `ratio_slide` 6.97 to 1.81 to 1.56
crossing the joint-condition boundary into STUCK. Neither has a figure.

*And the one nobody has attempted*: a three-class side-by-side at matched
physical conditions. All three hulls are converged, watertight and sha256
anchored; the placement code exists; the optics exist. The blocker is not
capability, it is that no run set exists with the cross-vehicle confounds
controlled (trap 3 above).

**Licensing and provenance.** Nothing new today. The vehicle-mesh CCSA question
is unchanged. One adjacent item does bear on reuse: the corpus records
`.claude/settings.local.json` as matching a credential-pattern filename, opened
by nobody, already flagged in the July master tree. Leave it that way.

**Infrastructure and deployment.** Three, all independent of the physics.
(a) Credentials, item C-4, third mention, `~/.env_mcp` still mode 644 `[live]`.
(b) The Vista `$WORK` allocation expires **2026-09-30** and is not a git remote,
so anything there is on a clock. (c) Per memory
`vista-su-burn-is-idev-not-science.md`, interactive burns 98.5-99.1% of Vista
node-hours and 95 of 184 jobs ended in TIMEOUT, while LS6 is the opposite. The
g128 runs correctly went to LS6. That routing decision should be written down as
a rule rather than rediscovered.

---

## PHASE 4, dispatches

Seven, mutually independent. No two write to the same file or branch, and none
depends on another's output. Dispatches 5, 6 and 7 are the forward push: the
three-class demonstration, the poster-grade visuals, and the citation closure
those visuals need. Dispatches 1 to 4 are the preservation and correctness work
that protects it.

---

### DISPATCH 1, Mac, `claude/rtfd-test-phase-1-4-569130`

```
SCOPE DECLARATION
MACHINE: Mac. WORKTREE: /Users/josie/can-it-ford/.claude/worktrees/rtfd-test-phase-1-4-569130
BRANCH: claude/rtfd-test-phase-1-4-569130 (already checked out there).
MAY WRITE TO: that branch only, and a bundle file under $TMPDIR.
NEVER TOUCH: main; any other worktree or branch; data/all_runs_inventory.csv;
renders/yaris_render_s1/gates_results_all_runs.json; the uncommitted .mcp.json
and untracked renders/*.py in the main worktree (another session's, unreviewed);
docs/CREDENTIAL_EXPOSURE_2026-08-13.md anywhere (Dispatch 3 owns it).

WHERE THIS THREAD LEFT OFF
Nine commits sit on this branch and are reachable from NO remote ref. Verified
with: git rev-list claude/rtfd-test-phase-1-4-569130 --not --remotes=origin
They are e431877, 5ca6c6b, 68e4a30, a6e42c1, then f2cdbeb, 9ddd648, 53d54e3,
8182719, 658ecfa (five "Preserve g128/g96 run artifacts" commits).
a6e42c1 answers register Section J item 15, the project's own stated single
highest-value open item. It also carries 29 tracked paths including
data/g128_canonical_2026-08-13/{canon_g128_m1100,m1609,m2337}/{metrics.csv,
summary.json}, analysis/classify_g128_canonical.py, and register items 17, 18
and 19, which exist on no other branch (grep for them in main's register
returns 0).
The session that made them stated: "Nothing was pushed; the standing rule
requires your confirmation, and .git/hooks/pre-push needs PUSH_OK=1."

WHY THIS IS URGENT, NOT HOUSEKEEPING
Those artifacts were force-added past .gitignore:10 precisely because register
item 16 records six canonical margins becoming permanently unverifiable when
job 866887 overwrote the g48/g96 run directories on 2026-07-26 with no tracked
copy anywhere. The failure mode item 16 documents is live again right now.

RESEARCH FINDINGS YOU NEED, DO NOT RE-DERIVE
- Steffen, Kirby and Berzins 2008 is the citable mechanism for MPM losing
  convergence under grid refinement at fixed particles-per-cell. a6e42c1
  records PPC constant at 8, which is exactly that paper's case. Cite it in the
  register entry, not just the commit body.
- Al-Qadami 2023 is named in project notes as the field's only mesh-independence
  study for a flood-vehicle result, and is the precedent for how to write this
  up. It is NOT in the research corpus index (zero hits across the 115-row
  manifest), so treat it as UNVERIFIED until you retrieve it. Do not cite it as
  settled. Scite or Consensus first.
- Register item 17 (on this branch) states the g64 settle gate is
  non-deterministic and that item 15's test "should be run at g96 and above, or
  repeated at several seeds". a6e42c1 complied. Keep that scope statement.

CONCRETE FIRST STEP
1. git -C <worktree> status --porcelain=v1 and confirm clean.
2. Create a backup bundle BEFORE anything else:
     git -C <worktree> bundle create "$TMPDIR/rtfd_g128_$(date +%s).bundle" \
       claude/rtfd-test-phase-1-4-569130
   then verify it with: git bundle verify <file>. Report the path and size.
3. Only then push, explicitly and with the gate:
     PUSH_OK=1 git -C <worktree> push -u origin claude/rtfd-test-phase-1-4-569130
4. Confirm it LANDED with git ls-remote --heads origin, not with the exit code.
5. Re-run the orphan test; it must now return zero commits.

DEFINITION OF DONE
git rev-list claude/rtfd-test-phase-1-4-569130 --not --remotes=origin returns
EMPTY, ls-remote shows the branch at 658ecfa, and a verified bundle exists as a
second copy. Plus one short note in the branch's own docs/ recording that
register items 17, 18 and 19 are still branch-only and need a deliberate merge
decision (do NOT merge them yourself, Dispatch 4 owns register reconciliation).
Correct register item 18's phrase "one finding in one commit" to "one
measurement": the same table also appears in docs/SESSION_TRACK1B_2026-08-13.md,
added by b62d554, 44 minutes before ed8bf8e. Three write-ups, one measurement.
```

---

### DISPATCH 2, Mac, new branch off `main`

```
SCOPE DECLARATION
MACHINE: Mac. Create a NEW worktree/branch: claude/vista-realism-triage-<slug>,
off main.
MAY WRITE TO: that new branch only, and only docs/ within it.
NEVER TOUCH: main; claude/rtfd-test-phase-1-4-569130 (Dispatch 1); the
corrections register (Dispatch 4); Vista's filesystem; any credential file.

WHERE THIS THREAD LEFT OFF
Vista's 12 realism_track commits were reported this week as existing on one
filesystem only. That is now STALE and the correction matters:
  [live] origin/vista-realism-track-2026-08-13 = 4b38aa3, 12 commits ahead of
  main. origin/track2/coupled-realism-explore = 3e66d8a.
  Vista's own clone is now 1 ahead / 5 behind and 1e4c6d5 / 4b38aa3 NO LONGER
  RESOLVE there (it was re-synced after pushing).
So nothing is at risk, but 12 commits are parked on a branch that has never been
reviewed or merged, and commit 68e4a30 plus the memory file
vista-unpushed-realism-commits.md both still say they are unpushed.

WHAT THIS THREAD IS FOR
Produce a merge/park/discard recommendation for those 12 commits, per commit,
with evidence. Do not merge anything.

RESEARCH FINDINGS YOU NEED
- track2/coupled-realism-explore carries track2_realism/FINDINGS_TRACK2_2026-08-13.md,
  the Genesis LegacyCoupler result. It is a FAILURE, not a validation:
    F_analytic 5022.7200 N, F_measured second half -291.6208 N, ERROR -105.8060%
    free body: sank 0.887500 -> 0.687123 m, a_fit +1.9857 vs a_ideal +9.8100,
    reported as -39.879%
  That document states in its own words that no "X% agreement with analytic
  buoyancy" claim is made for Genesis, and that neither number "should ever be
  quoted alongside warpmpm's 7.3-7.7%". The -39.9% is "an artifact of fitting an
  acceleration to a decelerating descent". Preserve that framing exactly.
- THREE buoyancy numbers exist for three different things and must never be
  merged: 7.3 to 7.7% (warpmpm SDF collider, canonical), +0.035% (NOT a buoyancy
  figure, it is a residual-acceleration identity, see commit d8a479f), and
  -105.8% / -39.9% (Genesis, failures).
- Register J1a records that the 7.3-7.7% figures come from run_c1_sdf at
  frac 1.0. Vista deliberately ran fraction 1.000 to avoid repeating J1a's
  documented error of scoring a partially submerged case against a fully
  submerged reference. Do not "correct" that choice.

CONCRETE FIRST STEP
git -C /Users/josie/can-it-ford log --oneline main..origin/vista-realism-track-2026-08-13
then, for each of the 12, read the full body with --format=%B and classify:
already-superseded-on-main / merge-candidate / exploratory-park / retraction.
Two of the 12 are explicit retractions per 68e4a30; find them and say what they
retract.

DEFINITION OF DONE
docs/VISTA_REALISM_TRIAGE_<date>.md on your new branch, one row per commit with
a recommendation and the evidence for it, plus an explicit correction notice
that 68e4a30 and the memory file are stale on the "one filesystem" claim.
Committed to your branch with explicit paths. No merge performed, no push to
main.
```

---

### DISPATCH 3, credentials, Mac plus remote read-only

```
SCOPE DECLARATION
MACHINE: Mac, driving Vista and LS6 read-only via scripts/tacc.sh.
BRANCH: claude/credential-exposure-2026-08-13-DO-NOT-PUSH (exists, 2 commits).
MAY WRITE TO: docs/CREDENTIAL_EXPOSURE_2026-08-13.md on that branch ONLY.
NEVER: push this branch (the GitHub repo is PUBLIC); print, echo, log or commit
any credential VALUE; rotate or revoke anything; delete an export line (it can
lock out a running headless session); touch any other branch.

HARD RULE FOR THIS THREAD
Rotation and revocation are Josie's account actions. You diagnose and prepare;
you do not execute. If you believe a step requires her, write it as an exact
command she can run and stop there.

WHERE THIS THREAD LEFT OFF
Commit 253b904 is diagnosis only, in its own words: "Nothing rotated, nothing
revoked, no export line removed, no credential value printed or logged."
It corrected three premises: LS6's three exports are NOT one token repeated
(lines 122/123 are one value, 124 is a DIFFERENT one, and bash takes the last,
so 122/123 are a dead credential on disk in three files); ~/.bashrc is 0700 on
both clusters, so the real defect is a file the earlier dispatch never named,
Vista ~/.env_mcp at 0644; and the exposure is 8 files, not 2.
[live] 2026-08-14, re-verified for this dispatch, names only, no values read:
  Vista ~/.bashrc   mode=700  matching-export-lines=1
  Vista ~/.env_mcp  mode=644  matching-export-lines=1
Still unrotated. This is the THIRD time it has been raised.

A COLLISION YOU MUST RESOLVE FIRST
docs/CREDENTIAL_EXPOSURE_2026-08-13.md exists in three states:
  118 lines, md5 2bbd337f, UNTRACKED in /Users/josie/can-it-ford (main worktree)
  268 lines, md5 727cc81b, UNTRACKED in worktrees/orphan-rescue-token-rotate-d72f90
  268 lines, md5 727cc81b, COMMITTED on this branch (identical to the second)
The 118-line file is unique and tracked nowhere. Determine whether it is an
earlier draft or independent content BEFORE touching anything. Do not delete it.

RESEARCH FINDINGS YOU NEED
- docs/SECURITY_ACTIONS_2026-07-31.md does NOT mention this exposure (verified,
  zero hits). Its lesson transfers and is the single most important sentence
  here: rotation without revocation left the W&B key live. Deleting an export
  line is not revocation.
- Corpus: 07_Repo_Provenance_and_Corrections/2026-07-24_security-note_secrets-env-
  credential-handling_CURRENT.md and ..._staged-inbox-risk_CURRENT.md are the
  project's own policy documents. Read both before writing remediation steps.
- Memory can-it-ford-github-repo-is-public.md: GitHub served a removed W&B key
  by SHA even after filter-repo. Nothing about this file goes to a remote.
- 253b904 records a measurement artifact worth not repeating: the first
  classifier regex reported ZERO real values on Vista, which was false, because
  the character class died on the opening quote. Matching the variable NAME is a
  different test from matching the VALUE.
- Bounded checks must be reported as bounded: a full recursive grep of Vista
  $HOME (20.8 GB) exceeded the transport timeout and was never completed.

CONCRETE FIRST STEP
Resolve the three-way file collision (diff the 118 against the 268 and say
plainly which content is unique to the shorter one). Then re-verify the 8-file
inventory live, by NAME and MODE only, and mark each row rotated / not-rotated /
dead-credential.

DEFINITION OF DONE
One reconciled docs/CREDENTIAL_EXPOSURE_2026-08-13.md on this branch containing:
the 8-file inventory with live modes as of today, an explicit "unrotated, third
mention" status line, and a numbered, copy-pasteable remediation sequence for
Josie that puts REVOCATION before line-deletion. Committed to the DO-NOT-PUSH
branch with explicit paths. Nothing pushed. The chmod 600 on Vista ~/.env_mcp is
the one action you may propose as a single command, but do not run it.
```

---

### DISPATCH 4, Mac, new branch, register reconciliation

```
SCOPE DECLARATION
MACHINE: Mac. Create a NEW branch claude/register-reconcile-<slug> off main.
MAY WRITE TO: docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md and one new
findings doc, on that new branch ONLY.
NEVER TOUCH: main; claude/rtfd-test-phase-1-4-569130 or
claude/friction-resolution-reconcile-84465d (read them, never write to them);
the uncommitted .mcp.json or untracked renders/*.py in the main worktree;
anything credential-related.

WHERE THIS THREAD LEFT OFF
[live] The register, which CLAUDE.md declares "the sole authority for any factual
claim it covers", exists in THREE divergent states:
  main                                        656 lines
  claude/rtfd-test-phase-1-4-569130           681 lines  (adds Section J 17,18,19)
  claude/friction-resolution-reconcile-84465d 817 lines  (adds D8c, D9, A6b)
Commit 109ae87 already had to reconcile a register conflict by hand once and
recorded "neither side was taken wholesale". Nobody has reconciled all three.

WHAT MAKES THIS DELICATE
The three sets of additions are not redundant, they are complementary and in one
place they interact:
- rtfd branch item 18: the "two independent resolution-dependence findings" are
  ONE measurement. CORRECT ITS PHRASING: it says "one finding in one commit
  ed8bf8e". [live] ed8bf8e's commit BODY does tabulate the sweep, but the same
  table also appears in docs/SESSION_TRACK1B_2026-08-13.md:233, added by
  b62d554, 44 minutes EARLIER. Three write-ups, one measurement.
- friction branch D9: friction (D8) and refinement (J15/J16) break DIFFERENT
  clauses of the same criterion. Friction drops the drift clause outright,
  22.64x over to 0.52-0.58x under, speed still 4x over. Refinement drops
  NEITHER: at Silverado g128 drift is 1.556x and speed 4.087x, both over, and
  triggered_slide is still False because their 3-frame co-occurrence fails.
  They are SEPARATELY SUFFICIENT, NOT SHOWN INDEPENDENT: D8 walked mu at one
  grid, J15 walked grid at one mu, and the 2x2 has never been run.
- friction branch D8c REFUSES a repoint that a 2026-08-13 change had already
  propagated: the gated driver is sha256 5215c38b, 389 lines, and :132-133 IS
  its floor plane, so CLAUDE.md item 3's (:132-137) was correct. If you merge
  the branches carelessly you can silently re-apply the refused repoint.

RESEARCH FINDINGS YOU NEED
- Corpus 07_.../2026-07-24_provenance-note_claude-md-provenance-tracking_CURRENT.md
  and ..._worktrees-and-backup_CURRENT.md are the project's own guidance on this
  exact hazard, written 2026-07-24 and never turned into a check.
- CLAUDE.md's DRIFT_THRESHOLD item is the worked example of why a bare count is
  the defect: 22/23/23/24 are all defensible depending on two independent binary
  scope choices. Apply the same discipline to any count you touch.
- Memory count-check-false-blocks-in-worktree.md: count_claims_check.py reports
  25 blocking defects inside a worktree and 0 in the main checkout, because 7
  declaration-site files are untracked and a worktree cannot see them. Do not
  treat an in-worktree 25 as a real regression.

CONCRETE FIRST STEP
Extract all three register versions to separate files and diff them pairwise:
  git show main:docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
  git show claude/rtfd-test-phase-1-4-569130:docs/...
  git show claude/friction-resolution-reconcile-84465d:docs/...
Produce a three-column table of every item that differs, before merging one line.

DEFINITION OF DONE
A single reconciled register on your new branch, with every item from all three
retained or explicitly rejected-with-reason, item 18's phrasing corrected, and
D8c's refusal preserved. register_integrity.py reports 0 blocking defects.
A findings doc listing every merge decision and its reason. Report, do not fix,
the two main-worktree shadow risks: modified .mcp.json and ~22 untracked
renders/yaris_render_s1/*.py, which a bare `git commit -m` from another session
would sweep in.
```

---

### DISPATCH 5, LS6 GPU, new branch, the three-class demonstration at matched conditions

```
SCOPE DECLARATION
MACHINE: LS6, submitted as BATCH not idev. Per memory
vista-su-burn-is-idev-not-science.md, interactive burns 98.5-99.1% of Vista
node-hours and 95 of 184 jobs ended in TIMEOUT, while LS6 shows 0 batch
timeouts. Vista's allocation also expires 2026-09-30.
BRANCH: new, claude/three-class-matched-<slug>, off main.
MAY WRITE TO: that branch, and a NEW output directory under $SCRATCH.
NEVER TOUCH: main; data/all_runs_inventory.csv;
renders/yaris_render_s1/gates_results_all_runs.json (both are Yaris-only and
stay that way, this is a COMPANION experiment, not an extension of the gated
set, and folding vehicle classes into the canonical store is a human decision);
any existing run directory under renders/ or data/ (register item 16 exists
because job 866887 overwrote run directories and made six margins permanently
unverifiable); claude/rtfd-test-phase-1-4-569130; the render branch (Dispatch 6
owns rendering).

WHAT THIS THREAD IS FOR
Produce the first physically comparable three-class result: compact_sedan,
midsize_suv and large_4wd, on their real converged hulls, with the cross-vehicle
confounds actually controlled. Today no such run set exists, and that absence is
the only thing blocking both the strongest available novelty claim and the best
available figures.

THE THREE HULLS, USE EXACTLY THESE, ANCHORED BY sha256 NOT BY PATH
  compact_sedan  2010 Toyota Yaris, NCAC
                 yaris_coarse_v1l_watertight.ply
                 3.542739 m3, rho 310.494, mass 1100 kg (deck header line 28)
  midsize_suv    2020 Nissan Rogue, CCSA
                 rogue_g96_pd8_coarse_watertight.ply
                 sha256 c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2
                 4.9503 m3, rho 317.4
                 mass 1571.3 kg is WEB-SOURCED ONLY, the deck states no mass;
                 the AR&R reference figure is 1609 kg. Say which you used.
  large_4wd      2007 Chevrolet Silverado, CCSA
                 silverado_g96_pd8_coarse_watertight.ply
                 sha256 46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9
                 7.9621 m3, rho 285.1
                 mass 2270 kg (deck header line 28) is the STRONGEST provenance.
                 The prior multigeom run used 2337 kg, whose own summary.json
                 records mass_source = "AR&R large_4wd class figure
                 (gates_both_scenarios.py:23)". Both are defensible; they are not
                 interchangeable, and docs/SILVERADO_MASS_PROVENANCE_2026-08-13.md
                 shows docs/MULTIGEOM_VALIDATION_2026-08-11.md labels the
                 WEAKEST-provenance figure "primary" and demotes the strongest to
                 mass_alt_kg, inverting the hierarchy. Do not inherit that.

SIX TRAPS, ALL ALREADY MEASURED, DO NOT REDISCOVER THEM
1. Do NOT use anything in vehicle_meshes/candidates/. Those two files are sha256
   duplicates of pool files AND are the two worst hulls by volume convergence,
   47.5% and 31.1% below converged, giving densities 605 and 415.6 kg/m3.
   candidates/SUMMARY.md printed those and still called them plausible.
2. euler_number cannot be a gate here: the canonical Yaris is at -442. Selecting
   on euler closest to 2 selects for coarseness, which erodes volume, which feeds
   buoyancy directly. Rank hulls by distance from converged volume.
3. THE CENTRAL CONTROL, AND THE WHOLE POINT OF THIS DISPATCH. Fixed n_grid is
   NOT fixed resolution across vehicles: grid_lim follows the hull extent, so at
   n_grid 96 dx is Yaris 0.0981, Rogue 0.1088, Silverado 0.1361, and the realized
   water depth differs too. Run the matrix so that dx AND realized depth are held
   fixed across the three vehicles, by choosing per-vehicle n_grid rather than a
   shared one, and REPORT the achieved dx and realized depth per run. If you also
   keep a shared-n_grid arm for continuity with the prior sweep, label the two
   arms distinctly and never average them.
4. The mesh pipeline is not bit-reproducible: same effective arguments give a
   different sha256 and at g96 different topology (72520 vs 72524 faces). Cite the
   artifact sha256, never the command, and do not regenerate a hull to "verify" it.
5. If any decimation is needed, use Open3D 0.19.0. trimesh's
   simplify_quadric_decimation breaks watertightness on this geometry at EVERY
   level 320k to 10k (49 to 172 non-manifold edges); Open3D preserves
   watertightness and genus.
6. Register E2: FloodScene vehicle.py:162 samples the mesh to 60,000 surface
   points before solidifying, so watertightness does NOT propagate into the sim.
   Do not claim a watertight-hull result without saying this.

DO NOT WIRE INERTIA OR CG. CLAUDE.md item 4 is explicit and this is the exact
place someone would be tempted. The solver already computes a better tensor from
the real hull particle cloud (kernels/mpm_solver_warp.py:859-871). The box tensor
overstates every principal moment by +16.3 to +26.1% because the hull fills only
33.2% of its bounding box, and the documented (L,W,H)->(x,y,z) convention is
TRANSPOSED relative to the gated scene, which puts the long axis on Y. A naive
write gives Ixx -69.2% and Iyy +379.2%. Report instead the free result: measured
cloud CG 0.6312 m above the floor, below bbox mid-height, so the no-topple result
is CONSERVATIVE.

RESEARCH FINDINGS YOU NEED, THESE ARE WHAT MAKE IT A CONTRIBUTION
- CLAUDE.md A-3: Smith, Modra and Felder 2019; Martinez-Gomariz et al. 2017; and
  Arrighi et al. 2015 jointly establish that buoyancy, drag and lift lever arms,
  and sliding/float/roll thresholds depend on DISPLACED VOLUME, UNDERBODY SHAPE,
  WHEELBASE, TRACK AND CoM, not mass alone. Note the corpus caveat: Smith/Modra/
  Felder and Arrighi 2015 already appear in the register at adjacent contexts, so
  they are NOT independent support; Martinez-Gomariz 2017 and Allen 2003 are new.
- This run set is the direct test of that claim: the three hulls differ in
  displaced volume by 2.25x (3.54 / 4.95 / 7.96 m3) while their densities span
  only 285 to 317 kg/m3. That is precisely the regime where a mass-only account
  and a geometry-aware account diverge.
- Allen et al. 2003, SAE 2003-01-0966, is the citable provisional CoM/inertia
  regression by class. The paper flags itself provisional; cite it as method, not
  validation.
- CLAUDE.md L-1: the AR&R and Shand thresholds describe a STATIONARY vehicle in
  flow, which is what this setup is. Do not write it up as a scenario mismatch.
- CLAUDE.md L-4: coarse resolution usually OVER-predicts peak hydrodynamic force,
  so over-threshold NO-FORD verdicts are conservative.
- CLAUDE.md L-3: the g64 baseline has 4 particle layers and depth/dx exactly
  2.000, against a rule of thumb of ~10 per flow depth. A limitation, never a
  converged resolution.
- Steffen, Kirby and Berzins 2008 is the citable mechanism for MPM losing
  convergence under refinement at fixed particles-per-cell; PPC is constant at 8
  in this stack, exactly that paper's case.
- Memory l1-l2-divergence-is-class-dependent: the paper's class-free divergence
  zone is already contradicted for 2 of 3 AR&R classes at 0.30 m / 1.5 m/s. Your
  three classes are the natural test of that, and it is currently an open claim.
- Register item 17: no single g64 arm of this ladder is quotable, it is
  non-deterministic at fixed configuration. Run g96 and above, or repeat seeds.
  And do not trust determinism_identical: it reported True on six runs that
  DIFFER. Compare metrics.csv directly.

CONCRETE FIRST STEP
Before submitting anything: sha256 all three hulls at the paths you will actually
read, and confirm they match the digests above. Then compute, for each vehicle,
the n_grid that yields a COMMON dx, and print a table of vehicle, n_grid, dx,
realized depth, depth/dx and particle count. Get that table right before spending
a single GPU-hour; it is the entire experiment.

DEFINITION OF DONE
All three classes run at matched dx and matched realized depth, classified with
the same simulation/failure_modes.classify_timeseries that produced the 17, with
margin_frames and k_crit reported beside every verdict. A CSV and a findings doc
on your branch, each run stamped with hull sha256, job id, node, driver sha256,
achieved dx and realized depth. Use lineterminator="\n" in any DictWriter
(.gitattributes:4 is eol=lf). State plainly whether the class ordering follows
mass or follows displaced volume, in either direction, and write it up the same
way whichever it is. Mark the whole set NON-CANONICAL in its own header. Branch
pushed with PUSH_OK=1 and confirmed with ls-remote, not with the exit code.
```

---

### DISPATCH 6, Mac, off `claude/render-realism-vehicle-water-ad1490`, poster-grade three-class visuals

```
SCOPE DECLARATION
MACHINE: Mac, no GPU needed for the render layer.
BRANCH: new, claude/three-class-render-<slug>, branched off
claude/render-realism-vehicle-water-ad1490 at e22737d (already pushed).
MAY WRITE TO: that new branch only: analysis/ render code, a new figures
directory, and one findings doc.
NEVER TOUCH: main; the solver, any gate, any verdict, any coupling code; the
canonical stores; Dispatch 5's branch (do not wait for it either, see below);
claude/rtfd-test-phase-1-4-569130.

HARD SCOPE RULE, INHERITED AND NON-NEGOTIABLE
Render layer only. Every function here reads already-computed particle positions
and rigid-body com/R state and turns them into colors and mesh vertices. No
verdict, no force, no coupling code, no gate result changes. warpmpm particle
output only, not Genesis, not a re-simulation.

WHERE THIS THREAD LEFT OFF
e22737d landed 1,949 insertions across 6 files and is ON ORIGIN:
  analysis/vehicle_mesh_transform.py   real .ply loading + placement from com/R
  analysis/flood_water_optics.py       SSC-driven Beer-Lambert, 9 citations
  analysis/make_hdri_cache.py          HDRI caching
  analysis/render_multigeom_shaded.py  extended multi-vehicle shaded render
  docs/RENDER_REALISM_2026-08-13.md    530 lines of working
  docs/PYSPLASHSURF_WHEELS_2026-08-13.md
Two later commits corrected the splashsurf attribution against primary source and
retracted an overstated 1.22x. Preserve those corrections.

THE ONE FIX THAT MATTERS MOST, IN THAT WORK'S OWN WORDS
"The rogue-hull render currently marching-cubes an isosurface from 9135 rigid
particles, because the render script never reads a .ply. That's why the car reads
as an unrecognizable blocky shape ... This is the single highest-leverage fix and
does not touch physics."
The registration is ALREADY SOLVED, verified 2026-08-13 against
g64_yaris_regression: yaw 90 degrees, because the body long axis lies on BODY Y
while the .ply long axis lies on MESH X, and t[0] sits 0.5948 m BELOW. Reuse it;
do not re-derive it and do not "fix" the 90 degrees.

USE THE CONVERGED HULLS, NOT THE CANDIDATES
  yaris_coarse_v1l_watertight.ply
  rogue_g96_pd8_coarse_watertight.ply      c0b778e2...06c310b2
  silverado_g96_pd8_coarse_watertight.ply  46fba11e...f7d466d7f9
The two files in vehicle_meshes/candidates/ are the two WORST hulls by volume
convergence, 47.5% and 31.1% below converged. A render built on those shows a
visibly wrong vehicle and implies a wrong displaced volume. Also: the pipeline is
not bit-reproducible, so anchor on sha256 and never regenerate to verify.
~/can-it-ford-meshes-qualified/ carries obj and stl exports of all three plus
MANIFEST.md if you need a non-.ply format.

THE OPTICS GAP YOU ARE CLOSING, AND ITS CITATIONS
flood_water_optics.py is honest about three things it did not derive, and closing
them is what moves this from plausible to citable:
  (a) the attenuation-coefficient-per-mg/L slope is TUNED for visual plausibility,
      not read off a published regression
  (b) the clear-water and sediment RGB values are a qualitative color consistent
      with cited spectral peaks, not a colorimetric conversion
  (c) floor_boost encodes the DIRECTION of the Brisbane finding but not its
      magnitude
The coefficients exist in sources that were abstract-only that session. Pull the
full text via Scite or the library connectors:
  Stewart, Fox, Harnett 2013, DOI 10.1061/9780784412947.167
  Stewart, Fox, Harnett 2014, J. Hydraulic Eng, DOI 10.1061/(ASCE)HY.1943-7900.0000887
  Davies-Colley and Smith 2001, JAWRA, DOI 10.1111/j.1752-1688.2001.tb03624.x
  Martinez et al. 2015, JGR Earth Surface, DOI 10.1002/2014JF003404
    (SPM 5-620 g/m3, reflectance saturation near 100 g/m3, 1 g/m3 = 1 mg/L)
  McKee and Gilbreath 2015, Environ Monit Assess, DOI 10.1007/s10661-015-4710-4
    (real urban storm-flow SSC 1.4-2700 mg/L)
  Brown, Chanson, McIntosh, Madhani, Brisbane River flood plain, Jan 2011
    (SSC increases as depth decreases, an actual flooded-road event)
  Alexandrov, Laronne, Reid 2003, DOI 10.1006/JARE.2002.1020 (six-year mean
    34,000 mg/L, use as physical upper bound only)
  Schneider et al. 2015 and Yang 2012 for the iron-oxide brown/tan mechanism
    (hematite peak 565 nm, goethite 505/435 nm)
If a coefficient still cannot be retrieved, say so and leave the value labelled
tuned. Do NOT quietly upgrade a tuned number to a cited one; that is the exact
failure this project keeps catching.

WHAT TO PRODUCE, RANKED
1. Three-class hero still: Yaris, Rogue and Silverado in the same flood
   condition, real hulls, correct placement, SSC-driven water. This is the image
   the whole project has been unable to make.
2. The two results that exist only as numbers today:
   - margin_frames collapsing 11 -> 10 -> 4 across g48/g64/g96 for m2337, with
     k_crit plotted beside it so the closeness is not mis-scaled
   - Silverado ratio_slide 6.9669 -> 1.8105 -> 1.5557 crossing the joint
     drift-and-speed condition into STUCK at g128
3. An honest caption block for each figure stating engine (warpmpm), hull sha256,
   what is measured versus tuned, and NON-CANONICAL status for anything
   multi-vehicle.

INDEPENDENCE NOTE
You do NOT depend on Dispatch 5. Render against run data that already exists:
data/rogue_silverado_slide_classification_2026-08-13.csv and the multigeom
rollouts referenced in docs/MULTIGEOM_VALIDATION_2026-08-11.md. If Dispatch 5's
matched-dx set lands later, re-render is cheap. Do not block on it.

CONCRETE FIRST STEP
Render ONE frame of the Rogue with the real hull loaded through
vehicle_mesh_transform.py and put it beside the current particle-isosurface
version. That before-and-after is the proof the highest-leverage fix works, and
it takes minutes.

DEFINITION OF DONE
A figures directory on your branch containing the three-class hero still and the
two quantitative figures, each with its honest caption; a findings doc recording
which optics coefficients were successfully retrieved from full text and which
remain tuned; and an explicit statement of whether the stills are poster-grade or
still diagnostic-only, which nobody has yet assessed. Branch pushed with
PUSH_OK=1 and confirmed with ls-remote.
```

---

### DISPATCH 7, no repo, research corpus Sprint 2 and the citations the figures need

```
SCOPE DECLARATION
MACHINE: Mac, no GPU, no repo access needed.
MAY WRITE TO: ~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/ ONLY, and its
_BUILD_LOG/ subdirectory.
NEVER TOUCH: the git repo at /Users/josie/can-it-ford in any way; any file
outside the corpus tree; any original source file (this tree is symlinks, keep it
non-destructive); anything credential-related.

WHERE THIS THREAD LEFT OFF
PROGRESS_LOG.md, last entry: steps 5, 6 and 7 extraction are COMPLETE. 1,477
Sprint-2-only multi-member clusters covering 9,314 files (one representative
each) and 4,401 true singletons were extracted, 5,878 representative reads, zero
read errors, saved to step6_extract_batch1-3.txt and step7_extract_batch1-5.txt.
Step 5 resolved 326 real Sprint-1 duplicates and correctly re-tagged 592
zero-byte matches as empty-file rather than letting them inherit an unrelated
verdict. It is STOPPED, waiting on a serial-versus-parallel decision, with the
extraction cost already paid. That makes it the highest-leverage idle item in the
project.

THE DECISION IS MADE: PROCEED SERIALLY IN BATCHES
Work the extracted snippets in order, appending verdicts. Do not re-extract, do
not re-checksum. Checkpoint to PROGRESS_LOG.md every ~500 snippets so an
interruption costs at most one batch.

FOUR TARGETED QUESTIONS TO ANSWER ON THE WAY, each currently blocking other work
1. THE refs.bib CLUSTER, blocking any bibliography work. The corpus's own Phase C
   found THREE distinct versions across six locations: {6a5958, overleaf_fresh}
   match; {canitford_tex_backup} is its own; {files (3)} is its own;
   {deliverables root, deliverables/paper/overleaf} match and are a third. Per
   memory overleaf-tex-is-canonical.md the paper builds from Overleaf, so
   deliverables/paper/overleaf/ is the default, but confirm before calling the
   others stale. This is live: a BibTeX key collision was caught this week
   (akinci2012 already used for a DIFFERENT 2012 Ihmsen/Akinci paper, renamed
   akinciN2012coupling), and a separate docs/PENDING_BIB_ENTRIES_2026-08-13.md
   exists on its own branch. Produce a definitive table: which version is
   canonical, what each other version uniquely contains, and whether any unique
   entry is cited anywhere.
2. IS Al-Qadami 2023 IN THE CORPUS ANYWHERE? It is cited in project dispatches as
   the field's only mesh-independence study for a flood-vehicle result, and a
   search of the 115-row Sprint 1 manifest returns ZERO hits. Search the full
   Sprint 2 corpus. If it genuinely is not there, say so plainly: a citation
   load-bearing for a planned write-up has no retrievable source on this machine.
3. THE OPTICS COEFFICIENTS, directly unblocking Dispatch 6's figures. Search the
   corpus for full text (not abstracts) of Stewart, Fox and Harnett 2013 and
   2014, and Guillen et al. 2000. Dispatch 6 needs the real
   attenuation-coefficient-per-mg/L regression; without it that coefficient stays
   labelled "tuned" and the render cannot be called citable. Report hit or miss
   with the path.
4. THE THREE VEHICLE-CLASS PAPERS. Confirm whether Martinez-Gomariz et al. 2017
   and Allen et al. 2003 (SAE 2003-01-0966) exist anywhere in the corpus as full
   text. CLAUDE.md A-3 flags these two as the NEW ones (Smith/Modra/Felder and
   Arrighi 2015 already appear in the register in adjacent contexts, so they are
   not independent support). Dispatch 5's contribution framing rests on them.

ALSO FLAG WHEN YOU MEET IT
- 01_.../2026-08-07_critical-finding_coupling-defect-force-accessor-route-forward_STALE.md
  is correctly tagged STALE (its -14.794 m/s2 and -9541 N are retracted) and is
  still being cited elsewhere. List every place in the corpus pointing at it.
- 00_BRIEFING.md says .claude/hooks/ has 14 files and that stop_signal_and_check.sh
  is absent. A live LS6 session fires stop_signal.sh, a different name. Reconcile
  the hook inventory.
- The corpus's Sprint 2 inventory marks 9 folders "cached only, path unverified
  live", including can-it-ford-main (848 files, most recently touched). Re-verify
  those paths live before any verdict that depends on them.

CONCRETE FIRST STEP
Answer questions 3 and 4 FIRST, before any bulk verdict work. They are two
targeted searches, they unblock two other dispatches, and they take minutes
rather than sessions. Then start batch verdicts at
_BUILD_LOG/step6_extract_batch1.txt.

DEFINITION OF DONE
This is explicitly a MULTI-SESSION item; do not fake completion. Done for THIS
session means: questions 1 to 4 answered with the search method stated, at least
1,000 snippets given verdicts appended to 00_RESEARCH_MANIFEST.tsv in the
existing 9-column schema, and PROGRESS_LOG.md updated with an exact resume point
(file and line). Report counts honestly, including how many remain.
```

---

---

# PART II. THE FORKED TRACK, added 2026-08-14

A second, parallel track: a moving vehicle in a realistic environment, benchmarked
against arXiv 2607.00673. It shares no branch, no file and no canonical store with
Part I. Dispatches 8 to 12 below are the fork; 1 to 7 above are unchanged.

## Evidence base added this pass

Four Undermind deep searches (`launch_deep_search`, 2026-08-14) plus an eight-agent
local scan of every research document, transcript and script on this machine.

| Report | Papers | Coverage | Decisive result |
|---|---|---|---|
| Multi-resolution MPM for Large-domain Flooding | 78 | 76% | **No MPM study follows a rigid vehicle with a refinement window through a large domain.** Closest is dynamic AMR for free-surface waves with no vehicle |
| Quantitative MPM Wall Penetration | 16 | 99% | **No paper reports the ~0.93-1.01 dx penetration plateau**, and none gives a defensible minimum cell count across a shallow layer |
| Settling and Force Reporting in Free-Surface Flow | 68 | 91% | **No universal settling threshold exists.** The defensible protocol is transient exclusion plus a demonstrated stationarity test plus correlated-sample uncertainty |
| Moving Rigid Body Free-Surface Validation | 44 | 92% | **No validated vehicle-fording MPM chain exists**, and the records do **not** establish an experimental basis for the 1.5 m/s fording rule |

**Corpus coverage, measured.** The Desktop research corpus indexes 115 files and
indexes **zero** of the Undermind reports and **zero** of the 36 `compass_artifact`
Claude research files. The four Undermind source reports live in `/Users/josie/Downloads/`
except `Trustworthy_AI_Assisted_Scientific_Simulation.md`, which is at
`/Users/josie/Claude/Projects/SCIPE UT Austin baby/REU_Knowledge/`. Two copies of
`Validated_MPM_Vehicle_Water_Coupling.md` exist with identical 60-DOI sets but
different dates and citation-rate fields, so any cit/yr quoted from it must carry
its file date.

## The five findings that define this track

**F1. Self-propulsion is a genuine literature gap, and therefore has no validation
target.** No source in the surveyed literature applies an active propulsive force or
engine torque to a vehicle in a coupled fluid-vehicle flood simulation. Azhar 2023
(10.1111/jfr3.12885), Al-Qadami 2022 (10.1111/jfr3.12828), Al-Qadami 2023
(10.3390/su151713262) and Xiong 2024 (10.1029/2023WR036739) all treat the vehicle as
a passive rigid body under drag, buoyancy and friction, or impose prescribed
kinematics. This is the novelty **and** the risk: validate against the passive and
prescribed-kinematic cases, never claim a validated self-propelled result.

**F2. There is one published precedent for the force balance, and its drive term is
negligible.** Shah et al. 2018, MATEC Web Conf. 203:07003, DOI
10.1051/matecconf/201820307003, is the only source combining a moving vehicle, an
explicit engine driving force, and a buoyancy-reduced normal force:
`F_D = F_RO + F_R + F_DV`, expanded to
`0.5*rho*C_D*A_D*v^2 = F_N*(mu_RO + mu) + F_DV`, with mu 0.3 after Bonham and
Hattersley 1967 for the parked baseline, 0.52 measured parallel to flow, and rolling
mu_RO 0.092. Its measured driving force was 0.0017 to 0.021 N at 1:10 scale, that is
numerically negligible, so it supplies the equation but does **not** constrain a real
traction budget.

**F3. There is a measured, Yaris-specific, depth-resolved traction curve.** Smith,
Modra and Felder 2019, DOI 10.1111/jfr3.12527: a Toyota Yaris at 1045 kg kerb weight
loses rear-axle traction from about 4.5 to 4.7 kN at zero depth to **0 kN at about
0.6 m**; a Nissan Patrol 4WD at 2478 kg falls from about 9.3 to 9.6 kN to **0 kN at
about 0.95 m**. Governing relation `F_F = mu*(W - B - L)`. Measured tyre friction was
0.75 wet and 0.78 dry on concrete; **0.3 was adopted conservatively** for the
published hazard curves. This is a stationary sideways winch pull-test, so it bounds
the traction available and does not validate propulsion.

**F4. The depth-only speed baseline exists and is not a stability criterion.**
Pregnolato et al. 2017, DOI 10.1016/j.trd.2017.06.020:
`v(w) = 0.0009*w^2 - 0.5529*w + 86.9448`, w in mm, v in km/h, R^2 = 0.95, flow
velocity explicitly excluded, 30 cm treated as impassable. It is the correct baseline
to contrast against, labelled driver-control and serviceability, not stability.

**F5. A live contradiction inside one author group, unreconciled.** Al-Qadami 2022
(vehicle **moving** perpendicular to flow) reports critical depth 0.38 m and minimum
depth-times-velocity 0.39 m2/s. Al-Qadami 2023 (vehicle **exposed** to flow) reports
floating at 0.38 m but sliding above 0.36 m2/s. An 8 percent spread between the
moving and stationary framings, which is precisely the distinction this track exists
to study. Do not average them.

**Standing citation warning, applies to every dispatch below.** The Australian
small-car limit is a limiting **still-water depth of 0.3 m**, not a depth-times-velocity
product of 0.3 m2/s. Per ARR Book 6 (Ball et al. 2019) the limits are 0.3, 0.4 and
0.5 m for small car, large passenger car and large 4WD, with velocity capped at
3 m/s. Kramer, Terheiden and Wieprecht 2016 (DOI 10.1016/J.IJDRR.2016.04.003)
independently propose total-head criteria of 0.3 m for passenger cars and 0.6 m for
emergency vehicles. Still-water depth limits must never be conflated with
depth-velocity products.

---

### DISPATCH 8, Mac, PREFLIGHT: three artifact sets exist on one machine each

```
SCOPE DECLARATION
MACHINE: Mac, plus read/write to Vista via /Users/josie/can-it-ford/scripts/tacc.sh.
BRANCHES YOU MAY WRITE TO: claude/moving-vehicle-exploratory-2026-08-11 (existing,
  four uncommitted files), and one NEW branch claude/fork-s3-rescue-<slug> off main.
NEVER TOUCH: main; the canonical stores data/all_runs_inventory.csv and
  renders/yaris_render_s1/gates_results_all_runs.json; claude/rtfd-test-phase-1-4-569130
  (Dispatch 1 owns it); realism-exploration (verified SAFE, see below, do not "rescue" it);
  any credential file (Dispatch 3 owns those).

NOTHING ELSE IN THE FORK STARTS UNTIL THIS IS DONE. Register item 16 exists because
six canonical margins became permanently unverifiable when run directories were
overwritten with no tracked copy. Three artifact sets are in that same state now.

8.1 renders/yaris_render_s3_enhanced/ IS ON ZERO GIT REFS AND IS GITIGNORED.
  git check-ignore -v renders/yaris_render_s3_enhanced/sim_enhanced.py
    -> .gitignore:31:renders/*
  git log --oneline --all -- renders/yaris_render_s3_enhanced/
    -> EMPTY. No ref in this clone contains it.
  The tree holds sim_enhanced.py (36359 bytes), NOTES_2026-08-07.md (17334 bytes),
  four .sbatch files, and results/ with SIX completed run summaries: ctrl_g64,
  enh_g96, enh_g96_c10, enh_g96_real, enh_g128_c10, enh_g128_real.
  ACTION: copy the tree out, then commit it into a NON-IGNORED path on your new
  branch. Do NOT add a .gitignore carve-out under renders/. The walk-down carve-out
  pattern has already gone wrong three times per CLAUDE.md and .gitignore line numbers
  have been wrong three times in one day; re-derive any line number you cite with
  /usr/bin/grep -n, never quote it positionally.

8.2 THE MOVING-VEHICLE WORK IS NOT EVEN COMMITTED.
  git -C /Users/josie/can-it-ford-moving-vehicle rev-parse --abbrev-ref HEAD
    -> claude/moving-vehicle-exploratory-2026-08-11 at feecf5f
  git ls-remote --heads origin | /usr/bin/grep -c moving-vehicle  -> 0
  Four untracked files: analysis/render_moving_vehicle_placeholder.py,
  analysis/render_moving_vehicle_surface.py,
  docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md,
  simulation/moving_vehicle_sdf_exploratory.py
  The branch is not on the remote AND the files are not committed to it. This is the
  seed of the entire fork.
  ACTION: stage the four by EXPLICIT PATH, commit, push. Never git add -A in that tree.
  KNOWN INCOMPLETE, carry it forward: that document has three unfilled placeholders,
  <!--LADDER--> at :143, <!--BOWWAVE--> at :164, <!--COST--> at :205, so its sections
  5, 6 and 8 are unfinished. Section 5 states a negative finding whose supporting
  table is one of those placeholders. Do not cite sections 5, 6 or 8 until filled.

8.3 THE VISTA 6-DOF DRIVER IS UNPUSHED.
  simulation/rigid6dof.py, run_c4_free_sdf in validate_coupling_force.py, and
  tests/test_rigid6dof.py with 25/25 tests passing, exist only at
  /work/11603/jcerrell0629/vista/can-it-ford-track1-6dof at local commit a231a73.
  git ls-remote --heads origin returns 17 branches, none named track1/sdf-6dof-driver.
  (track2/coupled-realism-explore IS present at 3e66d8a.)
  ACTION: recover over scripts/tacc.sh. That script exists, 3627 bytes, executable,
  with a host allowlist for vista/ls6 over ControlMaster sockets and an exit-3 refusal
  list. One survey claimed Vista is unreachable non-interactively because of MFA; a
  live ControlPersist socket contradicts that. TEST IT, do not assume either way. Exit
  255 means the socket expired and one interactive ssh restores it.
  IF BLOCKED: say so plainly and proceed. Dispatch 9 can use DynamicSDFBody instead.

8.4 DO NOT "RESCUE" THE REALISM TRACK. It is already safe and a survey got this wrong.
  git -C /Users/josie/can-it-ford-realism ls-files simulation/realism/ returns all
  nine modules including dynamic_body.py, outflow_deactivate.py, render_water.py; the
  tree is clean; branch realism-exploration is on origin at c4af419, matching local
  HEAD. Spend no recovery effort there.

DEFINITION OF DONE
All three artifact sets reachable from origin. For each: the branch name, the commit
SHA, and ls-remote output proving it landed, not an exit code. A short doc listing
what was recovered, what was already safe, and anything still blocked with the reason.
```

---

### DISPATCH 9, LS6 GPU, the moving-vehicle driver on the warpmpm SDF path

```
SCOPE DECLARATION
MACHINE: LS6, BATCH not idev (Vista burns 98.5-99.1% of node-hours interactively and
  95 of 184 jobs ended in TIMEOUT; LS6 shows 0 batch timeouts; Vista's allocation
  expires 2026-09-30).
BRANCH: new, claude/fork-moving-driver-<slug>, off main.
MAY WRITE TO: that branch, and a NEW $SCRATCH output directory.
NEVER TOUCH: main; renders/yaris_render_s1/sim_standing.py or any canonical driver;
  data/all_runs_inventory.csv; gates_results_all_runs.json; any existing run directory;
  Dispatch 8's branches; Dispatch 10's scene branch.

ENGINE DECISION, ALREADY MADE ON EVIDENCE. USE warpmpm, pinned SHA
544c93dd02cb9c7ead89e1155a62967243244fce, moving-SDF-collider path. Do not switch and
do not re-litigate. The reasons, so you do not repeat the search:
- NOT DualSPHysics: x86-only static libraries, hard aarch64 blocker on GH200.
- NOT Genesis. Six measured failures on the real hull: fixed 0.8 m cube V=0.512 m3
  fully submerged at gd16 gave F_analytic 5022.7200 N against F_measured second-half
  -291.6208 N, error -105.8060%, a CONVERGED WRONG ANSWER; a free body at half water
  density SANK from z 0.887500 to 0.687123 m in 0.64 s; the canonical Yaris hull gave
  -69.3862% buoyancy and ended 0.107 m below start; refinement converges toward ZERO
  force, gd16 to gd32 moving -111.945% to -97.538%; under strict settle the largest
  upward force under any configuration was +712.1 N against a 2511.4 N cube weight and
  a 10790.9 N Yaris weight, so nothing can rise. Genesis 1.1.1 has three couplers and
  only LegacyCoupler supports MPM, with only on/off booleans exposed.
- NOT CPIC, despite the literature recommending Hu et al. 2018 (10.1145/3197517.3201293).
  It has already been evaluated and REFUSED in this repo at
  analysis/verify_cpic_ground_clearance.py: rigid_g2p_accumulate at mpm_utils.py:1370-1412
  gathers grid_v_out with no CPIC masking and cdf_reaction_force is only zeroed and
  read, never applied to a body. Attaching a sheet to the hull blocks its p2g deposits
  while leaving its g2p gather unmasked, which is momentum non-conserving.
- Architecture worth imitating but NOT installing: Canelas et al. 2018
  (10.1016/J.APOR.2018.04.015) coupling DualSPHysics to Project Chrono. Chrono is the
  only stack exposing wheel torque, which is the propulsion hook nobody has used in a
  flood study. Read it for architecture only.

NO SOLVER CHANGE IS NEEDED FOR A MOVING BODY. The API already exists, verified in
third_party/mpm-engine-544c93dd-solver-core/core/solver.py:
  :324 add_sdf_collider   :339 set_sdf_pose   :348 reset_sdf_force
  :354 sdf_wrench         :363 add_cdf_collider   :93 periodic_x
The driver loop, per tick:
  reset_sdf_force(handle)
  solver.step(dt_sub, n_substeps)
  w = solver.sdf_wrench(handle, dt=n_substeps*dt_sub)   # TICK duration, not dt_sub
  integrate(w['force'], w['torque'], tick_dt)
  solver.set_sdf_pose(handle, center=..., quat=..., velocity=..., omega=...)

FIVE TRAPS, EACH WITH A MEASURED FAILURE BEHIND IT. Do not rediscover these.
1. NORMALISE THE WRENCH BY TICK DURATION. sdf_wrench divides accumulated impulse by
   whatever dt it is handed, and the accumulator spans every substep since the last
   explicit reset. Passing dt_sub for an n-substep tick inflates force by EXACTLY n,
   and the result looks plausible.
2. ZERO THE ACCUMULATOR EVERY WINDOW. The engine never zeroes param.force on the SDF
   path, so a naive read is the run-to-date total. Reference implementation:
   /Users/josie/can-it-ford-realism/simulation/realism/dynamic_body.py:178 and :244
   both call param.force.zero_().
3. QUATERNION ORDER DIFFERS WITHIN THE SAME FILE. solver.py:324 defaults
   quat=(0,0,0,1), xyzw. add_cup at :256 documents wxyz and defaults (1,0,0,0).
   Crossing them applies a wrong rotation SILENTLY.
4. COM-OFFSET IS A HARD BLOCKER AND THE LARGEST NEW-CODE ITEM. RigidBody6DOF raises
   NotImplementedError on a non-zero COM offset, because the SDF collider rotates
   about its centre and sdf_wrench reports torque about that same centre. The Yaris
   particle-cloud CG sits 0.6312 m above the floor against bbox mid-height 0.7427 m,
   so a real hull is NOT centre-symmetric. Implement COM-offset migration BEFORE any
   free-rotation run on a real hull.
5. NEVER COMBINE periodic_x WITH AN SDF VEHICLE. solver.py:90-92 says periodic_x is
   "incompatible with CDF colliders and rigid bodies", and add_cdf_collider guards on
   it at :379, but there is NO EQUIVALENT GUARD in add_sdf_collider. The combination
   is silently wrong rather than an error.

AN ENGINE DEFECT NO DRIVER CAN FIX. STATE IT IN EVERY WRITEUP.
mpm_utils.py:1100 initialises rigid particle stress to a zero mat33, :1104 excludes
material 8 from the SVD, and no mat==8 branch in :1105-1147 ever assigns one. The
rigid hull therefore exerts NO PRESSURE on the water, which is exactly what a moving
vehicle pushing water aside requires. Fixing it means patching a vendored engine at a
pinned SHA. Until then every drag and bow-wave force in this track is not physically
formed and the writeup must say so.
THE CORRECT NUANCE, do not overstate it: _apply_rigid_restitution IS live in all 17
gated runs at restitution 0.05, so "no force is ever formed" is FALSE. The real
limitation is that the net force cannot be DECOMPOSED into hydrodynamic, contact and
gravitational parts.

HOW THE VEHICLE MOVES, three options, ranked by defensibility not by ambition.
(a) PRESCRIBED KINEMATICS, constant velocity through the water. This is what the
    validation literature actually covers, so it is the only arm with a comparison.
(b) PRESCRIBED VELOCITY WITH A TRACTION BUDGET CHECK. Move at prescribed speed, but
    at every step compute the traction available from F_F = mu*(W - B - L) and report
    whether the drag exceeds it. This is Shah et al. 2018's balance
    (0.5*rho*C_D*A_D*v^2 = F_N*(mu_RO + mu) + F_DV) evaluated as a DIAGNOSTIC rather
    than integrated as a force. It is honest, cheap, and it is the graded result.
(c) FULL 6-DOF FREE BODY WITH APPLIED PROPULSION. Genuinely novel, and genuinely
    unvalidatable: no published source applies engine torque in a coupled flood
    simulation, so there is no target. Mark EXPLORATORY, run last, never headline it.
Start with (a), deliver (b), attempt (c) only if (a) and (b) close.

PARAMETERS, WITH PROVENANCE, DO NOT INVENT THESE
  mu 0.3 parked baseline (Bonham and Hattersley 1967, adopted conservatively for the
    published hazard curves), 0.52 measured parallel to flow, rolling mu_RO 0.092
    (Shah et al. 2018)
  measured tyre friction 0.75 wet / 0.78 dry on concrete (Smith, Modra, Felder 2019)
  C_D band 1.22 to 6.82 is a JOINT ENVELOPE over three vehicles and all flow
    directions (Hu et al. 2023, J. Hydrology 620:129525), so the midpoint 4.02 is not
    an estimate for any single vehicle at any orientation. Do not quote 95.71 percent
    agreement until the per-vehicle table is read.
  floor friction 0.55 and restitution 0.05 are the canonical scene values; the gated
    driver is sha256 5215c38b, 389 lines, and :132-133 IS its floor plane. A repoint
    to :210-211 was tested and REFUSED on evidence; do not re-apply it.

CONCRETE FIRST STEP
Reproduce the existing exploratory run before changing anything: load
rogue_g96_pd8_coarse_watertight.ply (sha256 c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2)
through the SDF path and confirm you recover volume 4.950341 m3 and canonicalized
extent 2.010112, 4.746607, 1.729385 with the long axis on y. If those three numbers
do not reproduce, stop and report; everything downstream is invalid.

DEFINITION OF DONE
Arm (a) and arm (b) running and classified, with per-step traction margin reported
against F_F = mu*(W - B - L). Every force number carries the "cannot be decomposed"
caveat and the no-rigid-pressure caveat. Wrench normalisation, accumulator zeroing and
quaternion order each verified by an explicit test, not by inspection. Branch pushed
with PUSH_OK=1 and confirmed by ls-remote.
```

---

### DISPATCH 10, Mac then LS6, the scene, and the constraint that decides its size

```
SCOPE DECLARATION
MACHINE: Mac for design, LS6 BATCH for any run.
BRANCH: new, claude/fork-scene-<slug>, off main.
MAY WRITE TO: that branch only.
NEVER TOUCH: main; canonical stores; Dispatch 9's driver branch; Dispatch 8's branches.

THE HARD ARCHITECTURAL CONSTRAINT, AND IT IS THE WHOLE DESIGN
warpmpm's GridConfig(n_grid, grid_lim) takes a SINGLE SCALAR, so the domain is
necessarily CUBIC. You cannot build a long shallow channel without paying cubically.
This is the strongest single argument against attempting an arXiv-2607.00673-scale
scene in this engine at this stage, and it must be stated in the writeup rather than
discovered at run time.

THE ARITHMETIC, so nobody proposes the impossible. Canonical realized depth is
0.2944294473 m. The validated near-floor regime is about 18 cells across that depth,
so dz = 0.01636 m.
  a 30 x 12 x 3 m road-scale scene at ISOTROPIC dz  -> 246.8 MILLION cells
  the canonical Yaris tank at g96                   ->     884,736 cells
  ratio                                              ->        279x
Anisotropic grading (dxy 0.08, dz 0.01636) would give 10.3 M cells, a 23.9x reduction,
BUT the explicit timestep still follows the SMALLEST cell dimension, so it buys memory
and per-step work and NOT step count. AND warpmpm cannot express it anyway: the grid
is a single scalar. Anisotropy is therefore a reason to change engine or to patch the
grid, not a free win. State that explicitly.

THE LITERATURE VERDICT ON THIS, ALREADY SEARCHED. Do not re-run it.
78 papers, 76% coverage. NO MPM study follows a rigid vehicle with a refinement window
through a large flood domain. The closest fluid result is dynamic AMR for free-surface
waves and breaking WITHOUT a vehicle (Mao, Chen, Li, Feng 2016,
DOI 10.1061/(ASCE)EM.1943-7889.0000981). Adaptive MPM-FSI work is preliminary and not
road-scale. What exists and is closest:
  local grid refinement for B-spline MPM, with bridging-domain Lagrange multipliers
    that SUPPRESS spurious stress reflection at the fine/coarse interface, plus
    multi-time-stepping: Sun, Gan, Huang, Zhou 2020, DOI 10.1002/nme.6312
  multi-resolution MPM by penalty formulation, no local equations to solve:
    He, Jin, Zhou, Yin, Chen 2025, DOI 10.1002/nag.70048
  structured mesh refinement in GIMP: Ma, Lu, Komanduri 2006, DOI 10.3970/CMES.2006.012.213
  truncated hierarchical B-spline MPM (uses particle SPLITTING, which is UNSAFE for
    history variables unless deformation-gradient and state transfer are defined):
    Zhang, Shen, Zhou, Balzani 2021, DOI 10.1016/J.COMPGEO.2021.104097
  implicit octree adaptive MPM, up to 5.5x speedup: Bird, Coombs, Augarde, O'Hare 2026
  sparse/dynamic grids cut memory when the domain is EMPTY but do not reduce the
    smallest-cell timestep and do not resolve the floor layer: Qiu et al. 2022
    (10.1145/3570160), Shin et al. 2010 dynamic meshing
  hybrid 3D MPM with 2D shallow-water far field: Pan et al. 2023, DOI 10.1002/fld.5233;
    MPM/finite-volume depth-averaged: Zheng et al. 2023, DOI 10.1016/j.compgeo.2023.105673
  NO moving-reference-frame MPM result was identified. Open-boundary MPM exists:
    Zhao, Bolognin, Liang, Rohe, Vardon 2019, DOI 10.1016/J.COMPFLUID.2018.10.007
DECISIVE CONSTRAINT ON ALL OF THEM: Steffen, Wallstedt, Guilkey, Kirby, Berzins 2008,
DOI 10.3970/CMES.2008.031.107, shows fixed particles-per-cell can LOSE convergence
under grid refinement. Our stack holds PPC constant at 8. Any refinement scheme must
co-refine or explicitly control PPC; otherwise AMR silently changes quadrature and
transfer conditioning. Standard MPM, GIMP, CPDI and B-spline MPM are therefore NOT
interchangeable. Nonuniform grids already produce projection error (Wallstedt and
Guilkey 2007, DOI 10.3970/CMES.2007.019.223).

USE THE DOMAIN RULE THAT ALREADY EXISTS. From
renders/yaris_render_s3_enhanced/hull_sweep.sbatch:38-42 (rescued by Dispatch 8):
  lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth)
  yaris 9.421742314   rogue 10.442536068   silverado 13.067932987
This reproduces the canonical Yaris grid_lim 9.421742313727737 EXACTLY, so it is the
as-ran rule generalised, not a new invention.
THE AXIS TRAP, and it is a 59 percent error: sim_standing.py:82 reads 2.2*ext[1] where
ext is the extent AFTER load_vehicle(up='z') permutes axes, so ext[1] is the PLY's x.
Taking PLY axes at face value gives 14.989 m instead of 9.4217 m.

THE SCENE ITSELF, SCOPED HONESTLY
Do NOT attempt a reconstructed outdoor scene in this dispatch. The Undermind corpus
contains ZERO papers on Gaussian splatting, scene reconstruction or terrain
construction, so there is no evidence base here for it, and a prior reconstruction
attempt produced a metrically wrong mesh: a car at 0.333 x 0.174 x 0.715 m, volume
0.0173 m3, watertight, because the splat trainer normalises median camera-to-subject
distance to 1.0 and no scale-recovery step exists. The directory is misnamed
"failed_reconstructions"; the failure was metric, not geometric.
WHAT TO BUILD INSTEAD, in order:
1. A flat floor with a correct CROSS-SLOPE, which is the one terrain property with a
   plausible hydraulic effect at this scale, and an inflow/outflow pair per Zhao 2019.
2. A sensitivity test: does cross-slope change the traction margin at all? If it does
   not, that is a publishable negative and it retires terrain fidelity as a concern.
3. Only if 2 says terrain matters, escalate to reconstructed geometry, and solve
   metric scale at capture time with a known-length reference object in frame.

DEFINITION OF DONE
A scene module on your branch, the domain-sizing rule applied with the axis trap
handled and a unit test that catches it, an inflow/outflow implementation citing
Zhao 2019, and a written statement of the resolution-versus-extent trade with the
arithmetic above reproduced from your own run. Plus the cross-slope sensitivity
result, in whichever direction it comes out.
```

---

### DISPATCH 11, Mac, validation and the verdict for a moving vehicle

```
SCOPE DECLARATION
MACHINE: Mac, no GPU.
BRANCH: new, claude/fork-validation-<slug>, off main.
MAY WRITE TO: that branch, docs/ only.
NEVER TOUCH: main; the register (Dispatch 4 owns it); any driver or scene branch;
  the canonical stores.

THE SITUATION, ALREADY ESTABLISHED BY A 44-PAPER SEARCH AT 92% COVERAGE
No validated vehicle-fording MPM chain exists. And, importantly, the search did NOT
establish an experimental basis for the US Army FM 90-13 1.5 m/s fording rule. Treat
that rule as doctrinal until proven otherwise; do not adopt it as a validation target
on its face. Field manuals are not scholarly literature and a deep search will not
resolve them; sweep them separately as primary documents via DTIC and the Army
Publishing Directorate if you want to settle the provenance.

THE VALIDATION TARGETS THAT DO EXIST, RANKED. These are the deliverable.
TIER 1, measured vehicle experiments, the strongest anchors:
  Smith, Modra, Felder 2019, DOI 10.1111/jfr3.12527. Full-scale stability curves.
    Yaris 1045 kg: rear-axle traction 4.5-4.7 kN at 0 m falling to 0 kN at ~0.6 m.
    Nissan Patrol 2478 kg: 9.3-9.6 kN falling to 0 kN at ~0.95 m. F_F = mu*(W-B-L).
    Measured tyre mu 0.75 wet / 0.78 dry; 0.3 adopted conservatively for the curves.
    THIS IS A STATIONARY SIDEWAYS WINCH PULL-TEST. It bounds available traction; it
    does not validate propulsion. Say so every time you cite it.
  Al-Qadami 2021 full-scale flooded passenger vehicle, DOI 10.1007/s11069-021-04949-6
  Arrighi 2015 drag and lift in incipient motion, DOI 10.1016/J.JFLUIDSTRUCTS.2015.06.010
  Xia, Falconer, Xiao, Wang 2013, DOI 10.1007/s11069-013-0889-2
  Hu, Li, Wang, Fang 2023 partially submerged at different flow orientations,
    DOI 10.1016/j.jhydrol.2023.129525
  Martinez-Gomariz, Gomez, Russo, Djordjevic 2017, DOI 10.1080/1573062X.2017.1301501
  Teo, Xia, Falconer, Lin 2012, DOI 10.1080/15715124.2012.674040
TIER 2, MOVING-vehicle sources, which is our case:
  Shah, Mustaffa, Martinez-Gomariz, Yusof 2020, hydrodynamic effect on NON-STATIONARY
    vehicles at varying Froude numbers on flat roadways, DOI 10.1111/jfr3.12657, R2=0.85
  Al-Qadami 2022, vehicle MOVING perpendicular to flow, DOI 10.1111/jfr3.12828,
    critical depth 0.38 m, minimum depth x velocity 0.39 m2/s
  He et al. 2026, "Predicting Vehicle-Water Interaction in Shallow Water: Simulations
    and Experimental Validation", J. Computational and Nonlinear Dynamics,
    DOI 10.1115/1.4071177. Ranked the single closest match. READ THIS FIRST.
TIER 3, method comparison:
  Zheng Xin and Su Donghai 2021, rotating-wheel VOF/RANS against road tests,
    DOI 10.1177/0954407020942005
TIER 4, canonical transferable hydrodynamics with public reference data:
  accelerating-plate drag and free-surface effects; near-surface added mass and
  damping; dam-break obstacle pressures with openly supplied measurements and video;
  planing-hull force data; baffled-tank loads with grid-refinement evidence. One
  benchmark in this set has approximately 0.3 percent experimental uncertainty, which
  is an unusually precise public target. Identify it and use it.
EXPLICITLY EXCLUDED AS A STANDARD: SPH work is admitted ONLY as a pointer to
experimental datasets, where the dataset is the asset. Do NOT take error bands,
resolution guidance or boundary treatment from SPH. Its tolerance norms are loose for
reasons specific to SPH, and importing them would import a weaker standard. One SPH
entry in the search is flagged dataset-only for exactly this reason.

THE CONTRADICTION YOU MUST NOT AVERAGE
Al-Qadami 2022 (moving, perpendicular) gives 0.38 m and 0.39 m2/s. Al-Qadami 2023
(exposed, stationary) gives 0.38 m and 0.36 m2/s. Same group, 8 percent spread,
across exactly the moving-versus-stationary distinction this track studies. Report
both with their framings attached. Resolving which applies to a driven vehicle is a
genuine contribution.

THE VERDICT QUESTION, WHICH IS THE REAL DELIVERABLE
The AR&R and Shand thresholds describe a STATIONARY vehicle in flow, so they remove
the degree of freedom a driven vehicle has. A moving-vehicle verdict needs a different
quantity. The candidates, with what exists behind each:
  TRACTION MARGIN. F_F = mu*(W - B - L), measured depth-resolved by Smith 2019, and
    embedded in a moving balance by Shah 2018 (10.1051/matecconf/201820307003):
    0.5*rho*C_D*A_D*v^2 = F_N*(mu_RO + mu) + F_DV. Best supported. Recommend this.
  SPEED CEILING. Pregnolato 2017 (10.1016/j.trd.2017.06.020),
    v(w) = 0.0009*w^2 - 0.5529*w + 86.9448, w in mm, v in km/h, R2 0.95, DEPTH ONLY,
    flow velocity excluded, 30 cm impassable. This is the depth-only baseline to
    contrast against, and it is driver-control and serviceability, not stability.
    A graded speed surface v_max(depth, flow velocity) does not exist in the
    literature and is claimable as original.
  TOTAL HEAD. Kramer, Terheiden, Wieprecht 2016 (10.1016/J.IJDRR.2016.04.003):
    0.3 m for passenger cars, 0.6 m for emergency vehicles.
STANDING WARNING: the Australian small-car limit is a limiting STILL-WATER DEPTH of
0.3 m, NOT a D x V product of 0.3 m2/s. ARR Book 6 (Ball et al. 2019) uses limiting
depths 0.3 / 0.4 / 0.5 m for small car / large passenger / large 4WD with velocity
capped at 3 m/s. Never conflate a depth cap with a hazard product.

SCALE EFFECTS, THE LATENT VARIABLE
Most of Tier 1 is model scale. Froude scaling preserves the gravity-to-inertia ratio
but NOT friction or viscous ratios, and the verdict depends on a friction coefficient.
Tag every target model-scale or full-scale and state the scaling assumed. Note also
that model-scale watertight vehicles are documented to float too shallow.

DEFINITION OF DONE
docs/FORK_VALIDATION_TARGETS_<date>.md containing: the ranked target table with DOI,
what is measured, model or full scale, and what it can and cannot validate; an
explicit recommendation of the traction-margin verdict with its equation and
parameter provenance; the Al-Qadami contradiction stated unresolved; and a plain
statement that self-propulsion has no validation target anywhere in the literature.
Every DOI checked with Scholar Sidekick auditBibliography and Scite before it lands.
```

---

### DISPATCH 12, Mac, the measurement protocol, and a canonical result that needs re-checking

```
SCOPE DECLARATION
MACHINE: Mac, plus one small LS6 BATCH instrumentation run.
BRANCH: new, claude/fork-protocol-<slug>, off main.
MAY WRITE TO: that branch, analysis/ and docs/ within it.
NEVER TOUCH: main; the canonical stores; the register; any other fork branch.

PART A. THE MEASUREMENT PROTOCOL, ALREADY SETTLED BY A 68-PAPER SEARCH AT 91% COVERAGE
There is NO universal frame count and NO universal force-settling threshold. Stop
looking for one. The defensible protocol, which this dispatch implements:
  1. Detect and EXCLUDE initial and final transients.
  2. DEMONSTRATE stationarity for the specific observable being reported.
  3. Attach uncertainty computed from CORRELATED samples, not from raw sample count.
Implement using: automated equilibration detection (Chodera 2015,
DOI 10.1101/021659) and correlated-data error estimation by blocking
(Flyvbjerg and Petersen 1989, DOI 10.1063/1.457480). Both are from molecular
dynamics, which has the most rigorous practice on exactly this question.
FOR A FINITE MOVING PASSAGE: report a PRESPECIFIED constant-speed interior window,
its mean, its filter and window sensitivity, and correlated uncertainty. This is a
PROTOCOL, not a transferable run length. Acceleration waves and force oscillations
can persist inside that window. Towing-tank practice is the source; see also
Brouwer et al. 2019 (DOI 10.1016/J.OCEANENG.2019.04.068) on random uncertainty of
statistical moments, Jentzsch et al. 2021 (DOI 10.1007/s00348-021-03151-5) on steady
and unsteady towing-tank velocities, and Thomas et al. 2007
(DOI 10.1080/14484846.2007.11464528) on water stilling, where the FIRST SLOSHING MODE
governs inter-run offset time.
IF THERE IS NO STEADY STATE, SAY SO AND REPORT SOMETHING ELSE. Slamming, water entry
and impact loading generally have no steady force; the accepted practice is to report
peak distributions, impulses, envelopes, or cycle and event statistics with repeat-run
uncertainty. Our own moving scene shows Fz oscillating by a factor of two or more at
150 frames with no steady value, so this is the likely outcome. An impulse is a
legitimate result; a fabricated steady force is not.
FOR THE VERDICT ITSELF: incipient motion is PROBABILISTIC and RECORD-LENGTH DEPENDENT.
The literature defines a movement probability or activity rate with detection
uncertainty, NOT a single critical stress. Our criterion is a joint condition held for
3 consecutive frames, and register item 15 records a canonical arm at margin_frames 0
and another one frame from flipping. Reframe the verdict as a probability with a
stated record length. This is the single most defensible upgrade available to the
project's headline result.

PART B. NON-DETERMINISM, CONFIRMED AS A REAL MECHANISM
The search confirms that non-associative, order-dependent reductions can produce small
drift OR ALTER DISCRETE GATES. That is our exact symptom: three runs at identical
configuration, geometry and seed gave settle_vmax_final 0.865234, 0.861557 and
0.594807 against a peak identical to four decimals, with two failing the settle gate
and one meeting it at 974 frames. Mitigations named: fixed-order or sorted reductions,
reproducible reductions, and higher-precision accumulation. Practice: report OUTCOME
SPREAD and GATE-PASS FREQUENCY across repeats; no universal repeat count exists, and
independent-start ensembles are the stronger convergence check.
ALSO FIX, cheap and high-value: the SDF cache never hits because load_vehicle draws
60,000 RANDOM surface samples, so back-to-back loads differ by 2.22e-16 m, one ULP,
which changes build_sdf_cached's content hash and forces a rebuild every run. Seed
that sampling. Note this is the same 60,000-sample mechanism as register E2.

PART C. THE CANONICAL RE-CHECK, AND THIS IS WHY THIS DISPATCH EXISTS
A 16-paper search at 99 percent coverage found NO paper reporting the 0.93 to 1.01 dx
floor-penetration plateau we measured, and NO defensible minimum cell count across a
shallow water layer. So our measurement appears to be novel, and it is unanchored.
MEASURED: penetration saturates at 0.93-1.01 dx in the MOVING scene.
MEASURED LIVE: canonical g64 has realized_depth_m / dx = 0.2944294473 / 0.1472147237
  = EXACTLY 2.000 cells across the water depth (CLAUDE.md L-3).
INFERRED AND UNTESTED: if that penetration is a property of the enforced plane BC
  rather than of one scene, the corrupted fraction of about 1/depth_cells implies
  roughly 50 PERCENT of the canonical water column sits in a boundary-corrupted layer.
DO NOT ASSERT THIS. MEASURE IT. Instrument the existing canonical scene for particle
z-position relative to the floor plane, report penetration in dx, and state plainly
whether it transfers. Both answers are publishable and the question is cheap.
MECHANISM HYPOTHESIS TO TEST: this is likely a kernel-support effect. With a quadratic
or cubic B-spline a particle influences nodes 1.5 to 2 cells away, so a particle can
sit about a cell below a node-enforced plane and still be seen. If so, penetration
scales with basis-function support width. The anchor for that analysis is Steffen et
al. 2008 (DOI 10.3970/CMES.2008.031.107), which systematically varies basis functions,
boundary treatments and GIMP smoothing length; it is the strongest mechanistic anchor
found and it does NOT establish our plateau, so this is an open question we can close.
RELATED, and useful: Schulz and Sutmann 2019 report that traditional grid-based
boundary treatment distorts stress MULTIPLE GRID LENGTHS into the body and propose
image particles to reduce it. Baumgarten and Kamrin 2023 (DOI 10.1002/nme.7217)
analyse and mitigate MPM spatial integration errors. Neither is validated for
free-surface water; label them as mechanistic evidence only.
NO PAPER REPORTS AN ACCEPTED CORRECTION for a smeared near-wall layer, so a
calibration is NOT established practice. Do not invent one and call it standard.

DEFINITION OF DONE
An implemented, tested stationarity-and-uncertainty module used by Dispatch 9's
outputs; a written protocol doc citing the sources above; the seeded-sampling fix with
a demonstrated cache hit; and the canonical floor-penetration measurement reported in
dx with a clear yes or no on whether the 2.000-cell canonical scene is boundary
corrupted. If it is, flag it to a human rather than editing any canonical claim
yourself, because it bears on a published result and that is outside this scope.
```

---

# PART III. AMENDMENTS AND THE ENGINE GO/NO-GO, added 2026-08-14 (second pass)

Three further research outputs landed after Part II was written: RB-6 (FOSS engine
assessment, `compass_artifact_wf-18992794`), RB-8 (scriptable grounding and citation
integrity, run live), and RB-3 (DeepWiki SDF band structure). They change the engine
decision in Dispatch 9, add a fabricated citation to remove, and add one new dispatch.

## A correction to RB-6 that must not propagate

**RB-6 section 1 does not describe this project's engine.** It states that
`kks32/mpm-engine` "appears not to exist as a public repo", treats it as CB-Geo mpm
(`github.com/cb-geo/mpm`), and concludes it has "no rigid-body/fluid force-coupling
mechanism at all". RB-6 caveats this itself ("if a different, e.g. private, repo was
intended, its specifics are unverified"). Verified live here, and the caveat applies:

- The vendored solver core is **11 Python files and 0 C++ files**, and
  `kernels/mpm_utils.py` imports `warp`. CB-Geo mpm is C++14 with TBB/MPI. Different
  codebases.
- `third_party/mpm-engine-544c93dd-solver-core/VENDORED.md` records the repo as
  `https://github.com/kks32/mpm-engine` at pinned SHA
  `544c93dd02cb9c7ead89e1155a62967243244fce`, MIT, fetched 2026-08-07 by raw URL with
  **every file re-fetched and sha256-compared, all five matched**. It resolved then.
- The SDF collider API exists at that SHA: `add_sdf_collider`
  (`kernels/mpm_solver_warp.py:2621`, `core/solver.py:324`), `set_sdf_pose` (`:2779`,
  `:339`), `reset_sdf_force` (`core/solver.py:348`), `sdf_wrench` (`:354`).

**What survives from RB-6 regardless:** warpmpm has no drivetrain, tyre or actuated
vehicle model, so the actuated-vehicle-in-fluid path is genuinely absent there. That
conclusion is unaffected by the repo mix-up.

**A second scoping correction, from RB-3.** The project's standing finding that "no
force accumulator exists" is true **only of the free-rigid material-8 path** used by
the 17 canonical runs. The **SDF-collider path has always had one**: per-node impulses
accumulate atomically into `param.force` and `param.torque`, readable via
`sdf_wrench()`. That is almost certainly how the 7.3 to 7.7 percent buoyancy agreement
was computed. Add this scope note wherever "no force accumulator" appears, so a future
reader does not apply it to the whole engine.

## Three findings that change what gets written down

**RB-8 found a fabricated DOI already in the project's own documents.**
`10.1016/j.cma.2022.114965`, attributed to "Qian et al. 2022, water entry of a
half-buoyant cylinder", **resolves to an unrelated phase-field crack-propagation
paper**. Do not cite it. Either locate the real Qian paper or drop it. Of 15 DOIs
checked, 13 were clean and none carried a retraction or update-to flag.

**One citation is now confirmed and safe.** Cheng Zhang, Shiwei Zhao, Hao Chen,
Jidong Zhao, "Stabilized explicit material point method for fluid flow and
fluid-structure interaction simulations using dual high-order B-spline volume
averaging", *Computer Methods in Applied Mechanics and Engineering*, 2026, DOI
**10.1016/j.cma.2025.118428**. Also: Shah, Mustaffa and Martinez-Gomariz are cited as
2019 in project docs; Crossref shows **2021**, titles matching exactly.

**A USGS data trap that would have understated a flood crest by 3.5x.** Gauge
**08159000, Onion Creek at US-183** publishes stage (00065) and discharge (00060)
only, with **no velocity parameter at all**, so velocity must be derived from
discharge over cross-sectional area rather than pulled. Worse, the continuous
instantaneous-values feed (`nwis/iv`) returned **zero data points during the
2013-10-31 06:00-09:00 rise** and a misleading 11.5 ft "peak" from surrounding hours,
because the sensor gapped during the event. The dedicated peak-flow record
(`nwis/peak`) gives the truth: **2013-10-31 08:30, gage height 40.13 ft, discharge
135,000 cfs**, confirming the project's 40.15 ft to within 0.02 ft.
**Standing rule: for any historical extreme-flood grounding, pull `nwis/peak`, never
`nwis/iv` alone.**

## Vehicle mass grounding, from the live NHTSA pull

| Vehicle | Project figure | NHTSA real curb weight | Verdict |
|---|---|---|---|
| 2020 Nissan Rogue | 1609 kg | AWD **1610**, FWD 1550 | matches the AWD trim almost exactly, well grounded |
| 2020 Nissan Rogue | **1571.3 kg** (job 896273) | falls between FWD and AWD | **pinned to no published trim, provenance still open** |
| 2018 Ram 1500 | 2337 kg | Crew Cab 5.7ft Box 4x4 = **2336 kg** | near-exact, well grounded |
| 2007 Chevrolet Silverado | 2337 kg | range 2020 to 2440 across trims | plausible, inside range, no single-trim match |
| 2010 Toyota Yaris | 1078 kg | 1043 to 1071 across trims | 0.6 to 3.4 percent above the top of range |

**Mechanism found for a standing rule.** 2337 kg attaches to both the Silverado and
the Ram 1500 in different project documents not because of an error but because
**both are MASH-2270P class pickups, engineered to the same nominal test weight by
design**. The register's existing rule (Silverado geometry is not the Ram, do not
conflate) is correct and now has a documented reason behind it.

**Open, and Dispatch 5 should close it:** the string `1571.3` appears nowhere in the
project knowledge that was searched. Trace it in the repo, not from memory.

## The SDF band structure, from RB-3, which explains the hull-high/box-low sign split

- **warpmpm**: `add_sdf_collider` takes a `band` parameter in world metres and
  **defaults to one grid cell (`dx`), flat and not feature-scaled**. Callers may pass a
  multiple of `dx` but nothing forces feature-aware scaling.
- **Genesis**: different design. Margin is the minimum `sdf_cell_size`, and for
  non-convex geometry that cell size is **adaptively shrunk so at least 2 cells span
  the thinnest wall**, explicitly to prevent tunnelling. warpmpm's default path has no
  equivalent thin-wall guard.
- **Both**: no sub-cell or fractional-volume treatment exists. A feature thinner than
  the band is inflated to at least one cell.
- Genesis alone has a mitigation: `watertighten_mesh` estimates local wall thickness by
  inward ray-casting from face centroids and sets
  `cell_size_target = min(material sdf_cell_size, wall_thickness/2)`. It fires **only
  if the mesh is watertight**, and is silently skipped otherwise.

This supports the **hull-high half** of the measured sign split: thin wheels and
underbody inflate to at least one cell, enlarging effective displaced volume. It says
nothing about why the box control reads **low**. That remains a separate mechanism,
consistent with over-carve plus floor smear. Do not treat this as confirming the whole
theory.

## The ULP cache defect is fully resolved, and the fix is already written

Root cause is **not** in the vendored engine. `mesh_sdf.py` is deterministic. The
60,000 random surface samples are drawn by **`load_vehicle`, project-owned code**,
unseeded, to derive a re-centring shift; `canonicalize()` cancels that shift
mathematically but not bitwise, and a 2.22e-16 residue survives into `v.mesh`, which
hashes differently every run and forces an 8-plus-minute SDF rebuild.
The fix is already applied in `simulation/moving_vehicle_sdf_exploratory.py`:
`np.random.seed(args.mesh_seed)` immediately before the load, with a comment recording
that seeded loads are bitwise identical.
**Still open, and it is a pure compute-cost question, not a physics one:** does the
canonical `renders/yaris_render_s1/sim_standing.py` also call `load_vehicle` without
seeding first? If so, every canonical run has been rebuilding the SDF unnecessarily.
Dispatch 12 owns this check.

**Worktree count, third revision.** Live `git worktree list` gives **18**: 1 main, 4
sibling-directory clones, 13 under `.claude/worktrees/`. Prior figures of 32 and of 4
are both dead. Two are in detached HEAD (`render-realism-vehicle-water-ad1490`,
`warpmpm-gravity-provenance-435363`), which is a standing orphan risk. Commit
`a01e6e9` on `claude/orphan-rescue-token-rotate-d72f90` independently records the same
18. **Recommendation: stop quoting a count at all and say "run `git worktree list`".**

---

### DISPATCH 13, engine go/no-go: does Chrono build on GH200

```
SCOPE DECLARATION
MACHINE: LS6 or Vista, whichever has a GPU node free. This is a BUILD task, not a
  physics task, so an interactive node is acceptable here even though production runs
  should be batch.
BRANCH: new, claude/fork-chrono-eval-<slug>, off main.
MAY WRITE TO: that branch (docs/ and scripts/ only), and a NEW $SCRATCH build
  directory. Chrono itself is built OUT of tree; do not vendor it into the repo in
  this dispatch.
NEVER TOUCH: main; the canonical stores; third_party/mpm-engine-544c93dd*/ (both
  vendored trees are separately provenanced and their provenance tables are
  load-bearing, per their own VENDORED.md); any other fork branch.

WHY THIS DISPATCH EXISTS
An independent FOSS engine assessment concluded that Project Chrono is the ONLY stack
that already ships BOTH genuine accumulated-force two-way fluid coupling AND a
self-propelled multibody vehicle. That is exactly the combination this fork needs and
that warpmpm does not have. Chrono is therefore a serious alternative to Dispatch 9's
warpmpm plan, and this dispatch decides between them on evidence rather than
preference. Dispatch 9 proceeds in parallel and is NOT blocked on this.

WHAT CHRONO ACTUALLY PROVIDES, so you do not re-derive it
- Chrono::FSI-SPH accumulates per-marker fluid forces into a net per-body force and
  torque by atomic accumulation into a per-body array in the BCE manager
  (src/chrono_fsi/sph/physics/BceManager.cu), exposed as
  chrono::fsi::ChFsiInterface::GetFsiBodyForce(i) and GetFsiBodyTorque(i).
  CAVEAT CARRIED FROM THE SOURCE: the specific line number (~373) came from a
  user-posted compiler error, not a blob view; the file path and the atomicAdd pattern
  are verified but the line may drift. Do not cite a line number you have not opened.
- Two-way is explicit and named: ChFsiInterfaceSPH::ExchangeSolidForces() moves fluid
  forces to the multibody system, ExchangeSolidStates() moves body states back to the
  SPH data manager.
- Chrono::Vehicle supplies engine, drivetrain and tyre subsystems, so the vehicle
  drives under its own power while the FSI interface reads the fluid reaction. The
  published fording configuration was a 4WD wheeled vehicle under a constant-speed
  controller with approximately 1.5 million SPH markers, chassis and tyre meshes
  decomposed into convex hulls for collision.
- TERRAIN INGEST IS THE OTHER REASON THIS MATTERS. RigidTerrain::AddPatch accepts a
  Wavefront OBJ mesh used for both contact and visualisation, and SCMDeformableTerrain
  initialises from a height-map image or an OBJ mesh. So a photogrammetry or 3DGS
  reconstruction exported as a heightfield or OBJ CAN be ingested directly as terrain,
  which is the single hardest thing to do in warpmpm.
  CAVEAT: semi-empirical tyre models (Fiala, LuGre, Pacejka) query GetHeight and
  GetNormal, which may be incomplete for an arbitrary rigid mesh. Rigid tyres and FEA
  tyres go through the contact engine and are unaffected. Choose the tyre model with
  this in mind.

THE GATING QUESTION, AND IT IS THE ONLY DELIVERABLE THAT MATTERS
There is NO documented case of Chrono or Chrono::FSI being built or run on
ARM64/aarch64, Jetson or GH200. Officially supported targets are Linux, Windows and
macOS on x86-64 with CUDA or HIP. Nothing in principle precludes aarch64 plus CUDA,
since CUDA supports SBSA Grace plus Hopper sm_90, but it is undocumented and untested.
YOUR JOB IS TO ANSWER: does Chrono::FSI-SPH build and run a clean demo on GH200?

GO/NO-GO MILESTONE, stated in advance so it cannot be moved afterwards:
  a clean run of demo_FSI-SPH_DamBreak or demo_FSI-SPH_ObjectDrop on a GH200 node,
  producing output, with the build recipe recorded.
BUDGET: treat this as a moderate build-porting task. If it proves infeasible after a
bounded effort, STOP and say so plainly. The documented fallbacks are, in order: an
x86 plus H100 host, or continue on warpmpm per Dispatch 9. Both are acceptable
outcomes. A negative result here is a real deliverable, not a failure.

KNOWN AARCH64 LANDMINE, unrelated to Chrono but it will bite you first: on aarch64 the
default pip install torch installs a CPU-ONLY build. Use the CUDA wheel index or an
NVIDIA NGC aarch64 Apptainer container. This is the most common GH200 failure mode.

VALIDATION REALITY CHECK, WRITE THIS INTO THE REPORT
Chrono's fording capability is a PHYSICS DEMONSTRATION AND VISUALISATION, not a
benchmark validated against experimental fording data. The rigorously validated Chrono
off-road work is soil and terramechanics (CRM and SCM), validated against single-wheel
experiments, DEM ground truth, and drawbar-pull and slip-sinkage tests. This matches
the independent finding that NG-NRMM treats SPH fording as a known gap. Therefore:
adopting Chrono does NOT inherit a validated fording result, it inherits a validated
SOIL result and a demo-level fluid one. Any quantitative NG-NRMM fording
error-reduction percentage is UNVERIFIED and must not be cited.

THE OTHER THREE CANDIDATES, ALREADY ASSESSED, DO NOT RE-SEARCH THEM
- SPlisHSPlasH: genuine momentum-conserving Akinci-2012 force coupling
  (doi:10.1145/2185520.2185558), best-architected non-Chrono base, and DiffFR
  (doi:10.1145/3618318) proves actuated control is feasible on it. But NO drivetrain or
  tyre model (major new work) and the SPH solvers are CPU-ONLY, so no GH200
  acceleration. Fallback only.
- DualSPHysics: true force coupling via Chrono, but ships x86-only precompiled
  libraries and GPU binaries limited to sm35 through sm80, while GH200 Hopper is
  sm_90. Hard blocker. Not recommended.
- Genesis: the most ARM64-plus-CUDA-ready backend of the five (Quadrants, forked from
  Taichi, targets ARM64 plus CUDA), but its LegacyCoupler is an impulse and
  velocity-projection scheme, not accumulated-force integration, and it FAILED this
  project's Yaris buoyancy test. Using it would mean replacing the coupler, a major
  rewrite. The benchmark that would reopen it: a corrected coupler reproducing static
  buoyancy on the Yaris hull to within a few percent of Archimedes.

CONCRETE FIRST STEP
Do not start with Chrono. Start with the cheapest possible discriminator: on a GH200
node, confirm that a CUDA sm_90 toolchain and a working PyTorch CUDA build are
present, then attempt the Chrono core build (no FSI) before attempting Chrono::FSI.
If the core will not configure on aarch64, you have your answer in an hour rather
than a week.

DEFINITION OF DONE
A written go/no-go with the build recipe if it worked, or the exact failure and where
it stopped if it did not. Either answer closes the question. If GO, add a scoped
comparison of what a Chrono arm would give that Dispatch 9's warpmpm arm cannot,
specifically the actuated drivetrain and the OBJ/heightfield terrain ingest. If NO-GO,
say so plainly and hand the fork back to Dispatch 9 unchanged.
```

## Amendments to existing dispatches

**Dispatch 9 (moving-vehicle driver).** The engine decision is now provisional, not
settled: warpmpm remains the default and the work proceeds, but Dispatch 13 may
supersede it. Add the RB-3 band finding to its trap list: `add_sdf_collider`'s `band`
defaults to one `dx`, flat and not feature-scaled, with no sub-cell treatment, so thin
wheels and underbody inflate to at least one cell. Add the scope correction that the
SDF path **does** have a force accumulator, unlike the free-rigid path.

**Dispatch 10 (scene).** If Dispatch 13 returns GO, the terrain problem changes
completely: Chrono ingests an OBJ mesh or heightfield directly as `RigidTerrain` or
`SCMDeformableTerrain`, which removes the cubic-domain constraint that currently makes
road-scale impossible in warpmpm. Do not rewrite Dispatch 10 until Dispatch 13
reports.

**Dispatch 11 (validation).** Remove the Qian citation, DOI
`10.1016/j.cma.2022.114965`, as fabricated. Add Zhang et al. 2026, DOI
`10.1016/j.cma.2025.118428`, as confirmed. Correct Shah, Mustaffa and
Martinez-Gomariz from 2019 to **2021**. Add the finding that Chrono fording is
demo-level, which strengthens rather than weakens the novelty claim: even the strongest
existing stack has not validated a fording verdict.

**Dispatch 12 (protocol).** The ULP root cause is confirmed and the fix is written;
the remaining task is narrowed to checking whether canonical `sim_standing.py` seeds
before `load_vehicle`, which is a compute-cost question only. Add the USGS
`nwis/peak` rule to its provenance section.

**Dispatch 5 (three classes).** Add the NHTSA grounding table above, the MASH-2270P
mechanism explaining the shared 2337 kg, and the open task of tracing `1571.3` in the
repo, which the grounding pull could not resolve from documents alone.

## Operating protocol, include verbatim in every dispatch above (1 to 13)

```
OPERATING PROTOCOL:

Before starting: check git log, .remember/ files, and the research
citations you were given, in that order. Do not duplicate work already
done elsewhere in this bundle.

When you hit an obstacle: try a fix. If it doesn't work, try a second,
genuinely different approach, not a variation of the same one. Before
concluding you're stuck, check whether an available connector or subagent
resolves it:
  - DeepWiki, for any question about how a library/repo actually behaves.
    Treat its answer as a hypothesis to verify against source, not fact.
  - The physics-skeptic subagent, before finalizing any claim involving a
    percentage, force, verdict count, or distance. If it's unavailable this
    session, say so explicitly and mark the claim unreviewed, do not fake
    the review.
  - Wolfram, for any physical parameter, unit conversion, or equation
    before it becomes a stated claim.
  - Scite, for any citation, DOI, or threshold before it's written as
    settled.
  - register_integrity.py (or the project's equivalent), before any commit.

Prefer proceeding on a clearly-labeled, reversible assumption over
stopping. State the assumption explicitly, in the commit message or the
write-up, so it can be revisited later without re-deriving it from
scratch.

Tag every factual claim by its source: read directly, recalled from
context, or inferred. Tag every solver/engine claim by which engine it
applies to. Never state a number from memory when you could check it live.

Keep working on everything else in your scope even if one specific thing
below is blocked, do not let one blocker stop the whole session.

Flag, rather than silently proceed past, only these four things:
1. You are about to discard, overwrite, or force-push over uncommitted
   work you did not create and cannot verify is safe to lose.
2. You've found two independently-reported results that genuinely
   disagree about the same physical quantity, not just different framing
   of the same thing, and resolving which is correct requires a judgment
   call, not just more data you can go get yourself.
3. You are about to edit a canonical file outside your declared scope.
4. A genuine hard-stop case: real financial cost, an exposed credential,
   a destructive/irreversible action, or anything matching the project's
   existing standing hard rules.

When you flag one of these: write it clearly to a named file (not just an
inline comment), keep working on everything else in your scope that isn't
blocked by it, and do not treat the flag as ending the session.

Write with an engineer/scientist's discipline throughout: state
assumptions before acting on them, prefer a falsifiable test over a
plausible-sounding claim (a no-forcing control, a held-fixed comparison,
a second seed), and write up a result the same way whether it confirms or
overturns something already published.

Before any push: confirm the target branch, stage explicit paths only,
never a blanket add, and confirm the push actually landed afterward,
don't just assume the command succeeding means the remote updated.
```
