# Failed vehicle reconstructions, archived 2026-07-25

**Do not use either of these for simulation.** They are kept only so the failure
is documented and nobody re-derives it. The single usable vehicle asset remains
`vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`, per
`docs/VERIFIED_FACTS_LEDGER_july24.md` Section F.

Recovered from the session scratchpad (`/private/tmp/...`) before it was lost.

## Measurements, taken live 2026-07-25 with trimesh

| file | verts | faces | watertight | extents x, y, z (m) | volume (m3) |
|---|---|---|---|---|---|
| `car_mesh.ply` | 31574 | 63180 | True | 0.3331, 0.1738, 0.7147 | 0.017291 |
| `car_mesh_rescaled.ply` | 31574 | 63180 | True | 4.6600, 2.4307, 9.9981 | 47.327822 |
| **canonical, for contrast** | | | | | |
| `../yaris_coarse_v1l_watertight.ply` | 327212 | 655308 | True | 4.2826, 1.7464, 1.5180 | 3.542739 |

## What went wrong

**`car_mesh.ply`** is a collapsed reconstruction. It is watertight, which is why
it can pass a naive geometry check, but it is not car-shaped: its tallest axis
(0.7147 m) is more than twice its longest horizontal axis (0.3331 m). A real
sedan is roughly 4.3 long by 1.75 wide by 1.5 tall. This is nothing like that at
any scale. Enclosed volume is 0.017 m3, about 0.5% of the canonical mesh.

**`car_mesh_rescaled.ply`** is the same mesh, identical vertex and face counts,
scaled uniformly by 13.9887 (verified: 4.6600/0.3331 = 2.4307/0.1738 =
9.9981/0.7147 = 13.9887). The rescale targeted 10 m on the **maximum extent**,
but the maximum extent of this mesh is Z, its height. The result is a 10 m tall
object. The rescale did not fix the reconstruction, it only made the wrong axis
large, and it multiplied the volume error: 47.3 m3 against a true 3.54 m3.

The lesson worth keeping: **a watertight check does not validate a
reconstruction.** Both of these are watertight. Aspect ratio against known
vehicle dimensions is what catches this, and it should be gated before any mesh
is accepted, not after a rescale.

Neither file has ever been used in a simulation run recorded in this repo.
