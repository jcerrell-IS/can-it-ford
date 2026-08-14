#!/usr/bin/env python3
"""The flooded-road scene spec, and the solver-side half of the Zhao 2019 BC.

TWO THINGS ARE DELIBERATELY SEPARATE HERE
    FloodRoadScene   pure data. No warp, no warpmpm, no GPU. It can be built,
                     printed and asserted on a laptop, which is where the
                     design mistakes are cheap.
    SelectionOutflow the solver-side wiring. Imports warp lazily, inside the
                     method that needs it, so importing this module on a
                     machine with no CUDA still works.

WHY THIS IS WIRING AND NOT A THIRD IMPLEMENTATION
=================================================
Two implementations of the Zhao et al. 2019 in/outflow BC already exist, and
writing a third would be waste. Checked live 2026-08-14:

  simulation/coupling_force/inflow_outflow.py   TRACKED on main. InletBC,
      OutflowRetirement, RecyclingConveyor. Its own header says "CPU reference
      implementation, analytically self-tested. NOT run against the GPU solver.
      No gated run uses it." A repo-wide search for an importer returns ZERO
      code consumers; only README.md and two findings docs mention it. This
      module imports it, which makes this its first wiring.

  simulation/realism/outflow_deactivate.py      on branch realism-exploration,
      GPU-wired through particle_selection, already run. Not on main and not in
      this dispatch's scope to move. Its design is followed rather than
      re-derived, and it is credited here.

THE DEFECT THAT MAKES A NAIVE WIRING SILENTLY WRONG
===================================================
`RecyclingConveyor.step()` sets `self.active[i] = False` and returns the
position and velocity arrays UNCHANGED for that particle. `active` is CPU
bookkeeping with NO solver-side effect. A driver that calls

    pos, vel, n_ret, n_iss = conv.step(solver.x(), solver.v(), dt)
    solver.set_x(pos); solver.set_v(vel)

leaves every "retired" particle fully simulated, sitting where it died, still
depositing mass and momentum onto the grid, until it happens to be reissued.
The outflow is then a no-op in the physics while the bookkeeping reports it
working. That is not a criticism of the reference module, which says plainly it
was never run against the solver; it is the specific thing the wiring must add.

THE REAL SINK, VERIFIED IN THE VENDORED KERNELS RATHER THAN ASSUMED
===================================================================
`state.particle_selection[p] == 0` gates the four per-particle fluid kernels,
read live at third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_utils.py:

    :922   p2g_apic_with_stress          deposits no mass or momentum
    :1049  g2p                           does not move
    :1157  compute_stress_from_F_trial   develops no stress
    :1173  g2p_stress_p2g                fused path, same gate

so setting it to 1 removes the particle from the fluid AND freezes it in place.
Both halves matter and the second one bites: `solver.x()` still returns frozen
particles, so EVERY depth, volume or free-surface measurement must mask on the
active set or it silently counts dead water sitting where it died.

TWO MORE gates exist at :1380 and :1472, both `particle_selection[p] == 0 and
particle_material[p] == 8`, i.e. the RIGID kernels honour it too. Deactivating a
rigid particle would silently remove part of the hull. This wiring refuses to
touch any index outside the water range for that reason.

WHAT IS STILL NOT A PORT, AND MUST NEVER BE CALLED ONE
======================================================
Zhao et al.'s outflow is PRESSURE-controlled. There is no pressure field in
warpmpm at any point (register B7); pressure exists only implicitly per
particle through J = det(F) and the bulk modulus in the weakly-compressible
EOS. The substitute is a depth-keyed and position-keyed deactivation, which is
register B7's own recommended re-expression. The velocity-controlled INLET half
does translate directly and is the half that is genuinely Zhao et al.'s.

    Zhao, X., Bolognin, M., Liang, D., Rohe, A., Vardon, P. J. (2019).
    Development of in/outflow boundary conditions for MPM simulation of uniform
    and non-uniform open channel flows. Computers & Fluids, 179, 27-33.
    doi:10.1016/j.compfluid.2018.10.007. Implemented by them in Anura3D, a
    Delft-lineage code with no relationship to warpmpm, so this is a
    TRANSLATION, not a port (register J8). NOT Kumar; that attribution was
    corrected 2026-08-07.

A MEASURED NEGATIVE THAT CONSTRAINS THE DESIGN, CARRIED FORWARD NOT REPEATED
============================================================================
`open_channel.py`'s ChannelRecycler was tested 2026-08-12 and LOST to the closed
tank on the depth-hold metric, 30.0 percent against 58.9 percent, and a
downstream sponge did not rescue it at any gain. The recorded mechanism: a
streamwise periodic wrap has NO MASS OR ENERGY SINK, so the surge that reaches
the outlet is re-injected at the inlet and circulates. Deactivation is a real
sink and is therefore a different boundary condition, not the same one again.
If it still loses to the closed tank, that is a second negative result and is
reported as one.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from simulation.fork_scene.cross_slope import (  # type: ignore[import-not-found]  # noqa: E402
    G, CrossSlope,
)
from simulation.fork_scene.domain import (  # type: ignore[import-not-found]  # noqa: E402
    CANONICAL_DEPTH_M, DomainSpec, grid_lim,
)

__all__ = ["FloodRoadScene", "SelectionOutflow", "build_canonical_scene"]

# Canonical scene constants, read live from the 389-line canonical driver
# renders/yaris_render_s1/_incoming/sim_standing.py and the run inventory.
FLOOR_FRICTION = 0.55
FLOOR_RESTITUTION = 0.05
WALL_FRICTION = 0.0
SURFACE_MODE = "slip"
BULK_MODULUS_PA = 150000.0
WATER_DENSITY = 1000.0
WATER_ETA = 0.001


@dataclass
class FloodRoadScene:
    """A cross-sloped flooded-road scene. Pure data; nothing here touches a GPU.

    `formulation` is "gravity" (bed-aligned frame, recommended) or "plane"
    (tilted floor, cross-check only). See cross_slope.py for why they are not
    equally good.
    """

    hull_extent: tuple[float, float, float]
    depth_m: float = CANONICAL_DEPTH_M
    n_grid: int = 64
    slope: CrossSlope = field(default_factory=lambda: CrossSlope(0.0))
    formulation: str = "gravity"
    inflow_velocity_ms: float = 1.5
    vehicle_mass_kg: float = 1100.0

    def __post_init__(self):
        if self.formulation not in ("gravity", "plane"):
            raise ValueError("formulation must be 'gravity' or 'plane'")
        if self.formulation == "plane":
            b = self.slope.S * self.lim_m
            if b >= self.depth_m:
                raise ValueError(
                    f"formulation='plane' at S={self.slope.S:g} drops the bed "
                    f"{b:.4f} m across a {self.lim_m:.4f} m tank, which is "
                    f"{100 * b / self.depth_m:.0f}% of the {self.depth_m:.4f} m "
                    "depth, so the upstream end runs dry and the comparison is "
                    "not held fixed. Use formulation='gravity', or deepen the "
                    "tank and accept that the water volume is no longer matched.")

    @property
    def lim_m(self) -> float:
        return grid_lim(self.hull_extent, self.depth_m)

    @property
    def domain(self) -> DomainSpec:
        return DomainSpec(self.lim_m, self.n_grid, self.depth_m)

    def gravity(self) -> tuple[float, float, float]:
        """Pass to Solver.set_material(material, g=...). See cross_slope.py for
        the live check that this override actually wins."""
        if self.formulation == "gravity":
            return self.slope.gravity_vector()
        return (0.0, 0.0, -G)

    def floor_plane(self) -> dict:
        """Arguments for Solver.add_plane for the road surface."""
        d = self.domain
        normal = ((0.0, 0.0, 1.0) if self.formulation == "gravity"
                  else self.slope.plane_normal())
        return {
            "point": (0.0, 0.0, d.floor_z),
            "normal": normal,
            "surface": SURFACE_MODE,
            "friction": FLOOR_FRICTION,
            "restitution": FLOOR_RESTITUTION,
            "keeps_fast_path": any(abs(abs(c) - 1.0) < 1e-6 for c in normal),
        }

    def inflow_outflow_spec(self) -> dict:
        """Geometry for the Zhao 2019 inlet and the deactivation outflow.

        The reach is the free water span between the wall bands. `z_target` is
        the intended free surface, which is what the depth-keyed outflow holds
        and is register B7's re-expression of Zhao's outlet pressure condition.
        """
        d = self.domain
        return {
            "x_in": d.wall,
            "x_out": d.lim_m - d.wall,
            "y_span": (d.wall, d.lim_m - d.wall),
            "z_span": (d.floor_z, d.floor_z + self.depth_m),
            "floor": d.floor_z,
            "z_target": d.floor_z + self.depth_m,
            "velocity": self.inflow_velocity_ms,
            "slab_thickness": 3.0 * d.dx,
            "h": d.h,
        }

    def describe(self) -> str:
        d, fp = self.domain, self.floor_plane()
        g = self.gravity()
        return (
            f"FloodRoadScene  formulation={self.formulation}  S={self.slope.S:g}"
            f" (theta {self.slope.theta_deg:.4f} deg)\n"
            f"  {d.describe()}\n"
            f"  floor normal {tuple(round(c, 6) for c in fp['normal'])}"
            f"  fast path {'KEPT' if fp['keeps_fast_path'] else 'LOST'}\n"
            f"  gravity {tuple(round(c, 6) for c in g)}"
            f"  |g| {math.hypot(*g):.9f} m/s2")


class SelectionOutflow:
    """The solver-side half: pushes retirement into `particle_selection`.

    Composes `simulation.coupling_force.inflow_outflow`'s InletBC and
    OutflowRetirement, which own the geometry and the discharge arithmetic, and
    adds the only thing they cannot do from CPU: making retirement real.

    Design follows `simulation/realism/outflow_deactivate.py` on branch
    realism-exploration, which established that this is the mechanism that
    works. Three of its lessons are reproduced deliberately:
      * `active_mask()` must be used for every measurement, because deactivated
        particles freeze in place at the top of the column and an unmasked
        percentile keeps reporting the surface just removed;
      * particle state (F, F_trial, C, Jp, stress) must be RESET on reissue, or
        the pool carries the surge's deformation and pressure history back to
        the inlet, which is the recirculation the periodic wrap was refuted for;
      * the inlet must be DEMAND-DRIVEN on a depth deficit, not driven by the
        nominal discharge.

    THE THIRD LESSON WAS LEARNED HERE THE HARD WAY, AND IT IS WORTH THE SPACE.
    The first version of this class took its inlet rate from
    `InletBC.particles_per_step`, i.e. n = Q*dt/v_p, because that is what the
    tracked CPU reference does. At the canonical geometry that is 304 particles
    per tick against an outflow of order tens, so the retired pool drained on
    every tick and EVERY retired particle was re-injected at the inlet in the
    same tick it left. That is precisely the streamwise periodic wrap that was
    tested on 2026-08-12 and LOST to the closed tank (30.0 percent against 58.9
    percent on depth-hold) because a wrap has no mass or energy sink. The class
    would have reported a working outflow the whole time.

    `tests/test_fork_scene_outflow.py::test_retirement_reaches_the_solver_array`
    is what caught it, and `wrap_ratio()` is what makes it visible from now on:
    sustained ~1.0 with a pool that never accumulates means this BC has
    degenerated into the refuted one. Default `inlet_mode` is therefore "depth".
    """

    SELECTION_ACTIVE = 0      # warp_utils: only selection == 0 is simulated
    SELECTION_RETIRED = 1

    def __init__(self, solver, n_water: int, spec: dict, seed: int = 0,
                 mode: str = "depth", inlet_mode: str = "depth",
                 relax_len: float | None = None, max_activate: int = 20000):
        from simulation.coupling_force.inflow_outflow import (  # noqa: PLC0415
            InletBC, OutflowRetirement,
        )
        import numpy as np  # noqa: PLC0415

        if inlet_mode not in ("depth", "discharge"):
            raise ValueError("inlet_mode must be 'depth' or 'discharge'")
        self._np = np
        self.s = solver
        self.sim = solver._sim
        self.n = int(n_water)
        self.inlet = InletBC(
            x_in=spec["x_in"], slab_thickness=spec["slab_thickness"],
            y_span=spec["y_span"], z_span=spec["z_span"],
            velocity=spec["velocity"], rho=WATER_DENSITY)
        self.outflow = OutflowRetirement(
            x_out=spec["x_out"], mode=mode, z_target=spec["z_target"])
        self.inlet_mode = inlet_mode
        self.spec = dict(spec)
        self.floor = float(spec["floor"])
        self.target_depth = float(spec["z_target"]) - self.floor
        self.y_span = tuple(float(c) for c in spec["y_span"])
        self.relax_len = float(
            relax_len if relax_len is not None
            else 0.25 * (spec["x_out"] - spec["x_in"]))
        self.max_activate = int(max_activate)
        self.h = float(spec["h"])
        self.particle_volume = self.h ** 3
        self.rng = np.random.default_rng(seed)
        self._pending = 0.0
        self.retired_total = 0
        self.reissued_total = 0
        self.history: list[dict] = []

        sel = self.sim.mpm_state.particle_selection.numpy()
        self.sel = np.asarray(sel).copy()
        if self.sel.shape[0] < self.n:
            raise ValueError("n_water exceeds the particle allocation")

    # ------------------------------------------------------------------ warp
    def _push_selection(self):
        import warp as wp  # noqa: PLC0415
        dev = self.sim.mpm_state.particle_selection.device
        wp.copy(self.sim.mpm_state.particle_selection,
                wp.from_numpy(self.sel.astype(self._np.int32), dtype=int, device=dev))

    def _reset_particle_state(self, idx):
        """Clear deformation history on reissued particles. See class docstring."""
        import warp as wp  # noqa: PLC0415
        np = self._np
        st = self.sim.mpm_state
        eye = np.eye(3, dtype=np.float32)
        for name, fill in (("particle_F", eye), ("particle_F_trial", eye),
                           ("particle_C", np.zeros((3, 3), np.float32)),
                           ("particle_stress", np.zeros((3, 3), np.float32))):
            arr = getattr(st, name, None)
            if arr is None:
                continue
            host = np.asarray(arr.numpy()).copy()
            host[idx] = fill
            wp.copy(arr, wp.from_numpy(host.astype(np.float32), dtype=wp.mat33,
                                       device=arr.device))
        jp = getattr(st, "particle_Jp", None)
        if jp is not None:
            host = np.asarray(jp.numpy()).copy()
            host[idx] = 1.0
            wp.copy(jp, wp.from_numpy(host.astype(np.float32), dtype=float,
                                      device=jp.device))

    # -------------------------------------------------------------- boundary
    def active_mask(self):
        """USE THIS FOR EVERY MEASUREMENT. Frozen particles are not water."""
        return self.sel[:self.n] == self.SELECTION_ACTIVE

    def water_volume_m3(self) -> float:
        return float(self.active_mask().sum()) * self.particle_volume

    def retired_fraction(self) -> float:
        """Occupancy of the retired pool. PUBLISH THIS WITH ANY RUN THAT USES
        THIS BC, exactly as `water_layers` is published now: while a particle
        sits retired it is mass that has genuinely left the domain."""
        return 1.0 - float(self.active_mask().mean())

    def wrap_ratio(self) -> float:
        """reissued / retired over the run so far. THE DEGENERACY DIAGNOSTIC.

        If this sits at ~1.0 with a pool that never accumulates, every particle
        that leaves the outlet is immediately re-injected at the inlet and the
        boundary condition has silently become the STREAMWISE PERIODIC WRAP that
        was already tested on 2026-08-12 and LOST to the closed tank, 30.0
        percent against 58.9 percent on depth-hold, because a wrap has no mass
        or energy sink. Publish it with any run that uses this BC. A BC that has
        degenerated into a refuted BC while its counters look healthy is exactly
        the failure this project keeps finding after the fact.
        """
        if self.retired_total == 0:
            return float("nan")
        return self.reissued_total / self.retired_total

    def inlet_depth(self, x, act) -> float:
        """Active-masked water depth in the inlet relaxation band.

        MUST be masked: deactivated particles freeze where they died, and they
        die at the TOP of the column by construction, so an unmasked percentile
        reports the surface this BC just removed.
        """
        np = self._np
        x0 = self.spec["x_in"]
        sel = (act
               & (x[:self.n, 0] >= x0)
               & (x[:self.n, 0] < x0 + self.relax_len))
        if sel.sum() < 20:
            return 0.0
        return float(np.percentile(x[:self.n][sel, 2], 99.0)) + 0.5 * self.h - self.floor

    def _demand(self, x, act, dt) -> int:
        """How many particles the inlet asks for this tick.

        'depth'     DEMAND-DRIVEN, register B7 / outflow_deactivate.py. The pool
                    absorbs the difference between outflow and inflow, so a surge
                    can be SWALLOWED rather than re-injected. This is the whole
                    reason deactivation is a different boundary condition from
                    the refuted wrap, and it is the default for that reason.
        'discharge' Zhao's velocity inlet read as a flux, n = Q*dt/v_p. Honest,
                    and the mode to use when the question is "what does a
                    prescribed discharge do". DANGEROUS AS A DEFAULT: whenever
                    the nominal Q exceeds the outflow rate, the pool drains every
                    tick and this degenerates into the wrap. `wrap_ratio()` is
                    what makes that visible instead of silent.
        """
        np = self._np
        if self.inlet_mode == "discharge":
            self._pending += self.inlet.particles_per_step(self.particle_volume, dt)
            return int(math.floor(self._pending))
        deficit = self.target_depth - self.inlet_depth(x, act)
        if deficit <= 0.0:
            return 0
        width = self.y_span[1] - self.y_span[0]
        return int(min(deficit * self.relax_len * width / self.particle_volume,
                       self.max_activate))

    def apply(self, dt: float) -> tuple[int, int]:
        """One control tick. Retire first, then reissue, so a particle that
        leaves this tick is available to re-enter this tick."""
        np = self._np
        x = self.s.x()
        v = self.s.v()
        act = self.active_mask()

        leaving = self.outflow.select(x[:self.n]) & act
        n_ret = int(leaving.sum())
        if n_ret:
            self.sel[:self.n][leaving] = self.SELECTION_RETIRED
            self.retired_total += n_ret
            act = self.active_mask()

        want = self._demand(x, act, dt)
        pool = np.flatnonzero(self.sel[:self.n] == self.SELECTION_RETIRED)
        n_iss = int(min(want, pool.size))
        if n_iss > 0:
            idx = pool[:n_iss]          # oldest first: the order they died in
            x[idx] = self.inlet.seed_positions(n_iss, self.rng)
            v[idx] = 0.0
            v[idx, 0] = self.inlet.velocity_at(x[idx][:, 2])
            self.sel[:self.n][idx] = self.SELECTION_ACTIVE
            if self.inlet_mode == "discharge":
                self._pending -= n_iss
            self.reissued_total += n_iss
            self.s.set_x(x)
            self.s.set_v(v)
            self._reset_particle_state(idx)

        if n_ret or n_iss:
            self._push_selection()
        self.history.append({"n_retired": n_ret, "n_reissued": n_iss,
                             "n_active": int(self.active_mask().sum()),
                             "wrap_ratio": self.wrap_ratio()})
        return n_ret, n_iss


def build_canonical_scene(slope_S: float = 0.0, n_grid: int = 64,
                          formulation: str = "gravity") -> FloodRoadScene:
    """The canonical Yaris geometry with a cross-slope applied.

    Hull extents are the measured PLY values from fork_scene.domain's anchors,
    so this reproduces the as-ran grid_lim 9.421742... to float32 precision.
    """
    from simulation.fork_scene.domain import ANCHORS  # noqa: PLC0415
    return FloodRoadScene(
        hull_extent=ANCHORS["yaris"]["ply_extent"],
        n_grid=n_grid,
        slope=CrossSlope(slope_S),
        formulation=formulation,
    )


if __name__ == "__main__":
    print("fork_scene.scene")
    print("=" * 88)
    for S in (0.0, 0.02, 0.06):
        print()
        print(build_canonical_scene(S).describe())
    print("\nformulation='plane' guard:")
    for S in (0.02, 0.06):
        try:
            build_canonical_scene(S, formulation="plane")
        except ValueError as exc:
            print(f"  S={S}: REFUSED -> {str(exc).splitlines()[0]}")
        else:
            print(f"  S={S}: accepted")
    print("\ninflow/outflow spec at S=0.02 (geometry only; the BC itself is")
    print("simulation/coupling_force/inflow_outflow.py, wired by SelectionOutflow):")
    spec = build_canonical_scene(0.02).inflow_outflow_spec()
    for k in sorted(spec):
        print(f"  {k:<16} {spec[k]}")
    print("=" * 88)
