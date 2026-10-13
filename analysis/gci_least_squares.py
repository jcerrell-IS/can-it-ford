"""Discretization uncertainty of an integrated quantity from a ladder of three or more grids.

Given a quantity phi (for example a mean force) computed on grids with cell sizes h, this reports the
apparent order of convergence, the extrapolated value and the uncertainty, and says plainly whether a
convergence claim is allowed. It implements three published procedures side by side:

  [1] Celik, Ghia, Roache, Freitas, Coleman and Raad (2008), "Procedure for Estimation and Reporting
      of Uncertainty Due to Discretization in CFD Applications", J. Fluids Eng. 130(7),
      doi:10.1115/1.2960953. The three-grid grid convergence index (GCI).
  [2] Xing and Stern (2010), "Factors of Safety for Richardson Extrapolation", J. Fluids Eng. 132(6),
      doi:10.1115/1.4001771, as used in ITTC Recommended Procedure 7.5-03-01-01. A factor of safety
      that depends on how close the observed order is to the formal order.
  [3] Eca and Hoekstra (2014), "A procedure for the estimation of the numerical uncertainty of CFD
      calculations based on grid refinement studies", J. Comput. Phys. 262, 104 to 130,
      doi:10.1016/j.jcp.2014.01.006. Least-squares fits over four or more grids.

A convergence claim (decision PASS) needs all of: at least four grid levels, an observed order inside
0.5 <= p < 2.1, a fit scatter below the data range, the correct sign, and a statistical (sampling)
uncertainty that is supplied, resolved between levels and small next to the discretization error.
Three levels can never pass, whatever they show.

Usage
    python3 analysis/gci_least_squares.py --h 0.075 0.05 0.0375 --phi 2473 1906 1557
Tests: tests/test_gci_least_squares.py.
"""
import argparse
import math
import sys

import numpy as np

P_LOW = 0.5
P_RE_HIGH = 2.0
P_FS_HIGH = 2.1
FS_RELIABLE = 1.25
FS_UNRELIABLE = 3.0
CELIK_MIN_RATIO = 1.3
MIN_LEVELS_LS = 4
STAT_ORDER_FACTOR = 0.1
NAN = float("nan")
P_SCAN = np.concatenate([np.arange(-1000, 0) * 0.01 + 0.005, np.arange(0, 1000) * 0.01 + 0.005])
FIXED_ORDERS = {"d1": (1,), "d2": (2,), "d12": (1, 2)}
FIT_MODELS = {
    "RE": "phi0 + a h^p, Eqs. (1), (8), (12)",
    "d1": "phi0 + a h, Eqs. (5), (9), (13)",
    "d2": "phi0 + a h^2, Eqs. (6), (10), (14)",
    "d12": "phi0 + a1 h + a2 h^2, Eqs. (7), (11), (15)",
}
VERDICT_ASYMPTOTIC = "asymptotic"
VERDICT_NOT = "not asymptotic: report U with Fs 3, do not claim convergence"
VERDICT_THREE = ("not demonstrated: three levels cannot satisfy the four-grid rule; "
                 "report U with Fs 3, do not claim convergence")


def cell_size(n_cells, extent=1.0, dim=3):
    if not (n_cells > 0 and extent > 0 and dim in (1, 2, 3)):
        raise ValueError("cell_size needs n_cells > 0, extent > 0 and dim 1, 2 or 3")
    return (float(extent) / float(n_cells)) ** (1.0 / dim)


def prepare(h, phi, stat_unc=None):
    h = np.asarray(h, dtype=float).ravel()
    phi = np.asarray(phi, dtype=float).ravel()
    if h.size != phi.size:
        raise ValueError("h and phi need one value per level (%d h, %d phi)" % (h.size, phi.size))
    if h.size < 3:
        raise ValueError("at least 3 levels are needed, %d given" % h.size)
    if not (np.all(np.isfinite(h)) and np.all(np.isfinite(phi))):
        raise ValueError("h and phi must be finite numbers")
    if np.any(h <= 0):
        raise ValueError("every h must be positive")
    order = np.argsort(h, kind="stable")
    h = h[order]
    phi = phi[order]
    if np.any(np.diff(h) <= 0):
        raise ValueError("h values must be distinct")
    u = None
    if stat_unc is not None:
        u = np.asarray(stat_unc, dtype=float).ravel()
        if u.size != h.size:
            raise ValueError("the statistical uncertainty needs one value per level (%d given for %d levels)"
                             % (u.size, h.size))
        if not np.all(np.isfinite(u)) or np.any(u < 0):
            raise ValueError("statistical uncertainties must be finite and non-negative")
        u = u[order]
    return h, phi, u


def _celik_q(p, r21, r32, s):
    if p == 0.0 and s > 0:
        return math.log(math.log(r21) / math.log(r32))
    return math.log((r21 ** p - s) / (r32 ** p - s))


def celik(h, phi, fs=FS_RELIABLE, tol=1e-13, max_iter=1000):
    h, phi, _ = prepare(h, phi)
    if h.size != 3:
        raise ValueError("celik() takes exactly three levels, %d given" % h.size)
    h1, h2, h3 = (float(v) for v in h)
    f1, f2, f3 = (float(v) for v in phi)
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    out = {"h": [h1, h2, h3], "phi": [f1, f2, f3], "r21": r21, "r32": r32,
           "ratios_above_1p3": bool(r21 > CELIK_MIN_RATIO and r32 > CELIK_MIN_RATIO),
           "eps21": e21, "eps32": e32, "ratio": NAN, "s": NAN, "oscillatory": False,
           "monotone": False, "p": NAN, "converged": False, "iterations": 0}
    scale = max(abs(f1), abs(f2), abs(f3))
    if abs(e21) <= 1e-12 * scale or abs(e32) <= 1e-12 * scale:
        out["status"] = "degenerate: a level difference is zero to round-off, so Eq. (3) cannot be solved"
        return out
    ratio = e32 / e21
    s = 1.0 if ratio > 0 else -1.0
    out.update(ratio=ratio, s=s, oscillatory=s < 0, monotone=s > 0)
    lnr = math.log(abs(ratio))
    ln21 = math.log(r21)
    p = abs(lnr) / ln21
    for k in range(1, max_iter + 1):
        out["iterations"] = k
        try:
            pn = abs(lnr + _celik_q(p, r21, r32, s)) / ln21
        except (ValueError, ZeroDivisionError, OverflowError):
            break
        if abs(pn - p) <= tol * max(1.0, pn):
            p = pn
            out["converged"] = True
            break
        p = pn
    if not out["converged"]:
        out["status"] = "the fixed-point iteration of Eq. (3) did not converge, so p is not established"
        return out
    out["p"] = p
    if p <= 0:
        out["status"] = "the apparent order is zero, so Eqs. (4) to (7) are undefined"
        return out
    rp21, rp32 = r21 ** p, r32 ** p
    ext21 = (rp21 * f1 - f2) / (rp21 - 1.0)
    ext32 = (rp32 * f2 - f3) / (rp32 - 1.0)
    e_a = abs((f1 - f2) / f1) if f1 != 0 else NAN
    e_ext = abs((ext21 - f1) / ext21) if ext21 != 0 else NAN
    out.update(phi_ext21=ext21, phi_ext32=ext32, delta_re=f1 - ext21, e_a21=e_a, e_ext21=e_ext,
               gci_fine21=fs * e_a / (rp21 - 1.0), gci_fine21_fs3=FS_UNRELIABLE * e_a / (rp21 - 1.0),
               u_fs3=FS_UNRELIABLE * abs(f1 - ext21),
               status="oscillatory convergence (eps32/eps21 < 0)" if s < 0 else "monotone convergence")
    return out


def xing_stern_fs(P):
    P = float(P)
    if not P > 0:
        return NAN
    if P <= 1.0:
        return 2.45 - 0.85 * P
    return 16.4 * P - 14.8


def xing_stern(c, formal_order=2.0):
    if not formal_order > 0:
        raise ValueError("the formal order must be positive")
    out = {"formal_order": float(formal_order), "defined": False, "P": NAN, "fs": NAN, "u": NAN, "u_rel": NAN}
    if not (c.get("converged") and c.get("monotone") and "delta_re" in c and c["p"] > 0):
        out["status"] = ("not defined: the factor of safety of Eq. (8) is used here for monotone "
                         "convergence with p > 0 only")
        return out
    P = c["p"] / formal_order
    fs = xing_stern_fs(P)
    u = fs * abs(c["delta_re"])
    f1 = c["phi"][0]
    out.update(defined=True, P=P, fs=fs, u=u, u_rel=abs(u / f1) if f1 != 0 else NAN, status="defined")
    return out


def _weights(x, weighted):
    w = 1.0 / x if weighted else np.ones_like(x)
    return w / w.sum()


def _sigma(phi, fit, w, n_params):
    dof = phi.size - n_params
    if dof <= 0:
        return NAN
    return math.sqrt(float(np.sum(phi.size * w * (phi - fit) ** 2)) / dof)


def _re_profile(p, x, phi, w):
    p = np.atleast_1d(np.asarray(p, dtype=float))
    with np.errstate(all="ignore"):
        X = x[None, :] ** p[:, None]
        xm = X @ w
        Xc = X - xm[:, None]
        alpha = ((Xc * phi[None, :]) @ w) / ((Xc * Xc) @ w)
        phi0 = float(w @ phi) - alpha * xm
        res = phi[None, :] - phi0[:, None] - alpha[:, None] * X
        S = (res * res) @ w
        dS = -2.0 * alpha * ((res * X * np.log(x)[None, :]) @ w)
    return phi0, alpha, res, S, dS


def fit_re(x, phi, weighted):
    w = _weights(x, weighted)
    S = _re_profile(P_SCAN, x, phi, w)[3]
    k = int(np.nanargmin(S))
    p = float(P_SCAN[k])
    at_bound = k in (0, P_SCAN.size - 1)
    if not at_bound:
        a, b = float(P_SCAN[k - 1]), float(P_SCAN[k + 1])
        if a * b > 0 and _re_profile(a, x, phi, w)[4][0] < 0 < _re_profile(b, x, phi, w)[4][0]:
            for _ in range(200):
                m = 0.5 * (a + b)
                if _re_profile(m, x, phi, w)[4][0] < 0:
                    a = m
                else:
                    b = m
                if b - a <= 4e-16 * max(1.0, abs(m)):
                    break
            p = 0.5 * (a + b)
    phi0, alpha, res, S, _ = _re_profile(p, x, phi, w)
    fit = phi - res[0]
    return {"kind": "RE", "weighted": weighted, "n_params": 3, "p": p, "phi0": float(phi0[0]),
            "coef": [float(alpha[0])], "fit": fit, "eps": np.abs(fit - float(phi0[0])),
            "sigma": _sigma(phi, fit, w, 3), "S": float(S[0]), "at_bound": at_bound}


def fit_fixed(x, phi, kind, weighted):
    w = _weights(x, weighted)
    A = np.column_stack([np.ones_like(x)] + [x ** o for o in FIXED_ORDERS[kind]])
    sw = np.sqrt(w)
    coef = np.linalg.lstsq(A * sw[:, None], phi * sw, rcond=None)[0]
    fit = A @ coef
    return {"kind": kind, "weighted": weighted, "n_params": A.shape[1], "p": NAN, "phi0": float(coef[0]),
            "coef": [float(v) for v in coef[1:]], "fit": fit, "eps": np.abs(fit - float(coef[0])),
            "sigma": _sigma(phi, fit, w, A.shape[1]), "S": float(np.sum(w * (phi - fit) ** 2)),
            "at_bound": False}


def eca_hoekstra(h, phi):
    h, phi, _ = prepare(h, phi)
    n = h.size
    out = {"run": False, "n_levels": n, "reliable": False, "fs": FS_UNRELIABLE, "p": NAN, "phi0": NAN}
    if n < MIN_LEVELS_LS:
        out["status"] = ("not run: %d levels, and the procedure needs at least %d (Sec. 2.3 and App. A)"
                         % (n, MIN_LEVELS_LS))
        return out
    dphi = float(phi.max() - phi.min()) / (n - 1)
    if not dphi > 0:
        out["status"] = "not run: every level gives the same value, so the data range parameter of Eq. (19) is zero"
        return out
    x = h / h[0]
    fits = [fit_re(x, phi, False), fit_re(x, phi, True)]
    for kind in ("d1", "d2", "d12"):
        for weighted in (False, True):
            fits.append(fit_fixed(x, phi, kind, weighted))
    positive = [f for f in fits[:2] if f["p"] > 0 and not f["at_bound"]]
    best = min(positive, key=lambda f: f["sigma"]) if positive else None
    p = round(best["p"], 9) if best is not None else NAN
    if best is not None and P_LOW <= p <= P_RE_HIGH:
        branch = "0.5 <= p <= 2, so the error estimate is delta_RE (Sec. 2.4.1)"
        candidates = [best]
    elif best is not None and p > P_RE_HIGH:
        branch = "p > 2, so the error estimate is the better of delta_1 and delta_2, four fits (Sec. 2.4.1)"
        candidates = [f for f in fits if f["kind"] in ("d1", "d2")]
    elif best is not None:
        branch = "p < 0.5, so the error estimate is the best of delta_1, delta_2 and delta_12, six fits (Sec. 2.4.1)"
        candidates = [f for f in fits if f["kind"] in ("d1", "d2", "d12")]
    else:
        branch = ("no fit gives an established p > 0: anomalous data, the best of six fixed-order fits "
                  "(Sec. 2.4.2)")
        candidates = [f for f in fits if f["kind"] in ("d1", "d2", "d12")]
    sel = min(candidates, key=lambda f: f["sigma"])
    for f in fits:
        f["candidate"] = any(f is c for c in candidates)
        f["selected"] = f is sel
    sigma = sel["sigma"]
    reliable = bool(best is not None and P_LOW <= p < P_FS_HIGH and sigma < dphi)
    fs = FS_RELIABLE if reliable else FS_UNRELIABLE
    dev = np.abs(phi - sel["fit"])
    if sigma < dphi:
        u = fs * sel["eps"] + sigma + dev
        u_fs3 = FS_UNRELIABLE * sel["eps"] + sigma + dev
        eq = "Eq. (20)"
    else:
        u = 3.0 * (sigma / dphi) * (sel["eps"] + sigma + dev)
        u_fs3 = u
        eq = "Eq. (21)"
    window = [f for f in fits[:2] if P_LOW <= round(f["p"], 9) <= P_RE_HIGH and not f["at_bound"]]
    out.update(run=True, h=h, x=x, phi=phi, fits=fits, re_selected=best, p=p, branch=branch, selected=sel,
               phi0=sel["phi0"], sigma=sigma, dphi=dphi, reliable=reliable, fs=fs, u=u, u_fs3=u_fs3, eq=eq,
               appendix_a_differs=bool(window) and sel["kind"] != "RE", status="run")
    return out


def statistical_checks(phi, u, k, eps):
    out = {"supplied": u is not None, "k": float(k), "ok": False}
    if u is None:
        return out
    eps = np.asarray(eps, dtype=float)
    diffs = np.abs(np.diff(phi))
    comb = k * np.sqrt(u[:-1] ** 2 + u[1:] ** 2)
    ku = k * u
    with np.errstate(invalid="ignore"):
        resolved = diffs > comb
        order_ok = ku <= STAT_ORDER_FACTOR * eps
    out.update(u=u, diffs=diffs, comb=comb, resolved=resolved, ku=ku, eps=eps, order_ok=order_ok,
               ok=bool(np.all(resolved) and np.all(order_ok)))
    return out


def _triplet_problem(c):
    if not c["converged"] or not math.isfinite(c["p"]) or "delta_re" not in c:
        return "finest three levels: " + c["status"]
    if c["oscillatory"]:
        return ("finest three levels converge oscillatorily (eps32/eps21 %.4g < 0), which Eca and "
                "Hoekstra (2014) treat as anomalous" % c["ratio"])
    if not P_LOW <= round(c["p"], 9) < P_FS_HIGH:
        return "finest three levels: apparent order p %.4f is outside 0.5 <= p < 2.1" % c["p"]
    return None


def assess(h, phi, formal_order=2.0, stat_unc=None, stat_k=2.0):
    if not formal_order > 0:
        raise ValueError("the formal order must be positive")
    if not stat_k > 0:
        raise ValueError("the coverage factor must be positive")
    h, phi, u = prepare(h, phi, stat_unc)
    n = h.size
    c = celik(h[:3], phi[:3])
    xs = xing_stern(c, formal_order)
    eh = eca_hoekstra(h, phi)
    four = n >= MIN_LEVELS_LS
    triplet = _triplet_problem(c)
    if eh["run"]:
        phi0 = eh["phi0"]
        eps = eh["selected"]["eps"]
    else:
        phi0 = c.get("phi_ext21", NAN)
        eps = np.abs(phi - phi0) if math.isfinite(phi0) else np.full(n, NAN)
    same_sign = bool(np.all(phi > 0) or np.all(phi < 0))
    physical = bool((not same_sign) or (math.isfinite(phi0) and np.sign(phi0) == np.sign(phi[0])))
    st = statistical_checks(phi, u, stat_k, eps)
    if four:
        asymptotic = bool(eh["run"] and eh["reliable"] and triplet is None)
        verdict = VERDICT_ASYMPTOTIC if asymptotic else VERDICT_NOT
    else:
        asymptotic = False
        verdict = VERDICT_THREE if triplet is None else VERDICT_NOT
    passed = bool(four and asymptotic and physical and st["ok"])
    if four and eh["run"]:
        u_report = float(eh["u"][0] if asymptotic else eh["u_fs3"][0])
    else:
        u_report = float(c.get("u_fs3", NAN))
    u_total = math.hypot(u_report, stat_k * float(u[0])) if (u is not None and math.isfinite(u_report)) else NAN
    reasons = []
    if not four:
        reasons.append("only %d levels: three levels can never satisfy the four-grid rule" % n)
        if not c["ratios_above_1p3"]:
            reasons.append("refinement ratios r21 %.4f and r32 %.4f are not both above 1.3 (Celik et al. 2008, "
                           "Step 2)" % (c["r21"], c["r32"]))
    elif not eh["run"]:
        reasons.append("Eca and Hoekstra " + eh["status"])
    else:
        if eh["re_selected"] is None:
            reasons.append("Eca and Hoekstra: no established positive observed order (anomalous data), so Fs is 3")
        elif not P_LOW <= eh["p"] < P_FS_HIGH:
            reasons.append("Eca and Hoekstra observed order p %.4f is outside 0.5 <= p < 2.1, so Fs is 3" % eh["p"])
        if not eh["sigma"] < eh["dphi"]:
            reasons.append("fit standard deviation %.4g is not below the data range parameter %.4g, so Fs is 3"
                           % (eh["sigma"], eh["dphi"]))
    if triplet is not None:
        reasons.append(triplet)
    if not physical:
        reasons.append("extrapolated value %.6g has the opposite sign to every level (physicality guard)" % phi0)
    if not st["supplied"]:
        reasons.append("statistical uncertainty not supplied (--stat-unc, one N_eff-based standard uncertainty "
                       "per level)")
    else:
        for i in np.flatnonzero(~st["resolved"]):
            reasons.append("levels h %.6g and %.6g differ by %.4g, which is not more than %.3g times their combined "
                           "standard uncertainty %.4g" % (h[i], h[i + 1], st["diffs"][i], stat_k,
                                                          st["comb"][i] / stat_k))
        for i in np.flatnonzero(~st["order_ok"]):
            reasons.append("at h %.6g the statistical uncertainty k u = %.4g is not one order of magnitude below the "
                           "discretization error estimate %.4g" % (h[i], st["ku"][i], eps[i]))
    return {"h": h, "phi": phi, "stat_unc": u, "n_levels": n, "formal_order": float(formal_order), "celik": c,
            "xing_stern": xs, "eca_hoekstra": eh, "four_grid_rule": four, "triplet_ok": triplet is None,
            "asymptotic": asymptotic, "verdict": verdict, "physical": physical, "same_sign": same_sign,
            "phi0": phi0, "stat": st, "u_report": u_report, "u_total": u_total, "passed": passed,
            "reasons": reasons}


def _num(v, fmt="%.6g"):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "n/a"
    return fmt % v if math.isfinite(v) else "n/a"


def _pct(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "n/a"
    return "%.2f%%" % (100.0 * v) if math.isfinite(v) else "n/a"


def _rel(a, b):
    return a / abs(b) if b != 0 else NAN


def render(r):
    h, phi, u, n = r["h"], r["phi"], r["stat_unc"], r["n_levels"]
    lines = ["Discretization uncertainty from a grid ladder: %d levels, finest first" % n,
             "  level  h             phi               stat u (1 sd)"]
    for i in range(n):
        lines.append("  %-5d  %-12s  %-16s  %s" % (i + 1, _num(h[i]), _num(phi[i], "%.10g"),
                                                    _num(u[i]) if u is not None else "not supplied"))
    if r["formal_order"] != 2.0:
        lines.append("note: the 0.5 <= p < 2.1 window and the fixed-order fits assume a theoretically "
                     "second-order method (Eca and Hoekstra 2014, Sec. 2.2); formal order %s was given, so the "
                     "window is applied as published and is unvalidated for that order" % _num(r["formal_order"]))
    c = r["celik"]
    lines += ["", "[1] Celik et al. (2008), the three finest levels",
              "  r21 %.4f, r32 %.4f; both above 1.3 (Step 2): %s"
              % (c["r21"], c["r32"], "yes" if c["ratios_above_1p3"] else "no"),
              "  eps21 %s, eps32 %s, eps32/eps21 %s: %s"
              % (_num(c["eps21"]), _num(c["eps32"]), _num(c["ratio"], "%.4g"), c["status"])]
    if "delta_re" in c:
        lines += ["  apparent order p %.4f (Eq. 3, fixed-point iteration, %d iterations)" % (c["p"], c["iterations"]),
                  "  phi_ext21 %s (Eq. 4); e_a21 %s (Eq. 5); e_ext21 %s (Eq. 6)"
                  % (_num(c["phi_ext21"]), _pct(c["e_a21"]), _pct(c["e_ext21"])),
                  "  GCI_fine21 %s with Fs 1.25 (Eq. 7); %s with Fs 3"
                  % (_pct(c["gci_fine21"]), _pct(c["gci_fine21_fs3"]))]
    x = r["xing_stern"]
    lines += ["", "[2] Xing and Stern (2010) factor of safety, formal order %s (ITTC 7.5-03-01-01, Eqs. 6 to 8)"
              % _num(x["formal_order"])]
    if x["defined"]:
        lines.append("  P = p / p_th %.4f; FS(P) %.4f; U = FS |delta_RE| %s (%s of phi_1)"
                     % (x["P"], x["fs"], _num(x["u"]), _pct(x["u_rel"])))
    else:
        lines.append("  " + x["status"])
    e = r["eca_hoekstra"]
    lines += ["", "[3] Eca and Hoekstra (2014) least squares"]
    if not e["run"]:
        lines.append("  " + e["status"])
    else:
        lines += ["  h relative to the finest level; weights none or 1/h (Eq. 16); sigma as defined in App. B",
                  "  fit  weights  phi0              p or orders  sigma         role       model"]
        for f in e["fits"]:
            role = "selected" if f["selected"] else ("candidate" if f["candidate"] else "")
            order = (_num(f["p"], "%.4f") + (" (bound)" if f["at_bound"] else "")) if f["kind"] == "RE" else \
                {"d1": "1", "d2": "2", "d12": "1 and 2"}[f["kind"]]
            lines.append("  %-4s %-8s %-17s %-12s %-13s %-10s %s"
                         % (f["kind"], "1/h" if f["weighted"] else "none", _num(f["phi0"], "%.10g"), order,
                            _num(f["sigma"], "%.4g"), role, FIT_MODELS[f["kind"]]))
        if e["re_selected"] is not None:
            lines.append("  observed order p %.4f, from the RE fit with the smaller sigma among those with p > 0 "
                         "(Sec. 2.4)" % e["p"])
        lines.append("  branch: " + e["branch"])
        if e["appendix_a_differs"]:
            lines.append("  note: App. A would use delta_RE here because one RE fit has 0.5 <= p <= 2; this module "
                         "follows Sec. 2.4, which takes p from the better-fitting RE fit")
        lines += ["  data range parameter %s (Eq. 19); sigma %s; sigma below it: %s"
                  % (_num(e["dphi"], "%.4g"), _num(e["sigma"], "%.4g"), "yes" if e["sigma"] < e["dphi"] else "no"),
                  "  Fs %s (Sec. 3 and App. A: 1.25 only when 0.5 <= p < 2.1 and sigma is below the data range "
                  "parameter)" % _num(e["fs"]),
                  "  U(phi_i) by %s:" % e["eq"],
                  "  level  h             phi_fit           eps           U             U/|phi|"]
        sel = e["selected"]
        for i in range(n):
            lines.append("  %-5d  %-12s  %-16s  %-12s  %-12s  %s"
                         % (i + 1, _num(h[i]), _num(sel["fit"][i], "%.10g"), _num(sel["eps"][i], "%.4g"),
                            _num(e["u"][i], "%.4g"), _pct(_rel(e["u"][i], phi[i]))))
    lines.append("")
    if r["four_grid_rule"]:
        lines.append("four-grid rule: met (%d levels)" % n)
    else:
        lines.append("four-grid rule: NOT MET. %d levels supplied; Eca and Hoekstra (2014) need at least 4, because "
                     "only a fourth level lets the observed order be checked. Three levels can never satisfy this "
                     "rule, whatever they show." % n)
    st = r["stat"]
    if st["supplied"]:
        lines.append("statistical uncertainty, coverage factor k = %s:" % _num(st["k"]))
        for i in range(n - 1):
            lines.append("  h %s to %s: difference %s against k times the combined u %s: %s"
                         % (_num(h[i]), _num(h[i + 1]), _num(st["diffs"][i], "%.4g"), _num(st["comb"][i], "%.4g"),
                            "resolved" if st["resolved"][i] else "NOT resolved"))
        for i in range(n):
            lines.append("  h %s: k u %s against 0.1 times the discretization error estimate %s: %s"
                         % (_num(h[i]), _num(st["ku"][i], "%.4g"), _num(st["eps"][i], "%.4g"),
                            "below" if st["order_ok"][i] else "NOT below"))
    tail = ""
    if math.isfinite(r["u_total"]):
        tail = "; with the statistical part by root sum square (ITTC Eq. 22) %s (%s)" % (
            _num(r["u_total"], "%.4g"), _pct(_rel(r["u_total"], phi[0])))
    lines.append("reported uncertainty at h %s: U %s (%s of phi_1), Fs %s%s"
                 % (_num(h[0]), _num(r["u_report"], "%.4g"), _pct(_rel(r["u_report"], phi[0])),
                    "1.25" if r["asymptotic"] else "3", tail))
    lines.append("verdict: " + r["verdict"])
    if r["passed"]:
        lines.append("decision: PASS (at least four levels, asymptotic, physical sign, statistical uncertainty "
                     "resolved and included)")
    else:
        lines.append("decision: no convergence claim")
        lines += ["  - " + s for s in r["reasons"]]
    lines.append("not checked here: identical record lengths and averaging windows across levels; the plan must "
                 "state them")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="gci_least_squares.py", allow_abbrev=False,
        description="Discretization uncertainty of an integrated quantity from three or more grid levels: "
                    "Celik et al. (2008), Xing and Stern (2010) and Eca and Hoekstra (2014).")
    ap.add_argument("--h", nargs="+", type=float, required=True,
                    help="representative cell size of each level, in any order")
    ap.add_argument("--phi", nargs="+", type=float, required=True,
                    help="the quantity on each level, in the same order as --h")
    ap.add_argument("--formal-order", type=float, default=2.0,
                    help="formal order of the scheme, used for the Xing and Stern P (default 2)")
    ap.add_argument("--stat-unc", nargs="+", type=float, default=None,
                    help="standard uncertainty (1 sd) of phi on each level from sampling, for a time mean "
                         "s / sqrt(N_eff), in the same order as --h")
    ap.add_argument("--stat-k", type=float, default=2.0,
                    help="coverage factor applied to --stat-unc (default 2)")
    a = ap.parse_args(argv)
    try:
        r = assess(a.h, a.phi, a.formal_order, a.stat_unc, a.stat_k)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print("\n".join(render(r)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
