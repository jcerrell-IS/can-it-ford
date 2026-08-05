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
  0-3.0 m/s. coup_friction IS the Coulomb friction coefficient in the
  LegacyCoupler MPM-rigid momentum exchange
  (genesis/engine/couplers/legacy_coupler.py:322), applied as
  |v_t_new| = max(0, |v_t| - mu*|v_n|). The separate numerical
  regularisation parameter is coup_softness, default 0.002. Confirmed
  2026-08-05 by direct source read, superseding all earlier statements
  that coup_friction was numerical-only.
- grid_density >= 96 is NOT the crash threshold and 64 is NOT
  confirmed safe. Replicated bisection 2026-08-05 found gd 80 and 88
  pass 3/3 at 60 steps, gd 90+ fails, non-monotone above the boundary,
  non-deterministic at fixed config. Before citing any grid_density
  as safe, check can-it-ford-audit/2026-08-04/CONFIRMED_FACTS_LEDGER.md.
- Before treating any claim in this file as settled: a claim cited
  from another session's confidence, a skill file, or a prior audit's
  conclusion is not a second source, it is the same source cited
  twice. Only a primary-source line, a runtime read, or a replicated
  control counts as verification. Before archiving or superseding any
  dated audit file, pull its VERIFIED-tier findings into
  CONFIRMED_FACTS_LEDGER.md first, the file can go stale, the facts
  inside it should not disappear with it.
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
- data/track1_sweep_v2/ — superseded box-proxy sweep (1390 kg box, 4.7352 m3
  solid volume vs the real hull's 3.542739 m3). Not archived, because
  analysis/gp_surrogate.py and analysis/build_poster_phase_space.py still read
  it and .gitignore lines 17-18 explicitly un-ignore it. Do not source a paper
  figure or a density number from it; use data/all_runs_inventory.csv instead.

## Nested ./can-it-ford/ duplicate directory, do not read data from it

There is a second copy of this project nested at ./can-it-ford/ inside the repo
root. It is NOT a synced mirror. Verified live 2026-07-29 by filecmp: paper/
conference_101719.tex and paper/can_it_ford_references_IEEE.bib are byte-identical
between root and nested, but data/scenario_sweep.csv, vehicle_params.py and
scripts/ford_sweep_driver.py all DIFFER. Root is canonical for every one of them.
Always confirm pwd is /Users/josie/can-it-ford, not the nested copy, before
reading a parameter or a verdict count, and exclude ./can-it-ford/ from repo-wide
greps or you will get two conflicting answers and no way to tell which is live.
