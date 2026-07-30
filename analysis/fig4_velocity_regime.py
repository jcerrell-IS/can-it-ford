"""
fig4_velocity_regime.py

Surge-velocity sweep: displacement and failure-mode regime for the coupled L2 MPM
runs, against the AR&R small-passenger hazard cap.

PROVENANCE
  Source data   renders/yaris_render_s1/_incoming/sweepV_g64_v{0p5,1p0,2p0,2p5,3p0}/
                renders/yaris_render_s1/g64_m1100/                (the v=1.5 point)
                Each supplies summary.json (scalars) and metrics.csv (time series).
  Solver        kks32/mpm-engine, vendored at third_party/mpm-engine-544c93dd,
                pinned SHA 544c93dd02cb9c7ead89e1155a62967243244fce, MIT.
                Driver renders/yaris_render_s1/sim_standing.py, which imports
                warpmpm.core.solver, warpmpm.materials.newtonian, warpmpm.vehicle.
  Scene         standing_water_sustained_inflow, n_grid 64, h = 0.0736 m,
                4 water layers, realized depth 0.2944 m (NOT the nominal 0.30 m).
  Vehicle       yaris_coarse_v1l_watertight.ply, 1100 kg, single hull, MASH 1100C.
  Classifier    simulation/failure_modes.py, thresholds slide_m = 0.05,
                slide_speed_ms = 0.05, float_m = 0.05, float_speed_ms = 0.02,
                sustain_frames = 3.
  AR&R cap      0.30 m2/s, small passenger, Shand, Cox, Blacka & Smith 2011,
                AR&R Revision Project 10 Stage 2, Report P10/S2/020,
                ISBN 978-0-85825-948-5, Table 3 (DRAFT INTERIM, stationary vehicles).

CAVEAT LABELS
  slide_m = 0.05 m is an INTERNAL NUMERICAL ONSET DETECTOR. It is NOT attributable
  to Smith, Modra & Felder 2019 or to any peer-reviewed drift criterion. See
  docs/VERIFIED_FACTS_LEDGER_july24.md Section B.
  ssf = 1.42 is an ESTIMATE flagged "CONFIRM before use" at vehicle_params.py:108.
  Every TOPPLE ratio scales as 1/ssf. The SLIDE and STUCK verdicts do not depend on it.

Usage
  /opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python \
      analysis/fig4_velocity_regime.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
RENDERS = REPO / "renders" / "yaris_render_s1"
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))
import failure_modes as FM  # noqa: E402

SSF = 1.42          # vehicle_params.py:108, ESTIMATE, flagged CONFIRM before use
ARR_DV_CAP = 0.30   # m2/s, small passenger, Shand et al. 2011 Table 3
DRIFT_M = 0.05      # internal numerical onset detector, NOT a cited physical threshold

RUNS = [
    (RENDERS / "_incoming" / "sweepV_g64_v0p5", 0.5),
    (RENDERS / "_incoming" / "sweepV_g64_v1p0", 1.0),
    (RENDERS / "g64_m1100", 1.5),
    (RENDERS / "_incoming" / "sweepV_g64_v2p0", 2.0),
    (RENDERS / "_incoming" / "sweepV_g64_v2p5", 2.5),
    (RENDERS / "_incoming" / "sweepV_g64_v3p0", 3.0),
]

MODE_COLOR = {"STUCK": "#1B7F4B", "SLIDE": "#B03A2E",
              "TOPPLE": "#6C3483", "FLOAT": "#1F6FB2"}


def collect():
    out = []
    for d, v_expect in RUNS:
        summ = json.loads((d / "summary.json").read_text())
        assert abs(float(summ["velocity_ms"]) - v_expect) < 1e-9, \
            f"{d.name}: summary says v={summ['velocity_ms']}, expected {v_expect}"
        res = FM.classify_timeseries(str(d / "metrics.csv"),
                                     float(summ["mass_kg"]), SSF)
        rd = res.__dict__
        mode = getattr(rd.get("mode"), "name", str(rd.get("mode")))
        ratios = {getattr(k, "name", k): float(v)
                  for k, v in rd.get("ratios", {}).items()}
        layers = int(summ["water_layers"])
        depth = layers * float(summ["h_m"] if "h_m" in summ else summ["h"])
        out.append(dict(
            run=d.name, v=float(summ["velocity_ms"]), mode=mode, ratios=ratios,
            disp=float(summ["final_disp_mag_m"]),
            passthru=float(summ["passthrough_max_frac"]),
            depth=depth, dv=depth * float(summ["velocity_ms"]),
            n_grid=int(summ["n_grid"]), layers=layers,
        ))
    return out


def main():
    rows = collect()
    depth = rows[0]["depth"]
    assert all(abs(r["depth"] - depth) < 1e-9 for r in rows), "depth not fixed across sweep"

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 5.4), facecolor="white",
                                   gridspec_kw={"width_ratios": [1.32, 1.0]})
    fig.suptitle("Surge velocity controls both how far the vehicle moves and how it fails",
                 fontsize=15, fontweight="bold", y=0.98)

    v = np.array([r["v"] for r in rows])
    d = np.array([r["disp"] for r in rows])

    axL.plot(v, d, "-", color="#444444", linewidth=1.6, zorder=2)
    for r in rows:
        axL.plot(r["v"], r["disp"], "o", markersize=13, zorder=4,
                 color=MODE_COLOR[r["mode"]], markeredgecolor="white", markeredgewidth=1.4)
        axL.annotate(f"{r['disp']:.3f}", (r["v"], r["disp"]), textcoords="offset points",
                     xytext=(0, 13), ha="center", fontsize=9, color="#333333")

    axL.axhline(DRIFT_M, color="#888888", linestyle=":", linewidth=1.8, zorder=1)
    axL.text(1.14, 0.072, f"onset detector {DRIFT_M} m",
             va="bottom", ha="left", fontsize=8, color="#666666")

    v_cap = ARR_DV_CAP / depth
    axL.axvline(v_cap, color="#0E6655", linestyle="--", linewidth=2.2, zorder=3)
    axL.text(v_cap + 0.07, 1.30, f"AR&R small-passenger cap\nD x V = {ARR_DV_CAP} m$^2$/s\n"
                                 f"reached at {v_cap:.2f} m/s",
             fontsize=9, color="#0E6655", va="top", ha="left")

    axL.set_xlabel("surge velocity (m/s)", fontsize=11.5)
    axL.set_ylabel("final displacement magnitude (m)", fontsize=11.5)
    axL.set_title(f"L2 coupled MPM, realized depth {depth:.4f} m "
                  f"({rows[0]['layers']} layers x h), n_grid {rows[0]['n_grid']}, 1100 kg",
                  fontsize=10.5)
    axL.set_ylim(-0.06, 1.55)
    axL.set_xlim(0.28, 3.22)
    axL.grid(alpha=0.25)

    seen = []
    for m in ("STUCK", "SLIDE"):
        if any(r["mode"] == m for r in rows):
            seen.append(plt.Line2D([], [], marker="o", linestyle="", markersize=11,
                                   color=MODE_COLOR[m], label=f"classifier verdict: {m}"))
    axL.legend(handles=seen, loc="lower right", fontsize=9.5, framealpha=0.95)

    width = 0.26
    idx = np.arange(len(rows))
    for k, key in enumerate(("SLIDE", "TOPPLE", "FLOAT")):
        vals = [r["ratios"].get(key, 0.0) for r in rows]
        axR.bar(idx + (k - 1) * width, vals, width, label=key,
                color=MODE_COLOR[key], alpha=0.88)
    axR.axhline(1.0, color="black", linestyle="--", linewidth=1.8)
    axR.text(-0.42, 1.12, "criterion met", fontsize=9, ha="left", color="#111111")
    axR.set_yscale("log")
    axR.set_xticks(idx)
    axR.set_xticklabels([f"{r['v']:g}" for r in rows])
    axR.set_xlabel("surge velocity (m/s)", fontsize=11.5)
    axR.set_ylabel("criterion ratio (log scale, 1.0 = met)", fontsize=11.5)
    axR.set_title("Sliding dominates. Toppling is exceeded transiently\n"
                  "from 1.5 m/s but never sustained for 3 frames.", fontsize=10.5)
    axR.legend(fontsize=9.5, loc="upper left")
    axR.grid(alpha=0.25, axis="y")

    fig.text(0.5, 0.005,
             "Solver kks32/mpm-engine @544c93dd (MIT). One hull, yaris_coarse_v1l_watertight.ply, "
             f"1100 kg (MASH 1100C). Water passthrough {min(r['passthru'] for r in rows):.1%} to "
             f"{max(r['passthru'] for r in rows):.1%} of particles. SSF 1.42 is an estimate; "
             "TOPPLE ratios scale as 1/SSF. The 0.05 m onset detector is internal to this work, "
             "not a cited physical threshold.",
             ha="center", fontsize=8, color="#555555")

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    outdir = REPO / "figures"
    outdir.mkdir(exist_ok=True)
    for ext, kw in (("pdf", {}), ("png", {"dpi": 200})):
        p = outdir / f"fig4_velocity_regime.{ext}"
        fig.savefig(p, format=ext, bbox_inches="tight", facecolor="white", **kw)
        print("wrote", p)

    print()
    print("%-18s %5s %8s %9s %9s %9s %-7s" %
          ("run", "v", "disp_m", "r_SLIDE", "r_TOPPLE", "r_FLOAT", "verdict"))
    for r in rows:
        print("%-18s %5.1f %8.4f %9.2f %9.4f %9.2f %-7s" %
              (r["run"], r["v"], r["disp"], r["ratios"].get("SLIDE", 0),
               r["ratios"].get("TOPPLE", 0), r["ratios"].get("FLOAT", 0), r["mode"]))
    print(f"\nrealized depth {depth:.6f} m, AR&R cap {ARR_DV_CAP} m2/s reached at "
          f"v = {v_cap:.4f} m/s")


if __name__ == "__main__":
    main()
