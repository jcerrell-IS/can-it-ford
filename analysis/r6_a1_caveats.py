#!/usr/bin/env python3
"""Re-derive A1's caveats from job 917797's own data, rather than repeating them.

The Round-6 handoff lists a set of caveats that "must travel with" A1. None of them had
been re-derived from the data. On this project the base rate for an unverified row is
roughly one in four, so they are checked here rather than carried forward.

All of them reproduce. One needs its statistic named: the handoff's "-0.1617 m/s" is the
mean over the NEGATIVE subset of conjunction frames, not over all of them. The mean over
all of them is +0.0156 m/s, which tells a different and more damaging story. See the vx
breakdown this prints.

Usage:
    /opt/homebrew/bin/uv run --with numpy python3 analysis/r6_a1_caveats.py \\
        --jobA <extracted d4_jobA dir>

Needs numpy; no system python on the Mac has it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

MASS_KG = 1100.0   # A1 swept friction on sweepV_g64_v0p5's arguments
SSF = 1.42         # vehicle_params compact_sedan, an ESTIMATE flagged "CONFIRM before use"
ARMS = (
    ("0.55", "canonical friction, the control. MUST reproduce STUCK or A1 is void"),
    ("0.30", "logged INDETERMINATE IN ADVANCE: the bracket (0.369, 0.739] straddles 0.5 m/s"),
    ("0.0250", "22x below canonical. Any flip here is SUB-PHYSICAL and must be said so"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobA", type=Path, required=True,
                    help="extracted d4_jobA directory, with brake_mu0.55/ etc")
    args = ap.parse_args()

    sys.path.insert(0, str(REPO / "simulation"))
    import numpy as np
    import failure_modes as FM

    th = FM.FailureThresholds()
    print(f"A1 brake sweep. mass {MASS_KG} kg, ssf {SSF}, classifier G {FM.G}")
    print("=" * 78)

    for mu, note in ARMS:
        p = args.jobA / f"brake_mu{mu}" / "metrics.csv"
        if not p.is_file():
            print(f"\nmu = {mu}: MISSING at {p}")
            continue
        res = FM.classify_timeseries(str(p), MASS_KG, SSF)
        kin = FM.kinematics_from_columns(FM.load_timeseries(str(p)), MASS_KG)
        vx = kin.vel[:, FM.SURGE_AXIS]
        drift = np.abs(kin.disp[:, FM.SURGE_AXIS])
        joint = (drift >= th.slide_m) & (np.abs(vx) >= th.slide_speed_ms)
        idx = FM._first_sustained_index(joint, th.sustain_frames)
        accel_g = np.abs(kin.accel[:, FM.SURGE_AXIS]) / FM.G

        print(f"\nmu = {mu}   {note}")
        print(f"  verdict                       {res.mode.value}")
        print(f"  first sustained SLIDE frame   {idx}")
        print(f"  joint frames                  {int(joint.sum())} of {len(joint)}")

        # The frame-0 one-sided-gradient artifact. It is IN THE PUBLISHED RECORD, so the
        # point is not that 0.682 g is wrong, it is that it is not a load.
        print(f"  peak_surge_accel_g from the classifier   {res.peak_surge_accel_g:.4f} g")
        for lbl, arr, off in (("incl frame 0", accel_g, 0),
                              ("excl frame 0", accel_g[1:], 1),
                              ("from frame 20", accel_g[20:], 20)):
            v = arr.max()
            print(f"    {lbl:14s} {v:.4f} g at frame {int(arr.argmax()) + off:3d}"
                  f"   margin to ssf {SSF}: {SSF / v:8.2f}x")

        # failure_modes.py:170 takes abs(vx). Name the support set of every mean, because
        # "mean -0.1617 m/s" is ambiguous between two different statistics.
        if joint.any():
            vj = vx[joint]
            neg, pos = vj[vj < 0], vj[vj >= 0]
            print(f"  CONJUNCTION FRAMES {len(vj)}, vx<0 in {len(neg)} "
                  f"({len(neg) / len(vj) * 100:.1f} %)")
            print(f"    mean vx over ALL conjunction frames  {vj.mean():+.4f} m/s")
            if len(neg):
                print(f"    mean vx over the NEGATIVE subset     {neg.mean():+.4f} m/s"
                      f"   <- {len(neg)} frames")
            if len(pos):
                print(f"    mean vx over the POSITIVE subset     {pos.mean():+.4f} m/s"
                      f"   <- {len(pos)} frames")
            print(f"    mean |vx| over all conjunction       {np.abs(vj).mean():+.4f} m/s")
            print(f"    min  vx over all conjunction         {vj.min():+.4f} m/s")
            if len(neg) and len(pos):
                print("    READ THIS AS OSCILLATION, NOT DRIFT: a near-zero mean over all")
                print("    conjunction frames with large means of both signs is a vehicle")
                print("    going nowhere, which abs() at failure_modes.py:170 scores as SLIDE.")
        else:
            print("  no conjunction frames, consistent with STUCK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
