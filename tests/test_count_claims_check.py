"""Tests for .claude/checks/count_claims_check.py.

That checker re-derives, live, how many times the drift tolerance (0.05 m) is
declared in *.py under five variable names, and BLOCKs when a number asserted in
the prose of CLAUDE.md, scripts/check_claims.py or .claude/hooks/audit_integrity_guard.py
matches no defensible live reading. It runs two ways: as a CLI, and as a PreToolUse
hook wired on Edit|Write in .claude/settings.json.

WHY THE SEEDED DECLARATIONS ARE BUILT PROGRAMMATICALLY. tests/ is inside the
checker's scan scope, so no line in this file may carry a drift-family name and the
tolerance value together, not even inside a string, a comment or this docstring.
Written that way it is counted as a real declaration by the very checker under
test, and every total in the repo shifts by one. Not hypothetical, twice over: an
earlier draft of the checker inflated its own totals by quoting a declaration in
its module docstring, and the first draft of THIS file did the same in the very
paragraph warning against it. The checker caught both. Build declarations with a
format string; never write one out longhand.

Each hook test asserts on the permissionDecision JSON, not on the exit code. The
hook exits 0 unconditionally by design; the decision rides in the payload.
"""

import json
import os
import subprocess
import sys
import tempfile
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHECKER = os.path.join(REPO, ".claude", "checks", "count_claims_check.py")

VALUE = "0.05"
# Seeded per-name counts for the synthetic repo. Total 6, no archive site, no
# loose-only site, so all four defensible readings collapse to 6.
SEED_COUNTS = [("DRIFT_THRESHOLD_M", 2), ("L2_DRIFT_M", 1), ("DRIFT_THRESHOLD", 1),
               ("DRIFT_M", 1), ("THRESHOLD", 1)]
SEED_TOTAL = 6

GOOD_TABLE = (
    "13. The drift tolerance is declared as a literal under FIVE names.\n"
    "\n"
    "      DRIFT_THRESHOLD_M  2\n"
    "      L2_DRIFT_M         1\n"
    "      DRIFT_THRESHOLD    1\n"
    "      DRIFT_M            1\n"
    "      THRESHOLD          1\n"
    "      TOTAL              6 in scope\n"
)


def seed(root, claude_md=GOOD_TABLE):
    """Build a synthetic repo with a known live count."""
    for i, (name, n) in enumerate(SEED_COUNTS):
        body = "".join("%s = %s\n" % (name, VALUE) for _ in range(n))
        path = os.path.join(root, "pkg", "m%d.py" % i)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(body)
    # The other two watched files must exist or the checker reports them missing.
    for rel in ("scripts/check_claims.py", ".claude/hooks/audit_integrity_guard.py"):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write("# watched file, carries no count assertion\n")
    with open(os.path.join(root, "CLAUDE.md"), "w") as fh:
        fh.write(claude_md)
    return root


def run_cli(root):
    p = subprocess.run([sys.executable, CHECKER, "--cli", "--root", root],
                       input="", capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout + p.stderr


def fire_hook(root, file_path, new_string=None, content=None, raw=None):
    """Return (stdout, stderr, elapsed). Hook exits 0 always; read the payload."""
    if raw is None:
        ti = {"file_path": file_path}
        if new_string is not None:
            ti["new_string"] = new_string
        if content is not None:
            ti["content"] = content
        raw = json.dumps({"tool_name": "Edit" if content is None else "Write",
                          "tool_input": ti})
    t0 = time.time()
    p = subprocess.run([sys.executable, CHECKER, "--root", root], input=raw,
                       capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, "hook must always exit 0, got %d: %s" % (p.returncode, p.stderr)
    return p.stdout, p.stderr, time.time() - t0


def denied(stdout):
    if not stdout.strip():
        return False
    return json.loads(stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


# ---------------------------------------------------------------- live repo

def test_repo_assertions_agree_with_repo_live_count():
    """The real repo must be self-consistent.

    Deliberately asserts no specific total. The count is scope-sensitive and has
    four defensible readings; hardcoding one here would recreate the bug.
    """
    rc, out = run_cli(REPO)
    assert "blocking defects  0" in out, out
    assert rc == 0, out


def test_repo_scan_actually_extracts_assertions():
    """Guards the defect that made an earlier draft a silent no-op: it reported
    zero blocking findings without ever having extracted a single assertion."""
    _, out = run_cli(REPO)
    found = int(out.split("assertions found")[1].split(",")[0].strip())
    assert found > 0, "extractor matched nothing, so a clean pass is vacuous:\n%s" % out


# ---------------------------------------------------------------- CLI fixtures

def test_matching_count_passes():
    with tempfile.TemporaryDirectory() as t:
        rc, out = run_cli(seed(t))
        assert rc == 0, out


def test_off_by_one_blocks_and_names_the_disagreeing_name():
    """Mirrors register D7's shape: a plausible total, one name that does not
    reproduce. The TOTAL is left correct so exactly one name disagrees."""
    bad = GOOD_TABLE.replace("THRESHOLD          1", "THRESHOLD          2")
    with tempfile.TemporaryDirectory() as t:
        rc, out = run_cli(seed(t, bad))
        assert rc == 1, out
        assert "asserts THRESHOLD" in out, out


def test_no_count_assertion_is_a_noop():
    prose = ("13. The drift tolerance has no peer-reviewed source. Cite the\n"
             "    enumeration produced by a live walk, never a remembered number.\n")
    with tempfile.TemporaryDirectory() as t:
        rc, out = run_cli(seed(t, prose))
        assert rc == 0, out


def test_unrelated_numbers_in_prose_are_not_swept_in():
    noisy = (GOOD_TABLE +
             "\n    The velocity sweep covered 24 runs and 17 gated outcomes.\n"
             "    Prior audits cited 16 and 24 before the enumeration above.\n")
    with tempfile.TemporaryDirectory() as t:
        rc, out = run_cli(seed(t, noisy))
        assert rc == 0, out
        assert "24" not in out.replace("count_claims_check", ""), out


def test_numeric_list_is_not_read_as_totals():
    """"Lines 46, 47 and 48 all read 0.05" must not become three totals."""
    line = GOOD_TABLE + "\n    DRIFT_THRESHOLD note. Lines 46, 47 and 48 are distinct.\n"
    with tempfile.TemporaryDirectory() as t:
        rc, out = run_cli(seed(t, line))
        assert rc == 0, out


# ------------------------------------------------- phrasing, both directions

def test_places_and_sites_phrasings_block_a_wrong_total():
    for phrase in ("The drift tolerance is declared at 99 sites.",
                   "The drift tolerance is declared in 99 places.",
                   "giving 99, 98 or 97."):
        with tempfile.TemporaryDirectory() as t:
            rc, out = run_cli(seed(t, GOOD_TABLE + "\n    " + phrase + "\n"))
            assert rc == 1, "missed a wrong total in %r:\n%s" % (phrase, out)


def test_correct_totals_in_those_phrasings_do_not_false_block():
    for phrase in ("The drift tolerance is declared at 6 places.",
                   "Four defensible totals, 6 / 6 / 6 / 6, all agreeing.",
                   "giving 6, 6 or 6.",
                   "reachable two ways: 6 strict/no-archive, 6 strict/archive."):
        with tempfile.TemporaryDirectory() as t:
            rc, out = run_cli(seed(t, GOOD_TABLE + "\n    " + phrase + "\n"))
            assert rc == 0, "false BLOCK on %r:\n%s" % (phrase, out)


def test_named_declared_at_reads_as_per_name_not_total():
    """"DRIFT_THRESHOLD is declared at 1 sites" is a per-name figure. Reading it
    as a total would compare 1 against the total and block a correct line."""
    with tempfile.TemporaryDirectory() as t:
        claude = GOOD_TABLE + "\n    DRIFT_THRESHOLD is declared at 1 sites.\n"
        rc, out = run_cli(seed(t, claude))
        assert rc == 0, out


def test_refutation_line_does_not_block():
    """Quoting a number in order to retire it is correct and must not block."""
    line = GOOD_TABLE + "\n    D7's earlier claim of 99 places is superseded.\n"
    with tempfile.TemporaryDirectory() as t:
        rc, out = run_cli(seed(t, line))
        assert rc == 0, out


# ---------------------------------------------------------------- robustness

def test_lowercase_name_does_not_crash_or_invent_a_label():
    """One left-context pattern was compiled case-insensitively while the live
    readings are keyed by the exact-case names, so a lowercase spelling raised
    KeyError mid-report.

    Name matching is deliberately case-SENSITIVE and stays that way: the five
    names are uppercase Python identifiers, and matching lowercase would read
    ordinary prose such as "a threshold 3 times higher" as a per-name figure. So a
    lowercase spelling is simply not a name here. What must never happen is a
    crash, or a finding that names a variable which does not exist.
    """
    with tempfile.TemporaryDirectory() as t:
        claude = (GOOD_TABLE +
                  "\n    DRIFT_THRESHOLD note.\n"
                  "    drift_threshold 1 in scope, 1 if archive/ is counted\n")
        _, out = run_cli(seed(t, claude))
        assert "Traceback" not in out, out
        assert "asserts drift_threshold" not in out, out


def test_root_under_a_skipped_path_still_scans():
    """An absolute-path exclusion test pruned the whole tree when the root itself
    sat under .claude/worktrees, reporting every name as 0 and then blocking a
    CLAUDE.md that was correct."""
    with tempfile.TemporaryDirectory() as t:
        root = os.path.join(t, ".claude", "worktrees", "probe")
        os.makedirs(root, exist_ok=True)
        rc, out = run_cli(seed(root))
        assert rc == 0, out
        assert "blocking defects  0" in out, out


# ---------------------------------------------------------------- hook mode

def test_hook_allows_unwatched_file_without_walking_the_repo():
    with tempfile.TemporaryDirectory() as t:
        seed(t)
        out, err, dt = fire_hook(t, os.path.join(t, "pkg", "m0.py"), new_string="x = 1")
        assert not out.strip() and not err.strip()
        assert dt < 5.0, "unwatched file should exit before the repo walk, took %.2fs" % dt


def test_hook_denies_a_wrong_number():
    with tempfile.TemporaryDirectory() as t:
        seed(t)
        out, _, _ = fire_hook(t, os.path.join(t, "CLAUDE.md"),
                              new_string="The drift tolerance is declared at 99 places.")
        assert denied(out), out
        assert "99" in out


def test_hook_allows_a_correct_number():
    with tempfile.TemporaryDirectory() as t:
        seed(t)
        out, _, _ = fire_hook(t, os.path.join(t, "CLAUDE.md"),
                              new_string="The drift tolerance is declared at 6 places.")
        assert not out.strip(), out


def test_hook_catches_a_fragment_with_no_topic_word():
    """An edit fragment carries no drift-family word: the totals-table rows read
    literally "22   bare literals only, archive/ excluded". Gating the hook on a
    topic word let exactly that edit through."""
    with tempfile.TemporaryDirectory() as t:
        seed(t)
        out, _, _ = fire_hook(t, os.path.join(t, "CLAUDE.md"),
                              new_string="      99   bare literals only, archive/ excluded\n")
        assert denied(out), out


def test_hook_handles_write_content_field():
    with tempfile.TemporaryDirectory() as t:
        seed(t)
        out, _, _ = fire_hook(t, os.path.join(t, "CLAUDE.md"),
                              content="drift tolerance declared in 99 places")
        assert denied(out), out


def test_hook_survives_malformed_and_empty_stdin():
    with tempfile.TemporaryDirectory() as t:
        seed(t)
        for raw in ("{not json at all", "", "   ", json.dumps({"tool_name": "Edit"})):
            _, err, dt = fire_hook(t, None, raw=raw)
            assert "Traceback" not in err, (raw, err)
            assert dt < 30, "stdin read hung on %r" % raw


if __name__ == "__main__":
    # pytest is not installed in this environment, so the suite also runs bare:
    #     python3 tests/test_count_claims_check.py
    # The test_* names keep it pytest-compatible for whoever has pytest.
    failures = 0
    for _name, _fn in sorted(globals().items()):
        if not _name.startswith("test_") or not callable(_fn):
            continue
        try:
            _fn()
            print("PASS   %s" % _name)
        except AssertionError as _exc:
            failures += 1
            print("FAIL   %s\n       %s" % (_name, str(_exc)[:400]))
        except Exception as _exc:  # noqa: BLE001
            failures += 1
            print("ERROR  %s\n       %r" % (_name, _exc))
    print("\n%d failing" % failures)
    sys.exit(1 if failures else 0)
