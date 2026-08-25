# NHTSA finite-element vehicles: mass distribution, hull volume, and what the audit changed

2026-08-25. Every number below was measured on this machine or read from a primary
source on the date stated. Claims that did not survive checking are recorded as
withdrawn rather than deleted.

**Acknowledgement.** The vehicle models are the Center for Collision Safety and
Analysis (CCSA) at George Mason University finite element models, developed under
contract with the Federal Highway Administration (FHWA). Their READMEs ask that
CCSA at GMU and FHWA be acknowledged in any publication using them. That applies
to every figure and number in this document.

---

## 1. What was built

Four CCSA models converted from LS-DYNA keyword format to per-part meshes:

| vehicle | AR&R class | parts | faces | source |
|---|---|---|---|---|
| 2010 Toyota Yaris coarse v1l | small passenger | 905 | 374,931 | repo |
| 2012 Toyota Camry detailed v5a | large passenger | 1,068 | 2,206,660 | downloaded 2026-08-25 |
| 2020 Nissan Rogue v3 | large passenger | 1,267 | 4,889,698 | `~/Downloads/flood vehicle/` |
| 2007 Chevrolet Silverado coarse v3a | large 4WD | 585 | 251,692 | repo |

Geometry, measured from the meshes, against published specifications:

| | wheelbase measured | published | error |
|---|---|---|---|
| Yaris | 2.5387 m | 2.550 | -11.3 mm |
| Camry | 2.7899 m | 2.775 | +14.9 mm |
| Rogue | 2.7017 m | 2.705 | -3.3 mm |
| Silverado | 3.6436 m | 3.645 | -1.4 mm |

The Camry's overall length measures 4.8067 m against a published 4805 mm, 1.7 mm.

---

## 2. Primary-source validation of the mass-properties chain

The CCSA Yaris validation report resolves live from `doi.org/10.13021/G8JS5D`.
Slide 7, "Inertia Comparisons", read directly 2026-08-25:

| | Actual Vehicle | CCSA FE Model | computed here |
|---|---|---|---|
| Weight, kg | 1078 | 1101 | 1096.31 |
| Roll inertia, kg m^2 | 388 | 396 | 394.7 |
| Pitch inertia, kg m^2 | 1498 | 1545 | 1542.9 |
| Yaw inertia, kg m^2 | 1647 | 1718 | 1715.6 |
| CG Z, mm | 558 | 557 | 556.4 |

Mass within 0.43 percent, CG within 0.6 mm, all three inertias within 0.3 percent,
computed independently from the raw deck.

**The FE Model column is not recorded in CLAUDE.md, which carries only the Actual
Vehicle column.** It is the correct target for anything derived from the model
rather than from the car.

### The defect this exposed, in this work

A first pass gave 867.81 kg, 21.2 percent light. The missing mass is
`*ELEMENT_MASS_PART` in `set-yaris-coarse-v1l.key`: 28 entries, 228.50 kg.
867.81 + 228.50 = 1096.31.

**That block is captioned "Rear Payload" and the caption is wrong.** The entries
are non-structural mass lumped onto the parts it attaches to, spanning the full
height of the car: 30.0 kg on the gas tank, 17.5 on the IP beam, **16.0 on the
roof**, 11.5 on each of three chassis rails. A density profile built without it is
not merely 21 percent light, it is biased in the vertical direction, which is the
one thing such a profile exists to get right. Silverado equivalent: 263.57 kg.

Also fixed: LS-DYNA `_TITLE` keyword variants insert a title line before the data
card. Matching bare keywords silently skipped **172,574 Rogue elements** and
under-counted its mass by 15 percent. Now zero skipped.

---

## 3. Mass distribution in the solver

`solidify_watertight` fills the hull uniformly, so the CG lands at the geometric
centroid. Replacing that with the FE model's own height-resolved density, verified
on `g64_m1100`:

| | CG z | error | Ixx | Iyy | Izz |
|---|---|---|---|---|---|
| target (FE, scaled) | 0.5951 | - | 1503.2 | 410.9 | 1697.4 |
| uniform, as shipped | 0.6561 | +61.0 mm | 1501.6 | 395.2 | 1685.1 |
| 15-band profile | 0.6002 | +5.2 mm | 1508.6 | 396.3 | 1693.0 |

This does **not** wire inertia. CLAUDE.md item 4 forbids writing the tabulated
tensor in as a parameter and `params_check.py check_inertia_wired()` enforces it.
Only density versus height is set; the solver still derives CG and inertia from its
own particle cloud. Total mass stays at the wired value. Delivery is through
`set_material_range`, whose per-range `density` override is public API.

`additional_material_params` was rejected: `apply_additional_params`
(`mpm_utils.py:1302`) selects by position and does not filter by material, so it
would also re-densify water under the vehicle and in the wheel wells.

### Measured effect, 5 repeats per arm, same seed

| config | displacement A -> B | passthrough | **P-2 (limit 0.10)** | roll |
|---|---|---|---|---|
| Yaris g48 | 0.350084 -> 0.414283 | 0.1002 -> 0.0963 | **1/5 -> 5/5 PASS** | flat |
| Yaris g64 | 0.657258 -> 0.734397 | 0.1067 -> 0.0991 | **0/5 -> 5/5 PASS** | flat |
| Yaris g96dxm | 0.268927 -> 0.356599 | 0.0969 -> 0.0949 | 5/5 -> 5/5 | flat |
| Rogue g96 | 0.937448 -> 1.067660 | 0.1210 -> 0.1091 | 0/5 -> 0/5 | **0.274 -> 0.861 deg** |
| Silverado g96 | 0.233560 -> 0.287826 | 0.0925 -> 0.0905 | 5/5 -> 5/5 | flat |

CLAUDE.md item 7 names `g48_m1100` and `g64_m1100` among the seven canonical P-2
failures. Those are exactly the two configurations where the gate flips.

**Caveats, all load-bearing.** This ran on `sim_enhanced.py`'s code path, not
`sim_standing.py`, so it is a faithful surrogate and not the gated pipeline. The
g64 margin below the limit is 0.95 percent, which is thin. P-2 is a containment
check, not a physics validation (item 6), so passing it validates nothing. The
SLIDE verdict does not move anywhere: both arms sit far above `DRIFT_THRESHOLD`.

The control arm reproduces the canonical record on five independent numbers:
`realized_rho` 309.738367 at g64 and 302.554376 at g48, `final_disp_mag_m`
0.657258 +/- 0.001569 against the recorded 0.658537 (0.82 sigma), g48 z-rise near
-0.054, and P-2 failing at g64. Solver noise at fixed configuration and fixed seed
is 0.52 mm on a 269 mm displacement, 0.19 percent.

---

## 4. Displaced volume is a modelling choice, not a geometric property

A car has a grille, wheel wells, panel gaps and an open underbody. "The volume it
displaces" depends on which openings count as sealed. Flood fill from outside at a
stated sealing scale, Yaris:

| sealing scale | enclosed volume | % of bbox |
|---|---|---|
| 0.100 m | 7.3980 m^3 | 69.1 |
| 0.070 m | 6.8322 | 63.8 |
| 0.050 m | 3.6500 | 34.1 |
| 0.035 m | 2.9623 | 27.7 |
| 0.025 m | 2.4156 | 22.6 |

A factor of 3.06, and it does not converge. Buoyancy scales linearly with it.

**The project's hull corresponds to sealing at roughly 50 mm**, calibrated on two
independent vehicles: Yaris 3.6500 against a hull of 3.542739 (3 percent), Rogue
5.2483 against 4.950341 (6 percent).

This is supported by experiment. Kramer, Terheiden and Wieprecht 2016,
`10.1016/j.ijdrr.2016.04.003`, already cited in this project, report that
"floating water depths are higher in prototype than in model scale, which is due to
the use of a watertight vehicle model". A sealed model is more buoyant than the
real vehicle, which is the direction found here.

### The Silverado hull is wrong by 55 percent

Ray-crossing parity on both hulls:

| | total enclosed | rear 30% |
|---|---|---|
| project hull | 7.9647 m^3 (recorded 7.962083) | 2.3282 |
| flood-fill hull | 5.1484 | 1.3804 |

The three cars sit at 34 to 36 percent of their bounding box; the pickup's project
hull sits at 35.0 percent of the FE bounding box, where the flood fill gives 22.6.

**Withdrawn: "the hull seals the open cargo bed."** Both hulls have a bed cavity.
The bed accounts for 0.948 m^3 of a 2.816 m^3 excess, only 34 percent. The rest is
global inflation, visible in the render and measurable: the project hull is
**2.338 m wide against the FE model's 2.0284 m**, 310 mm too wide. The replacement
is 2.034 m, within 6 mm.

Also withdrawn: an earlier proposal to build hulls by Blender voxel remesh. Against
the Yaris ground truth it gives 1.63 to 1.69x and never converges.

### Effect of the corrected hull

| Silverado | old | new | change |
|---|---|---|---|
| hull_m3 | 7.962083 | 4.875501 | -38.8% |
| realized_rho | 137.484 | 229.237 | +66.7% |
| final_disp_mag_m | 0.233560 | 0.619791 | +165% |

The mechanism is not established. Less displaced volume means less buoyancy, more
normal force and more friction, which argues for less sliding, not nearly three
times more. It is also mildly confounded: `grid_lim` tracks hull extent so dx moved
1.4 percent. **This needs explaining before it is used.**

---

## 5. The AR&R classes are covered, and one of them does not hold

Table 3, read from `citations/ARR_Project_10_Stage2_Report_Final.pdf`, printed p.14:

| class | Length | Kerb | Clearance | still depth | high-v depth | v max | DV |
|---|---|---|---|---|---|---|---|
| Small passenger | < 4.3 | < 1250 | < 0.12 | 0.3 | 0.1 | 3.0 | <= 0.3 |
| Large passenger | > 4.3 | > 1250 | > 0.12 | 0.4 | 0.15 | 3.0 | <= 0.45 |
| Large 4WD | > 4.5 | > 2000 | > 0.22 | 0.5 | 0.2 | 3.0 | <= 0.6 |

The high-velocity depth column is exactly `DV_limit / 3.0`, per the table's own
footnotes, so it is redundant with the DV constraint and `vehicle_params.py` loses
nothing by omitting it.

Coverage: Camry, Rogue and Silverado satisfy all three criteria. The Yaris meets
length and kerb weight and exceeds the clearance maximum at 146.6 mm. That is not a
defect: **six of AR&R's own seven test vehicles also exceed 0.12 m** (0.15, 0.15,
0.155, 0.16, 0.17, 0.18; only the Honda Civic at 0.10 is under). The clearance
column is indicative of a class, not a gate.

The Silverado's class turned on a brake drum: 217.0 mm measured including rotating
unsprung parts, 225.9 mm excluding them, against a 220 mm bound.

### Same class, different outcome

Camry and Rogue are both large passenger and receive identical published
thresholds. With matched hull provenance, the same mass, and dx within 3 percent:

| | hull m^3 | dx | displacement | passthrough | P-2 |
|---|---|---|---|---|---|
| Camry | 4.9398 | 0.1111 | 0.8200 +/- 0.0017 | 0.0863 | PASS |
| Rogue | 5.6286 | 0.1078 | 0.7072 +/- 0.0008 | 0.1221 | FAIL |

16.0 percent apart in displacement, and on opposite sides of a gate. This is a
direct measurement of what CLAUDE.md A-3 asserts from the literature: the
thresholds depend on displaced volume and underbody shape, not mass alone.

Read only this pair across vehicles. dx ranges 0.0982 to 0.1342 across the four
because `grid_lim` follows hull extent, the confound the hullsweep sbatch warns of.

AR&R itself names "small and large commercial vehicles" as classes needing
criteria. None were ever published, so no vehicle could be scored there.

---

## 6. What is still absent

**Added mass.** Searched, not assumed. The project corpus tags 6 papers
`added-mass`: oscillating offshore cylinders, streambed sediment twice, a rowing
oar, planing hulls, and a 1969 sphere. A scite search for added mass with vehicle
and flood returns damaged ships and autonomous underwater vehicles. **No published
work applies an added-mass term to a road vehicle in floodwater.** The nearest is
Azhar, Bui and Pauwels 2026, `10.1111/jfr3.70181`, which treats the same physics as
an unsteady drag increase rather than an added-mass term.

**Water ingress.** The hull is sealed. This is the same axis as the sealing scale
above, but time-dependent rather than static.

**Wheel rotation and suspension compliance.** Absent; the hull is one rigid body.

**Resolution.** Two grid cells across the flow depth, 1.5 across the Yaris minimum
clearance. No mass-distribution or hull fix changes that.

---

## 7. Claims withdrawn in this pass

1. "No FE Rogue exists." It was on the laptop at
   `~/Downloads/flood vehicle/2020-nissan-rogue-v3/rogue-v3.key` the whole time.
   Absence was concluded from a search bounded to the repo and one Downloads
   subdirectory.
2. "The hull is 2.5 percent short in length so it under-presents area to the flow."
   Backwards. Measured by orthographic render with pixel counting, converged over
   three resolutions, the hull **over**-presents by 5.93 percent overall and 3.35
   percent submerged.
3. "No gate moves." P-2 flips at g48 and g64.
4. "The Silverado hull seals its open bed." Only 34 percent of the excess; the rest
   is global inflation.
5. Voxel remesh as a hull generator. Failed calibration.
6. Ground clearance "177 mm" recalled from memory. Live values are 180.554 median
   and 146.952 minimum, and an independent FE measurement gives 146.6 mm.

Two measurement methods were also discarded after failing convergence checks:
rasterising a particle cloud (867 occupied cells at both 0.02 and 0.01 m) and
rasterising surface-mesh vertices (area fell 4.54 -> 4.11 -> 2.82 m^2 as the cell
shrank). Point-sampling a surface cannot measure its area.
