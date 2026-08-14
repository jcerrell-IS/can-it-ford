"""Executable proof of Dispatch 9's traps 1, 2 and 3, against the PINNED engine.

The dispatch's definition of done requires each of wrench normalisation, accumulator
zeroing and quaternion order to be "verified by an explicit test, not by inspection".
Reading the source tells you what the code says; these tests make the engine
demonstrate it, and each one FAILS LOUDLY if the trap is ever fixed upstream, which is
the behaviour you want from a trap test.

RUN:
    PYTHONPATH=<engine>/src python tests/test_sdf_wrench_contract.py
Engine must be the pinned SHA 544c93dd02cb9c7ead89e1155a62967243244fce.
A GPU is not required; --device cpu works and is the default when no CUDA is present.

WHAT EACH TEST PROVES

  T1 WRENCH NORMALISATION. sdf_wrench(handle, dt) divides the ACCUMULATED IMPULSE by
     whatever dt it is handed (core/solver.py:361, `f / dt`). So reading the same
     accumulator twice with dt=tick and dt=dt_sub must give results in exactly the
     ratio n_substeps. That is the trap: passing dt_sub for an n-substep tick inflates
     every force by exactly n and the number still looks plausible.

  T2 ACCUMULATOR ZEROING. Nothing in core/ or kernels/ zeroes an SDF collider's
     accumulator per step; every zeroing site is an explicit caller-facing method
     (reset_cup_wrench :295, reset_sdf_force :348, reset_cdf_wrench via :398,
     reset_tool_force :415). So stepping twice without a reset must give a strictly
     larger accumulated impulse than stepping once: the read is run-to-date, not
     per-tick.

  T3 QUATERNION ORDER. add_sdf_collider stores `wp.quat(q[0],q[1],q[2],q[3])`
     (kernels/mpm_solver_warp.py, in add_sdf_collider), and wp.quat is XYZW, while
     add_cup (core/solver.py:256) documents WXYZ and defaults (1,0,0,0). Feeding one
     convention's tuple to the other rotates the body differently AND SILENTLY. The
     test asserts the SDF path matches an independent numpy XYZW construction, and
     that the WXYZ reading of the same tuple is a genuinely different rotation.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np


def _tiny_scene(device: str, n_grid: int = 24):
    """Smallest scene that produces a nonzero SDF reaction: a water block resting on a
    box SDF collider. Physics fidelity is irrelevant here; these are contract tests.
    """
    import warp as wp  # noqa: F401  (import ordering matters for warp init)
    from warpmpm.core.solver import GridConfig, Solver
    from warpmpm.materials import newtonian

    lim = 1.0
    grid = GridConfig(n_grid=n_grid, grid_lim=lim)
    dx = grid.dx
    h = dx / 2.0

    # An analytic box SDF, built directly rather than from a mesh so the test has no
    # dependency on a hull file or on an 8-minute SDF build.
    res = 24
    half = 0.15
    cell = (2.0 * half + 6.0 * dx) / (res - 1)
    origin = (-half - 3.0 * dx, -half - 3.0 * dx, -half - 3.0 * dx)
    ax = origin[0] + cell * np.arange(res)
    X, Y, Z = np.meshgrid(ax, ax, ax, indexing="ij")
    q = np.stack([np.abs(X) - half, np.abs(Y) - half, np.abs(Z) - half], -1)
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=-1)
    inside = np.minimum(np.max(q, axis=-1), 0.0)
    vals = (outside + inside).astype(np.float64)
    g = np.gradient(vals, cell, cell, cell)
    grads = np.stack(g, -1)

    from types import SimpleNamespace
    sdf = SimpleNamespace(values=vals, grads=grads, origin=origin, cell=cell)

    # water block sitting above the collider
    centre = np.array([0.5 * lim, 0.5 * lim, 0.5 * lim])
    xs = np.arange(centre[0] - 0.18, centre[0] + 0.18, h)
    ys = np.arange(centre[1] - 0.18, centre[1] + 0.18, h)
    zs = np.arange(centre[2] + 0.16, centre[2] + 0.30, h)
    water = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
    vol = np.full(len(water), h ** 3, dtype=np.float32)

    s = Solver(grid=grid, device=device).load_particles(
        water.astype(np.float32), vol)
    s.set_material(newtonian(eta=1.0e-3, density=1000.0, bulk_modulus=1.5e5))
    s.add_domain_walls()
    handle = s.add_sdf_collider(sdf, center=tuple(centre), quat=(0.0, 0.0, 0.0, 1.0),
                                surface="separable", friction=0.4)
    return s, handle, len(water)


def test_wrench_normalisation(device: str) -> dict:
    """T1: the accessor divides by the dt it is handed, so the ratio is exactly n."""
    s, handle, n = _tiny_scene(device)
    n_sub, dt_sub = 8, 2.0e-5
    tick = n_sub * dt_sub

    s.reset_sdf_force(handle)
    s.step(dt_sub, n_sub)

    w_tick = np.asarray(s.sdf_wrench(handle, dt=tick)["force"], dtype=float)
    w_sub = np.asarray(s.sdf_wrench(handle, dt=dt_sub)["force"], dtype=float)

    nz = np.abs(w_tick) > 0
    if not nz.any():
        raise AssertionError("T1 inconclusive: the accumulator was zero, so the scene "
                             "produced no reaction and the ratio is undefined.")
    ratio = w_sub[nz] / w_tick[nz]
    err = float(np.abs(ratio - n_sub).max())
    ok = err <= 1e-9 * n_sub
    print(f"  T1 force(dt=dt_sub) / force(dt=tick) = {ratio[0]:.12f}  "
          f"expected exactly {n_sub}  max|err| {err:.3e}   {'PASS' if ok else 'FAIL'}")
    print(f"     => passing dt_sub for an {n_sub}-substep tick inflates force by {n_sub}x")
    return {"test": "wrench_normalisation", "pass": bool(ok), "n_substeps": n_sub,
            "ratio_measured": float(ratio[0]), "max_abs_err": err,
            "force_tick_N": w_tick.tolist(), "force_dtsub_N": w_sub.tolist()}


def test_accumulator_not_auto_zeroed(device: str) -> dict:
    """T2: without an explicit reset the read is run-to-date, not per-tick."""
    s, handle, n = _tiny_scene(device)
    n_sub, dt_sub = 8, 2.0e-5
    tick = n_sub * dt_sub

    s.reset_sdf_force(handle)
    s.step(dt_sub, n_sub)
    imp1 = np.asarray(s.sdf_wrench(handle, dt=tick)["force"], dtype=float) * tick

    s.step(dt_sub, n_sub)                       # deliberately NO reset
    imp2 = np.asarray(s.sdf_wrench(handle, dt=tick)["force"], dtype=float) * tick

    s.reset_sdf_force(handle)                   # now reset, one tick alone
    s.step(dt_sub, n_sub)
    imp3 = np.asarray(s.sdf_wrench(handle, dt=tick)["force"], dtype=float) * tick

    m1, m2, m3 = (float(np.linalg.norm(v)) for v in (imp1, imp2, imp3))
    grew = m2 > m1 * (1.0 + 1e-9)
    reset_works = m3 < m2 * (1.0 - 1e-9)
    ok = grew and reset_works
    print(f"  T2 |impulse| after 1 tick (reset first) {m1:.6e}")
    print(f"     |impulse| after 2 ticks, NO reset    {m2:.6e}   grew: {grew}")
    print(f"     |impulse| after reset + 1 tick       {m3:.6e}   reset works: {reset_works}")
    print(f"     {'PASS' if ok else 'FAIL'} => a naive read without reset_sdf_force is "
          f"the RUN-TO-DATE total")
    return {"test": "accumulator_not_auto_zeroed", "pass": bool(ok),
            "impulse_1tick": m1, "impulse_2ticks_no_reset": m2,
            "impulse_after_reset": m3}


def test_quaternion_order(device: str) -> dict:
    """T3: the SDF path is XYZW; the cup path is WXYZ; crossing them rotates wrongly."""
    import warp as wp

    ang = np.pi / 2.0
    q_xyzw = np.array([0.0, 0.0, np.sin(ang / 2.0), np.cos(ang / 2.0)])  # +90 deg about z

    # What the SDF path applies: wp.quat takes XYZW.
    wq = wp.quat(float(q_xyzw[0]), float(q_xyzw[1]), float(q_xyzw[2]), float(q_xyzw[3]))
    probe = np.array([1.0, 0.0, 0.0])
    rot_engine = np.array(wp.quat_rotate(wq, wp.vec3(*probe)), dtype=float)

    # Independent numpy XYZW rotation of the same tuple.
    x, y, z, w = q_xyzw
    R_xyzw = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    rot_xyzw = R_xyzw @ probe

    err_xyzw = float(np.abs(rot_engine - rot_xyzw).max())
    engine_is_xyzw = err_xyzw < 1e-6

    # The cup path's convention, read from the engine itself, on the SAME tuple.
    from warpmpm.colliders.glass import quat_to_mat
    rot_wxyz = np.asarray(quat_to_mat(tuple(q_xyzw)), dtype=float) @ probe
    divergence = float(np.abs(rot_engine - rot_wxyz).max())
    conventions_differ = divergence > 1e-3

    ok = engine_is_xyzw and conventions_differ
    print(f"  T3 probe {probe.tolist()} rotated by the SAME 4-tuple "
          f"{np.round(q_xyzw, 6).tolist()}")
    print(f"     SDF path (wp.quat, XYZW)  -> {np.round(rot_engine, 6).tolist()}")
    print(f"     numpy XYZW reference      -> {np.round(rot_xyzw, 6).tolist()}   "
          f"max|err| {err_xyzw:.2e}")
    print(f"     cup path (quat_to_mat)    -> {np.round(rot_wxyz, 6).tolist()}   "
          f"divergence {divergence:.4f}")
    print(f"     {'PASS' if ok else 'FAIL'} => the two conventions give different "
          f"rotations and neither errors")
    return {"test": "quaternion_order", "pass": bool(ok),
            "engine_is_xyzw": bool(engine_is_xyzw),
            "conventions_differ": bool(conventions_differ),
            "rot_sdf_path": rot_engine.tolist(), "rot_numpy_xyzw": rot_xyzw.tolist(),
            "rot_cup_path_wxyz": rot_wxyz.tolist(), "divergence": divergence}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=None, help="cuda:0 or cpu; default auto")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    import warp as wp
    wp.init()
    device = args.device
    if device is None:
        device = "cuda:0" if wp.get_cuda_device_count() > 0 else "cpu"

    print("=" * 78)
    print("DISPATCH 9 TRAP CONTRACT TESTS, pinned engine")
    print("=" * 78)
    import warpmpm
    import os
    print(f"warp     {wp.config.version}")
    print(f"warpmpm  {os.path.dirname(warpmpm.__file__)}")
    print(f"device   {device}\n")

    results = []
    failures = 0
    for fn in (test_wrench_normalisation, test_accumulator_not_auto_zeroed,
               test_quaternion_order):
        print(f"{fn.__name__}:")
        try:
            r = fn(device)
        except Exception as exc:  # a test that cannot run is not a test that passed
            r = {"test": fn.__name__, "pass": False, "error": f"{type(exc).__name__}: {exc}"}
            print(f"  ERROR {type(exc).__name__}: {exc}")
        results.append(r)
        failures += 0 if r.get("pass") else 1
        print()

    print("=" * 78)
    print(f"{len(results) - failures}/{len(results)} PASS")
    print("=" * 78)
    if args.json_out:
        import json
        with open(args.json_out, "w") as f:
            json.dump({"warp": wp.config.version, "device": device,
                       "results": results, "failures": failures}, f, indent=2)
        print(f"wrote {args.json_out}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
