# Mesh reconciliation: the Rogue and Silverado candidate selection

Date: 2026-08-08
Scope: verification, one file-level correction, documentation. No GPU job was run. Nothing
under `renders/yaris_render_s1/` was modified. `data/all_runs_inventory.csv` and
`gates_results_all_runs.json` were not touched. Nothing was pushed.

Repo HEAD at start: `ca13ed6`. Four other Claude Code sessions were reported active in this
working tree; every file this session wrote was checked for pre-existence first and no
tracked file was overwritten.

---

## 1. Verdict up front

The selection bug is real, it is exactly as previously diagnosed, and it is now corrected in
`~/Downloads/vehicle_meshes/candidates/`.

| | wrong file, still on disk | correct file, now staged |
|---|---|---|
| Rogue | `rogue_candidate_euler-32.ply`, 2.597 m3 | **`rogue_g96_pd8_coarse_watertight.ply`, 4.950 m3** |
| Silverado | `silverado_candidate_euler-82.ply`, 5.462 m3 | **`silverado_g96_pd8_coarse_watertight.ply`, 7.962 m3** |

Hull selection is **GO**. Running a simulation with either hull is **NO-GO today**, for one
specific, one-line reason given in section 7.

---

## 2. What was verified, and how

### 2a. The method was calibrated before it was trusted

Everything below uses the loader the 17 gated runs actually ran, quoted from
`analysis/render_v1/as_ran_local_copies/vehicle_live.py`:

```python
import trimesh
src_mesh = trimesh.load(path, force="mesh")
```

Run in `~/Downloads/vehicle_meshes/mesh_venv` (trimesh 4.12.2, numpy 2.5.1). Calibration
against the canonical Yaris hull, which has a published target in
`vehicle_geometry_research/WATERTIGHT_HULL_TOOL_FINDINGS.md`:

```
yaris_coarse_v1l_watertight.ply
  verts 327212   faces 655308   watertight True   volume 3.5427387900160743
```

**Exact match on all three, to the last floating-point digit.** The measurement script
refuses to print anything downstream if this check fails. Script kept at
`<scratchpad>/measure_hulls.py`.

### 2b. SHA256: both duplicate claims are exactly right

| file | sha256 |
|---|---|
| `candidates/rogue_candidate_euler-32.ply` | `5ef646213e00c86357a6b5c983fbd7b60fe40c0c93af93e0c260de4c2b924006` |
| `rogue_g96_pd6_coarse_watertight.ply` | `5ef646213e00c86357a6b5c983fbd7b60fe40c0c93af93e0c260de4c2b924006` |
| `candidates/silverado_candidate_euler-82.ply` | `c9c58ca7b931d09dc6291280b08695a5eac87cad4283b8cd2a3bb66121759ba1` |
| `silverado_g32_pd8_dq0.02_coarse_watertight.ply` | `c9c58ca7b931d09dc6291280b08695a5eac87cad4283b8cd2a3bb66121759ba1` |
| `rogue_g96_pd8_coarse_watertight.ply` | `c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2` |
| `silverado_g96_pd8_coarse_watertight.ply` | `46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9` |

Both promoted candidates are byte-identical to a pool file. The truncated hashes in the
memory file (`5ef646213e00c863...`, `c9c58ca7b931d09d...`) and in
`VEHICLE_MESH_QUALIFICATION.md` section 7b (`c0b778e2c4432631...`, `46fba11e77cd92dd...`)
all extend correctly.

### 2c. Volumes recomputed independently, not trusted from the memory file

| file | verts | faces | watertight | euler | volume m3 | L x W x H (m) |
|---|---|---|---|---|---|---|
| `rogue_candidate_euler-32.ply` | 31357 | 62778 | True | -32 | 2.597364 | 4.6660 x 1.8344 x 1.7302 |
| `silverado_candidate_euler-82.ply` | 2108 | 4380 | True | -82 | 5.462160 | 5.8147 x 2.1477 x 1.7587 |
| **`rogue_g96_pd8_coarse_watertight.ply`** | 36074 | 72520 | True | -186 | **4.950341** | 4.7466 x 2.0101 x 1.7294 |
| **`silverado_g96_pd8_coarse_watertight.ply`** | 26072 | 52280 | True | -68 | **7.962083** | 5.9400 x 2.3377 x 2.0102 |

Both land on the expected 4.95 and 7.96 m3.

### 2d. The convergence ladder reproduces to four decimals

| pd8 series | g24 | g32 | g48 | g64 | g96 |
|---|---|---|---|---|---|
| Rogue, re-measured | 2.897261 | 3.385951 | 4.131595 | 4.792703 | **4.950341** |
| Rogue, as claimed | 2.897 | 3.386 | 4.132 | 4.793 | 4.950 |
| Silverado, re-measured | n/a | 5.462160 | 6.711811 | 7.554701 | **7.962083** |
| Silverado, as claimed | n/a | 5.462 | 6.712 | 7.555 | 7.962 |

Monotone and converging in both series. Nothing in the ladder needed correcting.

### 2e. Mass provenance, checked against the decks themselves

| claim | verified? | evidence |
|---|---|---|
| Yaris 1100 kg from deck header line 28 | **YES** | `yaris-coarse-v1l.key:28` reads `$- Version 1l, 1100 kg` |
| Silverado 2270 kg from deck header line 28 | **YES** | `silverado-coarse-v3a.key:28` reads `$- version 3a, 2270 kg` |
| Rogue deck states no mass at all | **YES** | `rogue-v3.key` header and `README.md` both checked: no mass, no curb weight. The line-28 slot that carries the mass in the other two decks holds tire pressure instead |
| `gates_both_scenarios.py` uses 2337 kg for large_4wd | **YES** | `gates_both_scenarios.py:20` and `:23` |

One nuance worth recording, not a correction: `2270` is also a MASH class designation. The
repo's own `Simulation_Ready_Vehicle_Mesh_Assets.md` cites the Silverado validation paper as
the "MASH 2270kg Vehicle" and describes the truck as satisfying "2270P" requirements. So the
deck header figure is genuinely stated primary data, but it is not independent of the class
the model was built to represent. Both facts should be kept.

### 2f. Cross-validation held

`MULTI_GEOMETRY_SCOPE.md` section 2 recommends exactly `rogue_g96_pd8_coarse_watertight.ply`
and `silverado_g96_pd8_coarse_watertight.ply`, on density plausibility and resolution.
`VEHICLE_MESH_QUALIFICATION.md` section 7b reaches the same two files by a different route,
walking the parameter grid (g, Poisson depth, density-quantile trim) and eliminating
neighbours. Two independent routes, same answer. No averaging was needed and none was done.

### 2g. Vista staging, checked live read-only on the login node

| | on Vista? | evidence |
|---|---|---|
| Silverado hull | **YES, already staged** | `mpm-engine/test_meshes/silverado_test.ply`, 992723 bytes, md5 `6190ad32aa2bfcb0210356854fbcd539`, byte-identical to the Mac `silverado_g96_pd8_coarse_watertight.ply` (md5 confirmed equal this session) |
| Rogue hull | **NO** | A repo-wide `find` for `*rogue*` on `$WORK` returns exactly 2 hits, both `can-it-ford-OLD-pre-purge/vehicle_meshes/rogue/rogue_points_centered_150k.npy` and its parent directory. That is a point cloud, not a hull. No Rogue `.ply` mesh exists on Vista |

The Rogue point cloud is a trap for a glob: a `*rogue*` search finds something, and it is not
a usable hull. File check only, login node, no GPU, per CLAUDE.md.

---

## 3. Where the source material was wrong, stated plainly

The briefing document and the memory file are substantially correct. Five things did not
survive checking, all minor, none changing the conclusion.

1. **The Silverado candidate is 31.40% below converged, not 31.1%.**
   `(7.962083 - 5.462160) / 7.962083 = 0.31398`. The Rogue's 47.5% is right
   (`(4.950341 - 2.597364) / 4.950341 = 0.47532`).

2. **`candidates/SUMMARY.md` did not print 605 and 415.6 kg/m3.** It printed **619.6** and
   **427.8**. The briefing and the memory file both attribute 605 / 415.6 to that file. Both
   pairs are arithmetically correct; they differ only in which mass was divided:
   - 1571.3 / 2.597 = 605.0 and 2270 / 5.462 = 415.6 (memory file's mass choices)
   - 1609 / 2.597 = 619.6 and 2337 / 5.462 = 427.8 (what SUMMARY.md actually used)

   The substance of the criticism is unaffected, and is in fact slightly understated: the
   figures SUMMARY.md called "plausible" were the higher pair.

3. **The pool is 43 `.ply` files, not 44.** This resolves cleanly rather than being a real
   discrepancy: `VEHICLE_MESH_QUALIFICATION.md` hashed 44 because its set of 22 watertight
   hulls includes `yaris_coarse_v1l_watertight.ply` as a control, and that file lives in the
   repo, not in `~/Downloads/vehicle_meshes/`. 22 non-watertight `_poisson_raw` files plus 21
   watertight files in the pool is 43. Nothing is missing.

4. **1571.3 kg does not appear in project documentation.** A real `/usr/bin/grep` across the
   repo, `renders/` and `data/` included, returns no documentation hit; every match is a
   coincidental digit run inside scientific-notation CSV values. The figure appears only in
   the 2026-08-04 audit files and the memory file. Its trace is recorded there and is sound:
   2020 Rogue FWD S curb weight 3,464 lb from cars.com, which converts to 1571.2 kg.

5. **The briefing's step 3 asks which convention `candidates/` uses "elsewhere in the
   pipeline". It is used nowhere.** No script in the repo or in `~/Downloads/vehicle_meshes`
   reads that directory. There are no symlinks anywhere under `vehicle_meshes` except
   `mesh_venv`'s own python. The existing convention is therefore plain regular-file copies
   into a hand-curated staging directory that nothing consumes automatically.

---

## 4. Why the original criterion was invalid

The two files were promoted on `euler_number` closest to 2. That gate is not merely weak
here, it is inverted. `euler_number` measures topological genus. In this pipeline a value
near 2 is bought by coarseness, and coarseness erodes enclosed volume, and enclosed volume is
what buoyancy integrates. The criterion optimised the quantity that does not enter the
physics at the direct expense of the one that does.

The decisive counterexample is internal. `yaris_coarse_v1l_watertight.ply` has
**euler_number -442**, further from 2 than any file in this pool, and it is the hull under
every published result in this project. A gate that would reject the known-good reference
first is not a gate.

Two corroborating details:

- Poisson depth is the stronger lever than mesh2sdf grid resolution. At identical `g96`,
  `pd6` gives 2.597 m3 against `pd8`'s 4.950. A 47.5% volume collapse from one parameter.
- The Silverado candidate is 2108 verts / 4380 faces, against the Yaris hull's
  327212 / 655308.

Correct ranking metric: distance from converged volume.

---

## 5. Densities, with every mass labelled

Reference: the canonical Yaris hull, 1100 kg / 3.542739 m3 = **310.494 kg/m3**.

| file | 1571.3 kg (Rogue, web) | 1609 kg (Rogue, AR&R class) |
|---|---|---|
| `rogue_candidate_euler-32.ply` | 605.0 (+94.8% vs Yaris) | 619.5 (+99.5%) |
| **`rogue_g96_pd8_coarse_watertight.ply`** | **317.4 (+2.2%)** | **325.0 (+4.7%)** |

| file | 2270 kg (Silverado deck) | 2337 kg (AR&R large_4wd) |
|---|---|---|
| `silverado_candidate_euler-82.ply` | 415.6 (+33.8% vs Yaris) | 427.9 (+37.8%) |
| **`silverado_g96_pd8_coarse_watertight.ply`** | **285.1 (-8.2%)** | **293.5 (-5.5%)** |

Under every one of the four mass choices, the g96_pd8 hulls land within about 8% of the
Yaris hull's own working density and the promoted candidates land 34% to 100% away. The
internal-consistency argument does not depend on resolving the mass conflict, which is why
it can be made now.

**Caveat on the "class" labels above, per CLAUDE.md item 10.** 1609 kg and 2337 kg have **no
source in `vehicle_params.py`**; its nearest entries are `midsize_suv` at 1990.0 and
`light_pickup` at 2300.0. Both figures are unsourced in that sense. What is verified is
narrower and is stated as such: `run_s2.sh:15` reads
`for M in 1100:small_passenger 1609:large_passenger 2337:large_4wd`, and
`gates_both_scenarios.py:19,22` maps `1609.0` to `large_passenger` while `:20,23` maps
`2337.0` to `large_4wd`. Those are labels the pipeline attaches, not citations. Do not
describe the mass sweep as spanning cited vehicle classes.

**On the old density band, which CLAUDE.md and register item 9 mark STALE:** it is not used
as a gate anywhere in this document. The canonical Yaris hull sits at 310.494 kg/m3 and all
17 gated runs realise 302.55 to 663.58, every one of them above that retired band. It is
mentioned only because the original `SUMMARY.md`, `MULTI_GEOMETRY_SCOPE.md` and the memory
file all framed their objection in its terms, and any reader coming from those documents
needs to know the framing has been retired. Every load-bearing comparison in section 5 is
against the Yaris hull's measured 310.494 kg/m3, which is the surviving reference.

---

## 6. The Rogue mass conflict, surfaced and left open

Two documents disagree, and this session did not pick a winner.

| source | Rogue mass | provenance | status |
|---|---|---|---|
| `.claude/memory/rogue-silverado-candidate-hulls-are-worst-in-pool.md` and `can-it-ford-audit/2026-08-04/VEHICLE_MESH_QUALIFICATION.md` | **1571.3 kg** | cars.com, 2020 Rogue FWD S curb weight 3,464 lb. Explicitly flagged as secondary because the deck states no mass | verified this session that the deck genuinely states no mass |
| `_inbox/vehicle_files_to_pull.md:45` | **1,609 kg** | "2020 Nissan Rogue, real weight 1,609 kg", attributed to the CCSA model page | not independently verified this session |

They differ by 37.7 kg, 2.4%. On the recommended hull that is 317.4 against 325.0 kg/m3, so
**the hull decision does not turn on it**. It would enter any published buoyancy or
flotation-depth number.

`_inbox/vehicle_files_to_pull.md` also recommends a **2018 Dodge Ram** over the Silverado,
with fresh download links, and describes the Rogue and Ram as things to convert "someday",
with no awareness that the 44-file conversion pool exists and has already been qualified.
Two signals that it predates this work rather than contradicting it: it describes the
conversion pipeline as a cost still to be paid, which was paid on 2026-07-29, and it lists
the Ram at "real weight 2,337 kg", the same number `gates_both_scenarios.py` carries as the
AR&R `large_4wd` class figure. That coincidence is worth noticing before anyone treats 2337
as Silverado-specific: it is a class figure that a Ram also matches.

**Recommendation: treat `_inbox/vehicle_files_to_pull.md` as superseded on vehicle choice,
but do not discard its 1,609 kg figure.** Resolving it needs one thing this session could not
do: reading the CCSA 2020 Nissan Rogue model page and recording which mass it publishes. Until
then, carry both, labelled by source, exactly as the project already carries the Yaris at
1100 used / 1078 NCAC-stated / MASH-nominal.

---

## 7. Go / no-go for wiring a hull into a simulation

**Hull selection: GO.** Both files are verified, watertight, converged, provenance-traced to
a pipeline script and log, and now staged in `candidates/`.

**Running a simulation: NO-GO until one line changes.** `sim_standing.py` is the right entry
point and it already accepts an arbitrary hull:

```
228:    p.add_argument("--vehicle", default=str(YARIS))
```

That is a free-form path, not an enum, so `--vehicle /path/to/rogue.ply` works today. But:

```
15:  HULL = 3.542739
269:  print("INSTRUMENT solid_volume=%.5f m3 hull=%.5f fill_ratio=%.4f ...
360:  "solid_volume_m3": float(solid_volume), "hull_m3": HULL,
361:  "fill_ratio": float(solid_volume / HULL),
```

`HULL` is a hardcoded Yaris literal, not derived from the loaded mesh. Swap the hull and the
run still reports `hull_m3: 3.542739` and a `fill_ratio` computed against the wrong
denominator. Verified live this session at those exact lines.

The failure is silent and the numbers stay plausible-looking, which is the dangerous kind.
Predicted symptom, and a usable tripwire: a correct Rogue run would print `fill_ratio`
about **1.3973** (4.950341 / 3.542739) and a Silverado about **2.2474** (7.962083 / 3.542739)
instead of about 1.0. Conversely, a multi-hull run that prints about 1.0024 means `--vehicle`
never took effect.

Note that `realized_rho` at `:269` divides by `solid_volume`, not `HULL`, so **density
reporting is unaffected**. Only `hull_m3` and `fill_ratio` are corrupted by the hardcode.

This file is under `renders/yaris_render_s1/`, which this task was scoped out of. The fix is
one line (derive `HULL` from the loaded mesh volume) and belongs to whoever owns that
directory.

Ordered blockers before any GPU time:

1. **Fix `sim_standing.py:15`.** One line. Out of scope here.
2. **`scp` the Rogue hull to Vista.** About 1.4 MB. It is the single missing asset;
   confirmed absent this session. The Silverado is already there and byte-identical.
3. **`run_s2.sh` never passes `--vehicle`.** Confirmed live at both copies. That, not the
   driver, is why geometry never varied across all 17 gated runs. A hull sweep needs the
   wrapper extended.
4. **Ground clearance is unmeasured on all three hulls.** AR&R needs >= 0.12 m
   (large passenger) and >= 0.22 m (large 4WD). Not a mesh-selection blocker, but it gates
   the AR&R comparison the verdict rests on.

Two things that are explicitly **not** blockers, both control-backed, do not re-litigate:

- **No candidate is underbody-bridged.** Worst in the pool is 0.0216 enclosure at z=0.02 m,
  against a convex-hull negative control at 0.6042 and the known-good Yaris positive control
  at 0.0181. A 28x margin to the bridged control, and a 33x control separation proving the
  test would have caught it.
- **Fill ratio does not predict underbody enclosure.** Pearson r = -0.028 at z=0.02 and
  +0.033 at z=0.10, n=22. Indistinguishable from zero and opposite in sign. Do not substitute
  one metric for the other in any writeup.

**Confound to declare in any writeup that uses all three hulls:** resolution is unmatched
(327212 / 36074 / 26072 verts) and the Rogue and Silverado went through a Poisson
intermediate the Yaris did not. Any cross-vehicle difference is partly a pipeline
difference.

---

## 8. What this session changed

Two files, both outside the git repo, in `~/Downloads/vehicle_meshes/candidates/`.

1. **Added** `rogue_g96_pd8_coarse_watertight.ply` and
   `silverado_g96_pd8_coarse_watertight.ply` as plain copies from the pool, matching the
   directory's existing convention. `cp -n` was used so no existing file could be
   overwritten, and both copies were sha256-verified byte-identical to their source
   afterwards.

2. **Rewrote** `SUMMARY.md`. It now names which two files to use and which two not to, states
   the measured volumes and hashes, gives densities under every mass choice labelled by
   source, explains why `euler_number` is an invalid criterion, and retracts the
   "plausible-density" characterisation. The original 2026-07-29 text is preserved verbatim
   in a block at the bottom, with a note that its measurements were all correct and only its
   criterion and its conclusion were wrong.

**Deliberately not done, needs Josie's call:** the two wrong `.ply` files are still in
`candidates/`. CLAUDE.md requires explicit confirmation before deleting or overwriting a
file, so they were left in place and marked in `SUMMARY.md` rather than removed. Deleting or
renaming them is a one-command follow-up:

```bash
rm ~/Downloads/vehicle_meshes/candidates/rogue_candidate_euler-32.ply ~/Downloads/vehicle_meshes/candidates/silverado_candidate_euler-82.ply
```

Both are byte-identical duplicates of pool files that remain on disk, so nothing unique is
lost either way.

---

## 9. Sources read live for this document

- `~/Downloads/vehicle_meshes/` and `candidates/`, direct measurement and hashing
- `vehicle_geometry_research/WATERTIGHT_HULL_TOOL_FINDINGS.md`, calibration target and method
- `vehicle_geometry_research/2010-toyota-yaris-coarse-v1l/.../yaris-coarse-v1l.key:28`
- `vehicle_geometry_research/2007-chevrolet-silverado-coarse-v3a/.../silverado-coarse-v3a.key:28`
- `~/Downloads/flood vehicle/2020-nissan-rogue-v3/rogue-v3.key` and its `README.md`
- `~/can-it-ford-audit/2026-08-04/MULTI_GEOMETRY_SCOPE.md`, sections 0, 1c, 2
- `~/can-it-ford-audit/2026-08-04/VEHICLE_MESH_QUALIFICATION.md`, sections 1b, 1c, 2b, 2c, 2e, 7b
- `_inbox/vehicle_files_to_pull.md`
- `renders/yaris_render_s1/sim_standing.py` and `gates_both_scenarios.py`, read only
- `analysis/render_v1/as_ran_local_copies/run_s2.sh` and its `renders/` twin, read only
- Vista `$WORK`, read-only login-node `ls` / `md5sum` / `find` via `scripts/tacc.sh`
