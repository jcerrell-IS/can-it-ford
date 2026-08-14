#!/usr/bin/env python3
"""Classify the three-class matched-resolution set.  NON-CANONICAL.

Reads the run directories written by scripts/run_three_class_matched.sh and emits
one CSV row per run, stamped with hull sha256, job id, node, driver sha256, the
ACHIEVED dx and the ACHIEVED realized depth.

It classifies with the SAME simulation/failure_modes.classify_timeseries that
produced the 17 canonical verdicts, and reports margin_frames and k_crit beside
every verdict using the same two functions as
analysis/slide_verdict_fragility.py, imported rather than reimplemented so the
two cannot drift apart.

REALIZED DEPTH IS DERIVED, NOT REQUESTED. summary.json records water_layers and
h, and the water block is arange(floor+0.5h, floor+depth, h), so the realized
depth is water_layers*h. The nominal --depth 0.30 is never the realized value.

TWO ssf VALUES ARE REPORTED PER RUN, deliberately. ssf enters classification at
failure_modes.py:184 ONLY through the TOPPLE branch; it cannot affect SLIDE or
FLOAT. The 17 canonical runs were all classified with compact_sedan's ssf 1.42.
A cross-vehicle set should use each vehicle's own class ssf, so that is the
primary, and the compact_sedan-ssf verdict is carried alongside for continuity.
If the two ever disagree, that disagreement is itself the finding and must not
be silently resolved. peak_surge_accel_g is also reported so any reader can
apply a different ssf without re-running anything.

ssf SOURCE, and its limits. vehicle_params.py carries ssf only in the
params taxonomy (compact_sedan 1.42, midsize_suv 1.04, light_pickup 1.19), NOT
in the AR&R taxonomy the driver registry uses (small_passenger /
large_passenger / large_4wd have stability limits but no ssf). The Silverado is
mapped to light_pickup, the F150-class entry. vehicle_params.py:134 and :150
record that compact_sedan's cg_height and ssf are ESTIMATES, not NHTSA-measured,
and flag "CONFIRM before use". They are used here only as a TOPPLE gate on runs
that are not expected to topple; they are not wired into the solver, and per
CLAUDE.md item 4 they must not be.

Engine: warpmpm. NOT Genesis.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "analysis"))

import failure_modes as FM                                     # noqa: E402
from vehicle_params import get_vehicle                          # noqa: E402
from slide_verdict_fragility import k_crit, longest_joint_run   # noqa: E402

TH = FM.FailureThresholds()

# vehicle key -> (AR&R class used by the driver registry, params class carrying ssf)
CLASS_MAP = {
    "yaris": ("small_passenger", "compact_sedan"),
    "rogue": ("large_passenger", "midsize_suv"),
    "silverado": ("large_4wd", "light_pickup"),
}
CONTINUITY_PARAMS_CLASS = "compact_sedan"   # what all 17 canonical runs used

ARM_MEANING = {
    "S": "shared n_grid=96 (the confound, kept for continuity)",
    "M": "matched dx (PRIMARY)",
    "D": "matched dx, equal bulk density (geometry-vs-mass control)",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_provenance(base: Path):
    """Pull job id, node and driver sha256 out of 00_provenance.txt."""
    out = {"job_id": "", "node": "", "driver_sha256": "", "runner_sha256": ""}
    p = base / "00_provenance.txt"
    if not p.exists():
        return out
    text = p.read_text(errors="replace")
    m = re.search(r"job_id=(\S+)", text)
    if m:
        out["job_id"] = m.group(1)
    m = re.search(r"host=(\S+)", text)
    if m:
        out["node"] = m.group(1)
    m = re.search(r"driver sha256: ([0-9a-f]{64})", text)
    if m:
        out["driver_sha256"] = m.group(1)
    m = re.search(r"runner sha256: ([0-9a-f]{64})", text)
    if m:
        out["runner_sha256"] = m.group(1)
    return out


def classify_one(run_dir: Path, prov: dict):
    label = run_dir.name
    summary = json.loads((run_dir / "summary.json").read_text())
    metrics = run_dir / "metrics.csv"

    arm = label.split("_", 1)[0]
    vkey = summary.get("vehicle_key") or label.split("_")[1]
    arr_class, params_class = CLASS_MAP[vkey]

    mass = float(summary["mass_kg"])
    ssf_own = float(get_vehicle(params_class)["ssf"])
    ssf_cont = float(get_vehicle(CONTINUITY_PARAMS_CLASS)["ssf"])

    res_own = FM.classify_timeseries(str(metrics), mass, ssf_own)
    res_cont = FM.classify_timeseries(str(metrics), mass, ssf_cont)

    d = np.genfromtxt(metrics, delimiter=",", names=True)
    L = longest_joint_run(d["dx"], d["vx"], TH.slide_m, TH.slide_speed_ms)
    k = k_crit(d["dx"], d["vx"], TH.slide_m, TH.slide_speed_ms, TH.sustain_frames)

    S = FM.FailureMode.SLIDE
    h = float(summary["h"])
    layers = int(summary["water_layers"])
    hull_path = summary["hull_source"]
    hull_sha = sha256(hull_path) if Path(hull_path).exists() else "UNREADABLE"

    return {
        "label": label,
        "arm": arm,
        "arm_meaning": ARM_MEANING.get(arm, ""),
        "vehicle": vkey,
        "arr_class": arr_class,
        "params_class": params_class,
        # --- the control variables, ACHIEVED not requested ---
        "n_grid": int(summary["n_grid"]),
        "dx_m": float(summary["dx"]),
        "h_m": h,
        "grid_lim_m": float(summary["grid_lim"]),
        "water_layers": layers,
        "realized_depth_m": layers * h,
        "depth_over_dx": (layers * h) / float(summary["dx"]),
        "nominal_depth_m": float(summary["depth_m"]),
        "velocity_ms": float(summary["velocity_ms"]),
        # --- vehicle ---
        "mass_kg": mass,
        "mass_source": summary.get("mass_source", ""),
        "mass_alt_kg": summary.get("mass_alt_kg"),
        "hull_m3": float(summary["hull_m3"]),
        "solid_volume_m3": float(summary["solid_volume_m3"]),
        "fill_ratio": float(summary["fill_ratio"]),
        "realized_rho": float(summary["realized_rho"]),
        "rho_hull_basis": mass / float(summary["hull_m3"]),
        # --- verdict ---
        "mode": res_own.mode.value,
        "mode_continuity_ssf": res_cont.mode.value,
        "mode_agrees_across_ssf": res_own.mode.value == res_cont.mode.value,
        "ssf_own": ssf_own,
        "ssf_continuity": ssf_cont,
        "peak_surge_accel_g": float(res_own.peak_surge_accel_g),
        "ratio_slide": float(res_own.ratios[S]),
        "longest_joint_frames": L,
        "sustain_frames_required": TH.sustain_frames,
        "margin_frames": L - TH.sustain_frames,
        "k_crit": k,
        "headroom_x": (1.0 / k) if k > 0 else float("inf"),
        # --- containment and provenance ---
        "passthrough_max_frac": float(summary["passthrough_max_frac"]),
        "passthrough_gate_P2_limit": 0.10,
        "passthrough_P2_pass": float(summary["passthrough_max_frac"]) <= 0.10,
        "C2_veh_zmin_rise_m": float(summary["C2_veh_zmin_rise"]),
        "C3_oob_particle_frames": int(summary["C3_oob_particle_frames"]),
        "leaked_particle_frames": int(summary["leaked_particle_frames"]),
        "substeps": int(summary["substeps"]),
        "determinism_identical_FLAG_DO_NOT_TRUST": summary.get("determinism_identical"),
        "hull_source": hull_path,
        "hull_sha256": hull_sha,
        "driver_sha256": prov["driver_sha256"],
        "runner_sha256": prov["runner_sha256"],
        "job_id": prov["job_id"],
        "node": prov["node"],
        "engine": "warpmpm",
        "canonical": "NO",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True, help="three_class_matched_<TAG> directory")
    p.add_argument("--out", required=True, help="output CSV path")
    a = p.parse_args()

    base = Path(a.base)
    prov = parse_provenance(base)
    rows = []
    missing = []
    for run_dir in sorted(base.iterdir()):
        if not run_dir.is_dir():
            continue
        if not (run_dir / "summary.json").exists() or not (run_dir / "metrics.csv").exists():
            missing.append(run_dir.name)
            continue
        rows.append(classify_one(run_dir, prov))

    if not rows:
        raise SystemExit("no completed runs found under %s" % base)

    order = {"S": 0, "M": 1, "D": 2}
    veh = {"yaris": 0, "rogue": 1, "silverado": 2}
    rows.sort(key=lambda r: (order.get(r["arm"], 9), veh.get(r["vehicle"], 9)))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # .gitattributes:4 sets eol=lf, so the writer must not emit CRLF.
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("wrote %s, %d rows" % (out, len(rows)))
    if missing:
        print("INCOMPLETE, no summary.json/metrics.csv: %s" % ", ".join(missing))

    print()
    print("%-32s %6s %11s %13s %8s %7s %8s %8s %9s"
          % ("label", "n_grid", "dx_m", "realized_dep", "mode", "margin", "k_crit",
             "rho_real", "P2_pass"))
    for r in rows:
        print("%-32s %6d %11.7f %13.9f %8s %7d %8.4f %8.2f %9s"
              % (r["label"], r["n_grid"], r["dx_m"], r["realized_depth_m"], r["mode"],
                 r["margin_frames"], r["k_crit"], r["realized_rho"],
                 "yes" if r["passthrough_P2_pass"] else "FAIL"))

    print()
    for arm in ("S", "M", "D"):
        sel = [r for r in rows if r["arm"] == arm]
        if len(sel) < 2:
            continue
        dxs = [r["dx_m"] for r in sel]
        dps = [r["realized_depth_m"] for r in sel]
        print("arm %s (%s): dx spread %.4f%%, realized-depth spread %.4f%%"
              % (arm, ARM_MEANING[arm],
                 100.0 * (max(dxs) - min(dxs)) / min(dxs),
                 100.0 * (max(dps) - min(dps)) / min(dps)))

    # The no-forcing control: D_yaris repeats M_yaris exactly.
    m_y = next((r for r in rows if r["label"].startswith("M_yaris")), None)
    d_y = next((r for r in rows if r["label"].startswith("D_yaris")), None)
    if m_y and d_y:
        print()
        print("DETERMINISM CONTROL, identical config run twice in one job:")
        print("  M_yaris ratio_slide %.6f margin %d k_crit %.6f"
              % (m_y["ratio_slide"], m_y["margin_frames"], m_y["k_crit"]))
        print("  D_yaris ratio_slide %.6f margin %d k_crit %.6f"
              % (d_y["ratio_slide"], d_y["margin_frames"], d_y["k_crit"]))
        drs = abs(m_y["ratio_slide"] - d_y["ratio_slide"])
        rel = 100.0 * drs / max(abs(m_y["ratio_slide"]), 1e-12)
        print("  |d ratio_slide| = %.6e (%.4f%%), margin delta = %d"
              % (drs, rel, d_y["margin_frames"] - m_y["margin_frames"]))
        print("  Any cross-vehicle difference SMALLER than this is not a result.")

    print()
    print("ORDERING, the question this set exists to answer:")
    for arm in ("M", "D"):
        sel = [r for r in rows if r["arm"] == arm]
        if len(sel) < 2:
            continue
        by_vol = sorted(sel, key=lambda r: r["hull_m3"])
        print("  arm %s by displaced volume: %s"
              % (arm, "  ".join("%s(V=%.3f m3, margin=%d, k=%.3f)"
                                % (r["vehicle"], r["hull_m3"], r["margin_frames"], r["k_crit"])
                                for r in by_vol)))
        by_mass = sorted(sel, key=lambda r: r["mass_kg"])
        print("  arm %s by mass            : %s"
              % (arm, "  ".join("%s(m=%.1f kg, margin=%d, k=%.3f)"
                                % (r["vehicle"], r["mass_kg"], r["margin_frames"], r["k_crit"])
                                for r in by_mass)))


if __name__ == "__main__":
    main()
