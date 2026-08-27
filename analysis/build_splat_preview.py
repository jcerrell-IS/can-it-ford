from __future__ import annotations

import argparse
import array
import math
import struct
import sys
from pathlib import Path

SRC_PROPS = 59
KEEP = [0, 1, 2, 3, 4, 5, 51, 52, 53, 54, 55, 56, 57, 58]
OUT_NAMES = [
    "x", "y", "z",
    "f_dc_0", "f_dc_1", "f_dc_2",
    "opacity",
    "scale_0", "scale_1", "scale_2",
    "rot_0", "rot_1", "rot_2", "rot_3",
]
I_OPACITY = 51
I_SCALE = (52, 53, 54)


def sigmoid(x: float) -> float:
    if x < -60.0:
        return 0.0
    if x > 60.0:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def read_header(path: Path):
    with path.open("rb") as fh:
        blob = b""
        while b"end_header\n" not in blob:
            chunk = fh.read(4096)
            if not chunk:
                raise SystemExit(f"no end_header in {path}")
            blob += chunk
    end = blob.index(b"end_header\n") + len(b"end_header\n")
    text = blob[:end].decode("ascii", "replace")
    props = [ln.split()[-1] for ln in text.splitlines() if ln.startswith("property")]
    count = 0
    for ln in text.splitlines():
        if ln.startswith("element vertex"):
            count = int(ln.split()[-1])
    return end, props, count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--target", type=int, default=350_000)
    ap.add_argument("--min-alpha", type=float, default=0.1)
    args = ap.parse_args()

    src = Path(args.src)
    out = Path(args.out)

    off, props, n_declared = read_header(src)
    if len(props) != SRC_PROPS:
        raise SystemExit(f"expected {SRC_PROPS} properties, found {len(props)}")
    for i, name in zip(KEEP, OUT_NAMES):
        if props[i] != name:
            raise SystemExit(f"property {i} is {props[i]!r}, expected {name!r}")

    raw = src.read_bytes()
    vals = array.array("f")
    vals.frombytes(raw[off:])
    del raw
    n = len(vals) // SRC_PROPS
    if n != n_declared:
        raise SystemExit(f"header declares {n_declared} vertices, buffer holds {n}")
    print(f"source        : {src}")
    print(f"vertices      : {n:,}")

    alpha = vals[I_OPACITY::SRC_PROPS]
    s0 = vals[I_SCALE[0]::SRC_PROPS]
    s1 = vals[I_SCALE[1]::SRC_PROPS]
    s2 = vals[I_SCALE[2]::SRC_PROPS]

    scored = []
    dropped = 0
    for i in range(n):
        a = sigmoid(alpha[i])
        if a < args.min_alpha:
            dropped += 1
            continue
        footprint = math.exp((s0[i] + s1[i] + s2[i]) / 3.0)
        scored.append((a * footprint, i))
    print(f"below alpha   : {dropped:,} dropped at sigmoid(opacity) < {args.min_alpha}")
    print(f"eligible      : {len(scored):,}")

    scored.sort(key=lambda t: t[0], reverse=True)
    keep = sorted(i for _, i in scored[: args.target])
    print(f"kept          : {len(keep):,}")

    header = [
        "ply",
        "format binary_little_endian 1.0",
        f"element vertex {len(keep)}",
    ]
    header += [f"property float {nm}" for nm in OUT_NAMES]
    header.append("end_header")
    blob = ("\n".join(header) + "\n").encode("ascii")

    pack = struct.Struct("<14f").pack
    body = bytearray()
    for i in keep:
        base = i * SRC_PROPS
        body += pack(*(vals[base + j] for j in KEEP))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob + bytes(body))
    size = out.stat().st_size
    print(f"output        : {out}")
    print(f"size          : {size:,} bytes ({size / 1048576:.2f} MB)")
    print(f"reduction     : {src.stat().st_size / size:.1f}x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
