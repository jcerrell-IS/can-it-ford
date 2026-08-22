#!/bin/bash
# session_start_origin_check.sh
#
# Warn at session start when local HEAD differs from ITS OWN origin ref.
#
# WHY THIS IS NOT ALREADY COVERED. orient_live.sh compares the branch to
# origin/main. On a long-lived branch that prints "421 commits ahead of
# origin/main", which is true, constant, and says nothing about whether the work
# in front of you is pushed. On 2026-08-22 this branch sat 2 commits ahead of
# origin/claude/add-ci-checks, including the only copy of a confirmation
# document, and no session-start line said so. This compares HEAD to the
# upstream of the CURRENT branch instead, which is the question actually being
# asked.
#
# LOCAL REFS ONLY, NO NETWORK. It never runs git fetch or git ls-remote:
# SessionStart runs before the session is usable and a hanging remote call would
# stall every start. The counts are therefore relative to the last fetch, and
# the output says so rather than implying it is live.
#
# CANNOT BLOCK, BY DESIGN. Per the hooks reference, SessionStart cannot block a
# session and its stdout is added as context. This only ever prints.
#
# FAILS OPEN. Exits 0 on every path, including not-a-repo and detached HEAD.

# NO `trap ... ERR` HERE, DELIBERATELY. An earlier draft had one, and it fired on
# the expected non-zero from `git rev-parse @{u}` for a branch with no upstream,
# exiting 0 before the warning printed. It silently swallowed the single case
# this hook exists to report. Found by testing that case. Every path below exits
# 0 explicitly, so the trap bought nothing and cost the whole feature.

REPO="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$REPO" ] || exit 0
git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || exit 0

BR=$(git -C "$REPO" branch --show-current 2>/dev/null)
if [ -z "$BR" ]; then
  echo "GIT: detached HEAD at $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null), no upstream to compare."
  exit 0
fi

UP=$(git -C "$REPO" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null)
if [ -z "$UP" ]; then
  if git -C "$REPO" rev-parse --verify -q "origin/$BR" >/dev/null 2>&1; then
    UP="origin/$BR"
  else
    echo "GIT: '$BR' has NO upstream and origin/$BR does not exist locally. Nothing on this branch has ever been pushed, so every commit on it exists in one place only."
    exit 0
  fi
fi

AHEAD=$(git -C "$REPO" rev-list --count "$UP..HEAD" 2>/dev/null)
BEHIND=$(git -C "$REPO" rev-list --count "HEAD..$UP" 2>/dev/null)
[ -n "$AHEAD" ] || exit 0
[ -n "$BEHIND" ] || exit 0

if [ "$AHEAD" = "0" ] && [ "$BEHIND" = "0" ]; then
  echo "GIT: '$BR' matches $UP (as of the last fetch)."
  exit 0
fi

echo "GIT WARNING: '$BR' differs from $UP (as of the last fetch, not checked live)."
[ "$AHEAD" != "0" ] && echo "  AHEAD $AHEAD: unpushed, existing on this machine only. Push with: PUSH_OK=1 git -C \"$REPO\" push origin $BR"
[ "$BEHIND" != "0" ] && echo "  BEHIND $BEHIND: the remote holds commits this tree does not."
if [ "$AHEAD" != "0" ]; then
  echo "  unpushed commits:"
  git -C "$REPO" log --oneline "$UP..HEAD" 2>/dev/null | head -8 | sed 's/^/    /'
fi
exit 0
