"""Free overfall in a rectangular channel: the external validation case.

WHY THIS SCENE. Every result in this project so far has been checked against
itself. Zhao et al 2019 chose the free overfall as the stringent test of their
in/outflow BCs precisely because the bed level drops suddenly, and they report the
end-depth ratio against Rouse, who found the critical depth is about 1.4x the
brink depth. That ratio is the only EXTERNAL, quantitative target currently in
hand for this pipeline, so it is the one thing here that can fail for a reason
outside the code.

THE TWO MEASUREMENTS ARE INDEPENDENT, which is the whole point:
  y_b  brink depth, read off the free surface at the brink section.
  y_c  critical depth = (q^2/g)^(1/3), with q taken from the RECYCLING FLUX,
       i.e. particles caught below the brink per second times h^3, divided by the
       channel width. It never touches the free surface.
A ratio built from one surface measurement and one flux measurement can be wrong;
a ratio built from the surface twice cannot fail.

GEOMETRY. warpmpm's add_plane is an INFINITE plane, so it cannot express a bed
that stops. The bed here is an add_box collider (solver.py:224), documented as a
"volumetric grid-node velocity overwrite", spanning x in [0, x_brink] with its top
face at bed_top. That makes the bed NO-SLIP rather than the slip plane the
canonical scene uses, which is stated in the summary and is closer to a real
channel anyway. There is no floor plane in this scene at all: past the brink there
is nothing to stand on, which is what a free overfall is.

DOMAIN. Deliberately NOT the Yaris-derived 9.42 m box. This scene holds no
vehicle, so the domain is sized for the flow: lim 4.0 m at n_grid 64 gives
dx 0.0625 and h 0.03125, so a 0.30 m depth is about 10 particle layers rather than
the canonical 4. That is the "roughly 10 particles per flow depth" rule of thumb
recorded as L-3, met here for the first time in this project.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from warpmpm.core.solver import GridConfig, Solver      # noqa: E402
from warpmpm.materials import newtonian                 # noqa: E402

from openchannel_bc import (                            # noqa: E402
    OverfallBC, discharge_per_width, overfall_metrics, tilted_gravity,
)



def _box_mesh(half):
    """Axis-aligned box centred on the origin: 8 verts, 12 outward-wound triangles.

    Built by hand rather than via trimesh so the bed geometry is deterministic and
    has no dependency on the trimesh version, which is version-split on this project
    for seeded operations.
    """
    hx, hy, hz = half
    v = np.array([[-hx, -hy, -hz], [hx, -hy, -hz], [hx, hy, -hz], [-hx, hy, -hz],
                  [-hx, -hy, hz], [hx, -hy, hz], [hx, hy, hz], [-hx, hy, hz]], float)
    f = np.array([[0, 2, 1], [0, 3, 2],           # bottom  (-z)
                  [4, 5, 6], [4, 6, 7],           # top     (+z)
                  [0, 1, 5], [0, 5, 4],           # -y
                  [2, 3, 7], [2, 7, 6],           # +y
                  [1, 2, 6], [1, 6, 5],           # +x
                  [3, 0, 4], [3, 4, 7]], np.int32)  # -x
    return v, f


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--depth", type=float, default=0.30)
    p.add_argument("--velocity", type=float, default=1.0)
    p.add_argument("--frames", type=int, default=240)
    p.add_argument("--grid", type=int, default=64)
    p.add_argument("--lim", type=float, default=4.0)
    p.add_argument("--bed-top", type=float, default=1.5)
    p.add_argument("--brink-frac", type=float, default=0.65,
                   help="brink position as a fraction of lim")
    p.add_argument("--fall", type=float, default=0.6, help="catch depth below the bed")
    p.add_argument("--eta", type=float, default=1.0e-3)
    p.add_argument("--bulk", type=float, default=1.5e5)
    p.add_argument("--grade-deg", type=float, default=0.0)
    p.add_argument("--width", type=float, default=None,
                   help="channel width in m; default is the full domain minus walls")
    p.add_argument("--head-len", type=float, default=0.0,
                   help="length of the sustained upstream velocity band, m (0=off)")
    p.add_argument("--bed", choices=("box", "sdf"), default="sdf",
                   help="box = add_box velocity overwrite (register 25b, drains); "
                        "sdf = add_sdf_collider surface contact")
    p.add_argument("--bed-friction", type=float, default=0.4)
    p.add_argument("--bed-res", type=int, default=128)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()

    lim = float(a.lim)
    grid = GridConfig(n_grid=a.grid, grid_lim=lim)
    dx = grid.dx
    h = dx / 2.0                      # 8 particles per cell, Zhao et al's 8 PPE
    wall = 4.0 * dx
    bed_top = float(a.bed_top)
    x_brink = float(a.brink_frac) * lim
    catch_z = bed_top - float(a.fall)
    fps = 30
    rng = np.random.default_rng(a.seed)

    # A narrower channel costs far fewer particles for the same depth resolution,
    # and the grid is forced cubic so the domain cannot simply be made thin.
    y_lo = wall if a.width is None else 0.5 * (lim - float(a.width))
    y_hi = lim - wall if a.width is None else 0.5 * (lim + float(a.width))
    xs = np.arange(wall + 0.5 * h, x_brink - 0.5 * h, h)
    ys = np.arange(y_lo + 0.5 * h, y_hi - 0.5 * h, h)
    zs = np.arange(bed_top + 0.5 * h, bed_top + a.depth, h)
    water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
    water = (water + rng.uniform(-0.2 * h, 0.2 * h, water.shape)).astype(np.float32)
    n_water = len(water)
    vol = np.full(n_water, h ** 3, dtype=np.float32)

    width = y_hi - y_lo
    s = Solver(grid=grid).load_particles(water, vol)
    if s.sort_interval != 0:
        raise RuntimeError("sort_interval must be 0; water is addressed by index range")
    gravity = tilted_gravity(a.grade_deg)
    s.set_material(newtonian(eta=a.eta, density=1000.0, bulk_modulus=a.bulk), g=gravity)

    # THE BED. No floor plane anywhere in this scene: past the brink there is
    # nothing to stand on, which is what a free overfall is.
    #
    # add_box was the first choice and it is WRONG for this, measured not guessed.
    # Its own docstring says "volumetric grid-node velocity overwrite ... for
    # oriented surface contact with friction modes use add_sdf_collider", and the
    # measurement agrees: with the box bed, n_sunk averaged 52000 to 62000 of 94656
    # water particles PER FRAME and the channel collapsed to a film, because a
    # velocity sink supplies no normal support. Register item 25b.
    #
    # The SDF path is the one this project has already validated: register A-2 puts
    # C1-SDF buoyancy within 7.3 to 7.7 percent of analytic.
    bed_h = 0.40
    bed_cy = 0.5 * (y_lo + y_hi)
    bed_hy = 0.5 * (y_hi - y_lo) + 3.0 * dx
    if a.bed == "sdf":
        from warpmpm.geometry import build_sdf
        bv, bf = _box_mesh((0.5 * x_brink, bed_hy, 0.5 * bed_h))
        bed_sdf = build_sdf(bv, bf, res=int(a.bed_res), margin_cells=4.0)
        s.add_sdf_collider(bed_sdf,
                           center=(0.5 * x_brink, bed_cy, bed_top - 0.5 * bed_h),
                           surface="separable", friction=float(a.bed_friction))
    else:
        s.add_box(center=(0.5 * x_brink, bed_cy, bed_top - 0.5 * bed_h),
                  half_size=(0.5 * x_brink, bed_hy, 0.5 * bed_h),
                  velocity=(0.0, 0.0, 0.0))
    for pt, nrm in (((0, y_lo, 0), (0, 1, 0)), ((0, y_hi, 0), (0, -1, 0))):
        s.add_plane(pt, nrm, "slip", friction=0.0, restitution=0.05)
    s.add_domain_walls()

    c = float(np.sqrt(1.1 * a.bulk / 1000.0))
    v_fall = float(np.sqrt(2.0 * 9.81 * a.fall))
    v_ref = max(a.velocity, v_fall)
    rate = max(c / (0.28 * dx), 6.0e-3 / (1000.0 * dx * dx), v_ref / (0.5 * dx))
    substeps = int(np.ceil(rate / fps))
    dt = (1.0 / fps) / substeps

    head_len = float(a.head_len)
    bc = OverfallBC(n_water=n_water, x_in=wall, catch_z=catch_z, bed_top=bed_top,
                    inlet_velocity=a.velocity, dx=dx, grid_lim=lim, x_brink=x_brink,
                    seed=a.seed)

    print("SCENARIO=FREE_OVERFALL", flush=True)
    print("INSTRUMENT lim=%.4f dx=%.6f h=%.6f bed_top=%.4f x_brink=%.4f catch_z=%.4f"
          % (lim, dx, h, bed_top, x_brink, catch_z), flush=True)
    print("INSTRUMENT n_water=%d width=%.4f depth_layers=%d ppc=8"
          % (n_water, width, len(zs)), flush=True)
    print("INSTRUMENT c=%.4f substeps=%d dt=%.3e mach_margin_vs_fall=%.2f"
          % (c, substeps, dt, c / v_fall), flush=True)

    for _ in range(8):
        s.step(dt, substeps)
    v = s.v(); v[:, 0] += a.velocity; s.set_v(v)

    n_sunk_total = 0
    rows = ["frame,n_caught,q_m2_s,y_b,y_c,ratio,froude_up,reinject_depth,n_sunk,n_head"]
    for f in range(a.frames):
        x = s.x(); vv = s.v()
        # SUSTAINED HEAD. Injecting at the inlet only sets a recycled particle's
        # velocity once; nothing then drives the channel, so on a horizontal bed the
        # flow decelerates under bed friction and the discharge dies. Measured on the
        # first SDF-bed runs: q fell 0.043 to 0.008 m2/s over 300 frames while the
        # brink depth held, i.e. the channel filled and stopped.
        # Rouse's overfall is fed from a constant-head tank. The analogue here is a
        # sustained upstream velocity band, which is also what the canonical driver's
        # _sustain_inflow does. It is a momentum source, not a mass source, and it is
        # applied ONLY upstream of head_len so the brink section stays unforced.
        if head_len > 0.0:
            band = x[:n_water, 0] < (wall + head_len)
            vv[:n_water][band, 0] = a.velocity
            n_head = int(band.sum())
        else:
            n_head = 0
        n = bc.apply(x, vv)
        if n:
            s.set_x(x); s.set_v(vv)
        # cross-stream containment only; there is no streamwise clamp anywhere
        bc.project_cross_stream(x, vv, y_lo=y_lo, y_hi=y_hi, z_floor=0.0)
        # BED CONTAINMENT. add_box zeroes grid velocity inside the bed but applies
        # no restoring force, so a particle that drifts in is trapped for the rest
        # of the run and the channel bleeds water into its own bed. Measured, not
        # assumed: this is what drained the first three overfall runs.
        w_ = x[:n_water]
        sunk = (w_[:, 0] <= x_brink) & (w_[:, 2] < bed_top)
        n_sunk = int(sunk.sum())
        n_sunk_total += n_sunk
        if n_sunk:
            w_[sunk, 2] = bed_top
            vv[:n_water][sunk, 2] = np.maximum(vv[:n_water][sunk, 2], 0.0)
        s.set_x(x); s.set_v(vv)
        s.step(dt, substeps)
        w = s.x()
        q = discharge_per_width(n, fps, h, width)
        y_b, y_c, ratio, fr = overfall_metrics(w, bed_top, x_brink, dx, width, q)
        rows.append("%d,%d,%.8f,%s,%s,%s,%s,%.5f" % (
            f, n, q,
            "" if not np.isfinite(y_b) else "%.6f" % y_b,
            "" if not np.isfinite(y_c) else "%.6f" % y_c,
            "" if not np.isfinite(ratio) else "%.6f" % ratio,
            "" if not np.isfinite(fr) else "%.6f" % fr,
            bc.reinject_depth_last) + ",%d,%d" % (n_sunk, n_head))
        if f % 20 == 0 or f == a.frames - 1:
            print("frame %3d caught=%4d q=%.5f y_b=%s y_c=%s ratio=%s Fr=%s"
                  % (f, n, q,
                     "nan" if not np.isfinite(y_b) else "%.4f" % y_b,
                     "nan" if not np.isfinite(y_c) else "%.4f" % y_c,
                     "nan" if not np.isfinite(ratio) else "%.3f" % ratio,
                     "nan" if not np.isfinite(fr) else "%.3f" % fr), flush=True)

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "overfall.csv").write_text("\n".join(rows) + "\n")
    summary = {
        "scenario": "free_overfall", "label": a.label,
        "rouse_target_yc_over_yb": 1.4,
        "rouse_source": ("Zhao et al 2019 doi:10.1016/j.compfluid.2018.10.007, their own "
                         "text via Scite full-text search 2026-08-18, quoting Rouse: the "
                         "computed critical depth is about 1.4 times the brink depth"),
        "lim": lim, "n_grid": a.grid, "dx": float(dx), "h": float(h),
        "bed_top": bed_top, "x_brink": float(x_brink), "catch_z": float(catch_z),
        "channel_width_m": float(width),
        "y_lo": float(y_lo), "y_hi": float(y_hi), "depth_nominal_m": a.depth,
        "depth_layers": int(len(zs)), "particles_per_cell": 8,
        "inlet_velocity_ms": a.velocity, "frames": a.frames, "n_water": int(n_water),
        "bulk_modulus": float(a.bulk), "sound_speed_ms": c,
        "substeps": int(substeps), "dt": float(dt),
        "grade_deg": a.grade_deg, "gravity": gravity,
        "head_len_m": head_len,
        "bed_kind": a.bed, "bed_friction": float(a.bed_friction),
        "bed_res": int(a.bed_res), "bed_thickness_m": 0.40,
        "recycled_total": int(bc.recycled_total),
        "clamped_y": int(bc.clamped_y), "clamped_z": int(bc.clamped_z),
        "bed_reentry_particle_frames": int(n_sunk_total),
        "water_count_conserved": bool(len(s.x()) == n_water),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY " + json.dumps(summary), flush=True)
    print("DONE %s" % a.label, flush=True)


if __name__ == "__main__":
    main()
