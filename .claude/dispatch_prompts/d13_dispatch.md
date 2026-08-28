### DISPATCH 13, engine go/no-go: does Chrono build on GH200

```
SCOPE DECLARATION
MACHINE: LS6 or Vista, whichever has a GPU node free. This is a BUILD task, not a
  physics task, so an interactive node is acceptable here even though production runs
  should be batch.
BRANCH: new, claude/fork-chrono-eval-<slug>, off main.
MAY WRITE TO: that branch (docs/ and scripts/ only), and a NEW $SCRATCH build
  directory. Chrono itself is built OUT of tree; do not vendor it into the repo in
  this dispatch.
NEVER TOUCH: main; the canonical stores; third_party/mpm-engine-544c93dd*/ (both
  vendored trees are separately provenanced and their provenance tables are
  load-bearing, per their own VENDORED.md); any other fork branch.

WHY THIS DISPATCH EXISTS
An independent FOSS engine assessment concluded that Project Chrono is the ONLY stack
that already ships BOTH genuine accumulated-force two-way fluid coupling AND a
self-propelled multibody vehicle. That is exactly the combination this fork needs and
that warpmpm does not have. Chrono is therefore a serious alternative to Dispatch 9's
warpmpm plan, and this dispatch decides between them on evidence rather than
preference. Dispatch 9 proceeds in parallel and is NOT blocked on this.

WHAT CHRONO ACTUALLY PROVIDES, so you do not re-derive it
- Chrono::FSI-SPH accumulates per-marker fluid forces into a net per-body force and
  torque by atomic accumulation into a per-body array in the BCE manager
  (src/chrono_fsi/sph/physics/BceManager.cu), exposed as
  chrono::fsi::ChFsiInterface::GetFsiBodyForce(i) and GetFsiBodyTorque(i).
  CAVEAT CARRIED FROM THE SOURCE: the specific line number (~373) came from a
  user-posted compiler error, not a blob view; the file path and the atomicAdd pattern
  are verified but the line may drift. Do not cite a line number you have not opened.
- Two-way is explicit and named: ChFsiInterfaceSPH::ExchangeSolidForces() moves fluid
  forces to the multibody system, ExchangeSolidStates() moves body states back to the
  SPH data manager.
- Chrono::Vehicle supplies engine, drivetrain and tyre subsystems, so the vehicle
  drives under its own power while the FSI interface reads the fluid reaction. The
  published fording configuration was a 4WD wheeled vehicle under a constant-speed
  controller with approximately 1.5 million SPH markers, chassis and tyre meshes
  decomposed into convex hulls for collision.
- TERRAIN INGEST IS THE OTHER REASON THIS MATTERS. RigidTerrain::AddPatch accepts a
  Wavefront OBJ mesh used for both contact and visualisation, and SCMDeformableTerrain
  initialises from a height-map image or an OBJ mesh. So a photogrammetry or 3DGS
  reconstruction exported as a heightfield or OBJ CAN be ingested directly as terrain,
  which is the single hardest thing to do in warpmpm.
  CAVEAT: semi-empirical tyre models (Fiala, LuGre, Pacejka) query GetHeight and
  GetNormal, which may be incomplete for an arbitrary rigid mesh. Rigid tyres and FEA
  tyres go through the contact engine and are unaffected. Choose the tyre model with
  this in mind.

THE GATING QUESTION, AND IT IS THE ONLY DELIVERABLE THAT MATTERS
There is NO documented case of Chrono or Chrono::FSI being built or run on
ARM64/aarch64, Jetson or GH200. Officially supported targets are Linux, Windows and
macOS on x86-64 with CUDA or HIP. Nothing in principle precludes aarch64 plus CUDA,
since CUDA supports SBSA Grace plus Hopper sm_90, but it is undocumented and untested.
YOUR JOB IS TO ANSWER: does Chrono::FSI-SPH build and run a clean demo on GH200?

GO/NO-GO MILESTONE, stated in advance so it cannot be moved afterwards:
  a clean run of demo_FSI-SPH_DamBreak or demo_FSI-SPH_ObjectDrop on a GH200 node,
  producing output, with the build recipe recorded.
BUDGET: treat this as a moderate build-porting task. If it proves infeasible after a
bounded effort, STOP and say so plainly. The documented fallbacks are, in order: an
x86 plus H100 host, or continue on warpmpm per Dispatch 9. Both are acceptable
outcomes. A negative result here is a real deliverable, not a failure.

KNOWN AARCH64 LANDMINE, unrelated to Chrono but it will bite you first: on aarch64 the
default pip install torch installs a CPU-ONLY build. Use the CUDA wheel index or an
NVIDIA NGC aarch64 Apptainer container. This is the most common GH200 failure mode.

VALIDATION REALITY CHECK, WRITE THIS INTO THE REPORT
Chrono's fording capability is a PHYSICS DEMONSTRATION AND VISUALISATION, not a
benchmark validated against experimental fording data. The rigorously validated Chrono
off-road work is soil and terramechanics (CRM and SCM), validated against single-wheel
experiments, DEM ground truth, and drawbar-pull and slip-sinkage tests. This matches
the independent finding that NG-NRMM treats SPH fording as a known gap. Therefore:
adopting Chrono does NOT inherit a validated fording result, it inherits a validated
SOIL result and a demo-level fluid one. Any quantitative NG-NRMM fording
error-reduction percentage is UNVERIFIED and must not be cited.

THE OTHER THREE CANDIDATES, ALREADY ASSESSED, DO NOT RE-SEARCH THEM
- SPlisHSPlasH: genuine momentum-conserving Akinci-2012 force coupling
  (doi:10.1145/2185520.2185558), best-architected non-Chrono base, and DiffFR
  (doi:10.1145/3618318) proves actuated control is feasible on it. But NO drivetrain or
  tyre model (major new work) and the SPH solvers are CPU-ONLY, so no GH200
  acceleration. Fallback only.
- DualSPHysics: true force coupling via Chrono, but ships x86-only precompiled
  libraries and GPU binaries limited to sm35 through sm80, while GH200 Hopper is
  sm_90. Hard blocker. Not recommended.
- Genesis: the most ARM64-plus-CUDA-ready backend of the five (Quadrants, forked from
  Taichi, targets ARM64 plus CUDA), but its LegacyCoupler is an impulse and
  velocity-projection scheme, not accumulated-force integration, and it FAILED this
  project's Yaris buoyancy test. Using it would mean replacing the coupler, a major
  rewrite. The benchmark that would reopen it: a corrected coupler reproducing static
  buoyancy on the Yaris hull to within a few percent of Archimedes.

CONCRETE FIRST STEP
Do not start with Chrono. Start with the cheapest possible discriminator: on a GH200
node, confirm that a CUDA sm_90 toolchain and a working PyTorch CUDA build are
present, then attempt the Chrono core build (no FSI) before attempting Chrono::FSI.
If the core will not configure on aarch64, you have your answer in an hour rather
than a week.

DEFINITION OF DONE
A written go/no-go with the build recipe if it worked, or the exact failure and where
it stopped if it did not. Either answer closes the question. If GO, add a scoped
comparison of what a Chrono arm would give that Dispatch 9's warpmpm arm cannot,
specifically the actuated drivetrain and the OBJ/heightfield terrain ingest. If NO-GO,
say so plainly and hand the fork back to Dispatch 9 unchanged.
```

OPERATING PROTOCOL, applies to you in full:

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
