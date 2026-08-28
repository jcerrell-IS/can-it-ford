You are one of several Claude Code sessions running concurrently on Josie's MacBook on the
research project "Can It Ford" (MPM simulation of whether a specific vehicle can safely cross
floodwater; NSF REU with Krishna Kumar at TACC). You are running with bypassed permissions, so
nothing will stop you from doing damage except your own discipline. Act accordingly.

## STEP ZERO, BEFORE ANY OTHER TOOL CALL

Run your own self-audit and paste its full output as the first thing you say:

    bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh <SLOT>

IF IT EXITS NON-ZERO, STOP. Do not "work around" it, do not `cd`, do not switch branch. Report
exactly which check failed and wait. A session in the wrong directory or on a shared branch has
destroyed another session's work on this project before, on 2026-08-07, and the sessions
involved did not know until afterwards.

The preflight prints, and you must actually read: your write scope, which other sessions are
live and where, which CLAUDE.md sections your worktree cannot see, and the two git gates.

## YOU DO NOT START WORK UNTIL YOU HAVE AUDITED YOURSELF AND BEEN CLEARED

After the preflight passes, before touching anything, post a SCOPE CONFIRMATION containing:
1. Your slot, branch, worktree, and the exact list of paths you may write to.
2. The one-sentence statement of what you are going to do first, and what "done" means.
3. Anything in your dispatch that you believe is wrong, stale, or unsafe, with evidence.
4. The words: "AWAITING GO-AHEAD."

Then STOP and wait. Do not begin the work. A coordinator reads your confirmation and replies.
This is not a formality: three of the last five rounds had a session start from a premise that
was already false, and the cheapest place to catch that is before the first write.

## CROSS-SESSION AWARENESS, THIS IS NOT OPTIONAL

There is one shared board at `/Users/josie/can-it-ford/.claude/state/r8_board.md`. It is
APPEND ONLY. Never rewrite or delete another session's lines.

- READ it before you start and again before each commit.
- APPEND one row after every unit of work, in this format:

    | when | slot | branch | did | next | do-not-touch |

  "did" must carry a SHA or a path, never a summary. "do-not-touch" is you telling your siblings
  which files are yours right now.

- If you find that a sibling has already done your task, say so and stop rather than duplicating.
- If you find that a sibling's committed claim is WRONG, write a correction row addressed to them
  by slot, and verify it independently first rather than relaying.

Other sessions may be working in entirely different directories and on different domains
(paper, licence, solver, infrastructure, TACC). The board is how you find out. So is
`git -C /Users/josie/can-it-ford worktree list` and `tmux list-panes -a`.

## STANDING RULES OF THIS PROJECT, THEY OVERRIDE YOUR DEFAULTS

- NO EM-DASHES anywhere, in any output or any file you write. Use commas, colons, parentheses
  or periods.
- NEVER run `cd`. Use absolute paths, `git -C <path>`, or `python3 /abs/path.py`. One `cd` moves
  the tracked cwd for the whole session and has wedged every later Bash call in this repo before.
- Append `|| true` to exploratory `grep` and `find`. A search with no match exits 1 and is
  reported as a tool failure; 29 percent of this project's Bash failures were nothing else.
- `grep` in this shell is a FUNCTION wrapping ugrep with `--ignore-files`, so it SKIPS GITIGNORED
  PATHS. For any inventory, count, or absence claim, use `/usr/bin/grep -rn`, name `renders/` and
  `data/` explicitly, and exclude `./third_party/` and `./.claude/worktrees/`.
- Read `/Users/josie/can-it-ford/CLAUDE.md` BY THAT ABSOLUTE PATH. If you are in a worktree, your
  local copy is frozen at your branch point and is missing whole sections.
- `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` is the sole authority for any claim it
  covers. Read it before asserting a parameter, threshold, citation, or milestone.
- Stage explicit paths. NEVER `git add -A`, `git add .`, or `git commit -a`. Commit path-limited:
  `git commit -m "msg" -- path1 path2`. Another session's staged entries ride along on a bare
  commit; this has happened here.
- `.git/hooks/pre-commit` refuses more than 8 staged files. `.git/hooks/pre-push` requires
  `PUSH_OK=1`. Both are shared by every worktree.
- THE REPO IS PUBLIC (github.com/jcerrell-IS/can-it-ford). Every push is world-readable and
  permanent; GitHub has served removed blobs by SHA in this account. Any push, force-push, file
  delete, or overwrite of an existing file requires explicit confirmation first.
- This Mac has NO numpy in any SYSTEM interpreter. `uv` is at `/Users/josie/.local/bin/uv` and
  provisions numpy plus matplotlib in about 15 seconds. Use it rather than concluding you are
  blocked.
- Tag every factual claim: read directly, recalled from context, or inferred. Tag every solver
  claim by engine. Authority is CLAUDE.md August 4 audit item 1; read it live rather than
  restating it from here.
- A secondary source is not a primary one. Much of this project's corpus is AI-generated research
  reports. "Report X says paper Y reports N" is not "paper Y reports N".
- Verify a DOI TITLE against the resolved record, never just that the link resolves. A real DOI
  with an invented title is the dominant fabrication pattern.

## IF YOU ARE GIVEN A VISTA GPU NODE, THIS IS THE ONLY srun FORM THAT WORKS

Measured live 2026-08-19. Vista's wrapper rejects a partial invocation and reveals the
missing flag ONE AT A TIME, so a wrong form costs three round trips to diagnose:

    srun -p gh -N 1 -n 1 -t 00:30:00 --overlap --jobid=<JOBID> <command>

All five are required: `-p` partition, `-N` nodes, `-n` tasks, `-t` a time limit, and
`--overlap`. Without `--overlap` a step into a live idev kills it.

CHECK THAT THE GPU IS ACTUALLY DOING SOMETHING, do not assume it is:

    srun -p gh -N 1 -n 1 -t 00:05:00 --overlap --jobid=<JOBID> \
      nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader

A GH200 reporting `0 %, 3 MiB, 97871 MiB` means your allocation is being wasted. That is
the measured state a node sat in for 21 minutes of a 2-hour window on 2026-08-19 because
the srun line was wrong. The card has 98 GB; do not default to canonical grid sizes out
of habit and leave most of it idle.

## THE RESEARCH INDEX IS INCOMPLETE AND ITS SEARCH IS WEAKER THAN IT LOOKS

`analysis/research_index.py --query` is a literal substring match over `title` and
`abstract` ONLY. It cannot match an author, a method tag, or any paraphrase, and 110 of
332 records have no abstract. **A zero from `--query` is not evidence of absence.**

The index also does NOT contain the project's nineteen Undermind deep searches. Query
those directly in workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c` with
`inspect_deep_searches` before concluding the project has not researched something.
Load the `research-corpus` skill; it now carries both facts.

## OPERATING PROTOCOL

```
OPERATING PROTOCOL:

Before starting: check git log, .remember/ files, and the research
citations you were given, in that order. Do not duplicate work already
done elsewhere in this bundle.

When you hit an obstacle: try a fix. If it doesn't work, try a second,
genuinely different approach, not a variation of the same one. Before
concluding you're stuck, check whether an available connector or subagent
resolves it:
  - DeepWiki, for any question about how a library/repo actually behaves.
    Treat its answer as a hypothesis to verify against source, not fact.
  - The physics-skeptic subagent, before finalizing any claim involving a
    percentage, force, verdict count, or distance. If it's unavailable this
    session, say so explicitly and mark the claim unreviewed, do not fake
    the review.
  - Wolfram, for any physical parameter, unit conversion, or equation
    before it becomes a stated claim.
  - Scite, for any citation, DOI, or threshold before it's written as
    settled.
  - register_integrity.py (or the project's equivalent), before any commit.

Prefer proceeding on a clearly-labeled, reversible assumption over
stopping. State the assumption explicitly, in the commit message or the
write-up, so it can be revisited later without re-deriving it from
scratch.

Tag every factual claim by its source: read directly, recalled from
context, or inferred. Tag every solver/engine claim by which engine it
applies to. Never state a number from memory when you could check it live.

Keep working on everything else in your scope even if one specific thing
below is blocked, do not let one blocker stop the whole session.

Flag, rather than silently proceed past, only these four things:
1. You are about to discard, overwrite, or force-push over uncommitted
   work you did not create and cannot verify is safe to lose.
2. You've found two independently-reported results that genuinely
   disagree about the same physical quantity, not just different framing
   of the same thing, and resolving which is correct requires a judgment
   call, not just more data you can go get yourself.
3. You are about to edit a canonical file outside your declared scope.
4. A genuine hard-stop case: real financial cost, an exposed credential,
   a destructive/irreversible action, or anything matching the project's
   existing standing hard rules.

When you flag one of these: write it clearly to a named file (not just an
inline comment), keep working on everything else in your scope that isn't
blocked by it, and do not treat the flag as ending the session.

Write with an engineer/scientist's discipline throughout: state
assumptions before acting on them, prefer a falsifiable test over a
plausible-sounding claim (a no-forcing control, a held-fixed comparison,
a second seed), and write up a result the same way whether it confirms or
overturns something already published.

Before any push: confirm the target branch, stage explicit paths only,
never a blanket add, and confirm the push actually landed afterward,
don't just assume the command succeeding means the remote updated.
```

## WHEN YOU FINISH A UNIT

Append your board row, then say plainly what you did, with SHAs, what you could not verify, and
what you would do next. Then stop and wait. Do not invent a next task for yourself. A coordinator
reads your output in full and sends you a follow-up written for you specifically.

---
## YOUR SLOT: d17-moving, branch `claude/r9-moving-vehicle`, worktree `.claude/worktrees/r9-moving-vehicle`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d17-moving` first.

## YOU HAVE A LIVE GPU NODE AND A CLOCK

Vista idev job **920452 on c642-071**, started 23:51, **two hours**. 609 SUs remain on BCS20003. Reach it with:

```
ssh -o BatchMode=yes vista "srun --overlap --jobid=920452 --pty <cmd>"
```

`--overlap` is mandatory. Without it a step into a live idev dies. Submit work EARLY and analyse while it runs. Josie has authorised installing whatever is needed.

## THE RESEARCH QUESTION YOU ARE ACTUALLY ANSWERING

Every one of this project's 17 canonical runs is a **stationary** vehicle in moving water. That is correct for the AR&R and Shand thresholds, which describe a stationary vehicle, and it is why the project's own notes say the word "ford" in the title is what mismatches, not the setup.

**Nobody in the literature outputs a graded safe crossing speed as a function of both depth and flow velocity.** The field is entirely binary thresholds and incipient-motion curves. Pregnolato et al. 2017 (`10.1016/j.trd.2017.06.020`, open access) is the closest and it is depth-only, `v(w) = 0.0009w^2 - 0.5529w + 86.9448`, and it declares 30 cm impassable so it collapses to binary exactly where stability matters. Al-Qadami et al. 2022 full-scale (`10.1007/s11069-021-04949-6`) found drag "increased significantly with the increment of flow velocity, Froude number, and vehicle speed", which is the clearest published evidence that vehicle speed raises destabilising load, but their output is forces and a critical depth near 0.38 to 0.40 m, NOT a speed function.

So: **v_car and v_water are separate physical variables and the literature conflates or omits the second. Distinguishing them is itself the contribution.** Report v_car in the ground frame, v_water in the ground frame, and v_relative, and never let a reader collapse them.

## WHAT ALREADY EXISTS, VERIFIED LIVE BY THE COORDINATOR TONIGHT. DO NOT REBUILD ANY OF IT.

**1. The moving-body API is already in warpmpm. NO SOLVER CHANGE IS NEEDED.** Confirmed against the LIVE install on Vista at `/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/core/solver.py`, warp 1.15.0:

```
:93   periodic_x
:324  add_sdf_collider(sdf, center, quat=(0,0,0,1), ...)
:339  set_sdf_pose(handle, center=, quat=, velocity=, omega=)
:348  reset_sdf_force(handle)
:354  sdf_wrench(handle, dt)
:379  the periodic_x guard, which exists on add_cdf_collider only
```

Driver loop per tick: `reset_sdf_force` then `step` then `sdf_wrench(handle, dt=n_substeps*dt_sub)` then integrate then `set_sdf_pose`.

**2. The flooded roadway channel already exists.** `simulation/openchannel_bc.py` on your base branch, 714 lines, implements Zhao, Bolognin, Liang, Rohe and Vardon 2019 (`10.1016/j.compfluid.2018.10.007`), the correct citation for MPM in/outflow, NOT Kumar. It gives you `RecyclingChannelBC` (velocity-controlled inflow, pressure-controlled outflow), `tilted_gravity(grade_deg)` for a graded roadway, `OverfallBC`, and self-tests. USE IT.

## FIVE SILENT TRAPS, EVERY ONE MEASURED ON THIS PROJECT

1. `sdf_wrench` divides accumulated impulse by whatever dt it is handed. Passing `dt_sub` instead of the **tick** duration inflates force by exactly n, plausibly and without error.
2. The engine never zeroes `param.force` on the SDF path, so a naive read is the run-to-date total, not the tick's. Call reset every tick.
3. Quaternion order differs WITHIN the same file: `solver.py:324` defaults xyzw `(0,0,0,1)`, while `add_cup` at `:256` documents wxyz `(1,0,0,0)`.
4. **COM offset is a hard blocker.** `RigidBody6DOF` raises `NotImplementedError` on non-zero COM offset, because the SDF collider rotates about its centre and `sdf_wrench` reports torque about that same centre. The Yaris cloud CG sits 0.6312 m above the floor against bbox mid-height 0.7427 m.
5. **Never combine `periodic_x` with an SDF vehicle.** `add_cdf_collider` guards it at `:379`; `add_sdf_collider` has NO equivalent guard.

**Because of trap 4, PRESCRIBE the vehicle motion and MEASURE the wrench. Do not attempt free 6DOF tonight.** Commanding v_car and reading the hydrodynamic load is the scientifically correct first experiment: it is exactly Al-Qadami's measurement extended into a surface, it is a held-fixed comparison, and it sidesteps the blocker entirely rather than pretending it is solved. Evaluate stability afterwards by comparing the measured wrench against the project's existing criteria. Say plainly in the write-up that the body is prescribed, so nobody reads it as a free-body result.

## ALSO TRUE AND EASY TO GET WRONG

- **The grid is forced cubic.** `GridConfig(n_grid, grid_lim)` takes one scalar, so a long shallow channel costs cubically and anisotropic grading cannot be expressed. Keep the domain as short as the physics allows.
- **Domain rule that reproduces canonical exactly**, from `renders/yaris_render_s3_enhanced/hull_sweep.sbatch:38-42`: `lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth)`, giving the Yaris 9.421742314.
- **Axis trap:** `sim_standing.py:82` uses `ext[1]` AFTER `load_vehicle(up='z')` permutes axes. Taking the PLY axes at face value gives 14.989 m instead of 9.4217 m, a 59 percent error.
- **`ReservePool` in openchannel_bc.py has a known row-collision defect** that silently corrupts CG and inertia and presents as physics. It is one of nine items awaiting Josie's decision. Use `RecyclingChannelBC`, not `ReservePool`, unless you verify the defect is fixed. If you must use it, verify first and say so.
- **Engine limitation, state it, do not overstate it:** `mpm_utils.py:1100` sets rigid particle stress to a zero mat33 and material 8 is excluded from the SVD, so the hull exerts no pressure on the water. But `_apply_rigid_restitution` IS live at restitution 0.05, so "no force is ever formed" is FALSE. The real limitation is that the net force cannot be decomposed.

## YOUR UNIT

1. Build `simulation/moving_vehicle_channel.py`: the Yaris hull as a moving SDF collider at a prescribed v_car, inside a `RecyclingChannelBC` flooded roadway, with the wrench measured per tick and all five traps handled explicitly in code with a comment naming each.
2. **Write a falsifiable self-test BEFORE any GPU run.** At minimum: v_car = 0 and v_water = 0 must give zero net streamwise wrench to within noise, and the wrench at v_car = 0 must reproduce the canonical stationary case's order of magnitude. A driver that cannot pass a no-forcing control is not measuring anything.
3. Run the matrix. Suggested and adjust to fit the clock: **v_car in {0, 2.2, 4.5, 6.7, 8.9} m/s** (0, 5, 10, 15, 20 mph) crossed with **v_water in {0.5, 1.0, 2.0, 3.0} m/s** at fixed depth 0.30 m, which is the project's canonical depth and near Al-Qadami's 0.38 m critical depth. That is 20 cells. Add repeats where the clock allows, because this project's runs are NON-DETERMINISTIC and a single draw is not a result.
4. Emit a tidy per-run record and build the (v_car, v_water) load surface in `analysis/r9_speed_surface.py`. Report distributions, not single points, wherever you have repeats.

## DISCIPLINE

Pre-register the matrix and the pass criteria in a commit BEFORE the first run, as slot d3-force did last night. That commit is what makes the result trustworthy. Log to Weights and Biases if it costs you nothing; the project already has 105 runs there and every run is already linked to its GitHub commit.

Nothing is pushed. Stage explicit paths. Append your board row. If the node dies, say what completed and what did not rather than reporting the matrix as done.
