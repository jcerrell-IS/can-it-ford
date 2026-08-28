### DISPATCH 10, Mac then LS6, the scene, and the constraint that decides its size

```
SCOPE DECLARATION
MACHINE: Mac for design, LS6 BATCH for any run.
BRANCH: new, claude/fork-scene-<slug>, off main.
MAY WRITE TO: that branch only.
NEVER TOUCH: main; canonical stores; Dispatch 9's driver branch; Dispatch 8's branches.

THE HARD ARCHITECTURAL CONSTRAINT, AND IT IS THE WHOLE DESIGN
warpmpm's GridConfig(n_grid, grid_lim) takes a SINGLE SCALAR, so the domain is
necessarily CUBIC. You cannot build a long shallow channel without paying cubically.
This is the strongest single argument against attempting an arXiv-2607.00673-scale
scene in this engine at this stage, and it must be stated in the writeup rather than
discovered at run time.

THE ARITHMETIC, so nobody proposes the impossible. Canonical realized depth is
0.2944294473 m. The validated near-floor regime is about 18 cells across that depth,
so dz = 0.01636 m.
  a 30 x 12 x 3 m road-scale scene at ISOTROPIC dz  -> 246.8 MILLION cells
  the canonical Yaris tank at g96                   ->     884,736 cells
  ratio                                              ->        279x
Anisotropic grading (dxy 0.08, dz 0.01636) would give 10.3 M cells, a 23.9x reduction,
BUT the explicit timestep still follows the SMALLEST cell dimension, so it buys memory
and per-step work and NOT step count. AND warpmpm cannot express it anyway: the grid
is a single scalar. Anisotropy is therefore a reason to change engine or to patch the
grid, not a free win. State that explicitly.

THE LITERATURE VERDICT ON THIS, ALREADY SEARCHED. Do not re-run it.
78 papers, 76% coverage. NO MPM study follows a rigid vehicle with a refinement window
through a large flood domain. The closest fluid result is dynamic AMR for free-surface
waves and breaking WITHOUT a vehicle (Mao, Chen, Li, Feng 2016,
DOI 10.1061/(ASCE)EM.1943-7889.0000981). Adaptive MPM-FSI work is preliminary and not
road-scale. What exists and is closest:
  local grid refinement for B-spline MPM, with bridging-domain Lagrange multipliers
    that SUPPRESS spurious stress reflection at the fine/coarse interface, plus
    multi-time-stepping: Sun, Gan, Huang, Zhou 2020, DOI 10.1002/nme.6312
  multi-resolution MPM by penalty formulation, no local equations to solve:
    He, Jin, Zhou, Yin, Chen 2025, DOI 10.1002/nag.70048
  structured mesh refinement in GIMP: Ma, Lu, Komanduri 2006, DOI 10.3970/CMES.2006.012.213
  truncated hierarchical B-spline MPM (uses particle SPLITTING, which is UNSAFE for
    history variables unless deformation-gradient and state transfer are defined):
    Zhang, Shen, Zhou, Balzani 2021, DOI 10.1016/J.COMPGEO.2021.104097
  implicit octree adaptive MPM, up to 5.5x speedup: Bird, Coombs, Augarde, O'Hare 2026
  sparse/dynamic grids cut memory when the domain is EMPTY but do not reduce the
    smallest-cell timestep and do not resolve the floor layer: Qiu et al. 2022
    (10.1145/3570160), Shin et al. 2010 dynamic meshing
  hybrid 3D MPM with 2D shallow-water far field: Pan et al. 2023, DOI 10.1002/fld.5233;
    MPM/finite-volume depth-averaged: Zheng et al. 2023, DOI 10.1016/j.compgeo.2023.105673
  NO moving-reference-frame MPM result was identified. Open-boundary MPM exists:
    Zhao, Bolognin, Liang, Rohe, Vardon 2019, DOI 10.1016/J.COMPFLUID.2018.10.007
DECISIVE CONSTRAINT ON ALL OF THEM: Steffen, Wallstedt, Guilkey, Kirby, Berzins 2008,
DOI 10.3970/CMES.2008.031.107, shows fixed particles-per-cell can LOSE convergence
under grid refinement. Our stack holds PPC constant at 8. Any refinement scheme must
co-refine or explicitly control PPC; otherwise AMR silently changes quadrature and
transfer conditioning. Standard MPM, GIMP, CPDI and B-spline MPM are therefore NOT
interchangeable. Nonuniform grids already produce projection error (Wallstedt and
Guilkey 2007, DOI 10.3970/CMES.2007.019.223).

USE THE DOMAIN RULE THAT ALREADY EXISTS. From
renders/yaris_render_s3_enhanced/hull_sweep.sbatch:38-42 (rescued by Dispatch 8):
  lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth)
  yaris 9.421742314   rogue 10.442536068   silverado 13.067932987
This reproduces the canonical Yaris grid_lim 9.421742313727737 EXACTLY, so it is the
as-ran rule generalised, not a new invention.
THE AXIS TRAP, and it is a 59 percent error: sim_standing.py:82 reads 2.2*ext[1] where
ext is the extent AFTER load_vehicle(up='z') permutes axes, so ext[1] is the PLY's x.
Taking PLY axes at face value gives 14.989 m instead of 9.4217 m.

THE SCENE ITSELF, SCOPED HONESTLY
Do NOT attempt a reconstructed outdoor scene in this dispatch. The Undermind corpus
contains ZERO papers on Gaussian splatting, scene reconstruction or terrain
construction, so there is no evidence base here for it, and a prior reconstruction
attempt produced a metrically wrong mesh: a car at 0.333 x 0.174 x 0.715 m, volume
0.0173 m3, watertight, because the splat trainer normalises median camera-to-subject
distance to 1.0 and no scale-recovery step exists. The directory is misnamed
"failed_reconstructions"; the failure was metric, not geometric.
WHAT TO BUILD INSTEAD, in order:
1. A flat floor with a correct CROSS-SLOPE, which is the one terrain property with a
   plausible hydraulic effect at this scale, and an inflow/outflow pair per Zhao 2019.
2. A sensitivity test: does cross-slope change the traction margin at all? If it does
   not, that is a publishable negative and it retires terrain fidelity as a concern.
3. Only if 2 says terrain matters, escalate to reconstructed geometry, and solve
   metric scale at capture time with a known-length reference object in frame.

DEFINITION OF DONE
A scene module on your branch, the domain-sizing rule applied with the axis trap
handled and a unit test that catches it, an inflow/outflow implementation citing
Zhao 2019, and a written statement of the resolution-versus-extent trade with the
arithmetic above reproduced from your own run. Plus the cross-slope sensitivity
result, in whichever direction it comes out.
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
