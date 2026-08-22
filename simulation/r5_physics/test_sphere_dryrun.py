"""Execute sphere_heave.py end to end against a STUB solver, with no GPU and no warpmpm.

WHY. `sphere_heave.py` has never been executed. Only its geometry helpers are covered by
`test_sphere_geometry.py`; `SphereTank.__init__`, `advance()`, `config()` and `run()` have
never run a single line. The TACC socket has been cold all session, so the first time that
code executes would be inside a GPU job, where a wrong keyword or a shape error costs the
window rather than a second.

This installs a stub `warpmpm` into `sys.modules` that records every call and returns
plausible objects, then drives the real driver through it. It cannot validate physics. It
validates that the driver RUNS: keyword names, shapes, call order, the 1-DOF integration
arithmetic, and the documented trap contract.

WHAT IT ASSERTS BEYOND "no exception", because "it ran" is not a test:
  * `reset_sdf_force` is called before EVERY `step`, which is trap T2, the accumulator the
    engine never zeroes.
  * `sdf_wrench` receives the TICK duration, dt*substeps, not the substep dt. That is trap
    T1, which inflates force by exactly `substeps` and does so plausibly.
  * `set_sdf_pose` is called after the wrench read, never before, so the pose the solver
    sees for a tick is the one the integrator produced from the previous tick.
  * The free-heave integrator reproduces semi-implicit Euler exactly against a hand
    computation, given a known injected force.
  * `--fixed` mode does NOT move the body.
  * Water particle count, carve behaviour, and substep count match what the manifest
    costed the job at.

Run:  python simulation/r5_physics/test_sphere_dryrun.py
"""
from __future__ import annotations

import math
import sys
import types
from pathlib import Path

import numpy as np

CALLS = []
FORCE_Z = [0.0]          # injected wrench, set per test


class _StubSolver:
    def __init__(self, grid=None, device=None):
        CALLS.append(("Solver", {"grid": grid, "device": device}))
        self._n = 0

    def load_particles(self, pos, vol):
        CALLS.append(("load_particles", {"n": len(pos), "vol_n": len(vol),
                                         "pos_shape": tuple(np.shape(pos))}))
        self._n = len(pos)
        return self

    def set_material(self, material, **kw):
        CALLS.append(("set_material", {"material": material, **kw}))
        return self

    def add_plane(self, point, normal, surface="sticky", friction=0.0, restitution=0.0,
                  **kw):
        CALLS.append(("add_plane", {"point": tuple(point), "normal": tuple(normal),
                                    "surface": surface, "friction": friction,
                                    "restitution": restitution}))
        return self

    def add_domain_walls(self, **kw):
        CALLS.append(("add_domain_walls", {}))
        return self

    def add_sdf_collider(self, sdf, center, quat=(0.0, 0.0, 0.0, 1.0),
                         velocity=(0.0, 0.0, 0.0), surface="separable", friction=0.4,
                         **kw):
        CALLS.append(("add_sdf_collider", {"center": tuple(center), "quat": tuple(quat),
                                           "velocity": tuple(velocity),
                                           "surface": surface, "friction": friction}))
        return 0

    def reset_sdf_force(self, handle):
        CALLS.append(("reset_sdf_force", {"handle": handle}))
        return self

    def step(self, dt, substeps=1):
        CALLS.append(("step", {"dt": dt, "substeps": substeps}))
        return self

    def sdf_wrench(self, handle, dt):
        CALLS.append(("sdf_wrench", {"handle": handle, "dt": dt}))
        return {"force": np.array([0.0, 0.0, FORCE_Z[0]]), "torque": np.zeros(3)}

    def set_sdf_pose(self, handle, center=None, quat=None, velocity=None, omega=None):
        CALLS.append(("set_sdf_pose", {"handle": handle, "center": tuple(center),
                                       "velocity": tuple(velocity)}))
        return self


def install_stub():
    """Minimal warpmpm surface: only what sphere_heave.py actually imports."""
    wm = types.ModuleType("warpmpm")
    core = types.ModuleType("warpmpm.core")
    solver_mod = types.ModuleType("warpmpm.core.solver")
    mats = types.ModuleType("warpmpm.materials")
    geom = types.ModuleType("warpmpm.geometry")

    class GridConfig:
        def __init__(self, n_grid, grid_lim):
            CALLS.append(("GridConfig", {"n_grid": n_grid, "grid_lim": grid_lim}))
            self.n_grid, self.grid_lim = n_grid, grid_lim

    class SDFData:
        def __init__(self, res, cell, origin):
            n = res
            r = 0.15
            idx = np.arange(n) * cell
            gx, gy, gz = np.meshgrid(idx, idx, idx, indexing="ij")
            pts = np.stack([gx, gy, gz], -1) + origin
            self.values = np.linalg.norm(pts, axis=-1) - r
            self.grads = np.zeros(self.values.shape + (3,))
            self.origin, self.cell = np.asarray(origin, float), cell
            self.sdf_max = float(self.values.max())

    def build_sdf(verts, faces, res=64, margin_cells=4.0):
        CALLS.append(("build_sdf", {"res": res, "margin_cells": margin_cells,
                                    "nv": len(verts), "nf": len(faces)}))
        span = float(np.ptp(verts, axis=0).max())
        cell = span / (res - 1 - 2 * margin_cells)
        origin = -0.5 * np.array([1.0, 1.0, 1.0]) * cell * (res - 1)
        return SDFData(res, cell, origin)

    def newtonian(**kw):
        CALLS.append(("newtonian", kw))
        return "newtonian"

    solver_mod.Solver = _StubSolver
    solver_mod.GridConfig = GridConfig
    mats.newtonian = newtonian
    geom.build_sdf = build_sdf
    geom.SDFData = SDFData
    core.solver = solver_mod
    wm.core, wm.materials, wm.geometry = core, mats, geom
    for name, mod in (("warpmpm", wm), ("warpmpm.core", core),
                      ("warpmpm.core.solver", solver_mod),
                      ("warpmpm.materials", mats), ("warpmpm.geometry", geom)):
        sys.modules[name] = mod


FAILURES = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)


def main():
    print("sphere_heave.py dry run against a stub solver (no GPU, no warpmpm)\n")
    install_stub()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sphere_heave as sh

    # --- construction, the path that has never executed -------------------------------
    print("construction")
    CALLS.clear()
    tank = sh.SphereTank(n_grid=64, lim=1.2, depth=0.5, h0_over_d=0.1)
    names = [c[0] for c in CALLS]
    check("SphereTank constructs without error", True,
          f"({tank.n_water:,} water particles, {tank.substeps} substeps)")
    check("water count matches the manifest's costing", 550_000 < tank.n_water < 650_000,
          f"({tank.n_water:,}; manifest costed 598,505 at h0=0)")
    check("substeps match the manifest", tank.substeps == 82, f"({tank.substeps})")
    check("floor plane and four walls registered",
          names.count("add_plane") == 5, f"({names.count('add_plane')} planes)")
    check("domain walls registered", "add_domain_walls" in names)
    check("SDF collider registered", "add_sdf_collider" in names)
    mat = [c for c in CALLS if c[0] == "newtonian"][0][1]
    check("material built at the BENCHMARK density, not the canonical 1000",
          abs(mat["density"] - 998.2) < 1e-9, f"(density={mat['density']})")
    check("carve removed particles for a partially submerged sphere",
          tank.n_carved > 0, f"({tank.n_carved:,} carved)")

    # --- the documented trap contract --------------------------------------------------
    print("\ntrap contract (T1, T2, ordering)")
    CALLS.clear()
    FORCE_Z[0] = 100.0
    tank.advance()
    seq = [c[0] for c in CALLS]
    check("T2: reset_sdf_force precedes step",
          seq.index("reset_sdf_force") < seq.index("step"), f"({seq})")
    wr = [c for c in CALLS if c[0] == "sdf_wrench"][0][1]
    check("T1: sdf_wrench gets the TICK, not the substep",
          abs(wr["dt"] - tank.dt * tank.substeps) < 1e-15,
          f"(got {wr['dt']:.6g}, substep is {tank.dt:.6g})")
    check("set_sdf_pose comes AFTER the wrench read",
          seq.index("set_sdf_pose") > seq.index("sdf_wrench"))

    # --- integrator arithmetic, against a hand computation -----------------------------
    print("\n1-DOF integrator")
    t2 = sh.SphereTank(n_grid=64, lim=1.2, depth=0.5, h0_over_d=0.1)
    FORCE_Z[0] = 0.0                      # no fluid force: pure free fall
    z0, tick = t2.z, t2.tick
    t2.advance()
    v_exp = -sh.G_ENGINE * tick
    z_exp = z0 + v_exp * tick
    check("semi-implicit Euler reproduces a hand computation",
          abs(t2.vz - v_exp) < 1e-12 and abs(t2.z - z_exp) < 1e-12,
          f"(v {t2.vz:.9f} vs {v_exp:.9f})")
    FORCE_Z[0] = t2.mass * sh.G_ENGINE    # exact support: acceleration must vanish
    v_before = t2.vz
    t2.advance()
    check("a wrench equal to the weight produces zero acceleration",
          abs(t2.vz - v_before) < 1e-12, f"(dv={t2.vz - v_before:.3e})")

    # --- fixed mode must not move the body ---------------------------------------------
    print("\nfixed mode")
    t3 = sh.SphereTank(n_grid=64, lim=1.2, depth=0.5, h0_over_d=0.0, free=False)
    z_start = t3.z
    CALLS.clear()
    FORCE_Z[0] = 12345.0
    for _ in range(3):
        t3.advance()
    check("--fixed does not move the sphere", abs(t3.z - z_start) < 1e-15)
    check("--fixed never calls set_sdf_pose",
          not any(c[0] == "set_sdf_pose" for c in CALLS))

    # --- config assembly ---------------------------------------------------------------
    print("\nconfig assembly")
    cfg = tank.config()
    for k in ("dx_m", "n_water", "substeps", "dt_tick_s", "sphere_cells_across",
              "reflect_kramer_phase_s", "reflect_group_s", "reflect_shallow_bound_s",
              "mach_peak", "sdf_band_clearance"):
        check(f"config carries {k}", k in cfg,
              f"({cfg.get(k):.5g})" if isinstance(cfg.get(k), float) else "")
    check("config reports Kramer's phase convention as the default reflection",
          abs(cfg["reflect_kramer_phase_s"] - tank.reflection_return_s()) < 1e-12)

    print(f"\n{'ALL PASS' if not FAILURES else 'FAILURES: ' + ', '.join(FAILURES)}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
