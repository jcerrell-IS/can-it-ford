#!/bin/bash
echo "=== 1, CLAUDE.md not tracked in either repo ==="
git -C ~/can-it-ford check-ignore CLAUDE.md && echo "Mac: ignored, OK" || echo "Mac: NOT IGNORED, FIX THIS"
git -C ~/can-it-ford status --short | grep -q CLAUDE.md && echo "Mac: SHOWS IN STATUS, FIX THIS" || echo "Mac: absent from status, OK"

echo "=== 2, skill fork is the correct N-panel version ==="
EXPECTED_MD5="9bbabeab21f879f0067669ecd7a1167"
ACTUAL_MD5=$(md5 -q ~/.claude/skills/bug-triage-protocol/SKILL.md 2>/dev/null)
if [ "$ACTUAL_MD5" = "$EXPECTED_MD5" ]; then
  echo "skill: correct version, OK"
else
  echo "skill: MISMATCH, expected $EXPECTED_MD5, got $ACTUAL_MD5"
fi

echo "=== 3, WANDB_API_KEY is set and not the placeholder ==="
if [ -z "$WANDB_API_KEY" ]; then
  echo "WANDB_API_KEY: NOT SET, FIX THIS"
elif [ "$WANDB_API_KEY" = "your-new-key-here" ]; then
  echo "WANDB_API_KEY: STILL PLACEHOLDER TEXT, FIX THIS"
else
  echo "WANDB_API_KEY: set to a real value, OK (not printing it)"
fi

echo "=== 4, no wandb_backfill.py plaintext key anywhere known ==="
grep -rl "WANDB_API_KEY\s*=\s*['\"]" ~/can-it-ford ~/can_it_ford ~/can-it-ford-untracked-preserve 2>/dev/null
echo "(empty output above = clean)"

echo "=== 5, the two archive duplicate folders are actually gone ==="
ls ~/Archive/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07/ 2>&1

echo "=== 6, git status is otherwise clean of surprises ==="
git -C ~/can-it-ford status --short

echo "=== 7, mass bug fix actually applied to the live Vista file ==="
echo "(run this part on Vista, not Mac)"
echo 'ssh jcerrell0629@vista.tacc.utexas.edu "grep -n rho= /work/11603/jcerrell0629/vista/can-it-ford/simulation/can_it_ford_L2_mpm.py"'
