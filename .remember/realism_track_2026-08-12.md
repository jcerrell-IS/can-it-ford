# Realism track, worktree can-it-ford-realism, branch realism-exploration

## 21:07 | realism-exploration
Read docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md (280 lines) and
docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md (410 lines) in full. Hard
constraint confirmed at assessment section 1: inertia_kg_m2 is a box fallback
reproducing exactly from box_inertia(1100, 4.30, 1.70, 1.47), and the scene's
long axis is Y (measured extents 1.7078, 4.2014, 1.4853), so a naive wire is
Ixx -69.2 pct / Iyy +379.2 pct. Not wiring it. Open: which route, warpmpm or
Genesis.

## 21:20 | realism-exploration
[READ] Traced the material-8 defect to its exact line. mpm_utils.py:1411-1412
accumulates rigid_linear_mom by atomic_add of v_interp*mass_p, and
mpm_utils.py:1434 sets v_cm_new = rigid_linear_mom[b] / M. That is an OVERWRITE
of body velocity by the mass-weighted grid velocity, not v_old + F*dt/M. No
force term exists. Register A3 is correct for this path. Open: whether any
other path in the same engine forms a force.

## 21:28 | realism-exploration
[READ] It does. mpm_solver_warp.py:2732-2736 (add_sdf_collider's collide
kernel) computes impulse = m*(v_free - v_new) and atomic_adds it into
param.force and cross(rel, impulse) into param.torque, then writes the
constrained node velocity back. Exposed on the wrapper at core/solver.py:354
sdf_wrench (force = accumulated impulse / dt), :348 reset_sdf_force, :339
set_sdf_pose. Sign convention documented at core/solver.py:302-313: a static
cup holding m kg reads (0,0,-m*g), so a submerged body reads buoyancy as
POSITIVE z. Units check: kg*(m/s)/s = N, and rel x impulse / dt = N*m. This is
the force accessor the task asks to be designed, already built and already
validated to 7.3-7.7 pct against analytic buoyancy (register A-2, job 894731).
Open: is anything feeding that wrench back into the pose.

## 21:33 | realism-exploration
[READ] Nothing is. Both pose integrators are kinematic-only: the SDF modify
closure at mpm_solver_warp.py:2740-2760 does center += dt*velocity and rotates
the quat by a PRESCRIBED omega, and _integrate_cdf_poses at :3107-3148 does the
same for CDF lanes. Neither reads param.force. So the gap between the current
engine and a real force-coupled body is the feedback loop only, not a kernel.
Also [READ]: param.force is never zeroed by the engine on the SDF path (the
only reset is reset_cdf_wrench at :3153, which targets different arrays), so it
accumulates monotonically from creation and the caller must reset it per
measurement window. Open: route decision.

## 21:40 | realism-exploration
[READ] External retrieval. No open-source implementation of Qian 2022 or Zhang
2026 located; the Zhang paper resolves (CMAME, ScienceDirect S0045782525007005,
HKUST repository 1783.1-166298) but no public code repository was found in the
search results. GNN report read
(~/Downloads/GNN Surrogates for Fluid-Rigid Coupling...md, 84 lines): GNN
surrogates are NOT demonstrated for a freely-moving rigid body two-way coupled
to fluid, by Kumar's group or anyone the report located; every published
speedup (300x to 5000x) is granular-only or fixed-obstacle, and NeurIPS 2025
ML4PS #111 states verbatim that unmounted rigid bodies remain underutilized.
So the GNN surrogate is not a faster route to visual realism here. NOT FOUND on
disk: License_Analysis_of_the_Three_PhysGaussian_Repositories.md, searched to
depth 5 across /Users/josie. Moot for the proposed route, which touches no
PhysGaussian code. Open: route confirmation.

## 21:50 | realism-exploration
[READ] Environment. warpmpm, warp and trimesh are all absent on the Mac
(ModuleNotFoundError), so every coupled run is Vista-side; the canonical hull
PLY is present locally at 12.4 MB. Live squeue: job 906873 RUNNING on c642-031
(the other track's node, 15:07 elapsed) and job 906882 PENDING with reason
QOSMaxJobsPerUserLimit, so the second idev CANNOT start while the first holds
the limit. No node is available to this track. Proposing batch submission via
scripts/tacc_submit.sh instead, which is the sanctioned route anyway (idev
burned 99.1 pct of SUs historically). Open: route confirmation and compute
path, both put to the user before any simulation code is written.

## 22:00 | realism-exploration
User confirmed: my judgement on route, and authorised the live node c642-031
despite it belonging to the other track. Taking the dynamic-SDF-collider route.
Confining all writes to this worktree and to $WORK/realism_track_2026-08-12/ so
nothing the other track owns is touched. Open: environment on the node.

## 22:10 | realism-exploration
[READ] Environment resolved on c642-031: GH200 120GB idle (0 MiB used), python
at $WORK/mpm-engine/.venv/bin/python (3.12.13, warp 1.14.0), warpmpm reached via
PYTHONPATH=$WORK/mpm-engine/src. Default python3 has neither. No trimesh
anywhere. build_sdf signature confirmed: (verts, faces, res=64, margin_cells=4.0,
interior_probe=None). Open: cost of building an SDF from the 655k-face hull.

## 22:15 | realism-exploration
[READ] BLOCKER on the hull, and it changed the prototype's geometry. build_sdf
signs its field with a generalized winding number over every grid point against
every face (mesh_sdf.py:328-366, _winding_number at :205), pure numpy. At res=64
that is 262,144 * 655,308 = 1.7e11 solid-angle evaluations and it will not
finish. The distance half is cheap (scipy cKDTree over surface samples,
mesh_sdf.py:309-322) so only the SIGN is the problem. Decided: prove the
coupling on the 12-face cube, which is the same geometry the C1-SDF validation
used to establish 7.3-7.7 pct force accuracy, and treat the hull SDF as a
separable mesh-decimation problem. Two routes recorded for it, neither run:
vertex-clustering decimation to ~1e4 faces, or replace the winding-number sign
with an occupancy test against the pipeline's own solidified particle cloud.

## 22:32 | realism-exploration
Wrote simulation/realism/dynamic_body.py (DynamicSDFBody, installs into
sim.modify_bc[handle], the per-substep hook the engine calls at
mpm_solver_warp.py:1333 right after the collide kernel at :1320) and
simulation/realism/proto_float.py (Archimedes float test). Works in impulse
units directly, dv = J/M + g*dt, so no dt round-trip. Zeroes param.force every
substep because the engine never does. added_mass defaults to 0.0, i.e.
unmodified physics, deliberately not tuned. Falsifiable target: a cube at
rho_b = 310.494 must settle at draft/L = rho_b/rho_w = 0.310494, started at 0.60
so buoyancy has to lift it. Copied to Vista, smoke test running. Open: does it
run, and does it move toward the target.

## 22:50 | realism-exploration
Smoke run completed on c642-031, n_grid=24 / 6 frames / 2 settle frames, 14,080
water particles. PROTOTYPE RUNS AND DOES NOT DIVERGE. The loop closes: the
wrench is read, the body integrates, the pose feeds back, and the body MOVES in
response to force, draft/L 0.6025 -> 0.5900 against a target of 0.310494, i.e.
toward the target. moved_toward_target true, diverged false. Quantitative
Archimedes agreement is NOT established and must not be claimed: 6 frames is
0.1 s of sim time and the cube spans only 7.2 cells at this n_grid.
TWO DEFECTS FOUND BY READING THE WRENCH, both mine, not the engine's.
(a) The settle wrench read [-15.01, -15.01, -30.89] N against an analytic
    buoyancy of +158.9 N at that draft. The z sign is a startup transient: after
    only 2 settle frames (0.033 s) the water lattice has no hydrostatic pressure
    yet, so what the cube feels is water still falling onto it, not buoyancy.
    Fixed by settling 60 frames before release, not by touching the physics.
(b) The equal -15 N on BOTH lateral axes was a real geometry bug in my scene:
    floor() truncation in the lattice made the water centre 0.4948 against a
    cube at 0.5000. Fixed by centring the lattice on the domain axis. This is
    exactly the kind of thing the wrench accessor makes visible and the
    material-8 path cannot, since it forms no force to read.
Launched the settled run (n_grid=48, 60 settle frames, 300 frames, pid 4100661,
$WORK/realism_track_2026-08-12/float_g48.log -> float_g48.json). Open: the
quantitative draft number; the hull SDF decimation; open-channel BCs; render.

## 23:05 | realism-exploration
Settled g48 run with the MEASURED free surface. THIS IS THE RESULT.
settle wrench F = [+0.195, +0.195, +142.55] N against analytic 158.92 N at that
draft, i.e. -10.3 pct on the static force, and the lateral components fell from
-15.01 N to +0.195 N, a 77x improvement, confirming the lattice-centring fix.
settled draft/L = 0.29462 against the Archimedes target 0.310494, -5.11 pct.
Started at 0.600. No divergence. The earlier 41 pct error was mine: I measured
draft against the hardcoded fill height, which the initial carve invalidates.
Mesh on Vista verified byte-identical to the canonical hull by SHA256
b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95, not by path.

## 23:15 | realism-exploration
RETRACTION, and it is mine. I inferred from leaks_start 15,720 of 239,800 that
the run was losing about 5 percent of its water, and warned that this was the
same order as the 5.11 pct agreement. That inference is WRONG. The lattice is
80 x 80 x 40 = 256,000 particles and its outer shell is 256,000 - 78*78*39 =
18,724. A count of 15,657 is 84 pct of that shell, so the metric was counting
BOUNDARY-LAYER particles sitting a hair outside a plane whose grid node is still
constrained, which is normal MPM behaviour, not escapes. No mass loss was ever
demonstrated. Do not repeat the mass-loss claim.
Consequence for the projection run: n_projected_total = 3,585,787 over 400
frames is about 8,964 per frame, i.e. roughly 3.7 pct of all particles clamped
EVERY frame. The projection is a continuous wall intervention, not a rare
rescue, so it is the MORE perturbed arm, not the cleaner one. Its result is
draft/L 0.32687, +5.27 pct.
BEST HONEST STATEMENT: the two treatments BRACKET the Archimedes target from
opposite sides, -5.11 pct and +5.27 pct, so the coupling reproduces the
equilibrium draft to within about +/-5 pct. That spread is a better error bar
than either number alone, and it sits inside the independently validated
7.3-7.7 pct force accuracy of this same path.

## 23:20 | realism-exploration
Hull SDF, two findings, one of them a hard stop.
(a) DECIMATION FAILED ITS OWN CHECK and the script caught it. Vertex clustering
    to 4,848 faces lost 27.8 pct of hull volume (3.542739 -> 2.556947 m^3).
    Buoyancy is linear in displaced volume, so that SDF is unusable and is NOT
    being used. The printed trade curve gives the fix: vox 0.0642 m -> 39,381
    faces at -2.1 pct volume. Rebuilding there. Source volume itself reproduced
    the canonical 3.542739 m^3 to -0.000 pct, so the reader and the mesh are
    both sound; only the decimation was too aggressive.
(b) THE AXIS TRANSPOSITION IS REAL AND I HAVE NOW LOCATED IT. Raw mesh extents
    are (4.2826, 1.7464, 1.5180), LONG AXIS X. The assessment's scene extents
    are (1.7078, 4.2014, 1.4853), LONG AXIS Y. So the pipeline rotates the hull
    90 degrees about z when loading it; vehicle_params.py is not wrong about the
    MESH, it is wrong about the SCENE. Independent confirmation: permuting my
    solid-voxel inertia onto the scene axes gives mesh Ixx 370.7 vs scene Iyy
    395.0 (-6.2 pct), mesh Iyy 1402.5 vs scene Ixx 1501.5 (-6.6 pct), mesh Izz
    1625.1 vs scene Izz 1685.4 (-3.6 pct). All three agree within 7 pct once the
    permutation is applied, and disagree by -75 pct / +255 pct without it. This
    is the hard constraint's 379 pct hazard, measured from a second direction.
    Also measured: CG 0.5822 m above the hull's min-z, against the assessment's
    cloud value 0.6312 m and vehicle_params' 0.51 m estimate.

## 23:40 | realism-exploration
NEGATIVE RESULT, and it refutes my own hypothesis. Built simulation/realism/
open_channel.py (streamwise periodic wrap + Zhao velocity relaxation inlet;
Zhao's pressure outflow deliberately NOT ported, per register B7 there is no
pressure field) and proto_channel.py, a matched two-arm test where the ONLY
difference is the downstream boundary. Scored on the assessment's own metric,
frames within +/-10 pct of nominal depth:
    tank  (closed wall) 53/90 = 58.9 pct, excursion -26.2/+22.3, pileup 1.78
    channel (wrap)      27/90 = 30.0 pct, excursion -25.3/+33.1, pileup 1.99
THE PERIODIC WRAP IS WORSE THAN THE CLOSED TANK. Mechanism: a periodic domain
has no energy sink, so the surge recirculates while the inlet keeps injecting
momentum; a closed wall reflects once and settles.
Added a downstream sponge (Jacobsen, Fuhrman & Fredsoe 2012 relaxation-zone
style) and swept its gain. It does NOT rescue it:
    sponge 0.25  42/90 = 46.7 pct, pileup 2.88
    sponge 0.50  34/90 = 37.8 pct, pileup 3.33, excursion +77.8
    sponge 0.80  38/90 = 42.2 pct, pileup 3.52, excursion +85.4
The sponge damps vz, which dams the band and makes the pile-up WORSE. Tank wins
every arm on every measure. Report this as a clean negative result.
DO NOT claim either arm "beat the canonical 22 pct": my scene has 6.4 cells per
depth against the canonical 2.000, so that comparison is confounded. Only the
tank-vs-channel comparison is matched.
CONSISTENT WITH REGISTER F1, which already says "the tank is the CORRECT
analogue for L1, not a limitation," because the AR&R criteria were derived from
stationary vehicles subjected to flow. There is a live tension between that and
the assessment's section 4, and this experiment gives no reason to abandon the
tank. UNTRIED and genuinely different from what I built: register B7's own
prescription is a depth-controlled outflow that DEACTIVATES particles above a
target surface, i.e. removes mass, where I RECIRCULATED it. particle_selection
exists in the kernels (mpm_utils.py:1472 tests it), so deactivation is
available. That is the next thing to try, and it is not what was tested here.

## 23:45 | realism-exploration
Hull inertia at the volume-preserving decimation (39,381 faces, -2.148 pct
volume) INDEPENDENTLY REPRODUCES the assessment's tensor once the axis
permutation is applied, from raw mesh via solid voxelisation rather than from
the solver's particle cloud:
    mesh Ixx  392.7  vs scene Iyy  395.0   -0.6 pct
    mesh Iyy 1484.1  vs scene Ixx 1501.5   -1.2 pct
    mesh Izz 1671.6  vs scene Izz 1685.4   -0.8 pct
    CG 0.6426 m vs cloud 0.6312 m (+1.8 pct), vs vehicle_params 0.51 m (+26 pct)
All three within 1.2 pct permuted; -73.8/+275.7/-0.8 pct UNpermuted. Two
independent routes now agree, so the axis transposition is settled fact, not an
assessment claim. Coarse decimation gave -6.2/-6.6/-3.6 pct, so decimation
quality is visible in the tensor and 39k faces is enough.

## 23:55 | realism-exploration
THE CANONICAL YARIS HULL IS NOW FORCE-COUPLED AND VALIDATED. proto_hull_float.py
at n_grid 96, lim 7.0, depth 1.0 m, 765,280 water particles, 480 frames, 37 s
wall, no divergence, depth/dx 13.7.
    Fz_settled     10,794.74 N  against weight M*g = 1100*9.81 = 10,791.0 N
    error          +0.035 pct
    implied V_disp 1.10038 m^3  against M/rho_w = 1.100 m^3
    settled vz     -0.0044 m/s, i.e. converged
    settled draft  0.5237 m against a MEASURED surface of 1.0965 m
Nothing was tuned to hit this: both targets follow from mass and water density
alone. added_mass stayed 0.0, i.e. unmodified physics.
The axis hazard was HANDLED, not dodged: mesh-frame SDF + mesh-frame tensor +
a 90 deg quaternion about z, with DynamicSDFBody forming I_world^-1 =
R I_body^-1 R^T every substep. No tensor was permuted by hand.
SDF CARVE MATTERED, as predicted before running: n_carved_sdf 71,072 = 3.444 m^3
against n_carved_bbox_would_be 141,600 = 6.862 m^3, so a bounding-box carve
would have removed 1.99x the water and corrupted the equilibrium.
FIRST PASS (240 frames, un-remeasured surface) gave -0.68 pct and vz -0.029 m/s.
The improvement to +0.035 pct came from re-measuring the free surface and
settling longer, NOT from changing any physics parameter.
Still open: rendering (goals 5-7, not started); register B7's particle-
deactivation outflow (untried); the naive periodic channel stays refuted.
