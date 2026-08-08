# Bingham / Herschel-Bulkley rheology sensitivity sweep

**These are NOT canonical results.** They are a sensitivity study and must never be
merged into `data/all_runs_inventory.csv`, `renders/yaris_render_s1/gates_results_all_runs.json`,
or any figure describing the 17 gated runs.

Run 2026-08-07 on branch `claude/bingham-material-sweep-2026-08-07`, worktree
`.claude/worktrees/bingham-sweep-2026-08-07`, base commit `e0b983a`.

## Question

Is Newtonian water the simplest model sufficient for the fluid, or does floodwater's
real rheology (sediment load, debris) need a yield-stress model to get the right
FORD / NO-FORD verdict?

## How it was run

Driver: `renders/yaris_render_s1/sim_bingham_sweep.py`, derived from the canonical
`sim_standing.py` by exactly two physics edits plus CLI parametrization. `diff` the two
files; the diff is the audit trail.

1. `set_material(newtonian(...).with_yield(tau_y).with_powerlaw(K=hb_K, n=hb_n))`
2. `term_viscous` computed from `eta_cap = water_eta + tau_y/0.02 + hb_K*0.02**(hb_n-1)`
   instead of from `water_eta`.

Edit 2 is not optional. `kirchoff_stress_newtonian` (`kernels/mpm_utils.py:28-53`) floors
the shear rate at `eps = 0.02` (`:41`, `:51`), so the kernel's apparent viscosity is
capped at `eta_cap`, while the driver's own substep formula (`sim_standing.py:149`) reads
only the Newtonian `eta`. Without the paired edit a yield stress of tens of Pa raises the
true viscous CFL rate by orders of magnitude and the driver never notices. The settle
loop runs the water at rest, where the shear rate sits exactly on the `eps` floor, so it
is the first thing that would break.

The `0.02` is deliberately inline and NOT lifted into a shared constant: the kernel's copy
lives in a vendored engine at a pinned SHA, and a shared name would falsely imply that
changing one changes the other. It is also **not** one of the `0.05` DRIFT_THRESHOLD
literals in CLAUDE.md item 13; do not sweep it into that deduplication.

Launcher: `renders/yaris_render_s1/run_bingham.py`. It binds
`renders/yaris_render_s1/vehicle_live.py` as `warpmpm.vehicle` before running the driver.
This is required, see below.

## The engine binding, and why it matters

The pip-installed `warpmpm` (pinned via `direct_url.json` to `kks32/mpm-engine`
@`544c93dd02cb9c7ead89e1155a62967243244fce`) is **NOT** the code that produced the 17
gated runs. Verified live 2026-08-07, three independent divergences in the vehicle path:

1. it has no `solidify_watertight`, so `sim_standing.py:12` raises `ImportError`;
2. `VehicleBody.solidify()` (installed `:101-104`) unconditionally calls
   `solidify_columns`, with no watertight branch;
3. `load_vehicle()` (installed `:121-124`) dispatches on the `.ply` **suffix alone** and
   sends the file to `load_gaussians_ply`, so the canonical watertight hull dies with
   `ValueError: no field of name opacity`. Its own docstring claims it accepts "a
   watertight mesh readable by trimesh". The body does not.

`vehicle_live.py` is the module the runs actually used, and it reproduces the canonical
`g64_m1100` vehicle cloud exactly: `h=0.07360736182599795`, `n_particles=8905`,
`solid_volume=3.5513843861695054` m3, `fill_ratio=1.0024403113437104`,
`realized_rho=309.7383668982256`, every digit matching `data/all_runs_inventory.csv`.

The **solver** path (`core/solver.py`, `kernels/mpm_utils.py`) is byte-identical between
the install and `third_party/mpm-engine-544c93dd-solver-core/`, but whether Vista's solver
matched either is NOT established from this machine. Treat that as open.

## Venue

Mac CPU-ARM, warp 1.16.0, no CUDA. The 17 canonical runs were Vista GH200. A bit-exact
reproduction across backends is not achievable, so the control was gated on deviation, not
on equality. Control vs canonical `final_disp_mag_m`: see `bingham_sweep_results.csv`
header. For scale, CLAUDE.md item 5 records that the canonical run disagrees with *itself*
by 3.4 percent between `summary.json` (0.658537) and `rollout.npz` (0.637019).

## Caveats that must travel with any use of these numbers

- **Regime labels are indicative, not cited.** The "turbid", "hyperconcentrated", "mud
  flow" labels in `analysis/bingham_cfl_crossover.py` are not pinned to a primary source.
  Do not put them in the paper without a citation pass.
- **The sound speed is wrong by two orders of magnitude.** `bulk_modulus = 1.5e5` gives
  `c = 12.845 m/s` against water's real 1481 m/s. `tau_y_crit` scales linearly with sound
  speed, so every threshold here would shift under a physical sound speed. Isik and He
  2022 is the citable result that artificial sound speed can qualitatively flip a
  rigid-body outcome, and it has never been swept here.
- **A tau_y-only sweep at fixed eta is not fully physical.** Real sediment loading raises
  both together. The ladder includes two eta-coupled points (`etacoup_*`) for that reason,
  but the pairing itself is not sourced.
- **Resolution is unconverged.** 4 water particle layers, 2 grid cells per flow depth,
  against a rule of thumb of ~10 particles per depth. See CLAUDE.md L-3.

## Files

- `<tag>/summary.json`, `<tag>/metrics.csv`, `<tag>/rollout.npz` per ladder point
- `<tag>.log` stdout per point
- `bingham_sweep_results.csv` the collected table, written by
  `analysis/collect_bingham_sweep.py`
