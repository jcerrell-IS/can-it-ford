"""Round trip through the implemented half of bridge/: synthetic 3DGS .ply to MPM particle .npz."""
import numpy as np

from bridge.config import BridgeConfig
from bridge.extract import extract_mpm_particles
from bridge.gaussian_io import load_gaussian_checkpoint, save_mpm_particles

FIELDS = ["x", "y", "z", "opacity", "scale_0", "scale_1", "scale_2",
          "rot_0", "rot_1", "rot_2", "rot_3", "f_dc_0", "f_dc_1", "f_dc_2"]


def _write_splat(path, rows):
    header = "ply\nformat binary_little_endian 1.0\nelement vertex %d\n" % len(rows)
    header += "".join("property float %s\n" % f for f in FIELDS) + "end_header\n"
    with open(path, "wb") as fh:
        fh.write(header.encode("ascii"))
        fh.write(np.asarray(rows, dtype="<f4").tobytes())


def _synthetic_cloud(n_keep, n_drop, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_keep + n_drop):
        x, y, z = rng.uniform(-3.0, 5.0, size=3)
        opacity_logit = 4.0 if i < n_keep else -8.0   # sigmoid: ~0.98 kept, ~3e-4 dropped
        log_scale = np.log(rng.uniform(0.01, 0.05, size=3))
        quat = rng.normal(size=4)
        quat /= np.linalg.norm(quat)
        rows.append([x, y, z, opacity_logit, *log_scale, *quat, 0.0, 0.0, 0.0])
    return rows


def test_splat_to_particles_round_trip(tmp_path):
    ply = tmp_path / "scene.ply"
    _write_splat(ply, _synthetic_cloud(n_keep=200, n_drop=50))

    cloud = load_gaussian_checkpoint(str(ply))
    assert len(cloud) == 250

    cfg = BridgeConfig(checkpoint_path=str(ply), opacity_threshold=0.05, grid_lim=2.0)
    pos, vol, cov, transform = extract_mpm_particles(cloud, cfg)

    assert pos.shape == (200, 3) and pos.dtype == np.float32
    assert vol.shape == (200,) and cov.shape == (200, 6)
    assert pos.min() >= -1e-6 and pos.max() <= cfg.grid_lim + 1e-6
    assert np.all(vol > 0)

    # Covariance is symmetric positive definite: rebuild the 3x3 from its 6 stored entries.
    xx, xy, xz, yy, yz, zz = cov.T.astype(np.float64)
    sigma = np.stack([[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]]).transpose(2, 0, 1)
    assert np.all(np.linalg.eigvalsh(sigma) > 0)

    out = tmp_path / "out" / "mpm_init.npz"
    save_mpm_particles(str(out), pos, vol, cov)
    data = np.load(out)
    np.testing.assert_array_equal(data["mpm_init_pos"], pos)
    np.testing.assert_array_equal(data["mpm_init_vol"], vol)
    np.testing.assert_array_equal(data["mpm_init_cov"], cov)
