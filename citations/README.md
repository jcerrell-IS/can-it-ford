# Citation Register

Source documents this project's parameters and thresholds actually trace back to. `CITATION.cff` at the repo root is for citing this repository itself, not a bibliography, this file is the bibliography.

## Rights status of the files in this directory

**Added 2026-08-18.** This file is a bibliography: it records what each source establishes. It
previously recorded nothing about whether the project may redistribute the files sitting next to
it, and this directory publishes third-party publisher PDFs and 20 image reproductions to a
**public** repository. Licences below were resolved per DOI through Unpaywall on 2026-08-18.
Full working and the per-asset inventory: `THIRD_PARTY_NOTICES.md` and
`docs/R8_LICENCE_RECONCILE_2026-08-18.md`.

The repository's root `LICENSE` (BSD 3-Clause) does **not** apply to any of these files. It now
carries an explicit scope carve-out saying so.

| File or folder | Licence as found | Status |
|---|---|---|
| `Water Resources Research - 2021 - Wang and Marsooli ....pdf` | **CC BY-NC-ND** (DOI 10.1029/2020WR028616) | NonCommercial, NoDerivatives. Redistribution of the unmodified PDF with attribution is permitted; commercial use and derivatives are not. |
| `J Flood Risk Management - 2025 - Dasallas ....pdf` | **CC BY** (DOI 10.1111/jfr3.70154) | Clean. Attribution required and given here. |
| `Smith-Modra-Felder/` (16 images) | **closed access, all rights reserved** (DOI 10.1111/jfr3.12527) | **No permission established.** Unpaywall reports no open-access location; Crossref records Wiley's standard terms. Most exposed item in this directory. |
| `ARR_Project_10_Stage2_Report_Final.pdf`, `ARR table 1 ....png` | **UNRESOLVED** | All 29 pages carry no copyright, licence or reproduction statement; the report prints no DOI; `arr.ga.gov.au` returns 403. Two routes tried, both inconclusive. |
| `WRL reports technical and Research/` (3 images) | **UNRESOLVED** | Same publisher family and same silence as the AR&R report. |
| `vehicle(kks32).py`, `splat_sim(kks32).py` | **MIT**, header in-file | Clean. Copyright is "The mpm-engine authors", not this project. |
| `Elicit - *.bib`, `Elicit - *.csv`, and the `.md` notes | project-authored or tool output | Covered by the root `LICENSE`. |

**UNRESOLVED means no permission has been established, not that permission is presumed.** Silence
from a publisher is not a grant. If you hold rights in any of the above and object to its
inclusion, please open an issue on the repository.

## L0, static depth threshold

NWS Turn Around Don't Drown. https://www.weather.gov/safety/flood-turn-around-dont-drown

## L1, AR&R depth-velocity hazard scalar

Shand, T. D., Cox, R. J., Blacka, M. J., & Smith, G. P. (2011). Australian Rainfall and Runoff Project 10: Appropriate Safety Criteria for Vehicles, Literature Review, Stage 2. AR&R Report No. P10/S2/020. Water Research Laboratory, UNSW. PDF in `citations/ARR_Project_10_Stage2_Report_Final.pdf`.

**Threshold used: the JOINT rule, not a bare D x V scalar.** All three conditions must
hold for FORD; failing any one gives NO-FORD:

| AR&R class | Depth cap | Velocity cap | D x V cap |
|---|---|---|---|
| Small passenger | 0.30 m | 3.0 m/s | 0.30 m2/s |
| Large passenger | 0.40 m | 3.0 m/s | 0.45 m2/s |
| Large 4WD | 0.50 m | 3.0 m/s | 0.60 m2/s |

**The 2010 Toyota Yaris used throughout this project is Small passenger**, so its caps are
0.30 m, 3.0 m/s and 0.30 m2/s. Primary sources: `vehicle_params.py:207-223`
(`AR_R_STABILITY_LIMITS`) and `vehicle_params.L1_verdict` at `:228`, mirrored in
`hf_space/app.py:41-53` and `renders/yaris_render_s1/gates.py:23`.

> **Corrected 2026-08-18.** This entry previously read "Threshold used: DV <= 0.60 m2/s for the
> Large 4WD vehicle class specifically, not a generic all-vehicle number." That is the superseded
> hazard-only form, and 0.60 is the **Large 4WD** number applied to a **Small passenger** vehicle,
> which is twice this vehicle's actual D x V cap and returns FORD for cases the joint rule calls
> NO-FORD. Commit `f6348c7`, "Space L1 used the Large 4WD threshold for a Yaris and dropped two of
> three conditions", replaced exactly this error in the deployed demo; this file was not updated at
> the same time. The qualifier that survives is the useful half: 0.60 was never a generic
> all-vehicle number.

The report itself calls this table "draft, interim, informal," not an endorsed safety standard.

## L2, WCSPH physical validation

Smith, G. P., Modra, B. D., & Felder, S. (2019). Full-scale testing of stability curves for vehicles in flood waters. Journal of Flood Risk Management, 12(S2), e12527. DOI:10.1111/jfr3.12527. Source in `citations/Smith-Modra-Felder/`.

> **Title corrected 2026-08-18.** This entry previously read "Full-scale testing of vehicle floating and sliding in flowing floodwater", which is not the title at that DOI. Verified against the Crossref record: the DOI, authors and year were all correct, so this was a citation error rather than a fabricated reference, but it is the same surface pattern (a real DOI paired with a title that is not the resolved title) and it would fail a bibliography audit. **The bibliographies were then checked and are correct, so no further fix is needed:** `paper/can_it_ford_references_IEEE.bib` and `overleaf_sync/can_it_ford_references_IEEE.bib` both carry the Crossref title on `origin/main` and on `claude/add-ci-checks`. A `git grep` for the wrong title across both branches returns this file as the only citation-style occurrence; the two other hits are ordinary prose about floating and sliding as failure modes, not titles. The error was confined to this file.

## L2, DRIFT_THRESHOLD = 0.05m reframing

No published paper defines a fixed 0.05m displacement threshold. Flood-vehicle stability literature defines failure at incipient motion, not a prescribed distance. Reframed as 2.5-3.4% of representative vehicle body width:

- Xia, J., Falconer, R. A., Xiao, X., & Wang, Y. (2014). Criterion of vehicle stability in floodwaters based on theoretical and experimental studies. Natural Hazards. DOI:10.1007/s11069-013-0889-2. Honda Accord width 1.845m, Audi Q7 width 1.983m.
- Shah, S. M. H., Mustaffa, Z., Kim, D. K., & Yusof, K. W. (2018). Instability Criteria for Vehicles in Motion Exposed to Flood Risks. MATEC Web of Conferences. DOI:10.1051/matecconf/201820307003. Perodua Viva width 1.475m.

An earlier candidate fix citing Smith, Modra & Felder 2019 Eq. 6 as the DRIFT_THRESHOLD source was checked on July 7 and does not hold up, that paper does not state a finite displacement criterion either.

## Vehicle box-proxy geometry validation

Xiong, Y., Liang, Q., Zheng, J., Wang, G., & Tong, X. (2024). Simulation of the Full-Process Dynamics of Floating Vehicles Driven by Flash Floods. Water Resources Research, 60(10), e2023WR036739. DOI:10.1029/2023WR036739. Verified real July 7, exact DOI and author list confirmed. Caution before citing this for the box-proxy simplification specifically: the paper is a full entrainment/transport/deposition coupled model, read the actual method before using it to justify a simplified rigid-block vehicle representation.

## Pipeline framework

Thorpe, A. J., Tretiakov, S., Hsiao, C. H., Low, S. A., Li, X., Iqbal, H., Bhatt, N. P., Topcu, U., & Kumar, K. (2026). Physically Viable World Models: A Case for Query-Conditioned Embodied AI. arXiv:2605.30542.

Hsiao, C. H., & Kumar, K. (2025). NeRF-to-MPM inversion for granular material property estimation. arXiv:2507.09005. Inverse sibling of this project's forward pipeline.

## Bridge and solver technique

Xie, T., Zong, Z., Qiu, Y., Li, X., Feng, Y., Yang, Y., & Jiang, C. (2023). PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics. arXiv:2311.12198. CVPR 2024 Highlight. Splat-to-particle extraction logic reused for the PhysGaussian-to-Genesis bridge, opacity_threshold=0.02 default confirmed against the official `decode_param.py`.

Kerbl, B., Kopanas, G., Leimkuhler, T., & Drettakis, G. (2023). 3D Gaussian Splatting for Real-Time Radiance Field Rendering. ACM Transactions on Graphics, 42(4). arXiv:2308.04079.

## Background, not directly load-bearing

Kovacic, Z., & Ellis, K. (2026). MPMWorlds: Material-Point-Method Simulations for Inferring and Extrapolating Physical Dynamics. arXiv:2606.01538. General MPM/video-inference connection, not flood or vehicle specific.

Bansal, H., Lin, Z., Xie, T., Zong, Z., Yarom, M., Bitton, Y., Jiang, C., Sun, Y., Chang, K.-W., & Grover, A. (2024). VideoPhy: Evaluating Physical Commonsense for Video Generation. arXiv:2406.03520. Same caveat as MPMWorlds.

## Still unverified as of July 7

Amicarelli 2015, Albano 2016, Sole et al. 2020, Jancik & Hyhlik 2019, dam-break/bore-impact SPH validation citations from earlier drafts. Not yet independently checked, low priority, minor supporting role only.
