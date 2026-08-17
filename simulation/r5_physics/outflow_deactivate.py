"""Depth-keyed particle RETIREMENT for warpmpm. NOT an outflow. Do not run yet.

CORRECTED 2026-08-17 after review. The first version of this file was wrong in its central
physical description, wrong about the gate sites, and overstated its own novelty. Worse,
**it regressed against a primary-source finding I had already made and written down**:
`docs/OPTION_A_SESSION1_FINDINGS.md:146-149` states verbatim that advection
`x_new = particle_x[p] + dt*new_v` lives inside `g2p_particle` (`mpm_utils.py:1026`), "so a
deactivated particle also **freezes in place**". I then wrote "its mass leaves the
simulation".

WHAT DEACTIVATION ACTUALLY DOES
-------------------------------
Setting `particle_selection[p]` non-zero makes the particle **freeze in place and stay in
the array**. It is not advected, not gathered, not stress-updated, not scattered, because
the gate at `mpm_utils.py:1049` wraps `g2p_particle`, and advection is inside that. Its
mass is removed from the **grid transfer** only.

Of the six gate sites, only **two** touch P2G (`:922`, and `:1173` reaching `p2g_particle`
at `:1178`). `:1049` gates G2P, `:1157` the stress update, `:1380` and `:1472` the rigid
path. The earlier "gates the P2G scatter at six sites" was wrong.

THE ARTIFACT THAT MAKES THIS DANGEROUS TO RUN, AND IT IS THE DEFAULT
--------------------------------------------------------------------
**Nothing in this repository filters retired particles out of any diagnostic.**
`sim_standing.py:451` dumps `w = x[:n_water]` with no selection filter, so frozen ghosts
land in `rollout.npz`. `sim_standing.py:473-474` and `simulation/r5_physics/depth_station.py`
both take the 99.5th percentile of water z, and the ghosts are **by construction exactly
the particles that were above `z_target`, frozen there forever**.

Review measured the consequence on a faithful stub: the depth trace reads **0.7339 to
0.7347 over 60 ticks, flat to three decimals**, while the ACTIVE free surface sits at
0.6609. **The level appears to hold perfectly and the number producing it is dead water.**
Outflow also decays to near zero as the surface is stripped, so it looks like a converged
steady state from outside. Any depth number from a run using this module, taken with the
current diagnostics, is an artifact. `retired_mask()` exists so callers can filter; until
`local_depth_footprint` and `depth_station.py` do, do not quote a level.

WHAT THIS IS NOT
----------------
* **NOT an outflow.** The +x face is closed twice: `sim_standing.py:212-214` adds a slip
  plane at `x = lim - wall` and `:215` calls `add_domain_walls()`. My own F-7
  (`OPTION_A_SESSION1_FINDINGS.md:170-171`) says an outflow BC must skip that call or use a
  variant leaving +x open. This module does neither. **As written it is a mass sink placed
  upstream of a closed wall.**
* **NOT novel selection logic.** `inflow_outflow.py:157-163` `OutflowRetirement.select`
  already implements `past & (pos[:,2] > z_target)` verbatim, and that file already quotes
  B7. It is imported here rather than re-implemented. **The one genuinely new part is
  narrow: wiring retirement through `import_particle_selection_from_torch` so it reaches
  the solver at all**, where `OutflowRetirement` was CPU-side bookkeeping only. The earlier
  claim to "refute the premise in code" is withdrawn.
* **NOT a port of Zhao et al.** Theirs is PRESSURE-controlled; warpmpm has no pressure
  field (`grep -ci pressure` returns 0 over 3,181 lines). Never call this
  pressure-controlled.
* **NOT mass-conserving**, and `retired_fraction()` reports the loss every tick.
* **NOT VALIDATED.** Zero GPU time; the socket has been cold all session.

CONSTRAINTS, each with the failure it prevents
-----------------------------------------------
1. **Sense.** `selection == 0` is ACTIVE; deactivating writes non-zero. Confirmed at all
   six sites by review. Backwards, this freezes the domain on tick 1.
2. **Water only.** Deselecting a vehicle particle is worse than "removing part of the
   body": `mpm_solver_warp.py:856` fixes the rigid mass `M` once at
   `finalize_rigid_bodies` and `mpm_utils.py:1434` divides momentum by it, so the particle
   drops out of the momentum sum while its mass stays in `M`. That manufactures an
   unphysical drag on the vehicle, which is the published verdict variable.
3. **Monotone.** A particle allowed back re-enters carrying its old `particle_F/C/Jp`.
4. **Depth key.** Retiring on `x > x_out` alone strips the whole column.
5. **NEW: sort must be off.** `mpm_solver_warp.py:1573` sorts `particle_selection` with the
   other int arrays and `:1556-1557` warns that index identity changes. An index-keyed
   retirement mask scrambles under a sort. Asserted in `__init__`.
6. **NEW: the datum.** `z_target` is ABSOLUTE z, and the floor is at `3*dx`, not 0. Passing
   a labelled depth such as 0.30 retires the entire column. Asserted against `floor`.

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

    def __init__(self, solver, n_water, x_out, z_target, floor, lim, wall,
                 device=None, position_only=False):
        self.solver = solver
        self.n_water = int(n_water)
        self.x_out = float(x_out)
        self.z_target = float(z_target)
        self.floor = float(floor)
        self.position_only = bool(position_only)
        # Constraint: read the device from the solver rather than hardcoding cuda:0.
        self.device = device if device is not None else getattr(solver, "device", "cuda:0")
        # Constraint 5: an index-keyed mask is invalid under a mid-run sort.
        si = getattr(solver, "sort_interval", 0)
        if si:
            raise ValueError(
                f"sort_interval={si}: particle index identity changes at a sort "
                f"(mpm_solver_warp.py:1556-1557) and this retirement mask is index-keyed, "
                f"so retirement would scramble across water and vehicle. Set it to 0.")
        # Constraint 6: z_target is ABSOLUTE z and the floor is at 3*dx, not 0.
        if not (self.floor < self.z_target):
            raise ValueError(
                f"z_target={self.z_target} is not above floor={self.floor}. z_target is an "
                f"ABSOLUTE height, not a depth: passing a labelled depth retires the whole "
                f"column on tick 1, which looks like a drain rather than an error.")
        if not (self.x_out < lim - wall):
            raise ValueError(
                f"x_out={self.x_out} is at or past the closed downstream wall at "
                f"{lim - wall}. Retirement there is behind the wall, not before it.")
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
        # Reuse the project's existing selector rather than re-implementing it. Falls back
        # to the inline predicate only if that module is unavailable (e.g. this dry run).
        qualify = self._select(x)
        new = qualify & ~self._retired          # monotone: constraint 3
        n_new = int(new.sum())
        if n_new:
            self._retired |= new
            self._push()
        self.history.append({"retired_total": self.retired_count(),
                             "retired_this_tick": n_new,
                             "retired_fraction": self.retired_fraction()})
        return n_new

    def _select(self, x):
        try:
            import sys as _s
            from pathlib import Path as _P
            _s.path.insert(0, str(_P(__file__).resolve().parents[1] / "coupling_force"))
            from inflow_outflow import OutflowRetirement           # noqa
            sel = OutflowRetirement(
                x_out=self.x_out,
                mode="position" if self.position_only else "depth",
                z_target=None if self.position_only else self.z_target)
            return np.asarray(sel.select(x), dtype=bool)
        except Exception:
            past = x[:, 0] > self.x_out
            return past if self.position_only else (past & (x[:, 2] > self.z_target))

    def retired_mask(self):
        """The retirement bitmask. CALLERS MUST FILTER THIS OUT OF ANY DIAGNOSTIC.

        Retired particles are frozen, not removed, and no diagnostic in this repository
        knows selection exists. A depth statistic computed without this filter is pinned by
        dead water and will read flat regardless of what the live surface does.
        """
        return self._retired.copy()

    def save_mask(self, path):
        """Write the retirement mask as `retired` beside a rollout, per the guard contract.

        `active_water()` in depth_station.py and spin_down.py reads exactly this key. A run
        that retires particles and does NOT dump this is unanalysable: its ghosts are
        indistinguishable from water in the archive, and every depth statistic silently
        pins to them. Dump it or do not report a level.
        """
        np.save(str(path), self._retired)
        return path

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
    FLOOR, LIM, WALL = 0.44, 10.0, 0.59      # realistic g64 datum, not floor=0
    pos[:n_water, 2] = FLOOR + rng.uniform(0.0, 0.30, n_water)
    pos[n_water:, 2] = FLOOR + 0.28
    ZT = FLOOR + 0.20
    o = DepthKeyedOutflow(_Solver(pos), n_water=n_water, x_out=8.0, z_target=ZT,
                          floor=FLOOR, lim=LIM, wall=WALL)
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

    expect = int(((pos[:n_water, 0] > 8.0) & (pos[:n_water, 2] > ZT)).sum())
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

    # Constraint 3, asserted for real. The earlier version guarded on `if o._retired[0]:`
    # with a particle that had never qualified, so the check NEVER RAN and the commit
    # message claimed it had. Pick a genuinely retired index instead.
    idx = int(np.flatnonzero(o._retired)[0])
    pos[idx] = [0.0, 0.0, FLOOR]            # drag it far upstream and below the target
    o.step()
    check("constraint 3: a retired particle dragged back upstream STAYS retired",
          bool(o._retired[idx]), f"(index {idx}, now at x=0.0)")

    check("retired_fraction is reported and non-zero",
          0.0 < o.retired_fraction() < 1.0, f"({o.retired_fraction():.4f})")

    o2 = DepthKeyedOutflow(_Solver(pos.copy()), n_water=n_water, x_out=8.0,
                           z_target=ZT, floor=FLOOR, lim=LIM, wall=WALL,
                           position_only=True)
    n_pos = o2.step()
    # STRICT, not >=. With >= this passed even if the depth key were ignored entirely.
    check("position_only retires STRICTLY more than the depth-keyed mode",
          n_pos > n1, f"({n_pos} vs {n1})")

    print("\nguards (each of these SHOULD raise)")
    for name, kw in (("z_target below the floor (the datum trap)",
                      dict(z_target=0.30, floor=FLOOR, lim=LIM, wall=WALL)),
                     ("x_out behind the closed downstream wall",
                      dict(z_target=ZT, floor=FLOOR, lim=LIM, wall=WALL, x_out=9.9))):
        kw.setdefault("x_out", 8.0)
        try:
            DepthKeyedOutflow(_Solver(pos), n_water=n_water, **kw)
            check(f"raises on {name}", False)
        except ValueError:
            check(f"raises on {name}", True)

    check("retired_mask() is exposed so callers can filter ghosts from diagnostics",
          o.retired_mask().sum() == o.retired_count())

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
