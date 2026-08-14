"""Tests for SelectionOutflow, the solver-side half of the Zhao 2019 in/outflow BC.

WHY A FAKE SOLVER AND NOT A GPU RUN. The thing most likely to be wrong here is
not the kernel physics, it is the BOOKKEEPING: which array gets written, whether
a boolean mask on a slice writes through, and whether rigid particles can be
touched by accident. All of that is testable on a laptop, and none of it needs
CUDA. What a GPU run would add is confirmation that a selection of 1 really
stops a particle, and that is already established by direct kernel reads
(mpm_utils.py:922, :1049, :1157, :1173) rather than by these tests.

WHAT THE FAKE REPRODUCES, DELIBERATELY. `Solver.x()` is
`export_particle_x_to_torch().cpu().numpy()` (core/solver.py:537-541), which on
the CUDA path is a HOST COPY, so mutating the returned array does nothing until
`set_x` is called. The fake returns copies for exactly that reason: a test
against a fake that returned views would pass on code that silently does nothing
on a GPU.

THE DEFECT THESE TESTS EXIST TO CATCH. `RecyclingConveyor` in
simulation/coupling_force/inflow_outflow.py sets `active[i] = False` and returns
positions unchanged. `active` is CPU-only bookkeeping with no solver-side
effect, so a naive wiring leaves "retired" particles fully simulated while the
counters report an outflow working. `test_retirement_reaches_the_solver_array`
is the test that fails if SelectionOutflow ever regresses to that.

RUNNING IT
    python tests/test_fork_scene_outflow.py     # standalone
    pytest tests/test_fork_scene_outflow.py     # also works
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from simulation.fork_scene.scene import (  # type: ignore[import-not-found]  # noqa: E402
    SelectionOutflow, build_canonical_scene,
)


class _FakeState:
    def __init__(self, n):
        self.particle_selection = _FakeWarpArray(np.zeros(n, dtype=np.int32))
        # deliberately absent: particle_F, particle_C, particle_stress, particle_Jp.
        # _reset_particle_state must tolerate that via getattr(..., None).


class _FakeWarpArray:
    """Just enough of a warp array for the code under test: .numpy() and .device."""

    def __init__(self, arr):
        self._arr = arr
        self.device = "cpu"

    def numpy(self):
        return self._arr


class _FakeSim:
    def __init__(self, n):
        self.mpm_state = _FakeState(n)


class FakeSolver:
    """Mimics the warpmpm Solver surface SelectionOutflow uses, copy semantics included."""

    def __init__(self, pos, vel):
        self._x = np.asarray(pos, dtype=np.float64).copy()
        self._v = np.asarray(vel, dtype=np.float64).copy()
        self._sim = _FakeSim(len(self._x))
        self.set_x_calls = 0
        self.set_v_calls = 0

    def x(self):
        return self._x.copy()          # host copy, like the CUDA path

    def v(self):
        return self._v.copy()

    def set_x(self, pos):
        self._x = np.asarray(pos, dtype=np.float64).copy()
        self.set_x_calls += 1

    def set_v(self, vel):
        self._v = np.asarray(vel, dtype=np.float64).copy()
        self.set_v_calls += 1


class TestableOutflow(SelectionOutflow):
    """Stubs out the two warp-touching methods; everything else is the real code."""

    def _push_selection(self):
        self.pushed = getattr(self, "pushed", 0) + 1
        self.sim.mpm_state.particle_selection._arr[:] = self.sel.astype(np.int32)

    def _reset_particle_state(self, idx):
        self.reset_calls = getattr(self, "reset_calls", [])
        self.reset_calls.append(np.asarray(idx).copy())


def _harness(n_water=800, n_rigid=200, seed=0):
    """A scene-shaped particle set: water first, then rigid, exactly as the driver loads it."""
    scene = build_canonical_scene(0.0, n_grid=64)
    spec = scene.inflow_outflow_spec()
    rng = np.random.default_rng(seed)
    n = n_water + n_rigid
    pos = np.zeros((n, 3))
    pos[:n_water, 0] = rng.uniform(spec["x_in"], spec["x_out"] + 0.5, n_water)
    pos[:n_water, 1] = rng.uniform(*spec["y_span"], n_water)
    pos[:n_water, 2] = rng.uniform(spec["floor"], spec["z_target"] + 0.4, n_water)
    pos[n_water:] = [5.0, 4.7, spec["floor"] + 0.3]        # the "hull"
    vel = np.zeros((n, 3))
    solver = FakeSolver(pos, vel)
    bc = TestableOutflow(solver, n_water, spec, seed=seed, mode="depth")
    return scene, spec, solver, bc, n_water, n_rigid


def test_retirement_reaches_the_solver_array():
    """THE headline test. CPU bookkeeping alone is the defect; this catches it."""
    _, _, solver, bc, n_water, _ = _harness()
    before = solver._sim.mpm_state.particle_selection.numpy().copy()
    assert before.sum() == 0, "fixture should start with every particle active"
    n_ret, _ = bc.apply(dt=1.0 / 30.0)
    assert n_ret > 0, "fixture produced no retirable particles; test is vacuous"
    after = solver._sim.mpm_state.particle_selection.numpy()
    assert after.sum() > 0, (
        "retirement did not reach particle_selection. The BC is CPU bookkeeping "
        "only and every 'retired' particle is still fully simulated.")


def test_depth_keyed_rule_is_the_conjunction_not_either():
    """Retire only what is past x_out AND above the target surface.

    Tested on the SELECTION step alone, before any reissue can move a particle,
    so the assertion is about the rule and not about what happened afterwards.
    """
    _, spec, solver, bc, n_water, _ = _harness()
    x_before = solver.x()[:n_water]
    bc.apply(dt=1.0 / 30.0)
    sel = solver._sim.mpm_state.particle_selection.numpy()[:n_water].astype(bool)
    reissued = np.concatenate(getattr(bc, "reset_calls", [])) if \
        getattr(bc, "reset_calls", None) else np.array([], dtype=int)
    still = sel.copy()
    still[reissued[reissued < n_water]] = False
    assert still.sum() > 0, "nothing stayed retired; test is vacuous"
    should = (x_before[:, 0] > spec["x_out"]) & (x_before[:, 2] > spec["z_target"])
    assert should[still].all(), (
        "a particle was retired that does not satisfy BOTH clauses; the rule has "
        "become an OR, which would bleed off water that has not left the reach")


def test_rigid_particles_are_never_touched():
    """particle_selection also gates the RIGID kernels at mpm_utils.py:1380 and :1472,
    so a stray write here would silently delete part of the hull."""
    _, _, solver, bc, n_water, n_rigid = _harness()
    for _ in range(5):
        bc.apply(dt=1.0 / 30.0)
    sel = solver._sim.mpm_state.particle_selection.numpy()
    assert sel[n_water:].sum() == 0, (
        f"{int(sel[n_water:].sum())} of {n_rigid} RIGID particles were deactivated; "
        "that removes part of the vehicle from the simulation")


def test_particle_count_is_invariant():
    """A fixed-count engine: the allocation must never change size."""
    _, _, solver, bc, n_water, n_rigid = _harness()
    n0 = len(solver.x())
    for _ in range(6):
        bc.apply(dt=1.0 / 30.0)
    assert len(solver.x()) == n0 == n_water + n_rigid
    assert len(solver._sim.mpm_state.particle_selection.numpy()) == n0


def test_reissued_particles_land_in_the_inlet_slab_with_inlet_velocity():
    """Placement and velocity of a reissued particle, independent of demand policy.

    Runs in 'discharge' mode on purpose: the default 'depth' inlet correctly
    reissues nothing when the inlet band is already at target, which would make
    this test vacuous rather than passing.
    """
    _, spec, solver, _, n_water, _ = _harness()
    bc = TestableOutflow(solver, n_water, spec, seed=0, mode="depth",
                         inlet_mode="discharge")
    for _ in range(4):
        _, n_iss = bc.apply(dt=1.0 / 30.0)
        if n_iss:
            break
    assert getattr(bc, "reset_calls", None), "nothing was ever reissued; test is vacuous"
    idx = bc.reset_calls[-1]
    x, v = solver.x(), solver.v()
    assert (x[idx, 0] >= spec["x_in"] - 1e-9).all()
    assert (x[idx, 0] <= spec["x_in"] + spec["slab_thickness"] + 1e-9).all()
    assert np.allclose(v[idx, 0], spec["velocity"]), (
        "reissued particles did not get the inlet velocity; the inlet is then a "
        "position reset rather than a flux")
    assert np.allclose(v[idx, 1], 0.0) and np.allclose(v[idx, 2], 0.0)


def test_state_reset_is_called_on_reissue_not_on_retirement():
    """Without the reset the pool carries the surge's F, C and stress back to the
    inlet, which is the recirculation the periodic wrap was refuted for."""
    _, _, _, bc, _, _ = _harness()
    total_reissued = 0
    for _ in range(4):
        _, n_iss = bc.apply(dt=1.0 / 30.0)
        total_reissued += n_iss
    calls = getattr(bc, "reset_calls", [])
    assert sum(len(c) for c in calls) == total_reissued, (
        "reset was not called on exactly the reissued set")


def test_masked_measurements_ignore_frozen_particles():
    """Deactivated particles freeze at the top of the column by construction, so an
    unmasked percentile keeps reporting the surface this BC just removed."""
    _, _, solver, bc, n_water, _ = _harness()
    v0 = bc.water_volume_m3()
    bc.apply(dt=1.0 / 30.0)
    v1 = bc.water_volume_m3()
    assert v1 < v0, "water volume did not fall after a retirement; it is unmasked"
    assert 0.0 < bc.retired_fraction() < 1.0
    expected = float(bc.active_mask().sum()) * bc.particle_volume
    assert abs(v1 - expected) < 1e-15


def test_discharge_inlet_degenerates_into_the_refuted_wrap():
    """The defect the first version of SelectionOutflow actually had.

    With a discharge-driven inlet the nominal Q asks for ~304 particles a tick at
    the canonical geometry, far more than leave, so the pool drains every tick
    and every retired particle is re-injected immediately. That is the streamwise
    periodic wrap that LOST to the closed tank on 2026-08-12. This test pins the
    behaviour so it can never come back silently: in discharge mode the wrap
    ratio must sit at 1.0 and the pool must stay empty.
    """
    _, spec, solver, _, n_water, _ = _harness()
    _, _, solver2, _, _, _ = _harness()
    bc = TestableOutflow(solver2, n_water, spec, seed=0, mode="depth",
                         inlet_mode="discharge")
    for _ in range(3):
        bc.apply(dt=1.0 / 30.0)
    assert bc.retired_total > 0, "nothing retired; test is vacuous"
    assert abs(bc.wrap_ratio() - 1.0) < 1e-12, (
        f"expected the discharge inlet to re-inject one-for-one, got wrap_ratio "
        f"{bc.wrap_ratio()}")
    assert bc.retired_fraction() == 0.0, "pool should be drained every tick"


def test_depth_inlet_actually_retains_a_pool():
    """The default must NOT be a wrap: the pool has to absorb the difference."""
    _, _, _, bc, _, _ = _harness()
    for _ in range(3):
        bc.apply(dt=1.0 / 30.0)
    assert bc.retired_total > 0, "nothing retired; test is vacuous"
    assert bc.retired_fraction() > 0.0, (
        "the depth-driven inlet drained the pool completely, so it is behaving "
        "as a one-for-one wrap and has no mass sink")
    assert bc.wrap_ratio() < 1.0, f"wrap_ratio {bc.wrap_ratio()} implies a wrap"


def test_position_keyed_mode_is_strictly_more_permissive():
    _, spec, solver, bc_depth, n_water, _ = _harness(seed=3)
    _, _, solver2, bc_pos, _, _ = _harness(seed=3)
    bc_pos.outflow.mode = "position"
    n_d, _ = bc_depth.apply(dt=1.0 / 30.0)
    n_p, _ = bc_pos.apply(dt=1.0 / 30.0)
    assert n_p >= n_d, (
        f"position-keyed retired {n_p}, depth-keyed {n_d}; position keying drops "
        "the z clause so it can never retire fewer")


def test_refuses_n_water_larger_than_the_allocation():
    _, spec, solver, _, n_water, n_rigid = _harness()
    try:
        TestableOutflow(solver, n_water + n_rigid + 1, spec)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted n_water beyond the particle allocation")


def test_zhao_inlet_arithmetic_is_the_tracked_module_not_a_reimplementation():
    """Guard against this file quietly growing its own copy of the BC."""
    _, spec, _, bc, _, _ = _harness()
    from simulation.coupling_force.inflow_outflow import InletBC, OutflowRetirement
    assert isinstance(bc.inlet, InletBC)
    assert isinstance(bc.outflow, OutflowRetirement)
    area = (spec["y_span"][1] - spec["y_span"][0]) * (spec["z_span"][1] - spec["z_span"][0])
    assert abs(bc.inlet.area() - area) < 1e-12
    assert abs(bc.inlet.discharge() - spec["velocity"] * area) < 1e-12


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc}")
        else:
            print(f"ok    {fn.__name__}")
    print("-" * 72)
    print(f"{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
