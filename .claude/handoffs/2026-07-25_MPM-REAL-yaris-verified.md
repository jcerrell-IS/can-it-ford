# MPM-REAL ACHIEVED, YARIS, 2026-07-25

Job 866214, gh-dev, c642-011, GH200 120GB. Exit code 0. Written by the desktop-app
Claude session with live Vista SSH, every number below read from live stdout or the
live CSV, none from a summary.

## HEADLINE

First render-verified coupled MPM flood simulation with a real car-scale vehicle at
correct mass and correct displaced volume. Supersedes the Jul 13 truck artifact for
every purpose.

  final |d| = 0.09043 m   yaw +1.2506 deg   roll +0.0094 deg   pitch -0.0035 deg
  depth 0.30 m, surge 1.5 m/s, n_grid 64, 90 frames, 1100.0 kg Yaris

Artifacts, Mac, renders/yaris_L2_d0p30_v1p5/:
  flood_vehicle_yaris.mp4   880x616 h264, 45 frames, 6.43 s, 272270 bytes
  metrics.csv               92 rows, 15 cols (6-DOF + linear and angular velocity)
  instrument.npz            per-frame diagnostic dump
  run_866214.log            full stdout
  _frames/                  45 png

## THE BUG THAT WAS BLOCKING THIS

solidify_columns fills every (x,y) column from its lowest to its highest occupied
cell. On a watertight car hull that bridges the ground clearance and the wheel wells
solid. Measured over-fill 2.18x at n_grid=64, buoyancy overstated 1.64x at the
reference depth. It is not a tuning problem: the function cannot converge to ratio
1.0 at ANY resolution, because bridging is what it does by construction.

## THE FIX

New function solidify_watertight(mesh, h) in src/warpmpm/vehicle.py, exact vertical
ray parity. Per grid column, collect every z where the column axis crosses the
surface, sort, fill only between successive entry/exit pairs. Genuine voids stay
empty. Exact for a closed surface, resolution independent, 0.1 s.

Dispatch: VehicleBody gained a `mesh` field carrying the oriented hull. solidify()
uses parity fill when mesh is present and watertight, else falls back to
solidify_columns. load_vehicle() builds the oriented mesh for the trimesh path and
applies the same rotation, scale and shift it applies to the point cloud.

Backup of the pre-patch file: src/warpmpm/vehicle.py.bak_preparity

### Verified, standalone

  n_grid   h_mm        N       vol    ratio      rho
      48  98.14     3846   3.63566   1.0262   302.56
      64  73.61     8904   3.55094   1.0023   309.78
      96  49.07    29807   3.52211   0.9942   312.31
     128  36.80    71154   3.54705   1.0012   310.12

true hull volume 3.54274 m3, target rho 310.49. Realized mass 1100.00 kg at every row.

### Verified, in the live sim

  INSTRUMENT solid_volume=3.55086 m3  hull=3.54274 m3  fill_ratio=1.0023

### Regression, splat shells unaffected

With mesh forced to None the same call returns 19338 particles, ratio 2.1769, which
reproduces F0's measured 2.1763 for solidify_columns. truck_trimmed.ply and any holey
splat still take the column-fill path, as intended.

## GATE CRITERIA, ALL PASS

  C3 total_particle_frames_outside_domain = 0
  C3 global_max_xyz = [8.866 8.808 1.914]  lim = 9.42164   (inside)
  C2 local_depth max = 0.3077 m            (target 0.30)
  C2 veh_z_min rise = 0.000000 m           (no float)
  PASSTHROUGH max_water_frac_in_veh_bbox = 3.71 percent   (no tunneling)

## THREE CORRECTIONS TO THE RECORD

1. `.claude/handoffs/INDEX.md` states "load_vehicle cannot load this .ply at all".
   FALSE. Verified live: watertight True, volume 3.5427, extents
   [4.2826 1.7464 1.518], 655308 faces, load OK. Correct that line.

2. F0's "no n_grid passes the 0.85-1.20 band" is correct ONLY for solidify_columns.
   It measured the function and concluded about the vehicle. The mesh was never the
   problem. Scope that finding to the algorithm.

3. A ratio of 0.954 at n_grid=128 was reported mid-session from a
   binary_fill_holes approach and was WRONG. It was voxel-shell leakage at sparse
   surface sampling. At 6M samples the same method returns ~1.99. Retracted before it
   propagated. Do not cite 0.954.

## PHYSICS READ

Mass ratio Yaris/truck = 38.3x. Displacement ratio = 7.8x (0.0904 vs 0.7073). The
toy-scale artifact overstated motion by nearly an order of magnitude, which is the
concrete reason the Jul 13 mp4 could not carry a poster claim.

Against DRIFT_THRESHOLD = 0.05 m the Yaris exceeds by 1.81x. Note the standing caveat:
that threshold remains uncited and should be presented as a conservative numerical
onset-of-motion detector, not a literature stability criterion.

## ENVIRONMENT DELTA

rtree 1.4.1 installed into /work/11603/jcerrell0629/vista/.venv during diagnosis.
torch 2.11.0+cu128 and warp 1.15.0 verified intact afterward. rtree is NOT required by
the final fix; parity fill is pure numpy. It can be removed if the venv is being kept
minimal.

Vista login-node ffmpeg is broken: libunwind.so.8 missing. Compute nodes have no
ffmpeg at all. mp4 encoding was done on the Mac from pulled frames. Any future render
step should assume this.

## NOT DONE

- Patch is uncommitted in mpm-engine. Also uncommitted there, from another lane:
  the vx/vy/vz/wx/wy/wz CSV columns (preserved, do not clobber).
- Single condition only. No depth/velocity sweep on the corrected geometry.
- Every earlier sweep result on data/track1_sweep_v2 predates this fix and inherits
  both the warped-truck geometry and the 2.18x over-fill. Treat as superseded.
