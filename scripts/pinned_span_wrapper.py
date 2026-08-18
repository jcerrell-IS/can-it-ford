#!/usr/bin/env python3
"""
pinned_span_wrapper.py  --  run sim_standing.py with the water interior span
PINNED IN METRES across an n_grid ladder, without editing the driver.

WHY THIS EXISTS
sim_standing.py sets the domain from the hull alone:
    lim   = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)     (as_ran :82 / canonical :160)
    floor = 3.0*dx                                     (as_ran :86 / canonical :164)
    wall  = 4.0*dx                                     (as_ran :100 / canonical :178)
lim does NOT depend on n_grid but wall does, so the water interior span is
lim - 8*dx and it GROWS as the grid refines. Measured across the R6 ladder
(jobs 918247-918250, mass 2337, depth 0.30, v 1.5, 90 frames):
    n=48  span 7.851452 m
    n=128 span 8.832883 m      +12.50 percent
    plan area 61.645 -> 78.020 m2   +26.56 percent
So that ladder is four different tanks, not four resolutions of one tank, and any
trend across it confounds resolution with domain size.

WHAT IT DOES
Pins the span to S metres by choosing lim per grid:
    span = lim*(1 - 8/n) = S   =>   lim_n = S*n/(n - 8)
and reaches lim_n by PRESENTING A DIFFERENT extent[1] to the driver, since with
this hull the 2.2*ext[1] term is the binding one (2.2*4.282610 = 9.421742, which
is exactly the observed grid_lim). ext[1] is monkeypatched onto the vehicle object
inside canonicalize(), which is the single point every downstream consumer reads:
h_probe, lim1/lim2 determinism, the scene's own lim, and the extent written to the
rollout. The override therefore propagates consistently by construction.

THE HULL IS NOT RESCALED. Only the advertised extent[1] changes. Particles, mesh,
SDF, mass and spacing are the real hull, so the blockage ratio is held fixed too.
Verify in the output: solid_volume_m3 and hull_m3 must match the unpinned runs.

WHAT IT DOES NOT DO
It does not pin the realized water depth. depth is quantized to L*h with
L = ceil(depth/h - 0.5), so pinning the span makes the realized depth vary unless
40 divides (n - 8). See --require-exact-depth, which refuses any grid that would
move the depth. The unpinned R6 ladder happens to hold realized depth EXACTLY
constant at 0.2944294 m (= lim/32) at n = 48/64/96/128, so that control must not
be given up silently in exchange for the span control.

The driver is imported and its main() called; the file itself is never modified.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, sys
from pathlib import Path

import numpy as np

TARGET_DEPTH = 0.2944294473039918   # realized depth of every unpinned R6 rung


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_driver(path):
    spec = importlib.util.spec_from_file_location("sim_standing_pinned", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sim_standing_pinned"] = mod
    spec.loader.exec_module(mod)
    for need in ("canonicalize", "main", "StandingFloodScene"):
        if not hasattr(mod, need):
            raise SystemExit("driver %s lacks %s" % (path, need))
    return mod


def predict(n, lim, depth):
    dx = lim / n; h = dx / 2.0; floor = 3.0 * dx; wall = 4.0 * dx
    xs = np.arange(wall + 0.5 * h, lim - wall - 0.5 * h, h)
    zs = np.arange(floor + 0.5 * h, floor + depth, h)
    return dict(dx=dx, h=h, span=lim - 8.0 * dx, n_cols=len(xs),
                layers=len(zs), realized_depth=len(zs) * h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--driver", required=True)
    ap.add_argument("--span", type=float, required=True, help="interior span S in metres")
    ap.add_argument("--grid", type=int, required=True)
    ap.add_argument("--depth", type=float, default=0.30)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--require-exact-depth", action="store_true",
                    help="abort unless realized depth equals the unpinned ladder's 0.2944294 m")
    ap.add_argument("--provenance", default=None, help="path for the sidecar provenance json")
    args, passthrough = ap.parse_known_args()

    n = args.grid
    if n <= 8:
        raise SystemExit("n_grid must exceed 8; span = lim*(1 - 8/n)")
    lim_target = args.span * n / (n - 8.0)
    ext_y = lim_target / 2.2

    pre = predict(n, lim_target, args.depth)
    dev = pre["realized_depth"] - TARGET_DEPTH
    print("PINNED_SPAN n_grid=%d S=%.9f -> lim=%.9f ext_y_presented=%.9f" %
          (n, args.span, lim_target, ext_y), flush=True)
    print("PINNED_SPAN predicted dx=%.9f h=%.9f span=%.9f layers=%d realized_depth=%.9f (%+.3f%% vs unpinned %.9f)" %
          (pre["dx"], pre["h"], pre["span"], pre["layers"], pre["realized_depth"],
           100.0 * dev / TARGET_DEPTH, TARGET_DEPTH), flush=True)
    if args.require_exact_depth and abs(dev) > 1e-9:
        raise SystemExit(
            "REFUSED: at n_grid=%d the pinned span moves the realized water depth to "
            "%.9f m, %+.3f%% off the unpinned ladder's %.9f m. Pinning the span here "
            "would trade the domain confound for a depth confound. Exact pinning of "
            "both needs 40 | (n - 8); nearest valid grids are %s."
            % (n, pre["realized_depth"], 100.0 * dev / TARGET_DEPTH, TARGET_DEPTH,
               [8 + 40 * k for k in range(1, 7)]))

    mod = load_driver(args.driver)
    orig = mod.canonicalize
    seen = {}

    def patched(v):
        v = orig(v)
        true_ext = np.asarray(v.extent, dtype=float).copy()
        e = np.asarray(v.extent, dtype=float).copy()
        e[1] = ext_y
        if not (2.2 * e[1] > 3.5 * e[0] and 2.2 * e[1] > 6.0 * args.depth):
            raise SystemExit("REFUSED: 2.2*ext[1] is no longer the binding term "
                             "(2.2*%.6f vs 3.5*%.6f, 6*%.6f)" % (e[1], e[0], args.depth))
        v.extent = e
        seen["true_extent"] = true_ext.tolist()
        seen["presented_extent"] = e.tolist()
        return v

    mod.canonicalize = patched

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    prov = args.provenance or str(out / "pinned_span_provenance.json")
    Path(prov).write_text(json.dumps({
        "wrapper": str(Path(__file__).resolve()),
        "wrapper_sha256": sha256(__file__),
        "driver": str(args.driver),
        "driver_sha256": sha256(args.driver),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "n_grid": n, "span_target_m": args.span, "lim_target_m": lim_target,
        "ext_y_presented_m": ext_y, "depth_arg_m": args.depth,
        "predicted": pre, "unpinned_target_depth_m": TARGET_DEPTH,
        "realized_depth_dev_pct": 100.0 * dev / TARGET_DEPTH,
        "hull_is_rescaled": False,
    }, indent=2))
    print("PINNED_SPAN provenance -> %s" % prov, flush=True)

    sys.argv = [args.driver, "--label", args.label, "--out", str(out),
                "--depth", str(args.depth), "--grid", str(n)] + passthrough
    print("PINNED_SPAN argv %s" % " ".join(sys.argv[1:]), flush=True)
    mod.main()
    print("PINNED_SPAN extents true=%s presented=%s" %
          (seen.get("true_extent"), seen.get("presented_extent")), flush=True)


if __name__ == "__main__":
    main()
