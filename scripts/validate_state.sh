#!/bin/bash
echo "=== 1, CLAUDE.md is the canonical tracked rules file, and carries no personal content ==="
git -C ~/can-it-ford ls-files --error-unmatch CLAUDE.md >/dev/null 2>&1 \
  && echo "Mac: tracked, OK" || echo "Mac: NOT TRACKED, FIX THIS"
git -C ~/can-it-ford grep -qiE 'adhd|therapy|medication|prescription|psychiatr' -- CLAUDE.md 2>/dev/null \
  && echo "Mac: PERSONAL CONTENT IN TRACKED CLAUDE.md, FIX THIS" \
  || echo "Mac: no personal-content keywords, OK"

echo "=== 2, skill fork is the correct N-panel version ==="
EXPECTED_MD5="9bbabeab21f879f0067669ecd7a1167"
ACTUAL_MD5=$(md5 -q ~/.claude/skills/bug-triage-protocol/SKILL.md 2>/dev/null)
if [ ${#EXPECTED_MD5} -ne 32 ]; then
  echo "skill: BASELINE MALFORMED, ${#EXPECTED_MD5} chars where an md5 is 32."
  echo "skill: this check cannot pass until a human confirms the correct file and re-baselines."
  echo "skill: live file md5 is $ACTUAL_MD5"
elif [ "$ACTUAL_MD5" = "$EXPECTED_MD5" ]; then
  echo "skill: correct version, OK"
else
  echo "skill: MISMATCH, expected $EXPECTED_MD5, got $ACTUAL_MD5"
fi

echo "=== 3, WANDB_API_KEY is set and not the placeholder ==="
if [ "$WANDB_API_KEY" = "your-new-key-here" ]; then
  echo "WANDB_API_KEY: STILL PLACEHOLDER TEXT, FIX THIS"
elif [ -n "$WANDB_API_KEY" ]; then
  echo "WANDB_API_KEY: set in this shell, OK (not printing it)"
elif grep -qE '^[[:space:]]*(export[[:space:]]+)?WANDB_API_KEY=.+' ~/can-it-ford/.env 2>/dev/null; then
  echo "WANDB_API_KEY: not exported in this shell, present in .env, OK"
else
  echo "WANDB_API_KEY: NOT SET anywhere, FIX THIS"
fi

echo "=== 4, no wandb_backfill.py plaintext key anywhere known ==="
grep -rl "WANDB_API_KEY\s*=\s*['\"]" ~/can-it-ford ~/can_it_ford ~/can-it-ford-untracked-preserve 2>/dev/null
echo "(empty output above = clean)"

echo "=== 5, the two archive duplicate folders are actually gone ==="
if [ -d ~/Archive/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07/ ]; then
  echo "archive: STILL PRESENT, review then remove"
  ls ~/Archive/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07/
else
  echo "archive: gone, OK"
fi

echo "=== 6, git status is otherwise clean of surprises ==="
git -C ~/can-it-ford status --short

echo "=== 7, mass bug fix actually applied to the live Vista file ==="
echo "(run this part on Vista, not Mac)"
echo 'ssh jcerrell0629@vista.tacc.utexas.edu "grep -n rho= /work/11603/jcerrell0629/vista/can-it-ford/simulation/can_it_ford_L2_mpm.py"'
