# Vehicle Parameters and Mesh-to-SDF Coupling: A Cited Reference

### For MPM Flood-Crossing Simulation ("Can It Ford?", NSF SCIPE REU 2026, TACC/UT Austin)

This reference collects primary-source engineering values for three passenger-vehicle classes and version-specific (2026) best practices for converting external meshes into signed distance fields (SDFs) for Material Point Method (MPM) rigid-body coupling in NVIDIA Warp and Genesis (`genesis-world`). All physical values are drawn from manufacturer spec sheets, NHTSA/SAE measured databases, and official engine documentation — not aggregator sites.

**Conversions used:** 1 lb = 0.45359237 kg; 1 in = 0.0254 m; test-weight-in-Newtons → mass = N / 9.81 m/s².

---

## 0. Document status and provenance (added 2026-07-23, pane F4)

**Original body:** written 2026-07-08. It was never a tracked file in the `can-it-ford` repo (confirmed by `git ls-files` and `git log --all --diff-filter=A`, both empty for this filename). It existed only at `~/Downloads/vehicle_mpm_coupling_reference.md` and a byte-identical copy at `~/Documents/CAN_IT_FORD_ARCHIVE_2026-07-17/research_reports_and_citations/` (both 21,656 B). This copy brings it under version control so its claims can be diffed against live code going forward.

**Scope of the original body (Sections 1 and 2):** generic vehicle-class engineering values (box-proxy pipeline) and mesh-to-SDF conversion practice. It contains no vehicle-specific mass figure, no friction value, and no solver-coupling parameter. Section 3 below was added 2026-07-23 to close those gaps.

**What changed on 2026-07-23:**

| Item | Status | Where |
|---|---|---|
| Yaris mass resolved to 1100 kg | Added. The original body cited **no** Yaris or NCAC mass, so nothing here was superseded or corrected; this is new content, not a retraction. | §3.1 |
| Cross-pane signaling (Stop hook) | **No change made.** The original body does not mention cross-pane signaling, tmux, or hooks anywhere (the only matches for "pane" are "sheet-metal panels" and "thin panels" in §2.4). Nothing to reconcile. The live mechanism is recorded in §0.1 for reference only. | §0.1 |
| Flood-specific friction citation family | Added. The original body contained no friction content at all. | §3.2 |
| Azhar et al. 2023 vs Genesis `coup_friction` | Added, worded to match `README.md`. See the standing-agreement note in §3.3. | §3.3 |

**Punctuation note:** the original body's em-dashes are left as written. Several sit inside quoted paper titles (for example "Measured Vehicle Inertial Parameters — NHTSA's Data Through November 1998"), where rewriting them would corrupt a verifiable citation string. All content added 2026-07-23 is em-dash free.

### 0.1 Cross-pane signaling: current mechanism (reference only, no claim in this doc depends on it)

Verified live 2026-07-23 against `.claude/settings.json` in the repo root. The `Stop` hook is **file-based**, not `tmux wait-for`:

```
mkdir -p ~/.pane_signals && echo "$(date -u +%s)" > ~/.pane_signals/$(tmux display-message -p '#S_#I_#P' 2>/dev/null || echo unknown)_done 2>/dev/null || true
```

Each pane writes a Unix-epoch timestamp to `~/.pane_signals/<session>_<window>_<pane>_done` when it stops. `~/.pane_signals/` confirmed present with live signal files at time of writing. The earlier `tmux wait-for` approach was replaced because it does not work across machines (commit `0042612`, "Replace broken cross-machine tmux wait-for in Stop hook with file-based pane signaling").

---

## 1. Vehicle Class Engineering Values

The most authoritative source for the two hardest fields — center-of-gravity (CG) height and the full moment-of-inertia tensor — is NHTSA's **Light Vehicle Inertial Parameter Database**, published as SAE Technical Paper 1999-01-1336 (Heydinger, Bixel, Garrott, Pyne, Howe & Guenther, "Measured Vehicle Inertial Parameters — NHTSA's Data Through November 1998", DOI 10.4271/1999-01-1336). These are physically **measured** values (NHTSA IPMD / S.E.A. VIMF rigs), not estimates ([SAE Mobilus record, DOI 10.4271/1999-01-1336](https://saemobilus.sae.org/papers/measured-vehicle-inertial-parameters-nhtsas-data-november-1998-1999-01-1336); [full data listing, Auburn University](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf)). In that database, test weight is in **N**, CG height in **m**, moments of inertia in **kg·m²**, and SSF is unitless.

### 1.1 Compact Sedan (anchors: Toyota Corolla, Honda Civic)

| Property | Value | Source |
|---|---|---|
| Curb weight | ~1,300–1,480 kg | [Toyota UK Corolla tech-spec (DOI n/a)](https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210127M-Corolla-Tech-Spec.pdf); [Honda Canada 2025 Civic Sedan spec](https://www.honda.ca/-/media/Brands/Honda/Models/CIVIC-SEDAN/2025/PDF/2025-Honda-Civic-Sedan-Specifications---EN_v2.pdf) |
| Bounding box (L×W×H, W excludes mirrors) | ≈ 4.6–4.7 × 1.78–1.80 × 1.42–1.46 m | [Toyota UK Corolla](https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210127M-Corolla-Tech-Spec.pdf); [Honda Canada Civic](https://www.honda.ca/-/media/Brands/Honda/Models/CIVIC-SEDAN/2025/PDF/2025-Honda-Civic-Sedan-Specifications---EN_v2.pdf) |
| CG height above ground | ≈ 0.50–0.55 m (1998 Honda Civic 0.513 m) | [NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf) |
| SSF (static stability factor) | ≈ 1.30–1.45 (1998 Civic 1.431) | [NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf) |

Measured inertia (kg·m²), representative sedan entries ([NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf)):

| Vehicle | Mass (kg) | CG ht (m) | Ixx (roll) | Iyy (pitch) | Izz (yaw) |
|---|---|---|---|---|---|
| 1998 Honda Civic | ~1,143 | 0.513 | 365 | 1,617 | 1,785 |
| 1987 Toyota Corolla FX | ~996 | 0.550 | 443 | 2,087 | 2,142 |
| 1991 Honda Accord LX | ~1,412 | 0.504 | 476 | 2,433 | 2,495 |

**Representative sedan tensor:** Ixx ≈ 300–480, Iyy ≈ 1,100–2,400, Izz ≈ 1,200–2,500 kg·m².

### 1.2 Mid-Size SUV (anchors: Toyota Highlander, Ford Explorer)

| Property | Value | Source |
|---|---|---|
| Curb weight | ~1,880–2,100 kg | [Toyota UK Highlander tech-spec](https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210321M-Highlander-Tech-Spec.pdf) |
| Bounding box (L×W×H, W excludes mirrors) | ≈ 4.95–4.97 × 1.93 × 1.73–1.76 m | [Toyota UK Highlander](https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210321M-Highlander-Tech-Spec.pdf) |
| CG height above ground | ≈ 0.68–0.74 m (1998 Ford Explorer 0.697 m) | [NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf) |
| SSF | ≈ 1.01–1.10 (1998 Explorer 1.010–1.070) | [NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf) |

Measured inertia (kg·m²), representative SUV entries ([NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf)):

| Vehicle | Mass (kg) | CG ht (m) | Ixx (roll) | Iyy (pitch) | Izz (yaw) |
|---|---|---|---|---|---|
| 1998 Ford Explorer | ~2,018 | 0.697 | 740 | 3,561 | 3,682 |
| 1998 Jeep Grand Cherokee | ~1,805 | 0.695 | 683 | 2,889 | 3,124 |
| 1998 Dodge Durango | ~2,201 | 0.682 | 848 | 4,222 | 4,409 |

**Representative SUV tensor:** Ixx ≈ 700–860, Iyy ≈ 2,900–5,100, Izz ≈ 3,100–5,400 kg·m². Note the higher roll inertia (Ixx) than a sedan — directly relevant to roll response under lateral flood drag.

### 1.3 Light Pickup / Half-Ton (anchors: Ford F-150, Toyota Tacoma/Tundra)

| Property | Value | Source |
|---|---|---|
| Curb weight | ~1,825–2,600 kg | [Ford 2021 F-150 Technical Specs](https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2021/specs/2021-F-150-Technical-Specs.pdf); [Ford F-150 Europe Technical Specs](https://f150europe.com/-/media/Project/Hedin/Navigo/F150EuropeSite/PDF/EN-MY23-F-150-Technical-Specs-Europe.pdf) |
| Bounding box (L×W×H) | ≈ 5.89–6.19 × 2.03 (no mirrors; 2.43 with mirrors) × 1.92–2.01 m | [Ford 2021 F-150 Technical Specs](https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2021/specs/2021-F-150-Technical-Specs.pdf) |
| CG height above ground | ≈ 0.65–0.72 m (Tacoma ~0.57–0.60 m) | [NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf) |
| SSF | ≈ 1.05–1.25 (1990 F150 1.184–1.194) | [NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf) |

Measured inertia (kg·m²), representative pickup entries ([NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf)):

| Vehicle | Mass (kg) | CG ht (m) | Ixx (roll) | Iyy (pitch) | Izz (yaw) |
|---|---|---|---|---|---|
| 1990 Ford F150 | ~1,838 | 0.692 | 839 | 5,067 | 5,070 |
| 1992 Ford F150 XLT | ~1,889 | 0.700 | 787 | 5,257 | 5,324 |
| 1998 Toyota Tacoma | ~1,436 | 0.568 | 495 | 2,856 | 3,024 |

**Representative pickup tensor:** Ixx ≈ 500–850, Iyy ≈ 2,900–5,500, Izz ≈ 3,000–5,400 kg·m². The long wheelbase and heavy bed give the largest Iyy/Izz of the three classes.

### 1.4 Moment-of-Inertia: What Published Tensors Exist

Published, measured moment-of-inertia tensors exist for all three classes, from the SAE "Measured Vehicle Inertial Parameters" series:

- SAE **930897** — data through September 1992 (414 entries).
- SAE **1999-01-1336** — data through November 1998, 496 entries; the version with **CG height + Ixx/Iyy/Izz + roll-yaw products + tilt-table + SSF** for cars, SUVs, and pickups (DOI 10.4271/1999-01-1336) ([SAE Mobilus](https://saemobilus.sae.org/papers/measured-vehicle-inertial-parameters-nhtsas-data-november-1998-1999-01-1336)).
- SAE **2021-01-0970** — data through August 2020, +448 NCAP vehicles (2009–2020), **CG location only, no inertia** for the new entries (DOI 10.4271/2021-01-0970) ([SAE Mobilus](https://saemobilus.sae.org/articles/measured-vehicle-inertial-parameters-nhtsas-data-august-2020-2021-01-0970)).

Measurement methods: IPMD described in SAE 881767; VIMF described in Heydinger et al. SAE 950309. In every class, Izz ≈ Iyy ≫ Ixx — the physical signature of a body much longer/wider than it is tall.

Cross-class summary (all measured, [NHTSA/SAE 1999-01-1336](https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf)):

| Class | Ixx (roll) | Iyy (pitch) | Izz (yaw) | CG height (m) |
|---|---|---|---|---|
| Compact sedan | ~300–480 | ~1,100–2,400 | ~1,200–2,500 | ~0.50–0.55 |
| Mid-size SUV | ~700–860 | ~2,900–5,100 | ~3,100–5,400 | ~0.68–0.74 |
| Light pickup | ~500–850 | ~2,900–5,500 | ~3,000–5,400 | ~0.65–0.72 |

### 1.5 Fallback: Uniform-Density Box Inertia

When no measured tensor matches the target model, approximate the vehicle as a uniform-density box of mass \(m\) with length \(L\) (x, roll axis), width \(w\) (y, pitch axis), height \(h\) (z, yaw axis). About its own CG:

\[ I_{xx} = \tfrac{1}{12}\,m\,(w^2 + h^2), \quad I_{yy} = \tfrac{1}{12}\,m\,(L^2 + h^2), \quad I_{zz} = \tfrac{1}{12}\,m\,(L^2 + w^2) \]

**Two caveats critical for the L2 lateral-drag / overturning physics:**
1. A uniform box places the CG at \(h/2\); real vehicles sit well below that (measured CG ≈ 0.50–0.55 m sedan, 0.68–0.74 m SUV, 0.65–0.72 m pickup). Use the **measured** CG height, not \(h/2\), or the overturning moment arm will be overstated.
2. The box formula **overestimates** Iyy and Izz because real mass concentrates toward the floor and center. Prefer the measured NHTSA tensor when the model matches a class above.

---

## 2. Mesh → SDF Best Practices for MPM Rigid Coupling (2026)

Scope: converting an external triangle mesh (.obj/.stl/.ply) of a ~4–5 m vehicle into an SDF for MPM rigid coupling in (A) NVIDIA Warp and (B) Genesis. The Genesis SDF/mesh API parameters below are documented on the 0.3.x–1.0.0 doc builds; parameter names and semantics are stable across those builds and apply to v1.2.0.

### 2.1 Units / Scale Mismatch

**Genesis.** Positions are in meters — `gs.morphs.Mesh.pos` is defined as "The position of the entity in meters" ([Genesis `gs.morphs.Mesh` docs](https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/options/morph/file_morph/mesh.html)). The `scale` parameter (float or 3-tuple) reconciles file units to meters **before** the SDF collider is built; the collider grid `sdf_cell_size` is in meters (default 0.005) ([Genesis `gs.materials.Rigid` docs](https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/material/rigid.html)). A real example loads a mesh with `scale=0.001` (mm→m) ([Genesis issue #1114](https://github.com/Genesis-Embodied-AI/Genesis/issues/1114)). Scale also drives coupling reliability: a maintainer advises making the MPM grid smaller than the rigid object and, as a fix, both raising `grid_density` and using a "larger scale" ([Genesis issue #600](https://github.com/Genesis-Embodied-AI/Genesis/issues/600)).

**Warp.** Warp meshes have no intrinsic units — geometry lives in whatever coordinates you put in `warp.Mesh.points`, and returned distances are in those same units ([Warp `warp.Mesh` docs](https://nvidia.github.io/warp/api_reference/_generated/warp.Mesh.html)). `warp.Volume` ties voxels to spatial coordinates via `voxel_size` = "the size of each voxel in spatial coordinates" ([Warp `warp.Volume` docs](https://nvidia.github.io/warp/api_reference/_generated/warp.Volume.html)). Normalize the vertex array to meters before building the mesh or baking a volume.

### 2.2 Watertightness / Manifold Requirements

**Warp** conditions sign determination on watertightness explicitly: `mesh_query_point_sign_normal` is "robust for well conditioned meshes that are watertight and non-self intersecting," while `mesh_query_point_sign_winding_number` "provides a smooth approximation to sign even when the mesh is not watertight" but requires `support_winding_number=True` at construction ([Warp Built-Ins Reference](https://nvidia.github.io/warp/modules/functions.html); [Warp `warp.Mesh` docs](https://nvidia.github.io/warp/api_reference/_generated/warp.Mesh.html)). NVIDIA's Warp-backed `signed_distance_field` states it outright: "When False, the mesh should be watertight for reliable signs" ([PhysicsNeMo Geometry Functionals](https://docs.nvidia.com/physicsnemo/latest/physicsnemo/api/nn/functionals/geometry.html)).

**Genesis** flags raw non-convex SDF contact as "not yet so stable" and recommends CoACD convex decomposition instead (`convexify=True` is the rigid default; `CoacdOptions(threshold=0.01, preprocess_resolution=100)`) ([Genesis issue #444](https://github.com/Genesis-Embodied-AI/Genesis/issues/444)). Its collision pipeline repairs duplicate faces → tests convex-hull sufficiency → decomposes concave meshes → decimates high-poly meshes ([Genesis Mesh Processing docs](https://genesis-world.readthedocs.io/en/latest/user_guide/advanced_topics/mesh_processing.html)). `decompose_nonconvex` is deprecated in favor of `convexify` + `decompose_object_error_threshold` (default 0.15) ([Genesis `gs.morphs.Mesh` docs](https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/options/morph/file_morph/mesh.html)).

**Repair tools** (official sources): [trimesh](https://trimesh.org/trimesh.base.html) (`is_watertight`, `fill_holes`); [PyMeshFix](https://github.com/pyvista/pymeshfix/blob/main/README.rst) (outputs "a single watertight triangle mesh"); [manifold3d](https://github.com/elalish/manifold) (guaranteed manifold output, includes an SDF level-set function); [OpenVDB `meshToVolume`](https://www.openvdb.org/documentation/doxygen/MeshToVolume_8h.html) (signed or unsigned via `UNSIGNED_DISTANCE_FIELD` flag); and [mesh_to_sdf](https://github.com/marian42/mesh_to_sdf/blob/master/README.md) for open/non-watertight meshes. This is especially relevant for gsplat-derived vehicle meshes, which are rarely watertight — default to the winding-number path (Warp) or CoACD (Genesis).

### 2.3 Resolution / Voxel-Count Tradeoffs (~4–5 m vehicle)

**Genesis rigid SDF defaults:** `sdf_cell_size` = 0.005 m, `sdf_min_res` = 32 (≥16), `sdf_max_res` = 128 ([Genesis `gs.materials.Rigid` docs](https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/material/rigid.html)). On a 5 m car, `sdf_max_res=128` clamps the effective cell to ~5/128 ≈ 4 cm — features below that (bumpers, mirrors, underbody clearance) are under-resolved unless you raise `sdf_max_res`.

**MPM background grid (the coupling-limiting resolution):** `MPMOptions.grid_density` = "Number of grid cells per meter. Defaults to 64" (dx ≈ 0.0156 m); reference `particle_size = 0.01` at `grid_density = 64` ([Genesis `MPMOptions` docs](https://genesis-world.readthedocs.io/en/latest/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html)). Coupling failure is tied to this: particles tunnel through a car-scale object at default density; the fix is `grid_density=128` or 256, confirmed by the reporter to "almost resolve" tunneling ([Genesis issue #600](https://github.com/Genesis-Embodied-AI/Genesis/issues/600)). For thin coupling geometry, set `enable_CPIC=True` ([Genesis `MPMOptions` docs](https://genesis-world.readthedocs.io/en/latest/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html)).

**Warp / OpenVDB:** `voxel_size` is set explicitly at volume creation; allocation is in dense 8×8×8 tiles, so memory scales in 8³ granularity ([Warp `warp.Volume` docs](https://nvidia.github.io/warp/api_reference/_generated/warp.Volume.html)). Baking uses OpenVDB `meshToVolume` / `vdb_tool -mesh2ls voxel=0.1` and the NanoVDB result is loaded into `warp.Volume` ([OpenVDB `MeshToVolume.h`](https://www.openvdb.org/documentation/doxygen/MeshToVolume_8h.html)).

**Heuristics (NVIDIA):** keep the shortest-axis SDF resolution above ~20 cells or the SDF won't capture the shape; ~250 usually suffices, >1000 rarely needed. SDF resolution is memory-dominated, not compute-dominated — triangle count drives compute ([NVIDIA SDF-resolution dev-forum thread](https://forums.developer.nvidia.com/t/invalid-inertia-when-sdf-mesh-for-collision-has-sdf-resolution-too-low/270823); [Omniverse Collision Behavior Guide](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/dev_guide/guides/collision_guide.html)).

**Key principle:** match the SDF cell to the MPM dx (~0.008–0.016 m for a car in a `grid_density`=64–128 domain). An SDF much finer than dx wastes memory because the MPM grid cannot resolve it anyway.

### 2.4 Recommended Workflow for a 4–5 m Vehicle Mesh

1. **Fix units first.** Measure the longest dimension; set Genesis `morphs.Mesh(scale=...)` (or scale the Warp `points` array) so the loaded object is 4–5 m ([Genesis Mesh docs](https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/options/morph/file_morph/mesh.html); [Warp Mesh docs](https://nvidia.github.io/warp/api_reference/_generated/warp.Mesh.html)).
2. **Verify/repair watertightness.** Check `trimesh.is_watertight` / `fill_holes()`; if it fails, repair with PyMeshFix or manifold3d ([trimesh](https://trimesh.org/trimesh.base.html); [PyMeshFix](https://github.com/pyvista/pymeshfix/blob/main/README.rst); [manifold3d](https://github.com/elalish/manifold)).
3. **Genesis path:** keep `convexify=True`; for the concave car body enable CoACD decomposition (`threshold≈0.01–0.05`, higher `resolution`) rather than relying on raw non-convex SDF contact ([Genesis issue #444](https://github.com/Genesis-Embodied-AI/Genesis/issues/444)).
4. **Warp path:** watertight → `mesh_query_point_sign_normal`; not watertight → build with `support_winding_number=True` and use `mesh_query_point_sign_winding_number`; for a static baked SDF use OpenVDB `meshToVolume` → `warp.Volume` ([Warp Built-Ins](https://nvidia.github.io/warp/modules/functions.html); [OpenVDB](https://www.openvdb.org/documentation/doxygen/MeshToVolume_8h.html)).
5. **Set SDF/voxel resolution to the MPM grid.** Start MPM `grid_density=64` (dx≈0.0156 m); raise to 128/256 if particles tunnel; raise Genesis `sdf_max_res` above 128 for thin panels; Warp `voxel_size ≈ MPM dx`; keep shortest-axis SDF resolution ≳20 cells ([Genesis issue #600](https://github.com/Genesis-Embodied-AI/Genesis/issues/600); [Genesis Rigid docs](https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/material/rigid.html); [NVIDIA dev-forum](https://forums.developer.nvidia.com/t/invalid-inertia-when-sdf-mesh-for-collision-has-sdf-resolution-too-low/270823)).
6. **Enable CPIC for thin geometry.** `MPMOptions(enable_CPIC=True)` for sheet-metal panels / thin underbody ([Genesis `MPMOptions` docs](https://genesis-world.readthedocs.io/en/latest/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html)).
7. **Keep the domain tight.** Set MPM `lower_bound`/`upper_bound` to hug the vehicle+water region; domain size drives total voxel memory ([Genesis `MPMOptions` docs](https://genesis-world.readthedocs.io/en/latest/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html)).

---

## 3. Resolved physical parameters (added 2026-07-23)

Sections 1 and 2 above are pipeline-agnostic reference. This section records the values actually locked into the simulation, with the primary source for each.

### 3.1 Vehicle mass: the real-mesh (Yaris) path

**Resolved: 1100 kg.** Primary source is the LS-DYNA deck header itself, `yaris-coarse-v1l.key` line 27, "Version 1l, 1100 kg". Confirmed live in `scripts/ford_sweep_driver.py:45` (`YARIS_MASS_KG = 1100.0`) and locked in the canonical parameter reference by commit `aa13ac1` (2026-07-23), "Correct Yaris mass recommendation to Option A, 1100kg matches deck header, Option B was preferring secondary source over primary".

**Why 1078 kg is not used.** 1078 kg is the NCAC download-page "modeled weight" annotation, a *secondary* source describing the mesh. Two independent live reads of the deck confirmed 1100 kg is the only mass value the deck itself states; neither 1078 nor "MASH" appears anywhere in the deck. The earlier recommendation of 1078 kg was preferring a webpage annotation over the primary artifact. It is retained in `reference_data/vehicle_data_master_reference_2026-07-21.json` as history, superseded by the `recommended_pairing_CORRECTED_2026_07_23` field, not deleted.

**rho is not a constant here, and must not be pasted between pipelines.** In the live sweep driver rho is *not* hardcoded: it emerges at runtime as `mass / solid_volume`. The figure 310.4976 kg/m³ (stored as 310.50) is specifically 1100 kg divided by the **collider box volume** 3.5427 m³. It is meaningless against any other volume:

| Volume basis | Volume (m³) | rho at 1100 kg | Note |
|---|---|---|---|
| Yaris collider box | 3.5427 | 310.50 | The pairing locked by `aa13ac1` |
| Yaris raw enclosed mesh | 6.8185 | 161.33 | Collider-box vs raw-mesh divisor is still an open coupled question |
| Sedan box proxy (4.66 × 1.79 × 1.44) | 12.01 | 91.6 | **Different pipeline.** Do not use the Yaris rho here |

Units check: kg / m³ throughout. Against the CLAUDE.md plausibility band (vehicle effective density 100 to 300 kg/m³), 310.50 sits marginally above the band and 91.6 marginally below it; both are close enough to be plausible, but neither is comfortably inside it, and that is a function of which volume the divisor uses, not of the mass. Sedan mass 1100 kg is inside the 1000 to 1600 kg anchor.

The two vehicle pipelines stay separate: the box-proxy path (`vehicle_params.py`, generic bounding box plus NHTSA-measured inertia, Section 1 of this doc) and the real-mesh path (NCAC Yaris, its own rho from actual mesh volume). A script using one must never silently inherit a number computed for the other.

### 3.2 Ground friction: the flood-specific citation family

For a vehicle in floodwater, the defensible friction citation family is flood-vehicle-stability literature, which models the tire-ground interface as a **single lumped Coulomb coefficient**, not a material-resolved table:

| Quantity | Value | Source |
|---|---|---|
| μ_wet | 0.3 | Bonham & Hattersley (1967), the conservative all-surface wet convention; reused by Kramer et al. (2016) and Xia, Teo & Lin (2011) |
| μ_dry | 0.68 | Martínez-Gomariz et al. (2017), *Urban Water Journal* 14(9):930-939, DOI 10.1080/1573062X.2017.1301501; also Shu et al. (2011) |
| Cross-study range | 0.25 to 0.75 | Xiong et al. (2024), *Water Resources Research* 60:e2023WR036739, citing Gerard (2006), Martínez-Gomariz et al. (2017), Xia et al. (2014) |

Recommended use: μ_wet ≈ 0.3 as the central value, with a sensitivity sweep over 0.25 to 0.75.

**Category-mismatch warning, this is the load-bearing part.** Material-resolved friction values for wet asphalt, gravel, and dirt **do exist**, but only in general automotive and pavement-skid literature (representative published figures: dry asphalt ≈ 1.0, wet asphalt ≈ 0.7 to 0.8, snow ≈ 0.3). Those are on-road braking and tire-skid measurements on a wet surface, not force-balance measurements on a flooded or submerged bed. There is **no flood-vehicle-stability source that tabulates separate μ for wet asphalt vs saturated gravel vs saturated dirt**; the field deliberately collapses these into one conservative coefficient. Presenting a material-resolved μ as a flood-measured value is a category error, not a refinement, and must carry an explicit MISMATCH flag if used at all.

The nearest genuine exception is Smith, Modra & Felder (2019), *Journal of Flood Risk Management* 12:e12527, DOI 10.1111/jfr3.12527, the one flood study that measured traction across different bed materials (concrete, gravel, sand) at full scale. Its own stated conclusion is nevertheless that "a worst-case friction coefficient must be considered", so it does not supply a per-material μ table either. Its per-material numerics would have to be extracted from the full paper before any of them could be entered as VERIFIED.

### 3.3 Azhar et al. 2023 (μ = 0.55) vs Genesis `coup_friction`: two different quantities

**This wording is held in deliberate agreement with `README.md`. If either is edited, the other must be updated to match, they must not be allowed to drift into contradiction.**

The number **0.55 is citation-accurate to Azhar et al. 2023**, where it is a **physical Coulomb friction coefficient** between vehicle and bed in a DualSPHysics plus Chrono flood simulation. That attribution is not in dispute.

Genesis's `coup_friction` is a **numerical solver-coupling coefficient**: an impulse/stability parameter governing the fluid-to-rigid coupling in the MPM solver. It is not a Coulomb friction coefficient and shares only its name.

Therefore: **setting `coup_friction = 0.55` on the strength of Azhar et al. 2023 is an open modeling assumption, not a proven equivalence.** No source establishes that the solver parameter and the physical coefficient are the same quantity or take the same value. This must be stated as an assumption in Methods and Limitations, never as a cited physical parameter.

Two consequences worth stating plainly:

1. **The value is not automatically defensible even as physics.** 0.55 falls inside the 0.25 to 0.75 flood range of §3.2, but it is not the flood-literature central value; μ_wet ≈ 0.3 is. A physical bed-friction argument for a flooded crossing points at 0.3, not 0.55. (CLAUDE.md currently states the physical range as "0.3 to 0.55 per Azhar et al. 2023", which is narrower than, and sourced differently from, the 0.25 to 0.75 family in §3.2. The two are not yet reconciled.)
2. **Report what the code actually does.** Confirm the live value on the SDF collider calls before stating it. If a script carries the Genesis default of 0.4, report 0.4 as "engine default, not yet calibrated" rather than claiming 0.55. `can_it_ford_L2.py` is a known live example of this hazard: its `run_tag` string hardcodes `"cf0p4"` while the code sets `coup_friction=0.55`, so every output filename and CSV row from that script mislabels the value used.

---

## Source Index

**Vehicle parameters**
- NHTSA Light Vehicle Inertial Parameter Database — SAE 1999-01-1336 (DOI 10.4271/1999-01-1336): https://www.eng.auburn.edu/~dmbevly/mech4420/vehicle_params.pdf | https://saemobilus.sae.org/papers/measured-vehicle-inertial-parameters-nhtsas-data-november-1998-1999-01-1336
- SAE 2021-01-0970 (DOI 10.4271/2021-01-0970): https://saemobilus.sae.org/articles/measured-vehicle-inertial-parameters-nhtsas-data-august-2020-2021-01-0970
- Toyota UK Corolla tech-spec: https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210127M-Corolla-Tech-Spec.pdf
- Honda Canada 2025 Civic Sedan spec: https://www.honda.ca/-/media/Brands/Honda/Models/CIVIC-SEDAN/2025/PDF/2025-Honda-Civic-Sedan-Specifications---EN_v2.pdf
- Toyota UK Highlander tech-spec: https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/210321M-Highlander-Tech-Spec.pdf
- Ford 2021 F-150 Technical Specs: https://www.fromtheroad.ford.com/content/dam/fordmediasite/us/en/library/2021/specs/2021-F-150-Technical-Specs.pdf
- Ford F-150 Europe Technical Specs: https://f150europe.com/-/media/Project/Hedin/Navigo/F150EuropeSite/PDF/EN-MY23-F-150-Technical-Specs-Europe.pdf

**Flood-vehicle friction (added 2026-07-23, see §3.2)**
- Bonham & Hattersley (1967), origin of the μ = 0.3 conservative all-surface wet convention
- Martínez-Gomariz et al. (2017), *Urban Water Journal* 14(9):930-939 (DOI 10.1080/1573062X.2017.1301501), μ_dry ≈ 0.68
- Xiong et al. (2024), *Water Resources Research* 60:e2023WR036739, the 0.25 to 0.75 cross-study range
- Xia, Falconer, Xiao & Wang (2014), *Natural Hazards* 70:1619-1630 (DOI 10.1007/s11069-013-0889-2), μ = 0.25, C_d = 1.15 case
- Smith, Modra & Felder (2019), *Journal of Flood Risk Management* 12:e12527 (DOI 10.1111/jfr3.12527), full-scale multi-bed-material testing
- Azhar et al. (2023), *Journal of Flood Risk Management* (DOI 10.1111/jfr3.12885), source of the physical μ = 0.55, see §3.3 for why it does not transfer to `coup_friction`
- Underlying audit: `~/Downloads/Ground-Material Friction and Road-Camber Physics for Flood-Traversability Simulation: A Provenance-Grade Literature Audit.md` (2026-07-21). Not yet in-repo; a synthesized audit, so the DOIs above are the citable layer, not the audit document.

**Vehicle mass, real-mesh path (added 2026-07-23, see §3.1)**
- `yaris-coarse-v1l.key` line 27, LS-DYNA deck header "Version 1l, 1100 kg", primary source for the 1100 kg figure
- `reference_data/vehicle_data_master_reference_2026-07-21.json`, canonical parameter reference, corrected by commit `aa13ac1`
- `scripts/ford_sweep_driver.py:45`, the live consumer of the value

**Mesh → SDF coupling**
- Genesis `gs.materials.Rigid`: https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/material/rigid.html
- Genesis `gs.morphs.Mesh`: https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/options/morph/file_morph/mesh.html
- Genesis Mesh Processing: https://genesis-world.readthedocs.io/en/latest/user_guide/advanced_topics/mesh_processing.html
- Genesis `MPMOptions`: https://genesis-world.readthedocs.io/en/latest/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html
- Genesis issue #444 (non-convex SDF stability): https://github.com/Genesis-Embodied-AI/Genesis/issues/444
- Genesis issue #600 (MPM particles passing through rigid): https://github.com/Genesis-Embodied-AI/Genesis/issues/600
- Genesis issue #1114 (scale=0.001 example): https://github.com/Genesis-Embodied-AI/Genesis/issues/1114
- Warp `warp.Mesh`: https://nvidia.github.io/warp/api_reference/_generated/warp.Mesh.html
- Warp Built-Ins (mesh_query_point*): https://nvidia.github.io/warp/modules/functions.html
- Warp `warp.Volume`: https://nvidia.github.io/warp/api_reference/_generated/warp.Volume.html
- PhysicsNeMo Geometry Functionals: https://docs.nvidia.com/physicsnemo/latest/physicsnemo/api/nn/functionals/geometry.html
- trimesh: https://trimesh.org/trimesh.base.html
- PyMeshFix: https://github.com/pyvista/pymeshfix/blob/main/README.rst
- manifold3d: https://github.com/elalish/manifold
- mesh_to_sdf: https://github.com/marian42/mesh_to_sdf/blob/master/README.md
- OpenVDB `MeshToVolume.h`: https://www.openvdb.org/documentation/doxygen/MeshToVolume_8h.html
- NVIDIA SDF-resolution dev-forum thread: https://forums.developer.nvidia.com/t/invalid-inertia-when-sdf-mesh-for-collision-has-sdf-resolution-too-low/270823
- Omniverse Collision Behavior Guide: https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/dev_guide/guides/collision_guide.html

*Prepared for "Can It Ford?" — NSF SCIPE REU Site Award 2447887, TACC/UT Austin. CG height and inertia values are measured (NHTSA IPMD/VIMF); curb weight and dimensions are from manufacturer official spec sheets.*
