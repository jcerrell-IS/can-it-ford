#!/bin/bash
echo "=== live orientation, not memory, re-verify before citing anything ==="
git log --oneline -5 2>/dev/null
echo "--- uncommitted right now ---"
git status --short 2>/dev/null
echo "--- canonical files, confirmed as of tonight, do not substitute a duplicate ---"
echo "CLAUDE.md (project root) = Multi-Pane Standing Rules, confirmed synced Mac/Vista/LS6/GitHub"
echo "SESSION_STATE.md exists but check its own top timestamp against git log before trusting it, caught stale twice tonight"
echo "vehicle_params.py mass_kg should read 1100.0, verify live, do not assume"

# --- Safe Resume Protocol item 3, automated: is anything running on TACC? ---
# Fast and non-fatal. If the ControlMaster socket is cold this prints one line
# and moves on rather than stalling session start on an auth prompt.
echo "--- TACC live state (Safe Resume item 3) ---"
for h in vista ls6; do
  if ssh -o BatchMode=yes -o ConnectTimeout=6 "$h" true 2>/dev/null; then
    JOBS=$(ssh -o BatchMode=yes -o ConnectTimeout=6 "$h" \
      'squeue -u "$USER" -h -o "%.10i %.20j %.8T %.10M/%.10l %R"' 2>/dev/null)
    SU=$(ssh -o BatchMode=yes -o ConnectTimeout=6 "$h" \
      '/usr/local/etc/taccinfo 2>/dev/null | awk "/BCS20003/{print \$3}"' 2>/dev/null)
    if [ -n "$JOBS" ]; then
      echo "${h}: JOBS RUNNING (do not assume a clean boundary)"
      echo "$JOBS" | sed "s/^/    /"
    else
      echo "${h}: queue empty"
    fi
    [ -n "$SU" ] && echo "    SUs remaining: ${SU}"
  else
    echo "${h}: socket cold, run 'ssh ${h}' once to enable direct access this session"
  fi
done
echo "Direct TACC access is wired: scripts/tacc.sh <host> '<cmd>' or --status. No tmux relay needed."

# --- research corpus, hardwired 2026-08-15 -----------------------------------
# The research is only useful if a session knows it exists before it asserts
# something. Description-triggered skills are good but not guaranteed, so the
# index announces itself here every session.
IDX="${CLAUDE_PROJECT_DIR:-/Users/josie/can-it-ford}/data/research_corpus_index.json"
if [ -f "$IDX" ]; then
  /usr/bin/python3 - "$IDX" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
print("--- research corpus, query it before asserting novelty or a method ---")
print(f"{d.get('n_papers',0)} papers ({d.get('n_with_abstract',0)} with abstracts), "
      f"{d.get('n_documents',0)} documents "
      f"({d.get('n_documents_on_topic',0)} on-topic). "
      f"Only {d.get('n_cited_reader_facing',0)} papers reach paper/ or docs/.")
print("  python3 analysis/research_index.py --stats | --method X | --query X | --docs")
print("  Skill: research-corpus. Four prior vehicle-fording works exist and")
print("  paper/ cites NONE of them. settle_frames=8 is contradicted by all 25 runs.")
PY
fi
