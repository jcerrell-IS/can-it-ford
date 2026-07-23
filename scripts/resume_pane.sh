#!/bin/bash
PANE="$1"
FALLBACK_ENV="$2"

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
  exit 0
fi

echo "No live process and no resume ID found."
if [ -z "$FALLBACK_ENV" ]; then
  echo "ABORT: no fallback environment given. Re-run as:"
  echo "  $0 $PANE vista|ls6|mac"
  exit 1
fi

case "$FALLBACK_ENV" in
  vista)
    tmux send-keys -t "$PANE" "cd /work/11603/jcerrell0629/vista/can-it-ford && module load tacc-apptainer && export GENESIS_PATH=/work/10386/lsmith9003/vista/containers/genesis_container.sif && claude" Enter
    ;;
  ls6)
    tmux send-keys -t "$PANE" "cd /scratch/11603/jcerrell0629/can-it-ford && source ~/.venv_mcp_tools/bin/activate && claude" Enter
    ;;
  mac)
    tmux send-keys -t "$PANE" "cd ~/can-it-ford && claude" Enter
    ;;
  *)
    echo "ABORT: unknown fallback environment '$FALLBACK_ENV', expected vista, ls6, or mac"
    exit 1
    ;;
esac
