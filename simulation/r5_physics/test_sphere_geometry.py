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


def test_table1_is_self_consistent():
    """Table 1 over-determines the sphere, so it can be checked against itself.

    D, m and rho_w are three independent READ values, and half submergence is a stated
    property of the model. Any two of them predict the third. That is a check on my
    transcription of the table, which is the step most likely to be wrong.
    """
    print("\nKramer 2021 Table 1, internal consistency")
    r = 0.5 * sh.D_SPHERE
    vol = 4.0 / 3.0 * math.pi * r ** 3
    m_half = sh.RHO_W_BENCHMARK * vol / 2.0
    check("Table 1 m reproduces from D and rho_w by half submergence",
          abs(sh.M_SPHERE - m_half) < 1.0e-3,
          f"(Table 1 m={sh.M_SPHERE} kg, half submergence gives {m_half:.5f} kg, "
          f"gap {abs(sh.M_SPHERE - m_half):.6f} kg vs 1e-3 rounding)")
    check("Table 1 seabed depth d == 3D as section 1.1 states",
          abs(sh.SEABED_DEPTH_M - 3.0 * sh.D_SPHERE) < 1e-12,
          f"(d={sh.SEABED_DEPTH_M} m, 3D={3 * sh.D_SPHERE} m)")
    check("Table 1 H0 values are exactly {0.1D, 0.3D, 0.5D}",
          all(abs(a - b) < 1e-12 for a, b in zip(sh.H0_OVER_D, (0.1, 0.3, 0.5))),
          f"({sh.H0_M} m -> {tuple(round(x, 6) for x in sh.H0_OVER_D)} D)")
    check("CoG sits BELOW the geometric centre (ballasted, stable in pitch)",
          sh.COG_M[2] < 0 and abs(sh.COG_M[2]) < r,
          f"(CoG_z={sh.COG_M[2] * 1000:.1f} mm, inside the sphere)")
    # The superseded derivation is asserted as WRONG, so nobody reintroduces it.
    check("the old rho_w=1000 derivation is measurably wrong, not a rounding",
          abs(1000.0 * vol / 2.0 - sh.M_SPHERE) > 1.0e-3,
          f"(rho_w=1000 gives {1000.0 * vol / 2.0:.5f} kg vs Table 1 {sh.M_SPHERE})")


def test_reference_quantities():
    print("\nclosed-form heave reference")
    ref = sh.sphere_reference()
    r = 0.15
    vol = 4.0 / 3.0 * math.pi * r ** 3
    check("volume", abs(ref["volume_m3"] - vol) < 1e-12, f"({ref['volume_m3']:.9f} m3)")
    check("mass is Table 1's READ value, not a derivation",
          abs(ref["mass_kg"] - sh.M_SPHERE) < 1e-12,
          f"(m={ref['mass_kg']:.4f} kg, rho={ref['density_kg_m3']:.2f} kg/m3)")
    # Table 1 rounds m to 7.056 kg, where exact half submergence needs 7.05586 kg. The
    # published sphere is therefore 0.14 g HEAVY and does not float exactly at the
    # equator. Loosening a force tolerance would hide that; the meaningful test is what
    # the residual does to the equilibrium position, against the benchmark's OWN
    # displacement tolerance. Smallest drop is 30 mm, so the tolerance there is 0.09 mm.
    resid_N = ref["weight_N"] - ref["buoyancy_at_equilibrium_N"]
    offset_m = resid_N / ref["heave_stiffness_N_per_m"]
    tol_m = sh.published_displacement_tolerance_m(min(sh.H0_M))
    check("Table 1's rounded mass is not exactly neutrally floating",
          abs(resid_N) > 1e-4,
          f"(residual {resid_N * 1000:+.3f} mN, sphere is "
          f"{1000 * (sh.M_SPHERE - ref['mass_from_half_submergence_kg']):+.3f} g heavy)")
    check("but the implied equilibrium offset is far below the benchmark tolerance",
          abs(offset_m) < 0.05 * tol_m,
          f"(offset {offset_m * 1e6:.2f} um vs tolerance {tol_m * 1000:.3f} mm at the "
          f"smallest drop, a factor of {tol_m / abs(offset_m):.0f})")
    check("heave stiffness == rho_w*g*pi*R^2",
          abs(ref["heave_stiffness_N_per_m"]
              - sh.RHO_W_BENCHMARK * sh.G_ENGINE * math.pi * r ** 2) < 1e-9,
          f"({ref['heave_stiffness_N_per_m']:.4f} N/m)")
    # sanity band only: the added-mass ratio is an assumption, so the period is a
    # PREDICTION used to size the run, never a result.
    check("predicted natural period in a physically sane band",
          0.6 < ref["natural_period_s_predicted"] < 1.0,
          f"(T_n={ref['natural_period_s_predicted']:.4f} s, "
          f"assumed a33/m={ref['added_mass_ratio_assumed']})")
    check("artificial sound speed is the engine's, not water's",
          abs(ref["sound_speed_m_s"]
              - math.sqrt(1.1 * 1.5e5 / sh.RHO_W_BENCHMARK)) < 1e-9,
          f"({ref['sound_speed_m_s']:.4f} m/s, real water is ~1481)")


def test_gravity_bias_is_small_but_stated():
    print("\nirreducible gravity mismatch (engine 9.81 vs benchmark 9.82)")
    ref = sh.sphere_reference()
    bias = abs(ref["natural_period_gravity_bias_frac"])
    check("gravity bias is negative in g and halves in period",
          abs(abs(sh.GRAVITY_BIAS_FRACTION) / 2.0 - bias) / bias < 0.01,
          f"(g bias {sh.GRAVITY_BIAS_FRACTION * 100:+.4f}%, "
          f"period bias {ref['natural_period_gravity_bias_frac'] * 100:+.4f}%)")
    dt_period = abs(ref["natural_period_s_predicted"]
                    - ref["natural_period_s_at_benchmark_g"])
    check("period bias is below 1 ms and cannot be the limiting error",
          dt_period < 1e-3, f"({dt_period * 1000:.4f} ms on a "
          f"{ref['natural_period_s_predicted']:.4f} s period)")
    # The draft must be untouched: weight and stiffness both scale with g.
    r = 0.15
    vol = 4.0 / 3.0 * math.pi * r ** 3
    draft = [sh.M_SPHERE / (sh.RHO_W_BENCHMARK * vol) for _ in (0, 1)]
    check("equilibrium submerged FRACTION is independent of g",
          abs(draft[0] - draft[1]) < 1e-15,
          f"(submerged fraction {draft[0]:.6f}, i.e. {'half' if abs(draft[0] - 0.5) < 1e-3 else 'NOT half'})")


def test_uncertainty_semantics():
    print("\nbenchmark uncertainty: absolute, per drop height, average, 95%")
    check("uncertainty is recorded as a fraction of DROP HEIGHT",
          abs(sh.UNCERTAINTY_FRACTION_OF_DROP - 0.003) < 1e-12)
    check("it is flagged as an average at 95%, not a per-sample bound",
          sh.UNCERTAINTY_IS_AVERAGE_AT_95PCT is True)
    for h0 in sh.H0_M:
        tol = sh.published_displacement_tolerance_m(h0)
        print(f"      H0={h0 * 1000:5.1f} mm -> tolerance {tol * 1000:.3f} mm")
    tols = [sh.published_displacement_tolerance_m(h) for h in sh.H0_M]
    check("the three tolerances are 0.09 / 0.27 / 0.45 mm",
          all(abs(a - b) < 1e-9 for a, b in zip(tols, (9e-5, 2.7e-4, 4.5e-4))))
    check("tolerance SCALES with drop height (it is not one flat number)",
          tols[-1] > tols[0] * 4.9,
          f"({tols[-1] / tols[0]:.1f}x from the smallest drop to the largest)")


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
    # The number the --fixed pilot will be read against. It moved when rho_w did:
    # 69.3428 N at the assumed rho_w=1000, 69.2180 N at Table 1's 998.2. Anything that
    # still quotes 69.34 is quoting the superseded derivation.
    f_eq = sh.RHO_W_BENCHMARK * sh.G_ENGINE * cap(r)
    check("equilibrium buoyancy at Table 1 rho_w and engine g",
          abs(f_eq - 69.2180) < 1e-3, f"({f_eq:.4f} N; the old rho_w=1000 value was "
          f"{1000.0 * 9.81 * cap(r):.4f} N, a {100 * (1000.0 * 9.81 * cap(r) - f_eq) / f_eq:.3f}% overstatement)")
    check("it equals the sphere's weight at the same g",
          abs(f_eq - sh.M_SPHERE * sh.G_ENGINE) < 2e-3,
          f"(W={sh.M_SPHERE * sh.G_ENGINE:.4f} N)")


def test_domain_sizing():
    print("\ndomain sizing: reflection window, deep water, Mach")
    ref = sh.sphere_reference()
    t_n = ref["natural_period_s_predicted"]
    lam = ref["radiated_wavelength_m"]
    cg = ref["group_velocity_m_s"]

    cp = ref["phase_velocity_m_s"]
    csh = math.sqrt(9.81 * 0.5)
    check("group < phase < sqrt(g*h), so the convention choice is not cosmetic",
          cg < cp < csh,
          f"(c_g={cg:.4f} < c_phase={cp:.4f} < sqrt(gh)={csh:.4f} m/s)")
    err = sh.deep_water_error(0.5, lam)
    check("0.5 m depth is deep water to better than 0.5%", err < 5e-3,
          f"(1-tanh(kh) = {err:.5f})")

    # CORRECTED 2026-08-16. The previous version of this check asserted that the smallest
    # planned domain "buys two clean natural periods" using the GROUP velocity, and it
    # passed. Kramer 2021 section 3.5 p.16 does this calculation with the PHASE celerity
    # and calls that the conservative estimate. On the benchmark's own convention the old
    # assertion is false at lim=1.2 (1.06 T_n, not 2.12). This is the failure mode the
    # docs claim to have eliminated: a check that picks its own operating point passes.
    print(f"      {'lim':>5} {'wall':>7} {'group':>12} {'KRAMER phase':>14} {'sqrt(gh)':>12}")
    for lim in sorted({c[0] for c in sh.PLANNED_CONFIGS}):
        d = 0.5 * lim - sh.SphereTank.WALL
        vals = [2.0 * d / c / t_n for c in (cg, cp, csh)]
        print(f"      {lim:>5} {d:>7.3f} {vals[0]:>11.2f}T {vals[1]:>13.2f}T {vals[2]:>11.2f}T")
    largest = max(c[0] for c in sh.PLANNED_CONFIGS)
    got = 2.0 * (0.5 * largest - sh.SphereTank.WALL) / cp / t_n
    check("SOME planned domain buys two clean periods on KRAMER'S convention",
          got >= 2.0, f"(lim={largest} m gives {got:.2f} T_n on phase celerity)")
    smallest = min(c[0] for c in sh.PLANNED_CONFIGS)
    small_got = 2.0 * (0.5 * smallest - sh.SphereTank.WALL) / cp / t_n
    check("and the smallest is HONESTLY LABELLED as sub-two-period, not asserted past it",
          small_got < 2.0,
          f"(lim={smallest} m gives {small_got:.2f} T_n; it is kept as a cheap pilot, "
          f"not as a comparison domain)")

    for h0 in sh.H0_M:
        ma = h0 * 2 * math.pi / t_n / ref["sound_speed_m_s"]
        print(f"      H0={h0 * 1000:5.1f} mm: peak Mach ~ {ma:.4f}"
              f"{'   <-- at the weak-compressibility limit' if ma > 0.09 else ''}")
    # CORRECTED 2026-08-16. The previous assertion was "largest drop stays below Ma 0.1"
    # and it passed at 0.0944 using the LINEAR peak-velocity estimate H0*omega. Kramer
    # 2021 Figure 17b (p.15) shows a measured peak heave speed at H0=0.5D of roughly
    # 1.3 m/s, which gives Ma ~ 0.10. So the old check passed on the estimator most
    # favourable to passing. It is replaced by a reported band, not a pass/fail, because
    # a threshold this close to the true value is not something a self-chosen estimator
    # should be allowed to adjudicate.
    ma_lin = sh.H0_M[-1] * 2 * math.pi / t_n / ref["sound_speed_m_s"]
    ma_meas = 1.3 / ref["sound_speed_m_s"]
    print(f"      largest drop Mach: linear estimate {ma_lin:.4f}, "
          f"from Kramer Fig 17b measured peak ~1.3 m/s: {ma_meas:.4f}")
    check("the largest drop is reported as AT the weak-compressibility limit, not below it",
          ma_lin < 0.1 <= ma_meas * 1.02,
          f"(linear {ma_lin:.4f} < 0.1 <= measured {ma_meas:.4f}; the two straddle the "
          f"limit, so any number from the 0.5D case must carry its Mach)")


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
    test_table1_is_self_consistent()
    test_reference_quantities()
    test_gravity_bias_is_small_but_stated()
    test_uncertainty_semantics()
    test_hydrostatic_cap_volume()
    test_domain_sizing()
    test_floor_wall_guard()
    print(f"\n{'ALL PASS' if not FAILURES else 'FAILURES: ' + ', '.join(FAILURES)}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
