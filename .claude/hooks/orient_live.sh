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

# --- connector + CI health, added 2026-08-18 ---------------------------------
# Answers "is my stack actually working and being used", which git status alone
# never shows. FAILS OPEN by construction, per the hooks rule in CLAUDE.md:
# every probe is guarded, capped at 5s, and any error path prints nothing and
# returns 0. Network results are cached for 30 min in TMPDIR (never in the repo,
# so it creates no git noise and no worktree dependency).
{
  REPO="${CLAUDE_PROJECT_DIR:-/Users/josie/can-it-ford}"
  CACHE="${TMPDIR:-/tmp}/canford_connector_health"
  MAXAGE=1800

  # -- local, instant, no network: unpushed work and unlanded workflows --------
  echo "--- connector + CI health (network parts cached 30 min) ---"
  if git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
    AHEAD=$(git -C "$REPO" rev-list --count origin/main..HEAD 2>/dev/null)
    BR=$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ -n "$AHEAD" ] && [ "$AHEAD" -gt 0 ] 2>/dev/null; then
      echo "UNMERGED: ${BR} is ${AHEAD} commits ahead of origin/main"
    fi
    # A workflow file that exists here but not on main runs NOWHERE.
    for wf in "$REPO"/.github/workflows/*.yml; do
      [ -f "$wf" ] || continue
      b=$(basename "$wf")
      git -C "$REPO" cat-file -e "origin/main:.github/workflows/$b" 2>/dev/null \
        || echo "  CI: .github/workflows/${b} is ABSENT FROM origin/main, but it RUNS on push from other branches (7 green runs) and count_claims can exit 1 inside a green job. Absent-from-main and runs-nowhere are different claims; only the first is true."
    done
  fi

  # -- network probes, cached -------------------------------------------------
  NOW=$(date +%s 2>/dev/null || echo 0)
  AGE=999999
  if [ -f "$CACHE" ]; then
    MT=$(stat -f %m "$CACHE" 2>/dev/null || stat -c %Y "$CACHE" 2>/dev/null || echo 0)
    AGE=$(( NOW - MT ))
  fi

  if [ "$AGE" -gt "$MAXAGE" ] 2>/dev/null; then
    {
      # W&B: authenticated via ~/.netrc, which is the path a real job uses.
      WB=$(curl -s -n --max-time 5 -H 'Content-Type: application/json' \
        -d '{"query":"{project(name:\"can-it-ford\",entityName:\"jcerrell29-claremont-mckenna-college\"){runCount runs(first:1){edges{node{createdAt}}}}}"}' \
        https://api.wandb.ai/graphql 2>/dev/null)
      if printf '%s' "$WB" | grep -q '"runCount"'; then
        N=$(printf '%s' "$WB" | sed -E 's/.*"runCount":([0-9]+).*/\1/')
        LAST=$(printf '%s' "$WB" | sed -E 's/.*"createdAt":"([^"]{16}).*/\1/')
        echo "wandb: OK, ${N} runs, latest ${LAST}"
      else
        echo "wandb: NOT REACHABLE (check ~/.netrc machine api.wandb.ai)"
      fi

      # HuggingFace: the Mac token store the hf CLI itself uses.
      HFT="$HOME/.cache/huggingface/token"
      if [ -r "$HFT" ]; then
        HFN=$(curl -s --max-time 5 -H "Authorization: Bearer $(tr -d '\n\r' < "$HFT")" \
              https://huggingface.co/api/whoami-v2 2>/dev/null | sed -E 's/.*"name":"([^"]+)".*/\1/')
        case "$HFN" in
          ''|*'{'*|*'error'*) echo "hf: TOKEN DEAD or unreachable (regenerate at huggingface.co/settings/tokens)" ;;
          *) echo "hf: OK as ${HFN}" ;;
        esac
      fi

      # CI: the last conclusion of each workflow that is actually on main.
      if command -v gh >/dev/null 2>&1; then
        for w in csv-check.yml physics-consistency-review.yml sync-to-hub.yml; do
          C=$(gh run list -R jcerrell-IS/can-it-ford --workflow="$w" --limit 1 \
               --json conclusion -q '.[0].conclusion' 2>/dev/null)
          [ -n "$C" ] && [ "$C" != "success" ] && echo "CI FAILING: ${w} last run = ${C}"
        done
      fi
    } > "$CACHE" 2>/dev/null
  fi
  [ -f "$CACHE" ] && cat "$CACHE" 2>/dev/null
} 2>/dev/null || true
