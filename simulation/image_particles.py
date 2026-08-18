"""Image-particle wall boundary for a fixed-pool MPM engine.

THE DEFECT THIS TARGETS, measured not assumed. Register item 24: in the same
Yaris scene, floor-penetration clamps run 8009 in the closed box against 258334
in the open channel, a factor of 32, and 87.2 percent of all clamping in recycle
mode is the z axis. Sustained flow over a grid-BC wall goes through it. The hull
passthrough that item 24 also records, and that items 18 and 19 found refinement
WORSENING, is the same defect at a different surface.

Schulz and Sutmann (2019) name the mechanism: a wall implemented by zeroing grid
momentum gives the fluid no pressure support at the boundary, and the resulting
stress error "distorts the stress multiple grid lengths into the object". Their
remedy is image particles: a mirrored population across the wall so the grid sees
a symmetric state and the transfer is correct instead of truncated.

THE TRANSLATION, and why it is not the paper's method verbatim. warpmpm allocates
every particle at load_particles and exposes no add or remove
(third_party/mpm-engine-544c93dd-solver-core/core/solver.py:103), so images cannot
be created on demand. They are carved out of the pool at load time and repositioned
every tick, exactly as the in/outflow BC recycles rather than adds and removes.

THREE APPROXIMATIONS, all forced, all stated rather than buried:

(a) J IS NOT COPIED FROM THE SOURCE. An image ought to carry its source's
    compression state. F has no setter (solver.py exposes F() and F_torch() and
    nothing else), so an image carries whatever J its own history produced. The
    pairing below is deterministic and index-stable precisely to keep an image
    paired with a similar source from tick to tick, so its J tracks a similar
    depth rather than jumping. The residual error is real. Measure the effect,
    never assert it.

(b) IMAGES CARRY MASS. Particle volume is fixed at load, so an image contributes
    a full h^3 of fluid to the grid. That is what makes it work, and it also means
    a badly placed image is a real mass error, not a bookkeeping one. Images live
    strictly below the wall plane, inside the region the wall already excludes.

(c) SURPLUS IMAGES DUPLICATE. If fewer water particles sit in the band than there
    are images, the surplus are assigned cyclically to the sources that do exist,
    which doubles mass at those mirrored points. That is why n_image should be set
    below the typical band population, and why `duplicated_last` is reported every
    tick instead of being silently absorbed.

Images are ordinary fluid particles to the solver. Every diagnostic that counts
water MUST exclude the image range, or depth, passthrough and particle counts all
shift for a reason that has nothing to do with the physics being measured.
"""

from __future__ import annotations

import numpy as np

__all__ = ["ImageParticleWall"]


class ImageParticleWall:
    """Mirror water across a horizontal wall into a reserved slice of the pool.

    Layout: water occupies [0, n_water), images occupy [n_water, n_water+n_image),
    and anything above that (a rigid vehicle) is untouched.

    mode:
      "free_slip"  image velocity (vx, vy, -vz). Mirrors the canonical floor,
                   which is add_plane(..., "slip", friction=0.55).
      "no_slip"    image velocity (-vx, -vy, -vz). The stronger condition; use it
                   only if the wall it models is genuinely no-slip, such as the
                   add_box bed in the overfall scene.
    """

    def __init__(self, n_water, n_image, plane_z, dx, band_cells=1.0,
                 mode="free_slip", safe_lo=None, safe_hi=None):
        if mode not in ("free_slip", "no_slip"):
            raise ValueError("mode must be 'free_slip' or 'no_slip'")
        if n_image <= 0:
            raise ValueError("n_image must be positive")
        self.n_water = int(n_water)
        self.n_image = int(n_image)
        self.lo = self.n_water
        self.hi = self.n_water + self.n_image
        self.plane_z = float(plane_z)
        self.dx = float(dx)
        self.band = float(band_cells) * float(dx)
        self.mode = mode
        # Guard-safe box for image POSITIONS. The engine raises if any particle
        # comes within 1.5 dx of the grid edge, and it counts images like any other
        # particle. Measured 2026-08-18: without this, a 12000-image run tripped the
        # guard at x=9.0648 against a limit of 9.0537. Clamping an image is
        # bookkeeping on a synthetic construct, not a physics change, but it does
        # mean an image whose source sits in the last cell is displaced, so
        # clamped_images is reported rather than absorbed.
        self.safe_lo = safe_lo
        self.safe_hi = safe_hi
        self.clamped_images = 0
        self.duplicated_last = 0
        self.sources_last = 0
        # Park just under the wall, NOT far under it. The engine raises if any
        # particle sits within 1.5 dx of the grid edge (solver.py:_update_grid_box),
        # and the canonical floor is only 3 dx up, so a deep park would trip the
        # guard before the scene ever stepped.
        self.parked_z = self.plane_z - 0.5 * self.band

    def park(self, x, v):
        """Initial placement, before the first step.

        Images start stacked well below the wall rather than at the wall, so that
        a scene which never calls apply() has them somewhere inert and obvious
        instead of somewhere plausible.
        """
        x[self.lo:self.hi, 2] = self.parked_z
        v[self.lo:self.hi] = 0.0

    def apply(self, x, v):
        """Reposition every image as the mirror of a band particle. In place.

        Returns the number of distinct sources used. The caller writes x and v
        back with set_x / set_v.
        """
        w = x[:self.n_water]
        band = (w[:, 2] >= self.plane_z) & (w[:, 2] < self.plane_z + self.band)
        idx = np.flatnonzero(band)
        self.sources_last = int(idx.size)
        if idx.size == 0:
            # Nothing to mirror. Park rather than leave images wherever they were,
            # which would be a stale ghost wall under a dry floor.
            x[self.lo:self.hi, 2] = self.parked_z
            v[self.lo:self.hi] = 0.0
            self.duplicated_last = 0
            return 0
        # Deterministic and index-stable: sorting by particle index (not by depth)
        # keeps image k paired with the same source across ticks for as long as
        # that source stays in the band, which is what makes approximation (a)
        # tolerable. Sorting by depth would reshuffle the pairing every tick.
        if idx.size >= self.n_image:
            sel = idx[:self.n_image]
            self.duplicated_last = 0
        else:
            reps = int(np.ceil(self.n_image / idx.size))
            sel = np.tile(idx, reps)[:self.n_image]
            self.duplicated_last = int(self.n_image - idx.size)
        src_x = w[sel]
        src_v = v[:self.n_water][sel]
        x[self.lo:self.hi, 0] = src_x[:, 0]
        x[self.lo:self.hi, 1] = src_x[:, 1]
        x[self.lo:self.hi, 2] = 2.0 * self.plane_z - src_x[:, 2]
        if self.mode == "free_slip":
            v[self.lo:self.hi, 0] = src_v[:, 0]
            v[self.lo:self.hi, 1] = src_v[:, 1]
        else:
            v[self.lo:self.hi, 0] = -src_v[:, 0]
            v[self.lo:self.hi, 1] = -src_v[:, 1]
        v[self.lo:self.hi, 2] = -src_v[:, 2]
        if self.safe_lo is not None:
            blk = x[self.lo:self.hi]
            out = (blk < self.safe_lo) | (blk > self.safe_hi)
            n_out = int(out.any(axis=1).sum())
            if n_out:
                self.clamped_images += n_out
                np.clip(blk, self.safe_lo, self.safe_hi, out=blk)
        return int(idx.size)


def _selftest():
    dx, plane = 0.1472, 0.4416
    nw, ni, nveh = 800, 200, 30
    rng = np.random.default_rng(0)
    n = nw + ni + nveh
    x = np.zeros((n, 3), np.float32)
    v = rng.normal(0, 0.5, (n, 3)).astype(np.float32)
    # a third of the water inside the one-cell band above the wall
    x[:nw, 0] = rng.uniform(1.0, 8.0, nw)
    x[:nw, 1] = rng.uniform(1.0, 8.0, nw)
    x[:nw, 2] = np.concatenate([
        rng.uniform(plane, plane + dx, nw // 3),
        rng.uniform(plane + dx, plane + 0.30, nw - nw // 3)])
    x[nw + ni:, 2] = 5.0
    x0, v0 = x.copy(), v.copy()

    w = ImageParticleWall(nw, ni, plane, dx, band_cells=1.0, mode="free_slip")
    w.park(x, v)
    assert np.allclose(x[nw:nw + ni, 2], plane - 0.5 * dx), "park did not place images below"
    x, v = x0.copy(), v0.copy()
    ns = w.apply(x, v)

    # 1. water and vehicle untouched
    assert np.array_equal(x[:nw], x0[:nw]) and np.array_equal(v[:nw], v0[:nw])
    assert np.array_equal(x[nw + ni:], x0[nw + ni:]), "vehicle slice was written"
    # 2. every image is strictly below the wall
    zi = x[nw:nw + ni, 2]
    assert (zi < plane).all(), (zi.min(), zi.max())
    # 3. mirror geometry is exact for the paired sources
    band = (x0[:nw, 2] >= plane) & (x0[:nw, 2] < plane + dx)
    idx = np.flatnonzero(band)
    assert ns == idx.size and ns > 50, (ns, idx.size)
    sel = idx[:ni] if idx.size >= ni else np.tile(idx, int(np.ceil(ni / idx.size)))[:ni]
    assert np.allclose(x[nw:nw + ni, 2], 2.0 * plane - x0[sel, 2], atol=1e-5)
    assert np.allclose(x[nw:nw + ni, :2], x0[sel, :2], atol=1e-5)
    # 4. free slip reflects only the normal component
    assert np.allclose(v[nw:nw + ni, 2], -v0[sel, 2], atol=1e-5)
    assert np.allclose(v[nw:nw + ni, :2], v0[sel, :2], atol=1e-5)
    # 5. no slip reflects all three
    x2, v2 = x0.copy(), v0.copy()
    w2 = ImageParticleWall(nw, ni, plane, dx, 1.0, mode="no_slip")
    w2.apply(x2, v2)
    assert np.allclose(v2[nw:nw + ni], -v0[sel], atol=1e-5)
    # 6. duplication is counted, not hidden, when the band is thin
    x3, v3 = x0.copy(), v0.copy()
    x3[:nw, 2] = plane + 0.20                      # empty the band except a few
    x3[:5, 2] = plane + 0.5 * dx
    w3 = ImageParticleWall(nw, ni, plane, dx, 1.0)
    ns3 = w3.apply(x3, v3)
    assert ns3 == 5 and w3.duplicated_last == ni - 5, (ns3, w3.duplicated_last)
    # 7. a dry wall parks the images instead of leaving a stale ghost layer
    x4, v4 = x0.copy(), v0.copy()
    x4[:nw, 2] = plane + 0.25
    w4 = ImageParticleWall(nw, ni, plane, dx, 1.0)
    w4.apply(x4, v4)
    assert w4.apply(x4, v4) == 0
    assert np.allclose(x4[nw:nw + ni, 2], plane - 0.5 * dx)
    # 8. pairing is stable across a tick when sources do not change
    xa, va = x0.copy(), v0.copy()
    w5 = ImageParticleWall(nw, ni, plane, dx, 1.0)
    w5.apply(xa, va); first = xa[nw:nw + ni].copy()
    w5.apply(xa, va)
    assert np.allclose(xa[nw:nw + ni], first), "pairing reshuffled with unchanged input"
    # 9. the guard-safe clamp keeps images inside the box and counts the moves
    x6, v6 = x0.copy(), v0.copy()
    lo6 = np.array([2.0, 2.0, plane - 10.0], np.float32)
    hi6 = np.array([7.0, 7.0, plane + 10.0], np.float32)
    w6 = ImageParticleWall(nw, ni, plane, dx, 1.0, safe_lo=lo6, safe_hi=hi6)
    w6.apply(x6, v6)
    blk6 = x6[nw:nw + ni]
    assert (blk6[:, :2] >= 2.0).all() and (blk6[:, :2] <= 7.0).all(), "clamp did not hold"
    assert w6.clamped_images > 0, "fixture spans the box, so some clamp must have fired"
    print("image_particles selftest: 9 checks PASS")


if __name__ == "__main__":
    _selftest()
