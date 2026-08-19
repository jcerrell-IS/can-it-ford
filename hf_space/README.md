---
title: Can It Ford
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.24.0
app_file: app.py
pinned: false
license: bsd-3-clause
---

# Can It Ford?

**Vehicle stability in floodwater: the spread, and where the verdict flips.**

Given a flooded roadway, this project asks whether it is safe for a specific vehicle to
attempt a crossing. It answers through stationary-vehicle stability, which is a
**necessary** condition, not a sufficient one.

The published literature reports thresholds and single points. This Space shows two
things that a threshold hides:

1. **the spread**, so a result reads as an ensemble rather than a point;
2. **where a verdict flips** as a deciding threshold is moved, so a reader can see which
   results depend on a choice rather than on a measurement.

## The three panels

| panel | what it shows | data state |
|---|---|---|
| Where the verdict flips | peak surge drift for each gated run against a movable distance threshold | live, 17 runs |
| Load surface, `v_car` x `v_water` | vehicle speed and flow speed as **separate** axes, where the field usually collapses them into one relative speed | **schema only, no data yet** |
| Repeat spread | two independent draws of the same configuration | live, 3 configurations |

## Engine

The gated runs use **warpmpm**, a material point method solver, via
`renders/yaris_render_s1/sim_standing.py`.

**They are not Genesis.** Genesis was an earlier box-proxy path that never loaded the
vehicle hull. An earlier version of this page described the physics level as "Genesis
MPM"; that was wrong and is corrected here.

## Corrections to the previous version of this page

Three claims on the earlier version of this Space were checked against canonical sources
on 2026-08-19 and did not survive. They are recorded rather than quietly removed.

1. **"Genesis MPM"** as the physics engine. The gated runs are warpmpm. Corrected above.
2. **"a corrected density of rho = 115.7, giving the roughly 1390 kg target mass used
   across the project."** Neither figure is canonical. The canonical vehicle mass is
   **1100 kg**, and the canonical hull effective density is **310.494 kg/m^3**. The 115.7
   value belongs to a superseded box-proxy path, and the 1390 kg box comes from a sweep
   the project marks deprecated and instructs not to source figures from.
3. **"L2 is being rebuilt and has not produced a published verdict."** Stale. Seventeen
   gated runs exist with classified outcomes. What remains true, and is stated in the app,
   is that none of the gates is a physics validation.

## What is deliberately not here

**No rendered imagery, textures, HDRIs or meshes.** Asset provenance for this project's
render inputs is an open, unresolved licence question. Derived numbers are shown; image
assets are not, until that is settled. The dataset build script enforces this in code
rather than by convention.

## Limitations, stated as strongly as the results

- **Resolution is not converged.** The water column is resolved by roughly 2 grid cells
  and 4 particle layers, against a rule of thumb of about 10 particles per flow depth.
  Displacement magnitude is non-monotone under grid refinement, so cite the verdict and
  never the magnitude.
- **Coarse resolution usually over-predicts peak hydrodynamic force**, which makes
  over-threshold verdicts conservative for safety. That does not make them converged.
- **No gate is a physics validation.** The gates are self-consistency and numerical
  containment checks. Several compare against a reference derived from the same pipeline,
  so they cannot fail for a reason external to the code.
- **`sustain_frames = 3` has no published source.** No vehicle-stability criterion
  reviewed for this project uses a persistence count at all, yet it gates every verdict.
- **The load-surface vehicle is prescribed, not free.** When that panel is populated, the
  body is held on a path and the reaction load is measured. It cannot be swept away.
  **No FORD or NO-FORD verdict is derivable from it.**
- **The scenario is a stationary vehicle in flow**, which matches the validated stability
  criterion. The word "ford" implies motion; it is the title that mismatches, not the
  setup.

## Running locally

```
pip install -r requirements.txt
python app.py
```

Regenerate `data/` from the canonical repository with:

```
python3 analysis/hf_dataset_publish.py --out hf_space/data
```

Test the logic without a browser:

```
python3 hf_space/surface.py
```

## About

Josie Cerrell, NSF REU, GeoElements Lab, UT Austin. PI Krishna Kumar.
