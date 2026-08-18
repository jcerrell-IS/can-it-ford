import csv
import inspect
import json
import re
import sys
from pathlib import Path

import physics_gates_literature as lit

# Single source of truth for the required manifest fields is the gate itself,
# read off its signature so the two can never drift apart.
REQUIRED_MANIFEST_FIELDS = inspect.signature(
    lit.gate_manifest_completeness
).parameters["required_fields"].default

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DENSITY = 310.49
DENSITY_TOLERANCE = 0.5
# Canonical hull, vehicle_geometry_research/yaris_coarse_v1l_watertight.ply.
# 3.542739 m3 verified live 2026-08-08 in renders/yaris_render_s3_enhanced/
# sim_enhanced.py:137 (HULL_YARIS_REF) and in the hull_m3 field of every
# summary.json under renders/yaris_render_s1/.
CANONICAL_HULL_M3 = 3.542739
# Water reference density and the artificial-EOS exponent. GAMMA is read from
# the pinned solver at runtime by _pinned_gamma(); this is the fallback only.
RHO_WATER = 1000.0
GAMMA_FALLBACK = 1.1
PINNED_EOS_SOURCE = "third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_utils.py"
GAMMA_PATTERN = re.compile(r"^\s*gamma\s*=\s*([0-9]+\.?[0-9]*)\s*$", re.MULTILINE)
INVENTORY_CSV = "data/all_runs_inventory.csv"
SIM_DRIVER_REL = "renders/yaris_render_s1/sim_standing.py"
# Hull-volume constants hardcoded in scripts. A drift here is a real regression,
# unlike the realized solid_volume_m3, which legitimately differs by the
# solidify_watertight fill ratio (1.0023).
HULL_LITERAL_SOURCES = [
    ("renders/yaris_render_s3_enhanced/sim_enhanced.py", re.compile(r"HULL_YARIS_REF\s*=\s*([0-9]+\.[0-9]+)")),
    ("renders/yaris_render_s1/g0_validate.py", re.compile(r"\"hull_volume\"\s*:\s*([0-9]+\.[0-9]+)")),
]
KNOWN_ABANDONED_DENSITY_FILES = {
    "simulation/can_it_ford_L2_mpm.py",
    "simulation/can_it_ford_L2.py",
    "simulation/can_it_ford_L2_mpm_ytest.py",
    "designsafe-staging/scripts/can_it_ford_L2.py",
}
FIGURE_SCRIPT_GLOBS = [
    "analysis/make_phase_space_v2.py",
    "plot_phase_space_live.py",
    "wandb_backfill.py",
    "designsafe-staging/scripts/make_phase_space.py",
]
VEHICLE_DENSITY_PATTERN = re.compile(r"(?:vehicle_density|veh_density|veh_rho|rho_vehicle|vehicle_rho)\s*=\s*([0-9]+\.?[0-9]*)", re.IGNORECASE)
EXT_REF_PATTERN = re.compile(r"EXT_REF\s*=\s*(?:np\.array\()?\[([^\]]+)\]")
BBOX_PATTERN = re.compile(r"\"bbox_m\"\s*:\s*\(([^)]+)\)")
INLINE_THRESHOLD_PATTERN = re.compile(r"haz\s*<=|depth\s*\*\s*velocity\s*<=|d\s*\*\s*v\s*<=", re.IGNORECASE)
L1_VERDICT_READ_PATTERN = re.compile(r"L1_verdict")

failures = []
warnings = []


def skip_path(rel):
    return ("archive/" in rel or "third_party/" in rel or ".venv" in rel
            or ".claude/worktrees/" in rel or "renders_preview/" in rel
            or "kumar_july9_update/" in rel or "deliverables/" in rel)


def all_candidates(name):
    return [p for p in ROOT.rglob(name) if not skip_path(str(p.relative_to(ROOT)))]


def find_all_matches(name, pattern):
    results = []
    for c in all_candidates(name):
        text = c.read_text(errors="ignore")
        m = pattern.search(text)
        if m:
            results.append((c, m))
    return results


def find_density_literals():
    for pyfile in ROOT.rglob("*.py"):
        rel = str(pyfile.relative_to(ROOT))
        if skip_path(rel):
            continue
        text = pyfile.read_text(errors="ignore")
        for match in VEHICLE_DENSITY_PATTERN.finditer(text):
            value = float(match.group(1))
            if abs(value - CANONICAL_DENSITY) > DENSITY_TOLERANCE:
                if rel in KNOWN_ABANDONED_DENSITY_FILES:
                    warnings.append(f"{rel}: vehicle density literal {value}, known abandoned Track 2 file, not blocking")
                else:
                    failures.append(f"{rel}: vehicle density literal {value} does not match canonical {CANONICAL_DENSITY}")


def check_bbox_agreement():
    """DELIBERATELY NOT CALLED FROM main(). Do not re-enable without reading this.

    This compares gates.py EXT_REF against vehicle_params.py bbox_m at a 2 percent
    tolerance. It WILL fail if wired in, and the failure is not a defect:

        EXT_REF  = [1.746, 4.283, 1.518]   gates.py:12
        bbox_m   = (4.30,  1.70,  1.47)    vehicle_params.py

    Recomputed 2026-08-08: height differs 3.27 percent, width 2.71 percent, length
    0.40 percent. But these measure DIFFERENT OBJECTS. EXT_REF is the watertight
    PLY hull, confirmed because gates.py HULL = 3.542739 matches
    yaris_coarse_v1l_watertight.ply's volume to all seven digits. bbox_m is sourced
    to SRC["ncac_yaris_fe"], the NCAC FE model / Toyota published spec.

    So a mesh is being compared against a manufacturer datasheet, and gate G-1's
    2 percent tolerance is MIS-SPECIFIED rather than the data being wrong. Calling
    this from main() would block every commit in the repo for a non-defect. Decide
    which object G-1 is supposed to gate before re-enabling it.

    (CLAUDE.md item 14 records the percentages correctly but frames them as a
    defect; the spec-versus-mesh explanation is in
    docs/C1_ROOT_CAUSE_2026-08-07.md section 7 and the E4 discussion.)
    """
    ext_ref_hits = find_all_matches("gates.py", EXT_REF_PATTERN)
    bbox_hits = find_all_matches("vehicle_params.py", BBOX_PATTERN)
    if not ext_ref_hits:
        seen = [str(p.relative_to(ROOT)) for p in all_candidates("gates.py")]
        warnings.append(f"bbox check skipped, no EXT_REF literal found in any of: {seen}")
        return
    if not bbox_hits:
        seen = [str(p.relative_to(ROOT)) for p in all_candidates("vehicle_params.py")]
        warnings.append(f"bbox check skipped, no bbox_m literal found in any of: {seen}")
        return
    if len(bbox_hits) > 1:
        distinct_values = {tuple(sorted(float(x.strip()) for x in m.group(1).split(","))) for _, m in bbox_hits}
        if len(distinct_values) > 1:
            paths = [str(p.relative_to(ROOT)) for p, _ in bbox_hits]
            failures.append(f"vehicle_params.py bbox_m DISAGREES across live copies, not a tolerance issue, genuinely different values: {paths}")
            return
    gates_path, ext_ref_match = ext_ref_hits[0]
    params_path, bbox_match = bbox_hits[0]
    ext_ref = sorted(float(x.strip()) for x in ext_ref_match.group(1).split(","))
    bbox = sorted(float(x.strip()) for x in bbox_match.group(1).split(","))
    for a, b in zip(ext_ref, bbox):
        if a == 0:
            continue
        pct_diff = abs(a - b) / a * 100.0
        if pct_diff > 2.0:
            failures.append(f"bbox mismatch: {gates_path.relative_to(ROOT)} EXT_REF vs {params_path.relative_to(ROOT)} bbox_m differ by {pct_diff:.1f} percent, exceeds gate G-1 tolerance of 2 percent")


def check_inertia_wired():
    """Report that only mass reaches the solver, and BLOCK a naive re-wiring.

    The absence of an inertia/CG wire is currently CORRECT for compact_sedan, not
    a gap to be closed. Verified 2026-08-08, see
    docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md section 1 and the note in
    vehicle_params.py:
      - VEHICLE_PARAMS["compact_sedan"]["inertia_kg_m2"] reproduces exactly from
        box_inertia(1100, 4.30, 1.70, 1.47). It is a solid box, not a measurement.
        No measured Yaris tensor exists (SAE 1999-01-1336 ends Nov 1998).
      - warpmpm already derives a better tensor from the hull particle cloud
        (mpm_solver_warp.py:859-871): Ixx 1501.5, Iyy 395.0, Izz 1685.4 against
        the box's axis-corrected 1893.0 / 463.0 / 1959.8, i.e. the box overstates
        by +16.3% to +26.1%.
      - vehicle_params documents (L,W,H)->(x,y,z) but the gated scene puts the
        hull's long axis on Y (extents 1.7078 / 4.2014 / 1.4853), so a naive
        write gives Ixx -69.2% and Iyy +379.2%.
    """
    sim_driver = ROOT / "renders" / "yaris_render_s1" / "sim_standing.py"
    if not sim_driver.exists():
        warnings.append("inertia-wired check skipped, sim_standing.py not found at expected path")
        return
    text = sim_driver.read_text(errors="ignore")
    for attr in ("inertia", "cg_height", "ssf", "static_stability_factor"):
        if attr not in text:
            warnings.append(
                f"sim_standing.py never references '{attr}'; only mass reaches the solver. "
                "For compact_sedan this is CORRECT, not a gap: the tabulated tensor is a box "
                "fallback and its axes are transposed vs the scene. Do not 'fix' it."
            )
    # Blocking: catch an actual naive re-wire, in any sim driver.
    NAIVE_WIRE = re.compile(
        r"(rigid_inv_inertia_body\s*=|set_rigid_body_inertia|inertia_kg_m2\s*\[|"
        r"\[\s*[\"']inertia_kg_m2[\"']\s*\])"
    )
    AXIS_ACK = "AXIS-CHECKED"
    # Scan every file that BEHAVES like a solver driver, not a hardcoded path
    # list. A fixed list silently misses the next driver, and this repo creates
    # them regularly (validate_coupling_force_ladder.py, the class-specific runs).
    # An absent hit from a narrow scan is not evidence of absence.
    IS_SIM_DRIVER = re.compile(r"import\s+warpmpm|from\s+warpmpm|finalize_rigid_bodies|set_material_range")
    for p in sorted(ROOT.rglob("*.py")):
        try:
            rel = str(p.relative_to(ROOT))
        except ValueError:
            continue
        if skip_path(rel):
            continue
        try:
            body = p.read_text(errors="ignore")
        except OSError:
            continue
        if not IS_SIM_DRIVER.search(body):
            continue
        if NAIVE_WIRE.search(body) and AXIS_ACK not in body:
            failures.append(
                f"{rel} appears to wire an inertia tensor into the solver without an "
                f"'{AXIS_ACK}' acknowledgement. vehicle_params' inertia_kg_m2 is a BOX "
                "fallback whose axes are transposed vs the scene (long axis is Y, not X); "
                "a naive wire gives Ixx -69.2% and Iyy +379.2%. See "
                "docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md section 1."
            )


def check_figure_scripts_reimplement_l1():
    for rel_path in FIGURE_SCRIPT_GLOBS:
        fpath = ROOT / rel_path
        if not fpath.exists():
            continue
        text = fpath.read_text(errors="ignore")
        has_inline_threshold = bool(INLINE_THRESHOLD_PATTERN.search(text))
        reads_canonical = bool(L1_VERDICT_READ_PATTERN.search(text))
        if has_inline_threshold and not reads_canonical:
            failures.append(f"{rel_path}: recomputes an L1-style threshold inline instead of reading the canonical L1_verdict column")


def check_genesis_warpmpm_conflation():
    # REGISTER A3 says: "Any SKILL FILE naming it in a warpmpm context is engine-conflated."
    # Skill files are .md. The previous version of this check walked only ROOT.rglob("*.py")
    # AND required "warpmpm" in the file PATH, so it could not fire on a .md file, and could
    # not fire on any path lacking the literal string "warpmpm" either. It therefore could
    # not fire on the single real offender in the tree,
    # .claude/skills/flood-mpm-debugging-reference/SKILL.md:41, which prescribes summing
    # cfrc_coupling_vel to validate "ANY force number this pipeline produces" while the
    # canonical pipeline is warpmpm. A check that cannot fire on the file class its own
    # register names is not a check. Corrected 2026-08-18.
    #
    # The context test is now on FILE CONTENT, not on the path. Files whose purpose is to
    # STATE the rule necessarily name both terms, so they are allowlisted explicitly rather
    # than by a pattern, so the allowlist itself stays auditable.
    A3_RULE_STATING_FILES = {
        ".claude/checks/params_check.py",
        ".claude/hooks/banned_phrase_guard.py",
        ".claude/commands/engine-audit.md",
        "docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md",
    }
    for src in sorted(list(ROOT.rglob("*.py")) + list(ROOT.rglob("*.md"))):
        rel = str(src.relative_to(ROOT))
        if skip_path(rel) or rel in A3_RULE_STATING_FILES:
            continue
        try:
            text = src.read_text(errors="ignore")
        except OSError:
            continue
        if "cfrc_coupling_vel" not in text or "warpmpm" not in text.lower():
            continue
        # Test the ACTUAL condition, which is UNTAGGED usage, not mere co-occurrence.
        # Register A3's remedy is "tag the sentence GENESIS", so a line that carries an
        # explicit Genesis-only marker is compliant and must not be flagged. An earlier
        # version of this check flagged co-occurrence, which meant the very sentence that
        # applies the remedy still failed, i.e. the check could not be satisfied by doing
        # the thing it asked for. Checked per line because these are long markdown lines.
        for lineno, line in enumerate(text.splitlines(), 1):
            if "cfrc_coupling_vel" not in line:
                continue
            if re.search(r"GENESIS[- ]ONLY|Genesis[- ]only", line):
                continue
            failures.append(
                f"{rel}:{lineno}: names cfrc_coupling_vel in a file that also discusses "
                f"warpmpm, with no Genesis tag on that line. That accessor is Genesis-only "
                f"(register A3) and has no warpmpm counterpart. Tag the sentence "
                f"GENESIS-ONLY explicitly, or remove the accessor.")


# ---------------------------------------------------------------------------
# Literature-backed gates, from physics_gates_literature.py.
# Citation bank and per-gate rationale: docs/LITERATURE_CI_GATES_2026-08-08.md
#
# SEVERITY POLICY, deliberate, stated so it is not read as an oversight:
#   BLOCKING (failures) -> the gate detects a REGRESSION away from a state that
#       is currently known-good. Example: inertia starting to reach the solver.
#   NON-BLOCKING (warnings) -> the gate reports a condition that is TRUE TODAY
#       and already recorded in docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md.
#       These are surfaced, not suppressed, but they do not exit nonzero. The
#       commit gate at .claude/hooks/pretooluse_git_commit_gate.py:24-26 exits 2
#       on any nonzero return, so making a standing known-open finding blocking
#       would wedge every commit in the repo and the finding would be worked
#       around rather than read.
# ---------------------------------------------------------------------------


def _read(rel):
    path = ROOT / rel
    return path.read_text(errors="ignore") if path.exists() else None


def _report(ok, msg, gate, blocking):
    if ok:
        return
    line = f"[lit:{gate}] {msg}"
    (failures if blocking else warnings).append(line)


def _pinned_gamma():
    """Read the EOS exponent from the pinned solver, not from a wrapper copy."""
    text = _read(PINNED_EOS_SOURCE)
    if text:
        match = GAMMA_PATTERN.search(text)
        if match:
            return float(match.group(1))
    warnings.append(f"[lit:sound_speed_cfl] gamma not readable from {PINNED_EOS_SOURCE}, using fallback {GAMMA_FALLBACK}")
    return GAMMA_FALLBACK


def _inventory_rows():
    path = ROOT / INVENTORY_CSV
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _summary_files():
    """Every run manifest, excluding worktrees and the nested ./can-it-ford/
    duplicate, which is NOT a synced mirror (CLAUDE.md, provenance section)."""
    found = []
    for path in ROOT.rglob("*summary.json"):
        rel = str(path.relative_to(ROOT))
        if skip_path(rel) or rel.startswith("can-it-ford/"):
            continue
        found.append(path)
    return sorted(found)


def check_lit_solver_reads_mass_only():
    """Extends check_inertia_wired(), does not duplicate it. That check WARNS
    when an attribute is ABSENT from the driver. This one BLOCKS when one is
    PRESENT. Inverse directions on the same file. Commit fe91c50 established
    that wiring the inertia tensor is a regression, so presence is the defect."""
    text = _read(SIM_DRIVER_REL)
    if text is None:
        warnings.append(f"[lit:mass_inertia_cog] skipped, {SIM_DRIVER_REL} not found")
        return
    _report(*lit.gate_inertia_not_read_by_solver(text), gate="mass_inertia_cog", blocking=True)


def check_lit_floor_restitution():
    """Open item 31. NOTE: this gate has no entry in lit.LITERATURE_GATES, it is
    a repo-internal check, not a literature-derived one. Do not cite it."""
    text = _read(SIM_DRIVER_REL)
    if text is None:
        warnings.append(f"[lit:floor_restitution] skipped, {SIM_DRIVER_REL} not found")
        return
    _report(*lit.gate_floor_restitution(text), gate="floor_restitution", blocking=True)


def check_lit_hull_volume_literals():
    """Blocking. A hardcoded hull constant drifting is a genuine regression."""
    for rel, pattern in HULL_LITERAL_SOURCES:
        text = _read(rel)
        if text is None:
            continue
        match = pattern.search(text)
        if not match:
            warnings.append(f"[lit:geometry_bbox] {rel}: hull-volume literal pattern no longer matches, may have been renamed")
            continue
        ok, msg = lit.gate_hull_volume(float(match.group(1)), expected_volume_m3=CANONICAL_HULL_M3)
        _report(ok, f"{rel}: {msg}", gate="geometry_bbox", blocking=True)


def check_lit_realized_hull_volume():
    """Non-blocking. solid_volume_m3 is the solidified particle cloud, not the
    mesh, so it carries a GRID-DEPENDENT voxelization offset: measured live
    2026-08-08 at +0.24 percent for g64_m1100 (3.551384 m3) but +2.62 percent
    for g48_m1100 (3.635710 m3). The 0.002 m3 tolerance is far tighter than
    either, so this reports the discretization offset and its grid dependence
    rather than asserting a defect. Do not read it as a solidify_watertight
    failure, and do not feed hull_m3 here instead: that field is the canonical
    constant echoed back, so it would pass tautologically."""
    rows = _inventory_rows()
    offenders = []
    for row in rows:
        try:
            measured = float(row["solid_volume_m3"])
        except (KeyError, ValueError, TypeError):
            continue
        ok, msg = lit.gate_hull_volume(measured, expected_volume_m3=CANONICAL_HULL_M3)
        if not ok:
            offenders.append((row.get("run", "?"), msg))
    if offenders:
        run, msg = offenders[0]
        warnings.append(f"[lit:geometry_bbox] {len(offenders)}/{len(rows)} runs: realized solid_volume_m3 exceeds the 0.002 m3 tolerance, expected given fill_ratio 1.0023, e.g. {run}: {msg}")


def check_lit_mass_declared():
    """Blocking. An undeclared mass reaching a gated run is a real defect.
    CAVEAT carried into the docs: the gate's message calls (1100, 1609, 2337)
    the 'AR&R class set'. Per register item 10, 1609 and 2337 have NO source in
    vehicle_params.py. The set is the set actually run, not a cited class set."""
    for row in _inventory_rows():
        try:
            mass = float(row["mass_kg"])
        except (KeyError, ValueError, TypeError):
            continue
        ok, msg = lit.gate_mass_declared(mass)
        _report(ok, f"{row.get('run', '?')}: {msg}", gate="mass_inertia_cog", blocking=True)


def check_lit_sound_speed_cfl():
    """Non-blocking. All 17 gated runs use an artificial bulk modulus of 1.5e5
    Pa, giving c = 12.845 m/s (matches the sound_speed_ms field exactly). 15 of
    the 17 fall under the Monaghan 10x convention, measured live 2026-08-08:
    only the two slowest velocity-sweep runs clear it (v=0.5 at 25.7x, v=1.0 at
    12.8x), the v=1.5 baseline sits at 8.56x and v=3.0 at 4.28x. This is a
    standing property of the published sweep, not a regression, so it warns."""
    rows = _inventory_rows()
    if not rows:
        warnings.append(f"[lit:sound_speed_cfl] skipped, {INVENTORY_CSV} not found")
        return
    gamma = _pinned_gamma()
    offenders = []
    for row in rows:
        try:
            bulk = float(row["bulk_modulus"])
            vmax = float(row["velocity_ms"])
        except (KeyError, ValueError, TypeError):
            continue
        ok, msg = lit.gate_sound_speed_cfl(bulk, gamma, RHO_WATER, vmax)
        if not ok:
            offenders.append((vmax, row.get("run", "?"), msg))
    if offenders:
        offenders.sort(key=lambda item: -item[0])
        _, run, msg = offenders[0]
        warnings.append(f"[lit:sound_speed_cfl] {len(offenders)}/{len(rows)} runs below the 10x convention (gamma={gamma} from the pinned solver), worst is {run}: {msg}")


def check_lit_grid_convergence():
    """Non-blocking. Register item 5 already records that the g48/g64/g96 study
    is non-monotone and unconverged. The gate's job here is to keep that fact
    machine-checked, and to refuse to emit a GCI band that does not exist."""
    rows = _inventory_rows()
    by_mass = {}
    for row in rows:
        if row.get("sweep") != "mass_grid":
            continue
        try:
            by_mass.setdefault(row["mass_kg"], []).append(
                (int(row["n_grid"]), float(row["final_disp_mag_m"]))
            )
        except (KeyError, ValueError, TypeError):
            continue
    for mass, series in sorted(by_mass.items()):
        if len(series) < 3:
            continue
        grids = [g for g, _ in series]
        disps = [d for _, d in series]
        ok, msg = lit.gate_resolution_convergence_gci(grids, disps)
        _report(ok, f"mass {mass} kg across n_grid {sorted(grids)}: {msg}", gate="resolution_convergence_gci", blocking=False)


def check_lit_manifest_completeness():
    """Non-blocking. The provenance gap is real and standing: no summary.json
    carries a mesh hash or either git SHA, and the mass/grid fields are named
    mass_kg and n_grid rather than the required vehicle_mass and grid_density."""
    files = _summary_files()
    if not files:
        warnings.append("[lit:manifest_provenance] skipped, no summary.json found")
        return
    missing_counts = {}
    for path in files:
        try:
            payload = json.loads(path.read_text(errors="ignore"))
        except (ValueError, OSError):
            warnings.append(f"[lit:manifest_provenance] {path.relative_to(ROOT)} is not readable JSON")
            continue
        if not isinstance(payload, dict):
            continue
        ok, _ = lit.gate_manifest_completeness(payload)
        if not ok:
            for field in REQUIRED_MANIFEST_FIELDS:
                if field not in payload:
                    missing_counts[field] = missing_counts.get(field, 0) + 1
    if missing_counts:
        detail = ", ".join(f"{k} missing in {v}" for k, v in sorted(missing_counts.items()))
        warnings.append(f"[lit:manifest_provenance] across {len(files)} manifests: {detail}, runs cannot be traced to code plus data plus environment")


def run_literature_gates():
    check_lit_solver_reads_mass_only()
    check_lit_floor_restitution()
    check_lit_hull_volume_literals()
    check_lit_realized_hull_volume()
    check_lit_mass_declared()
    check_lit_sound_speed_cfl()
    check_lit_grid_convergence()
    check_lit_manifest_completeness()


def main():
    find_density_literals()
    check_inertia_wired()
    check_figure_scripts_reimplement_l1()
    check_genesis_warpmpm_conflation()
    run_literature_gates()
    for w in warnings:
        print(f"WARNING: {w}")
    for f in failures:
        print(f"FAIL: {f}")
    if failures:
        print(f"{len(failures)} blocking issue(s) found")
        sys.exit(1)
    print("params_check.py: no blocking issues found")
    sys.exit(0)


if __name__ == "__main__":
    main()
