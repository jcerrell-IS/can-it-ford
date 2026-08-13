"""Regime ladder: walk from C1 toward the 17 gated runs, one variable at a time.

Executes docs/REGIME_LADDER_DISPATCH_2026-08-07.md, which in turn executes section 8
of docs/C1_ROOT_CAUSE_2026-08-07.md. That section's ladder is:

    (a) fully submerged, still water, no planes          C1, already done
    (b) partially submerged, still water, no planes      here
    (c) (b) + floor restitution 0.05                     here
    (d) (c) + flow                                       here

ADDITIVE ONLY. This file imports simulation/validate_coupling_force.py read-only and
never edits it. Every geometry constant is pulled from that file rather than restated,
so this script cannot fork them (CLAUDE.md item 16 records an existing fork of exactly
that kind in gates.py).

WHY THE GEOMETRY BELOW IS WHAT IT IS
------------------------------------
The rung geometry is not invented. It reproduces the canonical gated scene exactly
where the two harnesses can be made to coincide, verified against
data/all_runs_inventory.csv (T1, read live 2026-08-07):

  grid_lim   9.421742313727737 m   identical in all 17 runs and in this harness's LIM
  dx (g64)   0.1472147236519959 m  identical, == LIM/64 == DX_CANON
  depth      0.2944294473039918 m  == 2 * DX_CANON exactly, so --depth-cells 2 lands on
                                   the gated realized_depth_m to the last digit
  layers     4 at g64, 6 at g96    reproduced by the same choice

The body is a cube of side L_BOX = 10*DX_CANON = 1.472147236519959 m spawned with its
bottom face on the floor plane, so submerged fraction is 0.2944294/1.4721472 = 0.2000
exactly. At rho_box = 600 (C1's value, unchanged) that makes the analytic target the
exact negative of C1's:

    a_ideal = g*(rho_w*h_sub/(rho_box*L) - 1)
    C1 (h_sub/L = 1):    9.81*(5/3 - 1)   = +6.5400 m/s^2
    rungs b/c/d (0.2):   9.81*(1/3 - 1)   = -6.5400 m/s^2

so a sign flip in the analytic reference is built into the ladder and any confusion
between "the body responds" and "the body falls" is detectable.

PRE-REGISTERED PREDICTION, stated before the runs so it cannot be fitted afterwards
-----------------------------------------------------------------------------------
C1_ROOT_CAUSE.md section 1 (T1): the body has no equation of motion. Every substep,
v_cm is reassigned to the mass-weighted mean of the GRID velocity gathered at its own
particles (kernels/mpm_utils.py:1411 and :1434). For a PARTIALLY submerged body that
mean is a blend of two populations:

  dry particles   nodes carrying rigid mass only, so v_node = v_body + dt*g exactly,
                  by partition of unity (this is the C0 degeneracy that
                  C1_ROOT_CAUSE.md section 6 item 4 identifies)
  wet particles   nodes shared with water, so v_node is the water's, near zero

With f_dry the dry mass fraction, the substep recursion is approximately

    v_{n+1} = f_dry * (v_n + dt*g)

whose fixed point is v* = f_dry*dt*g/(1 - f_dry), and whose late-window acceleration is
therefore approximately ZERO, not -6.54 m/s^2. At f_dry = 0.8 and g64 (dt = (1/30)/11):

    v* = 0.8 * 3.0303e-3 * (-9.81) / 0.2 = -0.1189 m/s

PREDICTION (b): a_late_window ~ 0, with a sustained downward drift of order 0.1 m/s,
NOT the analytic -6.54 m/s^2. The transition band is about 1.5*dx wide so f_dry is only
known to about +/-0.05, which puts v* somewhere in -0.09 to -0.17 m/s. Recorded as an
order-of-magnitude pre-registration, not a tolerance.

Independent corroboration that this is the right order: C1_ROOT_CAUSE.md section
8b-CORRECTION reports C2 (also partially submerged, also free-rigid) drifting downward
at "roughly 0.15 m/s" (T2, job 895448). Same sign, same order, different scene.

PREDICTION (c): floor restitution 0.05 registers the floor as a rigid contact surface
(mpm_solver_warp.py:1915) and _apply_rigid_restitution does POSITIONAL stabilization,
not only an impulse: it translates the body out of the plane by the deepest penetration
every substep (:936-943), with its own comment saying the impulse alone cannot hold a
resting body because the grid gather resets v_cm. So the descent of (b) should be
arrested and the drift should collapse toward zero.

Provenance tiers, per the dispatch: T1 read live, T2 measured on Vista, T3 derived here.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VCF_PATH = HERE / "validate_coupling_force.py"

# The rung geometry, in one place. See the module docstring for why each value.
DEPTH_CELLS = 2.0          # -> 2*DX_CANON == the gated realized_depth_m exactly
BOX_BOTTOM_CELLS = 0.0     # bottom face on the floor plane, as the gated vehicle is
RHO_BOX = 600.0            # unchanged from C1, so the walk is controlled
FLOOR_RESTITUTION = 0.05   # sim_standing.py:133, read live
INFLOW_LEN = 1.5           # sim_standing.py:77 inflow_len default, read live
MATCH_RUN_G64 = "g64_m1100"
MATCH_RUN_G96 = "g96_m1100"
MATCH_VELOCITY = 1.5       # velocity_ms of both, data/all_runs_inventory.csv


# --------------------------------------------------------------------------------------
# Constants, taken from validate_coupling_force.py WITHOUT importing it.
#
# That module imports warp and warpmpm at module scope, which is unavailable on the Mac
# and which memory `vista-login-warpmpm-import-hangs` records as a 600 s block on a Vista
# login node. Restating the constants here would create exactly the fork CLAUDE.md item
# 16 complains about, so instead the module is parsed and its top-level scalar
# assignments are evaluated in an empty namespace. No call node is ever evaluated.
# When warp IS importable, _load_vcf() re-checks every value against the imported module
# and raises on any disagreement, so the fork cannot open silently.
# --------------------------------------------------------------------------------------
_WANTED = ("LIM", "DX_CANON", "L_BOX", "RHO_W", "BULK", "ETA", "G", "GAMMA", "FPS")


def constants_from_source(path: Path = VCF_PATH) -> dict:
    tree = ast.parse(path.read_text(), filename=str(path))
    ns: dict = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in _WANTED:
            continue
        if any(isinstance(n, (ast.Call, ast.Attribute, ast.Subscript))
               for n in ast.walk(node.value)):
            raise ValueError(f"{target.id} is not a plain scalar expression; refusing to "
                             f"evaluate it. Re-read {path} and update this parser.")
        ns[target.id] = eval(compile(ast.Expression(node.value), str(path), "eval"),
                             {"__builtins__": {}}, dict(ns))
    missing = [k for k in _WANTED if k not in ns]
    if missing:
        raise ValueError(f"{path} no longer defines {missing}. It changed shape under "
                         f"this script; re-read it rather than guessing.")
    return ns


C = constants_from_source()
LIM = C["LIM"]
DX_CANON = C["DX_CANON"]
L_BOX = C["L_BOX"]
RHO_W = C["RHO_W"]
G = C["G"]
FPS = C["FPS"]


def _load_vcf():
    """Import validate_coupling_force and assert its constants match the parsed ones."""
    import importlib
    import sys

    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    vcf = importlib.import_module("validate_coupling_force")
    for name, parsed in C.items():
        live = getattr(vcf, name)
        if not math.isclose(float(live), float(parsed), rel_tol=0.0, abs_tol=0.0):
            raise RuntimeError(
                f"constant fork: {name} parses as {parsed!r} from {VCF_PATH} but imports "
                f"as {live!r}. The file changed under this script. Re-read it.")
    return vcf


# --------------------------------------------------------------------------------------
# Rung mechanics
# --------------------------------------------------------------------------------------
def enable_floor_restitution(tank, restitution=FLOOR_RESTITUTION, friction=0.0):
    """Register the ALREADY-PRESENT floor plane as a rigid contact surface.

    This is exactly equivalent to having constructed the plane with
    add_plane(..., restitution=r) in the first place, and the equivalence is provable
    from the source rather than assumed. In add_surface_collider
    (kernels/mpm_solver_warp.py:1880-1927, read live) `restitution` is used for one
    thing only: the `if restitution != 0.0` gate at :1915 that appends a dict to
    self.rigid_surface_colliders. It is never written to collider_param, so it cannot
    affect how the plane treats WATER. Appending the dict here therefore changes the
    rigid-body treatment and nothing else, and it avoids adding a second Dirichlet
    plane, which is what calling add_plane again would do.

    _apply_rigid_restitution re-reads self.rigid_surface_colliders every substep
    (:921), so a post-construction append is live immediately. Nothing snapshots it at
    finalize_rigid_bodies time; BoxTank itself already adds its planes AFTER that call.

    friction defaults to 0.0, matching BoxTank's own floor, so this changes exactly one
    variable. The 17 gated runs additionally carry floor friction 0.55
    (sim_standing.py:132); that is a THIRD variable and this ladder does not walk it.
    """
    sim = tank.solver._sim
    entry = {
        "point": [0.0, 0.0, float(tank.floor)],
        "normal": [0.0, 0.0, 1.0],
        "friction": float(friction),
        "restitution": float(restitution),
        "start_time": 0.0,
        "end_time": 999.0,
    }
    sim.rigid_surface_colliders.append(entry)
    return entry


def restitution_is_registered(tank) -> bool:
    return bool(getattr(tank.solver._sim, "rigid_surface_colliders", []))


def kick_water(tank, velocity):
    """The one-shot additive kick, sim_standing.py:160-162 read live.

    `v[: n_water, 0] += velocity` applied once, after settle. It ADDS; the per-frame
    clamp below OVERWRITES. CLAUDE.md item 2 records that distinction and it is kept.
    """
    v = tank.solver.v()
    v[: tank.n_water, 0] += velocity
    tank.solver.set_v(v)
    return int(tank.n_water)


def sustain_inflow(tank, velocity, inflow_x):
    """The per-frame upstream Dirichlet clamp, sim_standing.py:190-198 read live.

    Reimplemented rather than imported because StandingFloodScene owns it as a bound
    method on a scene this harness does not build. The band test, the axis, and the
    overwrite semantics are copied line for line.
    """
    s = tank.solver
    x = s.x()
    v = s.v()
    band = x[: tank.n_water, 0] < inflow_x
    vw = v[: tank.n_water]
    vw[band, 0] = velocity
    s.set_v(v)
    return int(band.sum())


def water_vx_near_box(tank, pad_cells=2.0):
    """Mean and 95th-percentile water vx in a slab spanning the box footprint.

    Used only to answer "did the flow actually reach the body before we measured", which
    a 160-substep window cannot be assumed to satisfy. Returns NaNs when there is no
    water or no particle in the slab.
    """
    if tank.n_water == 0:
        return float("nan"), float("nan"), 0
    x = tank.solver.x()[: tank.n_water]
    v = tank.solver.v()[: tank.n_water]
    pad = pad_cells * tank.dx
    sel = ((x[:, 0] >= tank.box_x0 - pad) & (x[:, 0] <= tank.box_x0 + tank.length + pad)
           & (x[:, 1] >= tank.box_x0 - pad) & (x[:, 1] <= tank.box_x0 + tank.length + pad))
    if not sel.any():
        return float("nan"), float("nan"), 0
    vx = v[sel, 0]
    return float(vx.mean()), float(np.percentile(vx, 95)), int(sel.sum())


def guard_slack(tank):
    """Distance to the nearest P2G edge-guard bound, over all particles and all axes.

    Mirrors core/solver.py:506-507 exactly: the guard tests the global min and max of the
    position array against 1.5*dx and lim - 2.5*dx, on all three axes when periodic_x is
    unset, which it always is here. Returns (slack_m, vmax) with slack negative once the
    guard would fire.
    """
    x = tank.solver.x()
    v = tank.solver.v()
    dx = tank.dx
    slack = min(float(x.min()) - 1.5 * dx, (LIM - 2.5 * dx) - float(x.max()))
    return slack, (float(np.abs(v).max()) if len(v) else 0.0)


def guard_would_trip(tank, margin_cells=0.25):
    """True when one more substep plausibly breaches the guard.

    Needed because rung (b) removes the only thing holding the body up. With every plane
    at restitution 0.0 the floor is invisible to a rigid body
    (kernels/mpm_solver_warp.py:1915), so the body descends through it and into the guard,
    which is the same crash C1_ROOT_CAUSE.md section 8b records for C2. At the gated water
    depth this is unavoidable rather than a tuning problem: 20 percent of the cube's
    height IS the full 0.2944294 m water depth, so a 20-percent-submerged cube must have
    its bottom face on the floor, which leaves only 1.5*dx of travel before the guard.
    Truncating the window and saying so is honest; enlarging the tank to dodge it would
    silently stop matching the gated scene.
    """
    slack, vmax = guard_slack(tank)
    return slack <= (vmax * tank.dt + margin_cells * tank.dx), slack, vmax


def submersion(tank, z_surface):
    """Submerged height and fraction of the cube, from a given free-surface height.

    Uses BoxTank.z_bottom() and BoxTank.column_surface(), the diagnostics that already
    exist. The dispatch asks for "whatever waterline diagnostic is cheapest to add ...
    do not invent a new one", so nothing new is invented here.
    """
    zb = tank.z_bottom()
    h_sub = float(np.clip(z_surface - zb, 0.0, tank.length))
    return h_sub, h_sub / tank.length, zb


def a_ideal_partial(h_sub, length, rho_box, rho_w=None, g=None):
    """g*(rho_w*h_sub/(rho_box*L) - 1). Reduces to C1's g*(rho_w/rho_box - 1) at h_sub=L.

    Units: [m/s^2] = [m/s^2] * ([kg/m^3][m] / ([kg/m^3][m]) - 1). Dimensionless bracket,
    so the expression is dimensionally sound.
    """
    rho_w = RHO_W if rho_w is None else rho_w
    g = G if g is None else g
    return g * (rho_w * h_sub / (rho_box * length) - 1.0)


def _write_timeseries_csv(res, path):
    """Write the rung-d surge trace in the exact format the failure-mode classifier eats.

    Header and column order are FloodHistory.to_csv (renders/yaris_render_s1/
    vehicle_live.py:315-325), the same 15 columns the 17 gated metrics.csv files carry,
    so simulation/failure_modes.classify_timeseries reads it unmodified. Its hard
    requirement is t,dx,dy,dz,vx,vy,vz (failure_modes.REQUIRED_COLUMNS); the extra
    columns are ignored by the classifier and kept only for shape parity. Angles are
    written as 0.0: this harness's body is a cube whose orientation the ladder does not
    reduce to Euler angles, and the classifier reads none of them.

    Frame cadence, not substep cadence, because sustain_frames=3 is a SAMPLE count and
    the gated runs sample once per frame at 30 fps.
    """
    if not res.get("flow_com_series"):
        raise SystemExit("--emit-timeseries needs a rung-d run: no flow trace was "
                         "recorded (rungs b and c have no flow phase).")
    t = np.asarray(res["flow_t_series"], dtype=float)
    com = np.asarray(res["flow_com_series"], dtype=float)
    vel = np.asarray(res["flow_vel_series"], dtype=float)
    om = np.asarray(res["flow_omega_series"], dtype=float)
    disp = com - np.asarray(res["flow_com0"], dtype=float)
    zero = np.zeros((len(t), 1))
    rows = np.column_stack([t, disp, np.linalg.norm(disp, axis=1),
                            zero, zero, zero,
                            vel, np.linalg.norm(vel, axis=1), om])
    header = ("t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg,"
              "vx,vy,vz,vmag,wx,wy,wz")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(p, rows, delimiter=",", header=header, comments="")
    return len(t)


def _first_sustained(mask, sustain):
    """Index where `mask` first holds for `sustain` consecutive samples, else -1.

    Reproduces simulation/failure_modes.py:135-151 `_first_sustained_index` so the
    ladder can report the classifier's own SLIDE trigger without importing it (this
    file's standing rule is that it imports validate_coupling_force read-only and
    restates nothing else). Verified against the classifier on the same arrays.
    """
    mask = np.asarray(mask, dtype=bool)
    run = 0
    for i, b in enumerate(mask):
        run = run + 1 if b else 0
        if run >= sustain:
            return int(i - sustain + 1)
    return -1


def late_window_slope(t, v, measure_substeps):
    """a_late_window, computed exactly as run_c1 computes it.

    run_c1 (read live): tail = min(len(t)-1, measure_substeps); polyfit over
    t[tail//2:]. Reproduced verbatim so the ladder's headline sits on the same axis as
    C1's. C1_ROOT_CAUSE.md section 2 and section 6 item 3 are why the early window is
    not used.
    """
    t = np.asarray(t)
    v = np.asarray(v)
    tail = min(len(t) - 1, measure_substeps)
    if tail <= 8:
        return float("nan")
    return float(np.polyfit(t[tail // 2:], v[tail // 2:], 1)[0])


def water_under_box(tank):
    """How much water is BENEATH the body's footprint, and beside it.

    This turned out to be the load-bearing diagnostic. BoxTank carves every water particle
    whose position falls inside the cube (its __init__ `inside` test), and at the gated
    depth the cube's bottom face is on the floor, so the carve removes the entire water
    column under the footprint and leaves nothing below the body at all. A buoyant force
    on this coupling path is a pressure difference across the body, so with zero water
    underneath there is nothing to generate one and the only coupling left is lateral
    shear on the wetted sides.
    """
    if tank.n_water == 0:
        return {"n_under": 0, "n_beside_wetted": 0, "frac_under": 0.0}
    w = tank.solver.x()[: tank.n_water]
    zb = tank.z_bottom()
    x0, x1 = tank.box_x0, tank.box_x0 + tank.length
    in_foot = ((w[:, 0] >= x0) & (w[:, 0] <= x1)
               & (w[:, 1] >= x0) & (w[:, 1] <= x1))
    under = in_foot & (w[:, 2] < zb)
    pad = 1.0 * tank.dx
    ring = (((w[:, 0] >= x0 - pad) & (w[:, 0] <= x1 + pad)
             & (w[:, 1] >= x0 - pad) & (w[:, 1] <= x1 + pad))
            & ~in_foot & (w[:, 2] >= zb))
    return {
        "n_under": int(under.sum()),
        "n_in_footprint_any_z": int(in_foot.sum()),
        "n_beside_wetted": int(ring.sum()),
        "frac_under": float(under.sum()) / float(tank.n_water),
        "box_bottom_z": zb,
    }


def run_rung(rung, n_grid, rho_box=RHO_BOX, depth_cells=DEPTH_CELLS,
             box_bottom_cells=BOX_BOTTOM_CELLS, settle_frames=1200,
             measure_substeps=160, flow_frames=60, velocity=MATCH_VELOCITY,
             device="auto", seed=0, guard_margin_cells=0.25):
    """Run one rung. rung is 'b', 'c' or 'd'."""
    if rung not in ("b", "c", "d"):
        raise ValueError(f"unknown rung {rung!r}, expected 'b', 'c' or 'd'")
    vcf = _load_vcf()
    # Installed for every rung, not just the Fix B demo. Rung (b) removes the floor from
    # the body's world, so a guard trip is a live possibility, and Fix B is exactly what
    # turns that trip from "x in [0.2207, 8.8697]" into a named axis and a named material.
    install_p2g_guard_diagnostic()

    dx = LIM / n_grid
    z_b0 = 3.0 * DX_CANON + box_bottom_cells * DX_CANON   # BoxTank's floor is 3*DX_CANON
    tank = vcf.BoxTank(n_grid, rho_box, depth_cells, z_b0, water=True,
                       device=device, seed=seed)

    # --- settle, body pinned -----------------------------------------------------------
    # Floor restitution is deliberately NOT registered yet. During settle the body is
    # pinned every frame (settle_pinned -> tank.pin), which rewrites rigid_x_cm and zeroes
    # v_cm, so any positional correction restitution made inside the frame is overwritten
    # at the frame boundary and cannot persist. Registering it later is therefore
    # equivalent for the physics, and it keeps _apply_rigid_restitution's per-substep
    # host-side numpy loop out of a window that can run 1200 frames.
    settle = vcf.settle_pinned(tank, settle_frames)
    settle_ok = bool(settle["settle_gate_met"])
    zs_settle, n_free_cols, col_iqr = tank.column_surface()

    restitution_entry = None
    if rung in ("c", "d"):
        restitution_entry = enable_floor_restitution(tank)
    rest_registered = restitution_is_registered(tank)

    # --- optional flow development phase, rung (d) only --------------------------------
    # A 160-substep window is 14.5 frames at g64. At 1.5 m/s the upstream band is roughly
    # 3.5 m from the body, about 2.3 s or 70 frames of transit, so measuring immediately
    # would measure still water with a clamp on the far wall. flow_frames lets the flow
    # arrive first, and vx_before/vx_after record whether it actually did.
    inflow_x = tank.wall + INFLOW_LEN
    flow = None
    flow_t = flow_com = flow_vel = flow_omega = flow_com0 = None
    if rung == "d":
        vx0 = water_vx_near_box(tank)
        # SURGE INSTRUMENTATION, added 2026-08-13. The body is FREE for the whole flow
        # phase and this phase runs entirely BEFORE the measure window, so any downstream
        # drift accumulated here was previously invisible: the window only ever recorded
        # rigid_state()["v"][2] and z_bottom(). In the 17 gated runs SLIDE onset is frame
        # 2 to 5 (onset_frame_slide in data/failure_modes_by_run_classified.csv), which
        # falls INSIDE this phase, not inside the window. Sampling is per FRAME here so
        # the series is directly comparable to the gated runs' 30 fps frame cadence.
        _rs0 = tank.solver.rigid_state()
        flow_com0 = [float(c) for c in _rs0["com"]]
        flow_t = [0.0]
        flow_com = [flow_com0]
        flow_vel = [[float(c) for c in _rs0["v"]]]
        flow_omega = [[float(c) for c in _rs0["omega"]]]
        frame_dt = tank.dt * tank.substeps
        n_kicked = kick_water(tank, velocity)
        n_band = 0
        flow_frames_run = 0
        flow_truncated = False
        for _ in range(flow_frames):
            trip, _slack, _vmax = guard_would_trip(tank, guard_margin_cells)
            if trip:
                flow_truncated = True
                break
            tank.project_water()
            n_band = sustain_inflow(tank, velocity, inflow_x)
            tank.solver.step(tank.dt, tank.substeps)
            flow_frames_run += 1
            _rs = tank.solver.rigid_state()
            flow_t.append(flow_frames_run * frame_dt)
            flow_com.append([float(c) for c in _rs["com"]])
            flow_vel.append([float(c) for c in _rs["v"]])
            flow_omega.append([float(c) for c in _rs["omega"]])
        vx1 = water_vx_near_box(tank)
        flow = {
            "flow_frames_run": flow_frames_run,
            "flow_truncated_by_p2g_guard": flow_truncated,
            "velocity_ms": velocity,
            "inflow_x_m": inflow_x,
            "inflow_len_m": INFLOW_LEN,
            "flow_frames": flow_frames,
            "n_kicked": n_kicked,
            "n_in_inflow_band_last": n_band,
            "water_vx_near_box_before": {"mean": vx0[0], "p95": vx0[1], "n": vx0[2]},
            "water_vx_near_box_after": {"mean": vx1[0], "p95": vx1[1], "n": vx1[2]},
            "flow_reached_body": bool(np.isfinite(vx1[0]) and vx1[0] > 0.25 * velocity),
        }
        # SURGE SUMMARY. disp is com minus the pre-flow com, which is this harness's
        # analogue of the gated runs' spawn com0: the body is at rest and unforced at
        # that instant. Axis convention is failure_modes.SURGE_AXIS = 0 = scene +x, the
        # same axis kick_water and sustain_inflow drive.
        _fc = np.asarray(flow_com, dtype=float)
        _fv = np.asarray(flow_vel, dtype=float)
        _disp = _fc - np.asarray(flow_com0, dtype=float)
        flow.update({
            "frame_dt_s": frame_dt,
            "surge_drift_final_m": float(_disp[-1, 0]),
            "surge_drift_max_m": float(np.abs(_disp[:, 0]).max()),
            "surge_speed_max_ms": float(np.abs(_fv[:, 0]).max()),
            "surge_speed_final_ms": float(_fv[-1, 0]),
            "lift_final_m": float(_disp[-1, 2]),
            # The classifier's own SLIDE test, applied here so the ladder reports the
            # same quantity the 17 gated verdicts are made of. Thresholds are the
            # failure_modes.FailureThresholds defaults, restated rather than imported so
            # this file keeps its "imports validate_coupling_force read-only" property.
            "slide_m_threshold": 0.05,
            "slide_speed_ms_threshold": 0.05,
            "sustain_frames": 3,
            "slide_ratio": float(np.abs(_disp[:, 0]).max() / 0.05),
            "slide_sustained": bool(_first_sustained(
                (np.abs(_disp[:, 0]) >= 0.05) & (np.abs(_fv[:, 0]) >= 0.05), 3) >= 0),
            "slide_onset_frame": int(_first_sustained(
                (np.abs(_disp[:, 0]) >= 0.05) & (np.abs(_fv[:, 0]) >= 0.05), 3)),
        })
        zs_settle, n_free_cols, col_iqr = tank.column_surface()

    h_sub0, frac0, zb0 = submersion(tank, zs_settle)
    wub0 = water_under_box(tank)

    # --- measurement window, substep resolution, mirroring run_c1 ----------------------
    ts = [0.0]
    vs = [float(tank.solver.rigid_state()["v"][2])]
    zbs = [tank.z_bottom()]
    truncated_at = None
    guard_slack_at_stop = None
    for i in range(measure_substeps):
        trip, slack, _vmax = guard_would_trip(tank, guard_margin_cells)
        if trip:
            truncated_at = i
            guard_slack_at_stop = slack
            break
        tank.project_water()
        if rung == "d" and tank.substeps and i % tank.substeps == 0:
            # sim_standing applies the clamp once per FRAME (its step() calls
            # _sustain_inflow then solver.step(dt, substeps)). This window advances one
            # SUBSTEP at a time, so the clamp is applied at frame boundaries only, to
            # keep its cadence rather than its call count. project_water stays per
            # substep because that is run_c1's cadence and rungs b and c must match it.
            sustain_inflow(tank, velocity, inflow_x)
        tank.solver.step(tank.dt, 1)
        ts.append((i + 1) * tank.dt)
        vs.append(float(tank.solver.rigid_state()["v"][2]))
        zbs.append(tank.z_bottom())

    t = np.asarray(ts)
    v = np.asarray(vs)
    # a_late_window is fitted over the second half of the window that ACTUALLY RAN, not
    # of the window that was requested. len(t)-1 is the achieved substep count, so a
    # truncated rung still gets a late-window fit over its own late half, and the
    # achieved count is reported alongside so nobody reads it as a full window.
    achieved = len(t) - 1
    a_late = late_window_slope(t, v, achieved)
    windows = {f"a_first_{n}_substeps": float(np.polyfit(t[: n + 1], v[: n + 1], 1)[0])
               for n in (2, 3, 5, 10, 20, 40) if n < len(t)}

    zs_end, _, _ = tank.column_surface()
    _h_sub1, frac1, zb1 = submersion(tank, zs_end)
    a_id0 = a_ideal_partial(h_sub0, tank.length, rho_box)
    tail_v = v[len(v) // 2:]

    return {
        "variant": f"LADDER_rung_{rung}",
        "rung": rung,
        "rung_description": {
            "b": "partially submerged, still water, all planes restitution 0.0",
            "c": "partially submerged, still water, floor restitution 0.05",
            "d": "partially submerged, floor restitution 0.05, sustained inflow",
        }[rung],
        "dispatch": "docs/REGIME_LADDER_DISPATCH_2026-08-07.md section 3",
        "geometry": tank.geometry(),
        "settle": settle,
        "settle_gate_met": settle_ok,
        "settle_is_discard": (not settle_ok),
        "surface_after_settle": zs_settle,
        "surface_columns_used": n_free_cols,
        "surface_column_iqr_m": col_iqr,
        "z_b_nominal_at_spawn": z_b0,
        "floor_z": tank.floor,
        "box_bottom_at_release": zb0,
        "box_bottom_at_end": zb1,
        "box_bottom_travel_m": zb1 - zb0,
        "box_bottom_travel_dx": (zb1 - zb0) / dx,
        "submerged_height_m": h_sub0,
        "submerged_frac": frac0,
        "submerged_frac_at_end": frac1,
        "restitution_registered": rest_registered,
        "restitution_entry": restitution_entry,
        "water_under_body_at_release": wub0,
        "water_under_body_at_end": water_under_box(tank),
        "guard_margin_cells": guard_margin_cells,
        "flow": flow,
        "matched_gated_run": (MATCH_RUN_G64 if n_grid == 64 else
                              MATCH_RUN_G96 if n_grid == 96 else None),
        "a_ideal_partial": a_id0,
        "a_ideal_fully_submerged_for_reference": G * (RHO_W / rho_box - 1.0),
        "a_windows": windows,
        "a_headline_first3": windows.get("a_first_3_substeps", float("nan")),
        "a_late_window": a_late,
        "a_late_as_fraction_of_ideal": (a_late / a_id0 if abs(a_id0) > 1e-12
                                        else float("nan")),
        "v_mean_late": float(tail_v.mean()),
        "v_final": float(v[-1]),
        "v_ptp_late": float(tail_v.max() - tail_v.min()),
        "prediction_v_star_free_rigid": _v_star_prediction(frac0, tank.dt),
        "measure_substeps_requested": measure_substeps,
        "measure_substeps_achieved": achieved,
        "window_truncated_by_p2g_guard": truncated_at is not None,
        "window_truncated_at_substep": truncated_at,
        "guard_slack_at_stop_m": guard_slack_at_stop,
        "late_window_usable": bool(achieved > 8),
        "measure_window_s": float(t[-1]),
        "dt": tank.dt,
        "substeps_per_frame": tank.substeps,
        "t_series": ts,
        "v_series": vs,
        "zb_series": zbs,
        # Rung-d surge trace, frame cadence, None on rungs b and c. com0 is the pre-flow
        # pose the displacements are measured from.
        "flow_com0": flow_com0,
        "flow_t_series": flow_t,
        "flow_com_series": flow_com,
        "flow_vel_series": flow_vel,
        "flow_omega_series": flow_omega,
        "diagnostics": tank.diagnostics(),
    }


def _v_star_prediction(submerged_frac, dt, g=None):
    """The pre-registered fixed point v* = f_dry*dt*g/(1 - f_dry). See module docstring.

    Returns NaN at f_dry == 1 (nothing submerged), where the recursion has no fixed
    point because the body simply free-falls.
    """
    g = G if g is None else g
    f_dry = 1.0 - float(submerged_frac)
    if f_dry >= 1.0 - 1e-12:
        return float("nan")
    return f_dry * dt * (-g) / (1.0 - f_dry)


# --------------------------------------------------------------------------------------
# Fix A: C3's estimator.
#
# C1_ROOT_CAUSE.md section 9: run_c3 reports a_as_fraction_of_g from a_headline_first3,
# the estimator section 2 discredits. For a NULL test that is strictly worse than for
# C1, because C3's pin injects a nonzero dV by construction, so the metric reads nonzero
# even under perfect coupling. It should use a_late_window, which run_c1 already
# computes and stores.
#
# The owning file simulation/validate_coupling_force.py is held by another session and
# the dispatch's section 1 rule 3 forbids editing it, so the fix lands here as a pure
# function over a C3 result. That is not a workaround for its own sake: because the
# corrected value is a function of fields ALREADY STORED in every C3 JSON, the fix can be
# applied retroactively to runs that have already been paid for, and validated on a login
# node at zero SU. The one-line patch the owner should make is printed by --fix-a.
# --------------------------------------------------------------------------------------
FIX_A_PATCH = (
    'simulation/validate_coupling_force.py, in run_c3, replace\n'
    '    res["a_as_fraction_of_g"] = res["a_headline_first3"] / G\n'
    'with\n'
    '    res["a_as_fraction_of_g"] = res["a_late_window"] / G\n'
    'and keep the old value under a distinct key if the published record needs it:\n'
    '    res["a_as_fraction_of_g_headline_first3_WITHDRAWN"] = res["a_headline_first3"] / G'
)


def fix_a_recompute(result: dict) -> dict:
    """Recompute C3's a_as_fraction_of_g from a_late_window. Pure, no solver needed."""
    for key in ("a_headline_first3", "a_late_window"):
        if key not in result:
            raise KeyError(f"not a C3/C1 result dict: missing {key!r}")
    old = float(result["a_headline_first3"]) / G
    new = float(result["a_late_window"]) / G
    stored = result.get("a_as_fraction_of_g")
    return {
        "variant": result.get("variant"),
        "n_grid": result.get("geometry", {}).get("n_grid"),
        "settle_gate_met": result.get("settle", {}).get("settle_gate_met"),
        "a_headline_first3": float(result["a_headline_first3"]),
        "a_late_window": float(result["a_late_window"]),
        "a_as_fraction_of_g_stored": (float(stored) if stored is not None else None),
        "a_as_fraction_of_g_before": old,
        "a_as_fraction_of_g_after": new,
        "stored_matches_before": (stored is not None
                                  and math.isclose(float(stored), old, rel_tol=1e-12)),
        "abs_change": abs(new - old),
        "sign_flips": (old * new) < 0.0,
    }


# --------------------------------------------------------------------------------------
# Fix B: the P2G edge guard's error message.
#
# C1_ROOT_CAUSE.md section 8b: core/solver.py:506 computes g = x[:, 1:] if periodic_x
# else x, so with periodic_x unset (as in every scene here) the guard checks ALL THREE
# axes, but the raised message at :508-512 hardcodes the label "x" and reports only the
# global min and max over the included axes. Section 8b's open item, "the identity of the
# tripping particle is UNKNOWN", is a direct consequence: the message cannot say which
# axis tripped, and cannot say whether the particle is water, hull, or a rotated corner.
#
# Implemented as an installable monkey-patch rather than an edit to the pinned vendored
# copy under third_party/, whose line numbers C1_ROOT_CAUSE.md section 0 relies on being
# stable. Install it from any driver that wants the diagnostic; the message text is
# produced by a pure function so it can be exercised with no GPU and no solver.
# --------------------------------------------------------------------------------------
AXES = ("x", "y", "z")
# particle_material codes seen in this project. 8 is the rigid body
# (kernels/mpm_solver_warp.py:854 keys on mat_np == 8, read live). Anything else in these
# scenes is the newtonian water set by set_material.
MATERIAL_NAMES = {8: "rigid(mat 8)"}


def p2g_guard_report(x, dx, lim, periodic_x=False, material=None, rigid_id=None):
    """The per-axis, per-material diagnostic the guard should print before it raises.

    x         (n, 3) particle positions
    material  (n,) particle_material, optional
    rigid_id  (n,) particle_rigid_id, optional

    Returns (tripped: bool, message: str). The message names the offending AXIS, the
    offending BOUND, and the identity of the offending particle, which is exactly what
    section 8b says is missing.
    """
    x = np.asarray(x)
    lo_bound = 1.5 * dx
    hi_bound = lim - 2.5 * dx
    checked = (1, 2) if periodic_x else (0, 1, 2)

    lines = []
    worst = None   # (slack, axis, side, index)
    for ax in checked:
        col = x[:, ax]
        i_lo = int(np.argmin(col))
        i_hi = int(np.argmax(col))
        lo, hi = float(col[i_lo]), float(col[i_hi])
        lines.append(f"    {AXES[ax]}: min {lo:.6f} (particle {i_lo}), "
                     f"max {hi:.6f} (particle {i_hi})")
        for slack, side, idx in ((lo - lo_bound, "low", i_lo),
                                 (hi_bound - hi, "high", i_hi)):
            if worst is None or slack < worst[0]:
                worst = (slack, ax, side, idx)

    assert worst is not None   # `checked` is never empty, so the loop always sets it
    tripped = worst[0] < 0.0
    if not tripped:
        return False, ("p2g guard OK; tightest margin "
                       f"{worst[0]:.6f} m on {AXES[worst[1]]} {worst[2]}\n"
                       + "\n".join(lines))

    slack, ax, side, idx = worst
    bound = lo_bound if side == "low" else hi_bound
    who = f"particle {idx}"
    if material is not None:
        code = int(np.asarray(material)[idx])
        who += f", material {code} ({MATERIAL_NAMES.get(code, 'water/newtonian')})"
    if rigid_id is not None:
        rid = int(np.asarray(rigid_id)[idx])
        if rid >= 0:
            who += f", rigid body {rid}"
    if material is not None:
        pos = np.asarray(x)[idx]
        who += f", at ({pos[0]:.6f}, {pos[1]:.6f}, {pos[2]:.6f})"

    msg = (f"particles within 2 cells of the grid edge on axis {AXES[ax].upper()} "
           f"({side} bound {bound:.6f} m, breached by {-slack:.6f} m = "
           f"{-slack / dx:.3f} dx): the P2G stencil would write out of bounds. "
           f"Offender: {who}. "
           f"Domain [0, {lim}] m, dx={dx:.4f}, guard band [{lo_bound:.4f}, "
           f"{hi_bound:.4f}] m"
           + (" (x exempt: periodic_x)" if periodic_x else "")
           + ".\n  per-axis extrema:\n" + "\n".join(lines)
           + "\n  Enlarge grid_lim or add a bounding box / wall collider.")
    return True, msg


def install_p2g_guard_diagnostic():
    """Patch Solver._update_grid_box so the guard raises with the report above.

    Returns the original method so a caller can restore it. Requires warpmpm, so it is
    only callable where the solver is importable.
    """
    from warpmpm.core.solver import Solver

    original = Solver._update_grid_box

    def patched(self, dt, substeps):
        x = self.x()
        dx = self.grid.dx
        lim = self.grid.grid_lim
        periodic = bool(getattr(self, "periodic_x", False))
        g = x[:, 1:] if periodic else x
        if g.min() < 1.5 * dx or g.max() > lim - 2.5 * dx:
            material = rigid_id = None
            try:
                material = self._sim.mpm_state.particle_material.numpy()
                rigid_id = self._sim.mpm_state.particle_rigid_id.numpy()
            except Exception:
                pass   # the diagnostic degrades to axis-only rather than masking the raise
            _tripped, msg = p2g_guard_report(x, dx, lim, periodic_x=periodic,
                                             material=material, rigid_id=rigid_id)
            raise RuntimeError(msg)
        return original(self, dt, substeps)

    Solver._update_grid_box = patched
    return original


FIX_B_PATCH = (
    'third_party/mpm-engine-544c93dd-solver-core/core/solver.py (and the live copy in\n'
    '$WORK/can-it-ford/mpm-engine on Vista), in _update_grid_box, replace the bare raise\n'
    'at :508-512 with the per-axis + per-material report. This script installs the same\n'
    'behaviour at runtime via install_p2g_guard_diagnostic(), so the vendored copy can\n'
    'stay byte-identical to the pinned SHA that C1_ROOT_CAUSE.md section 0 depends on.'
)


def verify_fix_b_live(n_grid=64, device="auto"):
    """End-to-end Fix B check against the REAL solver, on real particle arrays.

    Builds the rung scene, drives a single RIGID particle below the guard's low z bound,
    and steps once, first unpatched and then patched, capturing both messages. This is
    safe to do and safe to repeat because Solver.step calls _update_grid_box BEFORE any
    state mutation (core/solver.py:429-431, read live), so a trip leaves the particle
    state intact and the same scene can be reused for the second half.

    guard_interval is forced to 1 because step() only consults the guard every
    guard_interval ticks (:430) and the first call has already advanced _tick.
    """
    from warpmpm.core.solver import Solver

    vcf = _load_vcf()
    tank = vcf.BoxTank(n_grid, RHO_BOX, DEPTH_CELLS, 3.0 * DX_CANON, water=True,
                       device=device, seed=0)
    solver = tank.solver
    solver.guard_interval = 1
    dx = solver.grid.dx
    target_z = 1.5 * dx - 0.05          # 0.05 m inside the low bound, unambiguous

    x0 = solver.x().copy()
    idx = tank.n_water                   # first RIGID particle, water occupies [0, n_water)
    material = tank.solver._sim.mpm_state.particle_material.numpy()
    if int(material[idx]) != 8:
        raise RuntimeError(f"expected particle {idx} to be material 8 (rigid), got "
                           f"{int(material[idx])}. BoxTank's particle ordering changed.")

    def trip():
        x = x0.copy()
        x[idx, 2] = target_z
        solver.set_x(x)
        try:
            solver.step(tank.dt, 1)
        except RuntimeError as exc:
            return str(exc)
        finally:
            solver.set_x(x0)
        return None

    before = trip()
    original = install_p2g_guard_diagnostic()
    try:
        after = trip()
    finally:
        Solver._update_grid_box = original

    return {
        "n_grid": n_grid,
        "driven_particle_index": idx,
        "driven_particle_material": int(material[idx]),
        "driven_to_z": target_z,
        "guard_lo_m": 1.5 * dx,
        "both_tripped": bool(before and after),
        "before": before,
        "after": after,
        "patch_reverted": Solver._update_grid_box is original,
    }


def demo_fix_b():
    """Before/after on synthetic particles. No solver, no GPU, no SU."""
    dx = LIM / 64.0
    n_water = 40
    rng = np.random.default_rng(0)
    x = np.column_stack([
        rng.uniform(2.0, 7.0, n_water + 3),
        rng.uniform(2.0, 7.0, n_water + 3),
        rng.uniform(1.0, 3.0, n_water + 3),
    ])
    material = np.zeros(len(x), dtype=np.int64)
    rigid_id = np.full(len(x), -1, dtype=np.int64)
    material[n_water:] = 8
    rigid_id[n_water:] = 0
    # Reproduce C2's observed trip: a RIGID particle low in z, at the value
    # C1_ROOT_CAUSE.md section 8b records for g64.
    x[n_water, 2] = 0.2205
    x[n_water + 1, 2] = 1.30
    x[n_water + 2, 2] = 1.35

    g = x   # periodic_x is never set in these scenes
    before = (f"particles within 2 cells of the grid edge (x in "
              f"[{g.min():.4f}, {g.max():.4f}] m, domain [0, {LIM}] m, dx={dx:.4f}): "
              f"the P2G stencil would write out of bounds. Enlarge grid_lim or add a "
              f"bounding box / wall collider.")
    tripped, after = p2g_guard_report(x, dx, LIM, periodic_x=False,
                                      material=material, rigid_id=rigid_id)
    return {"tripped": tripped, "before": before, "after": after,
            "note": ("`before` is core/solver.py:508-512 verbatim at the pinned SHA. It "
                     "reports a global min over all three axes and labels it 'x'; here "
                     "the true minimum is in Z and the offender is the rigid body."),
            "patch": FIX_B_PATCH}


# --------------------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rung", choices=["b", "c", "d"])
    p.add_argument("--n-grid", type=int, default=64)
    p.add_argument("--rho-box", type=float, default=RHO_BOX)
    p.add_argument("--depth-cells", type=float, default=DEPTH_CELLS)
    p.add_argument("--box-bottom-cells", type=float, default=BOX_BOTTOM_CELLS)
    p.add_argument("--settle-frames", type=int, default=1200)
    p.add_argument("--measure-substeps", type=int, default=160)
    p.add_argument("--flow-frames", type=int, default=60)
    p.add_argument("--velocity", type=float, default=MATCH_VELOCITY)
    p.add_argument("--guard-margin-cells", type=float, default=0.25,
                   help="stop the window this many dx before the P2G edge guard would "
                        "fire, and record that the window was truncated")
    p.add_argument("--device", default="auto")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default=None)
    p.add_argument("--emit-timeseries", default=None, metavar="CSV",
                   help="rung d only: write the surge trace as a classifier-ready CSV "
                        "(FloodHistory.to_csv format), consumable unmodified by "
                        "simulation/failure_modes.classify_timeseries.")
    p.add_argument("--geometry-only", action="store_true",
                   help="print the derived rung geometry and exit; no solver, no GPU")
    p.add_argument("--fix-a", nargs="*", metavar="JSON",
                   help="Fix A: recompute C3's a_as_fraction_of_g from a_late_window for "
                        "each stored result JSON. No solver, no GPU.")
    p.add_argument("--demo-fix-b", action="store_true",
                   help="Fix B: print the guard message before and after. No GPU.")
    p.add_argument("--verify-fix-b-live", action="store_true",
                   help="Fix B: trip the REAL guard on a real rigid particle, unpatched "
                        "then patched, and print both messages. Needs a GPU node.")
    a = p.parse_args()

    if a.geometry_only:
        print(json.dumps(geometry_preview(a.n_grid, a.rho_box, a.depth_cells,
                                          a.box_bottom_cells), indent=2, default=float))
        return
    if a.demo_fix_b:
        d = demo_fix_b()
        print("=== Fix B: BEFORE (core/solver.py:508-512 at the pinned SHA) ===")
        print(d["before"])
        print("\n=== Fix B: AFTER (p2g_guard_report) ===")
        print(d["after"])
        print("\nnote: " + d["note"])
        return
    if a.verify_fix_b_live:
        d = verify_fix_b_live(a.n_grid, a.device)
        print("=== Fix B LIVE: BEFORE (unpatched Solver._update_grid_box) ===")
        print(d["before"])
        print("\n=== Fix B LIVE: AFTER (install_p2g_guard_diagnostic) ===")
        print(d["after"])
        print("\n" + json.dumps({k: v for k, v in d.items()
                                 if k not in ("before", "after")},
                                indent=2, default=float))
        return
    if a.fix_a is not None:
        rows = []
        for path in a.fix_a:
            data = json.loads(Path(path).read_text())
            row = fix_a_recompute(data)
            row["path"] = path
            rows.append(row)
            print(json.dumps(row, indent=2, default=float))
        if not rows:
            print("Fix A, no JSON given. The patch for the owning file is:\n" + FIX_A_PATCH)
        return

    if a.rung is None:
        p.error("--rung is required unless --geometry-only, --fix-a or --demo-fix-b")

    res = run_rung(a.rung, a.n_grid, a.rho_box, a.depth_cells, a.box_bottom_cells,
                   a.settle_frames, a.measure_substeps, a.flow_frames, a.velocity,
                   a.device, a.seed, a.guard_margin_cells)
    vcf = _load_vcf()
    res["provenance"] = dict(vcf.PROVENANCE)
    res["provenance"]["ladder_dispatch"] = "docs/REGIME_LADDER_DISPATCH_2026-08-07.md"
    res["provenance"]["floor_restitution_source"] = (
        "renders/yaris_render_s1/sim_standing.py:132-133 floor restitution=0.05 "
        "friction=0.55; :136 walls restitution=0.05 friction=0.0. Read live 2026-08-07. "
        "This ladder walks restitution only; floor friction stays at BoxTank's 0.0.")
    res["provenance"]["inflow_source"] = (
        "renders/yaris_render_s1/sim_standing.py:190-198 per-frame clamp, :160-162 "
        "one-shot additive kick. Both reproduced; read live 2026-08-07.")
    res["provenance"]["depth_source"] = (
        "data/all_runs_inventory.csv realized_depth_m = 0.2944294473039918 m in all 17 "
        "runs == 2*DX_CANON, so --depth-cells 2 matches it exactly. Read live 2026-08-07.")

    if a.emit_timeseries:
        n = _write_timeseries_csv(res, a.emit_timeseries)
        print(f"wrote timeseries {a.emit_timeseries} ({n} frames), "
              f"classifier-ready: simulation/failure_modes.classify_timeseries")

    print(json.dumps({k: v for k, v in res.items()
                      if k not in ("t_series", "v_series", "zb_series",
                                   "flow_t_series", "flow_com_series",
                                   "flow_vel_series", "flow_omega_series")},
                     indent=2, default=float))
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, indent=2, default=float))
        print(f"wrote {out}")


def geometry_preview(n_grid, rho_box=RHO_BOX, depth_cells=DEPTH_CELLS,
                     box_bottom_cells=BOX_BOTTOM_CELLS):
    """Everything about the rung scene that can be derived without a solver.

    Exists so the geometry claims in the results doc can be checked on a laptop, and so a
    mismatch against data/all_runs_inventory.csv is caught before any SU is spent.
    """
    dx = LIM / n_grid
    h = dx / 2.0
    floor = 3.0 * DX_CANON
    depth = depth_cells * DX_CANON
    z_b0 = floor + box_bottom_cells * DX_CANON
    n_side = int(round(L_BOX / h))
    length = n_side * h
    h_sub = min(depth, length)
    c = math.sqrt(C["GAMMA"] * C["BULK"] / RHO_W)
    substeps = int(math.ceil(max(c / (0.28 * dx),
                                 6.0 * C["ETA"] / (RHO_W * dx * dx),
                                 1.0e-6 / (0.5 * dx)) / FPS))
    dt = (1.0 / FPS) / substeps
    frac = h_sub / length
    return {
        "n_grid": n_grid,
        "grid_lim": LIM,
        "dx": dx,
        "h": h,
        "floor_z": floor,
        "water_depth_m": depth,
        "water_depth_over_dx": depth / dx,
        "water_layers": int(round(depth / h)),
        "box_side_m": length,
        "box_bottom_z": z_b0,
        "box_top_z": z_b0 + length,
        "submerged_height_m": h_sub,
        "submerged_frac": frac,
        "rho_box": rho_box,
        "a_ideal_partial": a_ideal_partial(h_sub, length, rho_box),
        "a_ideal_fully_submerged_for_reference": G * (RHO_W / rho_box - 1.0),
        "substeps_per_frame": substeps,
        "dt": dt,
        "measure_window_s_at_160_substeps": 160 * dt,
        "prediction_v_star_free_rigid": _v_star_prediction(frac, dt),
        "p2g_guard_lo_m": 1.5 * dx,
        "box_bottom_clearance_to_guard_m": z_b0 - 1.5 * dx,
        "matched_gated_run": (MATCH_RUN_G64 if n_grid == 64 else
                              MATCH_RUN_G96 if n_grid == 96 else None),
    }


if __name__ == "__main__":
    main()
