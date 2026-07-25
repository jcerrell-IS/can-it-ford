## Multi-Pane Standing Rules

These apply to every pane in every session automatically, do not
restate them in chat prompts.

- Never fabricate a command, parameter, or claim. Pull from actual
  file content, actual output, or actual verified search results.
  This includes a prior claim from Claude itself, verify independently
  rather than trust at face value.
- Any parameter assigned to a variable (rho, coup_friction, box
  dimensions, mass, thresholds) must trace to a primary source before
  being written into a script or command.
- Do not accept a physical result on intuition. State the formula or
  law used, do a units check, and compare against these anchors: water
  1000 kg/m^3, vehicle effective density 100-300 kg/m^3 band, sedan
  mass 1000-1600 kg, g=9.81, realistic depth 0-1.0m, velocity
  0-3.0 m/s. coup_friction is a numerical stability coefficient, NOT
  physical mu, physical mu is 0.3-0.55 per Azhar et al. 2023.
- For any rendered output: water reads as one connected fluid body,
  vehicle position matches its known density, no particles outside
  domain or clipped through geometry, motion continuous across frames.
- rho, coup_friction, box dimensions, mass, and grid resolution are
  coupled. Never flag a value as wrong by pattern-analogy to a
  different script's bug, recompute against the actual script's own
  geometry.
- Never let two panes touch the same file, branch, or process without
  explicit sequencing.
- Any git push, force-push, file delete, or overwrite of an existing
  file requires explicit confirmation before execution.
- Every prescribed task should trace to the poster (July 27), the
  paper (July 31), or a verified rendered physically-plausible MPM
  simulation with a vehicle. Flag anything else as optional/deferred.
- If a specific pane's blocking issue persists unresolved across 3+
  rounds, stop re-prescribing the same diagnostic, escalate to
  Cristian Moran per the 15-minute-stuck rule.
- Prefer event-driven pane signaling over polling: same machine, tmux
  wait-for; same machine automated, a Claude Code Stop hook;
  cross-machine, ntfy.
- Before prescribing idev/GPU allocation, confirm the task actually
  needs GPU. File checks, git operations, and monitoring belong on the
  login node, not inside idev.
- Before asserting any parameter, threshold, citation, mesh property, or
  milestone as fact, read docs/VERIFIED_FACTS_LEDGER_july24.md. Section B
  lists claims already proven false. Section F is the complete vehicle
  asset inventory: there is ONE usable mesh, not three. Do not re-derive
  anything in Section A.

## git filter-repo standing note
--path/--invert-paths and --replace-text are independent passes, filter-repo
does not combine them automatically. A rewrite touching an existing repo
(not a fresh clone) requires --force or it aborts safely rather than doing
nothing. After any filter-repo rewrite, --force --all pushes the FULL pack
again, not a diff, large repos with binary history take real time, cutoff
mid-transfer in a terminal paste does not mean it failed.

## File provenance, do not cite anything not on this list without checking it live

CANONICAL:
- CLAUDE.md (this file, project root) — Multi-Pane Standing Rules
- vehicle_params.py — mass_kg: 1100.0
- vehicle_geometry_research/yaris_coarse_v1l_watertight.ply — canonical Yaris mesh

DEPRECATED, do not read or cite:
- vehicle_geometry_research/yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply
- reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B
- data/track1_sweep_v3/
- docs/session_notes/2026-07-16_l1_l2_dxv_crossref.md
- files/CLAUDE_md_*_july13.md
