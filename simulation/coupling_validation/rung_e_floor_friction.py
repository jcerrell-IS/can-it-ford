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


# ======================================================================================
# HORIZONTAL INSTRUMENTATION, added 2026-08-13
#
# WHY. Section 4 of docs/FLOOR_FRICTION_RUNG_2026-08-12.md records the limitation that
# bounds every number this rung produced: the harness records VERTICAL motion only.
# Confirmed again live 2026-08-13 by walking all 55 keys of each of the four g96 arm
# JSONs on Vista: the only x-named fields are flow/inflow_x_m, a scalar geometry
# constant, and flow/water_vx_near_box_{before,after}, which are WATER statistics near
# the body, not the BODY's own state. No body x-position or x-velocity exists on disk
# for any arm.
#
# SLIDE is horizontal. failure_modes.py:180 requires surge_drift >= slide_m AND
# surge_speed >= slide_speed_ms, sustained, with surge_drift = |disp[:, SURGE_AXIS]|
# and SURGE_AXIS = 0 (failure_modes.py:16). So the rung could not speak to the 16 of 17
# SLIDE verdicts at all. This block records the missing channel.
#
# WHAT IS AND IS NOT NEW. New: recording. NOT new: any physics. The recorder only reads
# solver.rigid_state(), which copies warp arrays to host numpy and writes nothing back
# (core/solver.py:200-211). No ladder source is edited: this wraps two bound methods on
# the constructed BoxTank instance at runtime, the same monkeypatch discipline the file
# already uses for enable_floor_restitution.
#
# HOW THE PHASES ARE SEPARATED WITHOUT EDITING THE LADDER. run_rung has three stepping
# phases and no hook between them. They are told apart at the step() call site:
#   settle   n_substeps == tank.substeps, and tank.pin() is called immediately after
#            (validate_coupling_force.py:617-630), which rewrites rigid_x_cm and zeroes
#            v_cm, so x is reset every frame and settle drift MUST come out ~0. That is
#            the recorder's own self-check, not a result.
#   flow     n_substeps == tank.substeps, no pin. Rung d/f only. The body is FREE here
#            for flow_frames frames while inflow is sustained, so this is the longest
#            horizontal window in the run and the one closest to a gated scene.
#   measure  n_substeps == 1, the substep-resolution window run_rung fits a_late over.
# The pin flag is what separates settle from flow, so the classification does not depend
# on substeps > 1 and stays correct if a future grid gives substeps == 1.
#
# AXIS. The tank's x IS the flow axis: sustain_inflow and kick_water drive vx, and the
# inflow band is placed on x (validate_coupling_force_ladder.py:398). That matches
# SURGE_AXIS = 0. The (L,W,H) axis transposition recorded in CLAUDE.md item 4(c) is a
# property of the Yaris hull in the gated scene and does NOT apply here: this rung's body
# is a cube, so no axis remapping is needed or performed.
# ======================================================================================

_HTRACE: dict = {}


def _htrace_reset():
    """One arm's trace. Module-level because the tank is constructed inside run_rung."""
    _HTRACE.clear()
    _HTRACE.update({k: [] for k in ("n", "x", "y", "z", "vx", "vy", "vz", "pinned")})


def _attach_horizontal_recorder(tank):
    """Wrap solver.step and tank.pin on ONE instance. Read-only; returns nothing.

    Both are wrapped as instance attributes, so the class is untouched and a second
    BoxTank built later in the same process is unaffected. Every call site in the ladder
    reaches these through normal attribute access (`tank.solver.step(...)`,
    `tank.pin(...)`), so an instance attribute is sufficient to intercept all of them.
    """
    rec = _HTRACE
    orig_step = tank.solver.step
    orig_pin = tank.pin

    def step(dt, n_substeps, *a, **kw):
        out = orig_step(dt, n_substeps, *a, **kw)
        st = tank.solver.rigid_state()
        com, v = st["com"], st["v"]
        rec["n"].append(int(n_substeps))
        rec["x"].append(float(com[0]))
        rec["y"].append(float(com[1]))
        rec["z"].append(float(com[2]))
        rec["vx"].append(float(v[0]))
        rec["vy"].append(float(v[1]))
        rec["vz"].append(float(v[2]))
        rec["pinned"].append(False)
        return out

    def pin(com):
        out = orig_pin(com)
        if rec["pinned"]:
            rec["pinned"][-1] = True    # this frame's sample was a pinned settle frame
        return out

    tank.solver.step = step
    tank.pin = pin


def install_horizontal_instrumentation():
    """Patch vcf.BoxTank so every tank run_rung builds records its own horizontal trace.

    run_rung calls `vcf = _load_vcf()` then `vcf.BoxTank(...)`
    (validate_coupling_force_ladder.py:366, :374). importlib caches the module, so
    setting the attribute on the module object returned here is the same object run_rung
    will look the class up on. Returns the vcf module so the caller can record its md5.
    """
    vcf = L._load_vcf()
    base = vcf.BoxTank
    if getattr(base, "_horizontal_instrumented", False):
        return vcf

    class _InstrumentedBoxTank(base):                      # noqa: N801
        _horizontal_instrumented = True

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            _attach_horizontal_recorder(self)

    vcf.BoxTank = _InstrumentedBoxTank      # type: ignore[attr-defined]
    return vcf


def slide_thresholds():
    """Read the SLIDE thresholds LIVE from failure_modes rather than restating them.

    Restating 0.05 here would add a sixth declaration site to the five CLAUDE.md item 13
    already tracks, and item 13's own warning applies: slide_m and slide_speed_ms share
    the numeral 0.05 but are a DISTANCE and a SPEED. They are read by name, never by
    value, and the unit is carried in the key.
    """
    try:
        import failure_modes as FM
        th = FM.FailureThresholds()
        return {
            "slide_m": float(th.slide_m),
            "slide_speed_ms": float(th.slide_speed_ms),
            "sustain_frames": int(th.sustain_frames),
            "surge_axis": int(FM.SURGE_AXIS),
            "source": "simulation/failure_modes.py FailureThresholds() defaults, "
                      "read live at run time, not restated",
        }
    except Exception as exc:                               # never kill an arm over this
        return {"error": f"could not read thresholds live: {exc!r}"}


def _blocks():
    """Split the recorded trace into (settle, flow, measure) index lists."""
    pinned, n = _HTRACE["pinned"], _HTRACE["n"]
    settle = [i for i in range(len(n)) if pinned[i]]
    measure = [i for i in range(len(n)) if not pinned[i] and n[i] == 1]
    flow = [i for i in range(len(n)) if not pinned[i] and n[i] != 1]
    return settle, flow, measure


def _window_stats(idx, x_ref, dt_per_sample):
    """Drift and speed over one block, in the same sense failure_modes uses.

    max_surge_drift there is max(|disp_x|) (failure_modes.py:189) and surge_speed is
    |vel_x| (:168), both ABSOLUTE, so sign is deliberately discarded here too. The
    signed net displacement is kept alongside because a body that oscillates about its
    release point and one that translates steadily are different physics, and the
    absolute-value convention alone cannot tell them apart.
    """
    if not idx:
        return None
    xs = [_HTRACE["x"][i] for i in idx]
    vxs = [_HTRACE["vx"][i] for i in idx]
    disp = [v - x_ref for v in xs]
    half = len(vxs) // 2
    late = vxs[half:] or vxs
    # Two different quantities, and conflating them would misread the measure block.
    # surge_drift_max_abs_m is CUMULATIVE from release, which is what failure_modes
    # scores (its disp is measured from the run's start). within_block is the drift
    # accrued inside this block alone. For rung d/f the measure block is preceded by a
    # 60-frame free flow block, so the cumulative figure there mostly reports what the
    # flow block already did, and only within_block isolates the measurement window.
    within = [v - xs[0] for v in xs]
    return {
        "n_samples": len(idx),
        "sample_dt_s": dt_per_sample,
        "window_s": len(idx) * dt_per_sample,
        "x_at_reference_m": x_ref,
        "x_at_block_start_m": xs[0],
        "x_final_m": xs[-1],
        "surge_disp_net_signed_m": disp[-1],
        "surge_drift_max_abs_m": max(abs(d) for d in disp),
        "surge_drift_within_block_max_abs_m": max(abs(d) for d in within),
        "surge_disp_within_block_net_signed_m": within[-1],
        "surge_speed_max_abs_ms": max(abs(v) for v in vxs),
        "surge_speed_late_mean_abs_ms": sum(abs(v) for v in late) / len(late),
        "surge_speed_final_abs_ms": abs(vxs[-1]),
    }


def _sustained(idx, x_ref, th, sustain):
    """Joint SLIDE mask over one block, sustained for `sustain` consecutive samples.

    This mirrors failure_modes._first_sustained_index (:133-147) on the two clauses this
    harness can actually evaluate. It deliberately does NOT claim a SLIDE verdict: the
    real classifier ANDs in driven_downstream, max|surge_force| > 0 (:176, :193), and
    this scene has no force accumulator to produce it. See CLAUDE.md A-1: the material-8
    free-rigid path exchanges momentum by mass-weighted grid velocity averaging and
    accumulates no contact force. So what is returned is the KINEMATIC pair only.
    """
    if not idx or "error" in th:
        return None
    run = 0
    for i in idx:
        d = abs(_HTRACE["x"][i] - x_ref)
        s = abs(_HTRACE["vx"][i])
        if d >= th["slide_m"] and s >= th["slide_speed_ms"]:
            run += 1
            if run >= sustain:
                return True
        else:
            run = 0
    return False


def horizontal_summary(res):
    """Derive the horizontal result block from the trace recorded during this arm."""
    th = slide_thresholds()
    dt = float(res.get("dt") or 0.0)
    substeps = int(res.get("substeps_per_frame") or 1)
    settle, flow, measure = _blocks()

    if not _HTRACE.get("x"):
        return {"error": "no horizontal samples recorded; instrumentation did not attach"}

    # Displacement reference. failure_modes measures disp from the run's own start; here
    # the body is pinned through settle, so the physically meaningful zero is the state
    # at RELEASE, the last pinned sample. Falling back to the first sample only matters
    # if settle recorded nothing, which would itself be a defect worth seeing.
    x_release = _HTRACE["x"][settle[-1]] if settle else _HTRACE["x"][0]
    x_settle0 = _HTRACE["x"][settle[0]] if settle else None

    frame_dt = dt * substeps
    out = {
        "thresholds": th,
        "x_at_release_m": x_release,
        "blocks": {
            "settle": _window_stats(settle, x_settle0 if settle else x_release, frame_dt),
            "flow": _window_stats(flow, x_release, frame_dt),
            "measure": _window_stats(measure, x_release, dt),
        },
        "settle_pin_selfcheck": {
            "what": "the body is pinned every settle frame, so settle drift must be ~0",
            "surge_drift_max_abs_m": (None if not settle else
                                      max(abs(_HTRACE["x"][i] - x_settle0)
                                          for i in settle)),
            "reads_as_expected": None,
        },
    }
    sc = out["settle_pin_selfcheck"]
    if sc["surge_drift_max_abs_m"] is not None:
        sc["reads_as_expected"] = bool(sc["surge_drift_max_abs_m"] < 1e-9)

    if "error" not in th:
        sustain = th["sustain_frames"]
        out["slide_kinematic_pair_met"] = {
            "flow_frame_cadence": _sustained(flow, x_release, th, sustain),
            "measure_substep_cadence": _sustained(measure, x_release, th, sustain),
            "cadence_note": (
                "the classifier's sustain_frames is 3 FRAMES of metrics.csv. Flow samples "
                f"are one per frame, so that block is directly comparable. Measure samples "
                f"are one per SUBSTEP, {substeps} per frame at this grid, so 3 consecutive "
                "measure samples are a shorter physical time than the classifier means. "
                "Read the measure result as indicative only."),
            "driven_downstream_evaluable": False,
            "driven_downstream_reason": (
                "failure_modes.py:176 also requires max|surge_force| > 0. The material-8 "
                "free-rigid path accumulates no contact force (CLAUDE.md A-1), so this "
                "harness cannot evaluate that clause and does NOT report a SLIDE verdict."),
        }
    return out


def run_arm(base_rung, mu, n_grid, seed, args):
    """One arm. base_rung is the ladder rung whose scene we reuse ('c' or 'd').

    run_rung() looks `enable_floor_restitution` up as a module global at call time
    (validate_coupling_force_ladder.py:390), so swapping the module attribute is enough
    and no ladder source is touched. It is restored in a finally block so a crash in one
    arm cannot silently leak friction into the next.
    """
    L.enable_floor_restitution = _enable_with_friction if mu else _ENABLE_ORIG
    _htrace_reset()
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
    # Additive only. Nothing above is renamed, removed or recomputed, so an arm produced
    # by this revision stays diffable against the 2026-08-12 arms on every prior key.
    res["horizontal"] = horizontal_summary(res)
    res["x_series_by_block"] = {
        "note": "index lists into the flat trace, so the three blocks stay alignable",
        "x": _HTRACE["x"], "vx": _HTRACE["vx"],
        "n_substeps": _HTRACE["n"], "pinned": _HTRACE["pinned"],
    }
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
        "code_md5": _code_md5(),
    }
    return res


def _code_md5():
    """md5 of the three files whose content decides this arm's physics.

    Recorded per arm so a later reader can prove, rather than assume, that an
    instrumented arm and a 2026-08-12 arm share the ladder revision. The ladder is the
    one that must match: f650d762635fb3415d2cf202f5a5c979.
    """
    import hashlib
    out = {}
    for rel in ("simulation/validate_coupling_force_ladder.py",
                "simulation/validate_coupling_force.py",
                "simulation/coupling_validation/rung_e_floor_friction.py"):
        p = REPO / rel
        try:
            out[rel] = hashlib.md5(p.read_bytes()).hexdigest()
        except OSError as exc:
            out[rel] = f"unreadable: {exc!r}"
    return out


def summarise(res):
    """The fields that decide whether an arm is usable and whether mu did anything."""
    out = {
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
    # The horizontal channel, flattened into the index so the SLIDE comparison can be
    # made from fric_index.json alone without opening ten per-arm files.
    h = res.get("horizontal") or {}
    blocks = h.get("blocks") or {}
    for name in ("flow", "measure"):
        b = blocks.get(name) or {}
        out[f"surge_drift_{name}_m"] = b.get("surge_drift_max_abs_m")
        out[f"surge_disp_net_{name}_m"] = b.get("surge_disp_net_signed_m")
        out[f"surge_speed_{name}_max_ms"] = b.get("surge_speed_max_abs_ms")
        out[f"surge_speed_{name}_late_ms"] = b.get("surge_speed_late_mean_abs_ms")
    pair = h.get("slide_kinematic_pair_met") or {}
    out["slide_pair_met_flow"] = pair.get("flow_frame_cadence")
    out["slide_pair_met_measure"] = pair.get("measure_substep_cadence")
    out["settle_pin_selfcheck_ok"] = (h.get("settle_pin_selfcheck") or {}).get(
        "reads_as_expected")
    return out


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
    p.add_argument("--g96-only", action="store_true",
                   help="drop the six g64 arms. Five of those six were settle discards on "
                        "2026-08-12 and no g64 arm of this ladder is quotable, so a g64 "
                        "horizontal number would be unusable the moment it was measured.")
    p.add_argument("--tag-suffix", default="",
                   help="appended to every output tag, so an instrumented re-run cannot "
                        "silently overwrite the 2026-08-12 arms it must be compared to.")
    a = p.parse_args()

    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    vcf = install_horizontal_instrumentation()
    print(f"horizontal instrumentation attached to {vcf.BoxTank.__name__}")
    print(f"slide thresholds read live: {json.dumps(slide_thresholds())}")

    if a.smoke:
        a.settle_frames, a.measure_substeps = 20, 8
        plan = [("c", GATED_FLOOR_FRICTION, 64, 0, "smoke_e_g64")]
    else:
        plan = []
        if not a.g96_only:
            for s in range(a.g64_seeds):
                plan.append(("c", 0.0, 64, s, f"fric_c_g64_mu000_s{s}"))
                plan.append(("c", GATED_FLOOR_FRICTION, 64, s, f"fric_e_g64_mu055_s{s}"))
        plan.append(("c", 0.0, 96, 0, "fric_c_g96_mu000_s0"))
        plan.append(("c", GATED_FLOOR_FRICTION, 96, 0, "fric_e_g96_mu055_s0"))
        plan.append(("d", 0.0, 96, 0, "fric_d_g96_mu000_s0"))
        plan.append(("d", GATED_FLOOR_FRICTION, 96, 0, "fric_f_g96_mu055_s0"))

    if a.tag_suffix:
        plan = [(r, mu, g, s, t + a.tag_suffix) for r, mu, g, s, t in plan]

    print(f"planned arms: {len(plan)}")
    print(f"GATED_FLOOR_FRICTION = {GATED_FLOOR_FRICTION}  "
          f"(ladder default was {_ENABLE_ORIG.__defaults__})")

    index_name = f"fric_index{a.tag_suffix}.json"
    failed, index = 0, []
    for base_rung, mu, n_grid, seed, tag in plan:
        print(f"\n########## {tag}  rung={base_rung} mu={mu} g{n_grid} seed={seed} ####")
        # The write belongs INSIDE the try. Serialisation runs after the arm's GPU work
        # is already spent, and json.dumps(default=float) raises TypeError on anything
        # float() rejects (a numpy array of size > 1, for one). Outside the try that
        # exception escapes the loop and takes every remaining arm with it, which is
        # exactly what the guard below promises will not happen.
        try:
            res = run_arm(base_rung, mu, n_grid, seed, a)
            (out_dir / f"{tag}.json").write_text(json.dumps(res, indent=2, default=float))
            s = summarise(res)
        except Exception as exc:                      # one arm must not kill the rest
            failed += 1
            print(f"STATUS {tag} FAILED {type(exc).__name__}: {exc}")
            index.append({"tag": tag, "status": "FAILED", "error": repr(exc)[:300]})
            continue
        print(f"STATUS {tag} rc=0")
        print(json.dumps(s, indent=2, default=float))
        index.append({"tag": tag, "status": "OK", "base_rung": base_rung,
                      "floor_friction": mu, "n_grid": n_grid, "seed": seed, **s})
        # Rewritten after every arm, so a crash in a later arm cannot cost the index of
        # the ones that already succeeded.
        (out_dir / index_name).write_text(json.dumps(index, indent=2, default=float))

    (out_dir / index_name).write_text(json.dumps(index, indent=2, default=float))
    print(f"\nwrote {out_dir/index_name}")
    print(f"ALLDONE_FRICTION failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
