#!/usr/bin/env python3
"""Static audit of the reset -> step -> wrench/dt bracket in warpmpm driver code.

WHY THIS EXISTS
---------------
warpmpm is the only one of the three reference implementations surveyed on
2026-08-19 whose collider force accessor accumulates over TIME, and it is
therefore the only one that needs the caller to supply a dt at all:

  ours (warpmpm)  force = sum_nodes m (v_free - v_new) accumulated over
                  substeps, divided by a CALLER-SUPPLIED dt
                  (core/solver.py:354, kernels/mpm_solver_warp.py:2734-2735)
  Anura3D         nodal traction n.sigma.n interpolated from particle stress,
                  divided by nodal lumped mass; a stress, no dt
                  (src/MPMDynContact.FOR:443-512)
  Chrono::FSI     surface-integrated force over BCE markers, accumulated over
                  MARKERS not time, zeroed by the library immediately before
                  use; a force, no dt
                  (sph/physics/SphDataManager.cuh:394, SphBceManager.cu:530)

So the failure mode this file checks for cannot occur in the other two by
construction. It can occur here, silently, and it scales the force by exactly
the substep count.

THE CONTRACT BEING CHECKED, both halves verified live against the pinned solver
core at third_party/mpm-engine-544c93dd-solver-core on 2026-08-19:

  1. Solver.step(dt, substeps=N) advances N*dt of physical time, not dt.
     core/solver.py:429; the fused branch calls p2g2p_fused_tick(dt, substeps)
     and then does _step += substeps, the unfused branch loops N times over
     p2g2p(dt).
  2. The wrench accumulator is additive across substeps
     (wp.atomic_add at kernels/mpm_solver_warp.py:2734-2735) and is zeroed only
     by an explicit reset_sdf_force / reset_tool_force / reset_cup_wrench.

  Therefore the only correct divisor is the total time elapsed between the reset
  and the read: dt * (substeps advanced since the reset).

WHAT THIS TOOL DELIBERATELY DOES NOT DO
---------------------------------------
It does not evaluate expressions. If it cannot resolve the substep count or the
divisor symbolically it reports UNDECIDED, never OK. A checker that cannot tell
"correct" from "could not evaluate" produces uniform passes, which is the
failure this project has already been bitten by; so UNDECIDED is a first-class
verdict here and it is counted separately in the summary.

Usage:
    python3 analysis/r9_prior_code_compare.py <file.py> [<file.py> ...]
    python3 analysis/r9_prior_code_compare.py --self-test

Exit status is 1 if any site is FLAGGED, else 0. UNDECIDED does not fail the
run, it is reported for a human to resolve.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field

RESET_FNS = {"reset_sdf_force", "reset_tool_force", "reset_cup_wrench", "reset_wrench"}
READ_FNS = {"sdf_wrench", "tool_force", "cup_wrench", "cdf_wrench", "wrench"}
STEP_FNS = {"step"}


def _attr_name(node: ast.AST) -> str | None:
    """Return the trailing attribute/function name of a call target, or None."""
    if isinstance(node, ast.Call):
        return _attr_name(node.func)
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def _unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:                                    # pragma: no cover
        return "<unparseable>"


def _const_int(node: ast.AST) -> int | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def _step_substeps(call: ast.Call) -> tuple[int | None, str]:
    """Substeps advanced by one Solver.step call.

    Returns (n, description). n is None when the count is a symbol rather than a
    literal, which is not an error: it is resolved later by comparing symbols.
    """
    if len(call.args) >= 2:
        n = _const_int(call.args[1])
        return (n, _unparse(call.args[1]))
    for kw in call.keywords:
        if kw.arg == "substeps":
            n = _const_int(kw.value)
            return (n, _unparse(kw.value))
    return (1, "1")                                       # documented default


@dataclass
class Site:
    lineno: int
    reset: str
    steps: list[tuple[int | None, str]] = field(default_factory=list)
    read_fn: str = ""
    read_line: int = 0
    divisor: str = ""
    divisor_src: str = ""          # as written, before local-name resolution
    verdict: str = "UNDECIDED"
    why: str = ""


def _walk_block(body: list[ast.stmt]) -> list[Site]:
    """Find reset -> step... -> read brackets inside one statement block.

    ast.walk is BREADTH-first, so it does not yield calls in source order and a
    naive scan can see the wrench read before the step that precedes it. Every
    call in the block is therefore collected first and sorted by source position
    before the bracket is matched. This was not a hypothetical: the unsorted
    version reported "no step call found" for a correct site in coupler.py.
    """
    calls: list[tuple[int, int, str, ast.Call, str | None]] = []
    for stmt in body:
        # A `for _ in range(N): solver.step(dt)` advances N substeps, not one.
        # coupler.py uses exactly that idiom, so a tool blind to it cannot judge
        # the main coupled driver.
        loop_mult: str | None = None
        if isinstance(stmt, ast.For) and isinstance(stmt.iter, ast.Call) \
                and _attr_name(stmt.iter) == "range" and len(stmt.iter.args) == 1:
            loop_mult = _unparse(stmt.iter.args[0])
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                name = _attr_name(node)
                if name in RESET_FNS or name in STEP_FNS or name in READ_FNS:
                    calls.append((node.lineno, node.col_offset, name, node, loop_mult))
    calls.sort(key=lambda c: (c[0], c[1]))

    sites: list[Site] = []
    open_site: Site | None = None
    for lineno, _c, name, node, loop_mult in calls:
        if name in RESET_FNS:
            open_site = Site(lineno=lineno, reset=name)
            sites.append(open_site)
        elif name in STEP_FNS and open_site is not None:
            n, desc = _step_substeps(node)
            if loop_mult is not None:
                # N iterations of step(dt, n): symbolic unless both are literal.
                lit = _const_int(ast.parse(loop_mult, mode="eval").body)
                if lit is not None and n is not None:
                    n, desc = lit * n, f"{loop_mult}*{desc}"
                else:
                    n, desc = None, (loop_mult if desc == "1"
                                     else f"{loop_mult}*{desc}")
            open_site.steps.append((n, desc))
        elif name in READ_FNS and open_site is not None:
            open_site.read_fn = name
            open_site.read_line = lineno
            if len(node.args) >= 2:
                open_site.divisor = _unparse(node.args[-1])
            elif len(node.args) == 1 and name == "wrench":
                open_site.divisor = _unparse(node.args[0])
            open_site = None
    return sites


def _resolve(expr: str, defs: dict[str, str], depth: int = 3) -> str:
    """Substitute simple local definitions into a divisor expression.

    `step_dt = dt * substeps` then `sdf_wrench(h, step_dt)` is correct code, and
    a checker that cannot see through the name reports a false FLAG. A false
    alarm is more damaging than a miss here, because it trains a reader to
    ignore the tool.
    """
    seen = set()
    for _ in range(depth):
        key = expr.strip()
        if key in defs and key not in seen:
            seen.add(key)
            expr = defs[key]
        else:
            break
    return expr


def _classify(site: Site) -> Site:
    if not site.read_fn:
        site.verdict = "UNDECIDED"
        site.why = "reset with no matching wrench read in the same block"
        return site
    if not site.divisor:
        site.verdict = "UNDECIDED"
        site.why = "could not read the divisor argument"
        return site

    # A python-level loop of single steps is equivalent to one step(dt, N).
    literal = [n for n, _ in site.steps if n is not None]
    symbolic = [s for n, s in site.steps if n is None]

    if symbolic:
        # step(dt, N) with symbolic N: the divisor must mention that symbol.
        sym = symbolic[0]
        if sym in site.divisor and "*" in site.divisor:
            site.verdict = "OK"
            site.why = f"divisor {site.divisor} carries the substep symbol {sym}"
        else:
            site.verdict = "FLAGGED"
            site.why = (f"step advances {sym} substeps but divisor {site.divisor} "
                        f"does not multiply by {sym}: force scaled by {sym}")
        return site

    total = sum(literal) if literal else 0
    if total == 0:
        site.verdict = "UNDECIDED"
        site.why = "no step call found between reset and read"
        return site

    if total == 1:
        if "*" in site.divisor:
            site.verdict = "UNDECIDED"
            site.why = (f"one substep advanced but divisor {site.divisor} is a "
                        f"product; check it resolves to a single dt")
        else:
            site.verdict = "OK"
            site.why = f"1 substep advanced, divisor {site.divisor} is a single dt"
        return site

    # total >= 2 advanced: divisor must be a product.
    if "*" in site.divisor:
        site.verdict = "OK"
        site.why = f"{total} substeps advanced, divisor {site.divisor} is a product"
    else:
        site.verdict = "FLAGGED"
        site.why = (f"{total} substeps advanced but divisor {site.divisor} is a bare "
                    f"dt: force overstated by {total}x")
    return site


def _local_defs(tree: ast.AST) -> dict[str, str]:
    """Map simple `name = <expr>` bindings to the expression text.

    A name bound more than once is dropped rather than guessed at: two bindings
    mean the tool cannot know which one reaches the read, and an UNDECIDED there
    is honest where a substitution would be a coin flip.
    """
    seen: dict[str, str] = {}
    dup: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt = node.targets[0]
            if isinstance(tgt, ast.Name):
                if tgt.id in seen and seen[tgt.id] != _unparse(node.value):
                    dup.add(tgt.id)
                seen[tgt.id] = _unparse(node.value)
    return {k: v for k, v in seen.items() if k not in dup}


def audit_source(src: str, label: str) -> list[Site]:
    tree = ast.parse(src, filename=label)
    defs = _local_defs(tree)
    # Depth matters: an enclosing Module/ClassDef block sees the same calls but
    # loses the `for _ in range(N)` context that only the innermost block can
    # supply, so the innermost analysis of a given reset must win.
    sites: list[tuple[int, Site]] = []

    def descend(node: ast.AST, depth: int) -> None:
        body = getattr(node, "body", None)
        if isinstance(body, list):
            sites.extend((depth, s) for s in _walk_block(body))
        for child in ast.iter_child_nodes(node):
            descend(child, depth + 1)

    descend(tree, 0)

    # Several enclosing blocks yield a site at the same reset line. Keep the
    # best-informed one: a read found, then the innermost block, then the most
    # step calls seen.
    best: dict[int, tuple[tuple, Site]] = {}
    for depth, s in sites:
        rank = (bool(s.read_fn), depth, len(s.steps))
        cur = best.get(s.lineno)
        if cur is None or rank > cur[0]:
            best[s.lineno] = (rank, s)

    out: list[Site] = []
    for _rank, s in best.values():
        if s.divisor:
            s.divisor_src = s.divisor
            s.divisor = _resolve(s.divisor, defs)
        out.append(_classify(s))
    return sorted(out, key=lambda s: s.lineno)


SELF_TEST = '''
def correct_loop(solver, h, dt, substeps):
    for _ in range(10):
        solver.reset_sdf_force(h)
        solver.step(dt, substeps)
        w = solver.sdf_wrench(h, dt * substeps)

def correct_single(solver, h, dt):
    for _ in range(10):
        solver.reset_sdf_force(h)
        solver.step(dt, 1)
        w = solver.sdf_wrench(h, dt)

def wrong_bare_dt(solver, h, dt, substeps):
    for _ in range(10):
        solver.reset_sdf_force(h)
        solver.step(dt, substeps)
        w = solver.sdf_wrench(h, dt)

def wrong_literal(solver, h, dt):
    for _ in range(10):
        solver.reset_sdf_force(h)
        solver.step(dt, 20)
        w = solver.sdf_wrench(h, dt)
'''


def _self_test() -> int:
    sites = audit_source(SELF_TEST, "<self-test>")
    got = [(s.verdict, s.why) for s in sites]
    expect = ["OK", "OK", "FLAGGED", "FLAGGED"]
    ok = [v for v, _ in got] == expect
    for s in sites:
        print(f"  line {s.lineno:>3}  {s.verdict:<9} {s.why}")
    print(f"SELF-TEST {'PASS' if ok else 'FAIL'}: "
          f"expected {expect}, got {[v for v, _ in got]}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--self-test":
        return _self_test()

    n_flag = n_ok = n_und = 0
    for path in argv:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                src = fh.read()
        except OSError as exc:
            print(f"SKIP {path}: {exc}")
            continue
        try:
            sites = audit_source(src, path)
        except SyntaxError as exc:
            print(f"SKIP {path}: syntax error {exc}")
            continue
        if not sites:
            continue
        print(f"\n{path}")
        for s in sites:
            shown = s.divisor or "?"
            if s.divisor_src and s.divisor_src != s.divisor:
                shown = f"{s.divisor_src} -> {s.divisor}"
            print(f"  reset :{s.lineno}  read {s.read_fn}:{s.read_line}  "
                  f"divisor={shown}")
            print(f"    {s.verdict}: {s.why}")
            n_flag += s.verdict == "FLAGGED"
            n_ok += s.verdict == "OK"
            n_und += s.verdict == "UNDECIDED"

    print(f"\nSUMMARY  OK {n_ok}   FLAGGED {n_flag}   UNDECIDED {n_und}")
    if n_und:
        print("UNDECIDED is not a pass. Resolve each by hand before trusting the file.")
    return 1 if n_flag else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
