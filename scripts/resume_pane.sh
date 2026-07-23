#!/bin/bash
PANE="$1"
CURRENT_CMD=$(tmux display-message -t "$PANE" -p '#{pane_current_command}')
if [ "$CURRENT_CMD" = "claude" ] || [ "$CURRENT_CMD" = "claude.exe" ]; then
  echo "$PANE has a LIVE claude process running, not resuming or restarting."
  echo "Current state:"
  tmux capture-pane -t "$PANE" -p -S -20
  exit 0
fi
CAPTURE=$(tmux capture-pane -t "$PANE" -p -S -30)
RESUME_ID=$(echo "$CAPTURE" | grep -oE '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}' | tail -1)
if [ -n "$RESUME_ID" ]; then
  echo "No live claude process, found resume ID: $RESUME_ID"
  tmux send-keys -t "$PANE" "claude --resume $RESUME_ID" Enter
else
  echo "No live process and no resume ID found, starting fresh:"
  tmux send-keys -t "$PANE" "cd /work/11603/jcerrell0629/vista/can-it-ford && module load tacc-apptainer && export GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif && claude" Enter
fi
