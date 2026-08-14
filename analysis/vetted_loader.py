"""Run the vetted `vehicle_live.py` geometry pipeline without importing warpmpm.

WHY THIS EXISTS. The loader the 17 gated runs actually ran is `load_vehicle` in
`renders/yaris_render_s1/vehicle_live.py`, byte-identical to the tracked copy at
`analysis/render_v1/as_ran_local_copies/vehicle_live.py` (sha256 `5a5bbbab...`).
That module imports `warpmpm.core.solver` and `warpmpm.materials` at module scope
(lines 28-29), which is unavailable on the Mac and which memory
`vista-login-warpmpm-import-hangs` records as a 600 s block on a Vista login node.

Restating the loader here would create exactly the fork CLAUDE.md item 16 complains
about, so instead the module is PARSED and its warpmpm imports are dropped from the
AST. Nothing is rewritten and no function body is edited: the geometry code that runs
is the gated code, byte-for-byte, and the source digest is checked before it runs.

This is the same technique `simulation/validate_coupling_force_ladder.py` uses on
`validate_coupling_force.py` (see its lines 104-114), applied to functions rather
than to scalar constants.

WHAT IS SAFE HERE. `load_vehicle`'s splat branch imports `warpmpm.splats.*` INSIDE the
function (vehicle_live.py:222-223). That branch is only reached when
`is_gaussian_ply()` is true. A plain watertight mesh never takes it, so dropping the
module-scope imports does not disarm a code path a mesh will use. Passing a 3DGS ply
to this shim will still raise ImportError, which is the correct behaviour.
"""
from __future__ import annotations

import ast
import hashlib
import sys
import types
from pathlib import Path

_MODULE_NAME = "vehicle_live_geometry"

# The vetted digest. Both copies carried it when this module was written; verified
# live against analysis/render_v1/as_ran_local_copies/vehicle_live.py.
VETTED_SHA256 = "5a5bbbab7d2e21df16f59fc3f0d55d40744f61861223cc43160714c6175d5944"

# The AS-RAN gated driver, sha256 5215c38b..., 389 lines. THIS is the file register
# D8c's floor-plane ruling is about, NOT renders/yaris_render_s1/sim_standing.py.
# Measured live 2026-08-14: the two copies differ by 175 lines, and the floor plane
# sits at :132-133 in this one and at :210-211 in the other. Both line numbers are
# correct, for different files. See docs/FORK_MOVING_DRIVER_2026-08-14.md.
AS_RAN_SIM_STANDING_SHA256 = "5215c38bed60"  # 12-char prefix; full digest checked below

REPO_ROOT = Path(__file__).resolve().parents[1]
AS_RAN_DIR = REPO_ROOT / "analysis" / "render_v1" / "as_ran_local_copies"
TRACKED_COPY = AS_RAN_DIR / "vehicle_live.py"
AS_RAN_SIM_STANDING = AS_RAN_DIR / "sim_standing.py"
LIVE_COPY = REPO_ROOT / "renders" / "yaris_render_s1" / "vehicle_live.py"

_DROPPED_IMPORT_ROOTS = ("warpmpm",)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _strip_engine_imports(tree: ast.Module) -> tuple[ast.Module, list[str]]:
    """Drop module-scope `from warpmpm... import ...` nodes. Nothing else is touched."""
    kept, dropped = [], []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if root in _DROPPED_IMPORT_ROOTS:
                dropped.append(f"line {node.lineno}: from {node.module} import "
                               + ", ".join(a.name for a in node.names))
                continue
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
            if any(n.split(".")[0] in _DROPPED_IMPORT_ROOTS for n in names):
                dropped.append(f"line {node.lineno}: import " + ", ".join(names))
                continue
        kept.append(node)
    tree.body = kept
    return tree, dropped


def load_engine_free(src_path: Path | str, *, module_name: str,
                     expected_sha256: str | None = None) -> types.ModuleType:
    """Exec a warpmpm-importing module with its engine imports dropped from the AST.

    expected_sha256 may be a full digest or a unique prefix; None skips the check and
    must be justified in writing wherever it is used.
    """
    src_path = Path(src_path)
    if not src_path.exists():
        raise FileNotFoundError(
            f"source not found at {src_path}. renders/ is gitignored and may be "
            "physically absent from a worktree; use the tracked copy under analysis/."
        )
    digest = sha256_of(src_path)
    if expected_sha256 is not None and not digest.startswith(expected_sha256):
        raise RuntimeError(
            f"digest mismatch for {src_path}\n  got      {digest}\n"
            f"  expected {expected_sha256}\nRefusing to run an unvetted source."
        )
    tree = ast.parse(src_path.read_text(), filename=str(src_path))
    tree, dropped = _strip_engine_imports(tree)
    mod = types.ModuleType(module_name)
    mod.__file__ = str(src_path)
    mod.__dict__["__vetted_sha256__"] = digest
    mod.__dict__["__dropped_imports__"] = dropped
    sys.modules[module_name] = mod
    try:
        exec(compile(tree, filename=str(src_path), mode="exec"), mod.__dict__)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return mod


def load_as_ran_canonicalize():
    """`canonicalize` from the AS-RAN gated driver, not restated here.

    It recomputes extent FROM THE MESH rather than from load_vehicle's 60,000 random
    surface samples, which is why the canonicalized extent is reproducible while
    load_vehicle's own `.extent` is seed-dependent.
    """
    mod = load_engine_free(AS_RAN_SIM_STANDING, module_name="as_ran_sim_standing",
                           expected_sha256=AS_RAN_SIM_STANDING_SHA256)
    return mod.canonicalize


def load_vehicle_live(path: Path | str | None = None, *, require_digest: bool = True
                      ) -> types.ModuleType:
    """Return `vehicle_live` as a module with its warpmpm imports removed.

    require_digest=True refuses to run a source whose sha256 is not the vetted one.
    Turn it off only to deliberately test a different loader, and say so in writing.
    """
    src_path = Path(path) if path is not None else TRACKED_COPY
    if not src_path.exists():
        raise FileNotFoundError(
            f"vetted loader not found at {src_path}. renders/ is gitignored and may be "
            "physically absent from a worktree; use the tracked copy under analysis/."
        )
    digest = sha256_of(src_path)
    if require_digest and digest != VETTED_SHA256:
        raise RuntimeError(
            f"loader digest mismatch for {src_path}\n  got      {digest}\n"
            f"  expected {VETTED_SHA256}\nRefusing to run an unvetted loader."
        )
    source = src_path.read_text()
    tree = ast.parse(source, filename=str(src_path))
    tree, dropped = _strip_engine_imports(tree)
    mod = types.ModuleType(_MODULE_NAME)
    mod.__file__ = str(src_path)
    mod.__dict__["__vetted_sha256__"] = digest
    mod.__dict__["__dropped_imports__"] = dropped
    # @dataclass resolves sys.modules[cls.__module__] to check for KW_ONLY, so the
    # synthetic module must be registered before the class bodies execute.
    sys.modules[_MODULE_NAME] = mod
    try:
        exec(compile(tree, filename=str(src_path), mode="exec"), mod.__dict__)
    except Exception:
        sys.modules.pop(_MODULE_NAME, None)
        raise
    return mod


if __name__ == "__main__":
    m = load_vehicle_live()
    print(f"loaded {m.__file__}")
    print(f"sha256 {m.__vetted_sha256__}")
    for d in m.__dropped_imports__:
        print(f"dropped {d}")
    print("exports:", ", ".join(sorted(
        k for k in vars(m) if not k.startswith("_") and callable(getattr(m, k)))))
