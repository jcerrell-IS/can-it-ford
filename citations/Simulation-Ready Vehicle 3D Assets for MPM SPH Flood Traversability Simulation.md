# Simulation-Ready Vehicle 3D Assets for MPM/SPH/Genesis Flood Traversability Work

## Bottom line

Beyond NCAC/CCSA and CARLA, there is a small but real set of additional real-measured vehicle FE geometry sources — all in Europe, all LS-DYNA-keyword or LS-DYNA-derived, none pre-converted to OBJ/PLY/glTF/USD. No public evidence exists that the specific 2010 Toyota Yaris, 2007 Chevrolet Silverado, or 2020 Nissan Rogue NCAC models have been converted to a mesh-only format and shared publicly — the only "conversion" activity found is a 2026 MIT/Toyota Research Institute re-implementation (CarCrashNet) that re-derives Yaris/Silverado-class geometry in OpenRadioss format, not OBJ/PLY/glTF/USD, and a single unrelated Vietnamese academic paper that reconstructs simplified pickup/SUV/sedan FE models from NCAC data without releasing files. On the simulator side, only CARLA and (weakly) LGSVL ship redistributable vehicle assets with license clarity; Isaac Sim/Omniverse, AirSim, Apollo, and Autoware either use visual-default game assets or require third-party paid "SimReady" providers with no crash-derived mass data. No flood/water-crossing research group has published a dedicated vehicle mesh asset pack — every flood-AV paper found (including the PVWM/Genesis-adjacent literature) either builds its own simplified rigid-body proxy or reuses CARLA/generic box geometry.

## Government, academic, and research-institution FE vehicle sources beyond NCAC

### European Commission Joint Research Centre (JRC) generic vehicle models

The JRC (Ispra, Italy) publishes "generic" — i.e., brand-independent but dimensionally and mass-representative — heavy/medium goods vehicle finite element models built to ISO 22343 vehicle-ramming categories, explicitly for security-barrier crash simulation, not passenger-car flood work, but they are a genuine non-US, non-NCAC government FE source.[^1][^2][^3]

- **N1 category (light vehicle, ~3.5t)**: JRC generic model, first of the series, released under the EU Public Licence (EUPL), free of charge, in FE keyword form for multiple codes.[^1]
- **N2A / N3C / N3D categories** (medium/heavy trucks): JRC Publications Repository record JRC143166, "Generic vehicle model N2A & N3D split," describing three generic FE models per ISO 22343. Landing page: [publications.jrc.ec.europa.eu/repository/handle/JRC143166](https://publications.jrc.ec.europa.eu/repository/handle/JRC143166).[^2]
- **N3G category (30t heavy construction truck)**: JRC Publications Repository record JRC139954, authored by Sebik & Kodajkova (2024), explicitly stated to be "disseminated publicly under the open source public licence EUPL... intended for use by different stakeholders for virtual testing of security barriers". Landing page: [publications.jrc.ec.europa.eu/repository/handle/JRC139954](https://publications.jrc.ec.europa.eu/repository/handle/JRC139954).[^3]
- **License**: EUPL (EU Public Licence) — copyleft but redistributable and citable, compatible with NSF-funded academic reuse.[^3][^1]
- **Format**: FE keyword format ("provided in all FE codes" per Euro NCAP's related TB540 language); not OBJ/PLY/glTF/USD.[^4]
- **Physical data**: Real-representative mass/dimension per ISO 22343 vehicle class (these are "generic," not measured-VIN models like NCAC's), documented in the accompanying JRC technical reports rather than a separate spec sheet.[^3]
- **Access**: Direct download vs. request — the landing pages are public search records; actual file download links were not independently confirmed as one-click in this session, so treat as **request/verify** rather than guaranteed direct-download until you open the JRC repository page yourself.
- **Relevance to "Can It Ford"**: Truck classes (N-series) are closer to your "light pickup" abstraction level than to sedan/SUV, and mass data is class-representative rather than VIN-specific, so this is a secondary rather than primary source for your three target vehicle classes.

### UNECE / Euro NCAP generic vehicle FE models for pedestrian and DPPS testing

UNECE hosts "Generic Vehicle FE models for DPPS (Deployable Pedestrian Protection System) simulation procedure — common files," directly downloadable from its standards documents page: [unece.org/transport/documents/standards/generic-vehicle-fe-models-dpps-simulation-procedure-common-files](https://unece.org/transport/documents/standards/generic-vehicle-fe-models-dpps-simulation-procedure-common-files). These generic front-end/car-front models are also referenced in Euro NCAP's Technical Bulletin TB540/TB024 pedestrian-protection certification documents, which state the models are "generic replications of current car fronts... provided in all FE codes".[^5][^6][^4]

- **License**: Published by UNECE as part of an open regulatory annex; treat as citable technical-standard material, but confirm redistribution terms on the download page itself before reuse in a public repo.
- **Format**: FE keyword deck (LS-DYNA style), front-end-only geometry (not full vehicle) — most useful for hood/bumper contact physics, not full-body MPM coupling.
- **Physical data**: Representative of "current car fronts" by category, documented in the TB540/TB024 bulletins rather than measured from a specific VIN.[^4][^5]
- A related generic vehicle **interior** FE model is hosted on OpenVT (a GitLab-based FE model repository, formerly linked to European vehicle-safety research networks): [openvt.eu/fem/generic-vehicle-interior](https://openvt.eu/fem/generic-vehicle-interior), cloneable via `git clone https://virtual.openvt.eu/fem/generic-vehicle-interior.git`. This is interior-only (seats, restraints), not exterior body geometry, so it does not help with flood-drag hull shape but could support a future interior-flooding sub-study.[^7]

### JNCAP (Japan)

No public JNCAP-published FE/mesh vehicle model repository analogous to NCAC was found. JNCAP (administered by NASVA, Japan's National Agency for Automotive Safety and Victims' Aid) publishes crash-test *results* and safety ratings (e.g., its annual "Vehicle Safety Performance" report), and JNCAP crash-pulse data has been used academically to calibrate crush-energy accident-reconstruction FE models, but the underlying vehicle FE geometry in those academic studies is not released — it stays proprietary to the authors' institutions. **Conclusion: JNCAP is a dead end for downloadable geometry**; it is only useful as a source of real crash-test kinematic/force data if you need L2-simulation validation targets rather than mesh assets.[^8][^9]

### Other DOT/FHWA-funded FE archives beyond NCAC

- **ORNL/FHWA Tractor-Trailer FEM Archive**: [thyme.ornl.gov/FHWA/TractorTrailer/download/download.cgi](https://thyme.ornl.gov/FHWA/TractorTrailer/download/download.cgi) — Oak Ridge National Laboratory hosts standalone and crash-scenario LS-DYNA keyword models for tractors, semitrailers, ballast, and barriers, built from an NCAC-derived sleeper-cab tractor baseline, with day-cab and wheelbase variants. Format is LS-DYNA `.k` keyword decks organized via `*INCLUDE`/`*TRANSFORM`, same non-mesh format as NCAC. This is a heavy-truck source, not sedan/SUV/pickup, but demonstrates the same modular FE convention your pipeline would need to parse regardless of vehicle class.[^10][^11]
- **NHTSA's own vehicle-model page** (distinct from and complementary to NCAC/CCSA): [nhtsa.gov/crash-simulation-vehicle-models](https://www.nhtsa.gov/crash-simulation-vehicle-models) lists additional real, VIN/model-year-attributable FE models not hosted at CCSA:[^12]
  - 2014 Honda Accord mid-size sedan (full interior + dual occupant restraint FEM, developed by EDAG Inc., later improved by Virginia Tech Transportation Institute with ZF Group support).
  - 2019 Honda Odyssey second-row seat with integrated seatbelts (FEM with static/dynamic validation).
  - 2014 Chevrolet Silverado 1500 and 2014 Honda Accord, modified for NHTSA's oblique offset frontal crash structural countermeasure program (downloadable as a CAE model zip).
  - 2011 Honda Accord modified for IIHS small-overlap test (lightweight-vehicle variant).
  - Toyota Venza baseline/high-option/low-option body-in-white models (Lotus Engineering, CARB-funded lightweight-vehicle study).
  All are LS-DYNA-format FEMs, government-funded (NHTSA/CARB), and explicitly public downloads on a .gov page — this is a same-provenance-tier, non-NCAC-hosted supplement to your CCSA list, and the **2014 Honda Accord sedan and 2014 Silverado 1500** are directly relevant to your sedan and pickup classes.[^12]

### University vehicle-dynamics / aerodynamics labs (mesh-only, no crash mass)

- **DrivAerNet / DrivAerNet++** (MIT, Mohamed Elrefaie et al.): a large parametric dataset of 4,000+ (DrivAerNet) and 8,000 (DrivAerNet++) detailed 3D car meshes with CFD aerodynamic simulation data, covering fastback/hatchback/notchback body styles. GitHub: [github.com/Mohamedelrefaie/DrivAerNet](https://github.com/Mohamedelrefaie/DrivAerNet). **Format**: high-resolution 3D surface meshes (STL/mesh, CFD-ready), directly usable for MPM/SPH surface coupling without LS-DYNA parsing. **Physical data**: these are CAD-parametric aerodynamic study shapes (DrivAer generic body derived from BMW/Audi/TUM wind-tunnel geometry), not real measured curb-weight VIN vehicles — dimensions are realistic but mass/inertia are not crash-measured. **License**: released for research use on GitHub (check repo LICENSE file directly before redistribution). This is your best *readily usable mesh geometry* source if visual/aerodynamic realism matters more than crash-measured mass, and could be paired with literature-sourced curb weights for your three vehicle classes to approximate L1/L2 physical parameters.[^13][^14][^15][^16][^17]
- **AutoHood3D** (multi-institution FSI benchmark): 16,000+ automotive hood geometries with one-way fluid-structure interaction solutions, open-source license, multiple file modalities. Component-level (hood only), not full-vehicle, but is a rare *open, FSI-native, geometry+physics* dataset germane to your MPM-water coupling use case methodologically.[^18]
- **CarCrashNet** (MIT + Toyota Research Institute, 2026): explicitly rebuilds Dodge Neon, **Toyota Yaris**, and **Chevrolet Silverado** full-vehicle crash simulations using the open-source OpenRadioss solver, validated against LS-DYNA and physical crash tests, released under **CC BY 4.0** at [github.com/Mohamedelrefaie/CarCrashNet](https://github.com/Mohamedelrefaie/CarCrashNet). This is the closest thing found to a "third-party conversion" of the NCAC Yaris/Silverado models — but critically, **it is not a mesh-format conversion**: the released data is VTKHDF-format time-resolved FE field trajectories (nodal displacement, stress, plastic strain) from OpenRadioss re-simulation, still finite-element node/element topology, not OBJ/PLY/glTF/USD surface geometry. It does, however, confirm that Yaris and Silverado FE geometry *can* be extracted from these campaigns as an undeformed reference mesh (their notation \(\mathbf{X}^{(0)}\)), so a determined user could pull the first-frame nodal coordinates from their public VTKHDF release and mesh-cast them into OBJ/PLY — this would be a **novel, unpublished conversion**, not one that already exists in public form.[^19][^20][^21]

## Third-party conversions of the specific NCAC Yaris/Silverado/Rogue models

No evidence was found of an OBJ, PLY, glTF, or USD conversion of the 2010 Toyota Yaris, 2007 Chevrolet Silverado, or 2020 Nissan Rogue NCAC/CCSA models existing anywhere public — no GitHub repo, Kaggle dataset, Hugging Face space, or paper supplementary material surfaced one. Specific findings:

- A GitHub code search across NCAC-related repositories turned up only tooling *discussions*, not conversions: the BRL-CAD project's issue tracker explicitly lists "implement a LS-DYNA keyword file format importer... lots of great vehicle datasets at ncac.gwu.edu/vml/models.html" as an **open, unimplemented TODO** dating back years, confirming that even a major open-source solid-modeling project (BRL-CAD) never completed an NCAC-to-mesh importer.
- A 2021 Vietnamese academic paper ("Reconstruction finite element model of cars," Science and Technology Development Journal of Engineering and Technology) explicitly reconstructs six *simplified* car FE models — 1 pickup, 2 SUV, 3 sedan — derived from and validated against NCAC's original vehicle FE models, using LS-DYNA. This is the single closest hit to "someone repurposed NCAC geometry for a different vehicle-class mix," but (a) it stays in LS-DYNA keyword format, not mesh format, and (b) no public file release accompanies the paper — only the PDF describing the method: [stdjet.scienceandtechnology.com.vn/index.php/stdjet/article/download/782/1099](http://stdjet.scienceandtechnology.com.vn/index.php/stdjet/article/download/782/1099).[^22]
- CarCrashNet (above) is the only 2026 project that touches Yaris/Silverado geometry in a non-LS-DYNA pipeline, but its release format is VTKHDF FE field data, not a mesh-format conversion.[^21][^19]
- Generic web/GitHub searches for "gltf-car" and similar surfaced only unrelated hobby/tutorial repositories (e.g., a small personal glTF-car demo project) with no connection to NCAC data.[^23]

**Conclusion**: your original premise — no pre-converted OBJ/PLY/glTF/USD version of the Yaris/Silverado/Rogue NCAC models exists publicly — holds after this search. The nearest workaround is extracting the undeformed reference mesh from CarCrashNet's public VTKHDF release for Yaris and Silverado (Rogue is not covered by any project found), which would still require you to do the mesh extraction and format conversion yourself, and to check CC BY 4.0 attribution requirements back to MIT/Toyota Research Institute.

## AV/robotics simulation platforms besides CARLA

| Platform | Vehicle asset library | File format | Physical parameters | License for redistribution |
|---|---|---|---|---|
| NVIDIA Isaac Sim / Omniverse | No dedicated real-vehicle-mass car library; NVIDIA's SimReady library is strongest for industrial/warehouse objects, not road vehicles[^24]; developer forum confirms cars must be imported from Sketchfab/TurboSquid/CGTrader and manually converted, with default (not measured) physics until manually configured via the Vehicle Wizard[^25][^26] | USD (native); FBX/OBJ/glTF importable and convertible | Visual-default only unless manually set; Vehicle Wizard estimates mass/inertia from bounding-box scan of the mesh, not from real vehicle spec sheets[^26] | Isaac Sim itself is free NVIDIA software; imported third-party assets carry their own source license (often unclear, per NVIDIA's own forum note)[^25] |
| LGSVL / SVL Simulator (LG Electronics, now community-maintained) | Ships its own vehicle models for AV testing; Autoware Foundation received explicit license clarification | Unity-based custom asset pipeline | Not confirmed as crash-measured; built for driving dynamics simulation, not FSI | LG Simulator Software License Agreement — permits internal/non-commercial modification and use, including modeling new vehicle models, but **prohibits commercialization**; assets/content added by the licensee remain licensee property[^27][^28] |
| Microsoft AirSim | Ground-vehicle mode exists but is a secondary use case behind its aerial-vehicle focus[^29]; no documented real-mass vehicle catalog found | Unreal Engine assets | Visual/game-engine defaults | MIT-licensed open source, but no dedicated licensable vehicle-asset library with real mass data was found |
| Baidu Apollo | Uses a "Game Engine Based Simulator" per its own 2021 documentation[^30]; no public real-mass vehicle geometry catalog surfaced | Unity/Unreal-style game assets | Not documented as real/measured | Apache 2.0 for Apollo software; vehicle asset provenance undocumented |
| Autoware | Relies on external simulators (commonly LGSVL/CARLA) rather than shipping its own vehicle-asset library[^27] | Inherits host simulator's format | Inherits host simulator's data | Apache 2.0 for Autoware core; asset licensing inherited from whichever simulator is paired |
| Isaac Lab (successor framework on Isaac Sim/PhysX) | Same asset ecosystem as Isaac Sim above[^31] | USD | Same limitation — no native real-vehicle-mass catalog | Same as Isaac Sim |

The clearest finding: **none of these platforms ship a documented, licensable, real-or-near-real-mass vehicle asset library that would beat CARLA's CC-BY FBX catalog** for your purposes. CARLA remains the most defensible "game-engine visual" fallback precisely because its license and provenance are already fully documented (per your confirmed baseline), whereas Isaac Sim/LGSVL/AirSim/Apollo either lack a real vehicle catalog entirely or push the licensing burden onto whatever third-party marketplace asset you import.[^26][^25]

A commercial vendor, Physicl, explicitly markets "physics-accurate Isaac Sim assets" with computed (not guessed) mass/friction/collision data, positioned as filling the exact gap you're probing — but its current public library (documented via Imagine.io's "SimReady 3D Asset Library") covers only kitchen/appliance/cabinetry objects under CC BY-NC 4.0, with zero vehicles, and the vehicle-specific roadmap is described only in marketing copy without a shipped catalog. This is not yet a usable source but is worth monitoring since it directly targets the "visual-only vs. physics-accurate" gap you're evaluating.[^32][^24]

## Flood, water-crossing, and amphibious vehicle simulation datasets

No dataset or asset library built specifically for flood/water-crossing/amphibious vehicle simulation research that ships real or simplified vehicle geometry was found. The closest adjacent projects:

- **Mila Simulated Floods Dataset** (Schmidt et al., ClimateGAN, ICLR 2022): a Unity3D-built 1.5 km² virtual world with before/after flood image pairs, depth maps, and semantic segmentation masks that include a "car" class, but this is a 2D image/segmentation dataset for computer vision, not a downloadable 3D vehicle mesh asset — vehicles exist only as rendered Unity objects inside the scene, not as extractable geometry files. GitHub: [github.com/cc-ai/mila-simulated-floods](https://github.com/cc-ai/mila-simulated-floods), CC BY 4.0, dataset hosted on Google Drive. Not usable for your MPM coupling pipeline.[^33]
- **FLOW-3D HYDRO** (commercial CFD vendor) demonstrates a vehicle-flood interaction using its General Moving Objects (GMO) physics on a generic vehicle model in a promotional video, confirming the *problem* is being worked on commercially, but no geometry or dataset is released — it is a proprietary commercial capability demo, not a citable academic asset source.[^34]
- Your own space's PVWM paper (Thorpe et al., arXiv:2605.30542) and the companion "Path Planning in Physically Viable World Models" (arXiv:2607.00673) are themselves the most relevant precedent: the latter explicitly "add[s] floodwater while keeping the reconstructed geometry fixed to isolate the effect of changing vehicle mobility" in an Alaska village scene — meaning the PVWM team's own approach is to use *reconstructed* (Gaussian-splat-derived) vehicle geometry rather than sourcing a pre-built crash-test mesh. This directly validates your own project's gsplat-to-MPM pipeline design choice as the field's de facto solution to this exact sourcing gap, rather than there being a missed "off-the-shelf" flood-vehicle asset library you should have found.[^35]
- No IJRR, ASCE, AGU Water Resources Research, or Journal of Flood Risk Management paper surfaced in this search that ships companion 3D vehicle geometry; flood-vehicle-stability literature in these venues (not independently re-verified in this pass beyond the arXiv results above) focuses on hydrodynamic force coefficients and empirical D×V thresholds (e.g., the Shand et al. AR&R lineage referenced in your own space instructions) rather than distributing simulation-ready meshes.

## Practical implications for the "Can It Ford" pipeline

Given the gsplat-to-MPM pipeline design (real video to Gaussian splat to PhysGaussian MPM seeding), the absence of a pre-converted, physically-measured vehicle mesh in a usable format is not a blocking gap — it is consistent with how the field's own most relevant precedent (Thorpe et al.'s PVWM path-planning work) already operates, by reconstructing vehicle geometry directly from video rather than importing crash-test assets. For validation-grade mass/inertia numbers to pair with a gsplat-reconstructed sedan/SUV/pickup mesh, the NHTSA vehicle-models page's 2014 Honda Accord (sedan) and 2014/2007 Chevrolet Silverado (pickup) remain the strongest real, government-published, VIN-attributable mass sources beyond CCSA's own list, while DrivAerNet++'s meshes are the strongest ready-to-use *surface geometry* if a generic sedan/SUV shape (rather than a specific crash-tested VIN) is acceptable for the MPM rigid-body coupling stage. Both are immediately usable on a MacBook or DesignSafe JupyterHub (no cluster time needed) since they involve only file download and mesh preprocessing, not GPU-heavy simulation; only the eventual Genesis MPM open-channel coupling run itself would require Vista GH200 time.[^16][^13][^35][^12]

---

## References

1. [Generic vehicle models for finite element numerical simulations](https://ec.europa.eu/newsroom/pps/redirection/item/814739) - We put our Generic Vehicle Models at disposal for download under the European Union Public Licence (...

2. [JRC Publications - Generic vehicle model N2A & N3D split to](https://publications.jrc.ec.europa.eu/repository/handle/JRC143166) - In this report, we present three generic vehicle models corresponding to the categories N2A, N3C and...

3. [Generic vehicle model N3G - JRC Publications Repository](https://publications.jrc.ec.europa.eu/repository/handle/JRC139954) - As a part of the European Commission support to the EU Member States in protecting public spaces aga...

4. [Pedestrian Human Model Certification Technical Bulletin 540](https://cdn.euroncap.com/cars/assets/cp_540_pedestrain_human_model_certification_v41_fad357c7de.pdf) - Euro NCAP Version 4.1 — March 2025. Models are generic replications of current car fronts and are pr...

5. [Documentation of Generic Vehicle Models](https://wiki.unece.org/download/attachments/208536077/IWG-DPPS-25-05_Documentation_of_Generic_Vehicle_Models_20230904%20CK.pdf?api=v2) - Finite Element Software (supplied by code-houses to Industry) Generic Vehicle Models available on UN...

6. [Generic Vehicle FE models for DPPS simulation procedure](https://unece.org/transport/documents/standards/generic-vehicle-fe-models-dpps-simulation-procedure-common-files) - Generic Vehicle Front End models for Deployable Pedestrian Protection System simulation procedure. D...

7. [Generic Vehicle Interior - Finite Element Models - GitLab](https://openvt.eu/fem/generic-vehicle-interior) - This is a generic vehicle interior model. Download Model Download the files at OpenVT or Clone the r...

8. [Vehicle Safety Performance 2021](https://www.nasva.go.jp/mamoru/en/download/JNCAP_2022_panf_en.pdf)

9. [09-06-02-0009: Validation of Crush Energy Calculation Methods for Use in Accident Reconstructions by Finite Element Analysis - Journal Article](https://saemobilus.sae.org/articles/validation-crush-energy-calculation-methods-use-accident-reconstructions-finite-element-analysis-09-06-02-0009) - The crush energy is a key parameter to determine the delta-V in accident reconstructions. Since an a...

10. [[PDF] development and validation of an ncap simulation using ls-dyna3d](https://rosap.ntl.bts.gov/view/dot/38934/dot_38934_DS1.pdf)

11. [Download](https://thyme.ornl.gov/FHWA/TractorTrailer/download/download.cgi) - Here you can download the FEM models and reports for the project. The available FEM models are: The ...

12. [Crash Simulation Vehicle Models](https://www.nhtsa.gov/crash-simulation-vehicle-models) - A full vehicle finite element model (FEM) including a vehicle interior and occupant restraint system...

13. [DrivAerNet++: A Large-Scale Multimodal Car Dataset with ...](https://arxiv.org/html/2406.09624v1) - Each entry in the dataset features detailed 3D meshes, parametric models, aerodynamic coefficients, ...

14. [DrivAerNet: A Parametric Car Dataset for Data-Driven ...](https://arxiv.org/html/2403.08055v2) - DrivAerNet, with its 4000 detailed 3D car meshes using 0.5 million surface mesh faces and comprehens...

15. [DrivAerNet: A Parametric Car Dataset for Data-Driven Aerodynamic ...](https://arxiv.org/html/2403.08055v1)

16. [Mohamedelrefaie/DrivAerNet: A Large-Scale Multimodal ...](https://github.com/Mohamedelrefaie/DrivAerNet) - A Large-Scale Multimodal Car Dataset with Computational Fluid Dynamics Simulations and Deep Learning...

17. [DrivAerNet dataset - JuheAPI](https://www.juheapi.com/datasets/drivaernet-dataset) - Access JuheAPI's curated API Marketplace. Accelerate development, innovate faster, and transform you...

18. [A Multi‑Modal Benchmark for Automotive Hood Design and ...](https://arxiv.org/html/2511.05596v1) - This study presents a new high-fidelity multi-modal dataset containing 16000+ geometric variants of ...

19. [A Large-Scale Dataset and Hierarchical Neural Solver for ... - arXiv](https://arxiv.org/abs/2605.07098) - In this work, we introduce CarCrashNet, a public high-fidelity open-source benchmark for data-driven...

20. [CarCrashNet: A Large-Scale Dataset and Hierarchical Neural ...](https://arxiv.org/html/2605.07098v2)

21. [CarCrashNet: A Large-Scale Dataset and Hierarchical Neural Solver for Data-Driven Structural Crash Simulation](https://arxiv.org/html/2605.07098)

22. [Reconstruction finite element model of cars](http://stdjet.scienceandtechnology.com.vn/index.php/stdjet/article/download/782/1099) - ...Analysis Center (NCAC), validated by using results from experimental crash tests. The modified (s...

23. [Swastyy/gltf-car](https://github.com/Swastyy/gltf-car) - Contribute to Swastyy/gltf-car development by creating an account on GitHub. Search code, repositori...

24. [Isaac Sim Assets Built for Physics, Not Just Rendering](https://www.physicl.ai/insights/isaac-sim-assets) - Physicl produces Isaac Sim assets with physics calculated, not guessed, and works alongside NVIDIA's...

25. [Open Source Vehicle Asset Library - Isaac Sim](https://forums.developer.nvidia.com/t/open-source-vehicle-asset-library/336556) - We support a very wide array of assets, not just USD. So you can get assets in from anywhere, free o...

26. [Tutorial 2: Using the Vehicle Wizard to Turn an Asset into a ...](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/vehicles/tutorial-02.html) - This tutorial will use the Vehicle Wizard to configure the prims of a graphical vehicle asset. This ...

27. [LGSVL Simulator: License clarification from Autoware Foundation](https://discourse.ros.org/t/lgsvl-simulator-license-clarification-from-autoware-foundation/11581) - The Autoware Foundation received independent clarification on the LGSVL Simulator (GitHub - lgsvl/si...

28. [lgsvl/simulator: A ROS/ROS2 Multi-robot ...](https://github.com/lgsvl/simulator) - A: The Simulator Software License Agreement allows you to “modify or create derivative works of the ...

29. [Home - AirSim - Microsoft Open Source](https://microsoft.github.io/AirSim/)

30. [Off-Road Autonomy Validation Using Scalable Digital Twin ...](https://arxiv.org/html/2405.04743v2) - Additionally, the vehicle model also has a provision to include anti-roll ... Baidu Inc., “Apollo Ga...

31. [Isaac Lab: A GPU-Accelerated Simulation Framework for ...](https://arxiv.org/html/2511.04831v1) - Built on NVIDIA Isaac Sim, Isaac Lab combines RTX rendering for photorealistic, scalable visuals wit...

32. [SimReady 3D Asset Library - Imagine.io](https://physical.imagine.io/library/assets) - Browse physics-accurate 3D assets for robotics simulation. Sub-millimeter geometry, material propert...

33. [GitHub - cc-ai/mila-simulated-floods](https://github.com/cc-ai/mila-simulated-floods)

34. [Vehicle Crossing a Flooded Roadway | FLOW-3D HYDRO](https://www.youtube.com/watch?v=ctC-UXbhW_o) - Even shallow floodwaters can present hazardous conditions for vehicles trying to cross flooded roadw...

35. [Path Planning in Physically Viable World Models](https://arxiv.org/html/2607.00673v1) - In an Alaska village scene, we add floodwater while keeping the reconstructed geometry fixed to isol...

