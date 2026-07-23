Given a pane name as an argument, capture its current tmux content,
extract any visible Claude Code resume UUID, and either resume that
session or start a fresh one if no session is currently dead there.
Report which action was taken and show the pane's state after.
