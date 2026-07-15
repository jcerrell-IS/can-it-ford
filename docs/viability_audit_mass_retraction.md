# RETRACTED: the mass-conservation PASS in viability_audit.py

Date: July 15, 2026
Scope: `analysis/viability_audit.py`, `viability_audit_results.csv`, `README.md:143`
Status: retracted, README corrected, generator disabled

## What is retracted

Every `mass_integrity=PASS` ever reported by `analysis/viability_audit.py`, and the claim in
`README.md:143` that the script "checks mass conservation". The check never checked anything.

## Why: it is a tautology

The pre-retraction code (`analysis/viability_audit.py:17-24`):

```python
particle_mass = RHO0 * (depth * 2.0 * 1.0) / n_particles
masses        = np.ones(n_particles) * particle_mass
mass_sum      = masses.sum()
expected_mass = RHO0 * depth * 2.0 * 1.0
mass_err      = abs(mass_sum - expected_mass) / expected_mass
mass_label    = "PASS" if mass_err < 1e-6 else f"FAIL(err={mass_err:.2e})"
```

`mass_sum` divides `RHO0 * depth * 2.0 * 1.0` by `n_particles`, then multiplies it straight back.
It is `expected_mass` re-derived from the identical expression. Both sides of the comparison are the
same literal formula, so `mass_err` is float roundoff (5.7e-16) for every possible input.

The simulation output is never read. `pos` and `vel` are loaded from the `.npz` and then not used in
the mass calculation at all. The `depth * 2.0 * 1.0` water volume is a hardcoded assumption, not a
measurement of the seeded water body.

## Proof

Replacing every particle position and velocity in a real `.npz` with garbage
(`pos = 999.0`, `vel = 12345.0`) and re-running the identical check:

```
mass_err with real data    : 5.684341886080802e-16  -> PASS
mass_err with garbage data : 5.684341886080802e-16  -> PASS
```

Identical to the last digit. The check cannot fail, so it carries no information.

## What made it worse

An uncommitted fix widened the glob from `particles_d*.npz` to `particles_*.npz`, correctly making the
MPM-track files visible to the audit for the first time. Correct in itself, but it broadened the false
PASS from 1 file to 9. That is why `viability_audit_results.csv` currently reads 9/9 PASS.

## The 9 audited rows are void anyway, for two further reasons

1. **All of them carry `rho=604`**, the known-wrong vehicle density that commit `e0dd0fe` fixed to
   115.7 for the 1390kg sedan target. The fix has never actually been run. Every existing `.npz`
   predates it.
2. **The stored metadata contradicts the filenames.** Checked directly:

   | Filename says | Stored `grid_density` | Stored `coup_friction` |
   |---|---|---|
   | `grid128_cf0p4` (x5) | **64** | **0.55** |
   | `grid64_cf0p4` (x2) | 64 | 0.4 |

   Root cause: `run_tag` hardcodes `grid128`/`cf0p55` as literal text in an f-string, and `np.savez`
   hardcodes `grid_density=128, coup_friction=0.55, rho=115.7` as literals, instead of reading the
   scene. The `.npz` records what someone assumed, not what ran. This is the same class of defect as
   the mass check: an assumption echoed back and mistaken for a measurement.

   Some rows are marked `FORD ... PASS` for runs that `kumar_july9_update/STATUS.md` records as
   "Step 0 only / Verdict: None / Output written: None".

## Actions taken this pass

- `README.md:143` corrected. It no longer claims mass conservation is verified.
- `analysis/viability_audit.py`: the `mass_sum_kg` / `mass_integrity` columns and the
  "Mass conservation: N/N runs PASS" summary line removed, so the false PASS cannot regenerate.
  Momentum columns retained. No test depended on the removed columns
  (`tests/test_csv_schema.py` guards only `scenario_sweep.csv` and `l2_results_from_wandb.csv`).

## What a real mass check would need

Particle mass in Genesis MPM is immutable: set once at `mpm_solver.py:940` as
`particles_info[i_p].mass = _particle_volume * mat_rho`, stored in static `particles_info`, never in
the per-frame `particles` field. So `entity.get_mass()` sums constants and is flat by construction.
Logging it per step would produce a second tautology, just a more expensive one.

This solver can only lose mass by particles leaving the domain or deactivating. The real check is
therefore `get_particles_active()` and an in-bounds particle count over time, which requires per-step
logging that Track 2 does not yet emit. That instrumentation is the subject of the same pass as this
retraction.

## Note for other panes

Deliberately NOT written to `SESSION_STATE.md`, which was being actively edited by the Track 1
vehicle-density session throughout this investigation (it wrote at 03:41 and again at 04:12) and which
contains no mass claim to correct. Nothing here touches Track 1.

Originally written to `logs/`, per the pane-scratch convention, then moved here: `logs/` is gitignored
(`.gitignore:8`), and `README.md:143` now references this file, so a gitignored path would ship a
broken reference to anyone cloning the repo. This is the single source of truth for the retraction.
Do not duplicate it back into `logs/` or `SESSION_STATE.md`.
