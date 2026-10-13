"""Tests for analysis/gci_least_squares.py, the grid-convergence check.

Three groups:

  * Published worked examples, reproduced to their printed precision: Celik et al. (2008) Table 1,
    and the KCS ship-resistance example and Table 2 in the ITTC uncertainty procedure 7.5-03-01-01
    (2024 revision), including the one value in Celik's table that does not follow its own Eq. 6.
  * Synthetic ladders with known answers: exact second-order data must recover p = 2 and the exact
    limit; oscillatory, scattered or out-of-window ladders must never be reported as converged; three
    grid levels can never satisfy the four-level rule.
  * This project's own force ladders, as recorded. The Stage 1e streamwise force at 0.30 m and 1.5 m/s
    on grids of 0.075, 0.05 and 0.0375 m gives apparent order 0.41 and GCI 221 percent: not in the
    asymptotic range, so no convergence is claimed (the steady-force dataset card states the same).
    The Stage 1 ladder is kept as input only: its forces are withdrawn as force data, and an earlier
    version of the analysis scored that monotone ladder as converged at GCI 667 percent, which these
    tests now forbid. No drag coefficient appears here, because none from these campaigns is valid.
"""
import ast
import contextlib
import io
import json
import math
import os
import sys
import unittest

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))

import gci_least_squares as g  # noqa: E402

ANALYZE_STAGE1 = os.path.join(REPO, "tests", "data", "legacy_gci_stage1.py")
STAGE1E_JSON = os.path.join(REPO, "tests", "data", "stage1e_matched_window.json")
STAGE1E_RUNS = ("Pf_d030_u150_W20_dx0375_fo005_t30", "Pf_d030_u150_W20_dx050_fo005", "Pf_d030_u150_W20_dx075_fo005")
LADDER_H = [0.0375, 0.05, 0.075]
STAGE1E_FX = [1557.292538834614, 1905.8386116027832, 2473.262591435359]
STAGE1E_FX_SE = [20.803514432361542, 53.1954806484743, 42.4711889622872]
STAGE1E_FX_FINDINGS = [1557.0, 1906.0, 2473.0]
STAGE1_FX = [1439.7198285113325, 1750.9969937670362, 2211.2354781601457]
CELIK_CELLS = ((18000, 8000, 4500), (18000, 4500, 980), (18000, 4500, 980))
CELIK_PHI = ((6.063, 5.972, 5.863), (10.7880, 10.7250, 10.6050), (6.0042, 5.9624, 6.0909))
CELIK_PRINTED = ((1.53, 6.1685, 1.5, 1.7, 2.2), (0.75, 10.8801, 0.6, 0.9, 1.1), (1.51, 6.0269, 0.7, 0.4, 0.5))
KCS_CELLS = (12444794, 7368997, 3432556, 1902446, 1084560, 642810)
KCS_CFM = (2.8074, 2.8091, 2.8476, 2.8402, 2.8504, 2.8571)
KCS_CTM = (3.0632, 3.0708, 3.1253, 3.1482, 3.1710, 3.1901)
FOUR_H = [0.025, 0.0375, 0.05, 0.075]
NOISY_PHI = [100.0 + 2000.0 * x ** 1.5 + d for x, d in zip(FOUR_H, (0.15, -0.2, 0.25, -0.1))]
SCATTERED_PHI = [100.0 + 2000.0 * x ** 1.5 + d for x, d in zip(FOUR_H, (6.0, -6.0, 6.0, -6.0))]


def skip(msg):
    raise unittest.SkipTest(msg)


def table1_h(i):
    return [g.cell_size(n, dim=2) for n in CELIK_CELLS[i]]


def within(value, printed, half_unit):
    return abs(value - printed) <= half_unit + 1e-12


def cli(args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = g.main([str(a) for a in args])
    return rc, out.getvalue(), err.getvalue()


def legacy_gci():
    if not os.path.isfile(ANALYZE_STAGE1):
        skip("legacy GCI fixture is not at " + ANALYZE_STAGE1)
    with open(ANALYZE_STAGE1, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    node = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "gci"), None)
    if node is None:
        skip("legacy GCI fixture no longer defines gci()")
    ns = {"np": np, "math": math}
    exec(compile(ast.Module(body=[node], type_ignores=[]), ANALYZE_STAGE1, "exec"), ns)
    return ns["gci"]


def weights(x, weighted):
    w = 1.0 / x if weighted else np.ones_like(x)
    return w / w.sum()


def normal_equations(cols, x, phi, w):
    A = np.column_stack([np.ones_like(x)] + cols)
    return np.linalg.solve(A.T @ (w[:, None] * A), A.T @ (w * phi))


def test_celik_2008_table1_p_extrapolated_value_and_gci_to_printed_precision():
    for i, (p, ext, ea, _, gci) in enumerate(CELIK_PRINTED):
        c = g.celik(table1_h(i), CELIK_PHI[i])
        assert c["converged"], i
        assert within(c["p"], p, 0.005), (i, c["p"])
        assert within(c["phi_ext21"], ext, 0.00005), (i, c["phi_ext21"])
        assert within(100 * c["gci_fine21"], gci, 0.05), (i, c["gci_fine21"])
        assert within(100 * c["e_a21"], ea, 0.05), (i, c["e_a21"])


def test_celik_2008_table1_e_ext_columns_1_and_3():
    for i in (0, 2):
        c = g.celik(table1_h(i), CELIK_PHI[i])
        assert within(100 * c["e_ext21"], CELIK_PRINTED[i][3], 0.05), (i, c["e_ext21"])


def test_celik_2008_table1_column2_e_ext_follows_eq6_not_the_printed_0p9():
    c = g.celik(table1_h(1), CELIK_PHI[1])
    assert abs(100 * c["e_ext21"] - 0.8465) < 0.0005, c["e_ext21"]
    assert round(100 * c["e_ext21"], 1) == 0.8
    f1 = CELIK_PHI[1][0]
    assert round(100 * abs((c["phi_ext21"] - f1) / f1), 1) == 0.9


def test_celik_2008_table1_column1_needs_ratios_from_cell_counts():
    c = g.celik([1.0, 1.5, 1.5 * 1.333], CELIK_PHI[0])
    assert round(c["p"], 2) == 1.54, c["p"]
    assert not within(c["phi_ext21"], 6.1685, 0.00005), c["phi_ext21"]


def test_celik_2008_table1_column3_is_flagged_oscillatory_and_not_asymptotic():
    c = g.celik(table1_h(2), CELIK_PHI[2])
    assert c["oscillatory"] and not c["monotone"] and c["s"] == -1.0
    r = g.assess(table1_h(2), CELIK_PHI[2])
    assert r["verdict"] == g.VERDICT_NOT and not r["passed"]
    assert any("oscillatorily" in s for s in r["reasons"])


def test_synthetic_oscillatory_sequences_are_flagged_and_never_pass():
    c = g.celik(LADDER_H, [1.0, 1.1, 0.95])
    assert c["oscillatory"] and c["ratio"] < 0
    rc, out, _ = cli(["--h"] + LADDER_H + ["--phi", 1.0, 1.1, 0.95, "--stat-unc", 0, 0, 0])
    assert rc == 0 and "oscillatory convergence" in out and "PASS" not in out
    r = g.assess([1.0, 1.5, 2.25, 3.375], [1.00, 1.02, 0.99, 1.03], stat_unc=[0.0] * 4)
    assert r["celik"]["oscillatory"] and r["eca_hoekstra"]["re_selected"] is None
    assert r["verdict"] == g.VERDICT_NOT and not r["passed"]


def test_celik_agrees_with_the_legacy_stage1_gci_on_the_same_inputs():
    legacy = legacy_gci()
    cases = [(table1_h(i), CELIK_PHI[i]) for i in range(3)]
    for phi in (STAGE1E_FX, STAGE1E_FX_FINDINGS, STAGE1_FX, [1.0, 1.1, 0.95],
                [1.0 + 0.5 * x * x for x in LADDER_H]):
        cases.append((LADDER_H, phi))
    for h, phi in cases:
        a, b = g.celik(h, phi), legacy(h, phi)
        assert b["status"] != "degenerate", phi
        assert a["oscillatory"] == bool(b["oscillatory"]), (phi, a["oscillatory"], b["oscillatory"])
        for ka, kb in (("p", "p"), ("phi_ext21", "phi_ext"), ("e_a21", "e_a21"), ("e_ext21", "e_ext21"),
                       ("gci_fine21", "gci_fine")):
            assert math.isclose(a[ka], float(b[kb]), rel_tol=1e-8, abs_tol=1e-12), (phi, ka, a[ka], float(b[kb]))


def test_exact_second_order_three_levels_recover_p_and_phi0_but_cannot_pass():
    phi = [1.0 + 0.5 * x * x for x in LADDER_H]
    c = g.celik(LADDER_H, phi)
    assert abs(c["p"] - 2.0) < 1e-9 and abs(c["phi_ext21"] - 1.0) < 1e-9, (c["p"], c["phi_ext21"])
    r = g.assess(LADDER_H, phi, stat_unc=[0.0, 0.0, 0.0])
    assert r["verdict"] == g.VERDICT_THREE and not r["four_grid_rule"] and not r["passed"]


def test_exact_second_order_four_levels_least_squares_recover_p_and_phi0_and_pass():
    phi = [1.0 + 0.5 * x * x for x in FOUR_H]
    e = g.eca_hoekstra(FOUR_H, phi)
    for f in e["fits"][:2]:
        assert abs(f["p"] - 2.0) < 1e-9 and abs(f["phi0"] - 1.0) < 1e-9, (f["weighted"], f["p"], f["phi0"])
    assert abs(e["phi0"] - 1.0) < 1e-9 and e["reliable"] and e["fs"] == g.FS_RELIABLE
    r = g.assess(FOUR_H, phi, stat_unc=[0.0] * 4)
    assert r["verdict"] == g.VERDICT_ASYMPTOTIC and r["passed"], r["reasons"]
    rc, out, _ = cli(["--h"] + FOUR_H + ["--phi"] + [repr(v) for v in phi] + ["--stat-unc", 0, 0, 0, 0])
    assert rc == 0 and "decision: PASS" in out and "four-grid rule: met" in out


def test_four_levels_without_statistical_uncertainty_do_not_pass():
    r = g.assess(FOUR_H, [1.0 + 0.5 * x * x for x in FOUR_H])
    assert r["verdict"] == g.VERDICT_ASYMPTOTIC and not r["passed"]
    assert any("statistical uncertainty not supplied" in s for s in r["reasons"])


def test_noisy_four_levels_exercise_the_least_squares_branch_with_eq20():
    e = g.eca_hoekstra(FOUR_H, NOISY_PHI)
    sel = e["selected"]
    assert sel["kind"] == "RE" and e["eq"] == "Eq. (20)" and e["fs"] == g.FS_RELIABLE
    assert 0.5 <= e["p"] < 2.1 and e["sigma"] < e["dphi"]
    phi = np.array(NOISY_PHI)
    x = np.array(FOUR_H) / FOUR_H[0]
    assert math.isclose(e["dphi"], (phi.max() - phi.min()) / 3, rel_tol=1e-12)
    assert np.allclose(e["u"], e["fs"] * sel["eps"] + e["sigma"] + np.abs(phi - sel["fit"]), rtol=1e-12, atol=0)
    w = weights(x, sel["weighted"])
    res = phi - sel["fit"]
    assert math.isclose(e["sigma"], math.sqrt(np.sum(4 * w * res ** 2) / (4 - 3)), rel_tol=1e-12)
    xp, lx = x ** sel["p"], np.log(x)
    terms = (np.sum(w * phi * xp * lx), sel["phi0"] * np.sum(w * xp * lx), sel["coef"][0] * np.sum(w * xp * xp * lx))
    assert abs(terms[0] - terms[1] - terms[2]) < 1e-9 * max(abs(t) for t in terms), terms
    best = np.inf
    for q in np.arange(0.01, 8.0, 0.0005):
        phi0, alpha = normal_equations([x ** q], x, phi, w)
        best = min(best, float(np.sum(w * (phi - phi0 - alpha * x ** q) ** 2)))
    assert sel["S"] <= best * (1.0 + 1e-9), (sel["S"], best)
    for f in e["fits"][2:]:
        cols = {"d1": [x], "d2": [x ** 2], "d12": [x, x ** 2]}[f["kind"]]
        coef = normal_equations(cols, x, phi, weights(x, f["weighted"]))
        assert np.allclose([f["phi0"]] + f["coef"], coef, rtol=1e-9, atol=1e-9), (f["kind"], f["weighted"])


def test_scattered_four_levels_use_eq21_and_fs3():
    e = g.eca_hoekstra(FOUR_H, SCATTERED_PHI)
    assert e["sigma"] >= e["dphi"] and e["eq"] == "Eq. (21)" and e["fs"] == g.FS_UNRELIABLE and not e["reliable"]
    phi = np.array(SCATTERED_PHI)
    sel = e["selected"]
    expect = 3.0 * (e["sigma"] / e["dphi"]) * (sel["eps"] + e["sigma"] + np.abs(phi - sel["fit"]))
    assert np.allclose(e["u"], expect, rtol=1e-12, atol=0)
    r = g.assess(FOUR_H, SCATTERED_PHI, stat_unc=[0.0] * 4)
    assert r["verdict"] == g.VERDICT_NOT and not r["passed"]


def test_p_between_2_and_2p1_uses_fixed_order_fits_with_fs_1p25():
    e = g.eca_hoekstra(FOUR_H, [100.0 + 5000.0 * x ** 2.05 for x in FOUR_H])
    assert 2.0 < e["p"] < 2.1 and e["selected"]["kind"] in ("d1", "d2") and e["fs"] == g.FS_RELIABLE, e["branch"]


def test_ittc_2024_kcs_fits_reproduce_and_the_paper_rules_replace_its_fs():
    h = [g.cell_size(n) for n in KCS_CELLS]
    cases = ((KCS_CFM, 0.0898, 0.0041, -1.209, 2.8804, 0.0099, 0.1186),
             (KCS_CTM, 0.1584, 0.0037, -0.08351, None, 0.02538, 0.2067))
    for phi, eps_w12, sigma_w12, p_wre, phi0_wre, dphi, u_ittc in cases:
        e = g.eca_hoekstra(h, phi)
        fits = {(f["kind"], f["weighted"]): f for f in e["fits"]}
        w12, wre = fits[("d12", True)], fits[("RE", True)]
        assert abs(w12["eps"][0] - eps_w12) <= 0.0002, w12["eps"][0]
        assert round(w12["sigma"] / math.sqrt(6), 4) == sigma_w12, w12["sigma"]
        assert abs(wre["p"] - p_wre) <= 0.01, wre["p"]
        if phi0_wre is not None:
            assert abs(wre["phi0"] - phi0_wre) <= 0.0005, wre["phi0"]
        assert abs(e["dphi"] - dphi) <= 0.00005 + 1e-12, e["dphi"]
        assert e["re_selected"] is None and e["fs"] == g.FS_UNRELIABLE
        assert e["selected"]["kind"] == "d12" and not e["selected"]["weighted"]
        assert e["u"][0] > 2.0 * u_ittc, e["u"][0]


def test_xing_stern_factor_of_safety_matches_ittc_2024_eq8_and_table2():
    assert round(g.xing_stern_fs(0.845), 2) == 1.73 and round(g.xing_stern_fs(0.558), 2) == 1.98
    assert round(g.xing_stern_fs(0.845) * 0.00964, 4) == 0.0167
    assert round(g.xing_stern_fs(0.558) * 0.01274, 4) == 0.0252
    assert math.isclose(g.xing_stern_fs(1.0), 1.6) and math.isclose(g.xing_stern_fs(1.0 + 1e-12), 1.6, rel_tol=1e-9)
    assert math.isclose(g.xing_stern_fs(1.5), 9.8)
    assert all(math.isnan(g.xing_stern_fs(v)) for v in (0.0, -0.3))
    xs = g.xing_stern(g.celik(LADDER_H, STAGE1E_FX), 2.0)
    assert xs["defined"] and math.isclose(xs["fs"], 2.45 - 0.85 * xs["P"])
    assert not g.xing_stern(g.celik(LADDER_H, [1.0, 1.1, 0.95]), 2.0)["defined"]


def test_stage1e_ladder_reproduces_the_recorded_numbers_and_is_not_asymptotic():
    c = g.celik(LADDER_H, STAGE1E_FX)
    assert round(c["p"], 2) == 0.41 and round(100 * c["gci_fine21"], 1) == 221.0, (c["p"], c["gci_fine21"])
    f = g.celik(LADDER_H, STAGE1E_FX_FINDINGS)
    assert round(f["p"], 2) == 0.41 and round(100 * f["gci_fine21"], 1) == 224.7, (f["p"], f["gci_fine21"])
    for phi in (STAGE1E_FX, STAGE1E_FX_FINDINGS):
        r = g.assess(LADDER_H, phi)
        assert r["verdict"] == g.VERDICT_NOT and not r["passed"] and not r["four_grid_rule"]
    r = g.assess(LADDER_H, STAGE1E_FX, stat_unc=STAGE1E_FX_SE)
    assert r["stat"]["ok"] and not r["passed"] and r["verdict"] == g.VERDICT_NOT


def test_cli_on_the_stage1e_findings_values_says_not_asymptotic_and_never_prints_pass():
    rc, out, _ = cli(["--h", 0.075, 0.05, 0.0375, "--phi", 2473, 1906, 1557])
    assert rc == 0
    assert "verdict: " + g.VERDICT_NOT in out
    assert "four-grid rule: NOT MET" in out and "Three levels can never satisfy this rule" in out
    assert "Celik et al. (2008)" in out and "Xing and Stern (2010)" in out and "Eca and Hoekstra (2014)" in out
    assert "PASS" not in out


def test_stage1_monotone_ladder_once_scored_pass_at_gci_667_percent_never_passes():
    c = g.celik(LADDER_H, STAGE1_FX)
    assert c["monotone"] and round(c["p"], 2) == 0.14 and round(c["phi_ext21"]) == -6248
    assert round(100 * c["gci_fine21"]) == 667
    r = g.assess(LADDER_H, STAGE1_FX, stat_unc=[0.0, 0.0, 0.0])
    assert not r["passed"] and r["verdict"] == g.VERDICT_NOT and not r["physical"]
    rc, out, _ = cli(["--h"] + LADDER_H + ["--phi"] + STAGE1_FX + ["--stat-unc", 0, 0, 0])
    assert rc == 0 and "PASS" not in out and "not asymptotic" in out
    phi4 = STAGE1_FX + [STAGE1_FX[2] + 1.3 * (STAGE1_FX[2] - STAGE1_FX[1])]
    r4 = g.assess(LADDER_H + [0.1], phi4, stat_unc=[0.0] * 4)
    assert r4["eca_hoekstra"]["reliable"] and not r4["triplet_ok"] and not r4["passed"]
    assert r4["verdict"] == g.VERDICT_NOT


def test_monotone_power_law_ladders_pass_only_inside_the_window():
    hs = [0.025, 0.0375, 0.05, 0.075, 0.1, 0.15]
    for p_true in (0.1, 0.25, 0.4, 2.3, 3.0, 4.0):
        for n in (3, 4, 5, 6):
            r = g.assess(hs[:n], [100.0 + 5000.0 * x ** p_true for x in hs[:n]], stat_unc=[0.0] * n)
            assert not r["passed"] and r["verdict"] != g.VERDICT_ASYMPTOTIC, (p_true, n)
    for p_true in (0.6, 1.0, 1.5, 2.0):
        r3 = g.assess(hs[:3], [100.0 + 5000.0 * x ** p_true for x in hs[:3]], stat_unc=[0.0] * 3)
        assert not r3["passed"] and r3["verdict"] == g.VERDICT_THREE, p_true
        for n in (4, 5, 6):
            r = g.assess(hs[:n], [100.0 + 5000.0 * x ** p_true for x in hs[:n]], stat_unc=[0.0] * n)
            assert r["passed"] and r["verdict"] == g.VERDICT_ASYMPTOTIC, (p_true, n, r["reasons"])


def test_three_levels_can_never_satisfy_the_four_grid_rule():
    for p_true in (0.6, 1.0, 1.5, 2.0):
        phi = [1.0 + 0.5 * x ** p_true for x in LADDER_H]
        r = g.assess(LADDER_H, phi, stat_unc=[0.0, 0.0, 0.0])
        assert not r["four_grid_rule"] and not r["passed"] and r["verdict"] == g.VERDICT_THREE, p_true
        assert not r["eca_hoekstra"]["run"]
        rc, out, _ = cli(["--h"] + LADDER_H + ["--phi"] + [repr(v) for v in phi] + ["--stat-unc", 0, 0, 0])
        assert rc == 0 and "four-grid rule: NOT MET" in out and "PASS" not in out


def test_statistical_uncertainty_is_combined_and_gates_the_decision():
    phi = [1.0 + 0.5 * x * x for x in FOUR_H]
    small = g.assess(FOUR_H, phi, stat_unc=[1e-7] * 4)
    assert small["passed"] and math.isclose(small["u_total"], math.hypot(small["u_report"], 2e-7), rel_tol=1e-12)
    loose = g.assess(FOUR_H, phi, stat_unc=[1e-4] * 4)
    assert loose["stat"]["resolved"].all() and not loose["stat"]["order_ok"].all() and not loose["passed"]
    assert any("one order of magnitude" in s for s in loose["reasons"])
    noisy = g.assess(FOUR_H, phi, stat_unc=[2e-4] * 4)
    assert not noisy["stat"]["resolved"][0] and not noisy["passed"]
    assert any("combined standard uncertainty" in s for s in noisy["reasons"])
    k3 = g.assess(FOUR_H, phi, stat_unc=[1e-7] * 4, stat_k=3.0)
    assert math.isclose(k3["u_total"], math.hypot(k3["u_report"], 3e-7), rel_tol=1e-12)


def test_hardcoded_stage1e_values_match_the_recorded_analysis():
    if not os.path.isfile(STAGE1E_JSON):
        skip("Stage 1e fixture not present at " + STAGE1E_JSON)
    with open(STAGE1E_JSON, encoding="utf-8") as fh:
        d = json.load(fh)["runs"]
    for run, h, fx, se in zip(STAGE1E_RUNS, LADDER_H, STAGE1E_FX, STAGE1E_FX_SE):
        assert math.isclose(d[run]["dx"], h, rel_tol=1e-12), run
        assert d[run]["Fx"] == fx and d[run]["Fx_se_eff"] == se, run


def test_bad_inputs_are_refused():
    for h, phi in (([0.1, 0.2], [1.0, 2.0]), ([0.1, 0.1, 0.2], [1.0, 2.0, 3.0]),
                   ([0.1, -0.2, 0.3], [1.0, 2.0, 3.0]), ([0.1, 0.2, 0.3], [1.0, 2.0])):
        try:
            g.assess(h, phi)
        except ValueError:
            continue
        raise AssertionError("accepted h %s phi %s" % (h, phi))
    try:
        g.assess(LADDER_H, STAGE1E_FX, stat_unc=[1.0, 2.0])
    except ValueError:
        pass
    else:
        raise AssertionError("accepted a statistical uncertainty list of the wrong length")
    rc, out, err = cli(["--h", 0.1, 0.2, "--phi", 1, 2])
    assert rc == 2 and "error:" in err and out == ""


def main():
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    fails, skips = [], []
    print("gci_least_squares: %d tests\n" % len(tests))
    for name, fn in tests:
        try:
            fn()
            print("  PASS  " + name)
        except unittest.SkipTest as exc:
            skips.append(name)
            print("  SKIP  %s: %s" % (name, exc))
        except AssertionError as exc:
            fails.append(name)
            print("  FAIL  %s\n        %s" % (name, exc))
        except Exception as exc:
            fails.append(name)
            print("  ERROR %s\n        %s: %s" % (name, type(exc).__name__, exc))
    print("\nfailures %d   skips %d" % (len(fails), len(skips)))
    if skips:
        print("SKIPS ARE NOT PASSES: %s" % ", ".join(skips))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
