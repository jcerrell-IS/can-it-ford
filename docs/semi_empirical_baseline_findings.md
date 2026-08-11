# Semi-empirical sliding-onset baseline against L1

Date: 2026-08-08
Script: `scripts/semi_empirical_baseline.py`
Input: `data/scenario_sweep.csv` (unmodified, commit `cf5bda9`, 2026-07-29, 10 columns, 70 rows)
Output: `data/semi_empirical_baseline_2026-08-08.csv`

Reproduce with:

```bash
python3 scripts/semi_empirical_baseline.py
```

Pure standard library, no numpy, no pandas, no trimesh (none are installed on this Mac,
checked live against `/opt/homebrew/bin/python3`, `/usr/bin/python3` and `python3.12`).

---

## 1. Which formula path was used

**The first-principles fallback. Not Xia or Shu.**

Both target papers were located through the Scite connector and both are behind a paywall.
Retrieval failed again, exactly as in the earlier session.

| Paper | DOI | Scite result |
|---|---|---|
| Xia, Falconer, Xiao and Wang, *Criterion of vehicle stability in floodwaters based on theoretical and experimental studies*, Natural Hazards 70(2):1619-1630 | `10.1007/s11069-013-0889-2` | `isOa: false`, `oaStatus: "closed"`, `contentDenied: true`, zero full-text excerpts, access purchase-only (USD 37.95 buy / 19.00 rent) |
| Shu, Xia, Falconer and Lin, *Incipient velocity for partially submerged vehicles in floodwaters*, Journal of Hydraulic Research 49(6):709-717 | `10.1080/00221686.2011.616318` | `isOa: false`, `oaStatus: "closed"`, `contentDenied: true`, zero full-text excerpts, abstract field empty, access purchase-only (USD 73.95 buy / 25.00 rent) |

The published sliding and toppling conditions, and specifically the ground-slope term from the
2014 paper, were **not** retrieved, are **not** verified, and are **not** implemented here.
Per the instruction, no attempt was made to reconstruct them from citing papers. Several citing
papers were returned by the same search and describe the formulae in prose, but prose about an
equation is not the equation, and reconstructing from it would produce a citation that does not
trace.

Two incidental bibliographic notes from the retrieved records:

- Scite stamps the Xia paper `year: 2013`, `date: 2013-10-11`. That is the online-first date.
  The print issue is volume 70, issue 2, pages 1619-1630, which is 2014. This is consistent
  with the existing project note that the correct citation year is 2014, not 2013.
- Scite lists only the first three authors (Xia, Falconer, Xiao), which is its display cap, not
  evidence that Wang is absent.

An independent open-access check via Unpaywall was attempted and could not be completed: one
call returned `Too many requests` and the other returned `You are not subscribed to this API`.
So the paywall finding rests on Scite alone.

---

## 2. What the fallback actually computes

For each row, at flow depth `d` and depth-averaged velocity `V`:

```
f_sub(d)   = min(d, H_hull) / H_hull
V_sub(d)   = V_hull * f_sub(d)
F_buoy(d)  = rho_w * g * V_sub(d)
N(d)       = max(0, m*g - F_buoy(d))
F_fric(d)  = mu * N(d)
A(d)       = W_hull * min(d, H_hull)
F_drag     = 0.5 * rho_w * C_D * A(d) * V^2

sliding onset:  F_drag = F_fric
V_c(d)     = sqrt( 2 * mu * N(d) / (rho_w * C_D * A(d)) )

verdict:   NO-FORD if V >= V_c(d), else FORD
```

Units check: `N / (kg/m^3 * m^2)` is `(kg m/s^2)/(kg/m)` is `m^2/s^2`, whose square root is m/s.

### Inputs and their provenance

| Symbol | Value | Source, verified live |
|---|---|---|
| `rho_w` | 1000 kg/m^3 | CLAUDE.md physical-anchor list |
| `g` | 9.81 m/s^2 | CLAUDE.md audit item 3, solver hardcodes `g=[0,0,-9.81]` at `core/solver.py:167-169` |
| `m` | 1100.0 kg | `vehicle_params.py:125`, `compact_sedan.mass_kg` |
| `V_hull` | 3.542739 m^3 | `vehicle_geometry_research/failed_reconstructions_2026-07-25/README.md:17`, canonical `yaris_coarse_v1l_watertight.ply`; corroborated at `renders/yaris_render_s1/g0_validate.py:12` and in every `renders/yaris_render_s1/*/summary.json` `hull_m3` field |
| `W_hull`, `H_hull` | 1.7464 m, 1.5180 m | same README.md:17 row as the volume, so extents and volume share one source line |
| `mu` | 0.55 | `renders/yaris_render_s1/sim_standing.py:84` and `:235`, `floor_friction=0.55`, the value used across all 17 canonical runs |
| `C_D` | 1.22 to 6.82, midpoint 4.02 | **UNVERIFIED, see section 3** |

Two internal consistency checks pass exactly, which is the main evidence the implementation is
not arithmetically broken:

- Effective vehicle density `1100 / 3.542739 = 310.494 kg/m^3`, matching the CLAUDE.md anchor
  310.494 to three decimals.
- At the computed flotation depth 0.471330 m, submerged volume is 1.100000 m^3 against
  `m / rho_w = 1.100000 m^3`, and buoyant force is 10791.000 N against weight 10791.000 N.

### Vehicle class

The delivered CSV is computed for **1100 kg only**. That is deliberate. The hull volume
3.542739 m^3 and the extents 1.7464 by 1.5180 m are the Yaris's, and `vehicle_params.py:121-122`
maps `compact_sedan` to the AR&R "Small Car" class, which is the class the `L1_verdict` column
in `scenario_sweep.csv` is computed against (verified: `L1_verdict` and
`L1_verdict_small_passenger` agree on all 70 rows). Pairing 1990 kg or 2300 kg with a Yaris hull
would be a mass-only perturbation of the wrong geometry, not a vehicle-class result. Those two
masses are reported in the sensitivity block and should be read as nothing more than that.

Separately, on the note in the task framing: it is CLAUDE.md **item 10**, not item 6, that
records 1609 kg and 2337 kg as having no source in `vehicle_params.py`. Item 6 is the "no gate
is a physics validation" item. The substance is unaffected, and the masses used here (1100,
1990, 2300) all trace to `vehicle_params.py` directly.

### Approximations that are mine, not sourced

- **Submerged fraction is prismatic**, `f(d) = min(d, H)/H`. The hull is not prismatic: it
  fills 31.2 percent of its own bounding box. This is the largest geometric approximation in
  the model. Slicing the real mesh would be better and was not done, because no numpy or
  trimesh is installed and a pure-Python clip over 655,308 faces was not worth the added
  unvalidated code in a baseline script.
- **Reference area is the submerged frontal rectangle**, `A = W_hull * min(d, H)`. This is a
  convention, not a measurement.

---

## 3. The C_D provenance failure, stated plainly

The prescribed range 1.22 to 6.82 **could not be traced to any source**. Checked live:

- `docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md` **does not exist on disk**.
- `git log --all -- docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md` returns **empty**,
  so that file has never existed anywhere in this repository's history. CLAUDE.md line 405
  cites it by name as a demoted-to-historical file, which makes that line a dangling pointer.
- The string `6.82` appears **nowhere** in `docs/`.
- The PII `S0022169423004675` appears **nowhere** in the repository.
- The Journal of Hydrology article itself was not fetched, so the range has not been checked
  against its primary source either. It is unverified, not disproven.

What the repository *does* contain on vehicle drag, all pointing lower:

| Value | Kind | Location |
|---|---|---|
| C_D = 1.38 | directly **measured**, average | `docs/LIT_QUEUE_2026-07-30.md:59-60`, from the Smith, Modra and Felder full-scale traction study abstracted at `docs/Dynamic_Vehicle_Traction_in_Floodwater.md` |
| C_D = 1.1 | assumed in a desk study | `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:226`, Keller and Mitsch 1993 |
| "less than 1 for supercritical, more than 1 for subcritical" | CFD | `docs/Dynamic_Vehicle_Traction_in_Floodwater.md:329` |

The prescribed midpoint of 4.02 is roughly **three times** the only directly measured value on
disk. That does not make 4.02 wrong, since a flume study on a bluff partially submerged body can
legitimately report high C_D depending on the reference area it normalises against. But the
reference-area convention is precisely what cannot be checked, because the source is missing.
C_D and A are not separable: a C_D is only meaningful paired with the area it was defined
against. So the uncertainty here is wider than the quoted 1.22 to 6.82 band suggests.

The delivered CSV uses the prescribed midpoint 4.02, as instructed. The measured 1.38 is
reported alongside it as a comparator and is **not** used for the CSV.

---

## 4. Results

Incipient velocity by depth (m/s). Higher C_D means more drag, so a lower incipient velocity.

| depth (m) | C_D = 1.22 | C_D = 4.02 (point) | C_D = 6.82 | C_D = 1.38 (measured) |
|---|---|---|---|---|
| 0.1 | 6.6251 | 3.6497 | 2.8021 | 6.2292 |
| 0.2 | 4.0045 | 2.2060 | 1.6937 | 3.7652 |
| 0.3 | 2.5982 | 1.4313 | 1.0989 | 2.4429 |
| 0.4 | 1.4518 | 0.7998 | 0.6141 | 1.3651 |
| 0.5 and deeper | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

At the point estimate, depth 0.1 m has `V_c = 3.6497 m/s`, above the sweep's 3.0 m/s cap, so
that entire depth row is FORD by construction rather than by discrimination.

At and beyond 0.5 m the vehicle floats: computed flotation depth is **0.471330 m**, at which
buoyancy cancels weight, the normal force goes to zero, and so does the friction available to
resist any flow at all. `V_c = 0` means unstable even in still water. As a plausibility anchor,
the CFD study abstracted at `docs/Dynamic_Vehicle_Traction_in_Floodwater.md:329` reports
floating instability at 0.38 m for a medium-size passenger vehicle. Different vehicle and
different method, so this is a sanity check on the order of magnitude, not agreement.

### Overall agreement with `L1_verdict`

**67 of 70 rows agree, 95.71 percent.**

That headline number is misleading on its own, and should not be quoted without the split
below.

| Region | Rows | Agree | Rate |
|---|---|---|---|
| `d <= 0.4` (informative) | 28 | 25 | 89.29% |
| `d >= 0.5` (both saturated) | 42 | 42 | 100.00% |

60 percent of the grid sits at depths where the semi-empirical model says the car is already
floating and L1 says the depth exceeds the 0.30 m small-passenger cap. Both return NO-FORD, for
different reasons, and both would keep returning NO-FORD under almost any parameter choice.
That block of 42 rows is agreement by saturation and carries close to no information. Of all 67
agreements, 53 are NO-FORD/NO-FORD and only 14 are FORD/FORD.

One structural result is worth recording: **there is no row where L1 says FORD and the
semi-empirical model says NO-FORD.** All 14 L1 FORD rows are also semi-empirical FORD. On this
grid the force balance is uniformly the *less* conservative of the two, so it never contradicts
L1 in the unsafe direction.

### Every disagreement

Three rows, all in the same direction (semi-empirical permits, L1 forbids):

| depth (m) | velocity (m/s) | L1_verdict | semi-empirical | V_c (m/s) | why they differ |
|---|---|---|---|---|---|
| **0.2** | **2.0** | NO-FORD | FORD | 2.2060 | L1 fails it on the depth-velocity product: `0.2 * 2.0 = 0.40 m^2/s` against the small-passenger cap of 0.30. The force balance puts onset at 2.206 m/s, so 2.0 m/s is still 9 percent below sliding. |
| **0.4** | **0.0** | NO-FORD | FORD | 0.7998 | L1 fails it on depth alone: 0.4 m exceeds the 0.30 m cap, regardless of velocity. At 0.4 m the hull is 26.4 percent submerged, buoyancy has removed 85 percent of the normal force, but 1633 N of normal force and 898 N of friction remain, and still water applies no drag. |
| **0.4** | **0.5** | NO-FORD | FORD | 0.7998 | Same depth-cap mechanism. 0.5 m/s is below the 0.7998 m/s onset. |

All three are cases where L1's **depth cap** (or the D*V product cap) bites before the sliding
force balance does. This is expected and is not evidence that either is wrong: the AR&R caps
are not pure sliding criteria, they also encode flotation and loss-of-control margins that a
sliding-only force balance does not model at all.

### Sensitivity

| Variation | Agreement |
|---|---|
| C_D = 1.22 (unsourced lower bound) | 61/70 = 87.14% |
| C_D = 4.02 (unsourced midpoint, **delivered**) | 67/70 = 95.71% |
| C_D = 6.82 (unsourced upper bound) | 67/70 = 95.71% |
| C_D = 1.38 (measured, in-repo) | 62/70 = 88.57% |
| mu = 0.30 (worst case, measured) | 67/70 = 95.71% |
| mu = 0.55 (**delivered**, sim value) | 67/70 = 95.71% |
| mu = 0.78 (wet concrete, measured) | 65/70 = 92.86% |
| mass 1990 kg on the Yaris hull | 49/70 = 70.00% |
| mass 2300 kg on the Yaris hull | 44/70 = 62.86% |

The agreement rate swings from 87.14 to 95.71 percent across the prescribed C_D band alone. The
delivered 95.71 percent is what the **midpoint** happens to produce. It is not a fitted optimum,
but it is also not a prediction that survived a test it could have failed.

---

## 5. Is this independent validation of L1

**No. It is a consistency check, and a weak one.**

The task framing asked specifically about the shared friction coefficient. That particular
concern turns out not to apply, and the real problems are elsewhere.

**The friction overlap is not with L1.** `L1_verdict` in `vehicle_params.py:228-241` uses only
`AR_R_STABILITY_LIMITS`: a depth cap, a velocity cap, and a depth-velocity product cap. There
is no friction coefficient anywhere in that path. Verified live: `/usr/bin/grep -n "mu\|friction"
vehicle_params.py` returns exactly two lines, `:5` and `:268`, and both are the letters "mu"
inside the word "simulation" in a docstring. There is no friction variable and no friction
constant in the file. So this baseline and L1 do **not** share mu = 0.55.

Where mu = 0.55 *is* shared is with the 17 canonical MPM runs, which take it as `floor_friction`.
So this baseline is not independent of the **L2/MPM** results, and must never be presented as an
external check on those. Against L1 specifically, the friction coefficient is not the problem.

The reasons it still is not independent validation:

1. **The one free parameter was not constrained by anything.** C_D is the only knob in the model
   that was not read from a repo file or a primary source, and it moves the answer by 8.6
   percentage points across its own prescribed band. A check whose headline number depends on an
   untraceable constant is not a validation, it is a calculation with an assumption in it.
2. **The agreement is mostly structural.** 42 of 70 rows agree only because both methods
   saturate to NO-FORD in deep water. The informative region is 28 rows, and there the rate is
   89.29 percent, not 95.71 percent.
3. **The two methods are not measuring the same thing.** The force balance models sliding onset
   only. The AR&R criteria are empirical stability criteria for stationary vehicles
   (`vehicle_params.py:200-205`, Shand, Cox, Blacka and Smith 2011, Table 3, and the report's
   own text marks them DRAFT INTERIM, not an endorsed standard) and they fold in flotation and
   other loss-of-stability modes. All three disagreements are exactly at that seam. Agreement
   between them is partly a coincidence of where two different criteria happen to cross.
4. **They are not causally independent in origin.** The AR&R limits are themselves empirical
   fits from vehicle stability testing, that is, from the same physical phenomenon and broadly
   the same experimental lineage (recorded at
   `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:226`) that any credible C_D and mu for a
   flooded vehicle would also be drawn from. Two descriptions of one experimental tradition
   agreeing is not two independent lines of evidence.

**What it is legitimately good for.** It is a cheap analytic sanity check that the L1 verdict
surface is not obviously unphysical, and it produces one genuinely reportable structural
result: the sliding force balance never permits less than L1 anywhere on this grid, so L1 is
the more conservative of the two everywhere it was tested.

**What would make it validation.** Retrieve the Xia 2014 and Shu 2011 formulae from the primary
PDFs (both are purchasable, or reachable through a university library) and implement them as
published, including the ground-slope term, with their own calibrated coefficients rather than a
free C_D. Until then the honest description in the paper is "an independent analytic
cross-check of the L1 threshold surface under stated assumptions", never "validation", and the
C_D provenance gap has to travel with any number quoted from this file.

---

## 6. Open items this produced

1. **CLAUDE.md line 405 is a dangling pointer.** It demotes
   `docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md` to historical, but that file has never
   existed in git history. Either the filename is wrong or the content lives elsewhere. Until
   that is resolved, anything cited to it is uncited.
2. **The C_D range 1.22 to 6.82 has no traceable origin** and disagrees by roughly 3x with the
   only measured value in the repository (1.38). Resolve before any figure or paper text uses it.
3. **The prismatic submerged-fraction approximation is unquantified.** It could be replaced with
   a real mesh slice of `yaris_coarse_v1l_watertight.ply` once numpy or trimesh is available,
   and the difference in flotation depth measured rather than assumed small.
