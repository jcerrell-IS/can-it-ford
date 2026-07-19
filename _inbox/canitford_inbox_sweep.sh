#!/bin/bash
# canitford_inbox_sweep.sh
# Moves any recently-added can-it-ford-related files sitting in Downloads or
# Desktop into ~/can-it-ford/_inbox/, so nothing new joins the scattered mess
# again. Run manually, or install as a scheduled LaunchAgent (see
# SETUP_AUTOMATION.md in this same download).

set -euo pipefail

INBOX="$HOME/can-it-ford/_inbox"
LOGFILE="$HOME/can-it-ford/_inbox/.sweep_log.txt"
LOOKBACK_MINUTES=10080   # 7 days in minutes; safe to re-run repeatedly, already-moved files won't be in Downloads/Desktop anymore

mkdir -p "$INBOX"

PATTERN='(can[-_ ]?it[-_ ]?ford|canitford)'

echo "--- Sweep run: $(date) ---" >> "$LOGFILE"

for SRC in "$HOME/Downloads" "$HOME/Desktop"; do
  if [ -d "$SRC" ]; then
    find "$SRC" -maxdepth 1 -type f -mmin "-${LOOKBACK_MINUTES}" 2>/dev/null | while read -r f; do
      base="$(basename "$f")"
      if echo "$base" | grep -Eqi "$PATTERN"; then
        # avoid clobbering: if a file with this name already exists in inbox, prefix with today's date
        if [ -e "$INBOX/$base" ]; then
          dest="$INBOX/$(date +%Y-%m-%d)_$base"
        else
          dest="$INBOX/$base"
        fi
        mv "$f" "$dest" 2>>"$LOGFILE" && echo "moved: $f -> $dest" >> "$LOGFILE" || echo "FAILED to move (left in place, check .sweep_log.txt above this line for the reason): $f" >> "$LOGFILE"
      fi
    done
  fi
done

echo "Sweep complete. See $LOGFILE for details." | tee -a "$LOGFILE"
