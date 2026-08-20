#!/usr/bin/env python3
"""Turn one frame of a moving-vehicle FRAMES_*.npz into a Cycles scene directory.

    prep_cycles_frames.py --npz FRAMES_x.npz --frame N --hull h.ply --outdir DIR

WHY A SEPARATE ENTRY POINT. prep_cycles_scene.py reads the canonical `rollout.npz`
layout, where the vehicle is a stationary-start rigid body with a stored rotation and
a solidified particle cloud to fit the hull against. The moving-vehicle runs write a
different and smaller record: `water_xyz`, `hull_center` per frame, `hull_extent_m`,
and the scalars. Rather than branch the canonical reader and risk the 17 gated runs,
this adapter writes the SAME on-disk scene directory that cycles_render.py already
consumes, and reuses prep_cycles_scene's water reconstruction unchanged.

WHAT THIS DATA FIXES, and it is three things at once. The canonical g64 runs have a
9.42 m domain against a camera that sees about 5.7 m, so the water ends inside the
frame and everything downstream of that was scaffolding: the flat presentational
surround, its edge taper, and the visible patch rectangle. These runs have
**lim_m 22.0 at a FINER dx, 0.1375 against 0.1472**, so the water exceeds the frame by
roughly 4x and none of that scaffolding is needed.

THE ONE THING THIS RECORD CANNOT SUPPORT, stated because a render is persuasive.
`hull_center` is a POSITION and there is no rotation in the file. So the hull is
translated along the run's own path and never rotated, and no frame from this data may
be read as showing pitch, roll, yaw or any rotational response. If the vehicle in the
simulation rotated, this render does not show it. The caption must say so.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prep_cycles_scene import (write_ply, read_ply_vertices_faces, water_surface,
                               still_water_level, ROTZ)                # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True)
    ap.add_argument("--frame", type=int, default=50)
    ap.add_argument("--hull", required=True, help="hull .ply, READ not copied")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--half", type=float, default=7.0,
                    help="half-width of the reconstruction window. Larger than the "
                         "canonical 4.2 because the point of this data is a domain "
                         "bigger than the frame.")
    ap.add_argument("--cube-mult", type=float, default=0.40)
    ap.add_argument("--smooth-mult", type=float, default=2.0)
    ap.add_argument("--smooth-iters", type=int, default=25)
    ap.add_argument("--iso", type=float, default=0.6)
    ap.add_argument("--edge-taper", type=float, default=0.0,
                    help="0 by default and that is the point: the taper existed to "
                         "hide a patch edge inside the frame, and with a 22 m domain "
                         "the edge is outside it.")
    a = ap.parse_args()

    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    z = np.load(a.npz)
    f = a.frame
    w = np.asarray(z["water_xyz"][f], dtype=np.float64)
    hc = np.asarray(z["hull_center"][f], dtype=np.float64)
    ext = np.asarray(z["hull_extent_m"], dtype=np.float64)
    dx = float(z["dx_m"])
    h = dx / 2.0
    floor = float(z["floor_z_m"])
    lim = float(z["lim_m"])
    nframes = int(z["water_xyz"].shape[0])

    print("[frames] %s frame %d of %d" % (Path(a.npz).name, f, nframes))
    print("[frames] lim %.3f m, dx %.5f m, floor %.4f m, %d water particles, "
          "v_car %.2f m/s, v_water %.2f m/s"
          % (lim, dx, floor, len(w), float(z["v_car_ms"]), float(z["v_water_ms"])))

    # ---- hull: TRANSLATED ONLY. There is no rotation in this record. ----------
    P, HF = read_ply_vertices_faces(Path(a.hull))
    Q = P @ ROTZ["+90"].T                       # long axis onto Y, scene convention
    c = 0.5 * (Q.min(0) + Q.max(0))
    Q = Q - c + hc
    # Seat it on the floor rather than trusting hull_center's z, which is the body
    # centre in a record that does not say where the underside is.
    Q[:, 2] += floor - Q[:, 2].min()
    write_ply(out / "hull.ply", Q, HF)
    print("[frames] hull %s: %d verts, TRANSLATED to hull_center (%.3f, %.3f), "
          "seated on the floor. NO ROTATION IS STORED IN THIS RECORD, so none is "
          "applied and no rotational response may be read from the frame."
          % (Path(a.hull).name, len(Q), hc[0], hc[1]))
    print("[frames] hull extent from file %s, placed mesh %s"
          % (np.round(ext, 3), np.round(Q.max(0) - Q.min(0), 3)))

    cx, cy = float(hc[0]), float(hc[1])
    window = (cx - a.half, cx + a.half, cy - a.half, cy + a.half)
    swl, ncol = still_water_level(w, cx, cy, h)
    print("[frames] still-water level %.4f m, median of %d column maxima beyond "
          "3.2 m from the vehicle (%.4f m of water over the floor)"
          % (swl, ncol, swl - floor))

    WV, WF, kept, tot, wrect, surz = water_surface(
        w, h, window, a.cube_mult, a.iso, a.smooth_mult, a.smooth_iters, floor,
        a.edge_taper, Q.min(0), Q.max(0))
    write_ply(out / "water.ply", WV, WF)
    print("[frames] water surface: %d verts %d tris from %d of %d particles"
          % (len(WV), len(WF), kept, tot))

    margin = min(cx - (0.0), lim - cx, cy - 0.0, lim - cy)
    print("[frames] the reconstruction window is %.1f m across inside a %.1f m "
          "domain, and the nearest domain wall is %.1f m from the vehicle"
          % (2 * a.half, lim, margin))

    scene = {
        "run": Path(a.npz).stem, "frame": f, "fps": int(z["fps_nominal"]),
        "floor_z": floor, "dx": dx, "h": h,
        "hull_ply_source": str(a.hull), "hull_rotation": "+90 (translation only)",
        "hull_faces": int(len(HF)), "water_faces": int(len(WF)),
        "car_center": [cx, cy], "half": a.half,
        "still_water_z": swl, "still_water_columns": ncol,
        "water_rect": [float(v) for v in wrect], "surround_z": float(surz),
        "edge_taper_m": float(a.edge_taper),
        "domain_lim_m": lim,
        "NO_ROTATION_STORED": True,
        "physics": {
            "mass_kg": None, "n_grid": 160, "dx": dx, "water_layers": 4,
            "depth_m": float(z["depth_m"]), "velocity_ms": float(z["v_water_ms"]),
            "v_car_ms": float(z["v_car_ms"]), "label": "moving_vehicle_g160",
        },
    }
    (out / "scene.json").write_text(json.dumps(scene, indent=2))
    print("[frames] wrote %s" % (out / "scene.json"))


if __name__ == "__main__":
    main()
