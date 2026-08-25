"""The P2G edge guard must name the axis it actually guarded, and the particle.

Implements the check for the 2026-08-07 C2 diagnostic spec, written 2026-08-25.

The defect this pins down: `Solver._update_grid_box` guards
`g = x[:, 1:] if self.periodic_x else x`, so under `periodic_x` the guarded
columns are y and z. The message reported ONE global min and max across those
columns and labelled them "x" unconditionally, naming an axis that was not being
checked, hiding which axis moved, and never saying which particle or what
material it was.

This test reads the REAL method source out of the vendored solver rather than
importing it, because importing `core.solver` pulls in warp and torch, which are
not present on the Mac. Extracting the source keeps the test honest: it fails if
someone edits the method, which is the point of pinning a vendored engine.
"""
import ast
import os
import sys
import types

import numpy as np

SOLVER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "third_party", "mpm-engine-544c93dd-solver-core", "core", "solver.py")

WANT = {"_edge_violation_report", "_MATERIAL_NAMES"}


def _load_method_into_stub():
    """exec only the guard helper and its material table into a bare class."""
    src = open(SOLVER, encoding="utf-8").read()
    tree = ast.parse(src)
    cls = next(n for n in tree.body
               if isinstance(n, ast.ClassDef) and n.name == "Solver")
    picked = [n for n in cls.body
              if (isinstance(n, ast.FunctionDef) and n.name in WANT)
              or (isinstance(n, ast.Assign)
                  and any(getattr(t, "id", None) in WANT for t in n.targets))]
    assert len(picked) == 2, f"expected 2 nodes, found {len(picked)}"
    mod = ast.Module(body=picked, type_ignores=[])
    ast.fix_missing_locations(mod)
    ns: dict = {"np": np}
    exec(compile(mod, SOLVER, "exec"), ns)
    return type("StubSolver", (), {k: ns[k] for k in WANT})


class FakeMatArray:
    def __init__(self, mats):
        self._m = np.asarray(mats)

    def numpy(self):
        return self._m


def _stub(cls, pos, mats, periodic_x):
    s = cls()
    s.periodic_x = periodic_x
    pos = np.asarray(pos, dtype=float)
    s.x = lambda: pos
    if mats is None:
        s._sim = types.SimpleNamespace(mpm_state=types.SimpleNamespace())
    else:
        s._sim = types.SimpleNamespace(
            mpm_state=types.SimpleNamespace(particle_material=FakeMatArray(mats)))
    return s


def main() -> int:
    cls = _load_method_into_stub()
    dx, lim = 0.1, 4.0
    lo, hi = 1.5 * dx, lim - 2.5 * dx          # 0.15, 3.75
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            fails.append(f"{name}: {detail}")

    # ---- case 1: periodic_x, a rigid particle escapes BELOW on z ------------
    # particle 2 sits at z = 0.01, below lo = 0.15. x is deliberately far out of
    # range to prove the x column is not guarded and not reported as a violation.
    pos = [[0.5, 1.0, 1.0], [99.0, 2.0, 2.0], [0.5, 1.0, 0.01]]
    mats = [3, 3, 8]
    s = _stub(cls, pos, mats, periodic_x=True)
    g = np.asarray(pos)[:, 1:]
    msg = s._edge_violation_report(g, ("y", "z"), lo, hi, lim, dx)
    print("\ncase 1, periodic_x, rigid particle below on z:")
    print("   " + msg)
    check("names axis z", "axis z" in msg, msg)
    check("does NOT mislabel as x", "x in [" not in msg, msg)
    check("says x is not guarded", "not guarded" in msg, msg)
    check("names particle 2", "particle 2" in msg, msg)
    check("names material 8 rigid", "material 8 (rigid)" in msg, msg)
    check("reports per-axis y range", "y in [1.0000, 2.0000]" in msg, msg)
    check("reports depth below", "below the limit" in msg, msg)

    # ---- case 2: no periodic_x, a water particle escapes ABOVE on x ---------
    pos = [[0.5, 1.0, 1.0], [3.99, 1.0, 1.0]]
    mats = [0, 0]
    s = _stub(cls, pos, mats, periodic_x=False)
    g = np.asarray(pos)
    msg = s._edge_violation_report(g, ("x", "y", "z"), lo, hi, lim, dx)
    print("\ncase 2, no periodic_x, particle above on x:")
    print("   " + msg)
    check("names axis x", "axis x" in msg, msg)
    check("names particle 1", "particle 1" in msg, msg)
    check("reports above", "above the limit" in msg, msg)
    check("material 0 unnamed", "material 0 (unnamed in this build)" in msg, msg)
    check("guards all three axes", "x, y and z" in msg, msg)

    # ---- case 3: the material array is unreadable ---------------------------
    # A diagnostic that raises replaces the real error with its own. It must not.
    pos = [[0.5, 1.0, 0.01]]
    s = _stub(cls, pos, None, periodic_x=True)
    g = np.asarray(pos)[:, 1:]
    try:
        msg = s._edge_violation_report(g, ("y", "z"), lo, hi, lim, dx)
        ok = "unavailable" in msg and "axis z" in msg
    except Exception as exc:
        msg, ok = f"RAISED {type(exc).__name__}: {exc}", False
    print("\ncase 3, material array missing:")
    print("   " + msg)
    check("degrades without raising", ok, msg)

    # ---- case 4: the helper is total ---------------------------------------
    pos = [[0.5, 1.0, 1.0]]
    s = _stub(cls, pos, [0], periodic_x=False)
    g = np.asarray(pos)
    try:
        msg = s._edge_violation_report(g, ("x", "y", "z"), lo, hi, lim, dx)
        ok = isinstance(msg, str) and len(msg) > 0
    except Exception as exc:
        msg, ok = f"RAISED {type(exc).__name__}: {exc}", False
    print("\ncase 4, called with no actual violation:")
    print("   " + msg)
    check("returns a string rather than raising", ok, msg)

    print()
    if fails:
        print(f"FAILED ({len(fails)})")
        for f in fails:
            print("  " + f)
        return 1
    print("all edge-guard diagnostic checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
