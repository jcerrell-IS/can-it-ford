### DISPATCH 9, LS6 GPU, the moving-vehicle driver on the warpmpm SDF path

```
SCOPE DECLARATION
MACHINE: LS6, BATCH not idev (Vista burns 98.5-99.1% of node-hours interactively and
  95 of 184 jobs ended in TIMEOUT; LS6 shows 0 batch timeouts; Vista's allocation
  expires 2026-09-30).
BRANCH: new, claude/fork-moving-driver-<slug>, off main.
MAY WRITE TO: that branch, and a NEW $SCRATCH output directory.
NEVER TOUCH: main; renders/yaris_render_s1/sim_standing.py or any canonical driver;
  data/all_runs_inventory.csv; gates_results_all_runs.json; any existing run directory;
  Dispatch 8's branches; Dispatch 10's scene branch.

ENGINE DECISION, ALREADY MADE ON EVIDENCE. USE warpmpm, pinned SHA
544c93dd02cb9c7ead89e1155a62967243244fce, moving-SDF-collider path. Do not switch and
do not re-litigate. The reasons, so you do not repeat the search:
- NOT DualSPHysics: x86-only static libraries, hard aarch64 blocker on GH200.
- NOT Genesis. Six measured failures on the real hull: fixed 0.8 m cube V=0.512 m3
  fully submerged at gd16 gave F_analytic 5022.7200 N against F_measured second-half
  -291.6208 N, error -105.8060%, a CONVERGED WRONG ANSWER; a free body at half water
  density SANK from z 0.887500 to 0.687123 m in 0.64 s; the canonical Yaris hull gave
  -69.3862% buoyancy and ended 0.107 m below start; refinement converges toward ZERO
  force, gd16 to gd32 moving -111.945% to -97.538%; under strict settle the largest
  upward force under any configuration was +712.1 N against a 2511.4 N cube weight and
  a 10790.9 N Yaris weight, so nothing can rise. Genesis 1.1.1 has three couplers and
  only LegacyCoupler supports MPM, with only on/off booleans exposed.
- NOT CPIC, despite the literature recommending Hu et al. 2018 (10.1145/3197517.3201293).
  It has already been evaluated and REFUSED in this repo at
  analysis/verify_cpic_ground_clearance.py: rigid_g2p_accumulate at mpm_utils.py:1370-1412
  gathers grid_v_out with no CPIC masking and cdf_reaction_force is only zeroed and
  read, never applied to a body. Attaching a sheet to the hull blocks its p2g deposits
  while leaving its g2p gather unmasked, which is momentum non-conserving.
- Architecture worth imitating but NOT installing: Canelas et al. 2018
  (10.1016/J.APOR.2018.04.015) coupling DualSPHysics to Project Chrono. Chrono is the
  only stack exposing wheel torque, which is the propulsion hook nobody has used in a
  flood study. Read it for architecture only.

NO SOLVER CHANGE IS NEEDED FOR A MOVING BODY. The API already exists, verified in
third_party/mpm-engine-544c93dd-solver-core/core/solver.py:
  :324 add_sdf_collider   :339 set_sdf_pose   :348 reset_sdf_force
  :354 sdf_wrench         :363 add_cdf_collider   :93 periodic_x
The driver loop, per tick:
  reset_sdf_force(handle)
  solver.step(dt_sub, n_substeps)
  w = solver.sdf_wrench(handle, dt=n_substeps*dt_sub)   # TICK duration, not dt_sub
  integrate(w['force'], w['torque'], tick_dt)
  solver.set_sdf_pose(handle, center=..., quat=..., velocity=..., omega=...)

FIVE TRAPS, EACH WITH A MEASURED FAILURE BEHIND IT. Do not rediscover these.
1. NORMALISE THE WRENCH BY TICK DURATION. sdf_wrench divides accumulated impulse by
   whatever dt it is handed, and the accumulator spans every substep since the last
   explicit reset. Passing dt_sub for an n-substep tick inflates force by EXACTLY n,
   and the result looks plausible.
2. ZERO THE ACCUMULATOR EVERY WINDOW. The engine never zeroes param.force on the SDF
   path, so a naive read is the run-to-date total. Reference implementation:
   /Users/josie/can-it-ford-realism/simulation/realism/dynamic_body.py:178 and :244
   both call param.force.zero_().
3. QUATERNION ORDER DIFFERS WITHIN THE SAME FILE. solver.py:324 defaults
   quat=(0,0,0,1), xyzw. add_cup at :256 documents wxyz and defaults (1,0,0,0).
   Crossing them applies a wrong rotation SILENTLY.
4. COM-OFFSET IS A HARD BLOCKER AND THE LARGEST NEW-CODE ITEM. RigidBody6DOF raises
   NotImplementedError on a non-zero COM offset, because the SDF collider rotates
   about its centre and sdf_wrench reports torque about that same centre. The Yaris
   particle-cloud CG sits 0.6312 m above the floor against bbox mid-height 0.7427 m,
   so a real hull is NOT centre-symmetric. Implement COM-offset migration BEFORE any
   free-rotation run on a real hull.
5. NEVER COMBINE periodic_x WITH AN SDF VEHICLE. solver.py:90-92 says periodic_x is
   "incompatible with CDF colliders and rigid bodies", and add_cdf_collider guards on
   it at :379, but there is NO EQUIVALENT GUARD in add_sdf_collider. The combination
   is silently wrong rather than an error.

AN ENGINE DEFECT NO DRIVER CAN FIX. STATE IT IN EVERY WRITEUP.
mpm_utils.py:1100 initialises rigid particle stress to a zero mat33, :1104 excludes
material 8 from the SVD, and no mat==8 branch in :1105-1147 ever assigns one. The
rigid hull therefore exerts NO PRESSURE on the water, which is exactly what a moving
vehicle pushing water aside requires. Fixing it means patching a vendored engine at a
pinned SHA. Until then every drag and bow-wave force in this track is not physically
formed and the writeup must say so.
THE CORRECT NUANCE, do not overstate it: _apply_rigid_restitution IS live in all 17
gated runs at restitution 0.05, so "no force is ever formed" is FALSE. The real
limitation is that the net force cannot be DECOMPOSED into hydrodynamic, contact and
gravitational parts.

HOW THE VEHICLE MOVES, three options, ranked by defensibility not by ambition.
(a) PRESCRIBED KINEMATICS, constant velocity through the water. This is what the
    validation literature actually covers, so it is the only arm with a comparison.
(b) PRESCRIBED VELOCITY WITH A TRACTION BUDGET CHECK. Move at prescribed speed, but
    at every step compute the traction available from F_F = mu*(W - B - L) and report
    whether the drag exceeds it. This is Shah et al. 2018's balance
    (0.5*rho*C_D*A_D*v^2 = F_N*(mu_RO + mu) + F_DV) evaluated as a DIAGNOSTIC rather
    than integrated as a force. It is honest, cheap, and it is the graded result.
(c) FULL 6-DOF FREE BODY WITH APPLIED PROPULSION. Genuinely novel, and genuinely
    unvalidatable: no published source applies engine torque in a coupled flood
    simulation, so there is no target. Mark EXPLORATORY, run last, never headline it.
Start with (a), deliver (b), attempt (c) only if (a) and (b) close.

PARAMETERS, WITH PROVENANCE, DO NOT INVENT THESE
  mu 0.3 parked baseline (Bonham and Hattersley 1967, adopted conservatively for the
    published hazard curves), 0.52 measured parallel to flow, rolling mu_RO 0.092
    (Shah et al. 2018)
  measured tyre friction 0.75 wet / 0.78 dry on concrete (Smith, Modra, Felder 2019)
  C_D band 1.22 to 6.82 is a JOINT ENVELOPE over three vehicles and all flow
    directions (Hu et al. 2023, J. Hydrology 620:129525), so the midpoint 4.02 is not
    an estimate for any single vehicle at any orientation. Do not quote 95.71 percent
    agreement until the per-vehicle table is read.
  floor friction 0.55 and restitution 0.05 are the canonical scene values; the gated
    driver is sha256 5215c38b, 389 lines, and :132-133 IS its floor plane. A repoint
    to :210-211 was tested and REFUSED on evidence; do not re-apply it.

CONCRETE FIRST STEP
Reproduce the existing exploratory run before changing anything: load
rogue_g96_pd8_coarse_watertight.ply (sha256 c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2)
through the SDF path and confirm you recover volume 4.950341 m3 and canonicalized
extent 2.010112, 4.746607, 1.729385 with the long axis on y. If those three numbers
do not reproduce, stop and report; everything downstream is invalid.

DEFINITION OF DONE
Arm (a) and arm (b) running and classified, with per-step traction margin reported
against F_F = mu*(W - B - L). Every force number carries the "cannot be decomposed"
caveat and the no-rigid-pressure caveat. Wrench normalisation, accumulator zeroing and
quaternion order each verified by an explicit test, not by inspection. Branch pushed
with PUSH_OK=1 and confirmed by ls-remote.
```

OPERATING PROTOCOL, applies to you in full:

```
OPERATING PROTOCOL:

Before starting: check git log, .remember/ files, and the research
citations you were given, in that order. Do not duplicate work already
done elsewhere in this bundle.

When you hit an obstacle: try a fix. If it doesn't work, try a second,
genuinely different approach, not a variation of the same one. Before
concluding you're stuck, check whether an available connector or subagent
resolves it:
  - DeepWiki, for any question about how a library/repo actually behaves.
    Treat its answer as a hypothesis to verify against source, not fact.
  - The physics-skeptic subagent, before finalizing any claim involving a
    percentage, force, verdict count, or distance. If it's unavailable this
    session, say so explicitly and mark the claim unreviewed, do not fake
    the review.
  - Wolfram, for any physical parameter, unit conversion, or equation
    before it becomes a stated claim.
  - Scite, for any citation, DOI, or threshold before it's written as
    settled.
  - register_integrity.py (or the project's equivalent), before any commit.

Prefer proceeding on a clearly-labeled, reversible assumption over
stopping. State the assumption explicitly, in the commit message or the
write-up, so it can be revisited later without re-deriving it from
scratch.

Tag every factual claim by its source: read directly, recalled from
context, or inferred. Tag every solver/engine claim by which engine it
applies to. Never state a number from memory when you could check it live.

Keep working on everything else in your scope even if one specific thing
below is blocked, do not let one blocker stop the whole session.

Flag, rather than silently proceed past, only these four things:
1. You are about to discard, overwrite, or force-push over uncommitted
   work you did not create and cannot verify is safe to lose.
2. You've found two independently-reported results that genuinely
   disagree about the same physical quantity, not just different framing
   of the same thing, and resolving which is correct requires a judgment
   call, not just more data you can go get yourself.
3. You are about to edit a canonical file outside your declared scope.
4. A genuine hard-stop case: real financial cost, an exposed credential,
   a destructive/irreversible action, or anything matching the project's
   existing standing hard rules.

When you flag one of these: write it clearly to a named file (not just an
inline comment), keep working on everything else in your scope that isn't
blocked by it, and do not treat the flag as ending the session.

Write with an engineer/scientist's discipline throughout: state
assumptions before acting on them, prefer a falsifiable test over a
plausible-sounding claim (a no-forcing control, a held-fixed comparison,
a second seed), and write up a result the same way whether it confirms or
overturns something already published.

Before any push: confirm the target branch, stage explicit paths only,
never a blanket add, and confirm the push actually landed afterward,
don't just assume the command succeeding means the remote updated.
```
