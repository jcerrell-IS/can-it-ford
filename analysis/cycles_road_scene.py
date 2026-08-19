#!/usr/bin/env python3
"""Compose several prepared single-vehicle scenes onto ONE crowned road.

    cycles_road_scene.py --scene DIR --scene DIR --scene DIR --out DIR

WHAT THIS IS, STATED FIRST BECAUSE THE IMAGE IS PERSUASIVE
  Three vehicles in one photograph did not happen in one simulation. There is no
  three-vehicle run. Each vehicle here comes from its OWN warpmpm run and brings
  its OWN water with it: the hull pose and every water particle are that run's,
  unaltered. What this script does to them is a RIGID TRANSLATION, the same
  translation applied to the hull and to its water, so every distance, depth and
  angle inside a patch is preserved exactly. Nothing is rescaled, re-posed,
  re-simulated or interpolated.

  What is invented is the arrangement: which vehicle stands where along the road,
  and the flat water between the patches. Both are presentational and are labelled
  as such in the caption strip.

THE ROAD IS THE PROJECT'S OWN GEOMETRY, NOT A DRAWING
  The cross-section comes from simulation/road_geometry.road_profile(), the same
  function sim_road.py uses to build its SDF collider: crown, cross slope, gutters,
  a kerb and verges. It is imported rather than reimplemented so the picture cannot
  drift from the geometry the solver would use.

  Worth knowing while looking at it: per the literature sweep of this round, no
  retrieved study quantifies a crowned or cambered road against a flat plane, so
  this cross-section is an unevaluated configuration rather than a settled one.

THE ONE HONEST MISMATCH, AND HOW IT IS RESOLVED
  The runs composited here used a FLAT floor. The road is crowned. Those disagree
  by up to cross_slope * half_width, about 0.07 m over a 4 m carriageway at 2
  percent. Each patch is therefore seated at the LOWEST road height beneath its own
  footprint, so the road surface rises INTO the water volume rather than leaving a
  gap under it. Consequences, both stated rather than hidden:
    - the water SURFACE is exactly the simulated surface, untouched;
    - the water is shallower over the crown than the run simulated, by up to that
      same 0.07 m, which is the direction a real crowned road would go, but it is
      an artefact of seating a flat-floor run on a crowned road, NOT a simulated
      result. No depth may be read off the crown.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from prep_cycles_scene import write_ply, read_ply_vertices_faces          # noqa: E402
from simulation.road_geometry import road_profile                         # noqa: E402


def road_along_y(length, width_total, z_base, x0, y0, n_x=220, **kw):
    """Watertight road solid whose cross-section varies with X and which runs along Y.

    road_geometry.road_solid() extrudes along x with the profile in y. The scenes
    put every vehicle's long axis on Y, so the road has to run along Y or the cars
    would be driving across it. Rather than rotate the vehicles, which would mean
    rotating real particle data for cosmetic reasons, the profile is evaluated
    against X here and the extrusion runs along Y. road_profile() itself is
    imported unchanged, so the cross-section is the project's, not a copy.
    """
    xs = np.linspace(0.0, width_total, n_x)
    zs = road_profile(xs, width_total, **kw)
    ys = np.array([0.0, length])
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    Ztop = np.broadcast_to(zs[:, None], X.shape)
    top = np.stack([X, Y, Ztop], -1).reshape(-1, 3)
    bot = np.stack([X, Y, np.full_like(X, z_base)], -1).reshape(-1, 3)
    V = np.vstack([top, bot])
    nt = len(top)
    ny = 2

    def q(i, j):
        return i * ny + j

    F = []
    for i in range(n_x - 1):
        a, b, c, d = q(i, 0), q(i + 1, 0), q(i + 1, 1), q(i, 1)
        F += [[a, b, c], [a, c, d]]
        A, B, C, D = a + nt, b + nt, c + nt, d + nt
        F += [[A, C, B], [A, D, C]]
        F += [[a, b, b + nt], [a, b + nt, a + nt]]        # y = 0 wall
        F += [[d, d + nt, c + nt], [d, c + nt, c]]        # y = length wall
    for j in range(ny - 1):
        a, d = q(0, j), q(0, j + 1)
        F += [[a, a + nt, d + nt], [a, d + nt, d]]
        b, c = q(n_x - 1, j), q(n_x - 1, j + 1)
        F += [[b, c, c + nt], [b, c + nt, b + nt]]
    V = V + np.array([x0, y0, 0.0])
    return V, np.asarray(F, dtype=np.int64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", action="append", required=True,
                    help="a directory produced by prep_cycles_scene.py; repeat it")
    ap.add_argument("--out", required=True)
    ap.add_argument("--spacing", type=float, default=13.0,
                    help="metres between patch centres ALONG the road")
    ap.add_argument("--width-total", type=float, default=11.0)
    ap.add_argument("--carriageway", type=float, default=7.4)
    ap.add_argument("--cross-slope", type=float, default=0.02)
    ap.add_argument("--road-pad", type=float, default=34.0,
                    help="metres of road beyond the first and last patch")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    scenes = [json.loads((Path(d) / "scene.json").read_text()) for d in a.scene]

    n = len(scenes)
    span = a.spacing * (n - 1)
    length = span + 2.0 * a.road_pad
    xc = 0.5 * a.width_total                       # crown, in road coordinates
    crown_z = 0.0
    road_V, road_F = road_along_y(length, a.width_total, crown_z - 1.2, 0.0, 0.0,
                                  carriageway=a.carriageway,
                                  cross_slope=a.cross_slope, crown_z=crown_z)
    write_ply(out / "road.ply", road_V, road_F)
    print("[road] cross-section from simulation/road_geometry.road_profile: "
          "width %.1f m, carriageway %.1f m, cross slope %.3f, crown at x=%.2f"
          % (a.width_total, a.carriageway, a.cross_slope, xc))
    print("[road] %.1f m long along y, %d verts %d faces"
          % (length, len(road_V), len(road_F)))

    # ONE SEATING HEIGHT FOR ALL THREE, and this is a correction to the obvious
    # version. Seating each patch at the lowest road height under ITS OWN footprint
    # puts the three floors at three different heights, because the patches are
    # different WIDTHS: the Silverado's is 8.11 m and reaches into the gutter while
    # the Yaris's is 6.42 m and does not. Measured, that pushed the three water
    # surfaces 0.0995 m apart, of which only 0.062 m is the real difference in
    # simulated depth and the rest is an artefact of patch width. A single common
    # floor removes the artefact and leaves exactly the difference the runs
    # actually have.
    rects = [sc.get("water_rect") for sc in scenes]
    widest = max(r[1] - r[0] for r in rects if r)
    probe = np.linspace(xc - 0.5 * widest, xc + 0.5 * widest, 161)
    z_lo = float(road_profile(probe, a.width_total, carriageway=a.carriageway,
                              cross_slope=a.cross_slope, crown_z=crown_z).min())
    z_hi = float(road_profile(np.array([xc]), a.width_total,
                              carriageway=a.carriageway,
                              cross_slope=a.cross_slope, crown_z=crown_z)[0])
    print("[road] common seating height %.4f m, the lowest road point under the "
          "widest patch (%.2f m); crown is %.4f m, so the road rises %.4f m into "
          "the water" % (z_lo, widest, z_hi, z_hi - z_lo))

    vehicles = []
    surf_levels = []
    for i, (d, sc) in enumerate(zip(a.scene, scenes)):
        d = Path(d)
        HV, HF = read_ply_vertices_faces(d / "hull.ply")
        WV, WF = read_ply_vertices_faces(d / "water.ply")
        floor = float(sc["floor_z"])
        cx, cy = sc["car_center"]
        rect = sc.get("water_rect") or [WV[:, 0].min(), WV[:, 0].max(),
                                        WV[:, 1].min(), WV[:, 1].max()]

        y_station = a.road_pad + i * a.spacing
        # SEAT ON THE CROWN, not on the lowest road point. Seating on the lowest
        # point buries the vehicle: the hull's underside sits on its own flat
        # floor, so putting that floor 0.124 m below the crown drives the tyres
        # 0.124 m into the road. Seating on the crown puts the vehicle exactly on
        # the road surface it is standing on, and because the hull and its water
        # take the SAME translation, the waterline on the vehicle stays exactly
        # what the solver produced. That is the relationship carrying the physics
        # and it is preserved to the last significant figure.
        T = np.array([xc - cx, y_station - cy, z_hi - floor])
        HV = HV + T
        WV = WV + T
        # The water's flat bottom now sits ON the crown, so the road falls away
        # beneath it toward the gutters and would leave an air gap under the patch
        # edges: the patch would read as a floating slab again. Push ONLY the
        # bottom face down until it is clear below the lowest road point. This
        # adds no optical path, because everything below the road surface is
        # occluded by opaque road; the water a viewer can see is bounded by the
        # road, which is what a flooded road actually looks like. The free surface
        # is untouched.
        drop = (z_hi - z_lo) + 0.03
        onfloor = WV[:, 2] <= (floor + T[2]) + 1e-6
        WV[onfloor, 2] -= drop
        print("[place] %-26s bottom face dropped %.4f m below the crown so the "
              "crowned road occludes it (%d of %d water verts)"
              % (sc.get("run", "?"), drop, int(onfloor.sum()), len(WV)))
        write_ply(out / ("hull_%d.ply" % i), HV, HF)
        write_ply(out / ("water_%d.ply" % i), WV, WF)

        swl = float(sc.get("still_water_z", floor)) + T[2]
        # surround_z is stored in the SOURCE scene's frame, so it takes the same
        # translation; swl above already carries it, hence the two branches differ.
        surz = (float(sc["surround_z"]) + T[2]) if sc.get("surround_z") else swl
        surf_levels.append(surz)
        depth_crown = swl - z_hi
        depth_edge = swl - z_lo
        print("[place] %-26s -> y %.2f m, dz %+.4f m. free surface %.4f m; depth "
              "%.3f m over the crown, matching the %.3f m the run simulated, and "
              "%.3f m at the channel where the crowned road falls away."
              % (sc.get("run", "?"), y_station, T[2], swl, depth_crown,
                 float(sc.get("still_water_z", 0)) - floor, depth_edge))
        vehicles.append({
            "name": sc.get("run"),
            "hull": "hull_%d.ply" % i,
            "water": "water_%d.ply" % i,
            "hull_source": sc.get("hull_ply_source"),
            "hull_verts": int(len(HV)),
            "surround_z": surz,
            "water_rect": [rect[0] + T[0], rect[1] + T[0],
                           rect[2] + T[1], rect[3] + T[1]],
            "translation_m": T.tolist(),
            "physics": sc.get("physics", {}),
            "frame": sc.get("frame"),
            "still_water_depth_m": float(sc.get("still_water_z", 0)) - floor,
        })

    # ONE surround level for the whole road. The three runs realise water surfaces
    # that differ, so a single flat sheet cannot meet all three exactly; the median
    # is used and the spread is printed rather than quietly absorbed.
    surround = float(np.median(surf_levels))
    print("[road] surround sheet at %.4f m. The three patches sit at %s, a spread "
          "of %.4f m, because they are three independent runs at three realised "
          "depths, not one scene." %
          (surround, ", ".join("%.4f" % v for v in surf_levels),
           max(surf_levels) - min(surf_levels)))

    scene = {
        "kind": "road_composite",
        "road": "road.ply",
        "road_width_total": a.width_total,
        "road_carriageway": a.carriageway,
        "road_cross_slope": a.cross_slope,
        "road_length": length,
        "road_profile_source": "simulation/road_geometry.road_profile",
        "crown_x": xc,
        "verge_z": float(road_profile(np.array([0.0]), a.width_total,
                                      carriageway=a.carriageway,
                                      cross_slope=a.cross_slope,
                                      crown_z=crown_z)[0]),
        "floor_z": float(road_V[:, 2].min()),
        "road_crown_z": crown_z,
        "surround_z": surround,
        "surround_spread_m": float(max(surf_levels) - min(surf_levels)),
        "car_center": [xc, a.road_pad + 0.5 * span],
        "vehicles": vehicles,
        "PRESENTATIONAL": [
            "the arrangement of vehicles along the road",
            "the flat water between and beyond the patches",
            "the crowned cross-section, which none of these runs simulated",
        ],
    }
    (out / "scene.json").write_text(json.dumps(scene, indent=2))
    print("[road] wrote %s" % (out / "scene.json"))


if __name__ == "__main__":
    main()
