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
| L1 | Depth-velocity hazard scalar H = D x V, threshold 0.60 m2/s for the Large 4WD class (AR&R Shand et al. 2011, draft and interim criterion, not an endorsed safety standard) | Live in this demo |
| L2 | Full physics, Genesis MPM weakly-compressible water coupled to a rigid vehicle | Under active rebuild, no verdict published yet |

## L2 status

L2 is being rebuilt and has not produced a published verdict. The vehicle is modeled at a corrected density of rho = 115.7, giving the roughly 1390 kg target mass used across the project. No L2 result numbers are shown here until the rebuilt simulation is validated.

## Sources

- NWS Turn Around Don't Drown depth guidance
- Australian Rainfall and Runoff, Shand et al. 2011, vehicle stability hazard thresholds (draft and interim)
- Framing: query-conditioned physically viable world models, arXiv:2605.30542

## About

Josie Cerrell, NSF SCIPE REU 2026, GeoElements Lab, UT Austin (PI: Krishna Kumar).
This project contributes the reconstruct-to-decide pipeline and the abstraction-ladder experiment.
