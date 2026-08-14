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
(C-3 above), which matters because it removes warpmpm's cubic-domain problem:
Dispatch 10 records that warpmpm's `GridConfig(n_grid, grid_lim)` takes a single
scalar, forcing a cubic domain and a 279x cell-count penalty for a road-scale scene.
Chrono ingesting an OBJ or heightfield as `RigidTerrain` sidesteps that entirely.

**The obvious next step, and it is cheap:** rebuild with
`-DCH_ENABLE_MODULE_VEHICLE=ON` and run a wheeled-vehicle demo. The core build took
94 seconds; this is a small increment, and it converts item 2 from a source read into
a result. I did not do it because it is outside the milestone this dispatch fixed in
advance.

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
