#!/usr/bin/env bash
# Build the Can It Ford multi-dispatch tmux session.
# Each pane = one dispatch from docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md,
# in its own git worktree/branch so no two panes can collide.
#
#   ./canford_tmux.sh setup    create worktrees + prompt files (safe, idempotent)
#   ./canford_tmux.sh build    create the tmux session with claude running per pane
#   ./canford_tmux.sh go       submit every pane's prompt (THIS SPENDS TOKENS)
#   ./canford_tmux.sh go 4     submit only pane for dispatch 4
#   ./canford_tmux.sh kill     tear the session down (worktrees are NOT removed)
set -uo pipefail

REPO=/Users/josie/can-it-ford
WT=$REPO/.claude/worktrees
SESSION=canford
DOC=$WT/concurrent-session-safety-570b39/docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md
PROMPTS=$REPO/.claude/dispatch_prompts
CORPUS="/Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13"

# id | colour | short label | working dir | branch (empty = use existing checkout) | base
DISPATCHES=(
  "1|208|D1 PUSH-ORPHANED-g128|$WT/rtfd-test-phase-1-4-569130||"
  "2|045|D2 VISTA-REALISM-TRIAGE|$WT/fork-vista-triage|claude/fork-vista-triage|main"
  "3|196|D3 CREDENTIALS-HARD-STOP|$WT/fork-credentials-DO-NOT-PUSH|claude/credential-exposure-2026-08-13-DO-NOT-PUSH|"
  "4|129|D4 REGISTER-RECONCILE|$WT/fork-register-reconcile|claude/fork-register-reconcile|main"
  "5|046|D5 THREE-CLASS-MATCHED|$WT/fork-three-class|claude/fork-three-class|main"
  "6|051|D6 POSTER-GRADE-VISUALS|$WT/fork-render-3class|claude/fork-render-3class|claude/render-realism-vehicle-water-ad1490"
  "7|220|D7 CORPUS-SPRINT2|$CORPUS||"
  "8|202|D8 PREFLIGHT-RESCUE|/Users/josie/can-it-ford-moving-vehicle||"
  "9|033|D9 MOVING-DRIVER|$WT/fork-moving-driver|claude/fork-moving-driver|main"
  "10|140|D10 SCENE-AND-DOMAIN|$WT/fork-scene|claude/fork-scene|main"
  "11|085|D11 MOVING-VALIDATION|$WT/fork-validation|claude/fork-validation|main"
  "12|173|D12 PROTOCOL-AND-RECHECK|$WT/fork-protocol|claude/fork-protocol|main"
  "13|214|D13 CHRONO-GH200-GONOGO|$WT/fork-chrono-eval|claude/fork-chrono-eval|main"
)

field() { echo "$1" | cut -d'|' -f"$2"; }

setup() {
  mkdir -p "$PROMPTS"
  for d in "${DISPATCHES[@]}"; do
    id=$(field "$d" 1); dir=$(field "$d" 4); br=$(field "$d" 5); base=$(field "$d" 6)
    if [ -n "$br" ] && [ ! -d "$dir" ]; then
      echo "worktree: $br  <- $base"
      git -C "$REPO" worktree add -b "$br" "$dir" "$base" >/dev/null 2>&1 \
        || git -C "$REPO" worktree add "$dir" "$br" >/dev/null 2>&1 \
        || echo "  FAILED $br"
    fi
    cat > "$PROMPTS/d${id}.md" <<EOF
Read $DOC in full, then execute DISPATCH $id exactly as written there.

That document is the single source of truth for this session. Do not work from this
message beyond the following three points:

1. YOUR SCOPE IS THE ONE DECLARED IN DISPATCH $id. Twelve other Claude Code sessions
   are running right now in other worktrees of this same repository. If you write
   outside your declared scope you will corrupt another session's work. This has
   already happened once in this project's history, on 2026-08-07, when two sessions
   edited one working tree and one committed the other's uncommitted edits.
2. Follow the OPERATING PROTOCOL block at the end of that document in full.
3. Before any commit: re-check git status immediately beforehand (never trust an
   earlier check), stage explicit paths only, never git add -A. Do not push without
   asking. The GitHub repo is PUBLIC.

Working directory: $dir
$( [ -n "$br" ] && echo "Branch: $br  <-- YOU ARE ALREADY ON YOUR DEDICATED BRANCH." )
$( [ -n "$br" ] && echo "Where the dispatch says 'create a new branch off main', that is ALREADY DONE." )
$( [ -n "$br" ] && echo "Use this branch. Do NOT create another and do NOT switch branches." )
EOF
  done
  echo "prompts -> $PROMPTS"
}

build() {
  tmux kill-session -t "$SESSION" 2>/dev/null
  tmux new-session -d -s "$SESSION" -n core -c "$(field "${DISPATCHES[0]}" 4)"

  tmux set -g pane-border-status top
  tmux set -g pane-border-lines heavy
  tmux set -g pane-border-format " #[bold]#{pane_title} "
  tmux set -g pane-active-border-style "fg=colour231,bg=colour236,bold"
  tmux set -g mouse on
  tmux set -g status-style "bg=colour234,fg=colour252"
  tmux set -g status-left "#[bold] CAN IT FORD #[default]"
  tmux set -g status-right "#[bold]#{window_name}#[default] | %H:%M "

  local win=core n=0
  for d in "${DISPATCHES[@]}"; do
    id=$(field "$d" 1); col=$(field "$d" 2); lbl=$(field "$d" 3); dir=$(field "$d" 4)
    # 5 per window keeps every pane readable
    if [ $((n % 5)) -eq 0 ] && [ $n -ne 0 ]; then
      win="w$((n/5))"; tmux new-window -t "$SESSION" -n "$win" -c "$dir"
    elif [ $n -ne 0 ]; then
      tmux split-window -t "$SESSION:$win" -c "$dir"
      tmux select-layout -t "$SESSION:$win" tiled >/dev/null
    else
      tmux send-keys -t "$SESSION:$win" "cd '$dir'" C-m
    fi
    local pane; pane=$(tmux display-message -p -t "$SESSION:$win" '#{pane_id}')
    tmux select-pane -t "$pane" -T "$lbl" -P "fg=colour${col}"
    tmux send-keys -t "$pane" "clear; printf '\\033[1;38;5;${col}m%s\\033[0m\\n' '$lbl'; echo 'dir: $dir'" C-m
    tmux send-keys -t "$pane" "claude --model opus --effort max --name '$lbl'" C-m
    n=$((n+1))
  done
  for w in $(tmux list-windows -t "$SESSION" -F '#{window_name}'); do
    tmux select-layout -t "$SESSION:$w" tiled >/dev/null
  done
  echo "session '$SESSION' built, $n panes across $(tmux list-windows -t $SESSION | wc -l | tr -d ' ') windows"
  echo "attach:  tmux attach -t $SESSION"
}

go() {
  local only="${1:-}"
  for d in "${DISPATCHES[@]}"; do
    id=$(field "$d" 1); lbl=$(field "$d" 3)
    [ -n "$only" ] && [ "$only" != "$id" ] && continue
    local pane
    pane=$(tmux list-panes -a -F '#{pane_id} #{pane_title}' | /usr/bin/grep -F "$lbl" | cut -d' ' -f1 | head -1)
    [ -z "$pane" ] && { echo "no pane for D$id"; continue; }
    tmux send-keys -t "$pane" "Read and execute $PROMPTS/d${id}.md"
    sleep 1
    tmux send-keys -t "$pane" Enter
    echo "submitted D$id -> $pane"
  done
}

case "${1:-}" in
  setup) setup ;;
  build) build ;;
  go)    go "${2:-}" ;;
  kill)  tmux kill-session -t "$SESSION" 2>/dev/null; echo "session killed, worktrees left intact" ;;
  *)     echo "usage: $0 {setup|build|go [id]|kill}"; exit 1 ;;
esac
