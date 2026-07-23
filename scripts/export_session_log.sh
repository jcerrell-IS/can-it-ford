#!/bin/zsh

LOG_DIR="$HOME/can-it-ford/_inbox"
ARCHIVE_DIR="$LOG_DIR/session_archive"
LOG_FILE="$LOG_DIR/LIVE_SESSION_LOG.md"
TODAY=$(date +%Y-%m-%d)
NOW=$(date "+%Y-%m-%d %H:%M:%S")
TMPFILE=$(mktemp)

mkdir -p "$ARCHIVE_DIR"

rotate_log_if_needed() {
  if [ -f "$LOG_FILE" ]; then
    local first_line=$(grep -m1 "^# UPDATE:" "$LOG_FILE")
    local first_date=$(echo "$first_line" | awk '{print $3}')
    if [ -n "$first_date" ] && [ "$first_date" != "$TODAY" ]; then
      mv "$LOG_FILE" "$ARCHIVE_DIR/LIVE_SESSION_LOG_${first_date}.md"
      echo "Rotated previous log to $ARCHIVE_DIR/LIVE_SESSION_LOG_${first_date}.md"
    fi
  fi
}

capture_tmux() {
  local sessions=$(tmux list-sessions -F "#{session_name}" 2>/dev/null)
  if [ -z "$sessions" ]; then
    echo "## tmux sessions"
    echo "None running."
    echo ""
    return
  fi
  echo "## tmux sessions"
  echo ""
  for s in ${(f)sessions}; do
    local host=$(tmux show-environment -t "$s" HOSTNAME 2>/dev/null | cut -d= -f2)
    [ -z "$host" ] && host="Mac"
    echo "### tmux session: \`$s\` (host: $host)"
    tmux list-panes -t "$s" -F "#{pane_index}|#{pane_title}|#{pane_current_command}|#{pane_current_path}" 2>/dev/null | while IFS='|' read idx title cmd cwd; do
      echo "#### pane 0.$idx | $title | $cmd | $cwd"
      echo '```'
      tmux capture-pane -t "$s:0.$idx" -p -S -400 2>/dev/null
      echo '```'
      echo ""
    done
  done
}

capture_terminal_app() {
  echo "## Non-tmux terminal windows"
  echo ""
  local running=$(osascript -e 'tell application "System Events" to (name of processes) contains "Terminal"' 2>/dev/null)
  if [ "$running" != "true" ]; then
    echo "Terminal.app not running, skipped."
    echo ""
  else
    local wcount=$(osascript -e 'tell application "Terminal" to count windows' 2>/dev/null)
    local i=1
    while [ "$i" -le "${wcount:-0}" ]; do
      echo "### Terminal.app | window $i"
      echo '```'
      osascript -e "tell application \"Terminal\" to get contents of tab 1 of window $i" 2>/dev/null
      echo '```'
      echo ""
      i=$((i+1))
    done
  fi
  local iterm_running=$(osascript -e 'tell application "System Events" to (name of processes) contains "iTerm2"' 2>/dev/null)
  if [ "$iterm_running" != "true" ]; then
    echo "iTerm2 not running, skipped."
    echo ""
  else
    echo "### iTerm2"
    echo '```'
    osascript -e 'tell application "iTerm2" to get contents of current session of current window' 2>/dev/null
    echo '```'
    echo ""
  fi
}

capture_claude_code() {
  echo "## Claude Code sessions"
  echo ""
  echo "PORT_EXISTING_JSONL_LOGIC_HERE"
  echo ""
}

build_index() {
  echo "## INDEX"
  local sessions=$(tmux list-sessions -F "#{session_name}" 2>/dev/null)
  for s in ${(f)sessions}; do
    local pcount=$(tmux list-panes -t "$s" 2>/dev/null | wc -l | tr -d ' ')
    echo "- tmux: $s — $pcount panes"
  done
  [ -z "$sessions" ] && echo "- tmux: none running"
  echo ""
}

rotate_log_if_needed

{
  echo "# ================================================================"
  echo "# UPDATE: $NOW"
  echo "# (lookback: last 60m Claude Code activity, last 400 lines per pane)"
  echo "# ================================================================"
  echo ""
  build_index
  capture_tmux
  capture_terminal_app
  capture_claude_code
} > "$TMPFILE"

if [ -f "$LOG_FILE" ]; then
  cat "$TMPFILE" "$LOG_FILE" > "${LOG_FILE}.new"
  mv "${LOG_FILE}.new" "$LOG_FILE"
else
  mv "$TMPFILE" "$LOG_FILE"
fi
rm -f "$TMPFILE"
