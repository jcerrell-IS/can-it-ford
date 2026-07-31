---
name: vista-login-warpmpm-import-hangs
description: "Importing warpmpm on the Vista login node exceeds 240 s (RC=124); do CPU-only geometry work on the Mac by AST-extracting the pure numpy functions from the live vehicle.py"
metadata:
  type: project
---

Measured 2026-07-25 with `/work/11603/jcerrell0629/vista/.venv/bin/python`, running
`from warpmpm.vehicle import load_vehicle` on each node:

| node | wall time | user CPU | sys CPU | result |
|---|---|---|---|---|
| `login1` | 240 s, twice | not captured | not captured | RC=124 |
| `login1` | **600 s** | **0.746 s** | 0.741 s | RC=124 |
| `c642-001` (compute) | **78.9 s** | **5.4 s** | 0.56 s | IMPORT_OK |

**It blocks, it is not merely slow, and the CPU numbers are what prove it.** On login1 the
process consumed 0.75 s of CPU across ten wall-minutes. Filesystem contention would still
accumulate CPU; near-zero CPU with unbounded wall time is a blocking call. On a compute node
the same import does real work (5.4 s CPU) and completes in 79 s, which is itself slow because
torch and warp load off Lustre.

Most likely cause, not yet proven: warp's CUDA initialisation blocking on a driver call on a
login node that has no GPU. Do not re-diagnose this as a PATH, module, or venv problem.

Consequence: the obvious pattern "run `load_vehicle` on the login node to dump geometry, no
GPU needed" does not work at all. Use a compute node, or the Mac path below. Budget 80 s for
the import even on a compute node, so any `timeout` guard around it needs to be generous.

**Working alternative, validated:** copy the live `vehicle.py` down and AST-extract the pure
numpy functions, which have no warp/torch dependency:

    scp vista:/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py /tmp/vehicle_live.py
    # then ast.parse, exec the module-level Assign nodes (for _AXES etc) and the FunctionDefs
    # _up_rotation, euler_zyx, solidify_columns, solidify_watertight into a namespace with numpy

`load_vehicle`'s own orientation block (up-rotation, swap so the long horizontal axis is on y,
scale, centre in x/y with floor at z=0) is about 12 lines and gets replicated alongside. The
Mac env `/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3` has trimesh
4.12.2, numpy 2.5.1, matplotlib 3.11.0, imageio 2.37.3, imageio_ffmpeg 0.6.0.

**Validate the replication before trusting it.** These five must reproduce, and did:
hull volume 3.542739 m3, 655308 faces, `lim` 9.42163 at depth 0.30, h 0.0736065, parity fill
N=8904 giving rho 309.78 at 1100 kg.

**Known non-determinism, do not chase it as a bug:** `mesh.sample(60_000)` at
`vehicle.py:162` is unseeded, and `load_vehicle` derives the oriented mesh's `shift` from that
sample. So the parity fill returns 8904 particles locally and 8905 on Vista from identical
inputs, a 0.01 percent difference. The parity fill itself is deterministic given a mesh; the
mesh's placement is not.

**Why:** two ladder rungs were spent discovering this. **How to apply:** for any CPU-only
geometry question, go straight to the Mac path. Only use a GPU node when the solver is
actually needed. Related: [[solidify-watertight-supersedes-column-fill]].
