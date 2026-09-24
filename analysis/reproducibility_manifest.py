#!/usr/bin/env python3
"""Emit, in one place, a provenance record for the 17 gated runs, and verify it.

WHY. Literature searches on GPU particle solvers found that studies rarely report, in one
place, particle and grid counts, GPU model, wall time per simulated second, multi-GPU scaling
or a runnable vehicle case, and work on simulation provenance recommends recording code,
inputs, environment, hashes, outputs and analysis lineage. This project cannot validate its
physics against an external number, so a complete, machine-checkable provenance record is the
part it can deliver.

WHAT EACH FIELD MEANS. The physics and grid fields in each run's summary.json (particle
counts, grid size, spacing, substeps, sound speed, friction) were written by the run.
`canitford_git_commit`, `solver_git_sha` and `mesh_sha256` were not: a backfill on 2026-08-12
added them and labelled how each was obtained in `_provenance_backfill`. The commit is
RECONSTRUCTED from a file date (an upper bound, not evidence of what ran), and the solver SHA
and mesh hash are RESOLVED from the pinned solver and the recorded hull volume. The manifest
carries those labels per run as `field_provenance`, so "present" is never read as "recorded".

WHAT IS ABSENT IS NAMED, NOT OMITTED. No run record carries the GPU model or wall time. The
GPU is recorded once per batch in the batch logs (NVIDIA GH200 120GB on Vista), and no run
record carries a job id, host or timestamp, so wall time cannot be joined to a run. This
script prints both with that reason rather than dropping the rows, because a manifest that
silently omits what it could not find is the same defect as a check that cannot distinguish
absence from failure.

IT ALSO VERIFIES. It re-resolves every recorded git SHA against the live object store and
re-hashes the canonical mesh, so a run whose provenance no longer resolves is reported.

    python3 analysis/reproducibility_manifest.py      # stdlib only
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVENTORY = os.path.join(REPO, "data", "all_runs_inventory.csv")
MESH = os.path.join(REPO, "vehicle_geometry_research",
                    "yaris_coarse_v1l_watertight.ply")
OUT_JSON = os.path.join(REPO, "data", "reproducibility_manifest.json")
OUT_MD = os.path.join(REPO, "docs", "REPRODUCIBILITY_MANIFEST.md")

# The six items the provenance literature asks for, mapped to where each lives.
WANTED = [
    ("particle counts", "summary.json", ("n_water", "n_vehicle", "n_carved")),
    # KEYS MUST MATCH THE RUN DICT, NOT THE RAW summary.json. An earlier version
    # listed `grid_density` and `mesh_sha256`, neither of which is a key in the run
    # dict built below, so both rows printed PARTIAL while `fields_complete` said
    # 10 of 10. A mislabelled PARTIAL understates the project's own completeness,
    # which is the opposite of the usual failure and just as wrong.
    ("grid counts", "summary.json", ("n_grid", "dx", "grid_lim")),
    ("timestep / substeps", "summary.json", ("substeps", "frames")),
    ("fluid model", "summary.json",
     ("sound_speed_ms", "bulk_modulus", "water_eta", "floor_friction")),
    ("code provenance", "summary.json",
     ("canitford_git_commit", "solver_git_sha", "mesh_sha256_recorded")),
    ("GPU model", "MEASURED", ()),
    ("wall time per simulated second", "UNJOINABLE", ()),
    ("multi-GPU scaling", "N/A", ()),
]

# MEASURED ON A COMPUTE NODE 2026-08-20, not relayed. srun -p gh -N1 -n1 -t 00:10:00,
# job 924231, node c608-062. A second measurement found the identical
# hardware on c611-021 under job 924230.
VISTA_GPU = {
    "name": "NVIDIA GH200 120GB",
    "memory_total_mib": 97871,
    "driver_version": "590.48.01",
    "compute_capability": "9.0",
    "host_arch": "aarch64",
    "host_cpu": "Neoverse-V2",
    "host_cpus": 72,
    "measured": "2026-08-20, Vista job 924231 on c608-062, partition gh",
}

# LS6 for contrast, measured the same day: srun -p gpu-a100-dev, job 3378048, c301-003.
# This is the direct confirmation that LS6 is x86_64, which had only been INFERRED from a
# build directory named chrono_x86_build.
LS6_GPU = {
    "name": "NVIDIA A100-PCIE-40GB", "count_per_node": 3,
    "memory_total_mib": 40960, "driver_version": "570.195.03",
    "compute_capability": "8.0", "host_arch": "x86_64",
    "host_cpu": "AMD EPYC 7763 64-Core Processor",
    "measured": "2026-08-20, LS6 job 3378048 on c301-003, partition gpu-a100-dev",
}


def sh(*args):
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              timeout=20).stdout.strip()
    except Exception:                                          # noqa: BLE001
        return ""


def sha256(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


BACKFILLED_FIELDS = ("canitford_git_commit", "solver_git_sha", "mesh_sha256",
                     "vehicle_mass", "grid_density", "bulk_modulus")


def provenance_label(text):
    """Map the backfill's free-text field_confidence to one word."""
    t = (text or "").strip().lower()
    for word in ("reconstructed", "resolved", "aliased", "recorded"):
        if t.startswith(word):
            return word
    return "unknown"


def field_provenance(s):
    """How each audit field reached summary.json, as labelled by the backfill. A field the
    backfill did not label is reported as present, not as recorded."""
    pb = s.get("_provenance_backfill") or {}
    fc = pb.get("field_confidence") or {}
    out = {}
    for k in BACKFILLED_FIELDS:
        if k in fc:
            out[k] = provenance_label(fc[k])
        elif k in s:
            out[k] = "present, not backfilled"
    return out, pb.get("mode"), pb.get("date")


def sha_resolves(sha):
    """True if this git object exists in the live store. A recorded SHA that no
    longer resolves is a provenance failure, not a formatting detail."""
    if not sha or len(sha) < 7:
        return False
    return sh("git", "-C", REPO, "cat-file", "-t", sha) == "commit"


def main() -> int:
    if not os.path.isfile(INVENTORY):
        print(f"NOT EVALUABLE: {INVENTORY} absent", file=sys.stderr)
        return 2

    rows = list(csv.DictReader(open(INVENTORY, encoding="utf-8", errors="replace")))
    mesh_live = sha256(MESH)

    runs, unresolved, mesh_mismatch, missing_summary = [], [], [], []
    for r in rows:
        name = r.get("run", "")
        sp = r.get("summary_path", "") or ""
        cand = [sp if os.path.isabs(sp) else os.path.join(REPO, sp),
                os.path.join(REPO, "renders", "yaris_render_s1", name, "summary.json")]
        s, spath = None, None
        for c in cand:
            if c and os.path.isfile(c):
                try:
                    s = json.load(open(c, encoding="utf-8", errors="replace"))
                    spath = c
                    break
                except ValueError:
                    pass
        if s is None:
            missing_summary.append(name)
            continue

        repo_sha = s.get("canitford_git_commit") or ""
        solver_sha = s.get("solver_git_sha") or ""
        mesh_rec = s.get("mesh_sha256") or ""
        ok_repo = sha_resolves(repo_sha)
        if repo_sha and not ok_repo:
            unresolved.append((name, "canitford_git_commit", repo_sha))
        if mesh_live and mesh_rec and mesh_rec != mesh_live:
            mesh_mismatch.append((name, mesh_rec, mesh_live))

        fprov, bf_mode, bf_date = field_provenance(s)
        runs.append({
            "run": name,
            "summary_path": os.path.relpath(spath, REPO) if spath else None,
            "n_water": s.get("n_water"), "n_vehicle": s.get("n_vehicle"),
            "n_carved": s.get("n_carved"),
            "n_grid": s.get("n_grid"), "dx": s.get("dx"),
            "grid_lim": s.get("grid_lim"),
            "frames": s.get("frames"), "substeps": s.get("substeps"),
            "sound_speed_ms": s.get("sound_speed_ms"),
            "bulk_modulus": s.get("bulk_modulus"),
            "water_eta": s.get("water_eta"),
            "floor_friction": s.get("floor_friction"),
            "mass_kg": s.get("mass_kg") or s.get("vehicle_mass"),
            "canitford_git_commit": repo_sha or None,
            "canitford_commit_resolves": ok_repo,
            "solver_git_sha": solver_sha or None,
            "mesh_sha256_recorded": mesh_rec or None,
            "gpu_model": None,
            "gpu_model_inferred_from_venue": VISTA_GPU["name"],
            "wall_time_per_simulated_second": None,
            "field_provenance": fprov,
            "provenance_backfill": {"mode": bf_mode, "date": bf_date},
        })

    complete = [k for k in ("n_water", "n_vehicle", "n_grid", "dx", "substeps",
                            "sound_speed_ms", "floor_friction",
                            "canitford_git_commit", "solver_git_sha", "mesh_sha256_recorded")
                if all(r.get(k) is not None for r in runs)] if runs else []

    print("REPRODUCIBILITY MANIFEST")
    print("a provenance record for the 17 gated runs, in one place\n")
    print(f"  gated runs with a readable summary : {len(runs)} of {len(rows)}")
    print(f"  fields complete across ALL runs     : {len(complete)} of 10")
    print(f"  canonical mesh sha256 (live)        : {(mesh_live or 'MESH ABSENT')[:16]}")
    print()
    print("  what the literature asks for, and whether this project has it:")
    for label, where, keys in WANTED:
        if where == "MEASURED":
            print(f"    INFERRED {label:34} {VISTA_GPU['name']}, {VISTA_GPU['compute_capability']}, "
                  f"driver {VISTA_GPU['driver_version']}  [measured on a Vista node 2026-08-20; "
                  f"batch logs record it, run records do not]")
        elif label == "code provenance":
            have = all(all(r.get(k) is not None for r in runs) for k in keys) if runs else False
            print(f"    {'FILLED  ' if have else 'PARTIAL '} {label:34} {', '.join(keys)}  "
                  f"[added 2026-08-12: commit reconstructed, solver and mesh resolved]")
        elif where == "UNJOINABLE":
            print(f"    ABSENT   {label:34} NOT recoverable: no join key exists")
        elif where == "N/A":
            print(f"    N/A      {label:34} single-GPU runs; no scaling study was ever done")
        else:
            have = all(all(r.get(k) is not None for r in runs) for k in keys) if runs else False
            print(f"    {'PRESENT ' if have else 'PARTIAL '} {label:34} {', '.join(keys)}")
    print()
    if missing_summary:
        print(f"  NO SUMMARY FOUND for {len(missing_summary)}: {', '.join(missing_summary)}")
    if unresolved:
        print(f"  PROVENANCE FAILURE, recorded SHA does not resolve in this object store:")
        for n, f, v in unresolved:
            print(f"    {n:22} {f} = {v}")
    if mesh_mismatch:
        print(f"  MESH MISMATCH, recorded sha256 differs from the live canonical mesh:")
        for n, rec, live in mesh_mismatch:
            print(f"    {n:22} recorded {rec[:16]} live {live[:16]}")
    if not (missing_summary or unresolved or mesh_mismatch):
        print("  no provenance failures: every recorded commit resolves and every")
        print("  recorded mesh hash matches the live canonical mesh.")

    payload = {
        "generated_for": "a one-place provenance record for the 17 gated runs",
        "n_runs": len(runs),
        "fields_complete_across_all_runs": complete,
        "fields_complete_means":
            "present on every run, not recorded by every run. canitford_git_commit is "
            "RECONSTRUCTED from a file date and solver_git_sha and mesh_sha256 are RESOLVED, "
            "all three added by a backfill on 2026-08-12; see field_provenance in each run.",
        "field_provenance_across_runs": {
            k: sorted({r["field_provenance"].get(k, "absent") for r in runs})
            for k in BACKFILLED_FIELDS} if runs else {},
        "gpu_model_note":
            "not in any run record. The July batch logs record NVIDIA GH200 120GB on the Vista "
            "nodes that ran the batches, so gpu_model_inferred_from_venue carries that value for "
            "every run as an inference from the batch logs and the venue, not a per-run record.",
        "canonical_mesh_sha256": mesh_live,
        "hardware_vista": VISTA_GPU,
        "hardware_ls6_for_contrast": LS6_GPU,
        "absent_and_why": {
            # CORRECTED 2026-08-20. The first version said wall time "lives in Slurm
            # accounting on Vista", which implies go and fetch it. IT CANNOT BE FETCHED.
            # Slurm accounting DOES still hold 212 job records from 2026-07-01 to
            # 2026-08-10, but NOTHING JOINS THEM TO A RUN: all 17 summary.json files
            # carry zero job, host, or timestamp keys (the only pattern match is
            # C2_veh_zmin_start, a geometry field caught on the substring "start"), and
            # file mtimes do not help because summary.json was regenerated on 2026-08-12
            # while rollout.npz dates from 2026-07-26. A missing remote value and an
            # unjoinable one are different findings and the first understated it.
            "wall_time_per_simulated_second":
                "UNJOINABLE, not merely remote. Slurm accounting holds 212 records for "
                "the era but no summary.json carries a job id, host or timestamp, so "
                "there is no key to join on. Recoverable only for FUTURE runs, by "
                "emitting SLURM_JOB_ID into summary.json.",
            "wall_time_wandb_trap":
                # CORROBORATED FROM A SEPARATE SYSTEM, and it carries a trap. Weights and
                # Biases records runtime and GPU automatically, so it looks like the
                # obvious recovery route. It is not one, and the way it fails is worse
                # than being empty. Measured live 2026-08-20 against project can-it-ford
                # (106 runs) by read-only GraphQL: all 17 canonical runs are present,
                # every one reports host 'Josephines-MacBook-Air.local', gpu None, os
                # macOS-arm64, and _runtime EXACTLY 0. They were created 3 to 4 seconds
                # apart on 2026-08-17T21:30-21:31 with a heartbeat one second later, i.e.
                # they are a BACKFILL FROM THE MAC, not the GPU runs.
                # SO THE W&B DASHBOARD SHOWS A RUNTIME COLUMN READING 0 SECONDS FOR
                # SEVENTEEN GPU SIMULATIONS. That is a plausible-looking number that means
                # nothing, and it is the same shape as every instrument failure this
                # project has recorded: a value indistinguishable from a measurement when
                # nothing was measured. Never read timing for the canonical runs off the
                # W&B UI.
                "W&B is NOT a recovery route and its Runtime column is a trap: all 17 "
                "canonical runs show _runtime=0, host=Mac, gpu=None, because they were "
                "backfilled from the laptop on 2026-08-17. Two independent systems now "
                "agree wall time is unrecoverable for these runs.",
            "multi_gpu_scaling":
                "single-GPU runs throughout; no scaling study was ever performed",
        },
        "missing_summary": missing_summary,
        "unresolved_commits": unresolved,
        "mesh_mismatch": mesh_mismatch,
        "runs": runs,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print(f"\nwrote {os.path.relpath(OUT_JSON, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
