# SLOT d8-naming

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-naming, branch claude/r8-naming
(off claude/add-ci-checks).

You may write ONLY, inside YOUR worktree:
  analysis/build_runs_inventory.py
  analysis/check_run_validity_2026-08-10.py
  analysis/classify_three_class_matched.py
  analysis/make_poster_figures.py  and its _BIG, _BIG_GRIDAWARE, _GRIDAWARE variants
  renders/yaris_render_s1/sim_standing.py
  renders/yaris_render_s1/_incoming/sim_standing.py
  renders/yaris_render_s3_enhanced/sim_enhanced.py
  renders/yaris_render_s1/gates_all_runs.py
  analysis/render_v1/as_ran_local_copies/sim_standing.py
  docs/R8_DETERMINISM_RENAME_2026-08-18.md  (new)

NEVER TOUCH: simulation/failure_modes.py; data/*.csv or data/*.json (do NOT regenerate any
artifact); any other branch; the main checkout.

## THE DEFECT, stated precisely because two true statements look contradictory
  sim_standing.py:389   det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
  That is a particle count and a grid limit. It is not determinism.
  data/all_runs_inventory.csv reads determinism_identical = True on 17 of 17 rows (verified
  live: 17 rows, 42 columns, all True).
  Every trajectory nonetheless differs: all 20 A2 repeats are bit-different at every grid, with
  divergence by the first recorded frame.
So the FIELD VALUE and "false in practice" do NOT contradict each other. THE NAME DOES.

Ledger instruction: rename to hull_load_identical; do NOT delete it, because hull loading
genuinely IS bit-identical and that is what localises the nondeterminism to the solve.

## THE PUBLICATION-FACING HALF, which matters more than the rename
make_poster_figures.py:167 and its variants print
  "1100 kg, all runs deterministic (determinism_identical = True)."
That caption asserts the opposite of the measured state. Sites also at :565 and :602.
An adversarial pass puts the total at 23 sites across 9 files and says it reached the PRESENTED
poster PDF and three handoff copies bound for Kumar. My own count found 4 writers and 2
generators. The ledger says 5 writers and 7 generators. THREE SCOPES, NOT THREE ANSWERS.
RE-DERIVE IT, print the enumeration, and STATE YOUR SCOPE.

## A TRAP
renders/yaris_render_s1/sim_standing.py and renders/yaris_render_s1/_incoming/sim_standing.py are
TWO DIFFERENT FILES and register D4a records _incoming/ as the canonical per-run tree. Only 2 of
the 24 .py files under renders/yaris_render_s1/ are tracked (sim_standing.py and vehicle_live.py,
committed in 00b735c). Verify with
  git -C /Users/josie/can-it-ford ls-files --cached -- renders/yaris_render_s1/
before assuming an edit is version-controlled.

## YOU ARE NOT REGENERATING ARTIFACTS
Renaming a JSON key changes what future runs write. Every existing summary.json and
gates_results_all_runs.json keeps the old key. Your rename MUST be backward-compatible on read
(accept both keys) and forward-only on write. Say so in the code and the commit message.
gates_all_runs.py:105 already does `s.get("determinism_identical", "ABSENT")`, the pattern to follow.

## FIRST STEP
  /usr/bin/grep -rn 'determinism_identical' --include='*.py' /Users/josie/can-it-ford | /usr/bin/grep -vE '\.claude/worktrees|third_party|__pycache__' || true
Enumerate every site and print the list before changing one.

## DEFINITION OF DONE
1. Every site renamed, backward-compatible reads, enumeration in the commit message with scope.
2. The poster captions no longer assert "all runs deterministic". They state what is true: hull
   loading is bit-identical, trajectories are not.
3. No data/ artifact regenerated, and you say so.
4. A statement of what would break if someone regenerated them, so nobody does it casually.
