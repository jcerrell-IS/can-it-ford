"""Does periodic conveyance beat the filling tank on the assessment's own metric?

THE CONTROLLED COMPARISON
-------------------------
Two arms, IDENTICAL in every respect except the downstream boundary:

  tank      closed downstream wall. This is the canonical behaviour, and it is what
            produces the measured 2.5x pile-up (0.2729 -> 0.6750 m at the wall by
            mid-run) and the 22 percent depth-hold score.
  channel   ChannelRecycler: streamwise periodic wrap + Zhao velocity relaxation at the
            inlet.

Both arms get the SAME upstream velocity forcing, so the only difference is where the
water goes when it gets to the far end. Anything the channel arm wins is attributable to
the outlet and to nothing else.

THE METRIC IS NOT NEW
---------------------
`depth_hold_fraction` reproduces the assessment's criterion exactly: fraction of frames
within +/-10 percent of the nominal depth. The canonical scene scores 20 of 90 = 22
percent. That is the number to beat, and inventing a friendlier criterion alongside the
fix would make the comparison meaningless.

RESOLUTION NOTE
---------------
warpmpm's domain is cubic: `GridConfig(n_grid, grid_lim)` takes a single scalar, so a
channel cannot be made long in x alone. Resolution is therefore improved by shrinking the
domain rather than by stretching it. At lim = 3.0 and n_grid = 64, dx = 0.046875 m, so a
0.30 m depth spans 6.4 cells and 12 particle layers, against the canonical baseline of
**2.000 cells and 4 layers** (register B1, CLAUDE.md L-3). That clears the `H/dp >= 5`
wave-capture minimum which the canonical runs do not.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from open_channel import ChannelRecycler, depth_hold_fraction, water_depth_at  # noqa: E402
from outflow_deactivate import DepthControlledOutflow, active_depth_at  # noqa: E402

RHO_W = 1000.0
G = 9.81
BULK = 9.0e5
ETA = 1.0e-3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm",
                    choices=["tank", "channel", "outflow_sink", "outflow_pair"],
                    required=True,
                    help="tank/channel are the two arms already run and scored. "
                         "outflow_sink is register B7 as literally written, a "
                         "depth-controlled deactivation outflow with NO source, which is "
                         "expected to drain and is run to show what the prescription "
                         "alone does. outflow_pair adds the depth-controlled inlet that "
                         "makes it a closed in/outflow pair.")
    ap.add_argument("--n-grid", type=int, default=64)
    ap.add_argument("--lim", type=float, default=3.0)
    ap.add_argument("--depth", type=float, default=0.30)
    ap.add_argument("--u", type=float, default=1.5, help="target streamwise velocity m/s")
    ap.add_argument("--frames", type=int, default=90)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--cfl", type=float, default=0.4)
    ap.add_argument("--relax-gain", type=float, default=0.5)
    ap.add_argument("--sponge-gain", type=float, default=0.0,
                    help="downstream absorption; 0 reproduces the naive wrap")
    ap.add_argument("--out", default="channel_result.json")
    args = ap.parse_args()

    from warpmpm.core.solver import Solver, GridConfig
    from warpmpm.materials import newtonian

    lim, n_grid = float(args.lim), int(args.n_grid)
    dx = lim / n_grid
    h = dx / 2.0
    wall = 4.0 * dx
    floor = wall

    nxy = int(math.floor((lim - 2 * wall) / h))
    nz = int(math.floor(args.depth / h))
    lo = 0.5 * lim - 0.5 * (nxy * h)
    ax = lo + h * (0.5 + np.arange(nxy))
    az = floor + h * (0.5 + np.arange(nz))
    X, Y, Z = np.meshgrid(ax, ax, az, indexing="ij")
    pos = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1).astype(np.float32)
    vol = np.full(len(pos), h ** 3, dtype=np.float32)
    n_water = len(pos)

    c = math.sqrt(1.1 * BULK / RHO_W)
    dt = args.cfl * dx / c
    substeps = int(math.ceil((1.0 / args.fps) / dt))
    dt = (1.0 / args.fps) / substeps

    s = Solver(grid=GridConfig(n_grid=n_grid, grid_lim=lim), device="cuda:0")
    s.load_particles(pos, vol)
    s.set_material(newtonian(eta=ETA, density=RHO_W, bulk_modulus=BULK))
    s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=0.0, restitution=0.0)
    for pt, nrm in (((0, wall, 0), (0, 1, 0)), ((0, lim - wall, 0), (0, -1, 0))):
        s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.0)
    # upstream wall exists in BOTH arms; the downstream wall only in the tank arm,
    # which is the single difference under test.
    s.add_plane((wall, 0, 0), (1, 0, 0), "slip", friction=0.0, restitution=0.0)
    if args.arm == "tank":
        s.add_plane((lim - wall, 0, 0), (-1, 0, 0), "slip", friction=0.0, restitution=0.0)
    s.add_domain_walls()

    x_in = float(ax.min() - 0.5 * h)
    x_out = float(ax.max() + 0.5 * h)

    outflow = None
    if args.arm in ("outflow_sink", "outflow_pair"):
        outflow = DepthControlledOutflow(
            s, n_water, x_in, x_out, floor, args.depth, args.u, h,
            mode="sink_only" if args.arm == "outflow_sink" else "sink_source",
            relax_len=0.25 * (x_out - x_in), relax_gain=args.relax_gain)
        forcing = outflow
    else:
        rec = ChannelRecycler(s, n_water, x_in, x_out, args.u,
                              relax_gain=args.relax_gain,
                              sponge_gain=args.sponge_gain) if args.arm == "channel" else None
        # Both arms get the same upstream forcing: the inlet relaxation band. In the tank
        # arm it is applied without any wrap, which is the canonical Dirichlet-slab setup.
        forcing = ChannelRecycler(s, n_water, x_in, x_out, args.u,
                                  relax_len=0.25 * (x_out - x_in),
                                  relax_gain=args.relax_gain, wrap=False) if rec is None else rec

    probe_x = 0.5 * lim
    probe_y = 0.5 * lim
    half_win = 3.0 * h

    print(json.dumps({"setup": {
        "arm": args.arm, "n_grid": n_grid, "lim": lim, "dx": dx, "h": h,
        "n_water": n_water, "depth_nominal": args.depth,
        "depth_over_dx": args.depth / dx, "water_layers": nz,
        "canonical_depth_over_dx": 2.000, "canonical_water_layers": 4,
        "dt_sub": dt, "substeps_per_frame": substeps, "u_target": args.u,
        "x_in": x_in, "x_out": x_out,
        "reach_over_nothing_m": x_out - x_in,
    }}, indent=2), flush=True)

    depths, wall_depths, hist = [], [], []
    t0 = time.time()
    all_active = np.ones(n_water, dtype=bool)
    for f in range(args.frames):
        s.step(dt, substeps)
        forcing.apply()
        # Mask on the ACTIVE set. Deactivated particles are frozen where they died, which
        # is at the top of the column by construction, so an unmasked percentile would
        # keep reporting the free surface this boundary condition has just removed. For
        # tank and channel the mask is all-True and this is identical to the
        # `water_depth_at` used before, which the tank control arm re-verifies.
        act = outflow.active_mask() if outflow is not None else all_active
        xs_now = s.x()[:n_water]
        d = active_depth_at(xs_now, act, probe_x, probe_y, half_win, floor, h)
        dw = active_depth_at(xs_now, act, x_out - 4 * h, probe_y, half_win, floor, h)
        depths.append(d)
        wall_depths.append(dw)
        hist.append({"frame": f, "depth_mid": d, "depth_downstream": dw,
                     "n_active": int(act.sum())})
        if f % 10 == 0:
            extra = (f"kill={forcing.n_deactivated_total} act={forcing.n_activated_total} "
                     f"live={int(act.sum())}" if outflow is not None
                     else f"wrapped={getattr(forcing, 'n_wrapped_total', 0)}")
            print(f"  frame {f:4d}  mid={d:.4f} m  downstream={dw:.4f} m  {extra}",
                  flush=True)

    frac, n_ok, n_tot = depth_hold_fraction(depths, args.depth, tol=0.10)
    dw_arr = np.asarray(wall_depths)
    out = {
        "arm": args.arm, "wall_s": time.time() - t0,
        "depth_hold_fraction": frac, "frames_within_10pct": n_ok, "frames_total": n_tot,
        "canonical_baseline": {"fraction": 20 / 90, "frames_within": 20, "frames_total": 90,
                               "source": "REALISM_UPGRADE_ASSESSMENT_2026-08-08 section 4"},
        "mid_depth": {"min": float(np.min(depths)), "max": float(np.max(depths)),
                      "mean": float(np.mean(depths)),
                      "excursion_pct": [100 * (np.min(depths) - args.depth) / args.depth,
                                        100 * (np.max(depths) - args.depth) / args.depth]},
        "downstream_depth": {"first": float(dw_arr[0]), "max": float(dw_arr.max()),
                             "last": float(dw_arr[-1]),
                             "pileup_ratio": float(dw_arr.max() / max(dw_arr[0], 1e-9))},
        "n_wrapped_total": int(getattr(forcing, "n_wrapped_total", 0)),
        "n_deactivated_total": int(getattr(forcing, "n_deactivated_total", 0)),
        "n_activated_total": int(getattr(forcing, "n_activated_total", 0)),
        "n_active_final": int((outflow.active_mask().sum()) if outflow else n_water),
        "water_retained_frac": float((outflow.active_mask().sum() / n_water)
                                     if outflow else 1.0),
        "V_water_initial_m3": n_water * h ** 3,
        "V_water_final_m3": float(outflow.water_volume()) if outflow else n_water * h ** 3,
        "sponge_gain": args.sponge_gain, "relax_gain": args.relax_gain,
        "resolution": {"depth_over_dx": args.depth / dx, "water_layers": nz,
                       "canonical_depth_over_dx": 2.000, "canonical_water_layers": 4},
        "history": hist,
    }
    print("\n=== RESULT ===")
    print(json.dumps({k: v for k, v in out.items() if k != "history"}, indent=2))
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
