#!/bin/bash
# Pull ONLY the small artifacts (summary.json, metrics.csv, provenance) of the R7
# pinned-span ladder off Vista. rollout.npz is deliberately excluded: it is hundreds
# of MB per run and nothing in the analysis reads it.
set -uo pipefail
DEST=${1:?usage: r7_pull_pinned.sh DEST_DIR}
mkdir -p "$DEST"
ssh -o BatchMode=yes -o ConnectTimeout=15 vista \
  'cd $WORK && find r7_pin_g*_* -name "summary.json" -o -name "metrics.csv" -o -name "*provenance.json" | sort | tar czf - -T -' \
  > "$DEST/r7_pinned_small.tgz"
tar xzf "$DEST/r7_pinned_small.tgz" -C "$DEST"
echo "pulled into $DEST:"
ls -d "$DEST"/r7_pin_g*_* 2>/dev/null
