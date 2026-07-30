# L1 criteria reconciliation: what B7b would change, and what it would break

Written 2026-07-25 per AMENDMENT B items B7a to B7d. Everything below was read
from the live file or computed in the session that wrote it.

**Bottom line: do not apply the B7b block as written.** It contains two changes
that would silently corrupt every L1 verdict in the pipeline, and one of them
contradicts AMENDMENT B's own stated criterion. The genuinely good ideas in it
(binding constraints, signed margins, `audit_vehicle_class`) are worth having and
are preserved in a corrected patch at
`analysis/vehicle_params_B7b_patch_PROPOSED.py`. `vehicle_params.py` has **not**
been modified.

---

## B7a. What the live file already has

Read live from `vehicle_params.py:158-200`.

`AR_R_STABILITY_LIMITS` already carries **all three class-membership axes**:
`length_m_max`/`_min`, `kerb_weight_kg_max`/`_min`, `ground_clearance_m_max`/`_min`,
at `:169`, `:174`, `:179`. The premise that ground clearance needs adding is
false; it has been there.

`AR_R_SOURCE` already cites the **primary** report directly:

> Shand, Cox, Blacka & Smith (2011), AR&R Project 10 Stage 2, P10/S2/020,
> ISBN 978-0-85825-948-5, Table 3 "Proposed DRAFT Stability Criteria for
> Stationary Vehicles", PDF p.24 / printed p.14.

and it carries a caveat the B7b replacement drops: that these are the report's own
**DRAFT INTERIM figures for STATIONARY vehicles, not an endorsed safety standard**.

### Verified independently this session

The internal consistency claim holds. Computed, not asserted:

| class | D at v=3 | x V cap | product | D.V cap | consistent |
|---|---|---|---|---|---|
| small_passenger | 0.10 | 3.0 | 0.3000 | 0.30 | yes |
| large_passenger | 0.15 | 3.0 | 0.4500 | 0.45 | yes |
| large_4wd | 0.20 | 3.0 | 0.6000 | 0.60 | yes |

So the "high velocity depth" column is the corner of the D.V hyperbola with the
velocity cap, not a fourth constraint. Three numbers per class do specify the
envelope. Confirmed.

---

## The two blocking defects in the B7b block

### Defect 1: return type changes from `str` to `dict`, silently

Live signature, `vehicle_params.py:186`:

```python
def L1_verdict(depth_m: float, velocity_ms: float, vehicle_class: str = "small_passenger") -> str:
    ...
    return "FORD"
```

The B7b version returns a dict and drops the default for `vehicle_class`.

Real callers of this function, found by grep across the working tree:

| caller | line | what it does with the return |
|---|---|---|
| `scripts/gen_scenario_sweep.py` | `:27`, `:28` | writes it straight into CSV columns `L1_verdict` and `L1_verdict_{class}` |
| `analysis/render_v1/gates_both_scenarios.py` | `:65` | stores as `L1a_verdict` |

`scripts/gen_scenario_sweep.py` is the generator for `data/scenario_sweep.csv`,
which is the poster's data source. Under the B7b block every row would get the
**repr of a dict** written into the verdict column. Then every downstream
comparison against the string `'FORD'` or `'NO-FORD'` becomes permanently False,
and `analysis/make_phase_space_v2.py:12-15` would classify every row as `OTHER`.

Nothing raises. The CSV still writes, the plot still renders, and every verdict is
wrong. This is the worst failure mode available: silent.

### Defect 2: `>=` contradicts the criterion AMENDMENT B itself states

AMENDMENT B's own Table 4-2 gives the stability equation as **`D.V <= 0.3`**. A
vehicle at exactly `D.V = 0.30` is therefore **stable**, i.e. FORD.

| implementation | test | verdict at `D.V = 0.30` exactly |
|---|---|---|
| live `vehicle_params.py:197` | `dv > cap` | **FORD**, matches the table |
| B7b proposal | `dv >= cap` | **NO-FORD**, contradicts the table |

Measured on the real grid, `data/scenario_sweep.csv`, 70 rows, counting rows
sitting exactly on a cap:

| class | on depth cap | on velocity cap | on D.V cap | row-tests flipped by `>=` |
|---|---|---|---|---|
| small_passenger | 7 | 10 | 4 | **21** |
| large_passenger | 7 | 10 | 2 | **19** |
| large_4wd | 7 | 10 | 4 | **21** |

The velocity cap alone accounts for 10 rows per class, because `v = 3.0` is a grid
point in the sweep. Under `>=`, every run at exactly the AR&R velocity cap flips
to NO-FORD.

### Defect 3, smaller but real: the rounding is load-bearing

Live code rounds before comparing: `round(depth_m * velocity_ms, 6) > limits["haz_m2s"]`.
The B7b block drops it. Measured effect on `data/scenario_sweep.csv`:

| class | rows changed by dropping `round(dv, 6)` | example |
|---|---|---|
| small_passenger | 2 | `d=0.1, v=3.0` gives `0.30000000000000004`, so `> 0.30` fires spuriously |
| large_passenger | 0 | |
| large_4wd | 2 | `d=0.2, v=3.0` gives `0.6000000000000001` |

4 rows total flip to NO-FORD purely from binary floating point. The rounding is
not decoration.

### Defect 4: key renames break existing readers

B7b renames `depth_m` to `still_water_depth_cap_m`, `velocity_ms` to
`velocity_cap_ms`, `haz_m2s` to `dv_cap_m2s`, and turns the membership bounds into
tuples. Existing readers of the old key names:

- `analysis/render_v1/gates_both_scenarios.py:39`
- `analysis/four_rung_ladder.py:16-27` (its own copy of the dict and rule)
- `analysis/render_v1/gates.py:17-29` (another copy)

Renaming without updating these leaves `KeyError` at best and a stale duplicate
rule at worst.

### Defect 5: the citation would move from primary to secondary

The live `AR_R_SOURCE` cites Shand et al. (2011) P10/S2/020 Table 3 with ISBN and
page. The B7b replacement cites Table 4-2 of Smith, Davey & Cox (2014) WRL
TR2014-07, which is a **reproduction** of the same table. Citing the reproduction
in place of the original is a downgrade. Citing **both** is an upgrade, and that
is what the corrected patch does.

---

## B7c. Three-axis class audit, every axis measured

Ground clearance was measured from the canonical mesh, not assumed. Method: in the
vehicle frame with the floor at z = 0, take the central longitudinal strip
(`|x| < 0.30 * halfwidth`, `|y| < 0.25 * length`), which excludes the wheels, and
take its minimum z.

**Validity check, because a watertight reconstruction can have a fake flat
underside.** Only 4.3% of strip vertices lie within 20 mm of that minimum, with a
z standard deviation of 3.86 mm, so the underbody has real structure and is not an
artificial cap. Separately, the vertices below z = 5 mm sit at `|y|` 1.150 to
1.385 m and `|x|` 0.670 to 0.791 m, which is where tyre contact patches belong
(axle half-spacing about 1.285 m, body half-width 0.873 m). The mesh rests on its
tyres, so the floor reference is sound and the clearance number is meaningful.

**Measured native ground clearance: 0.1737 m.** AMENDMENT B assumed about 0.135 m.

| class | lam | length | | mass | | clearance | | axes |
|---|---|---|---|---|---|---|---|---|
| small_passenger | 1.000 | 4.2826 | `< 4.3` PASS | 1100 | `< 1250` PASS | **0.1737** | `< 0.12` **FAIL** | 2/3 |
| large_passenger | 1.144 | 4.9000 | `> 4.3` PASS | 1609 | `> 1250` PASS | 0.1987 | `> 0.12` PASS | **3/3** |
| large_4wd | 1.214 | 5.2000 | `> 4.5` PASS | 2337 | `> 2000` PASS | 0.2109 | `> 0.22` **FAIL** | 2/3 |

**AMENDMENT B's conclusions hold, its numbers do not.** It predicted 0.172 m for
large passenger and 0.182 m for large 4WD; measured are 0.1987 and 0.2109. Both
pass/fail verdicts are unchanged, and its central point stands: **the baseline
small passenger class fails the clearance axis**, and large passenger is the only
class satisfied on all three.

Note also that length for small passenger passes by 17 mm (4.2826 against 4.3).
That is a real pass but it is not comfortable, and it deserves a footnote rather
than silence.

---

## B7d. The downstream recomputers, corrected and counted

### First, the file list in B7d is partly wrong

| named in B7d | actual status |
|---|---|
| `analysis/make_phase_space_v2.py` | **exists**, and does recompute inline |
| `plot_phase_space_live.py` | **path wrong.** It is at `analysis/plot_phase_space_live.py`. Recomputes inline at `:7`. |
| `wandb_backfill.py` | **exists at repo root but does NOT recompute.** `:15` reads `row["L1_verdict"]` straight from the CSV. The claim that it "recomputes L1 inline with its own hardcoded threshold" is false for this file. A different file, `analysis/wandb_backfill.py`, does recompute at `:24` using `L1_HAZ_THRESHOLD_4WD` imported from `thresholds`. |
| `designsafe-staging/scripts/make_phase_space.py` | **exists**, recomputes inline at `:9`, but reads `phase_space_results.csv` by **relative path and that file is not present** in either `designsafe-staging/` or `designsafe-staging/scripts/`. It cannot currently run. |

So the real count is **three** inline recomputers plus one CSV consumer, not four
recomputers.

### What the inline rule actually is

All three use `'FORD' if h <= 0.60 else 'NO-FORD'` on the product alone. That is
the **large 4WD** D.V cap applied to every row regardless of class, and it ignores
the depth cap and the velocity cap entirely. It is not a class-agnostic
simplification; it is the most permissive class silently applied to all.

### Row changes, measured against `data/phase_space_results.csv` (23 deduped rows)

| class the recomputer should use | rows changed | percent |
|---|---|---|
| small_passenger | **10 of 23** | 43.5% |
| large_passenger | **5 of 23** | 21.7% |
| large_4wd | **3 of 23** | 13.0% |

Examples: `(0.6, 0.0)` goes FORD to NO-FORD for every class, because the inline
rule sees a product of 0.0 and never checks the 0.30/0.40/0.50 depth cap. That is
a stationary vehicle in 0.6 m of water being reported as safe.

### A divergence B7d did not mention

The working tree uses `h <= 0.60`; the three copies under `.claude/worktrees/`
use `h < 0.60`. On `data/phase_space_results.csv` there are **3 rows with
`L1_haz` exactly 0.60**, so the working tree and the worktrees disagree on 3 rows
today. Whichever direction this is resolved, it should be resolved once, in
`L1_verdict`, not in five places.

---

## Recommended action

1. **Do not apply the B7b block.** Apply
   `analysis/vehicle_params_B7b_patch_PROPOSED.py` instead, which keeps the three
   genuine improvements and none of the five defects.
2. Point the three inline recomputers at `L1_verdict` with an explicit
   `vehicle_class`, and regenerate the affected figures. Expect 10, 5 and 3 rows
   to move depending on the class chosen.
3. Delete the duplicate rule copies in `analysis/four_rung_ladder.py:16-27` and
   `analysis/render_v1/gates.py:17-29`, or make them import.
4. Decide the `<=` versus `<` boundary once and record the decision, since the
   working tree and the worktrees currently disagree on 3 rows.
