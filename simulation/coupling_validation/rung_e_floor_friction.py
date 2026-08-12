"""
rung_e_floor_friction.py

The rung `docs/REGIME_LADDER_RESULTS_2026-08-07.md` section 8 names and did not run:
**floor friction**. Everything else is held at the values that file already validated.

WHY THIS RUNG AND NOT A RE-RUN OF RUNG (b)
  Rung (b) is DONE. Job 895653, Vista c609-141, 2026-08-07, COMPLETED 00:01:38, exit
  0:0, artifacts data/coupling_validation/ladder_b_g{64,96}.{json,log}, written up at
  REGIME_LADDER_RESULTS section 5.2. Its g96 arm reads a_late_window +0.608004 against
  an analytic -6.5713, so -9.25 percent with the SIGN INVERTED; its g64 arm is a
  discard. Re-running it would re-measure a known number.

  What is NOT known is whether that defect moves the 17 gated VERDICTS. Section 8 gives
  three reasons the ladder cannot yet say, and only one of them is cheap to close:

    "Floor friction. This ladder walked restitution only. Its floor stays at BoxTank's
     friction=0.0; the 17 gated runs carry floor_friction=0.55 (sim_standing.py:132).
     Since section 5.3 concludes any buoyancy error in this regime lands in the normal
     force, and sliding resistance is friction times normal force, floor friction is the
     obvious next rung and it was not run here."

  That is the path to the verdicts. 16 of the 17 published verdicts are SLIDE, SLIDE is
  a displacement-and-speed criterion (failure_modes.py:179-181), and the only route from
  a vertical buoyancy error to a horizontal displacement is through mu*N. With mu = 0 the
  existing ladder short-circuits exactly that route, so it CANNOT have observed the
  effect even in principle. This rung restores mu.

  `enable_floor_restitution` already anticipated this. Its own docstring
  (validate_coupling_force_ladder.py:186-188) says friction "defaults to 0.0, matching
  BoxTank's own floor ... The 17 gated runs additionally carry floor friction 0.55
  (sim_standing.py:132); that is a THIRD variable and this ladder does not walk it."
  This script walks it, by passing the parameter that function already exposes.

WHAT IS NEW HERE AND WHAT IS NOT
  New: the value of one keyword argument, and seed replication at g64.
  Not new: the geometry, the settle procedure, the measurement window, the analytic
  reference, the guard, and every constant. All are imported. This file edits NOTHING.
  `validate_coupling_force.py` and `validate_coupling_force_ladder.py` are imported
  read-only and never written, per the standing instruction covering both.

ARMS, and why each one is present
  Every friction arm is paired with a mu=0 control run in the SAME job, on the same code
  revision and the same node. The 2026-08-07 numbers are NOT used as the control: they
  came from a different job on a different node, and section 5.5 records that the g64
  settle is non-deterministic at fixed configuration, so a cross-job comparison could not
  separate a friction effect from a settle draw.

    c_g64  seeds 0,1,2   mu=0.00   control, and the settle spread section 8 asks for
    e_g64  seeds 0,1,2   mu=0.55   treatment, same spread
    c_g96  seed 0        mu=0.00   control at the settled grid
    e_g96  seed 0        mu=0.55   treatment at the settled grid
    d_g96  seed 0        mu=0.00   control, with inflow, the closest arm to a gated run
    f_g96  seed 0        mu=0.55   treatment, with inflow

  Rung e is rung (c) plus friction. Rung f is rung (d) plus friction. The letters are
  local to this file and are NOT promoted into the register unless a result earns it.

  g64 carries the replicates because g64 is where section 5.5 saw the non-determinism.
  g96 settled in 20 frames in job 895653 at both rungs, so one draw is defensible there;
  if a g96 arm reports settle_gate_met False, treat it as a discard exactly as the
  dispatch's own rule requires, and do not quote it.

READ BEFORE QUOTING ANY NUMBER THIS PRODUCES
  A resting body's correct vertical acceleration is ZERO (section 5.3). Rungs c/e/d/f all
  rest on the floor, so a near-zero a_late_window is EXPECTED and is not by itself
  evidence of anything. This rung is not trying to re-measure buoyancy. It is asking a
  narrower question: does adding mu=0.55 change the body's behaviour at all, and in
  particular does it change the horizontal channel that SLIDE is scored on. Compare the
  friction arm against ITS OWN paired control, never against an absolute expectation.

  A null result is a real result here and must be reported as one. If mu changes nothing
  measurable, that is evidence the coupling defect does not reach the SLIDE verdicts
  through this path, which is worth more to the paper than a re-measured -9.25 percent.

Usage
  python simulation/coupling_validation/rung_e_floor_friction.py \
      --out-dir $WORK/can-it-ford/data/coupling_validation --device cuda:0
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))

import validate_coupling_force_ladder as L  # noqa: E402

# sim_standing.py:132, the gated floor. Read live 2026-08-07 per the ladder's own
# provenance block, which records "floor restitution=0.05 friction=0.55".
GATED_FLOOR_FRICTION = 0.55

_ENABLE_ORIG = L.enable_floor_restitution


def _enable_with_friction(tank, restitution=L.FLOOR_RESTITUTION,
                          friction=GATED_FLOOR_FRICTION):
    """Same call the ladder makes, with the one argument it never varied."""
    return _ENABLE_ORIG(tank, restitution=restitution, friction=friction)


def run_arm(base_rung, mu, n_grid, seed, args):
    """One arm. base_rung is the ladder rung whose scene we reuse ('c' or 'd').

    run_rung() looks `enable_floor_restitution` up as a module global at call time
    (validate_coupling_force_ladder.py:390), so swapping the module attribute is enough
    and no ladder source is touched. It is restored in a finally block so a crash in one
    arm cannot silently leak friction into the next.
    """
    L.enable_floor_restitution = _enable_with_friction if mu else _ENABLE_ORIG
    t0 = time.time()
    try:
        res = L.run_rung(base_rung, n_grid,
                         settle_frames=args.settle_frames,
                         measure_substeps=args.measure_substeps,
                         flow_frames=args.flow_frames,
                         velocity=args.velocity,
                         device=args.device,
                         seed=seed)
    finally:
        L.enable_floor_restitution = _ENABLE_ORIG

    res["floor_friction"] = float(mu)
    res["base_rung"] = base_rung
    res["seed"] = seed
    res["wall_s"] = round(time.time() - t0, 2)
    res["arm_provenance"] = {
        "script": "simulation/coupling_validation/rung_e_floor_friction.py",
        "walks": "floor friction only; every other variable is imported unchanged",
        "friction_source": "renders/yaris_render_s1/sim_standing.py:132, floor "
                           "restitution=0.05 friction=0.55",
        "why": "REGIME_LADDER_RESULTS_2026-08-07.md section 8 names floor friction as "
               "the obvious next rung and records that it was not run. Section 5.3 puts "
               "any buoyancy error in this regime into the normal force, and sliding "
               "resistance is mu*N, so this is the only cheap path from the coupling "
               "defect to the SLIDE verdicts.",
        "control_pairing": "each mu=0.55 arm has a mu=0.0 arm at the same grid and seed "
                           "in this same job. The 2026-08-07 numbers are NOT the control: "
                           "different job, different node, and section 5.5 records g64 "
                           "settle non-determinism at fixed config.",
        "rung_b_status": "ALREADY DONE, job 895653, not re-run here. See section 5.2.",
    }
    return res


def summarise(res):
    """The fields that decide whether an arm is usable and whether mu did anything."""
    return {
        "settle_gate_met": res.get("settle_gate_met"),
        "settle_is_discard": res.get("settle_is_discard"),
        "restitution_registered": res.get("restitution_registered"),
        "submerged_frac": res.get("submerged_frac"),
        "submerged_frac_at_end": res.get("submerged_frac_at_end"),
        "a_ideal_partial": res.get("a_ideal_partial"),
        "a_late_window": res.get("a_late_window"),
        "a_late_as_fraction_of_ideal": res.get("a_late_as_fraction_of_ideal"),
        "box_bottom_travel_m": res.get("box_bottom_travel_m"),
        "box_bottom_travel_dx": res.get("box_bottom_travel_dx"),
        "wall_s": res.get("wall_s"),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--settle-frames", type=int, default=1200)
    p.add_argument("--measure-substeps", type=int, default=160)
    p.add_argument("--flow-frames", type=int, default=60)
    p.add_argument("--velocity", type=float, default=L.MATCH_VELOCITY)
    p.add_argument("--g64-seeds", type=int, default=3,
                   help="replicates at g64, where section 5.5 saw settle non-determinism")
    p.add_argument("--smoke", action="store_true",
                   help="20-frame settle, 8-substep window, one arm. Numbers meaningless.")
    a = p.parse_args()

    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if a.smoke:
        a.settle_frames, a.measure_substeps = 20, 8
        plan = [("c", GATED_FLOOR_FRICTION, 64, 0, "smoke_e_g64")]
    else:
        plan = []
        for s in range(a.g64_seeds):
            plan.append(("c", 0.0, 64, s, f"fric_c_g64_mu000_s{s}"))
            plan.append(("c", GATED_FLOOR_FRICTION, 64, s, f"fric_e_g64_mu055_s{s}"))
        plan.append(("c", 0.0, 96, 0, "fric_c_g96_mu000_s0"))
        plan.append(("c", GATED_FLOOR_FRICTION, 96, 0, "fric_e_g96_mu055_s0"))
        plan.append(("d", 0.0, 96, 0, "fric_d_g96_mu000_s0"))
        plan.append(("d", GATED_FLOOR_FRICTION, 96, 0, "fric_f_g96_mu055_s0"))

    print(f"planned arms: {len(plan)}")
    print(f"GATED_FLOOR_FRICTION = {GATED_FLOOR_FRICTION}  "
          f"(ladder default was {_ENABLE_ORIG.__defaults__})")

    failed, index = 0, []
    for base_rung, mu, n_grid, seed, tag in plan:
        print(f"\n########## {tag}  rung={base_rung} mu={mu} g{n_grid} seed={seed} ####")
        try:
            res = run_arm(base_rung, mu, n_grid, seed, a)
        except Exception as exc:                      # one arm must not kill the rest
            failed += 1
            print(f"STATUS {tag} FAILED {type(exc).__name__}: {exc}")
            index.append({"tag": tag, "status": "FAILED", "error": repr(exc)[:300]})
            continue
        (out_dir / f"{tag}.json").write_text(json.dumps(res, indent=2, default=float))
        s = summarise(res)
        print(f"STATUS {tag} rc=0")
        print(json.dumps(s, indent=2, default=float))
        index.append({"tag": tag, "status": "OK", "base_rung": base_rung,
                      "floor_friction": mu, "n_grid": n_grid, "seed": seed, **s})

    (out_dir / "fric_index.json").write_text(json.dumps(index, indent=2, default=float))
    print(f"\nwrote {out_dir/'fric_index.json'}")
    print(f"ALLDONE_FRICTION failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
