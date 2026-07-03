#!/usr/bin/env bash
set -euo pipefail
REMOTE="jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/phase_space_results.csv"
LOCAL="$HOME/can-it-ford/data/phase_space_results.csv"
scp "$REMOTE" "${LOCAL}.tmp" && mv "${LOCAL}.tmp" "$LOCAL"
echo "[$(date)] pulled $LOCAL"
