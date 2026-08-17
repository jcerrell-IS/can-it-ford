"""Depth-keyed outflow for warpmpm by particle DEACTIVATION, not deletion.

WHAT THIS IS, AND WHY IT IS NOT WHAT THE PROJECT SAID WAS POSSIBLE
------------------------------------------------------------------
`simulation/coupling_force/inflow_outflow.py` argues that particle count is fixed at load,
so "a naive inlet that injects particles and an outlet that deletes them is not expressible
without changing the allocation, which would fork every gated run", and substitutes a
recycling conveyor. **Deletion is not the only way to remove mass.**

`kernels/mpm_utils.py` gates the P2G scatter on `particle_selection[p] == 0` at six sites
(`:922, :1049, :1157, :1173, :1380, :1472`), and
`kernels/mpm_solver_warp.py:1679 import_particle_selection_from_torch` writes that array at
runtime. A deselected particle contributes nothing to `grid_m`, so **its mass leaves the
simulation at fixed allocation, with no fork of any gated run and no array resized.**

That is exactly the register's own B7 wording, which the same file quotes: "a
depth-controlled outflow, **deactivating** particles above a target free-surface height".
This module implements that.

WHAT IT IS NOT
--------------
* **Not a port of Zhao et al. 2019.** Their outflow is PRESSURE-controlled and warpmpm has
  no pressure field anywhere: `grep -ci pressure kernels/mpm_solver_warp.py` returns 0
  across 3,181 lines at the pinned SHA. Pressure exists only implicitly per particle via
  `J = det(F)` in the weakly compressible EOS. This is a depth-keyed SUBSTITUTE for that
  control, which is what the register recommends, and it must never be described as
  pressure-controlled.
* **Not mass-conserving, and it must not pretend to be.** An outflow removes mass by
  definition. `retired_fraction()` reports exactly how much has left, every tick. Pairing
  it with an inlet is a separate piece of work and is not attempted here.
* **NOT VALIDATED.** Nothing in this file has run against the GPU solver: the TACC socket
  has been cold for this entire session. The dry-run self-test below exercises the driver
  logic against a stub and proves only that it RUNS and that its bookkeeping is
  self-consistent. Do not cite it as a working outflow.

FOUR CORRECTNESS CONSTRAINTS, each with the reason it exists
------------------------------------------------------------
1. **Sense.** `particle_selection[p] == 0` means ACTIVE. Deactivating means writing a
   NON-zero value. Getting the sense backwards silently deactivates the entire domain on
   the first tick, which would look like an instant drain rather than an error.
2. **Water only.** The rigid path also tests `particle_selection` (`:1380`, `:1472`), so
   deactivating a vehicle particle would silently remove part of the body. This driver
   only ever touches indices below `n_water`.
3. **Monotone.** Once retired, a particle stays retired. A particle allowed back would
   re-enter carrying its old `particle_F`, `particle_C` and `particle_Jp`, injecting the
   outlet's compression history. That is the defect that makes the existing
   `RecyclingConveyor` unsound, and it is avoided here by never clearing a bit.
4. **Depth key, not just position.** Retiring on `x > x_out` alone drains the full column
   and cannot hold a level. Retiring only ABOVE a target free surface removes the excess
   that a closed wall would otherwise pile up, which is the mechanism the level needs.

Run the dry run:  python simulation/r5_physics/outflow_deactivate.py --selftest
"""
from __future__ import annotations

import argparse

import numpy as np


class DepthKeyedOutflow:
    """Retire water particles past `x_out` that sit above `z_target`.

    `solver` is a `warpmpm.core.solver.Solver`. The selection array is reached through
    `solver._sim`, because the public API does not expose it: `core/solver.py` mentions
    "selection" exactly once, in an unrelated device docstring. That is the single wrapper
    worth adding upstream, and until it exists this reach-around is the honest way to do it
    rather than pretending the capability is absent.
    """

    def __init__(self, solver, n_water, x_out, z_target, device="cuda:0",
                 position_only=False):
        self.solver = solver
        self.n_water = int(n_water)
        self.x_out = float(x_out)
        self.z_target = float(z_target)
        self.device = device
        self.position_only = bool(position_only)
        self._retired = np.zeros(self.n_water, dtype=bool)   # monotone, never cleared
        self.history = []

    # --- reporting ---------------------------------------------------------------------
    def retired_count(self):
        return int(self._retired.sum())

    def retired_fraction(self):
        return float(self._retired.mean()) if self.n_water else 0.0

    # --- the tick ----------------------------------------------------------------------
    def step(self):
        """Retire newly qualifying particles and push the selection array. Call after step().

        Returns the number retired THIS tick, which is the instantaneous outflow rate in
        particles per tick and is the quantity to plot against the inflow when an inlet
        eventually exists.
        """
        x = self.solver.x()[: self.n_water]
        past = x[:, 0] > self.x_out
        if self.position_only:
            qualify = past
        else:
            qualify = past & (x[:, 2] > self.z_target)
        new = qualify & ~self._retired          # monotone: constraint 3
        n_new = int(new.sum())
        if n_new:
            self._retired |= new
            self._push()
        self.history.append({"retired_total": self.retired_count(),
                             "retired_this_tick": n_new,
                             "retired_fraction": self.retired_fraction()})
        return n_new

    def _push(self):
        """Write the selection array. NON-zero deactivates; zero is active (constraint 1)."""
        import torch

        sel = np.zeros(self._total(), dtype=np.int32)
        sel[: self.n_water][self._retired] = 1        # water only (constraint 2)
        t = torch.as_tensor(sel, dtype=torch.int32, device=self.device)
        self.solver._sim.import_particle_selection_from_torch(t, device=self.device)

    def _total(self):
        return int(self.solver.x().shape[0])


# --------------------------------------------------------------------------------------
def selftest():
    """Drive the logic against a stub solver. Proves it RUNS; proves nothing physical."""
    import sys
    import types

    pushed = []

    class _Sim:
        def import_particle_selection_from_torch(self, t, clone=True, device="cuda:0"):
            pushed.append(np.asarray(t.cpu() if hasattr(t, "cpu") else t).copy())

    class _Solver:
        def __init__(self, pos):
            self._pos = pos
            self._sim = _Sim()

        def x(self):
            return self._pos

    # stub torch: only as_tensor is used
    if "torch" not in sys.modules:
        th = types.ModuleType("torch")
        th.int32 = "int32"
        th.as_tensor = lambda a, dtype=None, device=None: np.asarray(a)
        sys.modules["torch"] = th

    fails = []

    def check(name, ok, detail=""):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  ' + detail) if detail else ''}")
        if not ok:
            fails.append(name)

    n_water, n_veh = 1000, 50
    rng = np.random.default_rng(0)
    pos = np.zeros((n_water + n_veh, 3))
    pos[:n_water, 0] = rng.uniform(0.0, 10.0, n_water)
    pos[:n_water, 2] = rng.uniform(0.0, 1.0, n_water)
    pos[n_water:, 0] = 9.9                    # vehicle sits PAST the outlet on purpose
    pos[n_water:, 2] = 0.9                    # and ABOVE the target, on purpose

    print("depth-keyed outflow, dry run against a stub\n")
    o = DepthKeyedOutflow(_Solver(pos), n_water=n_water, x_out=8.0, z_target=0.5)
    n1 = o.step()
    check("retires a nonzero number on the first tick", n1 > 0, f"({n1})")
    sel = pushed[-1]
    check("selection array covers ALL particles, not just water",
          sel.size == n_water + n_veh, f"({sel.size})")
    check("constraint 2: NO vehicle particle deactivated, though all qualify on x and z",
          sel[n_water:].sum() == 0,
          f"({int(sel[n_water:].sum())} of {n_veh} vehicle particles)")
    check("constraint 1: deactivation writes NON-zero, active stays zero",
          set(np.unique(sel)).issubset({0, 1}) and sel[:n_water].sum() == n1)

    expect = int(((pos[:n_water, 0] > 8.0) & (pos[:n_water, 2] > 0.5)).sum())
    check("depth key applied, not position alone", n1 == expect,
          f"({n1} retired vs {expect} qualifying on BOTH keys)")
    pos_only = int((pos[:n_water, 0] > 8.0).sum())
    check("constraint 4: the depth key retires strictly fewer than position alone",
          n1 < pos_only, f"({n1} vs {pos_only} on position alone)")

    n2 = o.step()
    check("constraint 3: monotone, a second identical tick retires nothing new",
          n2 == 0, f"({n2})")
    check("retired total is stable across the no-op tick",
          o.retired_count() == n1)

    # a particle drifting back upstream must NOT be reactivated
    pos[0] = [0.0, 0.0, 0.0]
    if o._retired[0]:
        o.step()
        check("constraint 3: a retired particle that drifts back stays retired",
              o._retired[0])

    check("retired_fraction is reported and non-zero",
          0.0 < o.retired_fraction() < 1.0, f"({o.retired_fraction():.4f})")

    o2 = DepthKeyedOutflow(_Solver(pos.copy()), n_water=n_water, x_out=8.0,
                           z_target=0.5, position_only=True)
    check("position_only mode retires more than the depth-keyed mode",
          o2.step() >= n1)

    print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + ', '.join(fails)}")
    print("\nThis proves the driver RUNS and its bookkeeping is self-consistent.")
    print("It proves NOTHING about whether a level holds. That needs the GPU, and the")
    print("TACC socket has been cold for this entire session.")
    return 1 if fails else 0


def main():
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        return selftest()
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
