# The Cycles presentation render, R9 slot d13-renders, 2026-08-19

Companion to `docs/R9_RENDER_MATERIALS_2026-08-18.md`, which covers the matplotlib
DIAGNOSTIC renderer. That renderer is kept and is not replaced. This document covers
the second, PRESENTATION path: `analysis/prep_cycles_scene.py` plus
`analysis/cycles_render.py` plus `analysis/cycles_caption.py`.

Everything below was measured on this Mac on 2026-08-19 unless it says otherwise.
Nothing here changed any simulation, any metric, or any verdict. No mesh was added,
moved or re-exported; hulls are READ from where they already live and the exported
copies are scratch render inputs under the session scratchpad, never repository
assets, so register E8 is not engaged.

## 0. Summary for someone with two minutes

Three photoreal frames exist, one per vehicle class, same camera, each stamped with
the solver numbers that would falsify it. The largest single change was not a
material: it was making the water a real reconstructed SURFACE instead of a
per-column heightfield, and then path-tracing it so it refracts.

Four things are worth reading even if you never touch this code:

1. **`pysplashsurf.reconstruct_surface`'s own docstring is wrong about its units**,
   and believing it produces a water surface that is invisible. Section 2.
2. **The as-simulated hull spread is 12.55x, not 155x.** The 155x figure is computed
   from a Silverado hull that no run used. Section 4.
3. **Four separate "the water looks wrong" symptoms were all scene geometry**, not
   materials: a plane through the fluid, a hole cut from the wrong rectangle, a
   zero-thickness surround, and two coplanar surfaces. Section 3.
4. **The Rogue and Silverado hulls are visibly lumpy and the Yaris is not.** That is
   real mesh geometry and photoreal rendering is what exposed it. Section 4.

## 1. Why a second renderer at all

`analysis/render_multigeom_shaded.py` imports `mpl_toolkits.mplot3d.art3d.Poly3DCollection`.
That is a painter's-algorithm polygon plotter: no ray tracing, no refraction, no
shadows, no global illumination, and a per-polygon depth sort that is undefined for
interpenetrating geometry, which is exactly what a hull in water is. Water without
refraction cannot look like water, so no further shading work in that file could
have produced a photographic image.

The split of duties is deliberate:

- **matplotlib stays the instrument.** Its particle-enclosure check, facing-ratio
  measurements and gate captions are what establish that a frame is honest.
- **Cycles is the picture.** It is far more persuasive, which is precisely why every
  frame it makes carries a caption strip naming what is solver output and what is
  invented.

## 2. The finding that generalises: a library docstring that is wrong

`pysplashsurf.reconstruct_surface` documents, verbatim in the installed build:

> Note that all parameters use absolute distance units and are not relative to the
> particle radius.

**That is false for `smoothing_length` and `cube_size`.** They are read as MULTIPLES
of the particle radius, the same convention its sibling `reconstruction_pipeline`
documents explicitly. Held-fixed measurement, one frame, 3779 particles of median
spacing 0.0404 m, `particle_radius` 0.04566 m, every other argument identical:

| what was passed | connected bodies | enclosed volume |
| --- | ---: | ---: |
| `smoothing_length=2.0*r, cube_size=0.75*r` (absolute, per the docstring) | 3779 | 0.0002 m3 |
| `smoothing_length=2.0, cube_size=0.75` (relative) | **6** | **1.4570 m3** |

3779 bodies for 3779 particles is one blob per particle. Passing absolute units
shrinks the kernel support by a factor of the radius, here to roughly 8 mm against a
40 mm particle spacing, so no particle ever reaches a neighbour and the fluid never
becomes a fluid. In the render this reads as "the water is invisible", which sends
you looking at the water MATERIAL. It is not a material bug.

**Why this survived the obvious checks.** The fragmented mesh passes everything cheap:
`trimesh.is_watertight` is True, it is edge-manifold, its bounding box matches the
particle cloud exactly, and it has ten times MORE triangles than the correct mesh.
Only the enclosed volume separates it from a real free surface. So `water_surface()`
now computes that volume on every export and refuses to write a surface outside
`[0.5, 1.6]` of the volume the particles carry, and refuses one whose body count
exceeds 2 percent of the particle count.

A second, smaller correction in the same place: the particle radius must carry the
particle's VOLUME. warpmpm seeds one water particle per `h^3` (measured: 48367
particles times `h^3` is 19.29 m3 against a slab of 8.30 x 8.31 x 0.294 m), so the
equivalent sphere radius is `(3 h^3 / 4 pi)^(1/3) = 0.6204 h`, not the `0.5 h` the
draft used, which understated each particle's volume by 47 percent.

**A check worth keeping.** The reconstructed free surface away from the vehicle sits
0.2950 m above the floor, against the run's own `realized_depth_m` of 0.2944 m. That
is 0.2 percent, reached through splashsurf and a column-maxima statistic rather than
by reading the summary field, so it is an independent confirmation that the
reconstruction reproduces the solver's water depth.

## 3. Four "material" symptoms that were all geometry

Recorded in order because each one looked like a shading problem and cost an
iteration. This is the same lesson `256d013` taught in the matplotlib renderer: a
scene-construction bug follows you into the path tracer and disguises itself.

1. **A flat surround plane cut through the fluid.** A full plane at the water level
   passes through the reconstructed volume and puts a spurious flat refracting
   interface inside it, which renders as a glass shelf slicing the bow wave. Fixed by
   making the surround an annulus with a hole.
2. **The hole was cut from the mesh bounding box.** That box is set by whichever
   splash droplet flew furthest, so a ring of bare road showed between the two
   surfaces. Fixed by cutting the hole at the exact rectangle `prep` clipped to.
3. **The surround had no thickness.** A zero-thickness sheet has no volume for
   Beer-Lambert to act over, so the simulated patch attenuated light through 0.3 m of
   water and the surround did not. The boundary stayed legible as a change of colour
   at matched height. Fixed by making the surround a closed frame-shaped SLAB with
   the identical water material.
4. **The road was exactly coplanar with the water's floor.** The reconstructed water
   is a closed volume whose bottom face lies on the floor plane, so a road at the same
   z gives Cycles two surfaces at identical depth. The road now sits 3 mm lower, which
   is 2 percent of one grid cell.

There was also a raised **bead** running round the patch: splashsurf closes the
isosurface where the particles stop, and that closing surface curls up a few
centimetres proud of the free surface. Against a flat surround it reads as a
rectangular plateau with a lip. `clip_to_rect()` cuts it off, dropping faces whole so
no vertex is moved and no water is invented, then re-closes the mesh with a vertical
skirt to the floor so the volume stays closed and the absorption cannot leak.

**Diagnostic that settled it.** Rather than keep guessing at the surround, its
absorption colour was temporarily set to pure red and the scene re-rendered. The red
appeared only in the surround ring and nowhere else, which proved the slab geometry
and its volume orientation were correct and moved the search elsewhere.

**One height error, stated because it recurred in two forms.** The surround must meet
the patch at the right height, and two cheaper answers are both wrong. The median z of
the reconstructed mesh mixes the top surface with the bottom, since the mesh is a
closed volume resting on the floor: that returned 0.4879 m against a true surface at
0.7366 m. And the particle-field free surface is not the mesh height either, because
the isosurface sits above the topmost particle centre, measured here at +0.0920 m for
the Yaris, +0.0593 m for the Rogue and +0.0448 m for the Silverado, so it is not a
fixed multiple of the radius and must be measured per run.

## 4. The hulls, and a correction to the dispatch

Vertex counts read directly from PLY headers. Which hull each run used was read from
its own `summary.json` `hull_source` field, not assumed.

| vehicle | hull the RUN used | vertices | hull used for RENDERING | vertices |
| --- | --- | ---: | --- | ---: |
| Yaris | `yaris_coarse_v1l_watertight.ply` | 327,212 | same | 327,212 |
| Rogue | `rogue_g96_pd8_coarse_watertight.ply` | 36,074 | `rogue_coarse_watertight.ply` | 66,987 |
| Silverado | `silverado_g96_pd8_coarse_watertight.ply` | 26,072 | `silverado_coarse_watertight.ply` | 48,706 |

**The as-simulated spread is 327,212 / 26,072 = 12.55x. The render spread is
327,212 / 48,706 = 6.72x.**

**The 155x figure should not be repeated as the as-simulated spread.** It comes from
`silverado_g32_pd8_dq0.02_coarse_watertight.ply` at 2,108 vertices. A live search of
tracked `*.py` outside `.claude/worktrees/` finds it in exactly ONE file,
`analysis/preflight_hull_guard.py` (2 lines), which is a guard rather than a
designation, while `silverado_g96_pd8_coarse_watertight.ply` appears in 4 files
(5 lines). No multigeom run used the 2,108-vertex file.

A NOTE ON THAT COUNT, because the first version of this paragraph got it wrong. It
said "named 85 times", which came from a `grep -rhn -oE` whose `-n` prefixed a line
number onto each `-o` match, so `uniq -c` was counting the string "27:silverado_..."
rather than counting files. The corrected figures above come from separate `grep -rl`
and `grep -rc` passes. The conclusion is unchanged and the number was wrong by more
than an order of magnitude, which is the argument for re-measuring anything that will
be quoted. The 155x figure currently appears in
`.claude/skills/research-corpus/SKILL.md` annotated `<-- 155x coarser`; that is the
line to fix, and it is not mine to edit.

**Mesh QUALITY differs more than vertex count suggests, and this is the honest
limitation.** The Yaris hull is smooth. The Rogue and Silverado hulls are visibly
lumpy at photoreal quality: their surfaces carry Poisson-reconstruction noise.

This was tested rather than asserted. Same run, same camera, same materials, only the
hull swapped: `rogue_coarse_watertight.ply` (66,987) against the run's own
`rogue_g96_pd8_coarse_watertight.ply` (36,074). **Both are lumpy**, so the noise is a
property of the Rogue mesh family and not an artefact of choosing the higher-vertex
render hull. The higher-vertex hull is still the better of the two.

Rendering at higher fidelity than the sim ran is normal, and the caption strip on
every frame says so explicitly, along with the vertex count and the source filename,
so a reader comparing the three frames cannot mistake a mesh-provenance difference for
a physics difference.

## 5. What is physics and what is appearance

**Physics, from the solver, unmodified**: every water particle position, the rigid-body
pose, the floor plane, and every number in the caption strip. The water surface is a
splashsurf reconstruction of those real particle positions and nothing else.

**Appearance, invented in the renderer, carrying no data**: all of the optics; the
paint / glazing / tyre split, which is a geometric partition of a single closed shell
and is not claimed to identify real parts; the procedural ripples on the surround; and
the flat water beyond the solver domain. warpmpm computes no optics of any kind.

**Not modelled, stated so nobody reads it into the image**: the hull is one closed
watertight shell with no separate window, wheel, trim or light geometry. There is no
cabin behind the glazing because there is no glazing, and no refraction happens through
it. Following the note from the coordinator on d17-moving's hull: there are no wheels,
no suspension and no rolling degree of freedom, and nothing in these frames should be
read as drivetrain behaviour. The wheels do not turn and are not depicted turning.

**Where effort was deliberately NOT spent.** The literature review supplied this round
reports that air entrainment, spray, surface tension and turbulence closure are not
shown to change a flood-vehicle stability verdict, whereas road friction and vehicle
watertightness are. Effort therefore went into the free surface reading as one
connected body and into real refraction, and no spray or foam was added to these
frames. The matplotlib renderer's Weber-number foam field is a post-hoc diagnostic and
is not carried over here.

## 6. The asphalt maps: a gap, not dead weight

`assets/Asphalt015_1K-JPG_Color.jpg`, `_NormalGL.jpg` and `_Roughness.jpg` are tracked
and, on `origin/main`, referenced by nothing but the dispatch prompt files themselves,
confirmed with `/usr/bin/grep -rn` naming `renders/` and `data/` explicitly. They are
now wired to the ground through `--ground-texture asphalt` in the shaded renderer and
`--asphalt-dir` here, and a frame rendered with them is attached to this round's
output, so they are demonstrably usable: **a gap, not dead weight.**

**RESOLVED 2026-08-19: they are now ON by default.** They were behind a flag and
defaulted OFF while their licence was unestablished, because no licence file ships in
`assets/` and no copyright or source string appears in any of the four file headers.
Josie confirmed by email on 2026-08-19 that licence permission is granted for these and
for `assets/DaySkyHDRI002A_1K_HDR.exr`, so both are used without hedging and the frames
may be published.

Two things did NOT change with that answer, and both are worth keeping straight. The
provenance gap in the files themselves is untouched: the maps still carry no embedded
licence or source string, so the permission rests on the owner's word rather than on
anything recoverable from the assets. And the flag is retained, so a caller who needs a
texture-free render can still have one. A permission question was answered by the
person entitled to answer it; a provenance question was not answered at all.

## 7. Reproducing the three frames

```
uv run --with numpy --with scipy --with trimesh --with matplotlib --with pysplashsurf \
  python3 analysis/prep_cycles_scene.py \
  --run render_s2/multigeom_2026-08-08/g64_yaris_regression --frame 60 \
  --hull vehicle_geometry_research/yaris_coarse_v1l_watertight.ply \
  --outdir <scratch>/scene_yaris --half 4.2

blender --background --python analysis/cycles_render.py -- \
  --scene <scratch>/scene_yaris --out <scratch>/final_yaris.png \
  --hdri assets/DaySkyHDRI002A_1K_HDR.exr --far-water \
  --samples 320 --res 1600 --res-y 1000 \
  --cam-elev 5.0 --cam-azim 137 --cam-dist 12.40 --lens 78

uv run --with pillow python3 analysis/cycles_caption.py \
  --scene <scratch>/scene_yaris --image <scratch>/final_yaris.png \
  --out <scratch>/canitford_yaris_cycles.png --hull-verts 327212 --title "..."
```

Blender is 5.2.0 LTS at `/opt/homebrew/bin/blender`, and its bundled Python is 3.13.13
with numpy 2.3.4, so the render half needs no `uv` environment. Cycles runs on Metal;
a 1600x1000 frame at 320 samples takes well under a minute.

Camera distance is scaled per vehicle at 2.88 times the hull's own long-axis extent
(Yaris 12.40 m, Rogue 13.70 m, Silverado 17.15 m) so the three are framed comparably.
Elevation, azimuth and focal length are identical across all three. The distances are
printed rather than hidden precisely because "same camera" would otherwise be a claim
nobody could check.

`pysplashsurf` installs and imports on arm64 macOS. Verified by live install this
session; `reconstruct_surface`, `reconstruction_pipeline` and `marching_cubes` are all
present. Any claim that it excludes aarch64 is refuted.

## 8. What is still wrong with these frames

Written up the same way it would be if it confirmed something.

1. **The patch boundary is still faintly visible** in some framings as a change in
   surface texture, because the simulated water is genuinely rougher than the smooth
   procedural surround. That contrast is physically correct near an obstruction; the
   sharp rectangular transition is not. The delivered camera azimuth was chosen so the
   boundary falls behind the vehicle, which is a mitigation and not a fix.
2. **The glazing band stair-steps** along triangle edges, because the paint / glazing
   split is a per-face geometric partition of an unlabelled shell.
3. **The surround is an extrapolation.** The solver domain is finite; beyond it there
   is no water field, and the flat slab out to 240 m is invention. Nothing may be
   measured off it.
4. **The three patches read as three separate ponds** in the composite, because each
   run's water is agitated across its whole tank while the presentational surround is
   calm. Section 9.

## 9. The composite: three classes on one crowned road

`analysis/cycles_road_scene.py` puts all three vehicles in one image.

**They were never in one simulation, and the caption strip says so first.** There is no
three-vehicle run. Each vehicle comes from its own warpmpm run and brings its own water
with it. What the composer applies is a RIGID TRANSLATION, the same translation to the
hull and to its water, so every distance, depth and angle inside a patch is preserved
and the waterline on each vehicle is exactly what its solver produced. The arrangement
along the road and the flat water between the patches are invented and are labelled.

**The road is the project's own geometry.** `simulation.road_geometry.road_profile` is
IMPORTED, not reimplemented, so the picture cannot drift from the cross-section
`sim_road.py` would hand the solver: crown, 2 percent cross slope, gutters, kerb,
verges. Per the literature sweep supplied this round, no retrieved study quantifies a
crowned or cambered road against a flat plane, so this is an unevaluated configuration
rather than a settled one.

**The one honest mismatch.** The runs used a FLAT floor and the road is crowned. Each
patch is seated so its floor sits on the CROWN, which keeps the depth over the crown
exactly the depth the run simulated (0.203, 0.265 and 0.235 m) and keeps the vehicle
standing on the road rather than buried in it. Away from the crown the road falls, so
the water is deeper toward the channel than the run simulated, up to 0.124 m. That is
the direction a real crowned road goes, but it is an artefact of seating a flat-floor
run on a crowned road and no depth may be read off it.

Two composer bugs worth recording, both caught by their own printed numbers:

- **Seating each patch at the lowest road point under its OWN footprint spread the
  three water surfaces by 0.0995 m**, of which only 0.062 m is the real difference in
  simulated depth. The rest was an artefact of patch WIDTH: the Silverado's patch is
  8.11 m and reaches into the gutter, the Yaris's is 6.42 m and does not. A single
  common seating height removes the artefact and leaves exactly the difference the runs
  actually have.
- **Seating on that lowest point buried every vehicle 0.124 m into the road**, because
  the hull's underside rests on its own flat floor. Seating on the crown fixes it, at
  the cost of the water's flat bottom then sitting above the falling road; the bottom
  face alone is pushed down until the opaque road occludes it, which adds no optical
  path because nothing below the road surface is visible.

**Three attempts at the surround mesh, and the last two failures were mine.** The
surround is one slab with a hole per patch. v1 emitted each tile as its own closed box,
so abutting boxes gave doubled coincident interfaces and rendered as black trenches.
v2 raised walls only on real boundaries, which is right, but left T-JUNCTIONS where a
full-width strip meets the shorter tiles beside a patch: the shell was then not closed,
the volume leaked, and a flat white band ran straight across the frame. v3 tiles the
whole sheet on a GLOBAL grid built from the union of every patch's x and y boundaries,
splits the walls on that same grid, welds coincident vertices, and asserts the result is
manifold. It now prints `surround shell: 29 cells, closed and manifold`, and that
assertion is the thing to keep: both failures looked like lighting and were meshing.

**What is still visible.** The patches read as rectangles because each run's water is
agitated across its whole tank while the surround is calm, and at a grazing camera angle
the Fresnel reflectance of water exceeds 0.8, so calm water mirrors the bright sky and
disturbed water reflects the dark treeline instead. That contrast is real optics, which
is why it survived three geometry fixes; only the sharp rectangular transition is
artificial. Raising the camera reduces it, and the surround was given a matching slope
distribution, but it is not eliminated. The honest fix is a run whose domain is larger
than the frame, not a renderer change.

## 10. What a reader may and may not take from these images

MAY: the waterline on each vehicle, which is that run's own; the free-surface shape
around each hull, which is a reconstruction of real particles; the relative sizes of the
three vehicles; the depth over the crown, which matches each run's realized depth.

MAY NOT: any depth read off the crowned road away from the crown; anything at all from
the flat water beyond the patches; any inference that the three vehicles experienced one
flood; any drivetrain, wheel-rotation or suspension behaviour, none of which the
simulation has; and any optical quantity, since warpmpm computes no optics.
