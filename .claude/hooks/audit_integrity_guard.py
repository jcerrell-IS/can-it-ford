#!/usr/bin/env python3
"""
PreToolUse guard for two documented, repeated, audit-invalidating failure modes.

Wired for Bash and Edit. Emits a structured permissionDecision so Josie stays in
the loop rather than being hard-blocked out of a search she meant to run.

CHECK 1, grep scope. Register H0.
    grep in this environment is a shell function wrapping ugrep with --ignore-files,
    so it SKIPS EVERY GITIGNORED PATH. .gitignore:14 is renders/ and :10 is data/*.
    A repo-wide `grep -rn "pattern" .` therefore silently omits
    renders/yaris_render_s1/ (sim_standing.py, vehicle_live.py, gates.py,
    gates_all_runs.py, gates_both_scenarios.py and all 17 runs' metrics.csv) and
    most of data/. Measured on the gravity inventory: 5 hits from `.` against 7
    when renders/ was named explicitly, and the two missing hits were both
    load-bearing. An absent hit is NOT evidence of absence.
    This check asks for confirmation on a recursive search that is scoped to the
    repo root, does not use /usr/bin/grep, and does not name renders/ or data/.

CHECK 2, threshold deduplication by value. Register D7a.
    simulation/failure_modes.py carries THREE 0.05 literals and one is not a
    distance:
        :46  slide_m         0.05  metres
        :47  slide_speed_ms  0.05  METRES PER SECOND
        :48  float_m         0.05  metres
    slide_speed_ms participates in the joint sustained condition at
    failure_modes.py:179-185 that produces the published 16 SLIDE / 1 STUCK
    verdicts. A find-and-replace on the value 0.05 silently converts a speed
    threshold into a distance threshold and changes published output without
    raising an error. Deduplicate by NAME and UNIT, never by value.
    Separately, DRIFT_THRESHOLD 0.05 m is declared under FIVE names
    (DRIFT_THRESHOLD, L2_DRIFT_M, DRIFT_THRESHOLD_M, THRESHOLD, DRIFT_M), so a
    value-keyed sweep across the repo hits all of them plus the speed.
    FIVE names is settled. The TOTAL is scope-sensitive and no single number is
    safe to quote: 22 in-scope .py sites enumerated 2026-08-12, 23 counting the
    archive/ copy, and a 24th code-shaped site hides behind a .DO_NOT_RUN suffix
    that no *.py glob will match. See CLAUDE.md item 13 for the enumeration.
    That is precisely why this check keys on the NAME and not on a count.
    This check denies a value-keyed in-place substitution of 0.05.

Exit code is always 0. The decision is carried in the JSON payload, matching the
pattern already used by gate_destructive.sh and gate_protected_files.sh.
"""

import json
import re
import sys


def decide(decision, reason):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    cmd = ti.get("command", "") or ""
    file_path = ti.get("file_path", "") or ""
    old_string = ti.get("old_string", "") or ""

    # ---- CHECK 2 first: it is a deny, and denies should not be masked by an ask.

    # The correct way to change one of these thresholds is to name it. If any of
    # the eight known identifiers appears, the edit is keyed by NAME, not by value,
    # which is exactly what register D7 and D7a ask for. Let it through.
    THRESHOLD_NAMES = r"slide_m|slide_speed_ms|float_m|L2_DRIFT_M|DRIFT_THRESHOLD_M|DRIFT_THRESHOLD|DRIFT_M|THRESHOLD"
    names_an_identifier = re.search(THRESHOLD_NAMES, cmd)

    # In-place stream edit keyed on the bare value 0.05. The flag may be written
    # -i, -i.bak, -pi, -pie or --in-place, so match a flag cluster containing i
    # rather than a bare -i token.
    IN_PLACE = r"(?:^|\s)(?:--in-place\b|-[A-Za-z]*i[A-Za-z]*(?:\.\w+)?\b)"
    # Inside a sed or perl expression the dot is normally escaped, so the literal
    # on the command line reads 0\.05 rather than 0.05. Match both, and the
    # bracketed form, or the guard is trivially evaded by correct sed style.
    VAL = r"0(?:\\)?(?:\.|\[\.\])0?5"
    value_keyed_sed = re.search(
        r"\b(?:sed|perl|gsed)\b[^|;&]*?" + IN_PLACE + r"[^|;&]*?" + VAL, cmd
    ) or re.search(
        r"\b(?:sed|perl|gsed)\b[^|;&]*?" + VAL + r"[^|;&]*?" + IN_PLACE, cmd
    )
    if tool == "Bash" and value_keyed_sed and not names_an_identifier:
        decide(
            "deny",
            "Register D7a: in-place substitution keyed on the literal 0.05. "
            "simulation/failure_modes.py:46-48 holds three 0.05 literals and :47 "
            "slide_speed_ms is a SPEED in m/s, not a distance. It feeds the joint "
            "sustained condition at :179-185 that produced the published 16 SLIDE / "
            "1 STUCK verdicts, so a value-keyed replace changes published output "
            "with no error. DRIFT_THRESHOLD is also declared at 24 sites under five "
            "names. Deduplicate by NAME and UNIT, never by value: target "
            "slide_m, slide_speed_ms, float_m, DRIFT_THRESHOLD, L2_DRIFT_M, "
            "DRIFT_THRESHOLD_M, THRESHOLD or DRIFT_M explicitly.",
        )

    # An Edit whose old_string is a bare 0.05 with no identifier to disambiguate it.
    if tool in ("Edit", "Write") and "failure_modes.py" in file_path:
        replacing_bare_value = (
            "0.05" in old_string
            and not re.search(r"slide_m|slide_speed_ms|float_m", old_string)
        )
        if replacing_bare_value:
            decide(
                "deny",
                "Register D7a: editing a 0.05 literal in failure_modes.py without "
                "naming which one. Lines 46, 47 and 48 all read 0.05 but :47 "
                "slide_speed_ms is metres per second, not metres. Include the "
                "variable name in old_string so the unit is unambiguous.",
            )

    # A value-keyed sweep that would collapse the drift threshold names together.
    if tool == "Bash" and re.search(r"DRIFT", cmd) and re.search(r"\bsed\b|\bperl\b", cmd) and "-i" in cmd:
        if not re.search(r"L2_DRIFT_M|DRIFT_THRESHOLD_M|DRIFT_THRESHOLD|DRIFT_M|THRESHOLD", cmd):
            decide(
                "deny",
                "Register D7: the drift tolerance is declared under FIVE names, and "
                "L2_DRIFT_M is the second most common at 7 sites, six of them poster "
                "figure generators. The total is scope-sensitive and disputed (22 "
                "in-scope, see CLAUDE.md item 13), so a value-keyed or count-keyed "
                "sweep is unsafe. Name the variable you mean.",
            )

    # ---- CHECK 1: recursive search scoped to the repo root without real grep.

    if tool == "Bash":
        recursive = re.search(r"\bgrep\b[^|;&]*?\s-[A-Za-z]*[rR]", cmd)
        real_grep = "/usr/bin/grep" in cmd
        names_hidden = re.search(r"renders/|data/|--no-ignore|--ignore-files=", cmd)
        # A search explicitly scoped into a subdirectory that is not the repo root
        # is fine; only a root-scoped sweep makes an inventory claim.
        root_scoped = re.search(
            r"\bgrep\b[^|;&]*?\s(?:\.|\./|\"\.\"|'\.'|\$\{?R\}?|/Users/josie/can-it-ford)\s*(?:$|[|;&])",
            cmd,
        ) or re.search(r"\bgrep\s+-[A-Za-z]*[rR][A-Za-z]*\s+[^|;&]*\s\.\s*$", cmd)

        if recursive and not real_grep and not names_hidden and root_scoped:
            decide(
                "ask",
                "Register H0: this is a recursive grep scoped to the repo root using "
                "the shell's grep function, which wraps ugrep with --ignore-files and "
                "SKIPS every gitignored path. .gitignore:14 is renders/ and :10 is "
                "data/*, so this will silently omit renders/yaris_render_s1/ "
                "(sim_standing.py, vehicle_live.py, gates*.py, all 17 runs' "
                "metrics.csv) and most of data/. An absent hit will NOT be evidence "
                "of absence. Use /usr/bin/grep -rn, or name renders/ and data/ "
                "explicitly. Approve only if you want tracked-files-only scope and "
                "will not make an inventory or absence claim from the result.",
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
