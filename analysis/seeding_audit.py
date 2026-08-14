"""Audit the unseeded 60,000-sample draw in load_vehicle, and its real consequences.

THE CLAIM BEING TESTED, restated so it can be falsified rather than repeated:

    "the SDF cache never hits because load_vehicle draws 60,000 RANDOM surface
     samples, so back-to-back loads differ by 2.22e-16 m, one ULP, which changes
     build_sdf_cached's content hash and forces a rebuild every run. Seed that
     sampling."

Three separable questions, each answered by measurement here rather than by reading
the claim back:

  Q1  Does the CANONICAL driver renders/yaris_render_s1/sim_standing.py call
      load_vehicle without seeding, and does it build an SDF at all? If it never
      builds one, there is no cache to miss and the compute-cost consequence does
      not apply to the canonical runs however true the mechanism is elsewhere.

  Q2  Is the perturbation really one ULP, and does it really change the cache key?
      _hashkey (warpmpm/geometry/mesh_sdf.py:520-535) is a SHA1 over the raw
      float64 bytes of the vertex array, so a single differing bit changes it.
      That much is structural. The MAGNITUDE is the part that needs measuring.

  Q3  Does np.random.seed() actually control trimesh's surface sampling in the
      installed trimesh version? This is the load-bearing assumption of the fix
      that is already written into simulation/moving_vehicle_sdf_exploratory.py.
      If trimesh internally uses np.random.default_rng(), which draws fresh OS
      entropy, then np.random.seed() would NOT control it and the fix would be
      inert while looking correct. Never assume a seeding call works; demonstrate
      the two loads are bitwise identical.

ENGINE SCOPE: warpmpm only, at the pinned SHA recorded in
third_party/mpm-engine-544c93dd-solver-core/VENDORED.md. Nothing here applies to
Genesis or to any other engine.

READ-ONLY. This script measures and reports. It edits no driver and no canonical
store. Where it finds a defect it says so and leaves the fix to a scoped change.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np

CANONICAL_DRIVER = Path("/Users/josie/can-it-ford/renders/yaris_render_s1/sim_standing.py")
CANONICAL_HULL = Path("/Users/josie/can-it-ford/vehicle_geometry_research/"
                      "yaris_coarse_v1l_watertight.ply")


def load_warpmpm_pieces(src: Path):
    """Import the real load_vehicle and _hashkey without dragging in torch.

    warpmpm/__init__.py -> core/solver.py -> kernels/ -> warp_utils.py imports torch,
    which is absent on this Mac and is not needed to answer any question here. The
    package __init__ is therefore bypassed and vehicle.py is loaded by path with its
    two module-level solver imports stubbed. Those stubs are only referenced by
    FloodScene, which this audit never constructs. This is the REAL upstream
    load_vehicle, not a reimplementation of it, which matters: a reimplementation
    could not detect a discrepancy between what the source says and what it does.
    """
    for name, attrs in (("warpmpm.core.solver", ("GridConfig", "Solver")),
                        ("warpmpm.materials", ("newtonian",))):
        m = types.ModuleType(name)
        for a in attrs:
            setattr(m, a, object)
        sys.modules[name] = m
    pkg = types.ModuleType("warpmpm"); pkg.__path__ = [str(src / "warpmpm")]
    sys.modules["warpmpm"] = pkg
    core = types.ModuleType("warpmpm.core"); core.__path__ = [str(src / "warpmpm" / "core")]
    sys.modules["warpmpm.core"] = core
    geo = types.ModuleType("warpmpm.geometry"); geo.__path__ = [str(src / "warpmpm" / "geometry")]
    sys.modules["warpmpm.geometry"] = geo

    def _load(modname: str, path: Path):
        spec = importlib.util.spec_from_file_location(modname, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod            # register BEFORE exec: @dataclass needs it
        spec.loader.exec_module(mod)
        return mod

    veh = _load("warpmpm.vehicle", src / "warpmpm" / "vehicle.py")
    msdf = _load("warpmpm.geometry.mesh_sdf", src / "warpmpm" / "geometry" / "mesh_sdf.py")
    return veh, msdf


def canonicalize(v, trimesh):
    """Byte-for-byte the canonicalize() of renders/yaris_render_s1/sim_standing.py:96-105.

    Copied deliberately rather than imported: the canonical driver is outside this
    branch's write scope and importing it would execute its module-level constants,
    which point at Vista paths that do not exist here.
    """
    mv = np.asarray(v.mesh.vertices, dtype=np.float64)
    lo, hi = mv.min(0), mv.max(0)
    shift = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    mv = mv - shift
    v.mesh = trimesh.Trimesh(vertices=mv, faces=np.asarray(v.mesh.faces), process=False)
    v.surface = (np.asarray(v.surface, dtype=np.float64) - shift).astype(np.float32)
    v.extent = mv.max(0) - mv.min(0)
    v.spacing = float(v.extent.max()) / 32.0
    return v


def q1_canonical_driver_audit() -> dict:
    """Static audit of the canonical driver: seeding, load count, SDF usage."""
    if not CANONICAL_DRIVER.exists():
        return {"error": "canonical driver not found at %s" % CANONICAL_DRIVER}
    text = CANONICAL_DRIVER.read_text()
    lines = text.split("\n")

    load_lines = [i + 1 for i, l in enumerate(lines) if "load_vehicle(" in l and "import" not in l]
    seed_lines = [i + 1 for i, l in enumerate(lines) if "np.random.seed" in l]
    rng_lines = [i + 1 for i, l in enumerate(lines) if "default_rng" in l]
    sdf_lines = [i + 1 for i, l in enumerate(lines)
                 if "sdf" in l.lower() and not l.strip().startswith("#")]

    first_load = min(load_lines) if load_lines else None
    seeded_before = bool(seed_lines and first_load and min(seed_lines) < first_load)
    return {
        "driver": str(CANONICAL_DRIVER),
        "n_lines": len(lines),
        "load_vehicle_call_lines": load_lines,
        "n_load_vehicle_calls": len(load_lines),
        "np_random_seed_lines": seed_lines,
        "default_rng_lines": rng_lines,
        "sdf_reference_lines": sdf_lines,
        "builds_an_sdf": bool(sdf_lines),
        "seeded_before_first_load": seeded_before,
        "surface_samples_drawn_per_run": 60_000 * len(load_lines),
    }


def q2q3_load_experiment(veh, msdf, trimesh, hull: Path) -> dict:
    """Load the hull repeatedly, unseeded and seeded, and compare bitwise."""
    def one(seed=None):
        if seed is not None:
            np.random.seed(seed)
        v = veh.load_vehicle(hull, up="z")
        pre_extent = np.array(v.extent, dtype=np.float64).copy()
        pre_verts = np.ascontiguousarray(v.mesh.vertices, dtype=np.float64).copy()
        v = canonicalize(v, trimesh)
        return {
            "pre_extent": pre_extent,
            "pre_verts": pre_verts,
            "post_verts": np.ascontiguousarray(v.mesh.vertices, dtype=np.float64).copy(),
            "post_extent": np.array(v.extent, dtype=np.float64).copy(),
            "faces": np.ascontiguousarray(v.mesh.faces, dtype=np.int64).copy(),
            "n_particles": int(v.n_particles),
            "spacing": float(v.spacing),
        }

    # --- unseeded, two back-to-back loads (what the canonical driver does) ---
    a, b = one(), one()
    dpre = np.abs(a["pre_verts"] - b["pre_verts"])
    dpost = np.abs(a["post_verts"] - b["post_verts"])
    key_a = msdf._hashkey(a["post_verts"], a["faces"], 64, 4.0)
    key_b = msdf._hashkey(b["post_verts"], b["faces"], 64, 4.0)

    # --- seeded with the SAME seed, two loads: does the fix actually work? ---
    s1, s2 = one(seed=1234), one(seed=1234)
    dseed = np.abs(s1["post_verts"] - s2["post_verts"])
    key_s1 = msdf._hashkey(s1["post_verts"], s1["faces"], 64, 4.0)
    key_s2 = msdf._hashkey(s2["post_verts"], s2["faces"], 64, 4.0)

    # --- seeded with DIFFERENT seeds: must differ, else the seed is being ignored
    #     and "identical" above would be meaningless ---
    d1, d2 = one(seed=1), one(seed=2)
    key_d1 = msdf._hashkey(d1["post_verts"], d1["faces"], 64, 4.0)
    key_d2 = msdf._hashkey(d2["post_verts"], d2["faces"], 64, 4.0)

    ulp = float(np.spacing(np.abs(a["post_verts"]).max()))
    return {
        "hull": str(hull),
        "n_vertices": int(a["post_verts"].shape[0]),
        "unseeded": {
            "extent_delta_pre_canonicalize_m": [float(q) for q in
                                                np.abs(a["pre_extent"] - b["pre_extent"])],
            "vertex_max_abs_delta_pre_canonicalize_m": float(dpre.max()),
            "vertex_max_abs_delta_post_canonicalize_m": float(dpost.max()),
            "n_vertices_differing_post": int((dpost > 0).any(axis=1).sum()),
            "one_ulp_at_this_magnitude_m": ulp,
            "delta_in_ulps": (float(dpost.max() / ulp) if ulp > 0 else float("nan")),
            "sdf_cache_key_a": key_a,
            "sdf_cache_key_b": key_b,
            "cache_would_hit": bool(key_a == key_b),
            "n_particles_a": a["n_particles"],
            "n_particles_b": b["n_particles"],
            "particle_count_stable": bool(a["n_particles"] == b["n_particles"]),
            "spacing_delta": abs(a["spacing"] - b["spacing"]),
        },
        "seeded_same": {
            "vertex_max_abs_delta_m": float(dseed.max()),
            "bitwise_identical": bool(np.array_equal(s1["post_verts"], s2["post_verts"])),
            "sdf_cache_key_1": key_s1,
            "sdf_cache_key_2": key_s2,
            "cache_would_hit": bool(key_s1 == key_s2),
            "n_particles_equal": bool(s1["n_particles"] == s2["n_particles"]),
        },
        "seeded_different": {
            "sdf_cache_key_seed1": key_d1,
            "sdf_cache_key_seed2": key_d2,
            "keys_differ_as_they_must": bool(key_d1 != key_d2),
        },
    }


def seed_mesh_sampling(mesh, count, seed):
    """Draw `count` surface samples reproducibly, whichever trimesh is installed.

    THIS IS THE DURABLE FORM OF THE FIX, and the reason it is not a one-liner:
    trimesh changed its RNG source between the version on LS6 and the version on
    this Mac, and the change is SILENT.

      trimesh 4.12.2 (LS6, measured live 2026-08-14): Trimesh.sample has NO seed
        kwarg and draws from the legacy global np.random state, so
        `np.random.seed(k)` before the call DOES make it reproducible.
      trimesh 5.0.0 (this Mac, measured live 2026-08-14): Trimesh.sample HAS a seed
        kwarg and uses np.random.default_rng internally, which ignores the legacy
        global state entirely, so `np.random.seed(k)` has NO effect.

    So `np.random.seed(k)` before load is correct today on LS6 and becomes a no-op
    the moment trimesh is upgraded, with no error and no warning: the runs simply
    stop being reproducible. Prefer the kwarg when it exists and fall back
    otherwise, so the seeding survives either version.
    """
    try:
        return np.asarray(mesh.sample(count, seed=seed))
    except TypeError:
        np.random.seed(seed)
        return np.asarray(mesh.sample(count))


def q3_direct_seed_control(trimesh, hull: Path, count: int = 2000,
                           repeats: int = 5) -> dict:
    """Test seed control DIRECTLY on mesh.sample(), with repeats.

    WHY NOT INFER IT FROM THE LOAD EXPERIMENT. Because that inference is unsound and
    was measured to be unsound. canonicalize() cancels the sample-dependent shift to
    within half an ULP, so the post-canonicalize vertex array collapses onto a small
    set of nearby float64 values; two INDEPENDENT unseeded loads therefore land on
    the same value a fair fraction of the time. A single same-seed pair coming out
    identical is then a coin flip, not evidence of seeding, and back-to-back runs of
    this very audit reported `bitwise_identical` True and False for the same trimesh.
    The direct test has no such degeneracy: two 2000-point surface samples that were
    not drawn from the same RNG state differ by metres, not by ULPs.

    Repeats are used because one trial cannot establish a deterministic property.
    """
    m = trimesh.load(hull, force="mesh")
    same_seed_identical = []
    for r in range(repeats):
        np.random.seed(1000 + r)
        a = np.asarray(m.sample(count))
        np.random.seed(1000 + r)
        b = np.asarray(m.sample(count))
        same_seed_identical.append(bool(np.array_equal(a, b)))

    unseeded_identical = []
    for _ in range(repeats):
        c = np.asarray(m.sample(count))
        d = np.asarray(m.sample(count))
        unseeded_identical.append(bool(np.array_equal(c, d)))

    kwarg_works = None
    try:
        e = np.asarray(m.sample(count, seed=42))
        f = np.asarray(m.sample(count, seed=42))
        g = np.asarray(m.sample(count, seed=43))
        kwarg_works = bool(np.array_equal(e, f) and not np.array_equal(e, g))
    except TypeError:
        kwarg_works = False                      # no seed kwarg in this version

    return {
        "trimesh_version": getattr(trimesh, "__version__", "unknown"),
        "repeats": repeats,
        "sample_count": count,
        "np_random_seed_reproduces": all(same_seed_identical),
        "np_random_seed_detail": same_seed_identical,
        "unseeded_ever_identical": any(unseeded_identical),
        "seed_kwarg_supported_and_works": kwarg_works,
    }


def q4_demonstrate_cache_hit(veh, msdf, trimesh, hull: Path, seed: int = 20260814) -> dict:
    """Demonstrate an actual SDF cache HIT once the sampling is genuinely seeded.

    load_vehicle's sampling call is monkeypatched for the duration, which emulates
    the corrected upstream line without editing upstream. Two loads are then made and
    their cache keys compared. A HIT here is the demonstration the dispatch asks for;
    a MISS would mean the seeding did not take and the fix is not real.
    """
    orig = trimesh.Trimesh.sample

    def seeded(mesh, count, *_a, **_kw):
        """Same two-branch logic as seed_mesh_sampling, against the unpatched call."""
        try:
            return np.asarray(orig(mesh, count, seed=seed))
        except TypeError:
            np.random.seed(seed)
            return np.asarray(orig(mesh, count))

    trimesh.Trimesh.sample = seeded
    try:
        keys = []
        for _ in range(3):
            v = canonicalize(veh.load_vehicle(hull, up="z"), trimesh)
            pv = np.ascontiguousarray(v.mesh.vertices, dtype=np.float64)
            keys.append(msdf._hashkey(pv, np.ascontiguousarray(v.mesh.faces, dtype=np.int64),
                                      64, 4.0))
    finally:
        trimesh.Trimesh.sample = orig
    return {
        "seed": seed,
        "keys": keys,
        "n_distinct": len(set(keys)),
        "cache_hits_after_first": bool(len(set(keys)) == 1),
        "trimesh_version": getattr(trimesh, "__version__", "unknown"),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="/Users/josie/Downloads/mpm-engine-main/src",
                   help="warpmpm source tree containing warpmpm/vehicle.py")
    p.add_argument("--hull", default=str(CANONICAL_HULL))
    p.add_argument("--out", required=True)
    a = p.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    report = {"q1_canonical_driver": q1_canonical_driver_audit()}

    q1 = report["q1_canonical_driver"]
    print("=== Q1  canonical driver static audit ===", flush=True)
    print("  load_vehicle called at lines      : %s (%d calls, %d surface samples/run)"
          % (q1.get("load_vehicle_call_lines"), q1.get("n_load_vehicle_calls", 0),
             q1.get("surface_samples_drawn_per_run", 0)), flush=True)
    print("  np.random.seed before first load  : %s" % q1.get("seeded_before_first_load"),
          flush=True)
    print("  np.random.seed anywhere           : %s" % (q1.get("np_random_seed_lines") or "NONE"),
          flush=True)
    print("  default_rng (local generator)     : %s" % (q1.get("default_rng_lines") or "NONE"),
          flush=True)
    print("  builds an SDF                     : %s  (sdf refs: %s)"
          % (q1.get("builds_an_sdf"), q1.get("sdf_reference_lines") or "NONE"), flush=True)

    try:
        import trimesh
        veh, msdf = load_warpmpm_pieces(Path(a.src))
    except Exception as e:                                  # noqa: BLE001
        report["q2q3_error"] = "%s: %s" % (type(e).__name__, e)
        print("\nQ2/Q3 BLOCKED: %s" % report["q2q3_error"], flush=True)
        (out / "seeding_audit.json").write_text(json.dumps(report, indent=2))
        return

    hull = Path(a.hull)
    if not hull.exists():
        report["q2q3_error"] = "hull not found: %s" % hull
        print("\nQ2/Q3 BLOCKED: %s" % report["q2q3_error"], flush=True)
        (out / "seeding_audit.json").write_text(json.dumps(report, indent=2))
        return

    print("\n=== Q2/Q3  live load experiment on the canonical hull ===", flush=True)
    r = q2q3_load_experiment(veh, msdf, trimesh, hull)
    report["q2q3_load_experiment"] = r
    u, s, d = r["unseeded"], r["seeded_same"], r["seeded_different"]
    print("  vertices                          : %d" % r["n_vertices"], flush=True)
    print("  UNSEEDED, two back-to-back loads:", flush=True)
    print("    extent delta pre-canonicalize   : %s m"
          % ["%.3e" % q for q in u["extent_delta_pre_canonicalize_m"]], flush=True)
    print("    vertex delta pre-canonicalize   : %.6e m" % u["vertex_max_abs_delta_pre_canonicalize_m"], flush=True)
    print("    vertex delta post-canonicalize  : %.6e m  (= %.2f ULP at this magnitude)"
          % (u["vertex_max_abs_delta_post_canonicalize_m"], u["delta_in_ulps"]), flush=True)
    print("    vertices differing              : %d of %d"
          % (u["n_vertices_differing_post"], r["n_vertices"]), flush=True)
    print("    SDF cache keys                  : %s vs %s -> %s"
          % (u["sdf_cache_key_a"], u["sdf_cache_key_b"],
             "HIT" if u["cache_would_hit"] else "MISS, rebuild forced"), flush=True)
    print("    particle count stable           : %s (%d vs %d)"
          % (u["particle_count_stable"], u["n_particles_a"], u["n_particles_b"]), flush=True)
    print("  SEEDED with the same seed:", flush=True)
    print("    bitwise identical vertices      : %s" % s["bitwise_identical"], flush=True)
    print("    SDF cache keys                  : %s vs %s -> %s"
          % (s["sdf_cache_key_1"], s["sdf_cache_key_2"],
             "HIT" if s["cache_would_hit"] else "MISS"), flush=True)
    print("  SEEDED with different seeds (control, keys MUST differ):", flush=True)
    print("    keys differ                     : %s" % d["keys_differ_as_they_must"], flush=True)

    print("\n=== Q3  DIRECT seed-control test on mesh.sample(), with repeats ===", flush=True)
    q3 = q3_direct_seed_control(trimesh, hull)
    report["q3_direct_seed_control"] = q3
    print("  trimesh version                   : %s" % q3["trimesh_version"], flush=True)
    print("  np.random.seed reproduces sampling: %s  %s"
          % (q3["np_random_seed_reproduces"], q3["np_random_seed_detail"]), flush=True)
    print("  unseeded pair ever identical      : %s (must be False)"
          % q3["unseeded_ever_identical"], flush=True)
    print("  seed= kwarg supported and works   : %s" % q3["seed_kwarg_supported_and_works"],
          flush=True)

    print("\n=== Q4  demonstrated cache HIT once the sampling is genuinely seeded ===",
          flush=True)
    q4 = q4_demonstrate_cache_hit(veh, msdf, trimesh, hull)
    report["q4_demonstrated_cache_hit"] = q4
    print("  trimesh version                   : %s" % q4["trimesh_version"], flush=True)
    print("  3 seeded loads, distinct keys     : %d" % q4["n_distinct"], flush=True)
    print("  keys                              : %s" % q4["keys"], flush=True)
    print("  CACHE HIT DEMONSTRATED            : %s" % q4["cache_hits_after_first"], flush=True)

    verdict = {
        # Taken from the DIRECT repeated test, never from the single-pair load
        # comparison, which is degenerate: see q3_direct_seed_control's docstring.
        "np_random_seed_controls_trimesh_sampling": bool(q3["np_random_seed_reproduces"]),
        "seed_kwarg_available_and_works": bool(q3["seed_kwarg_supported_and_works"]),
        "seeded_sampling_gives_a_cache_hit": bool(q4["cache_hits_after_first"]),
        "canonical_driver_seeds_before_load": bool(q1.get("seeded_before_first_load")),
        "canonical_driver_builds_an_sdf": bool(q1.get("builds_an_sdf")),
    }
    verdict["sdf_rebuild_cost_applies_to_canonical_runs"] = bool(
        verdict["canonical_driver_builds_an_sdf"]
        and not verdict["canonical_driver_seeds_before_load"])
    report["verdict"] = verdict
    print("\n=== VERDICT ===", flush=True)
    for k, v in verdict.items():
        print("  %-46s %s" % (k, v), flush=True)

    (out / "seeding_audit.json").write_text(json.dumps(report, indent=2))
    print("\nWROTE %s" % (out / "seeding_audit.json"), flush=True)


if __name__ == "__main__":
    main()
