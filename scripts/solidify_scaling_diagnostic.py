import numpy as np
from plyfile import PlyData

VEHICLE_PLY = "/work/11603/jcerrell0629/vista/truck_trimmed.ply"

CLASSES = {
    "sedan":  {"bbox_m": (4.66, 1.79, 1.44), "mass_kg": 1390.0},
    "suv":    {"bbox_m": (4.96, 1.93, 1.75), "mass_kg": 1990.0},
    "pickup": {"bbox_m": (5.89, 2.03, 1.96), "mass_kg": 2300.0},
}
N_GRIDS = [32, 48, 64, 96, 128]


def solidify_columns(pos, h):
    key = np.floor(pos / h).astype(np.int64)
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0]))
    k = key[order]
    col = k[:, :2]
    starts = np.flatnonzero(np.r_[True, np.any(col[1:] != col[:-1], axis=1)])
    out = []
    for s, e in zip(starts, np.r_[starts[1:], len(k)]):
        zlo, zhi = k[s, 2], k[e - 1, 2]
        zs = np.arange(zlo, zhi + 1)
        cells = np.column_stack([np.full_like(zs, k[s, 0]),
                                 np.full_like(zs, k[s, 1]), zs])
        out.append(cells)
    cells = np.concatenate(out)
    return ((cells + 0.5) * h).astype(np.float32)


def load_surface(path):
    v = PlyData.read(path)["vertex"]
    pos = np.stack([v["x"], v["y"], v["z"]], axis=1).astype(np.float64)
    ext = pos.max(0) - pos.min(0)
    if ext[0] > ext[1]:
        Rz = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        pos = pos @ Rz.T
    lo, hi = pos.min(0), pos.max(0)
    pos -= np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    extent = pos.max(0) - pos.min(0)
    return pos, extent


def fit_to_bbox(surface, extent, bbox_m):
    length, width, height = bbox_m
    target = np.array([width, length, height], dtype=np.float64)
    scale = target / np.asarray(extent, dtype=np.float64)
    return surface * scale


def lim_of(bbox_m, depth=0.0):
    length, width, height = bbox_m
    return max(2.2 * length, 3.5 * width, 6.0 * depth)


def main():
    surface, extent = load_surface(VEHICLE_PLY)
    print(f"raw surface points: {len(surface)}")
    print(f"oriented extent (x,y,z) m: {np.round(extent, 4)}\n")

    for cname, spec in CLASSES.items():
        bbox = spec["bbox_m"]
        mass = spec["mass_kg"]
        pos = fit_to_bbox(surface, extent, bbox)
        lim = lim_of(bbox)
        print(f"=== {cname}  bbox={bbox}  mass={mass}  lim={lim:.4f} m ===")
        print(f"{'n_grid':>7} {'h_m':>9} {'n_part':>9} {'solid_vol_m3':>13} "
              f"{'density':>9} {'N_ratio':>8} {'p_exp':>7} {'vol_ratio':>10}")
        prev = None
        for ng in N_GRIDS:
            dx = lim / ng
            h = dx / 2.0
            parts = solidify_columns(pos, h)
            n = len(parts)
            vol = n * h ** 3
            dens = mass / vol
            if prev is None:
                nr = pe = vr = float("nan")
            else:
                png, pn, pvol = prev
                nr = n / pn
                pe = np.log(n / pn) / np.log(ng / png)
                vr = vol / pvol
            print(f"{ng:>7} {h:>9.5f} {n:>9d} {vol:>13.4f} {dens:>9.2f} "
                  f"{nr:>8.3f} {pe:>7.3f} {vr:>10.4f}")
            prev = (ng, n, vol)
        print()


if __name__ == "__main__":
    main()
