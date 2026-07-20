# Watertight hull tooling for LS-DYNA coarse FE meshes -> MPM SDF collision geometry

Research note. Historical record: on 2026-07-17 06:07, mesh2sdf produced yaris_sedan_watertight.ply (watertight=True, 1 component, volume 6.8185 m^3). That result is SUPERSEDED and should not be read as the current deliverable. The canonical hull is yaris_coarse_v1l_watertight.ply (3.5427 m^3); the sedan hull must not be used for buoyancy. See the "Canonical hull note" section below for the full comparison and rationale. Sections below are the findings and recommendation.
Date: 2026-07-17 (sedan hull produced), superseded 2026-07-19 by the coarse_v1l hull, header corrected 2026-07-20.

## Source geometry (confirmed by direct inspection)

Four GMU/CCSA LS-DYNA crash FE models (shell-element decks, mm / metric-ton / N units):

- Silverado coarse v3a: 251,400 elements
- Yaris coarse v1l: 378,376 elements (919 *PART entries, 875 *SECTION_SHELL, node coords in mm)
- Silverado detailed v3e: 963,474 elements
- Yaris detailed v2j: 1,519,587 elements (full interior)

Every deck is a complete vehicle: exterior panels PLUS interior parts (seats, IP, firewall,
floorpan, suspension). Shells are zero-thickness surfaces, so none is a watertight solid.
Coarse decks are the better MPM starting point but still need a watertight-hull step.

## Headline finding

SuGaR is the WRONG category of tool. It is a Gaussian-splat-to-mesh reconstructor: its input
is a trained 3D Gaussian Splatting scene, not a mesh. It cannot ingest a .key file or any
mesh. It uses Poisson reconstruction to extract a surface FROM splats. It is not a convex
decomposition tool and not a mesh-repair tool. Ruled out for this task.

The real task (non-watertight FE shell soup -> watertight hull for an SDF) is a mesh-remeshing
problem. The correct family is voxel-remesh to a single watertight manifold, NOT convex
decomposition.

## Why not convex decomposition (CoACD / V-HACD)

Physics, not convenience. Buoyancy and drag integrate submerged displaced volume over the true
outer envelope. Underbody clearance and wheel wells are concavities open to the water. Convex
decomposition fills concavities toward convexity, traps air, overstates displaced volume, and
overstates buoyancy. That biases the ford/no-ford verdict directly.

- V-HACD requires a watertight closed input, so it cannot even ingest the shell soup unrepaired.
- CoACD can ingest non-watertight soup but returns N convex pieces with the same concavity bias.

Convex decomposition is right for contact stability, which is not the bottleneck. The rigid-MPM
coupler consumes a single SDF.

## Recommended tool: mesh2sdf

MIT license, pip install mesh2sdf. Purpose-built for this exact input and output:

- Accepts non-watertight triangle soup.
- Computes unsigned distance field, extracts surface at a small offset via marching cubes
  (guaranteed watertight manifold), then re-signs from the clean surface.
- Outputs BOTH the watertight mesh and the SDF grid.

Critical knob: the level-set offset d. Set d small relative to underbody clearance so panel
cracks close but the real underbody opening stays open (water fills it, buoyancy stays correct).

Alternative: ManifoldPlus (hjwdzh/ManifoldPlus) if a reusable standalone watertight .obj is
wanted first. Same voxel-remesh idea, knob is octree --depth. Caveat: non-commercial license.

## Governing caveat for every voxel-remesh option

The single resolution knob (mesh2sdf offset d, ManifoldPlus --depth, voxel pitch) both closes
spurious zero-thickness panel cracks (good) AND can wrongly bridge the underbody shut if too
coarse (bad, destroys buoyancy accuracy). Set it finer than the smallest genuine opening water
must enter, coarser than the panel cracks to seal. If no single resolution separates those two
length scales, that is the real finding to surface before committing to any tool.

## Engine context (grounded in repo code)

- Genesis: does not require watertight input (internal watertighten wrap + CoACD, SDF via
  igl.signed_distance), but the accurate SDF still wants a clean closed mesh. Produce the hull
  yourself as the safe target. Feed obj/ply/stl.
- kks32/mpm-engine: solidify_columns (FloodScene default) tolerates non-watertight input but is
  the same solidify_columns silhouette/density artifact flagged open in CLAUDE.md. Its true SDF
  collider (build_sdf / add_sdf_collider, winding-number sign) DOES require watertight input. A
  proper watertight hull is exactly what lets solidify_columns be replaced with a real SDF.
  Note: mpm-engine treats .ply as Gaussian-splat data, not a triangle mesh; use .obj/.stl for
  the mesh path.

## Extraction path (for later, not run yet)

- meshio does NOT read LS-DYNA .key (unimplemented since 2019). Do not plan around it.
- Use lsdyna-mesh-reader (PyPI) -> .to_grid() -> PyVista -> .extract_surface().triangulate().
- Do yourself: triangulate quads (each *ELEMENT_SHELL quad -> 2 tris), scale x0.001 (mm->m,
  no reader does this), fix normals (crash-deck shell winding is not consistently outward).
- Gotcha: 919 *PART entries include interior parts. Either select exterior body part IDs, or
  voxel-remesh the whole assembly and keep the outer shell. The voxel-remesh route (mesh2sdf /
  ManifoldPlus) handles this for free: interior parts absorb into the solid, leaving the outer
  envelope.

## Recommended pipeline

deck.key
  -> lsdyna-mesh-reader .to_grid()
  -> PyVista .extract_surface().triangulate()
  -> scale coords x0.001 (mm -> m)
  -> trimesh fix_normals / repair
  -> mesh2sdf (small offset d) -> watertight mesh + SDF grid
  -> feed SDF to the MPM rigid-body coupler

Cross-check the extracted surface once in LS-PrePost before committing.

## Cross-check against existing project references (added after review)

Two existing assets were checked so nothing here is re-derived from scratch.

### car_mesh_rescaled.ply (a SECOND, separate geometry candidate)
- NOT present on the Mac. Only truck_trimmed.ply is local. car_mesh_rescaled.ply lives on
  Vista (per SESSION_STATE.md, Jul 15, verified there by ls/find), alongside car_mesh.ply.
- It is a splat-derived Poisson reconstruction (holey-shell provenance), NOT CAD. Different
  and lower-fidelity source than the LS-DYNA .key decks.
- It is broken: 4.66 x 2.43 x 10.00 m (session note 2026-07-13_phase7_findings.md). X=4.66
  already matches the sedan length in the ref-06 table; Z=10.00 (should be ~1.44) and Y=2.43
  (should be ~1.79) are wrong. Signature of a length-only rescale with a bad/swapped up-axis.
- The render pipeline currently uses truck_trimmed.ply fit to bbox, NOT this file. The
  car_mesh_rescaled axis fix is flagged as needed but has no worked fix documented anywhere
  in mpm-technical-deep-reference (only the general "check scale/orientation" pitfall). It
  needs a scoped decision, not a silent swap. Treat it as a competing geometry source to the
  .key route, not part of it.

### mpm-technical-deep-reference/06_vehicle_physics_and_general_pitfalls.md
Reuse this, do not re-derive unit logic:
- mm -> m scale is x0.001. Ref 06's worked example (scale=0.001 for a mm-authored mesh)
  matches the NCAC .key mm units exactly. Confirmed.
- .key mass units are tonne, but mass comes from ref 06's NHTSA/SAE table, not the deck.
  Caution: table "compact sedan ~1390 kg" is Corolla/Civic; the Yaris is a subcompact
  (~1050 kg), so do not paste 1390 onto a Yaris run. Silverado maps to "light pickup ~2300 kg".
- Also take from ref 06: CG height 0.52 m (do NOT use box center), measured inertia tensor,
  sdf_max_res > 128 for a ~5 m car, grid_density 128/256 + enable_CPIC=True (underbody
  tunneling), non-watertight signing via support_winding_number / sign_winding_number, repair
  via trimesh / PyMeshFix / manifold3d.
- Tension to resolve in the scoped decision: ref 06 line 33 notes Genesis recommends CoACD
  for a concave car body (contact stability), but CoACD fills the underbody concavity and
  biases buoyancy upward (see convex-decomposition section above). For a ford verdict where
  displaced volume matters, the watertight-single-manifold SDF is the correct call; CoACD is
  the fallback only if the coupler is contact-unstable on a raw non-convex SDF.

## Sources

- SuGaR: arXiv:2311.12775, github.com/Anttwo/SuGaR
- CoACD: arXiv:2205.02961, github.com/SarahWeiii/CoACD
- V-HACD: github.com/kmammou/v-hacd
- ManifoldPlus: arXiv:2005.11621, github.com/hjwdzh/ManifoldPlus
- mesh2sdf: github.com/wang-ps/mesh2sdf, pypi.org/project/mesh2sdf
- OpenVDB meshToVolume: openvdb.org/documentation (Apache-2.0, heavier-weight equivalent)
- Genesis internals: DeepWiki Genesis-Embodied-AI/Genesis
- mpm-engine internals: DeepWiki kks32/mpm-engine
- meshio LS-DYNA status: github.com/nschloe/meshio/issues/607
- lsdyna-mesh-reader: akaszynski.github.io/lsdyna-mesh-reader

## Canonical hull note (added 2026-07-19)

Two watertight hulls now exist from the same Yaris coarse v1l deck. Both were produced by
direct *NODE / *ELEMENT_SHELL / *ELEMENT_SOLID card parsing (the compiled
lsdyna_mesh_reader hangs 20+ min on this 42MB / ~378k-element deck, do not retry it)
followed by mesh2sdf. Stats below were verified live on disk on 2026-07-19, not carried
from a summary:

| file | watertight | winding-consistent | volume | bbox (m) | verts / faces | implied density (1100 kg) |
|---|---|---|---|---|---|---|
| yaris_coarse_v1l_watertight.ply | True | True | 3.5427 m^3 | 4.283 x 1.746 x 1.518 | 327,212 / 655,308 | 310.5 kg/m^3 |
| yaris_sedan_watertight.ply | True | True | 6.8185 m^3 | 4.383 x 1.780 x 1.551 | 25,663 / 51,450 | 161.3 kg/m^3 |

CANONICAL: yaris_coarse_v1l_watertight.ply (mesh2sdf 256^3 padded, +17mm offset, underbody
and wheel wells kept open, enclosed volume ~32% of bbox). This is the hull to feed the
SDF collider. Its 2026-07-19 handoff line is in SESSION_STATE.md.

SUPERSEDED: yaris_sedan_watertight.ply (mesh2sdf 128^3, ~+42mm offset, underbody partly
bridged shut, enclosed volume ~62% of bbox). Kept on disk for now (non-destructive, only
977KB), do NOT use it for buoyancy. Retire it only after Panels 1 (VISTA-MPM-WATER) and 2
(VISTA-TRACK1-SDF) confirm they are on the coarse_v1l hull and nothing references the
sedan file.

Density caveat, documented honestly the same way as the Track 1 SUV class (308 kg/m^3):
the canonical hull implies 1100 kg / 3.543 m^3 = 310.5 kg/m^3, just outside this project's
100-300 kg/m^3 soft plausibility band. Not disqualifying. Counterpoint worth stating: the
sedan hull's 161.3 kg/m^3 lands inside the band only because it sealed the underbody shut
(larger enclosed volume), so its in-band figure is the misleading one, not a point in its
favor. Mass is 1100 kg from the deck header (tons/mm/N/sec units), NOT the 1390 kg
Civic/Corolla value.
