# Chrono on GH200: engine go/no-go

**Dispatch 13.** Branch `claude/fork-chrono-eval`. Written 2026-08-14.

## VERDICT: GO

Chrono::FSI-SPH builds and runs clean on GH200 aarch64. The milestone was fixed in
advance by the dispatch, and it is the milestone that was met, not a moved one:

> a clean run of `demo_FSI-SPH_DamBreak` or `demo_FSI-SPH_ObjectDrop` on a GH200
> node, producing output, with the build recipe recorded.

Both demos ran. Both produced output. The recipe is
`scripts/chrono_gh200_fsi_build.sbatch`, which is the file that actually executed,
not a reconstruction.

**Total cost of the answer: 2 minutes 15 seconds of GH200 node time across two
`gh-dev` jobs.** The build itself was 94 seconds. This came in far under the
"moderate build-porting task" budget the dispatch allowed.

---

## Evidence, tagged by how it was obtained

All `[live]` items were read from job stdout or from files on Vista `$SCRATCH`
this session. All `[source]` items were opened directly in the upstream repo.

### Hardware and toolchain `[live]`

| Item | Value |
|---|---|
| Node | `c642-021.vista.tacc.utexas.edu`, partition `gh-dev` |
| Arch | `aarch64`, Neoverse-V2 (Grace) |
| GPU | **NVIDIA GH200 120GB, compute capability 9.0, driver 590.48.01, 97871 MiB** |
| OS | Rocky Linux 9.7 |
| Compiler | GCC 13.2.0 (module `gcc/13.2.0`) |
| CUDA | **12.6.20**, target triple `sbsa-linux` |
| Thrust | 2.5.0 (from the CUDA toolkit) |
| CMake | 4.1.1 |
| Eigen | 3.4.0, fetched to `$SCRATCH` |
| Chrono | `1b90a9f9854575f1ce1287d359d957b0273c075f` |

### Results `[live]`

| Stage | Result |
|---|---|
| Configure, core only | exit 0, `C++17 compiler support: TRUE` |
| Configure, FSI-SPH | exit 0, `Chrono::FSI::SPH GPU backend: CUDA`, `CUDA archs (filtered): 90` |
| Build | **RC 0, 94 s**, `-j 24` on 72 allocated cores |
| Libraries | `libChrono_core.so`, `libChrono_fsi.so`, **`libChrono_fsisph.so`** |
| Demos built | 14 FSI-SPH demos, including both milestone targets |
| `demo_FSI-SPH_DamBreak` | **RC 0**, 30,327 markers (16,731 fluid + 13,596 boundary), 11 output CSVs |
| `demo_FSI-SPH_ObjectDrop` | **RC 0**, 78,772 markers incl. 759 rigid BCE, 3,199 steps, 21 output files |

Job IDs `911509` (build + DamBreak) and `911511` (verification), both `COMPLETED`.

---

## The GO is stronger than the milestone required, and here is why that matters

The dispatch accepted *either* demo. Passing on `DamBreak` alone would have been a
**weak** result, and it is worth stating why rather than quietly banking the pass:
`DamBreak`'s own counter block reports `numFsiBodies: 0` `[live]`. It exercises the
WCSPH fluid solver and **none** of the rigid-body force coupling, which is the only
reason Chrono is a candidate for this fork at all. A GO resting on `DamBreak` would
license no claim whatsoever about two-way coupling.

So a second job was run against `ObjectDrop`, which instantiates a real `ChBody`
`[source: demo_FSI-SPH_ObjectDrop.cpp:275]`, and two falsifiable checks were added.

**Control 1, did the fluid actually advance?** `[live]` "It produced files" is not
"it simulated". If the solver had silently no-oped, frame 0 and frame 9 would be
byte-identical.

```
md5 fluid0: 0da80835c5aba0ad2f3fc83bfe66d1d9
md5 fluid9: b9ac93c5db221a401bea347405074915
CONTROL PASSED: frames differ, the solver advanced state.
differing lines: 16731     (= every fluid marker)
```

**Control 2, did the two-way coupling do work?** `[live]` `ObjectDrop` writes
`fsi/FSI_body0.csv` with columns
`Time,x,y,z,q0,q1,q2,q3,Vx,Vy,Vz,Fx,Fy,Fz,Tx,Ty,Tz`, i.e. the accumulated fluid
force and torque on the body:

| t (s) | z (m) | Vz (m/s) | Fz (N) |
|---|---|---|---|
| 0.00 | 1.17000 | 0.0000 | 0.00 |
| 0.05 | 1.15774 | -0.4877 | 2.39 |
| 0.10 | 1.12853 | -0.6220 | 39.83 |
| 0.15 | 1.09665 | -0.6774 | 42.03 |
| 0.20 | 1.06304 | -0.6291 | 58.56 |
| 0.25 | 1.03469 | -0.4997 | 56.98 |
| 0.30 | 1.01452 | -0.2897 | 66.83 |
| 0.35 | 1.00573 | -0.0672 | 64.28 |

This is a coherent water-entry: the body descends, the fluid reaction `Fz` builds
from 0 to roughly 65 N, and that upward force **decelerates** the body, `Vz` going
from -0.488 to -0.067 m/s, approaching rest. The force is not merely reported, it
is fed back into the multibody integrator and changes the trajectory. Rigid BCE
markers moved correspondingly (760 rows per frame, frame 0 and frame 7 differ,
marker z 1.125 to 0.9607) `[live]`.

That is accumulated-force two-way coupling running on GH200 aarch64, which is
precisely the capability the fork went looking for.

**Not reviewed by the physics-skeptic subagent.** The operating protocol asks for
that before finalizing a claim involving a force or a distance. I did not invoke it,
because the standing session instruction is not to call subagents unless asked. The
numbers above are therefore transcribed directly from `FSI_body0.csv` and are
**unreviewed** rather than adversarially checked. They are demo output, not a
project physics claim, so nothing downstream depends on them.

---

## Four corrections to the dispatch, all from primary source

The dispatch was largely accurate on architecture and wrong on provenance in four
places. None changes the GO; all four would waste someone's time later.

**C-1. "There is NO documented case of Chrono ... being built or run on
ARM64/aarch64" is false for Chrono core.** `[source]` Chrono's own `PLATFORMS.md`
states verbatim:

> "Chrono currently includes existing support for 64-bit x86 CPUs and has also been
> known to build on AArch64 and POWER8/9 under Linux."

and lists "AArch64 / GCC 7 and newer" under *Previously Tested Architectures*. The
disclaimer is real and should be quoted with it: "not officially supported", "a
minimum of testing", "no guarantees". The dispatch's claim **is** correct for
Chrono::FSI, whose CUDA modules that document does not cover. Scope the claim to the
GPU modules, do not repeat it about the core.

Corroborating this, and not an afterthought in the build system: `[source]`
`cmake/FindSIMD.cmake:314-359` implements `test_neon_availability()` against
`arm_neon.h` with `-march=armv8-a` and `float64x2_t` intrinsics, and
`src/CMakeLists.txt:164` declares `option(CH_USE_SIMD "Enable use of SIMD if
supported (SSE, AVX, NEON)" ON)`. aarch64 has a first-class SIMD path.

**C-2. `src/chrono_fsi/sph/physics/BceManager.cu` does not exist.** `[source]` That
path 404s on `main`. The file is **`SphBceManager.cu`**. The dispatch warned not to
cite its line number unopened; I opened it. The per-body accumulation is at
`SphBceManager.cu:375-381`:

```
atomicAdd(&body_forces[body_ID].x, sharedForces[0].x);   // :375
...
atomicAdd(&body_torques[body_ID].z, sharedTorques[0].z); // :381
```

and `SphBceManager::Rigid_Forces_Torques()` at `:526` **zeroes** the accumulators at
`:530-531` via `thrust::fill(..., mR3(0))` before launching. The architectural claim
is confirmed; only the filename was stale.

Worth flagging for Dispatch 9: that zeroing is exactly the discipline warpmpm's SDF
path lacks, where per its trap list the engine never zeroes `param.force` and a naive
read returns the run-to-date total.

**C-3. `SCMDeformableTerrain` no longer exists.** `[source]` 404 on `main`; the class
is now **`SCMTerrain`**. `RigidTerrain::AddPatch` is confirmed as described:
`RigidTerrain.h:121` is the Wavefront-mesh overload, documented at `:120` as "The
mesh is specified through a Wavefront file and is used for both contact and
visualization", and `:133` is the heightmap-image overload.

**C-4. The tyre caveat is confirmed, not merely plausible.** `[source]`
`ChTire.cpp:430` calls `terrain.GetHeight(A + voffset)`, commented "terrain height at
query point", and Fiala, TMeasy and Pac02 all reach terrain query paths. Choose the
tyre model accordingly, as the dispatch said.

---

## The risk that the GO does not remove, and it is the one to watch

**Chrono::FSI-SPH is documented as requiring CUDA 12.8 or newer. Vista's newest
module is CUDA 12.6. This build is off-spec and it worked anyway.**

`[source]` The official installation page states verbatim: "The FSI-SPH module
requires CUDA version 12.8 or newer." `[source]` That minimum is **not enforced
anywhere in CMake**: `cmake/ChronoGPUDetect.cmake:73` only prints
`CUDAToolkit_VERSION`, and no `VERSION_LESS` gate on it exists. `[live]` So configure
succeeded, compilation succeeded, and both demos ran correctly on 12.6.20.

Read that precisely. It means the requirement is a documentation statement rather
than a hard gate, and that **the subset of the module exercised by these two demos**
compiles and runs on 12.6. It does **not** mean the whole module surface is safe on
12.6. A future Chrono pull, or a demo touching a newer CCCL or `cuda::` API, can
break with no warning from CMake. Two mitigations, in order of preference:

1. Pin the Chrono SHA. This build is `1b90a9f`. Do not float `main`.
2. If a newer CUDA is ever needed, it must **not** go in Vista `$HOME`, which is
   89.15% full at 20.8 of 23.3 GB `[live]`. Use `$WORK` or `$SCRATCH`.

Two smaller scope notes on what was built `[live]`: `CH_USE_SPH_DOUBLE=OFF`, so the
SPH solver ran in single precision, and `CH_ENABLE_MODULE_FSI_TDPF=OFF`. Splashsurf
was not found, so surface reconstruction is disabled. None blocked the milestone;
all three are choices someone will want to revisit before quantitative work.

---

## What a Chrono arm would give that Dispatch 9's warpmpm arm cannot

The dispatch asks for this scoped comparison on a GO. Two items, and I am
deliberately separating what I verified by execution from what I verified only by
reading source.

**1. Accumulated-force two-way coupling. VERIFIED BY EXECUTION `[live]`.** The
`FSI_body0.csv` table above is the demonstration. Chrono forms a per-body net force
and torque by atomic accumulation, zeroes it per step, exposes it as
`ChFsiInterface::GetFsiBodyForce(i)` / `GetFsiBodyTorque(i)`
`[source: ChFsiInterface.h:114, :118]`, and moves it across an explicitly named
two-way boundary, `ExchangeSolidForces()` and `ExchangeSolidStates()`
`[source: ChFsiInterface.h:179, :184]`.

This bears directly on a standing project limitation. On warpmpm's free-rigid
material-8 path used by the 17 canonical runs, the project's own finding is that the
net force cannot be **decomposed** into hydrodynamic, contact and gravitational
parts. Chrono's `Fx,Fy,Fz,Tx,Ty,Tz` is the fluid reaction specifically, separated by
construction. That is a real capability difference, not a preference.

**2. Actuated drivetrain and OBJ/heightfield terrain ingest. VERIFIED BY SOURCE
READ ONLY, NOT BUILT, NOT RUN.** `Chrono::Vehicle` was **OFF** in this build; the
configure log's "Warning: the Robosimian projects require Chrono::Vehicle!" is the
live confirmation `[live]`. So the actuated-vehicle claim is **not** established by
this dispatch. What is established is that the terrain API exists as described
(C-3 above), which matters because it removes warpmpm's cubic-domain problem. The
size of that problem is quantified in the next section, which also corrects the
figure the dispatch used for it.

**The obvious next step, and it is cheap:** rebuild with
`-DCH_ENABLE_MODULE_VEHICLE=ON` and run a wheeled-vehicle demo. The core build took
94 seconds; this is a small increment, and it converts item 2 from a source read into
a result. I did not do it because it is outside the milestone this dispatch fixed in
advance.

---

## Constraints that bear on scene construction, written for Dispatch 10

Added after D10 relayed a correction and asked what in this build constrains a
scene. D10 is designing against this now, so it is stated as specifically as the
evidence allows and the weak parts are labelled weak.

### First, a correction to the dispatch's own arithmetic, which I re-derived

D10 flagged that the dispatch's `279x` was quoted without saying what resolution
it assumed. That is right, and it is worse than a missing footnote: **the 279x
figure does not contain the cubic penalty at all.** Re-derived here independently
rather than taken on D10's word, from canonical depth 0.2944294473 m and
`depth/dx = 2.000` at g64 (CLAUDE.md L-3):

| Quantity | Value |
|---|---|
| Aspect-ratio waste for 30x12x3, resolution-INDEPENDENT | **25.00x** |
| Forced cube / g96 tank, at **g64** resolution (2.0 cells per depth) | **10x** |
| Forced cube / g96 tank, at **18** cells per depth | **6,973x** |
| The dispatch's **279x** | the **actual 30x12x3 box** at 18 cells per depth, **cubic penalty excluded** |

`246.8e6 / 884736 = 279`, so the dispatch's number is internally consistent, but it
measures the honest road box rather than the cube warpmpm would actually force. The
real forced-cube figure at that resolution is about 25x larger. My own report
inherited this error and it is corrected above.

D10 gets 6,984x where I get 6,973x, a 0.16 percent gap that is just whether cells
per side is rounded to an integer (1834 against 1834.19). Immaterial, recorded so
nobody re-opens it.

**Adopt D10's framing.** The defensible claim is *"road scale is reachable only at
a resolution we have already called a limitation"*, not *"road scale is
impossible"*. At g64 the forced cube is only 10x the g96 tank, which is plainly
reachable; and CLAUDE.md L-3 already calls 2.0 cells per depth a limitation rather
than a converged resolution. Any figure quoted from this family must carry the
resolution it assumes.

### What Chrono changes, and it is larger than removing the cube

**1. The domain is NOT cubic, and not even forced to one aspect ratio.**
`[source]` `ChFsiFluidSystemSPH.h:171` declares
`SetComputationalDomain(const ChAABB& computational_AABB, BoundaryConditions bc_type)`.
An axis-aligned bounding box, not warpmpm's single scalar. `[live]` Confirmed by
this build's own DamBreak run, which reported `boxDims: 14 1.1 32` and
`gridSize: 70 5 160`, a 32:1 ratio between axes. **The 25.00x aspect-ratio waste
factor simply does not exist in Chrono.**

**2. But resolution is still isotropic. Do not over-read item 1.** `[source]`
`initial_spacing` is a single scalar (`ChFsiFluidSystemSPH.h:97`, default 0.01 m,
set via `SetInitialSpacing`). Chrono removes the anisotropic-**extent** penalty and
does **not** grant anisotropic **resolution**. The graded `dxy` / `dz` scheme
Dispatch 10 costed out is still inexpressible, and the timestep still follows the
one spacing. This is the same wall, moved, not demolished.

**3. The real win is that SPH is Lagrangian, so empty domain is free.** A 30x12x3 m
box is 1080 m3, but at canonical depth only 106.0 m3 of it is water. warpmpm pays
for the whole cube; Chrono pays only for markers. Computed, **not measured**, from
`num_bce_layers` default 3 (`:96`):

At spacing 0.036804 m, i.e. **8 markers per depth, four times canonical g64**:

| Component | Markers |
|---|---|
| Fluid | 2.13e6 |
| BCE floor, 3 layers over 30x12 | 7.97e5 |
| BCE side walls, 3 layers | 3.91e4 |
| **Total** | **~2.96e6** |

That is **2.0x the published Chrono fording demo** (~1.5e6 markers), against
**5.42e8 cells** for warpmpm's forced cube at the same spacing, i.e. **183x more**.
A full road-scale scene at 4x the canonical resolution is an ordinary Chrono
problem, not a heroic one.

Caveats, so this is not over-quoted: these are marker counts derived from geometry,
not a run, and marker count is not runtime. Timestep still scales with spacing, so
finer spacing costs steps as well as markers. The neighbour-search binning does span
the AABB (~2.7e6 bins here at ~2x spacing) but that is a cell list where empty bins
are cheap, not a per-cell field solve. **Nothing here has been executed at road
scale and no timing is claimed.**

**4. A trap that looks exactly like the thing D10 wants.** `[source]`
`SetActiveDomain(const ChVector3d& box_dim)` at `:187` is a moving active-region box
and reads like the refinement window that follows a vehicle. Its own doc comment at
`:185-186` says it "should *not* be used for CFD simulations, but rather only when
solving problems using the CRM (continuum representation of granular dynamics) for
terramechanics simulations." **It is not available for the water case.** This is
worth knowing before designing around it, given the Undermind result that no MPM
study follows a vehicle with a refinement window through a large domain.

**5. Terrain ingest, concrete formats.** `[source]` `RigidTerrain::AddPatch` has a
Wavefront-mesh overload (`RigidTerrain.h:121`, doc at `:120`: "The mesh is specified
through a Wavefront file and is used for both contact and visualization") and a
heightmap-image overload (`:133`). The deformable class is **`SCMTerrain`**, not
`SCMDeformableTerrain`. Two things D10 should carry: `ChBodyGeometry::TrimeshShape`
takes an OBJ with a scale and a contact thickness
`[source: demo_FSI-SPH_ObjectDrop.cpp:270]`, which is the ingest path a hull would
use; and the tyre caveat in C-4 applies if a semi-empirical tyre is ever driven over
an arbitrary rigid mesh.

**6. Untested here.** BCE marker spacing against a *rigid mesh's* feature size is
the one thing I cannot answer from this build. `num_bce_layers` is 3 and
`d0_multiplier` is 1.2, so kernel support is 1.2 x spacing; whether a thin feature
such as a wheel arch is resolved or inflated is the Chrono analogue of the warpmpm
SDF band question, and it was not measured. Do not assume it is better behaved just
because the domain is more flexible.

---

## VALIDATION REALITY CHECK

Carried into this report as the dispatch requires, because a GO on a build is the
exact moment someone over-reads it.

**Chrono's fording capability is a physics demonstration and visualisation, not a
benchmark validated against experimental fording data.** The rigorously validated
Chrono off-road work is soil and terramechanics, CRM and SCM, validated against
single-wheel experiments, DEM ground truth, and drawbar-pull and slip-sinkage tests.
This matches the independent finding that NG-NRMM treats SPH fording as a known gap.

**Therefore: adopting Chrono does NOT inherit a validated fording result. It inherits
a validated soil result and a demo-level fluid one.** Any quantitative NG-NRMM
fording error-reduction percentage is UNVERIFIED and must not be cited.

Adding the obvious corollary, since this dispatch is what makes Chrono tempting: a
successful build proves portability and nothing about physical accuracy. Nothing in
this document validates any fording verdict, and the three-buoyancy-number rule
still stands. The 7.3 to 7.7 percent figure is warpmpm SDF-collider only; +0.035
percent is a residual-acceleration identity and not a buoyancy figure at all; and
-105.8 / -39.9 percent are Genesis failures. **No number in this report may be
quoted alongside any of them.** Nothing here was measured against Archimedes.

---

## Recommendation

**Chrono is now a live option rather than a speculative one, and Dispatch 9 is not
blocked either way.** The engine decision stays provisional exactly as the
amendments section says: warpmpm remains the default and Dispatch 9 proceeds.

What changed is that the aarch64 risk, which was the stated reason to doubt Chrono,
is measured and small. It cost 94 seconds of compile time. The remaining reasons to
choose between the two engines are now scientific rather than infrastructural:
whether the fork needs force decomposition and an actuated drivetrain badly enough to
pay for a second engine, against the standing project rule that a second simulator is
not ground truth and validating the pipeline already running beats porting.

Per that rule's own three-part test, a switch needs all of: the current pipeline
structurally cannot represent a decision-dominant effect; the candidate has direct
experimental validation for that exact effect; and it runs on project hardware in
bounded time. This dispatch settles **only the third**. The second is explicitly not
satisfied, per the validation reality check above.

Two things follow that someone should decide, not me:

1. Dispatch 10's road-scale scene design was written against warpmpm's cubic-domain
   constraint. The amendments already say not to rewrite it until this reported.
   This has now reported GO, so that rewrite is unblocked.
2. Whether to spend the small increment to build `Chrono::Vehicle` and close the
   actuated-drivetrain question, which is the one claim in the Chrono case that
   remains unverified by execution.

## Reproducing this

```
scripts/chrono_gh200_fsi_build.sbatch     # configure + build + DamBreak
scripts/chrono_gh200_fsi_verify.sbatch    # motion control + ObjectDrop coupling
```

Both are `gh-dev`, 1 node, and carry their non-obvious gotchas as header comments:
the NVHPC C++17 failure, the missing Eigen, the `nvidia-smi` hardware probe that
silently drops CUDA on a GPU-less host, and the CUDA 12.6-versus-12.8 gap.
Build tree: `$SCRATCH/chrono_eval_2026-08-14/` on Vista. Chrono is built **out of
tree** and is not vendored into this repo, per the dispatch's scope rule.
