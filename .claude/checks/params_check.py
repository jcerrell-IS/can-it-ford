import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DENSITY = 310.49
DENSITY_TOLERANCE = 0.5
KNOWN_ABANDONED_DENSITY_FILES = {
    "simulation/can_it_ford_L2_mpm.py",
    "simulation/can_it_ford_L2.py",
    "simulation/can_it_ford_L2_mpm_ytest.py",
}
FIGURE_SCRIPT_GLOBS = [
    "analysis/make_phase_space_v2.py",
    "plot_phase_space_live.py",
    "wandb_backfill.py",
    "designsafe-staging/scripts/make_phase_space.py",
]
DENSITY_PATTERN = re.compile(r"(?:rho|density)\s*=\s*([0-9]+\.?[0-9]*)", re.IGNORECASE)
INLINE_THRESHOLD_PATTERN = re.compile(r"haz\s*<=|depth\s*\*\s*velocity\s*<=|d\s*\*\s*v\s*<=", re.IGNORECASE)
L1_VERDICT_READ_PATTERN = re.compile(r"L1_verdict")

failures = []
warnings = []


def skip_path(rel):
    return "archive/" in rel or "third_party/" in rel or ".venv" in rel


def find_density_literals():
    for pyfile in ROOT.rglob("*.py"):
        rel = str(pyfile.relative_to(ROOT))
        if skip_path(rel):
            continue
        text = pyfile.read_text(errors="ignore")
        for match in DENSITY_PATTERN.finditer(text):
            value = float(match.group(1))
            if abs(value - CANONICAL_DENSITY) > DENSITY_TOLERANCE:
                if rel in KNOWN_ABANDONED_DENSITY_FILES:
                    warnings.append(f"{rel}: density literal {value}, known abandoned Track 2 file, not blocking")
                else:
                    failures.append(f"{rel}: density literal {value} does not match canonical {CANONICAL_DENSITY}")


def check_bbox_agreement():
    gates = ROOT / "simulation" / "gates.py"
    params = ROOT / "vehicle_params.py"
    if not gates.exists() or not params.exists():
        warnings.append("bbox check skipped, gates.py or vehicle_params.py not found at expected path")
        return
    gates_text = gates.read_text(errors="ignore")
    params_text = params.read_text(errors="ignore")
    ext_ref_match = re.search(r"EXT_REF\s*=\s*\[([^\]]+)\]", gates_text)
    bbox_match = re.search(r"bbox_m\s*=\s*\(([^)]+)\)", params_text)
    if not ext_ref_match or not bbox_match:
        warnings.append("bbox check skipped, EXT_REF or bbox_m pattern not found, may have changed")
        return
    ext_ref = sorted(float(x.strip()) for x in ext_ref_match.group(1).split(","))
    bbox = sorted(float(x.strip()) for x in bbox_match.group(1).split(","))
    for a, b in zip(ext_ref, bbox):
        if a == 0:
            continue
        pct_diff = abs(a - b) / a * 100.0
        if pct_diff > 2.0:
            failures.append(f"bbox mismatch: gates.py EXT_REF vs vehicle_params.py bbox_m differ by {pct_diff:.1f} percent, exceeds gate G-1 tolerance of 2 percent")


def check_inertia_wired():
    sim_driver = ROOT / "renders" / "yaris_render_s1" / "sim_standing.py"
    if not sim_driver.exists():
        warnings.append("inertia-wired check skipped, sim_standing.py not found at expected path")
        return
    text = sim_driver.read_text(errors="ignore")
    for attr in ("inertia", "cg_height", "ssf", "static_stability_factor"):
        if attr not in text:
            warnings.append(f"sim_standing.py never references '{attr}', only mass reaches the solver, known standing gap")


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
    for pyfile in ROOT.rglob("*.py"):
        rel = str(pyfile.relative_to(ROOT))
        if skip_path(rel):
            continue
        text = pyfile.read_text(errors="ignore")
        if "cfrc_coupling_vel" in text and "warpmpm" in rel.lower():
            failures.append(f"{rel}: references cfrc_coupling_vel, that accessor is Genesis-only, does not exist in warpmpm")


def main():
    find_density_literals()
    check_bbox_agreement()
    check_inertia_wired()
    check_figure_scripts_reimplement_l1()
    check_genesis_warpmpm_conflation()
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
