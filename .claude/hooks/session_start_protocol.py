import json, sys
ctx = (
    "Session-start standing reminders:\n"
    "1. Corrections authority is docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md only.\n"
    "2. 17 canonical runs use warpmpm. Genesis is the abandoned box-proxy path only.\n"
    "3. floor_friction=0.55 is CONFIRMED active, restitution=0.05 satisfies the mpm_solver_warp.py:1915 gate.\n"
    "4. Sound-speed sweep is DONE, jobs 895330 and 895378. Do not re-propose it as untested.\n"
    "5. scenario_sweep.csv: use the 10-column live file, never the 5-column snapshot.\n"
    "6. In/outflow BC citation is Zhao et al 2019, not Kumar.\n"
    "7. SDF-collider buoyancy validation is 7.3 to 7.7 percent, not 1.6 to 7.7.\n"
    "8. Two or more Claude Code sessions may be live in this repo at once. Re-check git status immediately before every commit, never trust a status check from earlier in the conversation."
)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}))
sys.exit(0)
