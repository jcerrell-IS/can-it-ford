# ROUND 3, D6 POSTER-GRADE-VISUALS

Read `ROUND3_SHARED.md` first. Both of the things you flagged are now
actionable, and one of them is exactly the artifact you needed.

## 1. The PLY artifact you needed exists and is readable right now

You recorded that your render script never reads a `.ply` and called fixing that
your highest-leverage change. D7 then found an unindexed artifact that is
directly on it and nobody had opened:

    82c51733  "Code-Level Analysis: PLY Loading in kks32/mpm-engine
              (splats module & load_vehicle)"

I opened it at 22:39 to confirm it is the right document. Its TL;DR:
`load_vehicle()` in `src/warpmpm/vehicle.py` delegates PLY parsing to
`load_gaussians_ply()` in `src/warpmpm/splats/io.py`, which reads the standard
3D Gaussian Splatting layout from Kerbl, Kopanas, Leimkühler & Drettakis.

Readable path, outside the TCC-blocked `~/Downloads`:

    /Users/josie/Claude/reu/compass_artifact_wf-82c51733-4a8b-559a-b300-fe37294b3009_text_markdown.md

Mirrors exist under `~/Documents/Claude/reu/` and in the corpus at
`01_Solver_Physics_and_Coupling/`.

Read it, then make the render path load the real hull. Treat the artifact as a
hypothesis and verify each claim against the vendored source at
`third_party/mpm-engine-544c93dd-solver-core/` before you rely on it. The
canonical mesh is
`vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`.

## 2. D5's matched-dx set has landed. Re-render.

You wrote: "If D5's matched-dx set lands, re-rendering is one command." It
landed. D5's branch `claude/fork-three-class` carries `59d3283` and the arms
before it, with the matched arm at dx 0.0849.

Your current three-up is shared-n_grid with realized depths of 0.294 / 0.326 /
0.306 m, and you correctly noted that a moving three-up invites direct
comparison in a way a still does not, no matter what the caption says. Re-render
at matched dx so the eye is not being asked to discount a depth difference.

Two things to carry into the new caption, both from D5 and both retracted or
corrected since your last render:

- The headline "removing the resolution confound flips the large_4wd verdict"
  was **retracted as false**. Register J15 already published that flip from
  plain shared-n_grid refinement. Correct form: refining dx below roughly 0.10 m
  flips it; matching dx makes the three comparable, it did not produce the flip.
  Do not put the causal version on a frame.
- The safety-factor figure is **about 3.5, not 40**. "40x the noise floor" set a
  between-configuration change against a within-configuration draw; the right
  column was `headroom_x 1.0447`.

## 3. Your friction caveat is right and now has a primary source

You put the caveat on every frame and observed that all three panels read
NO-FORD, the conservative direction, and that it is the Silverado's flip into
STUCK that sits on the optimistic side of a friction value near double the
field's convention. That reading is confirmed by five other sessions
independently (shared section 3).

You can now name the source on the frame instead of gesturing at it: mu = 0.55
is Azhar, Pauwels & Bui (2023)'s own spring-balance measurement of their
experimental rubber mat; the convention the guidelines assume is 0.3, from
Bonham & Hattersley 1967 carried forward. Keep D2's guard: analogous in
direction and magnitude, not the same quantity.

Send D4 a one-paragraph confirm-or-correct on your own line of the consolidated
entry only. Do not restate the whole finding.

## Constraints unchanged

E8 stays enforced the way you enforced it: verify with `git check-ignore -v` on
the artifact itself, not by assertion. Videos, sidecars, manifests and frames
stay untracked; only the withholding `.gitignore` is tracked. Keep the time axis
explicit the way you did (90 frames at 30 fps = 3.000 s simulated, 1.00x real
time, in the filename and the sidecar and `realtime_factor`).

## Skills and state

Call `mpm-render-pipeline`. ffmpeg is local-only and absent on gh-dev, which is
already your working path. No GPU needed: the frame data is in the rollouts.
Five commits held unpushed pending Josie's per-branch check; worktree clean.
