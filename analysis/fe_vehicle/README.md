# FE vehicle tooling

Converts CCSA/NCAC LS-DYNA vehicle models into meshes, measures their real mass
properties, and derives simulation inputs from them. Findings and the audit trail:
`docs/FE_VEHICLE_AUDIT_2026-08-25.md`.

**Acknowledgement.** These tools consume finite element models developed by the
Center for Collision Safety and Analysis at George Mason University under contract
with the Federal Highway Administration. CCSA/GMU and FHWA must be acknowledged in
any publication using them. The models themselves are NOT redistributed here; only
code and derived scalar tables are committed.

| script | what it does |
|---|---|
| `nhtsa_key_to_obj.py` | LS-DYNA keyword -> OBJ, one object per `*PART` |
| `nhtsa_mass_properties.py` | mass, CG, inertia tensor by LS-DYNA lumped-mass convention |
| `setfile_mass.py` | `*ELEMENT_MASS_PART` from the companion set file. NOT optional, see audit §2 |
| `measure_vehicle.py` | wheelbase, track, tire diameter, ground clearance |
| `fe_density_profile.py` | height-resolved density profile for the solver's particle cloud |
| `fe_mass_distribution.py` | the z-strata vs 3D-voxel comparison behind that choice |
| `hull_floodfill.py` | watertight hull whose enclosed volume is the flood-fill volume |
| `enclosed_volume.py` | displaced volume vs sealing scale. The uncertainty, not a number |
| `silhouette_area.py` | projected area by orthographic render and pixel count |
| `canitford_fe_render.py` | renders a warpmpm run with the real FE vehicle |

Most run inside Blender, which supplies numpy: neither the system nor homebrew
Python on the reference machine has it.

## Two things that will bite

`_TITLE` keyword variants insert a title line before the data card. Matching bare
keywords skipped 172,574 Rogue elements and under-counted its mass by 15 percent.

`bpy.ops.object.convert(target='MESH')` leaves ONE EMPTY material slot, so
`materials.append` lands at index 1 while every polygon still points at slot 0 and
the object renders as default grey.
