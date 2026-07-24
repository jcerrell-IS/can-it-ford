#!/bin/bash
echo "=== live orientation, not memory, re-verify before citing anything ==="
git log --oneline -5 2>/dev/null
echo "--- uncommitted right now ---"
git status --short 2>/dev/null
echo "--- canonical files, confirmed as of tonight, do not substitute a duplicate ---"
echo "CLAUDE.md (project root) = Multi-Pane Standing Rules, confirmed synced Mac/Vista/LS6/GitHub"
echo "SESSION_STATE.md exists but check its own top timestamp against git log before trusting it, caught stale twice tonight"
echo "vehicle_params.py mass_kg should read 1100.0, verify live, do not assume"
