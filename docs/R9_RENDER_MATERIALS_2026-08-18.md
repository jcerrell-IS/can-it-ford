# Vehicle and ground materials in the shaded renderer, R9 slot d13-renders

Session opened 2026-08-18 23:39 BST; every measurement below was taken 2026-08-19.
The filename keeps the date this slot's scope was declared under.

Branch `claude/r9-renders`. Files changed: `analysis/render_multigeom_shaded.py` only.
No simulation output, no metric, no verdict, no mesh, no file under `renders/*/sim_*.py`
was touched. `analysis/render_multigeom_rollout.py` is imported and read but not modified.

---

## 0. Summary for someone with two minutes

The water in `render_multigeom_shaded.py` had a real optical treatment (Schlick Fresnel,
Beer-Lambert absorption, GGX specular, all evaluated against an HDRI). The vehicle had one
clamped dot product, and there was **no ground at all**. Both now use the same ingredients
the water already used, in the same file, with the same output transform.

Three renders of the same frame of the same run through the same camera are attached to
the board row. **Every physics number is bit-identical across all three**, which is the
falsifier: if a material change had moved a measured quantity, the renderer would have been
reading something it should not.

Six defects were found on the way, and four of them are the kind that outlive a render:

| # | Defect | Status |
|---|---|---|
| 1 | The renderer could not be run from a clean checkout: `--hdri-cache` was `required=True` and nothing in the repo produced the cache | FIXED |
| 2 | Pointed at any of the 17 gated runs, the hardcoded banner printed a FALSE provenance claim onto the image | FIXED |
| 3 | Water and vehicle were composited in two different colour spaces in one collection | FIXED |
| 4 | Back-facing normals were clamped, driving Schlick to F=1, so half the mesh could render as sky-grey | FIXED |
| 5 | The reconstructed hull has genus ~100. It is closed, but about a hundred tunnels pass through it | REPORTED, not changed |
| 6 | `assets/DaySkyHDRI002A_1K_HDR.exr` ships ungated in a public repo with no licence record | ESCALATED to register B6, not mine |

---

## 1. What the dispatch said, and the one thing in it that was wrong

The dispatch stated that `analysis/render_multigeom_rollout.py` gives the water a Schlick
Fresnel / HDRI / Beer-Lambert / GGX treatment. It does not. A grep of that file for
`fresnel|schlick|ggx|beer|hdri|roughness|specular|F0|smith` returns **zero hits**.

The optics are all in `render_multigeom_shaded.py`. The dispatch was right that `shade()`
sits at `render_multigeom_rollout.py:207` and right about its three lines.

The substantive claim survives by a stronger route than the dispatch used.
`render_multigeom_shaded.py:79` does `import render_multigeom_rollout as RMR`, and the
per-frame draw called `fcol = RMR.shade(base, nrm)`. So inside the one figure that has the
full water treatment, the vehicle was shaded by importing the flat Lambert from the other
file, and both were then pushed into the **same** `Poly3DCollection`.

Second correction: "wire the asphalt PBR set to the ground plane" presumed a ground plane.
There was none. Dry columns are dropped entirely, which is the deliberate D2 fix recorded
in this module's own docstring, so outside the wet footprint the 3D view was blank paper.
This was creating a ground, not re-texturing one.

---

## 2. The vehicle material

Replaced, at `shade_vehicle()`:

```python
sh = np.clip(n @ LIGHT, 0.0, 1.0) * 0.6 + 0.4      # rollout.py:208
return np.clip(sh[:, None] * base, 0.0, 1.0)
```

with diffuse irradiance from the environment along the normal, a Schlick Fresnel term, a
roughness-blurred environment reflection, and a GGX lobe against the HDRI sun, then the
same Reinhard tone map and gamma the water already used.

Nothing here is a new shading model. Every term already existed in this file and was being
applied to one surface only. `ggx_spec()` and `tonemap()` are shared by the water, the
vehicle and the ground **as functions**, so the three cannot drift apart.

Parameters, and where they come from:

| Parameter | Value | Basis |
|---|---|---|
| `F0_DIELECTRIC` | 0.04 | `((1.5-1)/(1.5+1))**2` for n=1.5. Not tuned. |
| `ROUGH_BODY` | 0.22 | clearcoat over paint: glossy, not a mirror. A display choice. |
| `ROUGH_TIRE` | 0.80 | rubber, near-diffuse. A display choice. |
| `SPEC_GAIN` | 0.030 | held **equal to the water's** existing lobe gain, on purpose. |

The tire mask is recovered from the colour `RMR.base_colours()` assigned, not by
re-deriving its geometric test, so the two can never disagree about which face is rubber.
451 of 9000 faces, 5.0 percent.

### 2.1 The defect this exposed, which is worth more than the material

`np.clip(n @ v, 1e-4, 1.0)` on a back-facing normal returns ~0, and Schlick at ndotv=0 is
F=1, which means "pure mirror". Measured on this hull at the default camera:

```
flat n.v  < 0 for 4584 of 9000 faces (50.9%)
Fresnel F > 0.9 for 4941 faces (54.9%), and 77.4% of those are back faces
```

So **more than half the mesh was one clamp away from rendering as sky-grey**, and the first
render after the material change showed exactly that. The old flat-Lambert model concealed
it because its darkest possible output was `0.4*base`, a dark red. An environment-lit model
paints the same leaked faces with the sky.

Fixed by taking the absolute facing ratio `|n.v|`, which is the standard two-sided form.

### 2.2 Smoothed normals, and why that is not cheating

The vehicle is a marching-cubes isosurface of a particle lattice, so its facets are an
artifact of the RECONSTRUCTION, not of the hull. With flat facet normals the Schlick term
swings the full 0.04-to-1.0 range between neighbouring faces. `smooth_face_normals()`
computes area-weighted vertex normals and averages them back onto faces.

The **geometry is untouched**. Every silhouette, the floor contact, and the
particle-enclosure check still see the exact reconstructed surface. Because the body is
rigid, the smoothed normals are computed once in the body frame and rotated per frame, so
the per-frame cost is unchanged.

---

## 3. The ground, and the licence position

`--ground-texture {none,asphalt}`, **default `none`**. With `none` nothing in `assets/` is
read and the ground is a neutral dielectric. With `asphalt` the three Asphalt015 maps are
read: Color as albedo (degamma'd, it is sRGB-encoded), Roughness into the GGX roughness,
NormalGL as a tangent-space normal perturbation.

`--ground-tile-m` defaults to 2.0 and **is a display choice, not a measurement**: the files
carry no physical scale, so it is captioned rather than implied.

### 3.1 The asphalt also feeds the water

`BOTTOM_RGB` was a flat 0.05 grey whose own code comment already read `# wet asphalt`.
`shade_water()` now takes a per-cell bottom albedo, so when the ground is textured the
actual ground albedo is what the Beer-Lambert refraction integrates against. The road
therefore reads continuously from dry, through the shallow margin, into deep water where
absorption removes it. That is the physically coherent way to wire these maps, and it is
why the texture is worth having at all in a scene that is mostly submerged.

### 3.2 Licence: NOT ESTABLISHED, and that is why the flag defaults off

Checked live 2026-08-19:

- No licence or readme file ships in `assets/`.
- No copyright, licence, CC0, ambientCG, author or source string appears in the header of
  any of the four Asphalt015 files, nor in the EXR.
- `git grep -ln "Asphalt015"` over the tracked tree returns **nothing**, and
  `/usr/bin/grep -rn --include='*.py'` over `analysis/ simulation/ scripts/ renders/ data/
  designsafe-staging/` returns **no hits**. The only occurrences anywhere are in `_inbox/`
  and `archive/` session logs from 2026-07-22 and 2026-07-23.

The naming scheme (`Asphalt015_1K-JPG_Color/NormalGL/Roughness`, `DaySkyHDRI002A_1K_HDR`)
matches ambientCG, whose library is CC0. **That is inference from a naming convention, not
proof that these bytes came from there**, so it is not treated as established. The string
is carried in the code as `ASPHALT_LICENCE` and printed whenever the flag is used.

### 3.3 The escalated half, which is not about the asphalt

`assets/DaySkyHDRI002A_1K_HDR.exr` was `required=True` at `render_multigeom_shaded.py:353`,
has produced four committed manifests under `renders/multigeom_2026-08-08_render/`, and
ships in a public repository. `docs/R8_LICENCE_RECONCILE_2026-08-18.md` returns **zero
hits** for `asphalt`, `assets/`, `hdri`, `ambientcg`, `CC0`, `polyhaven` and `texture`
across all eleven of its sections.

So an asset of exactly the class this slot was told to gate is already shipping ungated,
and the audit that was supposed to settle third-party material never looked at the
directory. Recorded as B6 in `docs/R9_DISCREPANCY_REGISTER_2026-08-19.md`. **Nothing was
deleted or moved**: deletion does not unpublish, and this repo has already established that
origin serves removed blobs by SHA.

---

## 4. The four-clause acceptance test

CLAUDE.md, "For any rendered output". Run against `g64_m1100`, 90 frames, 48367 water
particles and 8905 vehicle particles. Each clause reports EVALUATED separately from
pass/fail, because a check that cannot tell "equal" from "could not evaluate" is worse than
no check.

### Clause 1: water reads as one connected fluid body. **PASS**

Connected-component labelling of the wet mask the renderer itself uses:

```
f0   wet cells 1936   components 1   largest 1.0000 of wet
f30  wet cells 1936   components 1   largest 1.0000
f60  wet cells 1932   components 1   largest 1.0000
f89  wet cells 1936   components 1   largest 1.0000
```

### Clause 2: vehicle position matches its known density. **PASS**, and this one is a real test

`realized_rho` is 309.7384 kg/m3 and `mass/solid_volume` reproduces it exactly
(1100.0 / 3.551384). Note this is 0.24 percent from the 310.494 quoted in CLAUDE.md's
anchor list, and it agrees with the 309.78 recorded in the `solidify_watertight` memory.
Not resolved here, flagged.

A body at 310 kg/m3 is less dense than water, so the naive reading is "it should float".
The correct test is whether the buoyancy of the **actually submerged** volume exceeds the
weight. Submerged particle count times h^3, against the 99th-percentile water surface over
the hull footprint:

```
f0    z_surf 0.6785 m   submerged  825/8905   V_sub 0.32902 m3
      buoyancy 3227.7 N  vs weight 10791.0 N   ratio 0.2991  -> predicts RESTS ON FLOOR
f89   z_surf 0.7548 m   submerged 1682/8905   V_sub 0.67079 m3
      buoyancy 6580.5 N  vs weight 10791.0 N   ratio 0.6098  -> predicts RESTS ON FLOOR
```

Observed hull z-min is 0.441643 m against a floor of 0.441644 m, a gap of -9.06e-07 m at
f0. The prediction and the observation agree. **The render showing the car sitting on the
road while partly submerged is what this density requires**, and the buoyancy never gets
closer than 61 percent of weight.

### Clause 3: no particles outside domain or clipped through geometry. **SPLIT**

```
water   particle-frames checked 4,353,030   outside domain 0   PASS
vehicle particle-frames checked   801,450   outside domain 0   PASS
P-2 passthrough_max_frac 0.1067 (limit <0.10)                  FAIL
```

The two absence claims carry their denominators, so a zero here is a measured zero rather
than a check that failed to run.

**The P-2 FAIL is real and is not caused by anything in this slot.** `g64_m1100` is one of
the seven runs CLAUDE.md August 4 audit item 7 already lists as failing P-2. It is printed
on the frame. A render of this run must not be presented as showing clean fluid-solid
separation.

### Clause 4: motion continuous across frames. **PASS**

The naive test flagged: 23 of 89 frames exceed 5x the median step. That threshold is the
wrong instrument for this signal, and the follow-up settles it:

```
largest 8 steps are frames 0..7, CONTIGUOUS, each within 1.13x of its own neighbours
isolated spikes (>5x median AND >4x own neighbours):  0 of 89
lag-1 autocorrelation of the step series:             0.9970
max implied vehicle speed 0.8795 m/s vs prescribed surge 1.5 m/s
```

An autocorrelation of 0.997 and zero isolated spikes is a smooth decaying transient, which
is what a velocity kick followed by frictional deceleration looks like. The median is small
only because the tail is nearly static.

**A third displacement estimator, reported not resolved.** Net centroid displacement over
the record is 0.64266 m. CLAUDE.md item 5 already records two disagreeing measures for this
same run, `summary.json` 0.658537 m against `rollout.npz` 0.637019 m, a 3.4 percent gap. My
number sits between them. This corroborates item 5's instruction to **cite the verdict,
never the displacement magnitude**, and adds nothing beyond that: three estimators, three
answers, spread ~3 percent.

---

## 5. The hull has genus ~100, and this was invisible until now

Measured at three decimation levels, counting edges used by exactly one face:

```
max_faces=9000    faces=9000     verts=4301     euler_chi=-174   boundary_edges=0
max_faces=40000   faces=40000    verts=19798    euler_chi=-188   boundary_edges=0
max_faces=0       faces=251014   verts=125309   euler_chi=-198   boundary_edges=0
```

**Zero boundary edges at every level**: the surface is closed and watertight. But
`chi = -174` means genus ~88, and at full resolution genus ~100. About a hundred **tunnels**
pass through the reconstructed hull, gaps the particle lattice never closed.

This has been true of every frame this renderer has produced. It was invisible because back
faces were drawn and filled the tunnels with the far interior surface. Turning on formally
correct back-face culling makes them see-through and the car reads as broken.

`--cull-backfaces` therefore exists and is **off by default**, which reproduces the previous
appearance. The silhouette, the floor contact and the particle-enclosure check are identical
either way; only the tunnel interiors differ.

Raising the smoothing to close the tunnels was tested and **rejected**:

```
sigma=1.0  genus=100  outside=0   margin_hi=[0.0368 0.0368 0.0367]
sigma=1.6  genus= 84  outside=0   margin_hi=[0.0368 0.0368 0.0327]
sigma=2.0  genus= 49  outside=0   margin_hi=[0.0368 0.0363 0.0230]
sigma=2.5  genus= 29  outside=49  margin_hi=[0.0365 0.0345 -0.0602]   <-- ERODES
```

sigma 2.5 pushes 49 particles outside the surface and drives the z margin negative, which
is exactly the erosion `build_surface()`'s own docstring warns about. sigma 2.0 is clean
numerically but visibly dissolves thin panels, because heavier smoothing pulls the 0.5 level
set inward on thin features. **The default sigma is unchanged at 1.0.**

---

## 6. What these renders do NOT show

Stated here because a render is the most persuasive artifact this project makes and the
least self-checking, and because the poster already carries two false statements under a
heading reading ESTABLISHED.

1. **This is a stationary hull in a tank, not a car fording a road.** The velocity is a
   per-frame Dirichlet clamp on an upstream particle slab plus a one-shot kick
   (August 4 audit item 2). The vehicle does not drive.
2. **No optics are simulated.** warpmpm computes no free surface, no air phase and no
   pressure field (register B7). The water surface is a per-column max-z reconstruction and
   the shading is an analytic display model. These pixels are not a light-transport
   solution.
3. **The foam is a post-hoc diagnostic.** The solver entrained no air. No verdict depends
   on it.
4. **The absorption is exaggerated 9x** (`VIS_GAIN`), a pre-existing display choice, stated
   on the frame.
5. **This run FAILS gate P-2.** Do not use it to argue that water and hull stay separate.
6. **The asphalt is not established as licensed** and is off by default.
7. **The corpus cannot vouch for any of this.** `research_index.py` returns 0 matches for
   `splashsurf`, `Loschner`, `marching cubes`, `visualization` and `rendering`, against 17
   for `free surface`, which is the positive control proving the query path evaluates.
   Those 17 are solver-side MPM free-surface methods, a different question from display
   reconstruction. **The 332-paper corpus has no rendering coverage at all.**

---

## 7. Reproducing the three frames

```
uv venv $S/venv --python 3.11
uv pip install --python $S/venv/bin/python numpy matplotlib scipy scikit-image \
    imageio trimesh fast_simplification OpenEXR

R=analysis/render_multigeom_shaded.py
RUN=renders/yaris_render_s1/_incoming/g64_m1100
COMMON="--frames 60 --hero --width 1700 --height 950 --half 2.7 --elev 20 --max-faces 60000"

python3 $R --run $RUN --outdir before $COMMON --legacy-vehicle-shading
python3 $R --run $RUN --outdir after   $COMMON
python3 $R --run $RUN --outdir asphalt $COMMON --ground-texture asphalt
```

`--hdri-cache` is now optional; the cache is built from the tracked EXR on first use and
defaults to `<outdir>/_hdri_cache`. `fast_simplification` is what `trimesh`'s
`simplify_quadric_decimation` needs; without it decimation is silently skipped and the
surface comes back at 251014 faces.

Falsifier, checked and passing: all three manifests carry
`summary_C2_veh_zmin_rise=-0.007077574729919434`,
`veh_zmin_frame0_m=0.44164325608378013`,
`veh_zmin_min_excursion_below_floor_m=-9.058558408381323e-07`, `P3_pass=True`, identical to
the last digit.

---

## 8. Phase 2, the moving vehicle, not started

d17-moving reports the SDF build is the long pole (~8 min at resolution 32, ~45 min at 64,
cache hits only if the mesh load is seeded), so moving-vehicle rollout data may not arrive.
Phase 1 is complete and standalone regardless.

What phase 2 changes is not the material, it is everything time-dependent. Three things are
already known to need a decision:

1. **Camera.** Tracking the vehicle or holding the channel fixed are different claims. A
   tracking camera hides absolute displacement, which is the measured quantity. Recommend
   **holding the camera fixed** and letting the car traverse the frame, with the tracking
   shot as a separate, labelled output.
2. **Clause 1 gets harder and clause 4 becomes binding.** A wake and a bow wave are exactly
   where a per-column max-z reconstruction fragments into multiple components, and the
   connected-component check above is the instrument that will catch it.
3. **`--half` and the window must not follow the car** if displacement is to stay readable
   against fixed axes.
