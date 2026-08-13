"""Open-channel conveyance instead of a filling tank.

THE PROBLEM THIS ADDRESSES, MEASURED
------------------------------------
`docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md` section 4 measures the canonical scene:
the bow probe swings -24.0 to +31.9 percent about the nominal 0.30 m depth, the footprint
probe -24.7 to +25.0 percent, and **only 20 of 90 frames (22 percent) sit within +/-10
percent of the labelled depth**. Water piles up 2.5x against the closed downstream wall by
mid-run (0.2729 -> 0.6750 m). The streamwise fetch is 9.4217 / 4.2014 = 2.2 hull-lengths.
So "depth 0.30 m" labels the initial condition, not the experiment.

WHAT IS PORTED, AND WHAT DELIBERATELY IS NOT
--------------------------------------------
Zhao, Bolognin, Liang, Rohe & Vardon 2019, Computers & Fluids 179:27-33,
DOI 10.1016/j.compfluid.2018.10.007.

  PORTED    their velocity-controlled inlet. It is a prescribed-velocity relaxation zone
            at the upstream end, which transfers directly.

  NOT PORTED, DELIBERATELY: their pressure-controlled outflow. **warpmpm has no pressure
            field at all** - `grep -ci pressure kernels/mpm_solver_warp.py` returns 0
            across 3,181 lines at the pinned SHA (register B7). Pressure exists only
            implicitly, per particle, via J = det(F) inside the weakly-compressible EOS.
            A literal port is therefore impossible, not merely inadvisable, and register
            B7 states the rule outright: **never describe a warpmpm outflow BC as
            "pressure-controlled."**

THE SUBSTITUTE, AND WHY THIS SHAPE
----------------------------------
Register F5 records that particle count is FIXED at load: no particle is created or
destroyed during a run. So an outflow that deletes particles is not available either.
The construction that satisfies both constraints is a **streamwise periodic wrap plus an
inlet relaxation zone**:

  outlet   a particle crossing x_out is wrapped to x_in, KEEPING its (y, z). Keeping the
           lateral and vertical coordinates makes this a periodic boundary rather than a
           re-seeding, so the depth profile is carried across the seam instead of being
           re-invented, and no free parameter is introduced.
  inlet    inside a relaxation band of width `relax_len`, streamwise velocity is driven
           toward `u_target`. This is Zhao's velocity inlet, and it is what stops the
           wake from re-entering unrelaxed - the standard periodic-channel artifact.

A pure periodic box would recirculate the vehicle's own wake into its own approach flow.
The relaxation band is what makes the periodicity admissible, so it is not an optional
extra and must not be disabled to "simplify" the scene.

WHAT THIS IS NOT
----------------
This is not a validated open-channel BC. It is a conveyance mechanism that removes the
downstream pile-up. The criterion it should be judged on is the assessment's own metric,
the fraction of frames within +/-10 percent of nominal depth, which this module measures
directly so the 22 percent baseline can be beaten or not on its own terms.
"""
from __future__ import annotations

import numpy as np

__all__ = ["ChannelRecycler", "depth_hold_fraction"]


class ChannelRecycler:
    """Streamwise periodic wrap + upstream velocity relaxation, applied per frame.

    Parameters
    ----------
    x_in, x_out   streamwise bounds of the conveying reach, metres.
    u_target      target streamwise velocity, m/s.
    relax_len     width of the inlet relaxation band, metres. Velocity is blended toward
                  u_target with weight 1 at x_in falling linearly to 0 at x_in+relax_len.
    relax_gain    blend fraction applied per call at full weight. 1.0 is a hard Dirichlet
                  clamp (what sim_standing.py does); below 1.0 is a softer relaxation that
                  does not discard the fluid's own dynamics in one step.
    """

    def __init__(self, solver, n_water, x_in, x_out, u_target,
                 relax_len=None, relax_gain=0.5, wrap=True,
                 sponge_len=None, sponge_gain=0.0):
        # `wrap=False` gives the inlet relaxation WITHOUT the periodic outlet, which is
        # what the tank control arm needs. It exists because the first attempt disabled
        # wrapping by passing x_out + 1e9, and the UPSTREAM wrap branch still fired and
        # teleported particles to x = 1e9, tripping the solver's own edge guard
        # ("particles within 2 cells of the grid edge ... x in [0.1814, 1000000000.0]").
        # A sentinel that only half-disables a branch is a bug, not a configuration.
        self.s = solver
        self.n = int(n_water)
        self.x_in = float(x_in)
        self.x_out = float(x_out)
        self.u = float(u_target)
        self.reach = self.x_out - self.x_in
        if self.reach <= 0:
            raise ValueError("x_out must exceed x_in")
        self.relax_len = float(relax_len if relax_len is not None else 0.25 * self.reach)
        self.relax_gain = float(relax_gain)
        self.wrap = bool(wrap)
        # Downstream relaxation ("sponge") zone. MEASURED NEED, not a precaution: with
        # sponge_gain = 0 the periodic arm scored 27/90 on the depth-hold metric against
        # 53/90 for the closed-tank control, i.e. the naive wrap was WORSE. A periodic
        # domain has no energy sink, so the surge recirculates while the inlet keeps
        # injecting momentum. This is the standard numerical-wave-tank remedy (relaxation
        # zones, e.g. Jacobsen, Fuhrman & Fredsoe 2012): blend velocity toward the target
        # over a band before the outlet so the wave is absorbed rather than recycled.
        self.sponge_len = float(sponge_len if sponge_len is not None else 0.30 * self.reach)
        self.sponge_gain = float(sponge_gain)
        self.n_wrapped_total = 0

    def apply(self):
        """One application. Returns the number of particles wrapped this call."""
        x = self.s.x()
        v = self.s.v()
        xs = x[:self.n, 0]

        # --- outlet: periodic wrap, keeping (y, z) -----------------------------------
        n_wrap = 0
        if self.wrap:
            past = xs > self.x_out
            n_wrap = int(past.sum())
            if n_wrap:
                xs[past] -= self.reach      # wrap, do not re-seed
                self.n_wrapped_total += n_wrap
            # a particle that ran upstream of the inlet wraps the other way
            before = xs < self.x_in
            if before.any():
                xs[before] += self.reach

        # --- inlet: Zhao velocity relaxation over a band -----------------------------
        band = (xs >= self.x_in) & (xs < self.x_in + self.relax_len)
        if band.any():
            w = 1.0 - (xs[band] - self.x_in) / self.relax_len       # 1 at inlet -> 0
            a = self.relax_gain * w
            vb = v[:self.n][band]
            vb[:, 0] = (1.0 - a) * vb[:, 0] + a * self.u
            vb[:, 1] *= (1.0 - a)          # damp cross-stream drift in the relaxed zone
            v[:self.n][band] = vb

        # --- outlet sponge: absorb before wrapping -----------------------------------
        if self.sponge_gain > 0.0:
            sp = xs > (self.x_out - self.sponge_len)
            if sp.any():
                w = (xs[sp] - (self.x_out - self.sponge_len)) / self.sponge_len  # 0 -> 1
                a = self.sponge_gain * w
                vs_ = v[:self.n][sp]
                vs_[:, 0] = (1.0 - a) * vs_[:, 0] + a * self.u
                vs_[:, 1] *= (1.0 - a)
                vs_[:, 2] *= (1.0 - a)      # kill the vertical surge, the thing that recirculates
                v[:self.n][sp] = vs_

        self.s.set_x(x)
        self.s.set_v(v)
        return n_wrap


def depth_hold_fraction(depths, nominal, tol=0.10):
    """Fraction of frames whose depth sits within +/-tol of nominal.

    This is the assessment's own metric, reproduced exactly so the result is comparable:
    the canonical scene scores 20 of 90 frames = 22 percent at tol = 0.10 against a
    nominal of 0.30 m. Anything reported here must be compared against that number and
    not against a fresh criterion invented alongside the fix.
    """
    d = np.asarray(depths, dtype=float)
    ok = np.abs(d - nominal) <= tol * nominal
    return float(ok.mean()), int(ok.sum()), int(len(d))


def water_depth_at(solver, n_water, x_centre, y_centre, half_window, floor, h):
    """Free-surface depth above `floor` in a column centred on (x_centre, y_centre).

    Column-sampled rather than domain-averaged, because the assessment's bow and
    footprint probes are local: a domain average would hide exactly the local excursion
    that the +/-10 percent metric is about.
    """
    x = solver.x()[:n_water]
    sel = ((np.abs(x[:, 0] - x_centre) <= half_window)
           & (np.abs(x[:, 1] - y_centre) <= half_window))
    if sel.sum() < 20:
        return 0.0
    return float(np.percentile(x[sel, 2], 99.0) + 0.5 * h - floor)
