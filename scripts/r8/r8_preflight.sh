#!/bin/bash
# r8_preflight.sh SLOT
#
# Self-audit that every R8 session runs BEFORE it does any work, and again
# before any commit. It refuses (exit 1) when the session is not where it
# believes it is. A session that cannot pass this must stop and say so.
#
# Why this exists, all three measured on this project:
#   1. On 2026-08-16 all four Round 5 panes ran in ONE worktree while their
#      launcher believed it had given them four. Verified by lsof, not assumed.
#   2. A worktree carries the CLAUDE.md from ITS branch point. Measured 676
#      lines in a worktree against 855 in the main tree, hiding three whole
#      sections including the rule that forbids convergence claims from any
#      extremal quantity.
#   3. Editing via an absolute /Users/josie/can-it-ford/... path from inside a
#      worktree silently writes to the MAIN tree on another branch.
#
# Zero dependencies. Read-only. Never runs `cd`.

set -uo pipefail
SLOT="${1:-}"
REPO=/Users/josie/can-it-ford
PLAN="$REPO/scripts/r8/r8_plan.tsv"
BOARD="$REPO/.claude/state/r8_board.md"
FAIL=0

say()  { printf '%s\n' "$*"; }
bad()  { printf 'PREFLIGHT FAIL: %s\n' "$*"; FAIL=1; }

if [ -z "$SLOT" ]; then bad "no slot given. Usage: r8_preflight.sh <slot>"; exit 1; fi
if [ ! -f "$PLAN" ]; then bad "plan file missing: $PLAN"; exit 1; fi

ROW=$(awk -F'\t' -v s="$SLOT" '$1==s' "$PLAN")
if [ -z "$ROW" ]; then bad "slot '$SLOT' is not in the plan"; exit 1; fi

WANT_BRANCH=$(printf '%s' "$ROW" | cut -f3)
WANT_TREE=$(printf '%s' "$ROW" | cut -f5)
WRITES=$(printf '%s' "$ROW" | cut -f7)

say "=== R8 PREFLIGHT, slot $SLOT ==="
say ""

# 1. Am I physically where the plan says.
HERE=$(pwd -P)
say "cwd            $HERE"
say "plan worktree  $WANT_TREE"
[ "$HERE" = "$WANT_TREE" ] || bad "cwd is not the planned worktree. Do NOT 'cd' to fix this; a single cd moves the tracked cwd for the whole session and breaks relative-path hooks. Relaunch in the right place."

# 2. Am I on the branch the plan says, in THIS tree.
GOT_BRANCH=$(git -C "$HERE" symbolic-ref --short HEAD 2>/dev/null || echo DETACHED)
say "branch         $GOT_BRANCH"
say "plan branch    $WANT_BRANCH"
[ "$GOT_BRANCH" = "$WANT_BRANCH" ] || bad "on the wrong branch"

# 3. Is any OTHER worktree also on my branch. Two trees on one branch is the
#    2026-08-07 breach topology.
DUPES=$(git -C "$REPO" worktree list --porcelain 2>/dev/null \
        | awk -v b="refs/heads/$WANT_BRANCH" '/^worktree /{w=$2} /^branch /{if($2==b) print w}')
NDUP=$(printf '%s\n' "$DUPES" | sed '/^$/d' | wc -l | tr -d ' ')
if [ "$NDUP" -gt 1 ]; then
  bad "branch $WANT_BRANCH is checked out in $NDUP worktrees:"
  printf '%s\n' "$DUPES" | sed 's/^/    /'
fi

# 4. Is another CLAUDE session sitting in my worktree. A bash or Python monitor
#    pane is not a session and must not trip this; only an interactive claude is.
CLAUDE_PANES=""
if command -v tmux >/dev/null 2>&1; then
  CLAUDE_PANES=$(tmux list-panes -a -F '#{session_name}:#{window_name}|#{pane_current_path}|#{pane_current_command}' 2>/dev/null \
    | awk -F'|' -v t="$WANT_TREE" '$2==t && ($3 ~ /claude/ || $3 ~ /^node$/ || $3 ~ /^[0-9]+\.[0-9]+\.[0-9]+$/) {print $1}')
  NP=$(printf '%s\n' "$CLAUDE_PANES" | sed '/^$/d' | wc -l | tr -d ' ')
  if [ "$NP" -gt 1 ]; then
    bad "$NP Claude sessions are already in this worktree: $(printf '%s ' $CLAUDE_PANES)"
  elif [ "$NP" = "1" ]; then
    say "claude panes    1 in this worktree (expected: you)"
  else
    say "claude panes    0 in this worktree"
  fi
  OTHERPANES=$(tmux list-panes -a -F '#{session_name}:#{window_name}|#{pane_current_path}|#{pane_current_command}' 2>/dev/null \
    | awk -F'|' -v t="$WANT_TREE" '$2!=t')
fi

# 5. CLAUDE.md drift. A worktree copy is frozen at its branch point.
MAIN_MD="$REPO/CLAUDE.md"
MINE_MD="$HERE/CLAUDE.md"
if [ -f "$MINE_MD" ] && [ -f "$MAIN_MD" ]; then
  A=$(wc -l < "$MINE_MD" | tr -d ' '); B=$(wc -l < "$MAIN_MD" | tr -d ' ')
  say ""
  say "CLAUDE.md      mine $A lines, main checkout $B lines"
  if [ "$A" != "$B" ]; then
    say "SECTIONS PRESENT IN THE MAIN CHECKOUT AND MISSING FROM YOURS:"
    diff <(/usr/bin/grep '^##' "$MINE_MD") <(/usr/bin/grep '^##' "$MAIN_MD") \
      | /usr/bin/grep '^>' | sed 's/^> /    /'
    say "    READ $MAIN_MD BY THAT ABSOLUTE PATH. Your copy is stale by design."
  fi
fi

# 5b. SKILL VERSION MISMATCH. Added 2026-08-19 after the cross-session readout found
#     the research-corpus skill in four different states across the live worktrees:
#     absent in two, an old copy in six, the coordinator's in the main checkout, and
#     the corrected one in a single worktree. Most sessions could not see a night of
#     corrections, and the old copy still asserted something CLAUDE.md had withdrawn.
#     The CLAUDE.md comparison below already existed and did not catch it, because a
#     skill lives in a different file.
SK_MAIN="$REPO/.claude/skills/research-corpus/SKILL.md"
SK_MINE="$HERE/.claude/skills/research-corpus/SKILL.md"
say ""
if [ -f "$SK_MAIN" ]; then
  A_SK=0; [ -f "$SK_MINE" ] && A_SK=$(wc -l < "$SK_MINE" | tr -d ' ')
  B_SK=$(wc -l < "$SK_MAIN" | tr -d ' ')
  say "research-corpus skill   mine $A_SK lines, main checkout $B_SK lines"
  if [ "$A_SK" != "$B_SK" ]; then
    say "SKILL VERSION MISMATCH. Your copy is not the corrected one."
    say "    READ $SK_MAIN BY THAT ABSOLUTE PATH before citing the corpus."
    say "    An old copy has asserted a withdrawn claim before."
  fi
fi

# 6. Repo-wide concurrency. Who else is live right now.
say ""
say "=== OTHER LIVE SESSIONS (do not touch their branches or worktrees) ==="
if [ -n "${OTHERPANES:-}" ]; then
  printf '%s\n' "$OTHERPANES" | awk -F'|' '{printf "  %-24s %-58s [%s]\n", $1, $2, $3}'
else
  say "  (none visible)"
fi

# 7. Working tree cleanliness of MY tree only.
say ""
DIRTY=$(git -C "$HERE" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
say "my tree dirty paths: $DIRTY"
[ "$DIRTY" = "0" ] || git -C "$HERE" status --porcelain | sed 's/^/    /' | head -20

# 8. My declared write scope, echoed back so it is in the session's context.
say ""
say "=== MY WRITE SCOPE, nothing outside this ==="
printf '%s\n' "$WRITES" | tr ',' '\n' | sed 's/^/    /'

# 9. The board.
say ""
if [ -f "$BOARD" ]; then
  say "=== BOARD, last 3 entries (read before starting, append after each unit) ==="
  tail -24 "$BOARD" | sed 's/^/  /'
else
  say "=== BOARD not yet created at $BOARD ==="
fi

# 10. The two git-native gates, so nobody rediscovers them the hard way.
say ""
say "=== GATES ON THIS REPO, shared by every worktree ==="
say "  .git/hooks/pre-commit  refuses more than 8 staged files"
say "  .git/hooks/pre-push    requires PUSH_OK=1"
say "  Stage explicit paths. Never 'git add -A', never 'git commit -a'."
say "  The repo is PUBLIC. Any push is world-readable and permanent."

say ""
if [ "$FAIL" != "0" ]; then
  say "PREFLIGHT FAILED. Do not start work. Report exactly which check failed."
  exit 1
fi
say "PREFLIGHT PASSED for slot $SLOT."
exit 0
