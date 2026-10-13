"""The three-grid GCI function the steady-force Stage 1 analysis used, kept as a test fixture.

Copied verbatim from `simulation/steady_force/analyze_stage1.py` (lines 32 to 62, development
repository commit c11c584e, 2026-10-03), which is not public. `tests/test_gci_least_squares.py`
checks that `analysis/gci_least_squares.py` gives the same Celik et al. (2008) numbers as this older
function on the same inputs, so the newer module's extra rules are the only difference between them.
"""
import math

import numpy as np


def gci(h, phi, fs=1.25):
    h = np.asarray(h, float)
    phi = np.asarray(phi, float)
    o = np.argsort(h)
    h1, h2, h3 = h[o]
    f1, f2, f3 = phi[o]
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    out = {"h": [h1, h2, h3], "phi": [f1, f2, f3], "r21": r21, "r32": r32}
    if e21 == 0 or e32 == 0:
        out["status"] = "degenerate"
        return out
    ratio = e32 / e21
    out["oscillatory"] = bool(ratio < 0)
    s = 1.0 if ratio > 0 else -1.0
    p = 2.0
    for _ in range(200):
        q = math.log((r21 ** p - s) / (r32 ** p - s)) if (r21 ** p - s) > 0 and (r32 ** p - s) > 0 else 0.0
        pn = abs(math.log(abs(ratio)) + q) / math.log(r21)
        if abs(pn - p) < 1e-10:
            p = pn
            break
        p = pn
    out["p"] = p
    ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    out["phi_ext"] = ext
    out["e_a21"] = abs((f1 - f2) / f1)
    out["e_ext21"] = abs((ext - f1) / ext) if ext != 0 else float("nan")
    out["gci_fine"] = fs * out["e_a21"] / (r21 ** p - 1)
    out["status"] = "oscillatory, report spread" if out["oscillatory"] else "monotone"
    return out
