#!/bin/zsh
SESSION="cif6"
REPO="$HOME/can-it-ford"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session $SESSION already exists. Attach with: tmux attach -t $SESSION"
  echo "Or kill it first with: tmux kill-session -t $SESSION"
  exit 1
fi

COLS=$(tput cols 2>/dev/null || echo ${COLUMNS:-200})
ROWS=$(tput lines 2>/dev/null || echo ${LINES:-50})

tmux new-session -d -s "$SESSION" -n main -c "$REPO" -x "$COLS" -y "$ROWS"
tmux split-window -h -t "$SESSION:0.0" -c "$REPO"
tmux split-window -h -t "$SESSION:0.0" -c "$REPO"
tmux select-layout -t "$SESSION:0" even-horizontal
tmux split-window -v -t "$SESSION:0.0" -c "$REPO"
tmux split-window -v -t "$SESSION:0.1" -c "$REPO"
tmux split-window -v -t "$SESSION:0.2" -c "$REPO"
tmux select-layout -t "$SESSION:0" tiled

PANE_COUNT=$(tmux list-panes -t "$SESSION:0" | wc -l | tr -d ' ')
if [ "$PANE_COUNT" -ne 6 ]; then
  echo "ERROR: expected 6 panes, got $PANE_COUNT."
  tmux kill-session -t "$SESSION"
  exit 1
fi

tmux select-pane -t "$SESSION:0.0" -T "1-colmap-gsplat"
tmux select-pane -t "$SESSION:0.1" -T "2-paper-git"
tmux select-pane -t "$SESSION:0.2" -T "3-vista-tier0"
tmux select-pane -t "$SESSION:0.3" -T "4-vehicle-geom"
tmux select-pane -t "$SESSION:0.4" -T "5-github-audit"
tmux select-pane -t "$SESSION:0.5" -T "6-poster"

tmux send-keys -t "$SESSION:0.0" "for i in {1..30}; do printf '\033[48;5;88m%-100s\033[0m\n' ''; done" C-m
tmux send-keys -t "$SESSION:0.0" "export PS1='%K{88}%F{255}%B%-100s1-COLMAP%b%f%k
%~ %# '" C-m
tmux send-keys -t "$SESSION:0.0" "cd ~/Documents/Claude/reu/datasets/drain_2956 && pwd" C-m

tmux send-keys -t "$SESSION:0.1" "for i in {1..30}; do printf '\033[48;5;22m%-100s\033[0m\n' ''; done" C-m
tmux send-keys -t "$SESSION:0.1" "export PS1='%K{22}%F{255}%B%-100s2-PAPER%b%f%k
%~ %# '" C-m
tmux send-keys -t "$SESSION:0.1" "cd $REPO && git status" C-m

tmux send-keys -t "$SESSION:0.2" "for i in {1..30}; do printf '\033[48;5;24m%-100s\033[0m\n' ''; done" C-m
tmux send-keys -t "$SESSION:0.2" "printf '\033[48;5;24m\033[97m\033[1m%-100s\033[0m\n' ' 3-VISTA'" C-m
tmux send-keys -t "$SESSION:0.2" "ssh jcerrell0629@vista.tacc.utexas.edu" C-m

tmux send-keys -t "$SESSION:0.3" "for i in {1..30}; do printf '\033[48;5;55m%-100s\033[0m\n' ''; done" C-m
tmux send-keys -t "$SESSION:0.3" "printf '\033[48;5;55m\033[97m\033[1m%-100s\033[0m\n' ' 4-VEHICLE'" C-m
tmux send-keys -t "$SESSION:0.3" "ssh jcerrell0629@vista.tacc.utexas.edu" C-m

tmux send-keys -t "$SESSION:0.4" "for i in {1..30}; do printf '\033[48;5;94m%-100s\033[0m\n' ''; done" C-m
tmux send-keys -t "$SESSION:0.4" "export PS1='%K{94}%F{255}%B%-100s5-GITHUB%b%f%k
%~ %# '" C-m
tmux send-keys -t "$SESSION:0.4" "cd $REPO && pwd" C-m

tmux send-keys -t "$SESSION:0.5" "for i in {1..30}; do printf '\033[48;5;23m%-100s\033[0m\n' ''; done" C-m
tmux send-keys -t "$SESSION:0.5" "export PS1='%K{23}%F{255}%B%-100s6-POSTER%b%f%k
%~ %# '" C-m
tmux send-keys -t "$SESSION:0.5" "echo Poster pane: open Canva manually, use this pane for figure regen commands" C-m

tmux select-pane -t "$SESSION:0.0"
tmux attach -t "$SESSION"
