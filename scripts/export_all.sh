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

  local sessions sess p title cmd panepath
  local sess_header_written captured captured_trimmed
  local t host repo_path files f actual_minutes
  local target_header_written parsed parsed_trimmed h jqfilter
  local remote_hosts rh remote_capture
  local paneskipped=0
  local claudeskipped_empty=0
  local claudeskipped_dup=0
  local claudelogged=0
  local -a sshopts
  sshopts=(-o BatchMode=yes -o ConnectTimeout=8)

  {
    echo "# ================================================================"
    echo "# UPDATE: $stamp"
    echo "# (lookback: last ${minutes}m Claude Code activity, last ${pane_lines} lines per pane)"
    echo "# ================================================================"
    echo ""
    echo "## Manual / shell panes (Mac, local)"
    echo ""

    sessions=($(tmux list-sessions -F '#S' 2>/dev/null))
    if [[ -z "$sessions" ]]; then
      echo "_(no local tmux sessions currently running)_"
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
          echo "### tmux session: \`$sess\` (host: Mac)"
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

    echo "## Manual / shell panes (remote)"
    echo ""

    remote_hosts=(vista ls6)
    for rh in $remote_hosts; do
      remote_capture=$(ssh "${sshopts[@]}" "$rh" "bash ~/bin/tmux_export_local.sh ${pane_lines}" 2>/dev/null)
      if [[ -z "$(echo "$remote_capture" | tr -d '[:space:]')" ]]; then
        echo "_(no tmux sessions on $rh, connection not up, or ~/bin/tmux_export_local.sh missing)_"
        continue
      fi
      echo "$remote_capture"
      echo ""
    done

    echo "## Claude Code sessions (all projects, all hosts, thinking + prompts + tool calls + tool results)"
    echo ""

    jqfilter='.message.role as $role | .message.content[]? | if .type=="thinking" then "[CLAUDE THINKING] " + .thinking elif .type=="text" and $role=="user" then "[JOSIE PROMPT] " + .text elif .type=="text" then "[CLAUDE TEXT] " + .text elif .type=="tool_use" then "[CLAUDE TOOL CALL] " + .name + ": " + (.input | tostring) elif .type=="tool_result" then "[TOOL RESULT] " + (.content | tostring) else empty end'

    for host in local vista ls6; do
      target_header_written=0
      if [[ "$host" == "local" ]]; then
        files=("${(@f)$(find "$HOME/.claude/projects" -maxdepth 1 -mindepth 1 -type d 2>/dev/null)}")
      else
        files=("${(@f)$(ssh "${sshopts[@]}" "$host" "find ~/.claude/projects -maxdepth 1 -mindepth 1 -type d 2>/dev/null")}")
      fi

      for projdir in $files; do
        [[ -z "$projdir" ]] && continue
        local jsonls
        if [[ "$host" == "local" ]]; then
          jsonls=("${(@f)$(find "$projdir" -name '*.jsonl' -mmin "-${minutes}" 2>/dev/null)}")
          actual_minutes=$minutes
          if [[ -z "${jsonls[1]}" ]]; then
            jsonls=("${(@f)$(find "$projdir" -name '*.jsonl' -mmin -120 2>/dev/null)}")
            actual_minutes=120
          fi
        else
          jsonls=("${(@f)$(ssh "${sshopts[@]}" "$host" "find '$projdir' -name '*.jsonl' -mmin -${minutes} 2>/dev/null")}")
          actual_minutes=$minutes
          if [[ -z "${jsonls[1]}" ]]; then
            jsonls=("${(@f)$(ssh "${sshopts[@]}" "$host" "find '$projdir' -name '*.jsonl' -mmin -120 2>/dev/null")}")
            actual_minutes=120
          fi
        fi

        for f in $jsonls; do
          [[ -z "$f" ]] && continue
          if [[ "$host" == "local" ]]; then
            parsed=$(jq -r "$jqfilter" "$f" 2>/dev/null)
          else
            parsed=$(ssh "${sshopts[@]}" "$host" "cat '$f'" 2>/dev/null | jq -r "$jqfilter" 2>/dev/null)
          fi
          parsed_trimmed=$(echo "$parsed" | tr -d '[:space:]')

          if [[ -z "$parsed_trimmed" ]]; then
            claudeskipped_empty=$((claudeskipped_empty + 1))
            continue
          fi

          h=$(echo "$parsed" | md5sum | cut -d' ' -f1)
          if grep -q "^$h\$" "$seenfile" 2>/dev/null; then
            claudeskipped_dup=$((claudeskipped_dup + 1))
            continue
          fi
          echo "$h" >> "$seenfile"
          claudelogged=$((claudelogged + 1))

          if [[ "$target_header_written" == "0" ]]; then
            echo "### $host : $projdir"
            target_header_written=1
          fi
          echo "#### $f"
          echo '```'
          echo "$parsed"
          echo '```'
          echo ""
        done
      done
    done

  } > "$tmpblock"

  sed -i '' -E 's/wandb_v1_[A-Za-z0-9_]+/[REDACTED_WANDB_KEY]/g' "$tmpblock"
  cat "$tmpblock" | pbcopy 2>/dev/null

  if [[ -f "$logfile" ]]; then
    cat "$tmpblock" "$logfile" > "${logfile}.new" && mv "${logfile}.new" "$logfile"
  else
    cp "$tmpblock" "$logfile"
  fi
  rm -f "$tmpblock"

  echo "Prepended to $logfile (this run's capture also copied to clipboard)"
  echo "Local panes skipped as empty: $paneskipped"
  echo "Remote hosts checked: ${remote_hosts[*]}"
  echo "Claude Code entries: skipped empty $claudeskipped_empty | skipped dup $claudeskipped_dup | logged $claudelogged"
}
