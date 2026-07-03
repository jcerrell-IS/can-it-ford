#!/bin/bash
set -euo pipefail
FORDPY="/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3"
DEST="$HOME/can-it-ford/data/phase_space_results.csv"
SRC="vista:/work/11603/jcerrell0629/vista/phase_space_results.csv"
while true; do
  scp "$SRC" "$DEST"
  "$FORDPY" "$HOME/can-it-ford/make_phase_space.py"
  echo "Pulled and regenerated at $(date +%H:%M:%S). Sleeping 5 min."
  sleep 300
done
