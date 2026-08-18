#!/usr/bin/env python3
"""Run sim_standing.py with a varied initial-condition seed, WITHOUT editing it.

WHY. The settling report (Undermind, 2026-08-14, numerical reproducibility
section) states: "Repeated runs should report outcome spread and gate-pass
frequency; no universal repeat count exists, while independent-start ensembles
are the stronger convergence check." It also warns that "non-associative,
order-dependent reductions can produce small drift or ALTER DISCRETE GATES",
which is a direct hit on a SLIDE / STUCK / FLOAT verdict.

THE GAP THIS CLOSES. sim_standing.py:155 takes `seed=0`, and :165 and :183 use it
for the initial water-particle jitter, +/- 0.2h on every water particle. main()
at :397 NEVER passes a seed, so every run in the three-class set so far shares
ONE initial condition. Repeats of an identical configuration measure solver and
reduction-order noise; they do not measure sensitivity to the initial state.

WHY A WRAPPER AND NOT A --seed FLAG. Adding the flag would change the driver
sha256 that stamps all 24 completed runs in
docs/THREE_CLASS_MATCHED_2026-08-14.md, and several dispatches share that file.
This subclasses the scene and injects the seed at construction, so the driver
file is untouched and its digest is unchanged.

FIDELITY CHECK BUILT IN: seed 0 must reproduce the existing runs, because that is
the value main() has always used implicitly. If seed 0 does NOT reproduce, the
wrapper is wrong and nothing else here is trustworthy.

Usage: ENSEMBLE_SEED=<int> python3 ensemble_seed_runner.py <normal sim_standing args>
"""
import os
import sys
from pathlib import Path

REPO = Path(os.environ.get("CANFORD_REPO", "/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford"))
sys.path.insert(0, str(REPO / "renders" / "yaris_render_s1"))

import sim_standing as S  # noqa: E402

SEED = int(os.environ.get("ENSEMBLE_SEED", "0"))
_Orig = S.StandingFloodScene


class SeededScene(_Orig):
    """Identical to StandingFloodScene except the initial-jitter seed is injected."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("seed", SEED)
        super().__init__(*args, **kwargs)


S.StandingFloodScene = SeededScene
print("ENSEMBLE_SEED=%d" % SEED, flush=True)
S.main()
