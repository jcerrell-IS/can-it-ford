#!/usr/bin/env python3
"""
check_claims.py  mechanical guard against claims this project has already refuted.

WHY THIS EXISTS
    CLAUDE.md plus the corrections register run to several hundred lines whose
    entire job is stopping a retired number from being restated as fact. That
    only works if every author, human or model, reads all of it every time.
    This file turns the subset that is pattern-matchable into a check that
    fails loudly instead.

    It is deliberately NOT a physics validator and NOT a citation checker. It
    answers one narrow question: does this text repeat something the project
    has already proven wrong, or state a forked value as if it were canonical?

WHY THE DEFAULT IS --staged
    This repo IS a correction archive. Sweeping every tracked file produces
    hundreds of hits on CLAUDE.md, the register, and the skills, because those
    documents quote the wrong number in order to retire it. Quoting to correct
    is legitimate. What is worth blocking is a NEW line entering history, so
    the default scope is the git index, and the full sweep is opt-in.

WHAT IT CANNOT DO
    A rule needs a stable surface form. Claims like "the mass sweep spans
    cited vehicle classes" are refuted (CLAUDE.md item 10) but phrased a
    hundred ways, so they stay prose-only. Absence of a hit is not proof a
    passage is correct.

USAGE
    scripts/check_claims.py                 # added lines in the git index
    scripts/check_claims.py paper/foo.tex   # specific files
    scripts/check_claims.py --all           # every tracked .md/.py/.tex/.bib
    scripts/check_claims.py --list          # show the rule table

EXIT: 0 clean | 1 at least one ERROR | 2 usage
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Never in scope. Historical or duplicated by definition.
EXCLUDE = (
    "can-it-ford/",                 # nested non-mirror duplicate, CLAUDE.md
    "third_party/",
    ".git/",
    "docs/VERIFIED_FACTS_LEDGER",   # demoted to historical 2026-08-06
    "data/track1_sweep_v2/",        # deprecated box-proxy sweep
    "scripts/check_claims.py",      # this file quotes every pattern verbatim
)

# Out of scope for --all only. These are the correction layer: their job is to
# state the retired claim next to its refutation. In --staged mode they stay in
# scope, because a NEW wrong line in CLAUDE.md is still a new wrong line.
CORRECTION_LAYER = (
    "CLAUDE.md",
    "docs/CANONICAL_CORRECTIONS_REGISTER",
    "PROVISIONAL_STATUS.md",
)

ERROR, WARN = "ERROR", "WARN"


@dataclass
class Rule:
    rid: str
    severity: str
    pattern: str
    message: str
    authority: str
    # If set, the line must ALSO match this OUTSIDE the primary match, so bare
    # numbers do not fire everywhere they legitimately appear.
    context: str | None = None
    _p: re.Pattern = field(init=False, repr=False)
    _c: re.Pattern | None = field(init=False, repr=False)

    def __post_init__(self):
        self._p = re.compile(self.pattern, re.I)
        self._c = re.compile(self.context, re.I) if self.context else None

    def hits(self, line: str) -> bool:
        m = self._p.search(line)
        if not m:
            return False
        if self._c is None:
            return True
        # Context must be satisfied by text OUTSIDE the match. Otherwise a rule
        # like gates_results.json + context "result" is self-satisfying and
        # fires on every mention, including correct ones.
        rest = line[:m.start()] + " " + line[m.end():]
        return bool(self._c.search(rest))


RULES: list[Rule] = [
    Rule("C1", ERROR,
         r"\b100\s*(?:-|–|to)\s*300\b",
         "The 100-300 kg/m^3 vehicle density band is STALE. The canonical Yaris "
         "hull is 310.494 kg/m^3, and all 17 gated runs realise 302.55-663.58, "
         "every one above the band.",
         "CLAUDE.md Multi-Pane Standing Rules; item 9",
         context=r"densit|rho|kg\s*/?\s*m\^?3|band"),

    Rule("C2", ERROR,
         r"\b(?:2\.17|2\.18x|7\.71|143(?:\.0)?\s*kg)",
         "Retired by solidify_watertight: fill_ratio is 1.0023 and rho 309.78, "
         "not 2.17/2.18x/7.71 m^3/143 kg/m^3.",
         "memory solidify-watertight-supersedes-column-fill",
         context=r"fill[_ ]?ratio|densit|rho|volume|m\^?3"),

    Rule("C3", ERROR,
         r"grid[_ ]?densit\w*\s*(?:>=|≥|of|at)?\s*96|\bgd\s*(?:>=|≥)\s*96",
         "grid_density >= 96 is NOT the crash threshold. Replicated bisection "
         "2026-08-05: gd 80 and 88 pass 3/3 at 60 steps, gd 90+ fails, "
         "non-monotone above the boundary and non-deterministic at fixed config.",
         "CLAUDE.md; register section C2",
         context=r"threshold|crash|onset|boundary"),

    Rule("C4", ERROR,
         r"\b(?:gd|grid[_ ]?densit\w*)\s*(?:=|of|at)?\s*64\b",
         "grid_density 64 is NOT confirmed safe, and gd=64 runs carry 21-31% of "
         "water particles inside the vehicle. 'It runs' is not 'it is correct'.",
         "CLAUDE.md; memory gd64-runs-have-heavy-particle-passthrough",
         context=r"\bsafe\b|confirmed|known[- ]good|validated|stable"),

    Rule("C5", ERROR,
         r"\bgenesis\b",
         "The 17 gated runs are warpmpm via renders/yaris_render_s1/sim_standing.py, "
         "NOT Genesis. Genesis is only the Track 2 box-proxy path, and no Genesis "
         "scene has ever loaded the Yaris hull.",
         "CLAUDE.md August 4 audit item 1",
         context=r"17\s*(?:gated\s*)?runs?|gated\s*runs?|sim_standing|yaris_render_s1"),

    Rule("C6", WARN,
         r"9\.80665",
         "9.80665 appears only at failure_modes.py:14, a 0.034% fork. The solver "
         "and gates_all_runs.py use 9.81. Use 9.81; that script was never wired "
         "into the 17-run pipeline, so 9.80665 never influenced a gated result.",
         "CLAUDE.md item 3 and item 12; register A2 and D6",
         context=None),

    Rule("C7", ERROR,
         r"\b(?:115\.7|579\.06)\b",
         "Forked vehicle density. 115.7 (can_it_ford_L2_mpm.py:27) and 579.06 "
         "(can_it_ford_L2.py:44) are two of four incompatible live values. The "
         "canonical Yaris hull figure is 310.494 kg/m^3.",
         "CLAUDE.md item 9",
         context=r"densit|rho|kg\s*/?\s*m\^?3"),

    Rule("C8", ERROR,
         r"drift[_ ]?threshold",
         "DRIFT_THRESHOLD 0.05 m has NO peer-reviewed source and is declared as a "
         "literal in 16 places under four names. Do not cite it as sourced.",
         "CLAUDE.md item 13; gates.py:195-196",
         context=r"peer[- ]review|\bcited\b|literature|standard|established|sourced"),

    Rule("C9", ERROR,
         r"xia\W{0,20}(?:et\s*al\.?\s*)?\W{0,6}2013",
         "Xia is 2014, not 2013. Four authors including Yejiang Wang, print year 2014.",
         "memory xia-2014-not-2013-citation-trap",
         context=None),

    Rule("C10", ERROR,
         r"failure_modes_result\.json",
         "failure_modes_result.json has no run identifier and is written by no "
         "script in the repo. It CANNOT be independent confirmation of anything.",
         "CLAUDE.md item 12",
         context=r"confirm|independent|corroborat|verif"),

    Rule("C11", ERROR,
         r"gates_results\.json",
         "gates_results.json holds 3 dry_start records and is NOT a 17-run store, "
         "and stores no pass/fail field. The 17-run stores are "
         "gates_results_all_runs.json and data/all_runs_inventory.csv.",
         "CLAUDE.md item 8",
         context=r"\b17\b|all\s*runs|verdict"),

    Rule("C12", WARN,
         r"\b(?:1609|2337)\s*kg\b",
         "1609 kg and 2337 kg have no source in vehicle_params.py. Do not describe "
         "the mass sweep as spanning cited vehicle classes.",
         "CLAUDE.md item 10",
         context=r"class|cited|sourced|NHTSA|represent"),

    Rule("C13", ERROR,
         r"physics\s+validation|validates?\s+the\s+physics|externally\s+validat",
         "No gate is a physics validation. Every gate is a self-consistency or "
         "numerical-containment check; G-3 compares against a constant derived "
         "from the same pipeline, and G-6/P-4/P-5 have no pass criterion at all.",
         "CLAUDE.md item 6",
         context=r"gate|G-\d|P-\d"),

    Rule("C14", WARN,
         r"\bconverged\b|\bconvergence\s+(?:is\s+)?(?:achieved|demonstrated|shown)",
         "The grid study is non-monotone and UNCONVERGED: final_disp_mag_m moves "
         "+87.8% g48->g64 then -59.2% g64->g96 at 1100 kg. Cite the binary verdict, "
         "never the displacement magnitude.",
         "CLAUDE.md item 5; L-5 Steffen et al. 2008",
         context=r"\bgrid\b|\bmesh\b|g48|g64|g96|resolution"),
]


def iter_targets(argv: list[str]) -> list[tuple[Path, list[tuple[int, str]]]]:
    """Return [(path, [(lineno, text), ...])] for whatever was requested."""
    explicit = [Path(a) for a in argv if not a.startswith("-")]
    full = "--all" in argv

    if not explicit and not full:
        diff = subprocess.run(
            ["git", "diff", "--cached", "--unified=0", "--no-color"],
            cwd=REPO, capture_output=True, text=True).stdout
        out: dict[str, list[tuple[int, str]]] = {}
        cur, lineno = None, 0
        for ln in diff.splitlines():
            if ln.startswith("+++ b/"):
                cur = ln[6:]
            elif ln.startswith("@@"):
                m = re.search(r"\+(\d+)", ln)
                lineno = int(m.group(1)) if m else 0
            elif ln.startswith("+") and not ln.startswith("+++") and cur:
                out.setdefault(cur, []).append((lineno, ln[1:]))
                lineno += 1
        return [(Path(k), v) for k, v in out.items()]

    paths = explicit
    if full:
        tracked = subprocess.run(["git", "ls-files"], cwd=REPO,
                                 capture_output=True, text=True).stdout.split()
        paths = [Path(p) for p in tracked
                 if p.endswith((".md", ".py", ".tex", ".bib"))]

    res = []
    for p in paths:
        fp = p if p.is_absolute() else REPO / p
        if not fp.is_file():
            continue
        try:
            lines = fp.read_text(errors="replace").splitlines()
        except OSError:
            continue
        res.append((p, list(enumerate(lines, 1))))
    return res


def main(argv: list[str]) -> int:
    if "--list" in argv:
        print(f"{'id':5} {'sev':6} {'authority':44} message")
        for r in RULES:
            print(f"{r.rid:5} {r.severity:6} {r.authority[:44]:44} {r.message[:76]}")
        return 0

    full = "--all" in argv
    staged = not full and not [a for a in argv if not a.startswith("-")]
    scope = "staged index" if staged else ("all tracked files" if full else "named files")
    print(f"check_claims: scope = {scope}")

    errors = warns = 0
    for path, lines in iter_targets(argv):
        sp = str(path)
        if any(x in sp for x in EXCLUDE):
            continue
        if full and any(x in sp for x in CORRECTION_LAYER):
            continue
        for lineno, text in lines:
            if len(text) > 2000:
                continue
            for rule in RULES:
                if rule.hits(text):
                    if rule.severity == ERROR:
                        errors += 1
                    else:
                        warns += 1
                    print(f"\n{rule.severity} [{rule.rid}] {sp}:{lineno}")
                    print(f"    {text.strip()[:160]}")
                    print(f"    -> {rule.message}")
                    print(f"    authority: {rule.authority}")

    print(f"\n{'=' * 70}")
    print(f"check_claims: {errors} ERROR, {warns} WARN  ({scope})")
    if errors or warns:
        print("A hit is not automatically a defect: quoting a refuted claim in order")
        print("to correct it is legitimate. Read the line before changing it.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
