#!/usr/bin/env bash
set -euo pipefail
REMOTE="${TACC_USER:?set TACC_USER}@vista.tacc.utexas.edu:${TACC_STOCKYARD:?set TACC_STOCKYARD to your /work/<group>/<user> path on TACC}/vista/phase_space_results.csv"
LOCAL="$HOME/can-it-ford/data/phase_space_results.csv"
scp "$REMOTE" "${LOCAL}.tmp" && mv "${LOCAL}.tmp" "$LOCAL"
echo "[$(date)] pulled $LOCAL"
