# Third-party notices

The root [`LICENSE`](LICENSE) (BSD 3-Clause) covers only the code and documentation written for
this project. Everything below keeps its own terms. Licences were checked at the source on
2026-08-18.

| Material | Path | Source | Licence as found |
|---|---|---|---|
| Vehicle finite element models: 2010 Toyota Yaris and 2007 Chevrolet Silverado, coarse and detailed | `vehicle_geometry_research/` | Center for Collision Safety and Analysis (CCSA), George Mason University, sponsored by FHWA. [DOI 10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D) | No licence statement in the distributed files. The upstream README asks that CCSA at GMU and FHWA be acknowledged in any resulting publication; this repository's README does so. |
| Watertight Yaris hull and reconstruction meshes (`.ply`) | `vehicle_geometry_research/` | Derived by this project from the CCSA Yaris coarse v1l model | Same terms as the source model |
| warpmpm solver core (mpm-engine) | `third_party/mpm-engine-544c93dd/`, `third_party/mpm-engine-544c93dd-solver-core/` | [`kks32/mpm-engine`](https://github.com/kks32/mpm-engine) at `544c93dd` | MIT, `LICENSE` retained in both trees |
| mpm-engine reference scripts | `citations/kks32_mpm_engine/` | `kks32/mpm-engine` | MIT, header retained in each file |
| Asphalt015 PBR texture set | `assets/Asphalt015*` | [ambientCG](https://ambientcg.com/) | CC0 1.0 |
| Dasallas 2025, *J. Flood Risk Management* | `citations/J Flood Risk Management - 2025 - Dasallas - ....pdf` | [DOI 10.1111/jfr3.70154](https://doi.org/10.1111/jfr3.70154) | CC BY |
| AR&R Project 10 Stage 2 report, and its Table 1 as an image | `citations/ARR_Project_10_Stage2_Report_Final.pdf`, `citations/ARR table 1 - ....png` | Shand, Cox, Blacka and Smith 2011, Engineers Australia report P10/S2/020, ISBN 978-0-85825-948-5 | No licence statement found in the document |
| Figure 5-5 and Tables 5-1 and 5-2 from WRL Technical Report 2014/07 (3 images) | `citations/WRL reports technical and Research/` | Water Research Laboratory, UNSW, September 2014 | No licence statement found |
| PhysGaussian algorithm | `bridge/` | Xie et al. 2023, [arXiv:2311.12198](https://arxiv.org/abs/2311.12198) | No upstream code is included. `bridge/` is an independent NumPy implementation of the published method. |

Two cited articles are referenced by DOI only and are not included: Smith, Modra and Felder 2019
([10.1111/jfr3.12527](https://doi.org/10.1111/jfr3.12527), closed access) and Wang and Marsooli
2021 ([10.1029/2020WR028616](https://doi.org/10.1029/2020WR028616)).

## Rights holders

If you hold rights in any of this material and want it changed or removed, please open an issue at
https://github.com/jcerrell-IS/can-it-ford.
