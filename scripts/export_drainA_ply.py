#!/usr/bin/env python3
"""
Export a single merged PLY from the completed drainA 30k gsplat run.

WHY THIS EXISTS
  Job 3306077 (drainA_fresh, COMPLETED 2026-07-20T19:59:34) trained
  simple_trainer.py to 30,000 steps across 3 A100 ranks, but its sbatch
  omitted --save-ply, so the run's own cfg.yml records save_ply: false and
  no PLY was written at step 29999. The only drainA PLY on disk is
  point_cloud_2999.ply from the 3,000-step run of 2026-07-17. Anything
  downstream consuming "the drainA splat" has been reading a 3k model.

  This re-exports from the surviving checkpoints. It does NOT retrain, so
  the exported geometry is exactly the model behind the published
  PSNR 22.7356 / SSIM 0.8249 / LPIPS 0.3112.

WHY ALL THREE RANKS
  simple_trainer.py shards the Gaussians across ranks; it does not
  replicate them. The three checkpoints hold different counts
  (399,491 / 374,677 / 373,526). stats/val_step29999.json reports
  num_GS 399491, which is rank 0's shard alone, not the scene. Exporting
  from rank 0 only would silently drop 65% of the model.

WHY NO GPU
  gsplat.exporter.export_splats is pure CPU tensor work: a NaN/Inf filter,
  a reshape, a concat, and a binary write. Nothing here touches CUDA, so
  this runs on a login node and needs no allocation.

WHAT THE PLY CONTAINS
  gsplat's splat2ply_bytes writes the RAW stored parameters, standard 3DGS
  convention: scales are log-scale and opacity is logit, not activated.
  59 float32 per vertex: x,y,z + f_dc_0..2 + f_rest_0..44 + opacity +
  scale_0..2 + rot_0..3. No nx/ny/nz normals field is emitted.

USAGE (on LS6, login node is fine)
  source /scratch/10386/lsmith9003/python-envs/gsplat_env/bin/activate
  python3 export_drainA_ply.py
  python3 export_drainA_ply.py --out /path/to/other.ply

Refuses to overwrite an existing output file unless --force is given.
"""

import argparse
import hashlib
import os
import struct
import sys

CKPT_DIR = "/scratch/11603/jcerrell0629/gsplat/examples/results/drainA/ckpts"
RANKS = (0, 1, 2)
EXPECTED_STEP = 29999
# Per-rank counts recorded live 2026-08-07 from stats/train_step29999_rank*.json.
EXPECTED_COUNTS = {0: 399491, 1: 374677, 2: 373526}
DEFAULT_OUT = (
    "/scratch/11603/jcerrell0629/gsplat/examples/results/drainA/ply/"
    "point_cloud_29999_merged_3ranks.ply"
)
FIELDS = ("means", "sh0", "shN", "opacities", "scales", "quats")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ckpt-dir", default=CKPT_DIR)
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--force", action="store_true",
                   help="allow overwriting an existing output file")
    return p.parse_args()


def main():
    args = parse_args()
    import torch
    from gsplat.exporter import export_splats

    if os.path.exists(args.out) and not args.force:
        sys.exit(f"REFUSING: {args.out} already exists. Pass --force to overwrite.")

    shards = []
    total = 0
    print("Loading checkpoints (CPU only):")
    for r in RANKS:
        path = os.path.join(args.ckpt_dir, f"ckpt_{EXPECTED_STEP}_rank{r}.pt")
        if not os.path.exists(path):
            sys.exit(f"MISSING: {path}")
        d = torch.load(path, map_location="cpu", weights_only=False)

        step = d.get("step")
        if step != EXPECTED_STEP:
            sys.exit(f"STEP MISMATCH in {path}: got {step}, expected {EXPECTED_STEP}")

        splats = d["splats"]
        missing = [f for f in FIELDS if f not in splats]
        if missing:
            sys.exit(f"MISSING TENSORS in {path}: {missing}")

        n = splats["means"].shape[0]
        # Every tensor in a shard must agree on N, or the concat silently misaligns.
        for f in FIELDS:
            if splats[f].shape[0] != n:
                sys.exit(f"RAGGED SHARD in {path}: {f} has "
                         f"{splats[f].shape[0]} rows, means has {n}")

        exp = EXPECTED_COUNTS.get(r)
        flag = "" if exp is None or exp == n else f"  <-- DIFFERS from census {exp}"
        print(f"  rank{r}: N={n:>9,}  step={step}{flag}")
        shards.append(splats)
        total += n

    if len({tuple(s["shN"].shape[1:]) for s in shards}) != 1:
        sys.exit("shN degree differs between ranks; refusing to concatenate.")

    print(f"  TOTAL  : N={total:>9,}")
    if total == EXPECTED_COUNTS[0]:
        sys.exit("Total equals rank0 alone. Refusing: this would be the 65% loss.")

    merged = {f: torch.cat([s[f] for s in shards], dim=0) for f in FIELDS}
    for f in FIELDS:
        if merged[f].shape[0] != total:
            sys.exit(f"CONCAT ERROR: {f} has {merged[f].shape[0]} rows, expected {total}")

    n_nonfinite = int((~torch.isfinite(merged["means"])).any(dim=1).sum())
    if n_nonfinite:
        print(f"  NOTE: {n_nonfinite} splats have non-finite means; "
              f"export_splats drops them.")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    print(f"Writing {args.out} ...")
    export_splats(
        means=merged["means"],
        scales=merged["scales"],
        quats=merged["quats"],
        opacities=merged["opacities"],
        sh0=merged["sh0"],
        shN=merged["shN"],
        format="ply",
        save_to=args.out,
    )

    verify(args.out, total - n_nonfinite)


def verify(path, expected_n):
    """Re-read the written file and prove the header and byte count agree."""
    size = os.path.getsize(path)
    header = b""
    with open(path, "rb") as fh:
        while b"end_header\n" not in header:
            chunk = fh.read(4096)
            if not chunk:
                break
            header += chunk
    head_txt = header.split(b"end_header\n")[0].decode("ascii", "replace")
    hdr_len = len(header.split(b"end_header\n")[0]) + len(b"end_header\n")

    n_hdr = None
    n_props = 0
    for line in head_txt.splitlines():
        if line.startswith("element vertex"):
            n_hdr = int(line.split()[-1])
        elif line.startswith("property float"):
            n_props += 1

    payload = size - hdr_len
    stride = n_props * 4
    print("\n--- VERIFICATION, read back from the written file ---")
    print(f"  file size          : {size:,} bytes")
    print(f"  header vertex count: {n_hdr:,}" if n_hdr is not None
          else "  header vertex count: MISSING")
    print(f"  expected count     : {expected_n:,}")
    print(f"  properties/vertex  : {n_props} floats ({stride} bytes)")
    print(f"  payload            : {payload:,} bytes")

    ok = True
    if n_hdr is None:
        print("  FAIL: no 'element vertex' line found in the header.")
        ok = False
    elif n_hdr != expected_n:
        print("  FAIL: header count does not match the merged tensor count.")
        ok = False
    if n_hdr is not None and stride and payload != n_hdr * stride:
        print(f"  FAIL: payload is not vertices*stride "
              f"(expected {n_hdr * stride:,}).")
        ok = False

    # Spot-check the first vertex is finite, so the file is not all zeros.
    if ok:
        with open(path, "rb") as fh:
            fh.seek(hdr_len)
            xyz = struct.unpack("<3f", fh.read(12))
        print(f"  first vertex x,y,z : {xyz}")
        if not all(map(lambda v: v == v and abs(v) != float("inf"), xyz)):
            print("  FAIL: first vertex is not finite.")
            ok = False

    h = hashlib.md5()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    print(f"  md5                : {h.hexdigest()}")
    print("  RESULT             : " + ("PASS" if ok else "FAIL"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
