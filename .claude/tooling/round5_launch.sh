#!/usr/bin/env bash
# =============================================================================
# round5_launch.sh — build the Round 5 tmux session so it can actually be WATCHED.
#
# WHY EVERY VISUAL CHOICE HERE EXISTS. Round 3 ran 13 panes tiled in ONE window
# on a 66-column client. Nothing was legible, a stalled session looked identical
# to a working one, and the coordinator could not tell which pane it was reading.
# Fixes, all deliberate:
#   * ONE WINDOW PER DISPATCH. Never tile. Window index == dispatch number.
#   * A COLOUR PER DISPATCH, carried on the border, the title bar and the
#     window-status entry, so a glance at any of the three identifies the session.
#   * pane-border-status top, always on, even with one pane, so the title is
#     visible without attaching.
#   * HEAVY border lines: at small font a single-line border is invisible.
#   * A status bar that shows branch and worktree, because the 2026-08-07 breach
#     was a session writing to the wrong tree without noticing.
#
# Usage:  bash round5_launch.sh            build and print how to attach
#         bash round5_launch.sh --restyle  reapply styling to a live session
# =============================================================================
set -uo pipefail

SESSION=canford5
REPO=/Users/josie/can-it-ford
TOOLING=$REPO/.claude/tooling
BOARD=$REPO/.claude/state/round5_board.md

# id | short label | colour | worktree dir | branch
DISPATCHES='
1|MINE-RESEARCH|colour39|.claude/worktrees/r5-research|claude/r5-research
2|E8-CREDENTIALS|colour208|.claude/worktrees/r5-exposure|claude/r5-exposure
3|SAFE-THE-WORK|colour148|.claude/worktrees/r5-safekeeping|claude/r5-safekeeping
4|PHYSICS-GATE|colour170|.claude/worktrees/r5-physics|claude/r5-physics
'

style_session() {
  tmux set -t "$SESSION" -g mouse on
  tmux set -t "$SESSION" -g history-limit 200000
  tmux set -t "$SESSION" -g base-index 0
  tmux set -t "$SESSION" -g pane-border-lines heavy
  tmux set -t "$SESSION" -g pane-border-status top
  tmux set -t "$SESSION" -g display-time 4000
  tmux set -t "$SESSION" -g status-interval 5
  tmux set -t "$SESSION" -g status-left-length 40
  tmux set -t "$SESSION" -g status-right-length 90
  tmux set -t "$SESSION" -g status-style "bg=colour234,fg=colour250"
  tmux set -t "$SESSION" -g status-left "#[bg=colour25,fg=colour255,bold] CANFORD5 #[default] "
  tmux set -t "$SESSION" -g status-right \
    "#[fg=colour244]#(cd $REPO && git rev-parse --abbrev-ref HEAD) #[fg=colour109]| %H:%M "
  tmux set -t "$SESSION" -g window-status-format \
    "#[fg=colour244] #I #W "
  tmux set -t "$SESSION" -g window-status-current-format \
    "#[bg=colour238,fg=colour255,bold] #I #W #[default]"
  tmux set -t "$SESSION" -g window-status-separator ""
}

style_window() {   # $1=window index  $2=colour  $3=label  $4=branch
  local w=$1 c=$2 label=$3 br=$4
  tmux set -w -t "$SESSION:$w" pane-border-style "fg=colour238"
  tmux set -w -t "$SESSION:$w" pane-active-border-style "fg=$c,bold"
  tmux set -w -t "$SESSION:$w" window-status-current-format \
    "#[bg=$c,fg=colour16,bold] #I $label #[default]"
  tmux set -w -t "$SESSION:$w" window-status-format \
    "#[fg=$c] #I $label "
  # The border title is the identity line: D#, label, branch.
  tmux set -w -t "$SESSION:$w" pane-border-format \
    "#[fg=$c,bold] D$w $label #[fg=colour244]| $br | #{pane_current_path} "
}

if [ "${1:-}" = "--restyle" ]; then
  style_session
  echo "$DISPATCHES" | while IFS='|' read -r id label colour dir br; do
    [ -z "$id" ] && continue
    style_window "$id" "$colour" "$label" "$br"
  done
  echo "restyled $SESSION"
  exit 0
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "session $SESSION already exists. Use --restyle, or kill it first:"
  echo "  tmux kill-session -t $SESSION"
  exit 1
fi

mkdir -p "$(dirname "$BOARD")"

# --- worktrees -------------------------------------------------------------
echo "$DISPATCHES" | while IFS='|' read -r id label colour dir br; do
  [ -z "$id" ] && continue
  full="$REPO/$dir"
  if [ ! -d "$full" ]; then
    git -C "$REPO" worktree add -b "$br" "$full" HEAD >/dev/null 2>&1 \
      && echo "  worktree created  $br" \
      || echo "  !! worktree FAILED $br (branch may exist; check manually)"
  else
    echo "  worktree exists   $br"
  fi
done

# --- session ---------------------------------------------------------------
tmux new-session -d -s "$SESSION" -n "0-MONITOR" -c "$REPO"
style_session
tmux set -w -t "$SESSION:0" pane-border-format \
  "#[fg=colour45,bold] MONITOR #[fg=colour244]| canford5 | follow-up dispatcher "
tmux set -w -t "$SESSION:0" pane-active-border-style "fg=colour45,bold"
tmux set -w -t "$SESSION:0" window-status-current-format \
  "#[bg=colour45,fg=colour16,bold] 0 MONITOR #[default]"
tmux set -w -t "$SESSION:0" window-status-format "#[fg=colour45] 0 MONITOR "

echo "$DISPATCHES" | while IFS='|' read -r id label colour dir br; do
  [ -z "$id" ] && continue
  tmux new-window -t "$SESSION:$id" -n "D$id" -c "$REPO/$dir"
  style_window "$id" "$colour" "$label" "$br"
done

tmux select-window -t "$SESSION:0"

cat > "$BOARD" <<EOF
# ROUND 5 BRANCH BOARD
Every dispatch appends here after each unit of work. Read it BEFORE starting
anything, so you do not duplicate a sibling. Append only; never rewrite another
session's lines.

| when | D | branch | did | next | do-not-touch |
|---|---|---|---|---|---|
EOF

echo
echo "built. attach with:"
echo "  tmux attach -t $SESSION"
echo "windows: 0-MONITOR, D1 MINE-RESEARCH, D2 E8-CREDENTIALS, D3 SAFE-THE-WORK, D4 PHYSICS-GATE"
echo "board:   $BOARD"
echo "next:    launch claude in each D window, then paste its dispatch file"
