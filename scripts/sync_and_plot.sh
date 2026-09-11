#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/can-it-ford"
./scripts/pull_vista_phase_space.sh
conda run -n can-it-ford python scripts/plot_phase_space.py
terminal-notifier -title "Can It Ford" -message "Synced and replotted" 2>/dev/null || true
