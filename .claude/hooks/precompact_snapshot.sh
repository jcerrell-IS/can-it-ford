#!/bin/bash
# PreCompact: freeze the live repo state to disk before the transcript is summarized.
# Compaction keeps the gist and drops the detail. This project has repeatedly been
# burned by acting on a stale snapshot, so the post-compact session gets a file it
# can read live instead of trusting a summary. Same data as the Safe Resume Protocol.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || ROOT=.
OUT="$ROOT/.claude/state/precompact_snapshots.txt"
mkdir -p "$ROOT/.claude/state" 2>/dev/null
{
  echo "=== precompact $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  git -C "$ROOT" log -1 --format='HEAD %h %ad %s' --date=iso 2>/dev/null
  echo "--- tracked, uncommitted, re-verify before citing ---"
  git -C "$ROOT" status --short 2>/dev/null | grep -v '^??'
  # This repo carries ~90 permanently-untracked paths. Listing them every compact
  # buries the tracked changes above, which are the only lines worth reading.
  echo "--- untracked: $(git -C "$ROOT" status --short 2>/dev/null | grep -c '^??') paths (run git status for the list) ---"
  echo
} >> "$OUT" 2>/dev/null
echo '{"systemMessage":"Pre-compact snapshot appended to .claude/state/precompact_snapshots.txt"}'
