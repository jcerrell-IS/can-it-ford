# Phase 7 Findings and Actions, July 13, 2026

Record for the next session so none of this has to be re-derived. Everything below was
verified live (grep, cat, md5, direct .ply measurement on Vista), not from memory.

## Doc-content corrections applied (Mac repo, tracked, staged for Phase 8)

- SESSION_STATE.md: grid_density (64 vs 128) is ruled out as the crash cause, not a
  pending fix. The live suspect is the domain-widening bounds
  (lower_bound=(-2.5,-1.0,-0.1), upper_bound=(4.5,1.0,2.5)), not yet tested with the
  corrected mass rho=115.7.
- kumar_july9_update/STATUS.md: DRIFT_THRESHOLD reframed at lines 171, 180, and 191 as a
  numerical onset-of-motion detection tolerance (approximately 2.5 to 3.4 percent of
  vehicle body width), not a physically-cited threshold. Incipient-motion physics: Xia
  et al. 2014 (DOI 10.1007/s11069-013-0889-2), Shah et al. 2018
  (DOI 10.1051/matecconf/201820307003).
- PROVISIONAL_STATUS.md: appended a correction after the "carries over" line noting
  rho=604 is the old box-proxy leftover; correct target for the 1390 kg sedan is
  rho=115.7. Historical entry left intact per this file's preserve-not-delete convention.
- README.md: freshened the status date (July 9 snapshot, reviewed July 13); hedged the
  truck_trimmed.ply line (closed July 10 as not vehicle-proportioned); corrected the
  "box proxy in both L2 scripts" claim to distinguish Track 2 (generic 1.0 x 1.6 x 1.5
  box) from Track 1's box_sdf (sedan 4.66 x 1.79 x 1.44 box).

## Track 1 live mesh check (the important nuance, do not lose this)

Verified July 13 by reading the live code and measuring the meshes on Vista:

- Track 1's FloodScene (mpm-engine/examples/flood_vehicle.py) DOES load a real mesh.
  Line 49: DEFAULT_PLY = Path(__file__).resolve().parents[2] / "truck_trimmed.ply",
  which resolves to /work/11603/jcerrell0629/vista/truck_trimmed.ply (exists). It flows
  into run(vehicle_path=DEFAULT_PLY), the --vehicle argparse default, and
  load_vehicle(vehicle_path) -> load_gaussians_ply. It is a real 3DGS splat with 191107
  vertices, NOT a box proxy.
- BUT it is wrong-scale as loaded: 1.4474 x 0.4500 x 0.4110 m, which is 0.31x / 0.25x /
  0.29x the 4.66 x 1.79 x 1.44 m sedan target, roughly 3 to 4x too small on every axis.
  It is a real splat at model scale. The code supports Froude-scaling via
  load_vehicle(target_length=5.5), but the default run does not invoke it, so the loaded
  geometry stays at 1.45 m.
- This is NOT a contradiction between CLAUDE.md and the satellite docs. They track
  different axes: CLAUDE.md (mesh vs box) is right that a real mesh loads;
  STATUS.md and PROVISIONAL_STATUS.md (full-size vs not) are right that no full-size
  vehicle is wired into the committed pipeline, and that the box_sdf_collider_setup.py
  variant uses a sedan-scale box, not this mesh. Reversing either doc would write
  something false, so neither satellite doc was changed on the mesh point.
- CLAUDE.md's "Vehicle mesh, corrected" section is being sharpened to state all of the
  above (real splat, model scale, Froude option, box_sdf variant). That edit is a
  CLAUDE.md-only change (gitignored, personal, out of the Phase 8 commit).
- Two other .ply files on Vista are dead ends, not loaded by default, do not
  re-investigate: car_mesh.ply (0.333 x 0.174 x 0.715 m, tiny Poisson attempt) and
  car_mesh_rescaled.ply (4.66 x 2.43 x 10.00 m, broken 10 m height).

## Skill fork resolution

- The file at ~/.claude/skills/bug-triage-protocol/SKILL.md had been silently overwritten
  by a second, differently-structured version (10490 bytes, "Claude Code only" scope, 9
  failure classes, Cluster A-D reference case).
- Restored the 8851-byte N-panel version (md5 9bbabeab21f879f0067669ecd7a1167) as
  canonical, because it matches what CLAUDE.md's KEY PATHS and SKILL ROUTING sections
  describe (N panels, dynamic count, split across Vista and Mac) and fits the real
  workflow, whereas the 10490 version's Claude-Code-only scope is narrower.
- The 10490 version was archived, not deleted, at
  docs/session_notes/archive/2026-07-13_bug-triage-protocol-SKILL_10490B_claude-code-only.md.
- The restore source was docs/session_notes/bug-triage-protocol-SKILL_UNMERGED_VARIANT.md.
- Vista has no bug-triage-protocol skill installed: the directory
  /home1/11603/jcerrell0629/.claude/skills/bug-triage-protocol/ exists but is empty.

## f6be080 flag, left for later

git status shows .claude/skills/bug-triage-protocol/SKILL.md as deleted in the Mac repo
working tree (it was added to the repo in commit f6be080). Left untouched this session. It
does not block anything. Open decision for a later session: whether skills belong in the
repo at all, or only in ~/.claude/skills/.

## Not committed in Phase 8

CLAUDE.md (gitignored, personal), anything under skills/, this note, and the archive
folder are all outside the Phase 8 commit. Phase 8 commits only the two session docs
(2026-07-12 and 2026-07-13 UPDATED) and the four doc-content edits listed above.
