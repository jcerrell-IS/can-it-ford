#!/usr/bin/env python3
"""Launcher that binds the CANONICAL vehicle module before running sim_enhanced.py.

WHY THIS EXISTS
---------------
The pip-installed warpmpm (pinned via direct_url.json to kks32/mpm-engine
@544c93dd02cb9c7ead89e1155a62967243244fce) is NOT the code that produced the 17 gated
runs. Verified live on the Mac 2026-08-07 against
/Users/josie/.venvs/canitford-mpm/lib/python3.12/site-packages/warpmpm/vehicle.py:
`hasattr(warpmpm.vehicle, "solidify_watertight")` is False, so `sim_enhanced.py`'s
import of it fails against the install. Three independent divergences:

  1. no `solidify_watertight`, so the driver's import line raises ImportError;
  2. `VehicleBody.solidify()` unconditionally calls `solidify_columns`, no watertight
     branch;
  3. `load_vehicle()` dispatches on the ".ply" SUFFIX alone and sends the file to
     `load_gaussians_ply`, so the canonical watertight hull dies with
     `ValueError: no field of name opacity`.

`renders/yaris_render_s1/vehicle_live.py` is the module the runs actually used. It
reproduces the canonical g64_m1100 vehicle cloud exactly: h=0.07360736182599795,
n_particles=8905, solid_volume=3.5513843861695054 m3, fill_ratio=1.0024403113437104,
realized_rho=309.7383668982256, every digit matching data/all_runs_inventory.csv.

It is BOUND here rather than copied, so there is exactly one copy of that module in the
repo and this launcher cannot drift from it.

On Vista the situation differs: $WORK/mpm-engine/src/warpmpm/vehicle.py IS a later
revision that already has solidify_watertight, so the bind is a no-op safety net there
rather than a requirement. Verified 2026-08-07 by importing it on the login node.

THIS DOES NOT MAKE THE SOLVER CANONICAL. Only the vehicle/geometry path is verified.

Usage: same arguments as sim_enhanced.py, forwarded verbatim.
  run_enhanced.py --estimate --grid 96 --bulk-modulus 1.5e7
"""
from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRIVER = HERE / "sim_enhanced.py"
# One copy only. Bound, never duplicated.
VEHICLE_LIVE = HERE.parent / "yaris_render_s1" / "vehicle_live.py"


def bind_canonical_vehicle() -> bool:
    """Bind vehicle_live.py as warpmpm.vehicle. Returns True if a bind happened."""
    import warpmpm  # ensure the parent package is importable first

    try:
        import warpmpm.vehicle as installed
        if hasattr(installed, "solidify_watertight"):
            print("BIND skipped: installed warpmpm.vehicle already has "
                  "solidify_watertight (%s)" % installed.__file__, flush=True)
            return False
    except Exception:
        pass

    if not VEHICLE_LIVE.exists():
        raise SystemExit("missing canonical vehicle module: %s" % VEHICLE_LIVE)

    spec = importlib.util.spec_from_file_location("warpmpm.vehicle", VEHICLE_LIVE)
    if spec is None or spec.loader is None:
        raise SystemExit("could not build a module spec for %s" % VEHICLE_LIVE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["warpmpm.vehicle"] = mod
    spec.loader.exec_module(mod)
    setattr(warpmpm, "vehicle", mod)
    if not hasattr(mod, "solidify_watertight"):
        raise SystemExit("bound vehicle module has no solidify_watertight; wrong file")
    print("BOUND warpmpm.vehicle -> %s" % VEHICLE_LIVE, flush=True)
    return True


def main() -> None:
    # --estimate is pure arithmetic and must not require warp, a GPU, or the mesh.
    if "--estimate" not in sys.argv:
        bind_canonical_vehicle()
    sys.argv[0] = str(DRIVER)
    runpy.run_path(str(DRIVER), run_name="__main__")


if __name__ == "__main__":
    main()
