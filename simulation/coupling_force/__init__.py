"""Force-based fluid-rigid coupling for warpmpm.

Additive module. It does NOT modify the kinematic material-8 velocity-averaging
path (kernels/mpm_utils.py:1434); it carries the body as an SDF collider so the
engine's real reaction wrench (core/solver.py:354) can drive a Newton-Euler
integrator. See coupler.py for the scheme and README.md for the reference search.
"""
from .rigid_body import (  # noqa: F401
    RigidBodyState,
    integrate,
    inertia_from_particles,
    quat_to_matrix,
    quat_normalize,
)
from .coupler import (  # noqa: F401
    ForceCoupledBody,
    CouplingConfig,
    CouplingTrace,
    RHO_WATER,
)

__all__ = [
    "RigidBodyState", "integrate", "inertia_from_particles",
    "quat_to_matrix", "quat_normalize",
    "ForceCoupledBody", "CouplingConfig", "CouplingTrace", "RHO_WATER",
]
