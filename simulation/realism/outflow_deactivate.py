"""Depth-controlled outflow by particle DEACTIVATION: register B7's actual prescription.

WHY THIS IS NOT THE THING ALREADY REFUTED
-----------------------------------------
`open_channel.py`'s ChannelRecycler was tested on 2026-08-12 and LOST to the closed tank
on the assessment's own depth-hold metric (30.0 percent against 58.9 percent), and a
downstream sponge did not rescue it at any gain. The mechanism of that failure is
recorded: a streamwise periodic wrap has NO MASS OR ENERGY SINK, so the surge that
reaches the outlet is re-injected at the inlet and circulates.

Register B7 prescribes something different, and it was never tried:

    "Zhao et al. 2019's pressure-controlled outflow cannot be ported literally. The
     correct re-expression is a depth-controlled outflow, deactivating particles above a
     target free-surface height rather than Dirichlet-constraining a pressure that does
     not exist."
    -- docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md B7, quoted verbatim

Deactivation is a REAL sink. It is not a velocity treatment like the sponge and it is not
transport like the wrap: the particle stops existing as far as the fluid is concerned.

THE SINK IS REAL, VERIFIED IN THE KERNELS RATHER THAN ASSUMED
-------------------------------------------------------------
`warp_utils.py:116` declares `particle_selection` with the comment "only
particle_selection[p] = 0 will be simulated". Four per-particle kernels test it, and all
four are launched every substep:

    compute_stress_from_F_trial   mpm_utils.py:1157   (launched :1047)
    p2g_apic_with_stress          mpm_utils.py:922    (launched :1049)
    g2p                           mpm_utils.py:1049   (launched :1061)
    g2p_stress_p2g                mpm_utils.py:1173   (launched :1078)

So a deactivated particle deposits no mass and no momentum onto the grid (p2g skipped),
develops no stress (stress kernel skipped), and does not move (g2p skipped). It is
removed from the fluid AND frozen in place. Both halves matter:

  * removed from the fluid  -> this is a genuine mass sink, which the wrap never had;
  * frozen in place         -> `solver.x()` still returns it, so EVERY depth, volume or
                               surface measurement must mask on the active set or it will
                               silently count dead particles sitting where they died.

THE SOURCE, AND WHY IT IS NOT JUST THE WRAP AGAIN
-------------------------------------------------
B7 specifies the OUTflow only. With a sink and no source the reach drains, so `sink_only`
below is the literal prescription and is expected to drain; it is run anyway, because
reporting what the prescription alone does is the honest baseline.

`sink_source` completes the pair with Zhao's velocity inlet. It reuses deactivated
particles, which superficially resembles the refuted wrap, and the three differences that
make it a different boundary condition are:

  1. DEMAND-DRIVEN, not automatic. The wrap re-injected every particle that crossed the
     outlet, one for one, so outlet mass flux forced inlet mass flux. Here the pool
     absorbs the difference and the inlet activates only what the depth controller asks
     for. A surge can be swallowed without being re-injected.
  2. STATE IS RESET. F, F_trial, C, Jp and stress are reset on activation, so the surge's
     accumulated deformation and pressure history do NOT return to the inlet. The wrap
     carried all of it across the seam.
  3. IT IS CONTROLLED ON DEPTH, which is the quantity being scored, rather than on
     particle bookkeeping.

If it still loses to the closed tank, that is a second negative result and is to be
reported as one.
"""
from __future__ import annotations

import numpy as np

__all__ = ["DepthControlledOutflow", "active_depth_at"]


def active_depth_at(x, active, x_centre, y_centre, half_window, floor, h):
    """Free-surface depth above `floor` in a column, counting ACTIVE particles only.

    `water_depth_at` in open_channel.py reads `solver.x()` with no mask, which is correct
    only while every particle is live. Deactivated particles are frozen at the position
    they died at, and they die at the TOP of the column by construction, so an unmasked
    percentile would keep reporting the surface this boundary condition just removed.
    """
    sel = (active
           & (np.abs(x[:, 0] - x_centre) <= half_window)
           & (np.abs(x[:, 1] - y_centre) <= half_window))
    if sel.sum() < 20:
        return 0.0
    return float(np.percentile(x[sel, 2], 99.0) + 0.5 * h - floor)


class DepthControlledOutflow:
    """Register B7's depth-controlled outflow, optionally paired with a Zhao velocity inlet.

    Parameters
    ----------
    x_in, x_out    streamwise bounds of the conveying reach, metres.
    floor          floor height, metres. Depths are measured above this.
    target_depth   the free-surface height the outflow holds, metres above `floor`.
    u_target       inlet streamwise velocity, m/s.
    h              particle spacing, metres. Sets the volume a particle carries, h**3.
    mode           'sink_only'   deactivation outflow alone, i.e. B7 as literally written;
                   'sink_source' the same outflow plus a depth-controlled inlet source.
    out_len        length of the outflow band, metres.
    max_activate   per-frame cap on activations, as a guard against re-seeding a whole
                   column in one frame and shocking the pressure field.
    """

    def __init__(self, solver, n_water, x_in, x_out, floor, target_depth, u_target, h,
                 mode="sink_source", out_len=None, relax_len=None, relax_gain=0.5,
                 max_activate=None):
        import warp as wp
        self._wp = wp
        self.s = solver
        self.sim = solver._sim
        self.n = int(n_water)
        self.x_in, self.x_out = float(x_in), float(x_out)
        self.reach = self.x_out - self.x_in
        self.floor = float(floor)
        self.target = float(target_depth)
        self.u = float(u_target)
        self.h = float(h)
        self.mode = str(mode)
        self.out_len = float(out_len if out_len is not None else 0.20 * self.reach)
        self.relax_len = float(relax_len if relax_len is not None else 0.25 * self.reach)
        self.relax_gain = float(relax_gain)
        self.max_activate = int(max_activate if max_activate is not None else 20000)

        self.dev = self.sim.mpm_state.particle_selection.device
        # host-side mirror; 0 = simulated, 1 = deactivated (warp_utils.py:116)
        self.sel = np.asarray(self.sim.mpm_state.particle_selection.numpy()).copy()
        self.n_deactivated_total = 0
        self.n_activated_total = 0
        self.history = []

    # ---------------------------------------------------------------- warp plumbing
    def _push_selection(self):
        wp = self._wp
        wp.copy(self.sim.mpm_state.particle_selection,
                wp.from_numpy(self.sel.astype(np.int32), dtype=int, device=self.dev))

    def _reset_particle_state(self, idx):
        """Clear deformation history on re-seeded particles.

        Without this the pool carries the surge's own F, C and stress back to the inlet,
        which is precisely the recirculation the wrap was refuted for. Reset in host
        arrays and copy back whole; the channel scene is ~1.5e5 particles so a full
        round-trip is a few MB and is not worth a custom kernel.
        """
        wp = self._wp
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

    # ---------------------------------------------------------------- the boundary
    def apply(self):
        x = self.s.x()
        v = self.s.v()
        act = self.sel[:self.n] == 0

        # ---- OUTFLOW (B7). Two clauses, and they are different things ---------------
        # (a) depth control: inside the outflow band, anything standing above the target
        #     free surface is removed. This is the re-expression of Zhao's outlet
        #     pressure condition, which cannot be imposed directly because no pressure
        #     field exists (B7).
        # (b) the outflow proper: anything past x_out has left the reach. Without this
        #     clause the water simply piles against the domain wall instead of the
        #     removed downstream wall, and the arm silently becomes the tank again.
        band = act & (x[:self.n, 0] >= self.x_out - self.out_len)
        kill_depth = band & (x[:self.n, 2] > self.floor + self.target)
        kill_past = act & (x[:self.n, 0] > self.x_out)
        kill = kill_depth | kill_past
        n_kill = int(kill.sum())
        if n_kill:
            self.sel[:self.n][kill] = 1
            self.n_deactivated_total += n_kill
            act = self.sel[:self.n] == 0

        # ---- INFLOW: activate from the pool only if the inlet is running below target
        n_act = 0
        if self.mode == "sink_source":
            d_in = active_depth_at(x[:self.n], act, self.x_in + 0.5 * self.relax_len,
                                   0.5 * (x[:self.n, 1].min() + x[:self.n, 1].max()),
                                   0.5 * self.relax_len, self.floor, self.h)
            deficit = self.target - d_in
            if deficit > 0.0:
                # volume the inlet band is short of, converted to particles
                width = float(x[:self.n, 1].max() - x[:self.n, 1].min())
                need = int(deficit * self.relax_len * width / self.h ** 3)
                pool = np.flatnonzero(self.sel[:self.n] == 1)
                n_act = int(min(need, len(pool), self.max_activate))
                if n_act > 0:
                    # take the pool in the order it died, so the oldest water returns first
                    idx = pool[:n_act]
                    # re-seed on a lattice in the inlet band, below the target surface:
                    # a demand-driven re-seed, NOT a one-for-one periodic wrap
                    rng = np.random.default_rng(self.n_activated_total)
                    xs = self.x_in + rng.uniform(0.0, self.relax_len, n_act)
                    ys = x[:self.n, 1].min() + rng.uniform(0.0, width, n_act)
                    zs = self.floor + rng.uniform(0.0, self.target, n_act)
                    x[idx, 0], x[idx, 1], x[idx, 2] = xs, ys, zs
                    v[idx, 0], v[idx, 1], v[idx, 2] = self.u, 0.0, 0.0
                    self.sel[:self.n][idx] = 0
                    self._reset_particle_state(idx)
                    self.n_activated_total += n_act
                    act = self.sel[:self.n] == 0

        # ---- Zhao velocity inlet, identical treatment to the other arms -------------
        xs_all = x[:self.n, 0]
        rb = act & (xs_all >= self.x_in) & (xs_all < self.x_in + self.relax_len)
        if rb.any():
            w = 1.0 - (xs_all[rb] - self.x_in) / self.relax_len
            a = self.relax_gain * w
            vb = v[:self.n][rb]
            vb[:, 0] = (1.0 - a) * vb[:, 0] + a * self.u
            vb[:, 1] *= (1.0 - a)
            v[:self.n][rb] = vb

        self.s.set_x(x)
        self.s.set_v(v)
        self._push_selection()
        self.history.append({"n_kill": n_kill, "n_act": n_act,
                             "n_active": int(act.sum())})
        return n_kill, n_act

    # ---------------------------------------------------------------- reporting
    def active_mask(self):
        return self.sel[:self.n] == 0

    def water_volume(self):
        """Volume still participating in the fluid, m^3. Falls under `sink_only`."""
        return float((self.sel[:self.n] == 0).sum()) * self.h ** 3
