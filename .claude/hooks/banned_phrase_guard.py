import json, subprocess, sys, re
data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")
if not re.search(r"\bgit\s+(commit|push)\b", cmd):
    sys.exit(0)
try:
    diff = subprocess.run(
        ["git", "diff", "--cached", "--", ":(top)",
         ":(exclude,top).claude/hooks/banned_phrase_guard.py"],
        capture_output=True, text=True).stdout
except Exception:
    sys.exit(0)
scanned = cmd + "\n" + diff
banned = [
    (r"Genesis\s+MPM", "the 17 runs use warpmpm, not Genesis MPM"),
    (r"gravity\s+is\s+unknown", "gravity is settled: g=[0,0,-9.81]"),
    (r"cfrc_coupling_vel", "cfrc_coupling_vel is Genesis-only, absent in warpmpm"),
    (r"effective\s+density\s+band\s+100.?300", "use realized density 310.494 kg/m3"),
    (r"grid_density\s*64\s+is\s+safe", "magnitude is not grid-invariant, verdict is"),
    (r"30\.4\s*percent|23\s+pairs", "stale, corrected is 14 FORD, 23 of 70 reclassify"),
    (r"DRIFT_THRESHOLD.{0,40}Smith.{0,20}Eq\s*6", "DRIFT_THRESHOLD has no peer source"),
    (r"box\s+proxy\s+vehicle", "canonical path uses the watertight hull, not a box"),
    (r"Al-?Qadami.{0,30}Yaris", "Al-Qadami tested a Perodua Viva, not a Yaris"),
    (r"Kumar\s+2019.{0,30}(in/?out|boundary)", "cite Zhao et al 2019, 10.1016/j.compfluid.2018.10.007"),
    (r"cannot\s+float\s+regardless\s+of\s+density", "retracted, see docs/COUPLING_VALIDATION_J1_2026-08-07.md"),
    (r"sign.?inverted?\s+coupling", "retracted, was a np.polyfit artifact, not physics"),
    (r"1\.6\s*(to|-)\s*7\.7\s*percent", "SDF error range is 7.3 to 7.7 percent, not 1.6 to 7.7"),
    (r"blob\s*7e5c7cd2", "that blob does not exist, do not cite it"),
]
hits = [msg for pat, msg in banned if re.search(pat, scanned, re.IGNORECASE)]
if hits:
    sys.stderr.write("BLOCKED banned phrase in commit message or staged diff:\n- " + "\n- ".join(hits) + "\n")
    sys.exit(2)
sys.exit(0)
