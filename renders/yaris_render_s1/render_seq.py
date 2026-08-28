from __future__ import annotations

import argparse
import json
from pathlib import Path

import render_realistic as RR


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--stop", type=int, default=90)
    p.add_argument("--stride", type=int, default=1)
    p.add_argument("--half", type=float, default=3.0)
    p.add_argument("--dpi", type=int, default=140)
    p.add_argument("--elev", type=float, default=17.0)
    p.add_argument("--azim", type=float, default=-62.0)
    a = p.parse_args()

    out = Path(a.outdir)
    (out / "_frames").mkdir(parents=True, exist_ok=True)

    rows = []
    for f in range(a.start, a.stop, a.stride):
        dst = out / "_frames" / ("f_%04d.png" % f)
        r = RR.render(a.run, f, out=str(dst), half=a.half, dpi=a.dpi,
                      elev=a.elev, azim=a.azim)
        rows.append({"frame": f, "vol": float(r["vol"]),
                     "v_true": float(r["v_true"]),
                     "err_pct": 100.0 * (r["vol"] - r["v_true"]) / r["v_true"],
                     "watertight": bool(r["watertight"])})
        print("frame %4d  vol %8.4f  err %+6.2f%%  watertight %s"
              % (f, r["vol"], rows[-1]["err_pct"], r["watertight"]), flush=True)

    (out / "volume_audit.json").write_text(json.dumps(rows, indent=2))
    bad = [r for r in rows if not r["watertight"]]
    worst = max(abs(r["err_pct"]) for r in rows)
    print("WROTE %d frames, worst volume error %.2f%%, non-watertight frames %d"
          % (len(rows), worst, len(bad)))


if __name__ == "__main__":
    main()
