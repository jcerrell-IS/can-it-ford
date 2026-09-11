import numpy as np
from plyfile import PlyData

VEHICLE_PLY = "/work/11603/jcerrell0629/vista/truck_trimmed.ply"
CLASSES = {
    "sedan":  {"bbox_m": (4.66, 1.79, 1.44)},
    "suv":    {"bbox_m": (4.96, 1.93, 1.75)},
    "pickup": {"bbox_m": (5.89, 2.03, 1.96)},
}
N_GRIDS = [32, 48, 64, 96, 128]


def column_stats(pos, h):
    key = np.floor(pos / h).astype(np.int64)
    order = np.lexsort((key[:, 2], key[:, 1], key[:, 0]))
    k = key[order]
    col = k[:, :2]
    starts = np.flatnonzero(np.r_[True, np.any(col[1:] != col[:-1], axis=1)])
    ends = np.r_[starts[1:], len(k)]
    heights = []
    for s, e in zip(starts, ends):
        heights.append(k[e - 1, 2] - k[s, 2] + 1)
    heights = np.array(heights)
    n_cols = len(heights)
    body_cells_tall = (pos[:, 2].max() - pos[:, 2].min()) / h
    return {
        "n_cols": n_cols,
        "frac_single": float(np.mean(heights == 1)),
        "mean_h": float(heights.mean()),
        "median_h": float(np.median(heights)),
        "max_h": int(heights.max()),
        "body_cells_tall": float(body_cells_tall),
    }


def load_surface(path):
    v = PlyData.read(path)["vertex"]
    pos = np.stack([v["x"], v["y"], v["z"]], axis=1).astype(np.float64)
    ext = pos.max(0) - pos.min(0)
    if ext[0] > ext[1]:
        Rz = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        pos = pos @ Rz.T
    lo, hi = pos.min(0), pos.max(0)
    pos -= np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    return pos, pos.max(0) - pos.min(0)


def fit_to_bbox(surface, extent, bbox_m):
    length, width, height = bbox_m
    target = np.array([width, length, height], dtype=np.float64)
    return surface * (target / np.asarray(extent, dtype=np.float64))


def main():
    surface, extent = load_surface(VEHICLE_PLY)
    for cname, spec in CLASSES.items():
        bbox = spec["bbox_m"]
        pos = fit_to_bbox(surface, extent, bbox)
        length, width, height = bbox
        lim = max(2.2 * length, 3.5 * width)
        print(f"=== {cname}  bbox={bbox}  lim={lim:.4f} ===")
        print(f"{'n_grid':>7} {'h_m':>9} {'n_cols':>8} {'body_tall':>10} "
              f"{'frac_1cell':>11} {'mean_h':>8} {'med_h':>7} {'max_h':>7}")
        for ng in N_GRIDS:
            h = (lim / ng) / 2.0
            s = column_stats(pos, h)
            print(f"{ng:>7} {h:>9.5f} {s['n_cols']:>8d} {s['body_cells_tall']:>10.1f} "
                  f"{s['frac_single']:>11.3f} {s['mean_h']:>8.2f} "
                  f"{s['median_h']:>7.1f} {s['max_h']:>7d}")
        print()


if __name__ == "__main__":
    main()
