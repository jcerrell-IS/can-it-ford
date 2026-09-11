from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

_DTYPE_BYTES = {"float": 4, "double": 8, "int": 4, "uint": 4, "short": 2,
                "ushort": 2, "char": 1, "uchar": 1}
_NP_DTYPE = {"float": "<f4", "double": "<f8", "int": "<i4", "uint": "<u4",
             "short": "<i2", "ushort": "<u2", "char": "<i1", "uchar": "<u1"}
_HEADER_MAX_BYTES = 1 << 20
_GAUSSIAN_PLY_FIELDS = frozenset({"opacity", "f_dc_0"})


@dataclass
class GaussianCloud:
    positions: np.ndarray
    opacities: np.ndarray
    scales: np.ndarray
    rotations: np.ndarray
    colors: np.ndarray | None = None

    def __len__(self) -> int:
        return int(self.positions.shape[0])


class PlyHeader:
    def __init__(self, fmt, count, props, header_bytes):
        self.fmt = fmt
        self.count = count
        self.props = props
        self.header_bytes = header_bytes

    @property
    def names(self):
        return [n for _, n in self.props]

    @property
    def row_bytes(self):
        return sum(_DTYPE_BYTES[t] for t, _ in self.props)

    @property
    def row_dtype(self):
        return np.dtype([(n, _NP_DTYPE[t]) for t, n in self.props])


def read_ply_header(path: str) -> PlyHeader:
    with open(path, "rb") as f:
        blob = f.read(_HEADER_MAX_BYTES)
    marker = b"end_header\n"
    idx = blob.find(marker)
    if idx < 0:
        raise ValueError(f"read_ply_header: no end_header in first {_HEADER_MAX_BYTES} bytes of {path}")
    header_bytes = idx + len(marker)
    lines = [ln.strip() for ln in blob[:idx].decode("ascii", errors="replace").splitlines()]
    if not lines or lines[0] != "ply":
        raise ValueError(f"read_ply_header: first line is not 'ply' in {path}")
    fmt = None
    count = None
    props = []
    in_vertex = False
    for ln in lines:
        if ln.startswith("format "):
            fmt = ln.split()[1]
        elif ln.startswith("element "):
            parts = ln.split()
            in_vertex = parts[1] == "vertex"
            if in_vertex:
                count = int(parts[2])
        elif ln.startswith("property ") and in_vertex:
            parts = ln.split()
            if parts[1] == "list":
                raise ValueError(f"read_ply_header: list property in vertex element of {path}")
            props.append((parts[1], parts[2]))
    if fmt is None or count is None:
        raise ValueError(f"read_ply_header: missing format or vertex element in {path}")
    return PlyHeader(fmt, count, props, header_bytes)


def is_gaussian_ply(path: str) -> bool:
    try:
        return _GAUSSIAN_PLY_FIELDS.issubset(set(read_ply_header(path).names))
    except Exception:
        return False


def load_gaussian_checkpoint(path: str, chunk_rows: int = 131072) -> GaussianCloud:
    if not path.lower().endswith(".ply"):
        raise ValueError(f"load_gaussian_checkpoint: only .ply is implemented, got {path}")
    hdr = read_ply_header(path)
    if hdr.fmt != "binary_little_endian":
        raise ValueError(f"load_gaussian_checkpoint: format {hdr.fmt} unsupported")
    if not _GAUSSIAN_PLY_FIELDS.issubset(set(hdr.names)):
        raise ValueError(f"load_gaussian_checkpoint: {path} is not a 3DGS ply")

    groups = {
        "positions": ("x", "y", "z"),
        "opacities": ("opacity",),
        "scales": ("scale_0", "scale_1", "scale_2"),
        "rotations": ("rot_0", "rot_1", "rot_2", "rot_3"),
        "colors": ("f_dc_0", "f_dc_1", "f_dc_2"),
    }
    names = set(hdr.names)
    for key, fields in groups.items():
        missing = [f for f in fields if f not in names]
        if missing:
            raise ValueError(f"load_gaussian_checkpoint: missing {missing} for {key}")

    expected = hdr.header_bytes + hdr.count * hdr.row_bytes
    actual = os.path.getsize(path)
    if actual != expected:
        raise ValueError(
            f"load_gaussian_checkpoint: size mismatch for {path}: expected {expected}, got {actual}"
        )

    out = {k: np.empty((hdr.count, len(f)), dtype=np.float32) for k, f in groups.items()}
    row_dt = hdr.row_dtype
    done = 0
    with open(path, "rb") as f:
        f.seek(hdr.header_bytes)
        while done < hdr.count:
            n = min(chunk_rows, hdr.count - done)
            buf = np.fromfile(f, dtype=row_dt, count=n)
            if buf.shape[0] != n:
                raise ValueError(f"load_gaussian_checkpoint: short read at row {done}")
            for key, fields in groups.items():
                for j, fld in enumerate(fields):
                    out[key][done:done + n, j] = buf[fld]
            done += n

    return GaussianCloud(
        positions=out["positions"],
        opacities=out["opacities"].reshape(-1),
        scales=out["scales"],
        rotations=out["rotations"],
        colors=out["colors"],
    )


def save_mpm_particles(path: str, pos: np.ndarray, vol: np.ndarray, cov: np.ndarray) -> None:
    if pos.shape[0] != vol.shape[0] or pos.shape[0] != cov.shape[0]:
        raise ValueError(
            f"particle count mismatch: pos={pos.shape[0]} vol={vol.shape[0]} cov={cov.shape[0]}"
        )
    if pos.shape[1] != 3 or cov.shape[1] != 6:
        raise ValueError(f"expected pos (N,3) and cov (N,6), got {pos.shape} and {cov.shape}")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    np.savez(
        path,
        mpm_init_pos=pos.astype(np.float32),
        mpm_init_vol=vol.astype(np.float32).reshape(-1),
        mpm_init_cov=cov.astype(np.float32),
    )
