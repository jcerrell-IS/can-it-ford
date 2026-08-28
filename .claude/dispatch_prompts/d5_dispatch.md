### DISPATCH 5, LS6 GPU, new branch, the three-class demonstration at matched conditions

```
SCOPE DECLARATION
MACHINE: LS6, submitted as BATCH not idev. Per memory
vista-su-burn-is-idev-not-science.md, interactive burns 98.5-99.1% of Vista
node-hours and 95 of 184 jobs ended in TIMEOUT, while LS6 shows 0 batch
timeouts. Vista's allocation also expires 2026-09-30.
BRANCH: new, claude/three-class-matched-<slug>, off main.
MAY WRITE TO: that branch, and a NEW output directory under $SCRATCH.
NEVER TOUCH: main; data/all_runs_inventory.csv;
renders/yaris_render_s1/gates_results_all_runs.json (both are Yaris-only and
stay that way, this is a COMPANION experiment, not an extension of the gated
set, and folding vehicle classes into the canonical store is a human decision);
any existing run directory under renders/ or data/ (register item 16 exists
because job 866887 overwrote run directories and made six margins permanently
unverifiable); claude/rtfd-test-phase-1-4-569130; the render branch (Dispatch 6
owns rendering).

WHAT THIS THREAD IS FOR
Produce the first physically comparable three-class result: compact_sedan,
midsize_suv and large_4wd, on their real converged hulls, with the cross-vehicle
confounds actually controlled. Today no such run set exists, and that absence is
the only thing blocking both the strongest available novelty claim and the best
available figures.

THE THREE HULLS, USE EXACTLY THESE, ANCHORED BY sha256 NOT BY PATH
  compact_sedan  2010 Toyota Yaris, NCAC
                 yaris_coarse_v1l_watertight.ply
                 3.542739 m3, rho 310.494, mass 1100 kg (deck header line 28)
  midsize_suv    2020 Nissan Rogue, CCSA
                 rogue_g96_pd8_coarse_watertight.ply
                 sha256 c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2
                 4.9503 m3, rho 317.4
                 mass 1571.3 kg is WEB-SOURCED ONLY, the deck states no mass;
                 the AR&R reference figure is 1609 kg. Say which you used.
  large_4wd      2007 Chevrolet Silverado, CCSA
                 silverado_g96_pd8_coarse_watertight.ply
                 sha256 46fba11e77cd92dda7464232bad2b03f14a2afbc91f87490bcf2f1f7d466d7f9
                 7.9621 m3, rho 285.1
                 mass 2270 kg (deck header line 28) is the STRONGEST provenance.
                 The prior multigeom run used 2337 kg, whose own summary.json
                 records mass_source = "AR&R large_4wd class figure
                 (gates_both_scenarios.py:23)". Both are defensible; they are not
                 interchangeable, and docs/SILVERADO_MASS_PROVENANCE_2026-08-13.md
                 shows docs/MULTIGEOM_VALIDATION_2026-08-11.md labels the
                 WEAKEST-provenance figure "primary" and demotes the strongest to
                 mass_alt_kg, inverting the hierarchy. Do not inherit that.

SIX TRAPS, ALL ALREADY MEASURED, DO NOT REDISCOVER THEM
1. Do NOT use anything in vehicle_meshes/candidates/. Those two files are sha256
   duplicates of pool files AND are the two worst hulls by volume convergence,
   47.5% and 31.1% below converged, giving densities 605 and 415.6 kg/m3.
   candidates/SUMMARY.md printed those and still called them plausible.
2. euler_number cannot be a gate here: the canonical Yaris is at -442. Selecting
   on euler closest to 2 selects for coarseness, which erodes volume, which feeds
   buoyancy directly. Rank hulls by distance from converged volume.
3. THE CENTRAL CONTROL, AND THE WHOLE POINT OF THIS DISPATCH. Fixed n_grid is
   NOT fixed resolution across vehicles: grid_lim follows the hull extent, so at
   n_grid 96 dx is Yaris 0.0981, Rogue 0.1088, Silverado 0.1361, and the realized
   water depth differs too. Run the matrix so that dx AND realized depth are held
   fixed across the three vehicles, by choosing per-vehicle n_grid rather than a
   shared one, and REPORT the achieved dx and realized depth per run. If you also
   keep a shared-n_grid arm for continuity with the prior sweep, label the two
   arms distinctly and never average them.
4. The mesh pipeline is not bit-reproducible: same effective arguments give a
   different sha256 and at g96 different topology (72520 vs 72524 faces). Cite the
   artifact sha256, never the command, and do not regenerate a hull to "verify" it.
5. If any decimation is needed, use Open3D 0.19.0. trimesh's
   simplify_quadric_decimation breaks watertightness on this geometry at EVERY
   level 320k to 10k (49 to 172 non-manifold edges); Open3D preserves
   watertightness and genus.
6. Register E2: FloodScene vehicle.py:162 samples the mesh to 60,000 surface
   points before solidifying, so watertightness does NOT propagate into the sim.
   Do not claim a watertight-hull result without saying this.

DO NOT WIRE INERTIA OR CG. CLAUDE.md item 4 is explicit and this is the exact
place someone would be tempted. The solver already computes a better tensor from
the real hull particle cloud (kernels/mpm_solver_warp.py:859-871). The box tensor
overstates every principal moment by +16.3 to +26.1% because the hull fills only
33.2% of its bounding box, and the documented (L,W,H)->(x,y,z) convention is
TRANSPOSED relative to the gated scene, which puts the long axis on Y. A naive
write gives Ixx -69.2% and Iyy +379.2%. Report instead the free result: measured
cloud CG 0.6312 m above the floor, below bbox mid-height, so the no-topple result
is CONSERVATIVE.

RESEARCH FINDINGS YOU NEED, THESE ARE WHAT MAKE IT A CONTRIBUTION
- CLAUDE.md A-3: Smith, Modra and Felder 2019; Martinez-Gomariz et al. 2017; and
  Arrighi et al. 2015 jointly establish that buoyancy, drag and lift lever arms,
  and sliding/float/roll thresholds depend on DISPLACED VOLUME, UNDERBODY SHAPE,
  WHEELBASE, TRACK AND CoM, not mass alone. Note the corpus caveat: Smith/Modra/
  Felder and Arrighi 2015 already appear in the register at adjacent contexts, so
  they are NOT independent support; Martinez-Gomariz 2017 and Allen 2003 are new.
- This run set is the direct test of that claim: the three hulls differ in
  displaced volume by 2.25x (3.54 / 4.95 / 7.96 m3) while their densities span
  only 285 to 317 kg/m3. That is precisely the regime where a mass-only account
  and a geometry-aware account diverge.
- Allen et al. 2003, SAE 2003-01-0966, is the citable provisional CoM/inertia
  regression by class. The paper flags itself provisional; cite it as method, not
  validation.
- CLAUDE.md L-1: the AR&R and Shand thresholds describe a STATIONARY vehicle in
  flow, which is what this setup is. Do not write it up as a scenario mismatch.
- CLAUDE.md L-4: coarse resolution usually OVER-predicts peak hydrodynamic force,
  so over-threshold NO-FORD verdicts are conservative.
- CLAUDE.md L-3: the g64 baseline has 4 particle layers and depth/dx exactly
  2.000, against a rule of thumb of ~10 per flow depth. A limitation, never a
  converged resolution.
- Steffen, Kirby and Berzins 2008 is the citable mechanism for MPM losing
  convergence under refinement at fixed particles-per-cell; PPC is constant at 8
  in this stack, exactly that paper's case.
- Memory l1-l2-divergence-is-class-dependent: the paper's class-free divergence
  zone is already contradicted for 2 of 3 AR&R classes at 0.30 m / 1.5 m/s. Your
  three classes are the natural test of that, and it is currently an open claim.
- Register item 17: no single g64 arm of this ladder is quotable, it is
  non-deterministic at fixed configuration. Run g96 and above, or repeat seeds.
  And do not trust determinism_identical: it reported True on six runs that
  DIFFER. Compare metrics.csv directly.

CONCRETE FIRST STEP
Before submitting anything: sha256 all three hulls at the paths you will actually
read, and confirm they match the digests above. Then compute, for each vehicle,
the n_grid that yields a COMMON dx, and print a table of vehicle, n_grid, dx,
realized depth, depth/dx and particle count. Get that table right before spending
a single GPU-hour; it is the entire experiment.

DEFINITION OF DONE
All three classes run at matched dx and matched realized depth, classified with
the same simulation/failure_modes.classify_timeseries that produced the 17, with
margin_frames and k_crit reported beside every verdict. A CSV and a findings doc
on your branch, each run stamped with hull sha256, job id, node, driver sha256,
achieved dx and realized depth. Use lineterminator="\n" in any DictWriter
(.gitattributes:4 is eol=lf). State plainly whether the class ordering follows
mass or follows displaced volume, in either direction, and write it up the same
way whichever it is. Mark the whole set NON-CANONICAL in its own header. Branch
pushed with PUSH_OK=1 and confirmed with ls-remote, not with the exit code.
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
