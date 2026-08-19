"""Does the free-surface ESTIMATOR explain job B's criterion-3 FAIL, or does the solver?

WHY THIS EXISTS
---------------
Job B fails criterion 3 at every window: `fz_over_analytic_measured` runs +34 to +64
percent against a 25 percent FAIL band. `docs/R5_PHYSICS_JOB_B_RESULT.md` has been through
four audit rounds and what survives is one sentence, its section 13.7:

    "The band is the dominant source of band-dependence in this scene."

That is weaker than it looks. Section 13.1 makes the point sharply and correctly: the band
sweep held `dx` FIXED, so it has ZERO POWER over any mechanism that scales with `dx`. The
free-surface estimator is exactly such a mechanism. So after four audits the field is still
two live explanations that no existing run separates:

  E1  THE DENOMINATOR IS WRONG. `SphereTank.measure_surface` estimates the free surface
      from a 99th percentile of water-particle z AFTER DISCARDING every particle within
      2R of the sphere axis. That annulus is where the surface is deformed by the body.
      If the discarded near field sits higher than the far field, the analytic cap volume
      in the denominator is too small and the ratio is inflated with no solver error.
  E3  THE FORCE IS CONTAMINATED BY THE CONTACT TREATMENT. `add_sdf_collider` gates its
      impulse at `sd <= band` and defaults `band` to `dx`
      (mpm_solver_warp.py:2627, :2711), so the fluid sees a body inflated by about one
      cell and really does push harder.

(E2, "the weakly-compressible scheme over-predicts", is bounded out arithmetically in
section 4 of the write-up and is not modelled here.)

THE MEASUREMENT THAT MOTIVATES THE RUN
--------------------------------------
`--offline` fits three one-parameter models to the MEASURED force of every existing fixed
sphere run, and the finding is a NEGATIVE one that has to be stated before any test is
designed: restricted to the `band_mult = 1.0` runs, where both mechanisms have power,

    collider inflated by k*dx        and        surface under-read by k*dx

fit the same data equally well. They are near-degenerate on a resolution ladder. No
existing run can separate them, which is why this file also carries a run.

THE PRE-REGISTERED TEST
-----------------------
The two models are NOT degenerate on the free surface itself, and that is the whole point:

  Under E1 the near-field surface must genuinely sit about `SURF_OFFSET_FITTED_DX * dx`
  above the far field, because that is the only place the missing denominator volume can
  come from. At g64 that is about 25 mm.
  Under E3 the near-field surface need only sit a few mm above the far field, the
  displacement rise of the inflated body, which section 13.5 already measured at 0.79 to
  1.02 of its own prediction.

So: MEASURE THE SURFACE OVER THE ANNULUS THE ESTIMATOR THROWS AWAY. The thresholds below
are fixed BEFORE the run and are not to be moved afterwards. They are stated as a ratio so
that they do not depend on which window is graded.

    PREDICT_E1   ratio against the near-field surface falls below 1.10
    PREDICT_E3   ratio against the near-field surface stays above 1.25
    Anything in between separates nothing and must be reported as such.

WHAT THIS FILE DOES NOT DO
--------------------------
It does not edit `sphere_heave.py`, `grade_job_b.py`, the manifest, or
`r7_jobb_bcfix_ab.py`. `--run` SUBCLASSES `SphereTank` and its `measure_surface` override
returns `super().measure_surface()` unchanged, so the value that feeds every published
column is bit-identical and the diagnostics are additive. In `--fixed` mode the surface
never feeds the dynamics at all (`self.free` is False, so `advance` integrates nothing),
which makes the physics risk of this instrumentation exactly zero.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import statistics as st
import sys
from pathlib import Path

# --- fixed in advance, do not edit these after seeing a result -------------------------
PREDICT_E1_RATIO_BELOW = 1.10
PREDICT_E3_RATIO_ABOVE = 1.25
# The surface-offset model's fitted coefficient, from --offline on the 8 DISTINCT
# band_mult=1.0 runs that existed on 2026-08-19. Quoted so the required magnitude can be
# re-derived rather than trusted. It moved from 1.3565 to 1.3875 when the duplicate filter
# was made transitive, which is a methodological fix made BEFORE any run landed; the two
# threshold constants above have not moved and are not to be.
SURF_OFFSET_FITTED_DX = 1.3875

RHO_W_BENCHMARK = 998.2     # Kramer 2021 Table 1
G_ENGINE = 9.81             # the engine's own hardcoded g, not the benchmark's 9.82


def cap_volume(sub: float, radius: float) -> float:
    """Spherical-cap volume, identical to SphereTank.buoyancy_at including its clamp."""
    sub = min(max(sub, 0.0), 2.0 * radius)
    return math.pi * sub * sub * (3.0 * radius - sub) / 3.0


# ======================================================================================
# OFFLINE: what the existing runs can and cannot settle
# ======================================================================================
# Two runs whose per-frame fz never differs by more than this FRACTION OF THE 69.218 N
# TARGET are the same simulation re-executed, not two samples. Normalising by the target
# rather than by the instantaneous force is deliberate and matches job B result 13.5's
# 2.6e-5: an early frame has fz near zero, so a per-frame relative difference blows up on
# the transient and is not a measure of reproducibility.
#
# THE THRESHOLD IS NOT TUNED. `--offline` prints the full pairwise distance matrix; the
# distribution is bimodal by four orders of magnitude, re-executions at 4e-5 to 2e-4 and
# genuinely distinct runs at 4e-2 upward, so anything in that gap gives the same partition.
# Grouping is by TRANSITIVE CLOSURE. Without it the partition depends on file order: at a
# 1e-3 per-frame relative tolerance, 918043 ~ 918240 ~ band1.0 but 918043 !~ band1.0, and
# one simulation ends up counted twice.
DUPLICATE_TOL_FRAC_OF_TARGET = 1.0e-3
TARGET_N = 69.2180


def _load(dirpath: str, verbose: bool = True) -> list[dict]:
    """Reduce every sphere_heave payload under dirpath to one record per run.

    Runs that predate `surface_z_measured_m` are skipped rather than patched: the whole
    question is about that column, so a run without it has nothing to say here.
    """
    cand = []
    for f in sorted(glob.glob(os.path.join(dirpath, "**", "*.json"), recursive=True)):
        try:
            p = json.loads(Path(f).read_text())
        except (ValueError, OSError):
            continue
        cfg, rows = p.get("config", {}), p.get("rows", [])
        if not rows or "surface_z_measured_m" not in rows[-1]:
            continue
        if cfg.get("mode") != "fixed":
            continue
        w = rows[-50:]
        radius = cfg["ref_radius_m"]
        cand.append({
            "name": os.path.relpath(f, dirpath),
            "radius": radius,
            "dx": cfg["dx_m"],
            "band_mult": float(cfg.get("band_mult", 1.0)),
            "n_grid": cfg["n_grid"],
            "fz": st.mean(x["fz_N"] for x in w),
            "surf": st.mean(x["surface_z_measured_m"] for x in w),
            "sub": st.mean(x["surface_z_measured_m"] for x in w) - (st.mean(x["z_m"] for x in w) - radius),
            "series": [x["fz_N"] for x in rows],
        })

    # Pairwise distance: the largest per-frame |dFz| over the overlap, as a fraction of the
    # 69.218 N target. Runs on different grids or bands are never comparable.
    m = len(cand)
    dist = [[float("inf")] * m for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            a, b = cand[i], cand[j]
            n = min(len(a["series"]), len(b["series"]))
            if n < 10 or a["n_grid"] != b["n_grid"] or a["band_mult"] != b["band_mult"]:
                continue
            dv = max(abs(a["series"][k] - b["series"][k]) for k in range(n)) / TARGET_N
            dist[i][j] = dist[j][i] = dv

    parent = list(range(m))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(m):
        for j in range(i + 1, m):
            if dist[i][j] < DUPLICATE_TOL_FRAC_OF_TARGET:
                parent[find(i)] = find(j)

    groups: dict[int, list[int]] = {}
    for i in range(m):
        groups.setdefault(find(i), []).append(i)
    if verbose:
        finite = sorted(dist[i][j] for i in range(m) for j in range(i + 1, m)
                        if dist[i][j] < float("inf"))
        if finite:
            below = [v for v in finite if v < DUPLICATE_TOL_FRAC_OF_TARGET]
            above = [v for v in finite if v >= DUPLICATE_TOL_FRAC_OF_TARGET]
            print(f"  pairwise max|dFz|/{TARGET_N:g}N over {len(finite)} comparable pairs: "
                  f"{len(below)} below the tolerance "
                  f"(max {max(below):.2e})" if below else "  no re-executions found")
            if above:
                print(f"  {len(above)} above (min {min(above):.2e}); "
                      f"the gap between the two groups is the justification for {DUPLICATE_TOL_FRAC_OF_TARGET:g}")
    out: list[dict] = []
    for _root, members in sorted(groups.items(), key=lambda kv: min(kv[1])):
        keep = min(members)
        for i in members:
            if i != keep and verbose:
                print(f"  [re-execution dropped] {cand[i]['name']} == {cand[keep]['name']} "
                      f"(max|dFz| {dist[i][keep] * TARGET_N:.2e} N)")
        out.append(cand[keep])
    for d in out:
        d.pop("series", None)
    return out


def _rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def _fit(recs, model, lo, hi, n=40000) -> tuple[float, float]:
    best = (lo, float("inf"))
    for i in range(n + 1):
        v = lo + (hi - lo) * i / n
        e = _rms([(RHO_W_BENCHMARK * G_ENGINE * model(d, v) - d["fz"]) / d["fz"]
                  for d in recs])
        if e < best[1]:
            best = (v, e)
    return best


MODELS = {
    # b = k * band. The collider acts as a sphere of radius R+b whose bottom is also b
    # lower, so BOTH the radius and the submergence gain b. Zero free parameters beyond k.
    "BAND    collider += k*band": (lambda d, k: cap_volume(d["sub"] + k * d["band_mult"] * d["dx"],
                                                           d["radius"] + k * d["band_mult"] * d["dx"]),
                                   0.2, 1.6, "k"),
    # A fixed surface under-read, in metres, independent of resolution.
    "SURFACE surf += Delta     ": (lambda d, v: cap_volume(d["sub"] + v, d["radius"]),
                                   0.0, 0.08, "m"),
    # A surface under-read proportional to dx. This is the estimator hypothesis in the
    # form that competes with BAND on equal terms.
    "SURFACE surf += k*dx      ": (lambda d, k: cap_volume(d["sub"] + k * d["dx"], d["radius"]),
                                   0.0, 4.0, "k"),
}


def offline(dirpath: str) -> None:
    recs = _load(dirpath)
    if not recs:
        raise SystemExit(f"no gradeable fixed-sphere payloads under {dirpath}")
    print(f"{len(recs)} distinct fixed-sphere runs (exact re-executions dropped)\n")
    hdr = (f"{'run':42s} {'n_grid':>6} {'dx_mm':>6} {'band/dx':>7} {'fz_N':>8} "
           f"{'sub_mm':>7} {'ratio':>6}")
    print(hdr)
    print("-" * len(hdr))
    for d in recs:
        ratio = d["fz"] / (RHO_W_BENCHMARK * G_ENGINE * cap_volume(d["sub"], d["radius"]))
        print(f"{d['name']:42s} {d['n_grid']:6d} {d['dx']*1000:6.2f} {d['band_mult']:7.2f} "
              f"{d['fz']:8.3f} {d['sub']*1000:7.2f} {ratio:6.3f}")

    for label, subset in (("ALL RUNS", recs),
                          ("band_mult = 1.0 ONLY", [d for d in recs if d["band_mult"] == 1.0])):
        print(f"\n=== {label}, {len(subset)} runs: one global parameter each ===")
        null = _rms([(RHO_W_BENCHMARK * G_ENGINE * cap_volume(d["sub"], d["radius"]) - d["fz"])
                     / d["fz"] for d in subset])
        print(f"  {'NULL, no correction':28s}            RMS rel err = {null:.4f}")
        for name, (model, lo, hi, unit) in MODELS.items():
            v, e = _fit(subset, model, lo, hi)
            print(f"  {name:28s} {unit}={v:8.4f}  RMS rel err = {e:.4f}")

    print("\nREAD THIS BEFORE DRAWING A CONCLUSION FROM THE TABLE ABOVE.")
    print("  On ALL RUNS the BAND model wins, but that comparison is decided by the")
    print("  band-sweep arms, and per job B result section 13.1 an experiment that holds")
    print("  dx fixed has no power over a dx-scaling rival. The honest comparison is the")
    print("  band_mult = 1.0 subset, and there the two models are near-degenerate.")
    # --- how demanding is E1, given a ceiling that already exists in the payloads? ------
    # water_z_max_m is the single highest water particle anywhere, INCLUDING the annulus the
    # estimator discards. It is therefore a hard CEILING on any near-field surface: a 99th
    # percentile over a subpopulation cannot exceed the population maximum. It is an
    # EXTREMAL quantity, so per CLAUDE.md it is used only as a bound here, never for a
    # trend and never for a convergence claim.
    ceil = []
    for f in sorted(glob.glob(os.path.join(dirpath, "**", "*.json"), recursive=True)):
        try:
            p = json.loads(Path(f).read_text())
        except (ValueError, OSError):
            continue
        rows = p.get("rows", [])
        if not rows or "water_z_max_m" not in rows[-1] or "surface_z_measured_m" not in rows[-1]:
            continue
        cfg = p["config"]
        if cfg.get("mode") != "fixed" or float(cfg.get("band_mult", 1.0)) != 1.0:
            continue
        w = rows[-50:]
        gap = st.mean(x["water_z_max_m"] - x["surface_z_measured_m"] for x in w)
        ceil.append((os.path.relpath(f, dirpath), cfg["n_grid"], cfg["dx_m"], gap))
    if ceil:
        print("\n=== HOW DEMANDING IS E1? a ceiling that already exists in the payloads ===")
        print("water_z_max is the single highest particle ANYWHERE, so the near-field 99th")
        print("percentile cannot exceed it. EXTREMAL: a bound only, never a trend.\n")
        hdr2 = (f"{'run':42s} {'n_grid':>6} {'E1 needs':>9} {'ceiling':>9} "
                f"{'needs/ceiling':>14}")
        print(hdr2)
        print("-" * len(hdr2))
        for name, n_grid, dx, gap in ceil:
            need = SURF_OFFSET_FITTED_DX * dx
            flag = "  IMPOSSIBLE" if need > gap else ""
            print(f"{name:42s} {n_grid:6d} {need*1000:8.2f}mm {gap*1000:8.2f}mm "
                  f"{need/gap:14.2f}{flag}")
        print("\nE1 is not ruled out by this ceiling, but it requires the annulus 99th")
        print("percentile to reach that fraction of the way to the tank's highest single")
        print("particle, which is a flat elevated shelf and not a splash. The run measures")
        print("the percentile directly, so this bound is superseded the moment it lands.")

    print("\nPRE-REGISTERED, fixed before the run, from --run's near-field surface:")
    print(f"  E1 (estimator) is supported if ratio_nearfield < {PREDICT_E1_RATIO_BELOW}")
    print(f"  E3 (contact band) is supported if ratio_nearfield > {PREDICT_E3_RATIO_ABOVE}")
    print("  In between separates nothing and must be reported as separating nothing.")


# ======================================================================================
# FLOOR: can criterion 3 produce an informative PASS at all?
# ======================================================================================
def floor_report(recs=None) -> None:
    """The smallest |ratio - 1| criterion 3 could report with a PERFECT coupling.

    WHY THIS EXISTS. d19-priorcode measured gate P-2's zero-penetration floor at 7.9 to
    10.0 percent against a 10 percent gate: at its own floor, a gate cannot tell a defect
    from the floor, so neither outcome is informative. Criterion 3's PASS band is +/-10
    percent on `fz / (rho*g*V_cap(surface))`, and its denominator is a MEASURED surface,
    so it inherits whatever the surface cannot be located to. That is not a modelling
    choice: in a particle method the free surface is only defined to within the particle
    spacing h, and `measure_surface` itself moved by exactly h/2 on 2026-08-18 when the
    layer-centre convention was replaced by the fill-line convention.

    Sensitivity is exact, not fitted. V_cap(sub) = pi*sub^2*(3R-sub)/3, so
    dV/d(sub) = pi*sub*(2R-sub) = A_w, the waterplane area at that submergence, and

        d(ratio)/d(surface) = -ratio * A_w / V_cap

    Two conventions for the surface-location uncertainty are both defensible, so both are
    reported rather than one being chosen: h/2, the spread between the layer-centre and
    fill-line conventions that this code has actually used, and h, the full layer.
    """
    R = 0.15
    print("Criterion 3 PASS band is +/- 10 percent. FAIL band is beyond 25 percent.")
    print("Floor = the |ratio - 1| forced by not knowing where in the top particle layer")
    print("the free surface is, with a PERFECT coupling and no other error.\n")
    hdr = (f"{'n_grid':>6} {'dx_mm':>7} {'h_mm':>6} {'sub_mm':>7} {'%/mm':>6} "
           f"{'floor_h/2':>10} {'floor_h':>8} {'band/floor_h/2':>15}")
    print(hdr)
    print("-" * len(hdr))
    states = [(n, 1.2 / n, R * 1000.0, "design, half submerged") for n in (64, 96, 128)]
    if recs:
        states += [(d["n_grid"], d["dx"], d["sub"] * 1000.0, d["name"])
                   for d in recs if d["band_mult"] == 1.0]
    for n_grid, dx, sub_mm, tag in states:
        h = dx / 2.0
        sub = sub_mm / 1000.0
        a_w = math.pi * sub * (2.0 * R - sub)
        v = cap_volume(sub, R)
        per_mm = 100.0 * (a_w / v) / 1000.0          # percent of ratio per mm, at ratio 1
        f_half = per_mm * (h / 2.0) * 1000.0
        f_full = per_mm * h * 1000.0
        print(f"{n_grid:6d} {dx*1000:7.2f} {h*1000:6.2f} {sub_mm:7.2f} {per_mm:6.2f} "
              f"{f_half:9.2f}% {f_full:7.2f}% {10.0/f_half:15.2f}   {tag}")
    print("\nA band/floor near 1 is the P-2 pathology: the gate cannot distinguish a defect")
    print("from its own floor. Read the ASYMMETRY, not the ratio alone: a floor of F makes")
    print("a PASS uninformative, but leaves a FAIL informative whenever the excess is")
    print("several times F. Job B's excess is +34.4 to +64.2 percent.")


# ======================================================================================
# RUN: the instrumented scene. Physics unchanged, diagnostics additive.
# ======================================================================================
def _build_instrumented(scene_dir: str):
    sys.path.insert(0, scene_dir)
    import numpy as np
    import sphere_heave as sh

    class InstrumentedTank(sh.SphereTank):
        """SphereTank plus a radial free-surface profile. No physics is changed.

        `measure_surface` returns `super().measure_surface()` verbatim, so every column
        the published grader reads is bit-identical to an uninstrumented run. Everything
        added here is written to NEW keys.
        """

        # PARTICLES PER CELL, at FIXED GRID. `sphere_heave` hardcodes `self.h = self.dx/2`,
        # so PPC is pinned at 8 and cannot be swept from the command line. It is assigned
        # exactly ONCE (sphere_heave.py:491) and read in nine places, so intercepting the
        # assignment with a property reaches all of them consistently: the lattice spacing
        # (:528, :555-557), the seed jitter (:560), the per-particle volume h**3 (:570),
        # the reported h_m (:654) and the +h/2 surface offset (:715).
        #
        # WHY THIS IS THE CONTROL THAT MATTERS. Wallstedt and Guilkey 2007 give the
        # mass-weighted velocity projection a falsifiable signature: for a NON-LINEAR
        # velocity field the projection error does NOT vanish as PPC rises, it plateaus at
        # a level set by the GRID, while the linear-field part converges as PPC^-2 for
        # bilinear and PPC^-3 for GIMP. So sweeping PPC at FIXED dx separates a
        # grid-set plateau from a particle-count-convergent error, and nothing else in
        # this scene does. The divisor is applied as a RATIO to the incoming value so that
        # PPC_DIVISOR = 2.0 reproduces the unmodified path bit-for-bit.
        PPC_DIVISOR = 2.0

        @property
        def h(self):
            return self._h

        @h.setter
        def h(self, value):
            self._h = value * (2.0 / self.PPC_DIVISOR)

        # Exclusion radii to sweep, as multiples of the sphere radius. 2.0 is the value
        # `SphereTank.measure_surface` actually uses; 0.0 keeps everything.
        R_EXCLUDE = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)
        # Radial bins, in multiples of R, for the surface PROFILE. r < 1.0 R is under the
        # body and is not a free surface at all; it is reported so that is visible.
        R_BINS = ((0.0, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 2.5),
                  (2.5, 3.0), (3.0, 4.0), (4.0, 1e9))
        PERCENTILES = (50.0, 90.0, 95.0, 99.0, 99.9)

        def measure_surface(self):
            x = self.solver.x()[: self.n_water]
            cx, cy = self.center_xy
            r = np.hypot(x[:, 0] - cx, x[:, 1] - cy)
            z = x[:, 2]
            d = {}

            # (1) The estimator as written, at a sweep of exclusion radii. Same statistic
            # (99th percentile) and same +h/2 offset, so only the population changes.
            for m in self.R_EXCLUDE:
                sel = z[r > m * self.radius] if m > 0 else z
                d[f"surf_excl_{m:g}R_m"] = (float(np.percentile(sel, 99.0)) + 0.5 * self.h
                                            if sel.size else float("nan"))
                d[f"n_excl_{m:g}R"] = int(sel.size)

            # (2) The DISCARDED annulus on its own. R < r <= 2R: outside the body's own
            # waterplane footprint, inside what the estimator throws away. This is the
            # near-field surface the pre-registered thresholds are about.
            near = (r > self.radius) & (r <= 2.0 * self.radius)
            d["surf_nearfield_m"] = (float(np.percentile(z[near], 99.0)) + 0.5 * self.h
                                     if near.any() else float("nan"))
            d["n_nearfield"] = int(near.sum())

            # (3) Radial profile, so the SHAPE of the deformation is visible and not
            # inferred from two numbers.
            for lo, hi in self.R_BINS:
                sel = z[(r > lo * self.radius) & (r <= hi * self.radius)]
                tag = f"{lo:g}_{hi:g}R" if hi < 1e8 else f"{lo:g}_infR"
                d[f"surf_bin_{tag}_m"] = (float(np.percentile(sel, 99.0)) + 0.5 * self.h
                                          if sel.size else float("nan"))
                d[f"n_bin_{tag}"] = int(sel.size)

            # (4) Percentile sensitivity at the estimator's own exclusion radius. A
            # percentile is a choice; if the answer moves with it, say so.
            far = z[r > 2.0 * self.radius]
            for p in self.PERCENTILES:
                d[f"surf_far_p{p:g}_m"] = (float(np.percentile(far, p)) + 0.5 * self.h
                                           if far.size else float("nan"))
            d["surf_far_max_m"] = float(far.max()) + 0.5 * self.h if far.size else float("nan")

            # (5) Domain-clean variant. About 7.4 percent of the water leaves the domain
            # by frame 299 (job B result 13.6); particles below the floor or outside the
            # wall bands are still in the array and still enter the percentile.
            lo_w, hi_w = self.WALL, self.lim - self.WALL
            inside = ((x[:, 2] >= self.FLOOR) & (x[:, 0] >= lo_w) & (x[:, 0] <= hi_w)
                      & (x[:, 1] >= lo_w) & (x[:, 1] <= hi_w))
            sel = z[inside & (r > 2.0 * self.radius)]
            d["surf_far_domainclean_m"] = (float(np.percentile(sel, 99.0)) + 0.5 * self.h
                                           if sel.size else float("nan"))
            d["n_domainclean"] = int(sel.size)

            # (6) A SECOND, INDEPENDENT ESTIMATOR that does not use a percentile at all.
            # Bin the far field into dx-wide columns, take the highest particle in each,
            # then the median over columns. A percentile of z over the whole cloud depends
            # on how many LAYERS the column has; a per-column maximum does not. Its bias
            # runs the other way: the max of the few particles in a column sits above the
            # layer centre by up to the 0.2h seed jitter, so this reads slightly HIGH
            # where the percentile route reads slightly low.
            m_far = r > 2.0 * self.radius
            if m_far.any():
                xi = np.floor(x[m_far, 0] / self.dx).astype(np.int64)
                yi = np.floor(x[m_far, 1] / self.dx).astype(np.int64)
                key = xi * 100000 + yi
                order = np.argsort(key, kind="stable")
                ks, zs = key[order], z[m_far][order]
                edges = np.flatnonzero(np.diff(ks)) + 1
                tops = np.array([seg.max() for seg in np.split(zs, edges)])
                d["surf_far_colmax_median_m"] = float(np.median(tops)) + 0.5 * self.h
                d["n_columns"] = int(tops.size)
            else:
                d["surf_far_colmax_median_m"] = float("nan")
                d["n_columns"] = 0

            self._diag = d
            # Bit-identical to an uninstrumented run. This is the whole safety argument.
            return super().measure_surface()

        def advance(self):
            rec = super().advance()
            rec.update(self._diag)
            # Ratios against every surface variant, so the decision is read off directly
            # rather than recomputed by hand later.
            zbot = self.z - self.radius
            for k in ("surf_nearfield_m", "surf_excl_0R_m", "surf_far_domainclean_m",
                      "surf_far_colmax_median_m"):
                s = rec.get(k, float("nan"))
                v = cap_volume(s - zbot, self.radius) if s == s else float("nan")
                fb = RHO_W_BENCHMARK * G_ENGINE * v if v == v else float("nan")
                rec["ratio_vs_" + k[:-2]] = (rec["fz_N"] / fb) if fb and fb > 0 else float("nan")
            return rec

    return sh, InstrumentedTank


def run(args) -> None:
    _sh, Tank = _build_instrumented(args.scene_dir)
    # THE FLOOR-ALIGNMENT ARM. `sphere_heave.py` is not edited; `FLOOR` is a CLASS
    # attribute read through `self.FLOOR`, so a subclass override reaches every use of it.
    #
    # WHY THIS EXISTS. Job 918450's "bcfix" turned out to be a one-character fork of the
    # ENGINE, `dotproduct < 0.0` -> `<= 0.0` at mpm_solver_warp.py:1955, which decides
    # whether a grid node lying EXACTLY on a plane collider is constrained. At lim = 1.2
    # the floor at 0.075 m sits exactly on a grid plane at every grid in the sweep
    # (0.075/dx is 3, 4, 6, 8, 12 at g48/64/96/128/192, exact in both f64 and f32), so one
    # whole plane of nodes went unconstrained. Shifting FLOOR by half a cell moves it off
    # the grid with dx, the SDF cache key and everything else held fixed, which is the only
    # way to separate the alignment from the engine change.
    if args.floor_offset_cells:
        Tank.FLOOR = 0.075 + args.floor_offset_cells * (args.lim / args.n_grid)
    Tank.PPC_DIVISOR = float(args.ppc_divisor)
    tank = Tank(n_grid=args.n_grid, lim=args.lim, depth=args.depth,
                h0_over_d=args.h0_over_d, seed=args.seed, device=args.device,
                sdf_res=args.sdf_res, free=False,
                sdf_cache=args.sdf_cache, band_mult=args.band_mult,
                n_ghost_layers=args.ghost_layers)
    cfg = tank.config()
    cfg["mode"] = "fixed"
    cfg["seed"] = args.seed
    cfg["instrumented_by"] = "analysis/r9_jobb_estimator_test.py"
    cfg["no_body_control"] = bool(args.h0_over_d >= 1.0)
    cfg["floor_offset_cells"] = float(args.floor_offset_cells)
    cfg["ppc_divisor"] = float(args.ppc_divisor)
    cfg["particles_per_cell"] = float(args.ppc_divisor) ** 3
    cfg["floor_m_effective"] = float(Tank.FLOOR)
    cfg["prereg_e1_ratio_below"] = PREDICT_E1_RATIO_BELOW
    cfg["prereg_e3_ratio_above"] = PREDICT_E3_RATIO_ABOVE
    print(json.dumps(cfg, indent=2, sort_keys=True), flush=True)

    rows = []
    for i in range(args.frames):
        rec = tank.advance()
        rec["frame"] = i
        rec["t_s"] = (i + 1) * tank.tick
        rows.append(rec)
        if i % max(1, args.frames // 30) == 0:
            print(f"  f{i:4d} Fz={rec['fz_N']:9.4f} far={rec['surface_z_measured_m']:.5f} "
                  f"near={rec['surf_nearfield_m']:.5f} "
                  f"d_mm={(rec['surf_nearfield_m']-rec['surface_z_measured_m'])*1000:+7.2f} "
                  f"ratio_near={rec.get('ratio_vs_surf_nearfield', float('nan')):7.3f}",
                  flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"config": cfg, "rows": rows}, indent=2, sort_keys=True))
    print(f"wrote {out} ({len(rows)} frames)", flush=True)


# ======================================================================================
# SELFTEST: does the instrument recover a surface geometry that was planted on purpose?
# ======================================================================================
def selftest() -> int:
    """Plant a known free surface, elevated only in the annulus, and try to recover it.

    WHY THIS EXISTS. The batch job's smoke run proves the code does not crash. It does not
    prove the numbers mean anything, and this whole unit's conclusion rests on those
    numbers. A synthetic cloud with a KNOWN answer is the only check that can fail for the
    right reason. It needs no GPU and no warpmpm; `SphereTank` is stubbed to its own
    `measure_surface` body, so the subclass under test is the real one.

    IT ALREADY BIT, AND THE BUG WAS IN THE TEST. The first version planted `FLOOR+DEPTH`
    as the far-field answer and reported a 3.26 mm instrument error. The lattice holds an
    INTEGER number of layers of spacing h and 0.5/h is 53.33, so the real fill line is
    FLOOR + 53h = 0.57187, not 0.575. The 3.26 mm was the test's own rounding. Derive the
    planted value from the lattice actually built, never from the nominal depth.

    WHAT IT ESTABLISHES, and both directions matter:
      - on a FLAT planted surface the estimator as written is accurate to 0.14 mm;
      - the percentile+h/2 route and the independent column-max-median route differ by
        1.34 mm at g64, which is 0.071 dx, so the CHOICE OF ESTIMATOR CONVENTION is worth
        about 2 percent of the ratio, not 40. E1 therefore cannot be a convention error;
        it requires a genuine physical near-field elevation, which is what the run tests;
      - the near-minus-far difference reads 1.87 mm HIGH on a planted 28.125 mm rise, 6.7
        percent. The instrument is biased TOWARD supporting E1, so an E1 verdict has to
        clear that bias and is reported with it attached.
    """
    import numpy as np

    class _Stub:
        """SphereTank.measure_surface as written, and nothing else."""
        solver: object
        n_water: int
        center_xy: tuple
        radius: float
        h: float

        def measure_surface(self):
            x = self.solver.x()[: self.n_water]
            cx, cy = self.center_xy
            r = np.hypot(x[:, 0] - cx, x[:, 1] - cy)
            far = r > 2.0 * self.radius
            z = x[far, 2] if far.any() else x[:, 2]
            return float(np.percentile(z, 99.0)) + 0.5 * self.h

    import types
    stub_mod = types.ModuleType("sphere_heave")
    stub_mod.SphereTank = _Stub                                    # type: ignore[attr-defined]
    sys.modules["sphere_heave"] = stub_mod
    _, Tank = _build_instrumented(".")

    R, DX, LIM, FLOOR, DEPTH, N_EXTRA = 0.15, 0.01875, 1.2, 0.075, 0.5, 3
    h = DX / 2.0
    rng = np.random.default_rng(0)
    n_lat, n_z = int(round((LIM - 0.2) / h)), int(round(DEPTH / h))
    far_fill = FLOOR + n_z * h
    near_fill = FLOOR + (n_z + N_EXTRA) * h
    ax = 0.1 + (np.arange(n_lat) + 0.5) * h
    az = FLOOR + (np.arange(n_z) + 0.5) * h
    gx, gy, gz = np.meshgrid(ax, ax, az, indexing="ij")
    w = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
    w += rng.uniform(-0.2 * h, 0.2 * h, size=w.shape)
    cx = cy = 0.5 * LIM
    rad = np.hypot(w[:, 0] - cx, w[:, 1] - cy)
    # Take the annulus slice ONCE, from the base lattice. Recomputing the mask against a
    # `w` that the loop is growing is an index-length bug that numpy catches loudly here
    # and would catch silently if the shapes happened to line up.
    ring = w[(rad > R) & (rad <= 2.0 * R)]
    layers = [w]
    for k in range(N_EXTRA):
        src = ring.copy()
        src[:, 2] = FLOOR + (n_z + k + 0.5) * h + rng.uniform(-0.2 * h, 0.2 * h, size=len(src))
        layers.append(src)
    w = np.concatenate(layers)
    # Carve the body out, so r < R carries no free surface, exactly as the real scene does.
    w = w[~((np.hypot(w[:, 0] - cx, w[:, 1] - cy) <= R) & (w[:, 2] > far_fill - 0.09))]

    t = Tank.__new__(Tank)
    t.solver = types.SimpleNamespace(x=lambda: w.astype(np.float32))  # type: ignore[assignment]
    t.n_water, t.center_xy, t.radius = len(w), (cx, cy), R
    t.h, t.dx, t.lim, t.FLOOR, t.WALL, t.z = h, DX, LIM, FLOOR, 0.1, far_fill

    far_est = t.measure_surface()
    d = t._diag
    print(f"planted far-field fill line   {far_fill:.5f} m  ({n_z} layers of h={h*1000:.4f} mm)")
    print(f"planted annulus fill line     {near_fill:.5f} m  (rise {N_EXTRA*h*1000:.3f} mm)")
    print(f"particles                     {len(w)}\n")
    print(f"estimator as written, excl 2R {far_est:.5f} m   error {(far_est-far_fill)*1000:+.2f} mm")
    print(f"near-field, R < r <= 2R       {d['surf_nearfield_m']:.5f} m   "
          f"error {(d['surf_nearfield_m']-near_fill)*1000:+.2f} mm")
    print(f"near minus far                {(d['surf_nearfield_m']-far_est)*1000:+.2f} mm  "
          f"planted {N_EXTRA*h*1000:.3f} mm")
    print(f"column-max median, independent{d['surf_far_colmax_median_m']:.5f} m   "
          f"error {(d['surf_far_colmax_median_m']-far_fill)*1000:+.2f} mm, "
          f"{d['n_columns']} columns")
    print(f"the two estimators differ by   {(d['surf_far_colmax_median_m']-far_est)*1000:+.2f} mm "
          f"= {(d['surf_far_colmax_median_m']-far_est)/DX:+.3f} dx")
    print("\nexclusion sweep, the step must land exactly at 2R:")
    for m in Tank.R_EXCLUDE:
        print(f"  excl {m:>4}R  {d[f'surf_excl_{m:g}R_m']:.5f} m  n={d[f'n_excl_{m:g}R']:9d}")
    print("radial profile:")
    for lo, hi in Tank.R_BINS:
        tag = f"{lo:g}_{hi:g}R" if hi < 1e8 else f"{lo:g}_infR"
        print(f"  r in {tag:>10s} {d['surf_bin_'+tag+'_m']:.5f} m  n={d['n_bin_'+tag]:9d}")

    ok_far = abs(far_est - far_fill) < 0.002
    ok_rise = abs((d["surf_nearfield_m"] - far_est) - N_EXTRA * h) < 0.003
    print(f"\nflat far-field recovered to < 2 mm   {ok_far}")
    print(f"planted rise recovered to < 3 mm     {ok_rise}")
    return 0 if (ok_far and ok_rise) else 1


# ======================================================================================
# VERDICT: apply the pre-registered thresholds to an instrumented payload
# ======================================================================================
def verdict(paths: list[str], last: int) -> None:
    for p in paths:
        payload = json.loads(Path(p).read_text())
        cfg, rows = payload["config"], payload["rows"][-last:]
        dx = cfg["dx_m"]
        nb = cfg.get("no_body_control", False)
        print(f"\n=== {os.path.basename(p)}  n_grid={cfg['n_grid']} dx={dx*1000:.2f} mm "
              f"band={cfg.get('band_mult',1.0)}x  last {len(rows)} frames"
              f"{'  [NO-BODY CONTROL]' if nb else ''} ===")
        far = st.mean(r["surface_z_measured_m"] for r in rows)
        near = st.mean(r["surf_nearfield_m"] for r in rows)
        print(f"  far-field surface (the estimator as written) {far:.5f} m")
        print(f"  near-field surface (the discarded annulus)   {near:.5f} m")
        print(f"  near minus far                               {(near-far)*1000:+.2f} mm "
              f"= {(near-far)/dx:+.3f} dx")
        if nb:
            design = cfg["surface_z_m"]
            print(f"  design waterline {design:.5f} m, estimator reads {far-design:+.2f} m "
                  f"= {(far-design)*1000:+.2f} mm with NO body in the water")
            print("  any offset here is estimator bias plus real settling, not body effect")
            continue
        print("  radial profile of the free surface, 99th percentile + h/2:")
        for k in sorted(k for k in rows[0] if k.startswith("surf_bin_")):
            tag = k[len("surf_bin_"):-2]
            v = st.mean(r[k] for r in rows if r[k] == r[k])
            n = st.mean(r["n_bin_" + tag] for r in rows)
            print(f"    r in {tag:>10s}  {v:.5f} m  ({v-far:+7.2f} mm vs far)  n={n:9.0f}"
                  .replace(f"{v-far:+7.2f}", f"{(v-far)*1000:+7.2f}"))
        rn = st.mean(r["ratio_vs_surf_nearfield"] for r in rows)
        rf = st.mean(r["fz_over_analytic_measured"] for r in rows)
        print(f"  ratio against the far-field surface  (as published) {rf:7.3f}")
        print(f"  ratio against the near-field surface (the test)     {rn:7.3f}")
        need = SURF_OFFSET_FITTED_DX * dx * 1000
        print(f"  E1 required near-field rise at this dx: {need:.2f} mm; "
              f"measured {(near-far)*1000:+.2f} mm")
        if rn < PREDICT_E1_RATIO_BELOW:
            print(f"  VERDICT E1: the estimator explains the FAIL (ratio < {PREDICT_E1_RATIO_BELOW})")
        elif rn > PREDICT_E3_RATIO_ABOVE:
            print(f"  VERDICT E3: the estimator does NOT explain the FAIL "
                  f"(ratio > {PREDICT_E3_RATIO_ABOVE}); the force is over-predicted")
        else:
            print("  VERDICT INCONCLUSIVE: between the pre-registered thresholds. "
                  "Report as separating nothing.")


def main() -> None:
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("offline", help="model discrimination on existing payloads")
    o.add_argument("dirpath")

    fl = sub.add_parser("floor", help="can criterion 3 produce an informative PASS at all?")
    fl.add_argument("dirpath", nargs="?", default=None)

    r = sub.add_parser("run", help="instrumented fixed-sphere run (needs warpmpm)")
    r.add_argument("--scene-dir", required=True, help="directory holding sphere_heave.py")
    r.add_argument("--n-grid", type=int, default=64)
    r.add_argument("--lim", type=float, default=1.2)
    r.add_argument("--depth", type=float, default=0.5)
    r.add_argument("--h0-over-d", type=float, default=0.0,
                   help="1.0 lifts the sphere clear of the water: the no-body control")
    r.add_argument("--frames", type=int, default=300)
    r.add_argument("--band-mult", type=float, default=1.0)
    r.add_argument("--ghost-layers", type=int, default=0)
    r.add_argument("--sdf-res", type=int, default=96)
    r.add_argument("--sdf-cache", default=None)
    r.add_argument("--ppc-divisor", type=float, default=2.0,
                   help="h = dx / this, so particles per cell = this**3. 2.0 is the "
                        "hardcoded default and reproduces it bit-for-bit; 3.0 gives PPC 27")
    r.add_argument("--floor-offset-cells", type=float, default=0.0,
                   help="shift FLOOR by this many dx. 0.5 moves the floor plane off the "
                        "grid, isolating the exact-node collider bug from the engine fix")
    r.add_argument("--seed", type=int, default=0)
    r.add_argument("--device", default="auto")
    r.add_argument("--out", required=True)

    sub.add_parser("selftest", help="recover a planted surface; needs numpy, no GPU")

    v = sub.add_parser("verdict", help="apply the pre-registered thresholds")
    v.add_argument("paths", nargs="+")
    v.add_argument("--last", type=int, default=50)

    a = p.parse_args()
    if a.cmd == "offline":
        offline(a.dirpath)
    elif a.cmd == "floor":
        floor_report(_load(a.dirpath, verbose=False) if a.dirpath else None)
    elif a.cmd == "selftest":
        raise SystemExit(selftest())
    elif a.cmd == "run":
        run(a)
    else:
        verdict(a.paths, a.last)


if __name__ == "__main__":
    main()
