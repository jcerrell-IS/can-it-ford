---
title: Can It Ford
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: bsd-3-clause
---

# Can It Ford?

**Autonomous vehicle flood traversability via reconstruct-to-decide world models**

Given a real flooded road, this project asks whether a specific vehicle can ford the crossing, and looks for the simplest physical abstraction that still answers correctly.

This Space is the interactive front end for the two lightweight abstraction levels. Enter a depth and a velocity and it returns both verdicts live.

## Abstraction levels

| Level | Model | Status |
|---|---|---|
| L0 | Static depth threshold, D >= 0.15 m gives NO-FORD (NWS Turn Around Don't Drown) | Live in this demo |
| L1 | AR&R stationary-vehicle stability, joint rule over depth, velocity and the D x V hazard product, class dependent | Live in this demo |
| L2 | Full physics, warpmpm MPM, weakly compressible Newtonian water coupled to the rigid vehicle hull | Runs offline on GPU, no L2 number is shown here |

## L1, the joint rule

All three conditions must hold for FORD. Failing any one gives NO-FORD.

| AR&R class | Depth cap | Velocity cap | D x V cap |
|---|---|---|---|
| Small passenger | 0.30 m | 3.0 m/s | 0.30 m2/s |
| Large passenger | 0.40 m | 3.0 m/s | 0.45 m2/s |
| Large 4WD | 0.50 m | 3.0 m/s | 0.60 m2/s |

The 2010 Toyota Yaris used throughout this project maps to **Small passenger**, so that is the default here.

These figures are reproduced from the report's own Table 3, "Proposed DRAFT Stability Criteria for Stationary Vehicles". They are draft interim criteria for **stationary** vehicles. They are not an endorsed safety standard.

An earlier version of this demo tested the hazard product alone against the Large 4WD figure of 0.60 m2/s, with no depth or velocity cap. That returned FORD for a large set of conditions the joint rule calls NO-FORD, so it was replaced. The thresholds and the rule here are copied from `vehicle_params.py` rather than restated, and are checked against it.

## L2 status

- **Engine: warpmpm.** The gated runs are warpmpm, not Genesis. Genesis was used only for an earlier box-proxy track, which is superseded and is not the gated result.
- **Vehicle:** the canonical 2010 Toyota Yaris hull, 1100 kg over a 3.542739 m3 watertight hull volume, giving the reference effective density of 310.494 kg/m3 that the gates check against. The density actually realised by the solidified particle cloud is grid dependent and is not identical to that reference: it spans 302.6 to 312.3 kg/m3 across the three 1100 kg runs.
- A previous version of this page gave rho = 115.7 and a roughly 1390 kg target mass. Those numbers describe a rectangular box proxy, not the Yaris hull, and are superseded.

Two limitations belong next to any L2 number, so they are stated here rather than in a footnote:

1. The gates in this project are self-consistency and numerical-containment checks. None of them is a physics validation against measured data.
2. Failure-mode classification across the 17 gated runs gives 16 SLIDE and 1 STUCK. That result is **not** established as grid-converged: the canonical set has not been run at the next refinement level, so the verdict split should not be read as resolution independent.

## Sources

- NWS Turn Around Don't Drown depth guidance
- Shand, Cox, Blacka & Smith (2011), Australian Rainfall and Runoff Project 10 Stage 2, P10/S2/020, ISBN 978-0-85825-948-5, Table 3
- Thorpe, Tretiakov, Hsiao, Low, Li, Iqbal, Bhatt, Topcu & Kumar (2026), *Physically Viable World Models: A Case for Query-Conditioned Embodied AI*, arXiv:2605.30542

## Safety

This is a research demo built on draft interim criteria for stationary vehicles. It is not a safety tool and must not be used to decide whether to drive into floodwater. Turn around, don't drown.

## About

Josie Cerrell, NSF SCIPE REU 2026, GeoElements Lab, UT Austin (PI: Krishna Kumar).
This project contributes the reconstruct-to-decide pipeline and the abstraction-ladder experiment.
