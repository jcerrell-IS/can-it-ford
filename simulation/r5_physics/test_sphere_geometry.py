"""Geometry and reference-quantity checks for sphere_heave.py that need no GPU.

Everything here runs on the Mac against numpy alone. warpmpm is imported only inside
functions in sphere_heave.py, so this module can be imported and run anywhere; if that
ever stops being true, test_module_imports_without_warpmpm fails loudly rather than the
whole file erroring at collection time.

The point of a sphere as the first external benchmark is that its geometry has closed
forms, so the mesh, the SDF and the hydrostatics can each be checked against exact truth
before a single GPU second is spent. That is what this file does.

Run:  python simulation/r5_physics/test_sphere_geometry.py
"""
from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sphere_heave as sh  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name}{('  ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


# --------------------------------------------------------------------------------------
def test_module_imports_without_warpmpm():
    print("\nmodule import")
    check("sphere_heave imports with no warpmpm present",
          "warpmpm" not in sys.modules,
          "(warpmpm imports are function-local by design)")


def test_mesh_is_closed_and_outward(diameter=sh.D_SPHERE):
    print("\nmesh topology and orientation")
    verts, faces = sh.sphere_mesh(diameter)
    r = 0.5 * diameter
    nv, nf = len(verts), len(faces)

    # every DIRECTED edge exactly once => closed and consistently oriented
    directed = Counter()
    for a, b, c in faces:
        directed[(a, b)] += 1
        directed[(b, c)] += 1
        directed[(c, a)] += 1
    check("every directed edge used exactly once",
          all(v == 1 for v in directed.values()),
          f"(max multiplicity {max(directed.values())})")

    undirected = Counter(tuple(sorted(e)) for e in directed)
    check("every undirected edge shared by exactly 2 faces",
          all(v == 2 for v in undirected.values()),
          f"({len(undirected)} edges)")

    euler = nv - len(undirected) + nf
    check("Euler characteristic V-E+F == 2", euler == 2,
          f"(V={nv} E={len(undirected)} F={nf} chi={euler})")

    # all vertices exactly on the sphere
    rad = np.linalg.norm(verts, axis=1)
    check("all vertices lie on the sphere",
          bool(np.max(np.abs(rad - r)) < 1e-12),
          f"(max |r-R| = {np.max(np.abs(rad - r)):.3e} m)")

    # signed volume: positive means faces wound OUTWARD
    v0, v1, v2 = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    signed = float(np.sum(np.einsum("ij,ij->i", v0, np.cross(v1, v2))) / 6.0)
    exact = 4.0 / 3.0 * math.pi * r ** 3
    check("signed volume positive (outward winding)", signed > 0,
          f"({signed:.9f} m3)")
    check("polyhedral volume within 0.5% of the exact sphere",
          abs(signed - exact) / exact < 5e-3,
          f"(exact {exact:.9f}, deficit {100 * (exact - signed) / exact:.4f}%)")


def test_sdf_margin_clears_the_band():
    print("\nSDF margin vs the engine's band guard")
    # The guard: add_sdf_collider refuses the collider unless the minimum stored SDF on
    # the grid's six faces exceeds band = dx. build_sdf sets cell = span/(res-1-2*margin),
    # so the stored margin distance is margin*cell.
    ok_all = True
    for lim, n_grid in sh.PLANNED_CONFIGS:
        dx = lim / n_grid
        res = 96 if dx >= 0.015 else 128
        span = sh.D_SPHERE
        margin = sh.sdf_margin_cells(span, dx, res, band_safety=2.0)
        cell = span / (res - 1 - 2 * margin)
        clearance = margin * cell
        ok = clearance >= 2.0 * dx
        ok_all &= ok
        print(f"      lim={lim} n_grid={n_grid} dx={dx:.6f} res={res} "
              f"margin={margin} cell={cell:.6f} clearance={clearance:.6f} "
              f"(need {2 * dx:.6f}) {'ok' if ok else 'SHORT'}")
    check("margin_cells clears 2*dx at every planned resolution", bool(ok_all))

    # The guard must raise when it CANNOT be satisfied, and must not raise when it can.
    # The first version of this check used dx=0.05 at res=16, which leaves 9 cells across
    # the mesh: the function was right to return, and the assertion was simply wrong.
    # Both directions are asserted now so a one-sided test cannot pass vacuously again.
    raised = False
    try:
        sh.sdf_margin_cells(sh.D_SPHERE, 0.20, res=16, band_safety=2.0)
    except ValueError:
        raised = True
    check("raises when the band cannot be cleared", raised,
          "(dx=0.20 at res=16 leaves 3 cells across the mesh)")

    margin_ok = sh.sdf_margin_cells(sh.D_SPHERE, 0.05, res=16, band_safety=2.0)
    check("does NOT raise when the band can be cleared",
          16 - 1 - 2 * margin_ok >= 8,
          f"(dx=0.05 at res=16 -> margin={margin_ok}, "
          f"{16 - 1 - 2 * margin_ok} cells across the mesh)")


def test_reference_quantities():
    print("\nclosed-form heave reference")
    ref = sh.sphere_reference()
    r = 0.15
    vol = 4.0 / 3.0 * math.pi * r ** 3
    check("volume", abs(ref["volume_m3"] - vol) < 1e-12, f"({ref['volume_m3']:.9f} m3)")
    check("mass from half submergence == 500 kg/m3 sphere",
          abs(ref["density_kg_m3"] - 500.0) < 1e-9,
          f"(m={ref['mass_kg']:.4f} kg, rho={ref['density_kg_m3']:.4f})")
    check("equilibrium buoyancy == weight",
          abs(ref["buoyancy_at_equilibrium_N"] - ref["mass_kg"] * sh.G) < 1e-9,
          f"({ref['buoyancy_at_equilibrium_N']:.4f} N)")
    check("heave stiffness == rho*g*pi*R^2",
          abs(ref["heave_stiffness_N_per_m"] - 1000.0 * 9.81 * math.pi * r ** 2) < 1e-9,
          f"({ref['heave_stiffness_N_per_m']:.4f} N/m)")
    # sanity band only: the added-mass ratio is an assumption, so the period is a
    # PREDICTION used to size the run, never a result.
    check("predicted natural period in a physically sane band",
          0.6 < ref["natural_period_s_predicted"] < 1.0,
          f"(T_n={ref['natural_period_s_predicted']:.4f} s, "
          f"assumed a33/m={ref['added_mass_ratio_assumed']})")
    check("artificial sound speed is the engine's, not water's",
          abs(ref["sound_speed_m_s"] - math.sqrt(1.1 * 1.5e5 / 1000.0)) < 1e-9,
          f"({ref['sound_speed_m_s']:.4f} m/s, real water is ~1481)")


def test_hydrostatic_cap_volume():
    print("\nspherical-cap hydrostatics (the fixed-mode reference)")
    r = 0.15
    # cap volume formula used in run(--fixed): V = pi h^2 (3R - h)/3
    def cap(h):
        return math.pi * h ** 2 * (3.0 * r - h) / 3.0
    check("cap at h=R is exactly half the sphere",
          abs(cap(r) - 0.5 * (4.0 / 3.0 * math.pi * r ** 3)) < 1e-15,
          f"({cap(r):.9f} m3)")
    check("cap at h=2R is the whole sphere",
          abs(cap(2 * r) - 4.0 / 3.0 * math.pi * r ** 3) < 1e-15)
    check("cap at h=0 is zero", abs(cap(0.0)) < 1e-18)
    check("equilibrium buoyancy from the cap == 69.343 N",
          abs(1000.0 * 9.81 * cap(r) - 69.3428) < 1e-3,
          f"({1000.0 * 9.81 * cap(r):.4f} N)")


def test_domain_sizing():
    print("\ndomain sizing: reflection window, deep water, Mach")
    ref = sh.sphere_reference()
    t_n = ref["natural_period_s_predicted"]
    lam = ref["radiated_wavelength_m"]
    cg = ref["group_velocity_m_s"]

    check("group velocity is well below sqrt(g*h)", cg < math.sqrt(9.81 * 0.5),
          f"(c_g={cg:.4f} vs sqrt(gh)={math.sqrt(9.81 * 0.5):.4f} m/s)")
    err = sh.deep_water_error(0.5, lam)
    check("0.5 m depth is deep water to better than 0.5%", err < 5e-3,
          f"(1-tanh(kh) = {err:.5f})")

    for lim in sorted({c[0] for c in sh.PLANNED_CONFIGS}):
        d_wall = 0.5 * lim - sh.SphereTank.WALL
        rt = 2.0 * d_wall / cg
        print(f"      lim={lim} m: wall at {d_wall:.3f} m, reflection returns at "
              f"{rt:.3f} s = {rt / t_n:.2f} T_n")
    smallest = min(c[0] for c in sh.PLANNED_CONFIGS)
    check("the SMALLEST planned domain still buys two clean natural periods",
          2.0 * (0.5 * smallest - sh.SphereTank.WALL) / cg / t_n >= 2.0,
          f"(lim={smallest} m gives "
          f"{2.0 * (0.5 * smallest - sh.SphereTank.WALL) / cg / t_n:.2f} T_n)")

    for f in sh.H0_OVER_D:
        h0 = f * sh.D_SPHERE
        ma = h0 * 2 * math.pi / t_n / ref["sound_speed_m_s"]
        print(f"      H0={f}D = {h0:.4f} m: peak Mach ~ {ma:.4f}"
              f"{'   <-- at the weak-compressibility limit' if ma > 0.09 else ''}")
    ma_max = sh.H0_OVER_D[-1] * sh.D_SPHERE * 2 * math.pi / t_n / ref["sound_speed_m_s"]
    check("largest drop stays below Ma 0.1", ma_max < 0.1, f"(Ma={ma_max:.4f})")


def test_floor_wall_guard():
    print("\nfixed floor/wall offsets vs dx")
    # The offsets are absolute so a refinement study is not silently a geometry change.
    # They must still clear 3dx / 4dx at the COARSEST planned dx.
    # Asserted over the WHOLE of PLANNED_CONFIGS. The first version hardcoded
    # dx_max = 1.5/80, which silently excluded the one config that failed.
    all_ok = True
    for lim, n_grid in sh.PLANNED_CONFIGS:
        dx = lim / n_grid
        ok = sh.SphereTank.FLOOR >= 3 * dx and sh.SphereTank.WALL >= 4 * dx
        all_ok &= ok
        print(f"      lim={lim} n_grid={n_grid} dx={dx:.6f}: need floor>={3 * dx:.5f} "
              f"wall>={4 * dx:.5f}  have {sh.SphereTank.FLOOR}/{sh.SphereTank.WALL}"
              f"  {'ok' if ok else 'TOO COARSE'}")
    check("EVERY planned config clears both offsets", bool(all_ok))


def main():
    print("sphere_heave geometry checks (no GPU, no warpmpm)")
    test_module_imports_without_warpmpm()
    test_mesh_is_closed_and_outward()
    test_sdf_margin_clears_the_band()
    test_reference_quantities()
    test_hydrostatic_cap_volume()
    test_domain_sizing()
    test_floor_wall_guard()
    print(f"\n{'ALL PASS' if not FAILURES else 'FAILURES: ' + ', '.join(FAILURES)}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
