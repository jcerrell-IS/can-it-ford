# Citation Register

Source documents this project's parameters and thresholds actually trace back to. `CITATION.cff` at the repo root is for citing this repository itself, not a bibliography, this file is the bibliography.

## L0, static depth threshold

NWS Turn Around Don't Drown. https://www.weather.gov/safety/flood-turn-around-dont-drown

## L1, AR&R depth-velocity hazard scalar

Shand, T. D., Cox, R. J., Blacka, M. J., & Smith, G. P. (2011). Australian Rainfall and Runoff Project 10: Appropriate Safety Criteria for Vehicles, Literature Review, Stage 2. AR&R Report No. P10/S2/020. Water Research Laboratory, UNSW. PDF in `citations/ARR_Project_10_Stage2_Report_Final.pdf`.

Threshold used: DV <= 0.60 m2/s for the Large 4WD vehicle class specifically, not a generic all-vehicle number. The report itself calls this table "draft, interim, informal," not an endorsed safety standard.

## L2, WCSPH physical validation

Smith, G., Modra, B., & Felder, S. (2019). Full-scale testing of vehicle floating and sliding in flowing floodwater. Journal of Flood Risk Management. DOI:10.1111/jfr3.12527. Source in `citations/Smith-Modra-Felder/`.

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
