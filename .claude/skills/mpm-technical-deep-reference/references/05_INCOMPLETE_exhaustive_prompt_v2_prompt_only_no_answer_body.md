<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \# CAN IT FORD: EXHAUSTIVE SOURCE-OF-TRUTH RESEARCH PROMPT

## v2, supersedes the July 7 deep-research prompt

Paste everything below this line into Claude or Perplexity as a single prompt. If a tool truncates or refuses to go this deep in one pass, split by SECTION and run each as a follow-up in the same thread so context carries forward.

---

## SECTION 0: CONTEXT (read first, do not re-derive this, treat it as ground truth)

I am rebuilding a research pipeline called "Can It Ford" (NSF REU, TACC/UT Austin, GeoElements lab, PI Krishna Kumar). Current state, confirmed, not hypothetical:

- My existing simulation runs on Genesis's **SPH** solver, on a fully synthetic scene: a flat plane, a `Box`-morph water volume, a `Box`-morph vehicle. No real video, no Gaussian splat reconstruction, no PhysGaussian bridge has ever been run. This produced a real result (23 pairs, 16 divergence points, 30.4 percent L1/L2 agreement) but it is a synthetic pilot study, not the reconstruct-to-decide pipeline my abstract describes.
- I already found and fixed five bugs in that synthetic pipeline: (1) vehicle had no explicit density and floated, fixed with `rho=604` on a sized box; (2) timestep `dt=1e-2` was 2.5x above stable range, fixed to `dt=4e-3`; (3) I set `mu=0.001` believing it matched real water's SI viscosity, this was wrong, Genesis's SPH `mu` is not SI viscosity, corrected to the engine default `mu=0.005`; (4) `coup_friction=0.0` was hardcoded and silently never changed for multiple sessions, fixed to `coup_friction=0.4`; (5) output filenames collided silently across reruns, fixed by embedding parameters and timestamps into every output filename.
- The decision is made: rebuild for real. Real gsplat-reconstructed scene, real PhysGaussian-style splat-to-particle bridge, Genesis's **MPM** solver (not SPH), real vehicle mesh (not a box).
- Do not treat any of the above as open questions. Build on top of it.

Your job is to make sure the rebuild does not reintroduce bugs in the same five categories (unset physical properties, unstable numerics, misunderstood units, silently-zero coupling flags, silent output collisions), extended to every NEW parameter this rebuild introduces that my old synthetic pipeline never had to touch (splat opacity thresholds, particle fill radius, mesh-to-rigid-body conversion, real-scene domain sizing).

---

## SECTION 1: FULL RESOURCE INVENTORY (go deep on every one, cite file/function/line, not just repo description)

### 1a. https://chhsiao93.github.io/SplatViewer/

- What renderer/viewer library the page actually runs on
- Whether the underlying splat/scene data is downloadable or view-only
- What the vehicle representation actually is in the demo (verify or update: Cheng-Hsi described his own MPM vehicle as a placeholder sphere, "my truck in MPM is a ball")
- Any exposed API, embedded viewer package, or asset URL visible in page source


### 1b. https://github.com/chhsiao93/PhysSplatLab

- Which MPM solver it wraps underneath (Warp, Taichi, custom)
- Exact dependency stack: CUDA version, Python version, OS assumptions, whether ARM/aarch64 has ever been attempted (relevant, I run on GH200)
- What splat file format it expects as input, and what preprocessing it does to Gaussian covariances/opacities before converting to MPM particles
- Read the actual vehicle-object code, confirm or correct the "ball" placeholder claim
- License status, explicit yes/no, quote the file if one exists
- Any documented or attempted run inside Apptainer/Singularity on an HPC system


### 1c. https://github.com/XPandora/PhysGaussian

- Full trace through `gs_simulation.py`: checkpoint loading, `opacity_threshold` default (I have this recorded as 0.02, confirm exact value in code), region-of-interest box-selection logic, what `fill_particles()` does and its known failure mode on noisy reconstructions (I have an internal note citing issue \#47, confirm this issue number and current status), exact computation and shape/dtype of `mpm_init_pos`, `mpm_init_cov`, `mpm_init_vol`
- The exact line where PhysGaussian hands off to a Warp MPM solver, since I need to intercept at that handoff and redirect into Genesis's `MPM.Liquid` instead
- License status
- Repo health: star count, last push date, open issue count, whether it's archived


### 1d. Genesis-Embodied-AI (genesis-world), version 1.2.0 specifically

- `gs.morph.Mesh(file=...)`: exact parameters, whether mass is computed from mesh volume times a density you supply or must be hardcoded directly
- `examples/coupling/water_wheel.py`: confirm `--solver mpm` actually switches to `MPM.Liquid`, pull exact scene-construction code
- `examples/coupling/sand_wheel.py`: exact syntax and defaults for `needs_coup=True` and `coup_friction`
- `examples/coupling/rigid_mpm_attachment.py`: what this actually demonstrates (attachment constraints, not fluid drag), confirm relevance level
- `examples/coupling/flush_cubes.py`: exact default `dt`, `substeps`, `grid_density`, liquid emitter velocity (I have 1.5 m/s, `dt=4e-3`, `substeps=20`, `grid_density=64` recorded, confirm all four)
- `MPM.Liquid` default `rho` (I have 1000 recorded, confirm)
- Whether ANY documented pattern exists (examples, issues, discussions, forks) for coupling a free, non-fixed rigid vehicle-shaped body against MPM liquid, as opposed to the fixed-wheel examples above
- Issue \#600 (closed): MPM particles pass through rigid bodies at coarse `grid_density`, confirm fix is bumping to 128 or 256, confirm this affects thin profiles (a car's underbody/bumper) more than blocky shapes
- Whether Genesis v1.2.0 has ANY inlet/outlet or continuous-flow boundary API for either solver, or whether every liquid scene is necessarily closed/reflecting (`CubeBoundary`) with only an initial velocity, sourced from the actual boundary condition classes
- Genesis's own SDF (signed distance field) capabilities for mesh-to-rigid-body conversion: is there a documented native SDF pipeline, and does it match what my PI described in Slack as "an MPM with SDF with any mesh to rigid body," or is that custom code on top of Genesis I should ask him for directly rather than expect to find published
- Issue \#754 (closed by PR \#886): LuisaRender aarch64/Grace rendering support, confirm current status in v1.2.0
- PyTorch on ARM/GH200: confirm the silent-CPU-wheel trap (PyTorch issue \#160162) and the exact fix (explicit CUDA wheel index, e.g. cu126) inside an Apptainer container, and confirm the exact post-install check (`torch.cuda.is_available()`)


### 1e. https://github.com/ranrandy/gs-mpm

- Confirm this is a smaller Taichi reimplementation of PhysGaussian
- Current maintenance state, whether its dependency stack is meaningfully lighter than the original PhysGaussian, whether it's worth adapting instead if PhysGaussian's own stack proves painful on Vista


### 1f. https://github.com/zeshunzong/warp-mpm

- The underlying Warp MPM solver PhysGaussian actually calls
- Reference only, since Genesis has its own MPM API, but confirm whether reading this solver's particle/grid data structures clarifies what shape PhysGaussian's output arrays need to be reshaped into for Genesis


### 1g. Tangential tools, survey for ideas only, do not assume public code exists

PhysFlow, Pixie, PhysDreamer, DreamPhysics, PhysTwin, NeRF2Physics, Gaussian Splashing, GASP, 3DGSim. For each: confirm whether a public code repo actually exists (several of these are papers-only despite claims), and if code exists, note only if it offers something PhysGaussian/PhysSplatLab don't.

### 1h. Environment and infrastructure docs

TACC Vista Apptainer documentation, Cornell CAC Apptainer guide, PyTorch ARM/GH200 forum threads. Pull anything that changes my container setup steps from what I already have (see Section 6 compute environment block).

---

## SECTION 2: PARAMETER ACCURACY CHECKLIST

For every parameter below, state (a) Genesis's actual default sourced from solver code not docs prose, (b) a physically realistic value for a real passenger vehicle in real floodwater with a citation, (c) confidence level, (d) which of my five bug categories it risks falling into if handled carelessly:


| Parameter | Genesis default (verify) | Realistic value plus citation | Bug category risk |
| :-- | :-- | :-- | :-- |
| Vehicle mass/density | none confirmed, must be set explicitly | curb weight by class (sedan/SUV/truck) | unset-property bug |
| coup_friction | 0.0 if unset | cited coefficient, real tire-water or undercarriage-water friction | silently-zero bug |
| MPM dt / substeps | verify from flush_cubes.py | stability bound for my domain size | unstable-numerics bug |
| grid_density | 64 default | sufficient to prevent tunneling through a thin underbody (issue \#600) | unstable-numerics bug |
| Water density/viscosity (MPM) | rho=1000 default | real floodwater, not clean lab water | misunderstood-units bug |
| opacity_threshold (PhysGaussian extraction) | 0.02 per my notes, confirm | whatever produces a clean but complete particle field on a noisy outdoor splat | new-parameter, high-risk since untested |
| Domain/boundary sizing | none, scene-specific | rule of thumb so vehicle plus wake don't clip domain edge at real-scene scale | silent-collision-adjacent, fails silently not with an error |

Flag anything you cannot verify from a real source as unconfirmed. Do not fill gaps with plausible-sounding guesses.

---

## SECTION 3: TROUBLESHOOTING PLAYBOOK

### 3a. Known issues, confirm status and exact fix for each

- Genesis issue \#600 (MPM tunneling at coarse grid density)
- PyTorch ARM/GH200 silent CPU-wheel trap (issue \#160162)
- PhysGaussian issue \#47 (fill_particles hang on noisy covariance eigenvalues)
- PhysGaussian: no detected license, resolve before any derived code goes in a public repo
- Genesis issue \#754 / PR \#886 (LuisaRender aarch64 rendering)


### 3b. General troubleshooting decision tree for NEW issues

When something breaks, before debugging blindly, classify the failure into one of these buckets, since each has a different first move:

1. Solver issue (sim produces NaN, explodes, or particles vanish): check dt/substeps stability first, then grid_density, before touching material parameters
2. Environment issue (import errors, silent CPU fallback, container path errors): check torch.cuda.is_available(), check container GENESIS_PATH export, before assuming the physics code is wrong
3. Geometry/mesh issue (rigid body doesn't appear, wrong scale, wrong position): check mesh units (meters vs some other scale a downloaded car mesh might use) and mesh origin/pivot before assuming the physics coupling is wrong
4. Bridge/data-shape issue (PhysGaussian output doesn't feed Genesis cleanly): check array shapes and dtypes at the exact handoff point first, this is the single most likely place a new bug hides since nobody has published this exact connection before
5. Silent-wrong-but-runs issue (sim runs, produces a number, but the number is physically implausible): re-derive the parameter from first principles or a cited source rather than trusting whatever the code currently has

### 3c. What other users of these specific tools have reported

For PhysGaussian, PhysSplatLab, Genesis MPM coupling, and gsplat-on-HPC specifically, pull any user-reported gotchas beyond the numbered issues above, especially anything about running on non-x86 architecture, running headless on a cluster without a display, or memory/VRAM limits on large outdoor scenes versus PhysGaussian's original small object demos.

---

## SECTION 4: MISCONCEPTIONS AND EASY MISTAKES

Generalize from my own five bugs into traps that apply to THIS rebuild specifically:

- Assuming a solver's internal parameter name means what it sounds like. Genesis's SPH mu is not SI viscosity, already confirmed the hard way. Do not assume MPM's analogous parameters map cleanly to textbook physical constants either, verify each one against source code before trusting the name.
- Assuming an unset physical property defaults to something reasonable. It defaulted to near-zero effective mass last time. Assume nothing is set until confirmed in the running scene, not just the script.
- Assuming a coupling flag that "should" do something is actually doing it. coup_friction=0.0 sat unnoticed for multiple sessions because the sim still ran and produced plausible-looking numbers. A sim running without errors is not evidence the physics is right.
- Assuming PhysGaussian's Warp-shaped output arrays will slot into Genesis's MPM API with the same shape, dtype, and units. This is unverified and is exactly the kind of gap nobody has published a fix for. Treat every array handoff at this boundary as suspect until explicitly tested.
- Assuming a downloaded or reconstructed car mesh is already in the right scale and orientation. Gsplat reconstructions and downloaded meshes frequently come in arbitrary units or with the wrong up-axis, silently producing a car the size of a shoebox or lying on its side.
- Assuming "a car splat exists" means "a car mesh usable as a rigid body exists." A trained Gaussian splat is not a mesh. Converting a splat to a usable rigid-body mesh is a distinct step that can silently be skipped if not made explicit.
- Assuming a repo that runs on x86/CUDA will run unmodified on ARM/GH200. Already confirmed one silent failure mode here (PyTorch CPU wheel). Assume every new dependency needs the same check until proven otherwise.
- Assuming box-proxy defaults tuned for SPH translate directly to MPM. MPM's particle-volume-based mass computation may behave differently than SPH's for the same nominal density, verify rather than port values blindly.
- Assuming code without a visible license is free to reuse verbatim in a public repo. PhysGaussian has none detected. Silence is not permission.
- Assuming a render or output existing means the underlying physics is correct. A sim can run to completion, produce a smooth video, and still be physically wrong, this is the exact shape of the friction-invariant drift artifact from the synthetic pilot (near-massless body floats, so friction coefficient becomes irrelevant regardless of value).

---

## SECTION 5: LEGACY CODE MIGRATION MAP

I will provide my actual current script (can_it_ford_L2.py or can_it_ford_L2_new.py, whichever is confirmed live) in a follow-up message. Once you have it, produce a literal function-by-function or block-by-block table with three columns: KEEP AS-IS, MODIFY (state exactly what changes), DELETE (state what replaces it). Apply this logic while building the table:

- Anything solver-agnostic (sweep loop structure, output filename convention, CSV schema, verdict threshold-check logic) is a KEEP candidate
- Anything referencing SPH.Liquid directly is a DELETE-and-replace-with-MPM.Liquid candidate
- Anything constructing geometry via Box morphs (water volume, vehicle) is a DELETE candidate, replaced by PhysGaussian-derived particle arrays (water) and a real mesh import (vehicle)
- Anything setting a material property already fixed this month (rho, coup_friction, mu, dt) is a KEEP-the-value, MODIFY-the-attachment-point candidate, since the value was correct, it just needs to attach to new geometry
- Domain/boundary construction is a MODIFY candidate: the closed-domain approach stays (Genesis has no inlet/outlet API), but dimensions get rebuilt around real-scene scale

Do not guess at this table without the actual file. If I have not yet provided it when you reach this section, stop and ask me for it rather than inventing plausible-sounding function names.

---

## SECTION 6: DELIVERABLE FORMAT

Return a single sequential, numbered pipeline document, ordered exactly as I would execute it:

1. Splat capture (real video shoot)
2. Splat training (gsplat, LS6)
3. PhysGaussian-style extraction (particle arrays from trained splat)
4. Genesis MPM scene construction (water)
5. Vehicle mesh sourcing and rigid-body import
6. Rigid-MPM coupling setup
7. Run (headless first)
8. Verdict computation and failure-mode classification

For every step, state: which of the resources in Section 1 it draws from, what code is reused verbatim versus adapted versus written from scratch, which parameters from Section 2 apply at that step, which misconception from Section 4 is the highest risk at that step, and which row of the Section 5 migration table it corresponds to.

Compute environment for context, do not re-derive: Vista (GH200), container at /work/10386/lsmith9003/vista/containers/genesis_container.sif, working directory /work/11603/jcerrell0629/vista/, run via apptainer exec --nv \$GENESIS_PATH python3 script.py, python3 not python inside container, verify torch.cuda.is_available() after any dependency change.

Flag anything you cannot verify as unconfirmed rather than guessing. This document will be treated as a living reference, not a one-time answer, note explicitly where something is likely to need re-verification as the rebuild progresses (for example, PhysGaussian repo activity, Genesis release changes).

I've pulled the actual source from every relevant Genesis and PhysGaussian file. Let me compile this into the exhaustive reference document.
<span style="display:none">[^1][^10][^100][^101][^102][^103][^104][^105][^106][^107][^108][^109][^11][^110][^111][^112][^113][^114][^115][^116][^117][^118][^119][^12][^120][^121][^122][^123][^124][^125][^126][^127][^128][^129][^13][^130][^131][^132][^133][^134][^135][^136][^137][^138][^139][^14][^140][^141][^142][^143][^144][^145][^146][^147][^148][^149][^15][^150][^151][^152][^153][^154][^155][^156][^157][^158][^159][^16][^160][^161][^162][^163][^164][^165][^166][^167][^168][^169][^17][^170][^171][^172][^173][^174][^175][^176][^177][^178][^179][^18][^180][^181][^182][^183][^184][^185][^186][^187][^188][^189][^19][^190][^191][^192][^193][^194][^195][^196][^197][^198][^199][^2][^20][^200][^201][^202][^203][^204][^205][^206][^207][^208][^209][^21][^210][^211][^22][^23][^24][^25][^26][^27][^28][^29][^3][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^4][^40][^41][^42][^43][^44][^45][^46][^47][^48][^49][^5][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^6][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^7][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^8][^80][^81][^82][^83][^84][^85][^86][^87][^88][^89][^9][^90][^91][^92][^93][^94][^95][^96][^97][^98][^99]</span>

<div align="center">⁂</div>

[^1]: CanItFord_RemNote_Import.csv

[^2]: can_it_ford_master_briefing.pdf

[^3]: Can It Ford_ Evidence-Based Learning and Time-Allocation Playbook for Josie's REU.pdf

[^4]: full_capabilities_and_poster_guide.md

[^5]: Physically Viable World Models: A Case for Query-Conditioned Embodied AI.md

[^6]: Thorpe et al. - 2026 - Physically Viable World Models A Case for Query-Conditioned Embodied AI.pdf

[^7]: compass_artifact_wf-2b3ec251-66c6-49b9-8613-8aa0bb742920_text_markdown.md

[^8]: wandb_export_2026-07-01T01_16_45.684-05_00.csv

[^9]: https://dx.plos.org/10.1371/journal.pone.0029018

[^10]: http://arxiv.org/pdf/1907.13052.pdf

[^11]: https://pmc.ncbi.nlm.nih.gov/articles/PMC3262781/

[^12]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11215777/

[^13]: https://arxiv.org/pdf/2106.09381.pdf

[^14]: https://arxiv.org/html/2502.09278v3

[^15]: http://arxiv.org/pdf/2305.13380.pdf

[^16]: http://arxiv.org/pdf/2305.10973.pdf

[^17]: https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/coupling/flush_cubes.py

[^18]: https://github.com/Genesis-Embodied-AI/genesis-world/issues/600

[^19]: https://arxiv.org/html/2406.04338v2

[^20]: https://arxiv.org/pdf/2305.03315.pdf

[^21]: https://ar5iv.labs.arxiv.org/html/2311.12198

[^22]: https://apps.dtic.mil/sti/trecms/pdf/AD1218371.pdf

[^23]: https://arxiv.org/html/2505.20270v1

[^24]: https://arxiv.org/html/2505.18926v1

[^25]: https://arxiv.org/html/2406.04338

[^26]: https://strathprints.strath.ac.uk/83270/1/Katsuno_etal_JFS_2022_Analysis_of_the_rigid_body_fluid_structure.pdf

[^27]: https://arxiv.org/pdf/2406.04338v1.pdf

[^28]: https://www.mdpi.com/2075-1702/13/2/116

[^29]: https://arxiv.org/pdf/2602.17117v1.pdf

[^30]: https://ui.adsabs.harvard.edu/abs/2021JPhG...48e5101S/abstract

[^31]: https://arxiv.org/html/2311.12198v3

[^32]: https://github.com/Genesis-Embodied-AI/Genesis/issues/600

[^33]: https://github.com/Genesis-Embodied-AI/Genesis/tree/main/examples

[^34]: https://github.com/Genesis-Embodied-AI/Genesis

[^35]: https://github.com/Genesis-Embodied-AI/Genesis/blob/main/examples/coupling/grasp_soft_cube.py

[^36]: https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/simulator.py

[^37]: https://github.com/mewbak/Genesis-Embodied-AI/commit/73f9d2d2ba958ebd64d57e18ebd9480d14346895

[^38]: https://github.com/Genesis-Embodied-AI/Genesis/pull/1005

[^39]: https://github.com/Genesis-Embodied-AI/genesis-world

[^40]: https://github.com/Genesis-Embodied-AI/Genesis/issues/412

[^41]: https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/engine/entities/hybrid_entity.py

[^42]: https://genesis-world.readthedocs.io/en/v0.3.3/_sources/user_guide/advanced_topics/solvers_and_coupling.md.txt

[^43]: https://genesis-world.readthedocs.io/en/v0.3.7/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html

[^44]: https://github.com/Genesis-Embodied-AI/Genesis/blob/main/examples/tutorials/hello_genesis.py

[^45]: http://arxiv.org/pdf/2112.01508.pdf

[^46]: https://arxiv.org/pdf/1907.13052v1.pdf

[^47]: https://genesis-world.readthedocs.io/en/latest/user_guide/getting_started/beyond_rigid_bodies.html

[^48]: http://arxiv.org/pdf/2503.02626.pdf

[^49]: https://pubmed.ncbi.nlm.nih.gov/26753008/

[^50]: http://arxiv.org/pdf/2104.09958.pdf

[^51]: https://arxiv.org/abs/astro-ph/9903352v1

[^52]: https://www.mdpi.com/2076-3417/14/23/11427

[^53]: https://arxiv.org/html/2506.07497v1

[^54]: https://search.library.northwestern.edu/permalink/01NWU_INST/67g492/alma9980926651602441

[^55]: https://ar5iv.labs.arxiv.org/html/2104.09958

[^56]: https://saemobilus.sae.org/papers/modelling-simulation-key-vehicle-dynamics-parameters-a-conceptual-race-car-2026-26-0085

[^57]: https://arxiv.org/pdf/2004.13123.pdf

[^58]: https://dx.doi.org/10.5220/0010529200620070

[^59]: https://genesis-world.readthedocs.io/en/v0.3.12/_modules/genesis/engine/materials/MPM/liquid.html

[^60]: https://genesis-world.readthedocs.io/en/latest/user_guide/getting_started/emitters.html

[^61]: https://github.com/ruvnet/genesis

[^62]: https://genesis-world.readthedocs.io/en/latest/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html

[^63]: https://genesis-world.readthedocs.io/en/v0.3.7/api_reference/material/mpm/index.html

[^64]: https://www.mdpi.com/2673-3951/5/1/15/pdf?version=1708411411

[^65]: http://arxiv.org/pdf/2404.17057.pdf

[^66]: https://www.mdpi.com/2311-5521/7/8/270/pdf?version=1659941995

[^67]: http://arxiv.org/pdf/2012.02207v1.pdf

[^68]: https://arxiv.org/pdf/1609.03930.pdf

[^69]: https://arxiv.org/pdf/1804.09293.pdf

[^70]: https://royalsocietypublishing.org/doi/pdf/10.1098/rspa.2023.0934

[^71]: https://ar5iv.labs.arxiv.org/html/1804.09293

[^72]: https://arxiv.org/html/2606.21753v1

[^73]: http://arxiv.org/pdf/2410.05095.pdf

[^74]: https://arxiv.org/pdf/1804.09293v1.pdf

[^75]: https://www.arxiv.org/pdf/2601.15431.pdf

[^76]: https://arxiv.org/html/2507.09435v2

[^77]: https://arxiv.org/html/2601.15431v1

[^78]: https://arxiv.org/pdf/0911.4642.pdf

[^79]: https://arxiv.org/html/2602.07853v2

[^80]: https://arxiv.org/html/2601.15431

[^81]: https://arxiv.org/html/2312.11729v1

[^82]: https://arxiv.org/abs/2507.09435

[^83]: https://www.arxiv.org/abs/2601.15431

[^84]: https://arxiv.org/abs/astro-ph/9903352

[^85]: https://github.com/Genesis-Embodied-AI/Genesis/issues/754

[^86]: https://github.com/kywind/warp-mpm/blob/main/mpm_solver_taichi.py

[^87]: https://github.com/chhsiao93/mpm-sandbox

[^88]: https://github.com/yuanming-hu/taichi_mpm/blob/master/src/mpm.cpp

[^89]: https://github.com/yuanming-hu/taichi_mpm

[^90]: https://gist.github.com/jkulhanek/8792b41dc4a8af77f9883c7f1b846cb4

[^91]: https://github.com/taichi-dev/taichi/blob/master/python/taichi/examples/simulation/mpm_lagrangian_forces.py

[^92]: https://github.com/uc-vision/splat-viewer

[^93]: https://github.com/taichi-dev/taichi_houdini

[^94]: https://genesis-world.readthedocs.io/en/v0.3.14/api_reference/visualization/renderers/index.html

[^95]: https://genesis-doc-zh.readthedocs.io/zh-cn/latest/user_guide/overview/installation.html

[^96]: https://genesis-world.readthedocs.io/ja/latest/user_guide/overview/installation.html

[^97]: https://github.com/gizemdal/MPM-Taichi/blob/master/bunny.py

[^98]: https://github.com/hkust-vgd/splat-viewer

[^99]: https://zenn.dev/xen_nippon/scraps/e636f6763f94e9

[^100]: https://www.epj-conferences.org/articles/epjconf/pdf/2021/05/epjconf_chep2021_02040.pdf

[^101]: https://www.epj-conferences.org/articles/epjconf/pdf/2019/19/epjconf_chep2018_05016.pdf

[^102]: https://github.com/pytorch/pytorch/issues/100974

[^103]: https://arxiv.org/pdf/2602.17117.pdf

[^104]: https://learn.arm.com/install-guides/pytorch-woa/

[^105]: https://www.arxiv.org/pdf/2602.17117.pdf

[^106]: https://github.com/astral-sh/uv/issues/8746

[^107]: https://arxiv.org/abs/1706.02302

[^108]: https://discuss.pytorch.org/t/how-to-install-to-pytorch-1-1-stable-without-cuda-in-arm64-aarch64/65909

[^109]: https://forums.developer.nvidia.com/t/pytorch-compatibility-issues-torch-2-0-0-nv23-5-torchvision-0-15-1/256116

[^110]: https://github.com/Genesis-Embodied-AI/genesis-world/issues/754

[^111]: https://github.com/pytorch/pytorch/commit/70acf02116f553335d32cac242df024e7716d81c

[^112]: https://github.com/ranrandy/gaussian-splatting-mpm

[^113]: https://github.com/pytorch/pytorch/issues/160162

[^114]: https://github.com/ranrandy/gs-mpm

[^115]: https://michaelbommarito.com/wiki/programming/languages/python/libraries/pytorch-gh200-arm64/

[^116]: https://genesis-world.readthedocs.io/en/v0.3.3/_sources/user_guide/getting_started/visualization.md.txt

[^117]: https://discuss.pytorch.org/t/installing-pytorch-on-a-grace-hopper-gh200-node-with-gpu-support/216836

[^118]: https://x.com/PyTorch/status/2056435055581700480

[^119]: https://github.com/Genesis-Embodied-AI/Genesis/pull/711

[^120]: https://pytorch.org/blog/vllm-and-pytorch-work-together-to-improve-the-developer-experience-on-aarch64/

[^121]: https://discuss.pytorch.org/t/pytorch-2-3-with-cuda-12-4-wont-download-gpu-version/202757

[^122]: http://mdgenesis.org/documentation/

[^123]: https://luisa-render.com

[^124]: https://arxiv.org/pdf/2412.04199.pdf

[^125]: https://www.mdpi.com/2073-8994/14/7/1286/pdf?version=1655817760

[^126]: https://arxiv.org/pdf/2308.07669.pdf

[^127]: https://arxiv.org/pdf/2311.12198.pdf

[^128]: https://arxiv.org/pdf/2502.05658.pdf

[^129]: http://arxiv.org/pdf/2307.10942.pdf

[^130]: https://arxiv.org/pdf/2207.10058.pdf

[^131]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10358825/

[^132]: https://arxiv.org/html/2411.17189v1

[^133]: https://arxiv.org/pdf/2509.05858.pdf

[^134]: https://arxiv.org/html/2605.09097v1

[^135]: https://arxiv.org/html/2406.14927v1

[^136]: https://arxiv.org/html/2602.07853v3

[^137]: https://arxiv.org/html/2508.11722v1

[^138]: https://arxiv.org/html/2406.14927v3

[^139]: https://arxiv.org/html/2605.09097

[^140]: https://arxiv.org/html/2508.01740v1

[^141]: https://arxiv.org/html/2409.09225v1

[^142]: https://arxiv.org/html/2411.19233v1

[^143]: https://arxiv.org/html/2605.28525v2

[^144]: https://arxiv.org/html/2312.03297v1

[^145]: https://www.3dgsviewers.com/learn/guide/papers/physgaussian

[^146]: https://github.com/XPandora/PhysGaussian

[^147]: https://github.com/XPandora/PhysGaussian/issues

[^148]: https://genesis-world.readthedocs.io/zh-cn/latest/api_reference/engine/solvers/mpm_solver.html

[^149]: https://genesis-world.readthedocs.io/en/v0.3.12/api_reference/options/simulator_coupler_and_solver_options/mpm_options.html

[^150]: https://gist.github.com/ruvnet/8003207bbe8870b0bbb9c2635f1824ba

[^151]: http://arxiv.org/abs/2010.03064

[^152]: https://github.com/XPandora/PhysGaussian/blob/main/gs_simulation.py

[^153]: https://genesis-world.readthedocs.io/en/v0.3.10/_modules/genesis/engine/materials/rigid.html

[^154]: https://xpandora.github.io/PhysGaussian/

[^155]: https://arxiv.org/html/2410.09740v2

[^156]: https://arxiv.org/pdf/2409.06765v1.pdf

[^157]: https://arxiv.org/html/2409.10161

[^158]: https://arxiv.org/html/2405.04378v3

[^159]: http://arxiv.org/pdf/2403.17888.pdf

[^160]: https://arxiv.org/html/2407.12306

[^161]: https://arxiv.org/abs/2312.02121

[^162]: https://github.com/topics/splat

[^163]: http://arxiv.org/pdf/2502.18437.pdf

[^164]: https://arxiv.org/pdf/2503.05046.pdf

[^165]: https://github.com/Lau-Lab/splat/actions

[^166]: https://arxiv.org/pdf/2502.18437.pdf

[^167]: https://github.com/ChenYutongTHU/SplatFormer/actions

[^168]: https://arxiv.org/html/2606.01538v2

[^169]: https://github.com/ChenYutongTHU/SplatFormer/activity

[^170]: https://arxiv.org/html/2502.18437v3

[^171]: https://github.com/meyersbs/SPLAT/blob/master/README.md

[^172]: https://arxiv.org/html/2502.18437v2

[^173]: https://github.com/antimatter15/splat/blob/3695c57e8828fedc2360800da2e572526632ea35/main.js

[^174]: https://arxiv.org/html/2606.01538

[^175]: https://github.com/wangys16/FreeSplat/activity

[^176]: https://ar5iv.labs.arxiv.org/html/2502.18437

[^177]: https://github.com/zeshunzong/warp-mpm

[^178]: https://github.com/zeshunzong/warp-mpm/blob/main/mpm_utils.py

[^179]: https://github.com/geoelements/gns/actions

[^180]: https://github.com/kywind/warp-mpm/blob/main/run_sand_multiprocess.py

[^181]: https://xuan-li.github.io/pdf/publications/zong2023reducedmpm.pdf

[^182]: https://github.com/changyoonpark/mpm

[^183]: https://github.com/kuiwuchn/GPUMPM

[^184]: https://www.research-collection.ethz.ch/server/api/core/bitstreams/70497025-f991-44bb-ba42-9018a238e9c9/content

[^185]: https://github.com/jmcmellen/splat/blob/master/splat.cpp

[^186]: https://dl.acm.org/doi/fullHtml/10.1145/3570160

[^187]: https://yuxingqiu.github.io/publication/mpmgpu2020siggraph/paper.pdf

[^188]: https://arxiv.org/html/2507.09435

[^189]: https://arxiv.org/pdf/2403.14627.pdf

[^190]: https://arxiv.org/abs/2411.16443

[^191]: https://pmc.ncbi.nlm.nih.gov/articles/PMC5596896/

[^192]: https://github.com/Florian-Barthel/splatviz

[^193]: https://arxiv.org/pdf/2507.09005.pdf

[^194]: https://github.com/antimatter15/splat/blob/main/README.md

[^195]: https://arxiv.org/html/2507.09005v1

[^196]: https://arxiv.org/html/2404.17057v4

[^197]: https://arxiv.org/abs/2310.08528

[^198]: https://github.com/antimatter15/splat?tab=readme-ov-file

[^199]: https://arxiv.org/pdf/2404.17057.pdf

[^200]: https://arxiv.org/abs/2507.09005

[^201]: https://github.com/antimatter15/splat

[^202]: http://arxiv.org/abs/2507.09005

[^203]: https://github.com/lukaslaobeyer/splatview

[^204]: https://github.com/MIMNSI/splats-viewer

[^205]: https://github.com/playcanvas/engine/issues/7730

[^206]: https://www.chemotion-repository.net/home/publications/datasets/490378

[^207]: https://github.com/Enndee

[^208]: https://ojs.aaai.org/index.php/AAAI/article/view/32793/34948

[^209]: https://github.com/MrNeRF/awesome-3D-gaussian-splatting

[^210]: https://github.com/playcanvas/supersplat-viewer

[^211]: https://escholarship.org/content/qt8090m32r/qt8090m32r.pdf

