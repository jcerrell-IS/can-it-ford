export_all() {
  local minutes="${1:-60}"
  local pane_lines="${2:-400}"
  local logfile="$HOME/can-it-ford/_inbox/LIVE_SESSION_LOG.md"
  local seenfile="$HOME/can-it-ford/_inbox/.export_all_seen_hashes.txt"
  mkdir -p "$(dirname "$logfile")"
  touch "$seenfile"
  local tmpblock
  tmpblock=$(mktemp)
  local stamp
  stamp=$(date "+%Y-%m-%d %H:%M:%S")

  # every variable reused across loop iterations declared exactly once,
  # here, never re-declared with `local` inside a loop body again
  local sessions sess p title cmd panepath
  local sess_header_written captured captured_trimmed
  local t host repo_path encoded remote_dir files f actual_minutes
  local target_header_written parsed parsed_trimmed h jqfilter targets
  local paneskipped=0
  local claudeskipped_empty=0
  local claudeskipped_dup=0
  local claudelogged=0

  {
    echo "# ================================================================"
    echo "# UPDATE: $stamp"
    echo "# (lookback: last ${minutes}m Claude Code activity, last ${pane_lines} lines per pane)"
    echo "# ================================================================"
    echo ""
    echo "## Manual / shell panes"
    echo ""

    sessions=($(tmux list-sessions -F '#S' 2>/dev/null))
    if [[ -z "$sessions" ]]; then
      echo "_(no tmux sessions currently running)_"
    fi
    for sess in $sessions; do
      sess_header_written=0
      for p in $(tmux list-panes -s -t "$sess" -F "#{window_index}.#{pane_index}" 2>/dev/null); do
        captured=$(tmux capture-pane -p -t "$sess:$p" -S "-${pane_lines}" 2>/dev/null)
        captured_trimmed=$(echo "$captured" | sed '/^[[:space:]]*$/d')
        if [[ -z "$captured_trimmed" ]]; then
          paneskipped=$((paneskipped + 1))
          continue
        fi
        if [[ "$sess_header_written" == "0" ]]; then
          echo "### tmux session: \`$sess\`"
          sess_header_written=1
        fi
        title=$(tmux display -p -t "$sess:$p" '#{pane_title}' 2>/dev/null)
        cmd=$(tmux display -p -t "$sess:$p" '#{pane_current_command}' 2>/dev/null)
        panepath=$(tmux display -p -t "$sess:$p" '#{pane_current_path}' 2>/dev/null)
        echo "#### pane $p | $title | $cmd | $panepath"
        echo '```'
        echo "$captured"
        echo '```'
        echo ""
      done
    done

    echo "## Claude Code sessions (thinking + tool calls + tool results)"
    echo ""

    jqfilter='.message.content[]? | if .type=="thinking" then "[THINKING] " + .thinking elif .type=="text" then .text elif .type=="tool_use" then "[TOOL CALL] " + .name + ": " + (.input | tostring) elif .type=="tool_result" then "[TOOL RESULT] " + (.content | tostring) else empty end'

    targets=(
      "jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford"
      "jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/mpm-engine"
      "local:$HOME/can-it-ford"
    )

    for t in $targets; do
      host="${t%%:*}"
      repo_path="${t#*:}"
      encoded="${repo_path//\//-}"
      target_header_written=0

      if [[ "$host" == "local" ]]; then
        files=("${(@f)$(find "$HOME/.claude/projects/${encoded}" -name '*.jsonl' -mmin "-${minutes}" 2>/dev/null)}")
        actual_minutes=$minutes
        if [[ -z "${files[1]}" ]]; then
          files=("${(@f)$(find "$HOME/.claude/projects/${encoded}" -name '*.jsonl' -mmin -120 2>/dev/null)}")
          actual_minutes=120
        fi
      else
        remote_dir="~/.claude/projects/${encoded}"
        files=("${(@f)$(ssh "$host" "find $remote_dir -name '*.jsonl' -mmin -${minutes} 2>/dev/null")}")
        actual_minutes=$minutes
        if [[ -z "${files[1]}" ]]; then
          files=("${(@f)$(ssh "$host" "find $remote_dir -name '*.jsonl' -mmin -120 2>/dev/null")}")
          actual_minutes=120
        fi
      fi

      for f in $files; do
        [[ -z "$f" ]] && continue
        if [[ "$host" == "local" ]]; then
          parsed=$(jq -r "$jqfilter" "$f" 2>/dev/null)
        else
          parsed=$(ssh "$host" "cat '$f'" 2>/dev/null | jq -r "$jqfilter" 2>/dev/null)
