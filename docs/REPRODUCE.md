# Reproduce a result from a clean clone

Written 2026-08-26. Every command below was run on that date and its real output is pasted
underneath, including the parts that fail.

## What you can and cannot reproduce on a laptop

**You can reproduce every number in the paper and on the poster**, because the simulation output
is committed as CSV.

**You cannot reproduce a simulation run.** The solver is warpmpm from `kks32/mpm-engine` and it
needs a CUDA GPU. The 17 gated runs were produced on NVIDIA GH200 (TACC Vista) and A100 (TACC
Lonestar6). `requirements.txt` deliberately does not list it.

So the honest claim is: **the analysis is reproducible in about two minutes, the simulation is
not reproducible without an allocation.**

## Setup

```bash
git clone https://github.com/jcerrell-IS/can-it-ford.git
cd can-it-ford
python -m venv .venv && source .venv/bin/activate
make install
```

`make` uses the miniforge env this project was developed in by default. Override it:

```bash
make test PYTHON=$(which python)
```

## The two-minute version: re-derive the headline numbers

```bash
make facts
```

Real output, 2026-08-26:

```
gated runs            17
grids                 ['48', '64', '96']
masses kg             ['1100.0', '1609.0', '2337.0']
water particles       1151002
vehicle particles     198905
total particles       1349907
largest run, water    180067
verdicts              {'SLIDE': 16, 'STUCK': 1}
L1 conditions         70
FORD small_passenger  14
FORD large_passenger  19
FORD large_4wd        26
```

Those twelve lines are every headline number in the abstract, and they come straight from
`data/all_runs_inventory.csv`, `data/failure_modes_by_run_classified.csv` and
`data/scenario_sweep.csv`. Nothing is cached and nothing is hardcoded.

## Rebuild a figure

```bash
make figures
```

Writes the G-series into `figures/`. The figure whose provenance is best documented is
`figures/g1_velocity_sweep.pdf`, the centre poster panel: it answers whether the depth-velocity
product returns the right verdict when varied along its own velocity axis, and it is built from
`data/all_runs_inventory.csv` by `analysis/make_poster_figures.py`. Expect under a minute.

Per-figure provenance, tiered A through D, is in `deliverables/FIGURE_PROVENANCE.md`.

## Run the gates and the checks

```bash
make gates
make checks
```

Both exit 0. `params_check.py` prints warnings and no blocking issues. Two warnings are real
limitations rather than noise, and both are reported in the paper:

- `lit:resolution_convergence_gci` cannot compute an apparent order across n_grid 48/64/96,
  so the raw non-monotone spread is reported instead of a GCI band.
- `lit:manifest_provenance` finds that across **67 manifests**, `solver_git_sha`, `mesh_sha256`,
  `grid_density` and `vehicle_mass` are each missing in **23**. Those runs cannot be traced to
  code plus data plus environment. This is a disclosed provenance gap, not a silent one.

**A trap.** Run these from a normal clone, not from a git worktree. `renders/` is gitignored and
therefore physically absent in a worktree, so `manifest_provenance` reports "skipped, no
summary.json found" and finds 0 manifests instead of 67. An absent hit there is not evidence of
absence.

## Run the tests, and what currently fails

```bash
make test
```

Real result, 2026-08-26: **27 passed, 6 failed.**

All six failures are in `tests/test_count_claims_check.py`. The test fires
`.claude/checks/count_claims_check.py` as a subprocess against a seeded temporary tree and
expects a denial payload; the checker returns empty stdout instead. That is a defect in a
**repository guardrail**, not in the physics, the analysis or the figures. The physics gates
(`make gates`) and the integrity checks (`make checks`) both pass with zero blocking defects.

It is left visible rather than skipped or excluded. A suite that hides its own failures is worth
less than one that shows them.

## What is deliberately not built

**The reconstruct-to-decide front end does not exist.** No Gaussian splat has ever entered a
simulation. The splat pipeline was trained and validated in isolation, and the simulation
pipeline runs on a finite-element-derived hull. They are two stages that are not connected. The
poster states this under Scope, and it is a scoping decision, not an omission.
