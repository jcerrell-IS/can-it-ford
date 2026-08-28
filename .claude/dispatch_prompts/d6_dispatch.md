### DISPATCH 6, Mac, off `claude/render-realism-vehicle-water-ad1490`, poster-grade three-class visuals

```
SCOPE DECLARATION
MACHINE: Mac, no GPU needed for the render layer.
BRANCH: new, claude/three-class-render-<slug>, branched off
claude/render-realism-vehicle-water-ad1490 at e22737d (already pushed).
MAY WRITE TO: that new branch only: analysis/ render code, a new figures
directory, and one findings doc.
NEVER TOUCH: main; the solver, any gate, any verdict, any coupling code; the
canonical stores; Dispatch 5's branch (do not wait for it either, see below);
claude/rtfd-test-phase-1-4-569130.

HARD SCOPE RULE, INHERITED AND NON-NEGOTIABLE
Render layer only. Every function here reads already-computed particle positions
and rigid-body com/R state and turns them into colors and mesh vertices. No
verdict, no force, no coupling code, no gate result changes. warpmpm particle
output only, not Genesis, not a re-simulation.

WHERE THIS THREAD LEFT OFF
e22737d landed 1,949 insertions across 6 files and is ON ORIGIN:
  analysis/vehicle_mesh_transform.py   real .ply loading + placement from com/R
  analysis/flood_water_optics.py       SSC-driven Beer-Lambert, 9 citations
  analysis/make_hdri_cache.py          HDRI caching
  analysis/render_multigeom_shaded.py  extended multi-vehicle shaded render
  docs/RENDER_REALISM_2026-08-13.md    530 lines of working
  docs/PYSPLASHSURF_WHEELS_2026-08-13.md
Two later commits corrected the splashsurf attribution against primary source and
retracted an overstated 1.22x. Preserve those corrections.

THE ONE FIX THAT MATTERS MOST, IN THAT WORK'S OWN WORDS
"The rogue-hull render currently marching-cubes an isosurface from 9135 rigid
particles, because the render script never reads a .ply. That's why the car reads
as an unrecognizable blocky shape ... This is the single highest-leverage fix and
does not touch physics."
The registration is ALREADY SOLVED, verified 2026-08-13 against
g64_yaris_regression: yaw 90 degrees, because the body long axis lies on BODY Y
while the .ply long axis lies on MESH X, and t[0] sits 0.5948 m BELOW. Reuse it;
do not re-derive it and do not "fix" the 90 degrees.

USE THE CONVERGED HULLS, NOT THE CANDIDATES
  yaris_coarse_v1l_watertight.ply
  rogue_g96_pd8_coarse_watertight.ply      c0b778e2...06c310b2
  silverado_g96_pd8_coarse_watertight.ply  46fba11e...f7d466d7f9
The two files in vehicle_meshes/candidates/ are the two WORST hulls by volume
convergence, 47.5% and 31.1% below converged. A render built on those shows a
visibly wrong vehicle and implies a wrong displaced volume. Also: the pipeline is
not bit-reproducible, so anchor on sha256 and never regenerate to verify.
~/can-it-ford-meshes-qualified/ carries obj and stl exports of all three plus
MANIFEST.md if you need a non-.ply format.

THE OPTICS GAP YOU ARE CLOSING, AND ITS CITATIONS
flood_water_optics.py is honest about three things it did not derive, and closing
them is what moves this from plausible to citable:
  (a) the attenuation-coefficient-per-mg/L slope is TUNED for visual plausibility,
      not read off a published regression
  (b) the clear-water and sediment RGB values are a qualitative color consistent
      with cited spectral peaks, not a colorimetric conversion
  (c) floor_boost encodes the DIRECTION of the Brisbane finding but not its
      magnitude
The coefficients exist in sources that were abstract-only that session. Pull the
full text via Scite or the library connectors:
  Stewart, Fox, Harnett 2013, DOI 10.1061/9780784412947.167
  Stewart, Fox, Harnett 2014, J. Hydraulic Eng, DOI 10.1061/(ASCE)HY.1943-7900.0000887
  Davies-Colley and Smith 2001, JAWRA, DOI 10.1111/j.1752-1688.2001.tb03624.x
  Martinez et al. 2015, JGR Earth Surface, DOI 10.1002/2014JF003404
    (SPM 5-620 g/m3, reflectance saturation near 100 g/m3, 1 g/m3 = 1 mg/L)
  McKee and Gilbreath 2015, Environ Monit Assess, DOI 10.1007/s10661-015-4710-4
    (real urban storm-flow SSC 1.4-2700 mg/L)
  Brown, Chanson, McIntosh, Madhani, Brisbane River flood plain, Jan 2011
    (SSC increases as depth decreases, an actual flooded-road event)
  Alexandrov, Laronne, Reid 2003, DOI 10.1006/JARE.2002.1020 (six-year mean
    34,000 mg/L, use as physical upper bound only)
  Schneider et al. 2015 and Yang 2012 for the iron-oxide brown/tan mechanism
    (hematite peak 565 nm, goethite 505/435 nm)
If a coefficient still cannot be retrieved, say so and leave the value labelled
tuned. Do NOT quietly upgrade a tuned number to a cited one; that is the exact
failure this project keeps catching.

WHAT TO PRODUCE, RANKED
1. Three-class hero still: Yaris, Rogue and Silverado in the same flood
   condition, real hulls, correct placement, SSC-driven water. This is the image
   the whole project has been unable to make.
2. The two results that exist only as numbers today:
   - margin_frames collapsing 11 -> 10 -> 4 across g48/g64/g96 for m2337, with
     k_crit plotted beside it so the closeness is not mis-scaled
   - Silverado ratio_slide 6.9669 -> 1.8105 -> 1.5557 crossing the joint
     drift-and-speed condition into STUCK at g128
3. An honest caption block for each figure stating engine (warpmpm), hull sha256,
   what is measured versus tuned, and NON-CANONICAL status for anything
   multi-vehicle.

INDEPENDENCE NOTE
You do NOT depend on Dispatch 5. Render against run data that already exists:
data/rogue_silverado_slide_classification_2026-08-13.csv and the multigeom
rollouts referenced in docs/MULTIGEOM_VALIDATION_2026-08-11.md. If Dispatch 5's
matched-dx set lands later, re-render is cheap. Do not block on it.

CONCRETE FIRST STEP
Render ONE frame of the Rogue with the real hull loaded through
vehicle_mesh_transform.py and put it beside the current particle-isosurface
version. That before-and-after is the proof the highest-leverage fix works, and
it takes minutes.

DEFINITION OF DONE
A figures directory on your branch containing the three-class hero still and the
two quantitative figures, each with its honest caption; a findings doc recording
which optics coefficients were successfully retrieved from full text and which
remain tuned; and an explicit statement of whether the stills are poster-grade or
still diagnostic-only, which nobody has yet assessed. Branch pushed with
PUSH_OK=1 and confirmed with ls-remote.
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
