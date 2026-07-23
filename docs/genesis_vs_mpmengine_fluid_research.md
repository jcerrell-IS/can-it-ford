# Genesis vs kks32/mpm-engine, Fluid Physics and Photoreal Rendering, Sourced Findings

Compiled July 21, 2026. Every claim below is tied to a clickable source. Where I could not find something, that's stated plainly rather than filled in with a guess.

---

## Headline finding, read this first

`kks32/mpm-engine` already has a built-in, functioning PhysGaussian-style Gaussian Splat simulation system, `src/warpmpm/splats`, with `examples/splat_sim.py`. It loads real trained 3D Gaussian Splatting PLY files (the standard INRIA layout, the same format `gsplat`'s own trainer can export), fills the interior with material points, advects covariances, rotates spherical-harmonic color coefficients under deformation, and exports frames as PLY compatible with what the codebase's own docs call "Cheng-Hsi's SplatViewer." Critically, `src/warpmpm/vehicle.py`'s `load_vehicle()` function can load a **vehicle body directly from a 3DGS splat PLY**, not just a box proxy.

This means the full splat-to-MPM bridge you thought only existed as a citation in your abstract may already be built, inside Kumar's own repo, not something you'd need to write from scratch against Genesis. This wasn't previously surfaced in your project's own audits. Worth checking `examples/splat_sim.py` and `load_vehicle()` directly before assuming any of the "build the bridge" work in your Master Instructions still needs doing from zero.

Source: [kks32/mpm-engine DeepWiki query, splats package and splat_sim.py](https://deepwiki.com/search/describe-in-detail-the-srcwarp_5c917f46-6ec2-45bd-bd8c-6bb97efd7b64), reading `src/warpmpm/splats/`, `examples/splat_sim.py`, and `src/warpmpm/vehicle.py` in [kks32/mpm-engine](https://github.com/kks32/mpm-engine).

---

## Q1: Does Genesis's weakly-compressible water produce physically correct wave behavior at this scale?

**No dedicated benchmark paper found comparing Genesis's fluid solver against an analytical or experimental wave case.** I looked specifically for this and could not find one, stating that plainly rather than padding it. What does exist, from real bug reports:

- **SPH particles scatter uncontrollably on collision.** Reported directly against `Genesis-Embodied-AI/genesis-world`: particles hit a mesh or floor and scatter at extreme velocity regardless of the collision surface, a "too bouncy/unstable" failure exactly matching your concern. Reducing collision velocity or particle size partially mitigates it but wasn't viable for the reporter's own water-pouring task.
  Source: [Issue #685, SPH particles scatter uncontrollably upon collision](https://github.com/Genesis-Embodied-AI/genesis-world/issues/685)

- **MPM demo produces unexpected bouncing/jerking behavior**, differing from the documentation's own reference video, on a standard RTX 4090 setup, not exotic hardware.
  Source: [Issue #476, simulation result of MPM demo is not as expected](https://github.com/Genesis-Embodied-AI/Genesis/issues/476)

- **No macro-scale wave/hydrodynamics model exists at all**, confirmed by an open feature request: Genesis only simulates fluid at the individual-particle level, there's no trochoidal/ocean-scale wave model, and the requester separately notes that `splashsurf` surface reconstruction (the standard external tool, see Q5) doesn't run on GPU in their setup.
  Source: [Issue #682, Marine and wave simulation, buoyancy, hydrodynamics](https://github.com/Genesis-Embodied-AI/Genesis/issues/682)

**On the `kks32/mpm-engine` side, this is actually documented directly, not just inferred from bug reports:** the repo's own performance notes state that to keep the timestep near your target 1e-4s, the bulk modulus is deliberately softened "far below real water," which the docs themselves say means the speed of sound, and therefore bulk wave propagation, does not accurately reflect real-world water. They also document a measured +22% apparent volume inflation in pouring scenarios with the current explicit solver. A future implicit density-projection solver is planned to fix both, not yet shipped.
Source: `docs/performance.md` in [kks32/mpm-engine](https://github.com/kks32/mpm-engine), via [DeepWiki query on wave propagation and free-surface behavior](https://deepwiki.com/search/how-does-this-codebase-handle_745f1a9a-149b-4d69-9dd4-b4ac9ed7e927)

**Bottom line on Q1:** neither engine has a published wave-propagation validation for your exact scale. kks32/mpm-engine is more honest about it, its own docs admit the softened-bulk-modulus tradeoff outright. Genesis's issue tracker shows real users hitting "too bouncy" and "not what the demo showed" behavior on the fluid side.

---

## Q2: Bow-wave and wake formation, moving rigid body through liquid

**No dedicated report found on bow-wave/wake specifically, in Genesis or in graphics-MPM/SPH more generally, as a named phenomenon people have studied or fixed.** This appears to be a real gap in what's publicly discussed, not something either community has written up as solved or broken.

What exists as adjacent evidence:

- `kks32/mpm-engine` has this **directly built and tested**, not just documented as aspirational: `tests/test_vehicle.py` includes `test_flood_pushes_rigid_body_downstream`, an automated test verifying a rigid body is pushed downstream by a fluid surge. The `FloodScene` class in `src/warpmpm/vehicle.py` couples grid momentum into vehicle force and torque every substep specifically for this kind of interaction.
  Source: `tests/test_vehicle.py`, `src/warpmpm/vehicle.py`, via [DeepWiki query on shallow water and rigid body interaction](https://deepwiki.com/search/how-does-this-codebase-handle_745f1a9a-149b-4d69-9dd4-b4ac9ed7e927)

- Genesis's grasping/manipulation issues (below, Q3) show rigid-MPM coupling failing in the opposite direction, an arm failing to grip an MPM object correctly, which is evidence the rigid-MPM contact model has real, reported weak spots generally, even if nobody's filed one specifically about lateral wake formation in liquid.

**Bottom line on Q2:** treat this as unvalidated in both engines rather than "known broken" or "known solved." kks32/mpm-engine has the closer, tested analog (downstream push under surge), which is at least a partial proxy for wake-type behavior, Genesis doesn't have an equivalent automated test that I could find.

---

## Q3: Additional Genesis issues beyond your existing list

Confirmed via direct search, all beyond the five you already had:

| Issue | What it shows | Link |
|---|---|---|
| #1640 | Robotic arm fails to properly grasp an MPM cube, rigid-MPM contact producing wrong behavior | [github.com/.../issues/1640](https://github.com/Genesis-Embodied-AI/Genesis/issues/1640) |
| #476 | MPM demo bounces/jerks unexpectedly vs. documented reference video, standard RTX 4090 | [github.com/.../issues/476](https://github.com/Genesis-Embodied-AI/Genesis/issues/476) |
| #685 | SPH particles scatter uncontrollably on any collision surface | [github.com/.../issues/685](https://github.com/Genesis-Embodied-AI/genesis-world/issues/685) |
| #682 | No macro wave/hydrodynamics model exists, open feature request | [github.com/.../issues/682](https://github.com/Genesis-Embodied-AI/Genesis/issues/682) |
| #1598 | MPM Elastic "pbs" sampler regressed, stopped working after a new release | [github.com/.../issues/1598](https://github.com/Genesis-Embodied-AI/genesis-world/issues/1598) |
| #1180 | Differentiable MPM push example fails, missing `GLIBCXX_3.4.26` symbol at runtime | [github.com/.../issues/1180](https://github.com/Genesis-Embodied-AI/Genesis/issues/1180) |
| #1881 | Liquid pouring simulation reported as very slow even on a workstation-class GPU | [github.com/.../issues/1881](https://github.com/Genesis-Embodied-AI/Genesis/issues/1881) |
| #124 | Liquid sim on macOS Metal backend, sampler falls back and warns | [github.com/.../issues/124](https://github.com/Genesis-Embodied-AI/Genesis/issues/124) |
| #42 | LuisaRender fails to build on arm64 specifically, `Undefined symbols for architecture arm64`, confirmed on Apple Silicon (M3 Pro), same failure category as the x86-only build issue you already had, now with an exact error and a real thread | [github.com/.../issues/42](https://github.com/Genesis-Embodied-AI/Genesis/issues/42) |

No Discord content surfaced in search, Discord threads generally aren't publicly indexed. If you have access to Genesis's own Discord, a manual search there for "MPM liquid" or "wave" would be the only way to check that channel specifically, I can't do it from here.

---

## Q4: kks32/mpm-engine's fluid dynamics documentation and behavior, vs Genesis

Better documented on the honesty-about-limitations front, and has capability Genesis doesn't:

- **Fluid model**: weakly compressible Newtonian, softened bulk modulus, explicitly documented tradeoff (see Q1).
- **`FloodScene` class exists specifically for your scenario**: shallow water depth, surge velocity, rigid vehicle coupling, already parameterized for depths in the 0.08-0.6m range and velocities 1-3 m/s in `experiments/flood_sweep.py`, closely matching your own target ranges.
- **Splat simulation is real and load-bearing**, not experimental (see headline finding above).
- **Known, self-reported limitations**: +22% volume inflation in pouring, CDF colliders are "soft" (fluid can sit a few mm inside a thin boundary) and only read a geometry-dependent fraction of the true load, SDF colliders recommended instead for calibrated force readings.
- No public GitHub issues found on `kks32/mpm-engine` itself beyond what's already in your project files, it's a smaller, less-trafficked repo than Genesis, so there isn't a large independent bug-report corpus to check against.

Source for all of the above: [DeepWiki queries against kks32/mpm-engine](https://deepwiki.com/search/how-does-this-codebase-handle_745f1a9a-149b-4d69-9dd4-b4ac9ed7e927), reading `docs/performance.md`, `src/warpmpm/vehicle.py`, `experiments/flood_sweep.py`, `tests/test_analytic_benchmarks.py`, `tests/test_cdf_transfers.py` directly.

---

## Q5: Particle-to-photoreal render pipeline, headless Linux/ARM specifically

The real, established tool for this is **splashsurf** (`InteractiveComputerGraphics/splashsurf`), a Rust CLI and library, marching-cubes-based surface reconstruction purpose-built for SPH/MPM particle output. Takes VTK, PLY, BGEO, or raw XYZ particle files, outputs a closed triangle mesh. Has weighted Laplacian smoothing specifically to remove the "typical bumps" that make raw particle-derived surfaces look blobby or jelly-like.
Source: [InteractiveComputerGraphics/splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf), [splashsurf_lib docs](https://docs.rs/splashsurf_lib)

- Python bindings exist (`pysplashsurf` on PyPI), but the published wheels I found are built for `x86_64`, `i686`, and `armv7l`, **not** `aarch64`/`arm64`, which is what GH200 actually is. This means `pip install pysplashsurf` may not have a prebuilt wheel for Vista, worth checking directly before assuming it installs cleanly, you'd likely need to build from source via `cargo`, which splashsurf being a normal Rust crate should support on aarch64, but that's not confirmed, only inferred from it being ordinary Rust.
  Source: [pysplashsurf on PyPI, file listing](https://pypi.org/project/pysplashsurf/)

- **Real precedent for exactly this pipeline**: a published framework paper reconstructs SPH particle output to a surface using SplashSurf, then renders in Blender for the final visually compelling result. Directly matches "accurate and visually compelling" as their own stated goal.
  Source: [Journey into SPH Simulation: A Comprehensive Framework and Showcase, arXiv 2403.11156](https://arxiv.org/pdf/2403.11156)

- Genesis's own issue tracker independently confirms `splashsurf` is the tool people reach for even inside the Genesis ecosystem, and flags that it doesn't run on GPU in at least one reporter's setup, a performance consideration for a headless HPC run.
  Source: [Genesis Issue #682](https://github.com/Genesis-Embodied-AI/Genesis/issues/682)

**Nothing found specific to headless/ARM Blender rendering** beyond general Blender-on-Linux documentation, which is standard and not worth padding this report with.

---

## Q6: Anyone doing this exact pipeline on ARM64/Grace-Hopper specifically

**Nothing found.** No report, issue, paper, or forum post of shallow moving water plus rigid vehicle plus photoreal render on GH200 or any Grace-Hopper system specifically. This combination is genuinely rare enough that it isn't showing up anywhere searchable. Closest adjacent, general GH200 build guidance, not fluid-sim specific:

- Practical, detailed GH200 PyTorch setup guide confirming your already-known CPU-only-wheel problem and giving the actual fix, use PyTorch's nightly aarch64+CUDA builds or NVIDIA's own prebuilt container rather than plain `pip install torch`.
  Source: [pytorch cuda setup for nvidia gh200 (arm64), Michael Bommarito](https://michaelbommarito.com/wiki/programming/languages/python/libraries/pytorch-gh200-arm64/)

---

## Where this leaves you, one paragraph

The most concrete, actionable new information here is the `kks32/mpm-engine` splats module, it changes "would I need to build a PhysGaussian bridge" from an open research question into "check whether this already-existing code does what I need." Second most useful: `splashsurf` is the real tool for particle-to-mesh, but confirm it actually builds on Vista's aarch64 before planning around it, the PyPI wheels don't obviously cover that architecture. Everything else above is context and citations for what you already suspected, real users hitting bounce/scatter/inflation problems in both engines' fluid solvers, nobody having validated wave physics rigorously in either, and GH200 being niche enough that you're genuinely off the well-trodden path.
