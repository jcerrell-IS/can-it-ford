# Third-party notices

The BSD 3-Clause licence in `LICENSE` applies only to the original code and documentation written
for this project. It does not apply to the third-party material below, which keeps its own terms.

## Included in this repository

| Material | Path | Source | Licence |
|---|---|---|---|
| Vendored `warpmpm` solver, pinned at `544c93dd02cb9c7ead89e1155a62967243244fce` | `third_party/mpm-engine-544c93dd/`, `third_party/mpm-engine-544c93dd-solver-core/` | [kks32/mpm-engine](https://github.com/kks32/mpm-engine) | MIT, with its `LICENSE` file kept in both trees. Copyright (c) 2026 The mpm-engine authors |
| mpm-engine reference scripts | `citations/vehicle(kks32).py`, `citations/splat_sim(kks32).py` | mpm-engine authors | MIT, full header kept in each file |
| Asphalt015 texture set, DaySkyHDRI002A sky | `assets/` | [ambientCG](https://ambientcg.com) | CC0 1.0 |
| Kloofendal 43d Clear (Pure Sky) HDRI | `assets/hdri/` | [Poly Haven](https://polyhaven.com) | CC0 |
| Dasallas (2025), *Integration of Stability Functions Into a Transport Flood Risk Modelling Framework*, Journal of Flood Risk Management, [10.1111/jfr3.70154](https://doi.org/10.1111/jfr3.70154) | `citations/` | Wiley, gold open access | CC BY, attribution given here |

`bridge/` is an independent NumPy implementation of the published PhysGaussian algorithm (Xie et
al., arXiv:2311.12198). It contains no upstream source code. The upstream repository,
`XPandora/PhysGaussian`, has no licence file.

## Used by this project but not redistributed

Their licences are unresolved or don't permit redistribution, so these are not in this
repository. Obtain them from the source.

| Material | Where to get it |
|---|---|
| 2010 Toyota Yaris and 2007 Chevrolet Silverado finite element models, and the watertight hull derived from the Yaris model | Center for Collision Safety and Analysis (CCSA), George Mason University, <https://www.ccsa.gmu.edu/>. Documentation: [10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D). See `vehicle_geometry_research/README.md` |
| Shand, Cox, Blacka and Smith (2011), *Australian Rainfall and Runoff Project 10: Appropriate Safety Criteria for Vehicles*, Stage 2 report P10/S2/020, ISBN 978-0-85825-948-5 | Engineers Australia |
| Smith, Modra and Felder (2019), *Full-scale testing of stability curves for vehicles in flood waters*, Journal of Flood Risk Management | [10.1111/jfr3.12527](https://doi.org/10.1111/jfr3.12527) (closed access) |
| Wang and Marsooli (2021), *Physical Instability of Individuals Exposed to Storm-Induced Coastal Flooding: Vulnerability of New Yorkers During Hurricane Sandy*, Water Resources Research | [10.1029/2020WR028616](https://doi.org/10.1029/2020WR028616) (CC BY-NC-ND) |
| WRL Technical Report 2014/07, combined flood hazard curves | Water Research Laboratory, UNSW |

## Acknowledgement

As the model's authors request, this project acknowledges the CCSA at George Mason University and
the Federal Highway Administration (FHWA) for the 2010 Toyota Yaris finite element model.

If you hold rights in anything listed here, please open an issue on this repository.
