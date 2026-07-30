# Gap manifest, 2026-07-25

Read-only survey. Nothing in this file has been fixed. Every row was checked live in the
session that wrote it (lane `yaris-render`, 2026-07-25 evening); rows that came from a
handoff or memory note and then failed a live check are marked CORRECTED and the stale
claim is named.

Deadlines: **poster Jul 27 09:00**, **session Jul 30**, **paper Jul 31**.

Effort key: S under 1 h, M 1 to 4 h, L over 4 h, XL multi-day.

---

## BLOCKS THE JUL 27 09:00 POSTER

| # | gap | where | why it matters | effort |
|---|---|---|---|---|
| 1 | `solidify_watertight` patch is UNCOMMITTED | `/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py` (` M` in git status, HEAD `fd390d6`) | Every correct number on the poster depends on this function. It exists only as a working-tree edit on one machine. A lost `$WORK` or a stray `git checkout` erases the entire result. Also uncommitted in the same file, from another lane: the `vx,vy,vz,vmag,wx,wy,wz` CSV columns. Committing must preserve both. | S |
| 2 | Poster carries no L2 figure from corrected geometry | `figures/Cerrell_TACC_42x56.pdf` (404 KB, 1 page, 4032x3024 pt) | The only VERIFIED poster row is fig1, which is L1-only. The new L2 assets (`yaris_hero_frame.png`, `yaris_flood.gif`, `three_class_table.md`) exist as of this session but are not placed on the poster. | M |
| 3 | Divergence-zone claim is class-free and wrong for 2 of 3 classes | paper/poster text, wherever "depth >= 0.25, v >= 1.2, D x V < 0.60" appears | Measured this session at 0.30 m / 1.5 m/s: small_passenger L1=NO-FORD L2=NO-FORD (agree), large_4wd L1=FORD L2=FORD (agree), only large_passenger diverges. The zone must carry a class label or it is false as written. | S |
| 4 | Both poster logo slots empty, QR slot reserved but empty | `figures/Cerrell_TACC_42x56.pdf` | Cosmetic but visible at 42x56 in. No logo asset exists anywhere in the repo. | S |
| 5 | `DRIFT_THRESHOLD = 0.05 m` has no peer-reviewed source | `simulation/`, used by every L2 verdict | Every FORD/NO-FORD on the poster rests on it. Must appear as "conservative numerical onset-of-motion tolerance, not a literature stability criterion" in the same sentence as any verdict. The large_passenger verdict sits 2.2 % above the threshold (0.05110 vs 0.05000), inside its own uncertainty. | S |

## BLOCKS THE JUL 30 SESSION

| # | gap | where | why it matters | effort |
|---|---|---|---|---|
| 6 | No depth-velocity sweep on corrected geometry | `data/track1_sweep_v1/`, `data/track1_sweep_v2/` | Both existing sweeps predate `solidify_watertight` and inherit the 2.17x over-fill; v2 additionally inherits `fit_to_bbox`-warped truck geometry (4.6x divergence, do-not-ship). One single point (0.30 / 1.5) exists on corrected geometry. A phase-space figure needs a grid. | L |
| 7 | 100-300 kg/m3 plausibility band is wrong | `CLAUDE.md` Multi-Pane Standing Rules; `flood-mpm-debugging-reference` skill Part 3 | Correct density is 1100 / 3.5427 = **310.5 kg/m3**, ABOVE the band. The band was only ever satisfied because the over-fill diluted density. Re-derived live at n_grid 48-192: rho 302.6 to 312.3, all outside. Widen or restate; do not adjust the vehicle. | S |
| 8 | Water resolved by only 4 layers at n_grid 64 | `FloodScene.__init__` | Depth dependence is claimable but coarse. NEWLY UNBLOCKED: raising n_grid is now permitted (see gap 9) and buys layers 4 -> 6 -> 8 -> 12 at n_grid 64 -> 96 -> 128 -> 192 with volume error inside 0.6 %. | M |
| 9 | F0 grid-gate verdict is obsolete and still cited | `.claude/handoffs/2026-07-25_ford-F0-gridgate.md` | CORRECTED this session. Its "no n_grid passes the ratio band" and "raising n_grid still forbidden" were derived under `solidify_columns`. A correction block is appended to that file and to `INDEX.md`. Anything else quoting 2.41x, 2.18x, 8.5475 m3 or 143 kg/m3 is stale. | S |
| 10 | AR&R's D is undefined for a transient surge, and it decides a verdict | `vehicle_params.py:166`, `L1_verdict` | Nominal D x V is 0.4500. Honest local D x V measured at the vehicle is 0.1892 / 0.1645 / 0.1530, i.e. **58 to 66 % lower**, because local depth rises (bow wave) while local speed collapses (stagnation). Re-running L1 on local values flips large_passenger FORD -> NO-FORD on the DEPTH limit and makes L1 and L2 agree on all three classes. Which definition AR&R intends is unresolved and it is the whole ballgame for that class. | M |
| 11 | Finite dam-break slab, not a sustained flood | `FloodScene.__init__`, water block construction | Local depth at the vehicle decays from 0.40-0.43 m peak to 0.107-0.124 m by frame 89 as the slab drains downstream. Any claim about steady-state fording needs an inflow boundary condition that does not exist. | L |

## BLOCKS THE JUL 31 PAPER

| # | gap | where | why it matters | effort |
|---|---|---|---|---|
| 12 | V2 real meshes never converted | `reference_data/vehicle_data_master_reference_2026-07-21.json` part 2 | Silverado (2007, 2337 kg, MASH 2270P, 251400 elements) and Rogue (2020, 1609 kg, 3240729 elements) exist only as CCSA LS-DYNA `.k` decks with URLs and sha384. **NOT ATTEMPTED this session.** Prior attempts failed twice: marching cubes stalled at genus 9, Poisson produced a 0.345 m asset. Until converted, the three-class result is mass-only on one hull and must be labelled as such. | XL |
| 13 | Three-class result is mass-only, one geometry | `figures/three_class_table.md` | All three runs use the SAME Yaris hull; only `--vehicle-mass` varies. The 1609 and 2337 kg rows are NOT a Rogue and NOT a Silverado. Geometry effects (frontal area, ground clearance, SSF) are entirely absent, and clearance is exactly what AR&R classes on. | (blocked by 12) |
| 14 | `mesh.sample(60_000)` is unseeded | `vehicle.py:162` | `load_vehicle` derives the body's `shift` from an unseeded random surface sample, so the oriented mesh placement jitters run to run. Measured effect: parity fill returns 8904 particles locally and 8905 on Vista from identical inputs (0.01 %). Small, but it means no run is bit-reproducible and the exact particle count is not a stable citation. | S |
| 15 | No ground truth for shallow-flood hydrodynamics | both engines | No published wave-propagation or bow-wake benchmark exists at this scale for Genesis or mpm-engine. Treat fluid behaviour as unvalidated, not as known-good. | XL |
| 16 | Bulk modulus softened, wave speed not physical | `mpm-engine` `docs/performance.md`, `FloodScene` default `bulk_modulus=1.5e5` | Deliberate, documented stability tradeoff. Belongs in Limitations explicitly so it does not read as an oversight. | S |
| 17 | Track 2 Genesis is blocked and unrelated | `can_it_ford_L2_mpm.py` | P2G `CUDA_ERROR_ILLEGAL_ADDRESS` at grid_density >= 96; gd=64 runs have 21-31 % water inside the vehicle. Escalated to Cristian Moran. Not this track; do not mix its numbers into L2 results. | (external) |

## INFRASTRUCTURE, not deadline-blocking but cost real time this session

| # | gap | where | why it matters | effort |
|---|---|---|---|---|
| 18 | `warpmpm` import times out on the Vista login node | `login1.vista.tacc.utexas.edu` | Measured this session: `from warpmpm.vehicle import load_vehicle` exceeded a 240 s timeout, RC=124, twice. Any CPU-only geometry check must therefore run on a compute node or on the Mac. This session worked around it by AST-extracting the pure numpy functions from the live `vehicle.py` and running them on the Mac, validated to match Vista digit for digit. | M |
| 19 | ffmpeg broken on Vista, three ways | login1 and compute nodes | `libunwind.so.8` missing on login1, exit 127 on compute nodes, no module provides it. Encode on the Mac. `imageio_ffmpeg` 0.6.0 works locally (`ffmpeg-macos-aarch64-v7.1`) and produced both deliverables this session. | (worked around) |
| 20 | CORRECTED: "no matplotlib on any Mac interpreter" | `.claude/handoffs/2026-07-25_ford-F2-l1-boundary.md` | **FALSE.** `/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3` has matplotlib 3.11.0, trimesh 4.12.2, numpy 2.5.1, imageio 2.37.3. fig1 regeneration is NOT env-blocked on the Mac. | S |
| 21 | CORRECTED: fig1 tripwire "NOT updated" | `analysis/plot_l1_three_class.py:26` | **Already updated.** Live read shows `EXPECTED_FORD = {"small_passenger": 14, "large_passenger": 19, "large_4wd": 26}`. F2's handoff said this was pending; lane-P appears to have done it at 17:45. Gap closed, no action. | none |
| 22 | `drift 0.1198 m` has no provenance anywhere | project-wide | Searched all 126 session `.jsonl` (115 MB) plus `docs/` and `.claude/handoffs/`: zero occurrences. `0.09043` and `866214` both present. Any gate or doc still quoting 0.1198 as a reproduction target is citing a number that does not exist on this machine. | S |
| 23 | `analysis/` scripts are untracked | `plot_l1_three_class.py`, `plot_traction_bias.py`, `plot_geometry_pipeline.py`, `recompute_l1_l2.py` | Every current poster figure is generated by a script git does not track. A clean clone reproduces nothing. | S |
| 24 | Two `mpm-engine` trees still coexist | `/work/.../vista/mpm-engine` (installed) vs `can-it-ford/mpm-engine` (stale) | The stale nested copy already produced one false blocker in an earlier session. It is still on disk. | S |

---

## What this session verified rather than assumed

- Mesh: `is_watertight True`, volume 3.542739 m3, 655308 faces, 327212 vertices, oriented
  extents [1.7461 4.2826 1.5175] m. Mac and Vista agree.
- Grid, verbatim from the live run:
  `grid 64^3 lim=9.42m  water 23532 + vehicle 8905 particles (1100.0 kg)  dt=3.03e-03 (11 substeps/frame)`
  and `INSTRUMENT dx=0.147213 h=0.073606 floor=0.441638 lim=9.421618`, water_layers 4.
- Fill: `fill_ratio` 1.0023 to 1.0024, realized rho 309.75 to 309.78 at 1100 kg.
- Reproduction: this session's 1100 kg run gave final |d| = 0.09240 m against job 866214's
  0.09043 m on disk, +2.2 %.
