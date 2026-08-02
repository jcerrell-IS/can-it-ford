# Vehicle Physics Reference (NHTSA/SAE, real engineering sources)

Sourced July 8 from cited Perplexity research using real engineering sources (NHTSA Light Vehicle Inertial Parameter Database, SAE 1999-01-1336, manufacturer spec sheets), not aggregators. This data existed in prior research but had not been placed in any skill file before this audit pass — that was a real gap, not a stylistic choice.

## Purpose
For MPM rigid-body seeding across vehicle classes (sedan, SUV, pickup) when moving past the single validated box proxy toward a multi-vehicle sweep.

## Data table

| Class | Example | Mass (kg) | Bounding box L×W×H (m) | CG height (m) | Ixx (roll, kg·m²) | Iyy (pitch, kg·m²) | Izz (yaw, kg·m²) |
|---|---|---|---|---|---|---|---|
| Compact sedan | Corolla/Civic | ~1390 (range 1300-1480) | 4.66 × 1.79 × 1.44 | 0.52 | 365 | 1617 | 1785 |
| Midsize SUV | Highlander/Explorer | ~1990 | 4.96 × 1.93 × 1.75 | 0.70 | 740 | 3561 | 3682 |
| Light pickup | F-150/Tacoma | ~2300 | 5.89 × 2.03 × 1.96 | 0.69 | 839 | 5067 | 5070 |

Inertia tensor source: 1998 Civic measured values (NHTSA database), not estimated from geometry alone. Treat as representative for the compact-sedan class, not that exact model year specifically.

## Physics notes, don't skip these when building the collider

- **Measured CG sits well below bounding-box half-height.** Do NOT default a rigid-body's center of mass to the geometric box center — this overstates the overturning moment under lateral flood drag. Use the CG height column above, not `size[2]/2`.
- **Uniform-density box inertia overestimates Iyy/Izz versus real vehicles**, since real mass concentrates near the floor/center rather than distributing uniformly through the volume. Prefer the measured tensor above when the target model matches one of these three classes; only fall back to a uniform-density box approximation when no measured data exists for the class in question.
- **Box inertia fallback formula**, for classes not covered above: for a uniform rectangular box of mass `m` and dimensions `(a, b, c)` along x, y, z respectively:
  - `Ixx = m*(b² + c²)/12`
  - `Iyy = m*(a² + c²)/12`
  - `Izz = m*(a² + b²)/12`
  This systematically overestimates the real tensor per the note above — use it as an upper bound, not a best estimate, when real data isn't available.

## Mesh-to-SDF technical facts (Genesis v1.2.0, confirmed from source — kept for reference even though the current build target is kks32/mpm-engine, since the underlying physics/scale reasoning still applies)

- `gs.materials.Rigid` SDF defaults: `sdf_cell_size=0.005m`, `sdf_min_res=32`, `sdf_max_res=128`. Raise `sdf_max_res` above 128 for a ~5m car, or features under ~4cm go under-resolved.
- MPM `grid_density` default 64 (`dx≈0.0156m`) causes particle tunneling through car-scale rigid bodies (Genesis issue #600). Fix: `grid_density` 128 or 256.
- `enable_CPIC=True` needed for thin panels/underbody to avoid tunneling.
- Genesis flags raw non-convex SDF contact as unstable; recommends CoACD convex decomposition for a concave car body (issue #444).
- **Unit mismatch is a real, silent failure mode**: `gs.morphs.Mesh` needs `scale=` set explicitly to convert file units to meters. A real example needed `scale=0.001` for a mesh authored in millimeters. A car mesh imported without checking this can silently come out shoebox-sized or building-sized.
- Warp path: watertight mesh → `mesh_query_point_sign_normal`; non-watertight mesh needs `support_winding_number=True` plus `sign_winding_number`.
- Repair tools for a non-watertight mesh: `trimesh` (`is_watertight`/`fill_holes`), `PyMeshFix`, `manifold3d`.

## General misconceptions to guard against when extending to multiple vehicle classes

Generalizing from bugs already found and fixed in this project (unset density → floating body; wrong friction assumption; unstable timestep; silently-zero coupling flag):
- **Assuming a downloaded or reconstructed car mesh is already in the right scale and orientation.** Gsplat reconstructions and downloaded meshes frequently come in arbitrary units or with the wrong up-axis, silently producing a car the size of a shoebox or lying on its side. Always check scale and orientation explicitly before trusting a new mesh.
- **Assuming "a car splat exists" means "a car mesh usable as a rigid body exists."** A trained Gaussian splat is not a mesh. Converting a splat to a usable rigid-body mesh is a distinct step that can silently be skipped if not made explicit.
- **Assuming box-proxy parameter values validated for one vehicle class transfer directly to another.** Mass, CG height, and inertia all scale differently across sedan/SUV/pickup — use the table above per class, don't reuse the sedan's validated numbers for an SUV run.
- **Assuming a solver's internal parameter name means what it sounds like.** Already confirmed the hard way with Genesis SPH's `mu` not being SI viscosity — verify every new parameter name against source code before trusting the name, this applies equally to kks32/mpm-engine.
