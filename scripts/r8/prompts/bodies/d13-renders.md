## YOUR SLOT: d13-renders, branch `claude/r9-renders`, worktree `.claude/worktrees/r9-renders`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d13-renders` first.

### The state, verified live by the coordinator before this dispatch

`analysis/render_multigeom_rollout.py` gives the WATER a real optical treatment (Schlick Fresnel, HDRI, Beer-Lambert absorption, GGX) and gives the VEHICLE a single flat Lambert term. The whole vehicle material is the `shade()` function around line 208:

```
def shade(base, n):
    sh = np.clip(n @ LIGHT, 0.0, 1.0) * 0.6 + 0.4
    return np.clip(sh[:, None] * base, 0.0, 1.0)
```

Separately, four PBR maps ARE tracked in the repo and referenced by nothing: `assets/Asphalt015.png`, `assets/Asphalt015_1K-JPG_Color.jpg`, `assets/Asphalt015_1K-JPG_NormalGL.jpg`, `assets/Asphalt015_1K-JPG_Roughness.jpg`. Confirm that "referenced by nothing" is still true with `/usr/bin/grep -rn Asphalt015` naming `renders/` and `data/` explicitly, because the shell `grep` here skips gitignored paths and would give you a false negative.

### Your unit

Bring the vehicle and the ground up to the standard the water already has, in the same renderer, without touching the physics or any simulation output.

1. Give the vehicle a material with the same ingredients the water already uses in this file. You are not inventing a shading model, you are applying the one that is already here to a second surface.
2. Wire the asphalt PBR set to the ground plane. Tracked-and-unreferenced assets are either a gap or dead weight; resolve which.
3. Produce a BEFORE and AFTER frame from the SAME rollout data and the same camera, and send both to Josie. A claim that a render improved is worth nothing without the pair.

### Hard boundaries

- You may NOT change any simulation output, any metric, any verdict, or any file under `renders/*/sim_*.py`. If a render change appears to alter a physical quantity, stop and report it, because that means the renderer is reading something it should not.
- The canonical Yaris hull and derived meshes are already public on origin and their licence question is UNRESOLVED. Do not add, move, or re-export any mesh. Read `.claude/memory/derived-hull-already-public-on-origin.md` before touching anything mesh-shaped.
- Slot d10-licence established last night that the root BSD-3 licence was claiming third-party material it does not own, and that four sources are reproduced as images. The asphalt maps have their own licence. Establish what it is from the file or its source before you make them part of a deliverable. If you cannot establish it, wire them behind a flag and say so; do not guess.
- This Mac has NO numpy in any system interpreter. Use `/Users/josie/.local/bin/uv` or `/opt/homebrew/bin/uv run --with numpy --with matplotlib --with scikit-image python3 ...`.

This is the one slot in this wave whose output is visual. Send the images with SendUserFile rather than describing them.
