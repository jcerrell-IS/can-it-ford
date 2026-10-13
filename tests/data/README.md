# Test fixtures

Small copies of real run output, so the data tests in `tests/` run in CI on a clean checkout. The full
outputs (particle rollouts of 23 to 232 MB per run) are not in this repository. Every file here is
rebuilt by `build_fixtures.py`, and `SHA256SUMS` lists its hash; the hashes of the source files it read
are inside `rollout_shapes.json` and `stage1e_matched_window.json`.

| File | What it is |
|---|---|
| `runs/<run>/metrics.csv` | Byte-for-byte copy of the per-frame record of each of the 17 gated coupled runs listed in `data/all_runs_inventory.csv`: time, vehicle displacement, rotation, linear and angular velocity, 91 rows (t = 0 to 3 s at 30 frames per second). |
| `rollout_shapes.json` | The array shapes inside each run's `rollout.npz`, read from the file headers, plus the sha256 of each rollout. |
| `stage1e_matched_window.json` | Grid spacing, mean streamwise force `Fx` (N) and its standard error over the matched averaging window, for the three grid levels of the Stage 1e steady-current ladder at 0.30 m and 1.5 m/s. |
| `legacy_gci_stage1.py` | The older three-grid GCI function, copied verbatim, so `tests/test_gci_least_squares.py` can compare against it. |

What these runs are and are not. The 17 runs set all the water moving in one step inside a closed
tank, so their records describe a start-up surge, not a steady current; their FORD and NO-FORD
labels are withdrawn as verdicts (see `FINDINGS.md`). The tests use them as recorded data: they check
that the records are finite and bounded, that the rollouts hold the particle counts the runs recorded,
and that the recorded move-or-stay labels do not change silently. No drag coefficient is included,
because none from these campaigns is valid; the Stage 1e forces are not grid-converged (the test that
reads them says so) and are not a physical load.
