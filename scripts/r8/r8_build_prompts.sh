#!/bin/bash
# Compose each slot's final prompt = shared header + per-slot body.
# Keeping the header in one file means a rule fixed once is fixed for every session.
set -uo pipefail
D=/Users/josie/can-it-ford/scripts/r8/prompts
n=0
for b in "$D"/_body_*.md; do
  slot=$(basename "$b" .md); slot=${slot#_body_}
  { cat "$D/_HEADER.md"; echo; sed "s/<SLOT>/$slot/g" "$b"; } > "$D/$slot.md"
  # substitute the slot into the header's preflight line too
  sed -i '' "s|r8_preflight.sh <SLOT>|r8_preflight.sh $slot|" "$D/$slot.md"
  echo "built $slot.md  ($(wc -c < "$D/$slot.md" | tr -d ' ') bytes)"
  n=$((n+1))
done
echo "$n prompts built"
