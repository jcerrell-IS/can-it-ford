#!/bin/bash
# r8_launch.sh [--wave A|B|C] [--slot NAME] [--go]
#
# Creates the worktree and branch for each planned R8 slot, then launches one
# Claude Code session per slot in its own tmux window, in ITS OWN directory, on
# ITS OWN branch, with a deterministic session id so the watcher can find its
# transcript without guessing.
#
# DRY RUN BY DEFAULT. Nothing is created and nothing is launched without --go.
#
# Design notes, each one from a measured failure on this project:
#   * One window per slot, and `-c <worktree>` per window, because on 2026-08-16
#     a launcher that passed the right -c still ended with all four panes in one
#     worktree. This script VERIFIES the pane path after launch instead of
#     trusting the flag.
#   * A fixed --session-id per slot, so the watcher reads the exact transcript
#     rather than pattern-matching a directory of 292 jsonl files.
#   * The first thing every session is told to run is r8_preflight.sh, which
#     refuses if the session is not where it believes it is.

set -uo pipefail
REPO=/Users/josie/can-it-ford
PLAN="$REPO/scripts/r8/r8_plan.tsv"
STATE="$REPO/.claude/state"
IDS="$STATE/r8_session_ids.tsv"
TMUX_SESSION=canford8
GO=0; WAVE=""; ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --go)   GO=1 ;;
    --wave) WAVE="${2:-}"; shift ;;
    --slot) ONLY="${2:-}"; shift ;;
    *) echo "unknown arg: $1"; exit 2 ;;
  esac
  shift
done

mkdir -p "$STATE"
[ -f "$IDS" ] || : > "$IDS"

run() {
  if [ "$GO" = "1" ]; then eval "$@"; else echo "    DRY: $*"; fi
}

sid_for() {
  local slot="$1" existing
  existing=$(awk -F'\t' -v s="$slot" '$1==s{print $2}' "$IDS")
  if [ -n "$existing" ]; then printf '%s' "$existing"; return; fi
  local new; new=$(uuidgen | tr 'A-Z' 'a-z')
  if [ "$GO" = "1" ]; then printf '%s\t%s\n' "$slot" "$new" >> "$IDS"; fi
  printf '%s' "$new"
}

echo "=== R8 LAUNCH  (GO=$GO, wave=${WAVE:-all}, slot=${ONLY:-all}) ==="
echo

# Refuse to run at all if the dead Round 5 autodispatcher is still firing.
# `pgrep -f` matches the FULL command line, and every R8 session is launched with a
# 12 KB prompt as an argv element. A prompt that merely NAMES this script therefore
# matches, and on 2026-08-18 23:37 that false positive blocked a whole wave: the only
# match was slot d6-tooling's own claude process, whose dispatch quotes the filename.
# So subtract the claude sessions from the matches and refuse only on what is left.
_ad_all=$(pgrep -f round5_autodispatch 2>/dev/null | sort -u)
_ad_claude=$(pgrep -f "claude --model" 2>/dev/null | sort -u)
_ad_real=$(comm -23 <(printf '%s\n' "$_ad_all") <(printf '%s\n' "$_ad_claude") | sed '/^$/d')
if [ -n "$_ad_real" ]; then
  echo "REFUSING: a real round5_autodispatch.py is running (PIDs: $_ad_real) and will type into panes."
  echo "  Stop it first, then re-run:  kill $_ad_real"
  exit 1
fi

if [ "$GO" = "1" ]; then
  tmux has-session -t "$TMUX_SESSION" 2>/dev/null || tmux new-session -d -s "$TMUX_SESSION" -n board -c "$REPO"
fi

while IFS=$'\t' read -r slot wave branch base tree needs_gpu writes; do
  [ "$slot" = "slot" ] && continue
  [ -n "$WAVE" ] && [ "$wave" != "$WAVE" ] && continue
  [ -n "$ONLY" ] && [ "$slot" != "$ONLY" ] && continue

  echo "--- $slot   wave $wave   branch $branch   gpu:$needs_gpu"
  SID=$(sid_for "$slot")
  echo "    session-id $SID"

  if [ "$base" = "SAME" ]; then
    echo "    IN-PLACE slot: uses the existing checkout $tree on its current branch."
    echo "    This slot shares a working tree with other live sessions. Launch it ALONE."
  else
    if [ -d "$tree" ]; then
      echo "    worktree already exists: $tree"
    else
      run "git -C '$REPO' worktree add '$tree' -b '$branch' '$base'"
    fi
  fi

  PROMPT="$REPO/scripts/r8/prompts/$slot.md"
  if [ ! -f "$PROMPT" ]; then
    echo "    MISSING PROMPT: $PROMPT   (skipping launch for this slot)"
    continue
  fi

  # One window per slot, started in the slot's own directory.
  # NOTE, measured: on the first launch of the day the bypassPermissions consent
  # dialog appears and SWALLOWS the prompt argument. The session comes up idle at
  # ctx 0 percent with no turn. Deliver the prompt afterwards with r8_send.py
  # rather than trusting the argument, and check ctx before assuming it landed.
  # PER-SLOT PERMISSION MODE, from coordinator-audit finding A1. Measured across 18
  # transcripts: 878 records carried bypassPermissions and ZERO carried plan, for the whole
  # round, because this line hard-coded it. Deny and ask rules apply in every mode, so the
  # 15 deny and 6 ask rules in .claude/settings.json were live throughout; what a global
  # bypass actually cost was the 23 allow rules going inert and the confirmation step, and
  # it overrode per-slot judgement with one global setting. The plan file now carries a
  # permmode column; read and audit slots default to plan.
  PM=$(awk -F'\t' -v s="$slot" '$1==s{print $NF}' "$PLAN")
  case "$PM" in plan|acceptEdits|bypassPermissions) : ;; *) PM=acceptEdits ;; esac
  CMD="claude --model opus --effort max --permission-mode $PM"
  CMD="$CMD --session-id $SID --add-dir $REPO"
  CMD="$CMD \"\$(cat '$PROMPT')\""

  if [ "$GO" = "1" ]; then
    tmux new-window -t "$TMUX_SESSION" -n "$slot" -c "$tree"
    # NAMED "Enter", never "C-m". Measured 2026-08-18 21:52: C-m leaves text in
    # the input and the turn never starts, on the shell line and inside the TUI
    # alike. Four delivery attempts were lost to this before it was isolated.
    tmux send-keys -t "$TMUX_SESSION:$slot" "$CMD" Enter
    sleep 2
    ACTUAL=$(tmux display-message -p -t "$TMUX_SESSION:$slot" '#{pane_current_path}' 2>/dev/null)
    if [ "$ACTUAL" != "$tree" ]; then
      echo "    LAUNCH VERIFY FAILED: pane is in '$ACTUAL', expected '$tree'"
    else
      echo "    launched and verified in $ACTUAL"
    fi
  else
    echo "    DRY: tmux new-window -t $TMUX_SESSION -n $slot -c $tree"
    echo "    DRY: $CMD"
  fi
  echo
done < "$PLAN"

echo "=== done. Attach with:  tmux attach -t $TMUX_SESSION ==="
[ "$GO" = "1" ] || echo "=== THIS WAS A DRY RUN. Re-run with --go to actually create and launch. ==="
