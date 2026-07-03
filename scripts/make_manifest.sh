#!/bin/bash
set -euo pipefail
STAGING="$HOME/can-it-ford/designsafe-staging"
OUT="$STAGING/MANIFEST.txt"
cd "$STAGING"
{
  echo "Can It Ford dataset manifest"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  printf "%-12s  %-40s  %s\n" "SIZE" "FILE" "SHA256"
  find . -type f ! -name "MANIFEST.txt" | sort | while read -r f; do
    size=$(stat -f%z "$f")
    hash=$(shasum -a 256 "$f" | awk '{print $1}')
    printf "%-12s  %-40s  %s\n" "$size" "${f#./}" "$hash"
  done
} > "$OUT"
echo "Wrote $OUT"
cat "$OUT"
