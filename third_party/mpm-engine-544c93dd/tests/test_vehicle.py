"""Vehicle-in-flood module: column solidification, orientation math, and a smoke run
of the two-way rigid coupling (the surge must move the body downstream)."""
from __future__ import annotations

import numpy as np
import pytest

from warpmpm.vehicle import (
    FloodScene,
    VehicleBody,
    _up_rotation,
    euler_zyx,
    load_vehicle,
    solidify_columns,
)


def _box_shell(size=(0.08, 0.12, 0.06), h=0.01):
    """Hollow axis-aligned box shell of surface points, floor at z = 0."""
    sx, sy, sz = size
    xs = np.arange(-sx / 2, sx / 2 + h / 2, h)
    ys = np.arange(-sy / 2, sy / 2 + h / 2, h)
    zs = np.arange(0, sz + h / 2, h)
    faces = []
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    for z in (0.0, sz):
        faces.append(np.stack([X.ravel(), Y.ravel(), np.full(X.size, z)], 1))
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    for y in (-sy / 2, sy / 2):
        faces.append(np.stack([X.ravel(), np.full(X.size, y), Z.ravel()], 1))
    Y, Z = np.meshgrid(ys, zs, indexing="ij")
    for x in (-sx / 2, sx / 2):
        faces.append(np.stack([np.full(Y.size, x), Y.ravel(), Z.ravel()], 1))
    return np.concatenate(faces)


def test_solidify_columns_fills_hollow_shell():
    shell = _box_shell()
    h = 0.01
    solid = solidify_columns(shell, h)
    # interior points exist: cells strictly inside the shell in x, y, and z
    inner = ((np.abs(solid[:, 0]) < 0.03) & (np.abs(solid[:, 1]) < 0.05)
             & (solid[:, 2] > 0.015) & (solid[:, 2] < 0.045))
    assert inner.sum() > 50
    # nothing outside the bounding box (one cell of slack for voxel centering)
    assert solid[:, 2].min() > -h and solid[:, 2].max() < 0.06 + h


def test_up_rotation_and_euler_roundtrip():
    for up in ("z", "-y", "y", "x"):
        R = _up_rotation(up)
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
        assert np.isclose(np.linalg.det(R), 1.0)
    # -y up: a point along -y maps to +z
    assert np.allclose(_up_rotation("-y") @ np.array([0, -1, 0]), [0, 0, 1], atol=1e-12)
    yaw = np.radians(25.0)
    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0],
                   [0, 0, 1]])
    y, p, r = euler_zyx(Rz)
    assert np.isclose(np.degrees(y), 25.0) and abs(p) < 1e-9 and abs(r) < 1e-9


def test_load_vehicle_from_mesh(tmp_path):
    trimesh = pytest.importorskip("trimesh")
    m = trimesh.creation.box(extents=(0.5, 0.2, 0.15))
    path = tmp_path / "box.stl"
    m.export(path)
    v = load_vehicle(path, target_length=1.0)
    # long axis rotated to y and rescaled; floor at z = 0; solid interior
    assert np.isclose(v.extent[1], 1.0, rtol=0.05)
    assert v.extent[1] > v.extent[0]
    assert v.particles[:, 2].min() > -v.spacing
    assert v.n_particles > 200
    assert v.splat_pos is None  # meshes render nothing; particles still simulate


def test_flood_pushes_rigid_body_downstream():
    shell = _box_shell()
    v = VehicleBody(particles=solidify_columns(shell, 0.008), spacing=0.008,
                    extent=np.array([0.08, 0.12, 0.06]), surface=shell)
    scene = FloodScene(v, depth=0.04, velocity=1.2, n_grid=24, fps=20,
                       bulk_modulus=4.0e4, settle_frames=2, device="cpu",
                       vehicle_mass=1.7)
    assert scene.solver._sim.n_rigid_bodies == 1
    # vehicle_mass overrides density and matches the fork's own body mass
    assert np.isclose(scene.vehicle_mass, 1.7)
    assert np.isclose(scene.solver._sim.rigid_mass.numpy()[0], 1.7, rtol=1e-5)
    scene.run(frames=3)
    d = np.asarray(scene.history.displacement[-1])
    assert np.isfinite(d).all()
    # the surge travels along +x and must push the body downstream, beyond jitter
    assert d[0] > 1e-4
    # pose helper returns a rigid transform: R orthonormal, t maps spawn com to com
    R, t = scene.vehicle_pose()
    assert np.allclose(R @ R.T, np.eye(3), atol=1e-5)
    com_veh = scene.com0 - scene._place
    assert np.allclose(R @ com_veh + t, scene.solver.rigid_state()["com"], atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
