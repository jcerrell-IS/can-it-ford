"""Hero render for the gated warpmpm run g64_m1100 (Can It Ford).

Renders EXISTING solver output only. No simulation is run here.

Source data
  renders/yaris_render_s1/_incoming/g64_m1100/rollout.npz   particle + rigid-body history
  renders/yaris_render_s1/gates_results_all_runs.json       gate verdicts (read live)
  vehicle_geometry_research/yaris_coarse_v1l_watertight.ply canonical Yaris hull

Solver provenance: warpmpm via renders/yaris_render_s1/sim_standing.py. NOT Genesis.

Vehicle frame, derived at runtime, never hardcoded
  The canonical vehicle frame used by vehicle_live.load_vehicle + sim_standing.canonicalize is
  the hull rotated by Rz(+90) so the long axis lies along y, then centred on its vertex bbox in
  x and y with z_min driven to 0. Reproducing solidify_watertight() on that mesh at the run's
  own h returns 8905 points matching veh_particles_vehframe to 1.2e-07, which is what fixes the
  rotation and the centring. A residual body-frame offset c between veh_particles_vehframe and
  the (R, t) rigid history is solved from the stored checkpoint frames, so the chain

      world(i) = (canonical_mesh + c) @ R[i].T + t[i]

  reproduces veh_particles_scene0, veh_check_45 and veh_check_last to < 1e-06 m.

Water shading: screen-space PBR + depth-peeled transparency. This VTK build ships no OSPRay
raytracing module, so there is no true refraction, transmission or caustics. See RENDER_NOTES.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.spatial import ConvexHull

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUN = "g64_m1100"
NPZ = HERE / "_incoming" / RUN / "rollout.npz"
SUMMARY = HERE / "_incoming" / RUN / "summary.json"
GATES = HERE / "gates_results_all_runs.json"
MESH = REPO / "vehicle_geometry_research" / "yaris_coarse_v1l_watertight.ply"
CLIMS = HERE / "global_color_limits.json"

RZ90 = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])


# ----------------------------------------------------------------------------- geometry


def canonical_hull() -> trimesh.Trimesh:
    """Yaris hull in the vehicle frame load_vehicle/canonicalize actually produce."""
    m = trimesh.load(MESH, process=False)
    v = np.asarray(m.vertices, dtype=np.float64) @ RZ90.T
    lo, hi = v.min(0), v.max(0)
    v = v - np.array([(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2]])
    return trimesh.Trimesh(vertices=v, faces=np.asarray(m.faces), process=False)


def solve_body_offset(d) -> np.ndarray:
    """Body-frame offset c with world(i) = (vehframe + c) @ R[i].T + t[i].

    Solved from the three stored checkpoint frames and cross-checked for agreement, so a
    convention change upstream shows up as an assertion rather than a silently wrong pose.
    """
    R, t, pv_ = d["R"], d["t"], np.asarray(d["veh_particles_vehframe"], np.float64)
    checks = {0: d["veh_particles_scene0"], 45: d["veh_check_45"], 89: d["veh_check_last"]}
    cs = [(((np.asarray(W, np.float64) - t[i]) @ R[i]) - pv_).mean(0) for i, W in checks.items()]
    cs = np.asarray(cs)
    spread = float(np.abs(cs - cs.mean(0)).max())
    assert spread < 1e-5, f"body offset inconsistent across checkpoints: {spread:.3e}"
    c = cs.mean(0)
    for i, W in checks.items():
        err = float(np.abs((pv_ + c) @ R[i].T + t[i] - np.asarray(W, np.float64)).max())
        assert err < 1e-5, f"pose chain failed at frame {i}: {err:.3e} m"
        print(f"  pose check frame {i:2d}: max abs err {err:.3e} m")
    return c


# ----------------------------------------------------------------------------- water


class WaterField:
    """Particle -> density/speed grid -> marching-cubes free surface.

    The isolevel is calibrated once on frame 0 (a flat hydrostatic slab of known depth) and then
    held fixed for every frame, matching the project's fixed-limits convention.
    """

    def __init__(self, lim: float, floor: float, gs: float, sigma: float):
        self.gs, self.sigma, self.floor = gs, sigma, floor
        self.org = np.array([0.0, 0.0, floor - 4.0 * gs])
        top = np.array([lim, lim, floor + 1.35])
        self.dim = np.maximum(np.ceil((top - self.org) / gs).astype(int) + 1, 2)
        self.level: float | None = None

    def _grids(self, pos: np.ndarray, spd: np.ndarray):
        idx = (pos - self.org) / self.gs
        ok = np.all((idx >= 0) & (idx <= self.dim - 1.001), axis=1)
        idx = idx[ok]
        base = np.floor(idx).astype(np.int64)
        frac = idx - base
        den = np.zeros(self.dim, np.float64)
        num = np.zeros(self.dim, np.float64)
        s = spd[ok]
        for dx in (0, 1):  # trilinear deposit keeps the surface from beading on the grid
            wx = frac[:, 0] if dx else 1.0 - frac[:, 0]
            for dy in (0, 1):
                wy = frac[:, 1] if dy else 1.0 - frac[:, 1]
                for dz in (0, 1):
                    wz = frac[:, 2] if dz else 1.0 - frac[:, 2]
                    w = wx * wy * wz
                    flat = np.ravel_multi_index(
                        (base[:, 0] + dx, base[:, 1] + dy, base[:, 2] + dz), self.dim
                    )
                    den.ravel()[:] += np.bincount(flat, weights=w, minlength=den.size)
                    num.ravel()[:] += np.bincount(flat, weights=w * s, minlength=den.size)
        den = gaussian_filter(den, self.sigma, mode="nearest")
        num = gaussian_filter(num, self.sigma, mode="nearest")
        return den, num

    def _contour(self, den, level) -> pv.PolyData:
        grid = pv.ImageData(dimensions=tuple(self.dim), spacing=(self.gs,) * 3,
                            origin=tuple(self.org))
        grid.point_data["den"] = den.ravel(order="F")
        return grid.contour([level], scalars="den")

    def _free_surface_z(self, surf, xmax) -> float | None:
        """Median top-of-column height in undisturbed water, orientation independent."""
        if surf.n_points == 0:
            return None
        p = surf.points
        sel = (p[:, 0] < xmax) & (p[:, 0] > 0.4) & (p[:, 2] > self.floor - 0.05)
        if sel.sum() < 200:
            return None
        p = p[sel]
        key = np.floor(p[:, :2] / (4.0 * self.gs)).astype(np.int64)
        _, inv = np.unique(key, axis=0, return_inverse=True)
        tops = np.full(inv.max() + 1, -np.inf)
        np.maximum.at(tops, inv, p[:, 2])
        return float(np.median(tops[np.isfinite(tops)]))

    def calibrate(self, pos, spd, target_z: float, xmax: float = 3.5) -> float:
        """Bisect the isolevel so the frame-0 free surface sits at the physical depth.

        Density rises inside the fluid, so surface height falls monotonically with level.
        Targeting the known hydrostatic depth beats any fixed percentile heuristic.
        """
        den, _ = self._grids(pos, spd)
        hi = float(den.max())
        lo, hi_l = 1e-6 * hi, hi
        best = None
        for _ in range(40):
            mid = 0.5 * (lo + hi_l)
            z = self._free_surface_z(self._contour(den, mid), xmax)
            if z is None:
                hi_l = mid
                continue
            best = (mid, z)
            if z > target_z:
                lo = mid
            else:
                hi_l = mid
            if abs(z - target_z) < 1e-4:
                break
        assert best is not None, "isolevel calibration failed to find any free surface"
        self.level = best[0]
        self.calib_z = best[1]
        return self.level

    def surface(self, pos, spd) -> pv.PolyData:
        den, num = self._grids(pos, spd)
        surf = self._contour(den, self.level)
        if surf.n_points == 0:
            return surf
        spd_f = num / np.maximum(den, 1e-9)
        ijk = (surf.points - self.org) / self.gs
        surf.point_data["speed"] = map_coordinates(
            spd_f, ijk.T, order=1, mode="nearest"
        ).astype(np.float32)
        return surf.smooth(n_iter=18, relaxation_factor=0.16)


# ----------------------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "hero_2026-08-06"))
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--grid-spacing", type=float, default=0.05)
    ap.add_argument("--sigma", type=float, default=1.25)
    ap.add_argument("--frames", default="all", help="'all' or a single frame index for a probe")
    a = ap.parse_args()

    out = Path(a.out)
    (out / "frames").mkdir(parents=True, exist_ok=True)

    d = np.load(NPZ)
    summary = json.loads(SUMMARY.read_text())
    lim, floor = float(d["lim"]), float(d["floor"])
    fps, nfr = int(d["fps"]), int(d["frames"])
    R, t = d["R"], d["t"]
    water, speed = d["water"], d["speed"]

    # verdicts: live from the gates store, never a literal
    recs = json.loads(GATES.read_text())
    recs = recs.get("runs", recs) if isinstance(recs, dict) else recs
    g = [r for r in recs if r.get("run") == RUN]
    assert len(g) == 1, f"expected exactly 1 gates record for {RUN}, got {len(g)}"
    g = g[0]
    vmax = float(json.loads(CLIMS.read_text())["global_vmax"])

    print(f"run {RUN}: {nfr} frames @ {fps} fps, lim {lim:.4f} m, floor {floor:.5f} m")
    print(f"  gates L0={g['L0_verdict']} L1a={g['L1a_verdict']} "
          f"L1b={g['L1b_verdict']} L2={g['L2_verdict']} ({g['rungs_no_ford']}/4)")
    print(f"  speed clim [0, {vmax:.4f}] m/s (global_color_limits.json)")

    hull = canonical_hull()
    c = solve_body_offset(d)
    print(f"  body offset c = {np.round(c, 8).tolist()}")
    hv = np.asarray(hull.vertices) + c
    faces = np.hstack([np.full((len(hull.faces), 1), 3), np.asarray(hull.faces)]).ravel()

    def pose(i):
        return hv @ R[i].T + t[i]

    # realized depth is layers * particle pitch, not the requested 0.30 m
    realized_depth = int(summary["water_layers"]) * float(d["h"])
    target_z = floor + realized_depth
    wf = WaterField(lim, floor, a.grid_spacing, a.sigma)
    lvl = wf.calibrate(water[0], speed[0], target_z)
    err = wf.calib_z - target_z
    print(f"  isolevel {lvl:.5f} -> frame-0 free surface z {wf.calib_z:.5f} m "
          f"(depth {wf.calib_z - floor:.5f} m vs realized {realized_depth:.5f} m, "
          f"err {err * 1e3:+.2f} mm)")
    assert abs(err) < 5e-3, f"free surface off by {err * 1e3:.1f} mm"

    disp = np.linalg.norm(t - t[0], axis=1)

    # ---- scene
    pl = pv.Plotter(off_screen=True, window_size=(a.width, a.height))
    pl.set_background("#0d1520", top="#243447")
    pl.enable_depth_peeling(number_of_peels=12)

    bed = pv.Plane(center=(lim / 2, lim / 2, floor), direction=(0, 0, 1),
                   i_size=lim, j_size=lim, i_resolution=1, j_resolution=1)
    pl.add_mesh(bed, color="#3b3f45", ambient=0.28, diffuse=0.75, specular=0.05)

    car = pv.PolyData(pose(0), faces)
    pl.add_mesh(car, color="#d9dde3", pbr=True, metallic=0.55, roughness=0.34, ambient=0.16)

    def footprint(i, z):
        """Plan-view outline of the hull at frame i, drawn on the bed."""
        p = pose(i)[:, :2]
        hull2d = ConvexHull(p)
        ring = np.c_[p[hull2d.vertices], np.full(len(hull2d.vertices), z)]
        ring = np.vstack([ring, ring[:1]])
        return pv.lines_from_points(ring)

    # start footprint is fixed; the gap to the moving car is the displacement, read directly
    pl.add_mesh(footprint(0, floor + 0.008), color="#ff8c42", line_width=5,
                lighting=False, render_lines_as_tubes=True)
    now_actor = None

    water_actor = None
    pl.add_light(pv.Light(position=(lim * 0.15, -lim * 0.35, lim * 0.95), focal_point=(5.7, 4.7, 0.7),
                          color="white", intensity=0.95))
    pl.add_light(pv.Light(position=(lim * 1.2, lim * 1.1, lim * 0.7), focal_point=(5.7, 4.7, 0.7),
                          color="#bcd6ff", intensity=0.45))

    focal = np.array([t[0][0] + 0.30, t[0][1] - 0.10, floor + 0.42])
    pl.camera_position = [tuple(focal + np.array([-7.0, -6.6, 3.35])), tuple(focal), (0, 0, 1)]
    pl.camera.zoom(1.52)

    fs = a.height / 1080.0  # keep overlay proportions identical at 1080p and 4K
    idxs = range(nfr) if a.frames == "all" else [int(a.frames)]
    for i in idxs:
        car.points = pose(i)
        surf = wf.surface(water[i], speed[i])
        if water_actor is not None:
            pl.remove_actor(water_actor)
        if now_actor is not None:
            pl.remove_actor(now_actor)
        now_actor = pl.add_mesh(footprint(i, floor + 0.010), color="#f4f8ff", line_width=3,
                                lighting=False, render_lines_as_tubes=True)
        water_actor = pl.add_mesh(
            surf, scalars="speed", cmap="viridis", clim=[0.0, vmax],
            opacity=0.80, pbr=True, metallic=0.30, roughness=0.13, ambient=0.10,
            smooth_shading=True, show_scalar_bar=(i == idxs[0]),
            scalar_bar_args=dict(title="water speed (m/s)", n_labels=5,
                                 color="#e8eef6", width=0.24, height=0.040,
                                 position_x=0.735, position_y=0.905,
                                 title_font_size=round(16 * fs),
                                 label_font_size=round(13 * fs), fmt="%.2f"),
        )
        head = (f"Can It Ford      run {RUN}      warpmpm MPM (sim_standing.py)\n"
                f"Toyota Yaris hull, {summary['mass_kg']:.0f} kg ({g['arr_limit_set']}),   "
                f"depth {g['nominal_depth_m']:.4f} m,   flow {g['velocity_ms']:.1f} m/s,   "
                f"grid {int(d['n_grid'])}^3")
        foot = (f"t = {i / fps:5.2f} s of {(nfr - 1) / fps:.2f} s          "
                f"body displacement = {disp[i]:.3f} m   "
                f"(final {disp[-1]:.3f} m, drift threshold 0.05 m)")
        verd = (f"L0 {g['L0_verdict']}    L1a {g['L1a_verdict']}    "
                f"L1b {g['L1b_verdict']}    L2 {g['L2_verdict']}\n"
                f"{g['rungs_no_ford']}/4 rungs NO-FORD")
        key = "orange outline: start footprint      white outline: current footprint"
        acts = [pl.add_text(head, position=(0.012, 0.940), viewport=True,
                            font_size=round(11 * fs), color="#eaf1fa"),
                pl.add_text(foot, position=(0.012, 0.038), viewport=True,
                            font_size=round(11 * fs), color="#dce6f2"),
                pl.add_text(verd, position=(0.012, 0.838), viewport=True,
                            font_size=round(15 * fs), color="#ff9f5a"),
                pl.add_text(key, position=(0.012, 0.100), viewport=True,
                            font_size=round(9 * fs), color="#9fb4cc")]
        pl.screenshot(str(out / "frames" / f"f{i:04d}.png"))
        for t_ in acts:
            pl.remove_actor(t_)
        if i % 10 == 0 or i == nfr - 1:
            print(f"    frame {i:3d}/{nfr - 1}  disp {disp[i]:.3f} m  surf {surf.n_points} pts",
                  flush=True)
    pl.close()

    if a.frames == "all":
        mp4 = out / f"hero_{RUN}_2026-08-06.mp4"
        cmd = ["ffmpeg", "-y", "-framerate", str(fps), "-i",
               str(out / "frames" / "f%04d.png"), "-c:v", "libx264", "-preset", "slow",
               "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"\nwrote {mp4}")


if __name__ == "__main__":
    main()
