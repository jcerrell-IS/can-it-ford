"""Rebuild Fig. 1 (the reconstruct-to-decide pipeline) for
paper/conference_101719.tex, with unrealized stages drawn as dashed boxes.

WHY THIS SCRIPT EXISTS
  paper/pipeline_diagram.png has no generator anywhere in the repository or in
  git history (checked live: `git log --all -- '*pipeline_diagram*'` returns
  only the binary). The five equal solid boxes therefore could not be edited at
  source. Geometry below was measured back off that PNG pixel by pixel so this
  reproduction is faithful rather than a redesign:

    canvas        1613 x 512
    box i         x = 36 + 315*i, width 280   (i = 0..4)
    box y         119 -> 391                  (height 272)
    arrows        centered y = 255, spanning the 36 px inter-box gap
    fill          #F4F4F4, verdict box #E8E8E8 with a drop shadow
    border        black, 3 px

WHICH STAGES ARE DASHED, AND WHY TWO AND NOT ONE
  The paper's own Fig. 1 caption (conference_101719.tex line 67) states:
    "The Gaussian-splat reconstruction and the PhysGaussian kernel-to-particle
     bridge are designed and not yet built."
  and Section II-B (line 83) adds that no drop-in flood-video-to-Genesis-MPM
  pipeline exists and that PhysGaussian's reference implementation targets a
  Warp MPM solver, not Genesis. Section IV-A (line 174) further FLAGs that
  splat-checkpoint training for the one captured scene is NOT confirmed
  complete.

  So stages 2 and 3 are both unrealized. Dashing only stage 3 would leave
  "Gaussian Splat" solid and thereby assert it IS realized, which contradicts
  the caption directly above it. UNBUILT is the single knob:
      UNBUILT = {1, 2}   both unrealized stages dashed  (matches the caption)
      UNBUILT = {2}      PhysGaussian Bridge only

  Stage 1 stays solid: Section IV-A confirms COLMAP structure-from-motion is
  complete for one real scene ("Drain A"), so video capture is genuinely done.
  Stages 4 and 5 stay solid: 17 coupled runs in render_s2 exercise them. Not "gated":
  no artifact records a gate pass or fail, only gate inputs. data/all_runs_inventory.csv
  has 42 columns and none of them is a gate outcome; analysis/render_v1/gates.py prints
  PASS/FAIL to stdout but never persists it.

OUTPUT
  paper/figures_review/pipeline_diagram_v2.svg   NEW file, overwrites nothing
  paper/figures_review/pipeline_diagram_v2.pdf   via rsvg-convert, TRUE VECTOR

Stdlib only for the SVG, matching analysis/paper_fig_mass_grid_sweep_v2.py.
The PDF step shells out to rsvg-convert (librsvg 2.62.3, /opt/homebrew/bin).
"""
import subprocess
from pathlib import Path

REPO = Path('/Users/josie/can-it-ford')
OUTDIR = REPO / 'paper' / 'figures_review'
OUTDIR.mkdir(parents=True, exist_ok=True)
SVG = OUTDIR / 'pipeline_diagram_v2_GRIDAWARE.svg'
PDF = OUTDIR / 'pipeline_diagram_v2_GRIDAWARE.pdf'

# ---- geometry measured off paper/pipeline_diagram.png --------------------
W, H = 1613, 512
BOX_W, BOX_X0, PITCH = 280, 36, 315
BOX_Y0, BOX_Y1 = 119, 391
RADIUS = 18
MID_Y = (BOX_Y0 + BOX_Y1) / 2          # 255.0
FILL, FILL_VERDICT = '#F4F4F4', '#E8E8E8'
STROKE_W = 3
FONT = "DejaVu Serif, Times New Roman, Times, serif"
FS = 27                                 # body size, px
LINE_H = 34

# index -> lines of label text
STAGES = [
    ["Real Video", "(flooded / water-", "adjacent scene)"],
    ["Gaussian Splat", "(gsplat, LS6)"],
    ["PhysGaussian", "Bridge", "(kernel to MPM", "particle seed)"],
    ["Genesis MPM", "(rigid-fluid", "coupling)"],
    ["FORD /", "NO-FORD", "Verdict"],
]

# Stages designed but not built. See module docstring for the justification.
UNBUILT = {1, 2}

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" role="img">',
    '<title>Can It Ford? reconstruct-to-decide pipeline</title>',
    '<desc>Five-stage pipeline. The Gaussian Splat and PhysGaussian Bridge '
    'stages are drawn with dashed borders to mark them as conceptual, not '
    'part of the path used for the reported results.</desc>',
    '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
    'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0 0L10 5L0 10Z" fill="#000"/></marker></defs>',
    f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
]

for i, lines in enumerate(STAGES):
    x = BOX_X0 + PITCH * i
    is_verdict = (i == len(STAGES) - 1)
    if is_verdict:                       # drop shadow, as in the original
        parts.append(
            f'<rect x="{x+5}" y="{BOX_Y0+5}" width="{BOX_W}" '
            f'height="{BOX_Y1-BOX_Y0}" rx="{RADIUS}" fill="#BFBFBF"/>')
    dash = ' stroke-dasharray="14 10"' if i in UNBUILT else ''
    parts.append(
        f'<rect x="{x}" y="{BOX_Y0}" width="{BOX_W}" height="{BOX_Y1-BOX_Y0}" '
        f'rx="{RADIUS}" fill="{FILL_VERDICT if is_verdict else FILL}" '
        f'stroke="#000000" stroke-width="{STROKE_W}"{dash}/>')

    cx = x + BOX_W / 2
    y0 = MID_Y - (len(lines) - 1) * LINE_H / 2 + FS * 0.35
    for k, ln in enumerate(lines):
        parts.append(
            f'<text x="{cx}" y="{y0 + k*LINE_H}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="{FS}" fill="#000000">'
            f'{esc(ln)}</text>')

    if not is_verdict:                   # arrow into the next box
        ax0 = x + BOX_W + 7
        ax1 = x + PITCH - 7
        parts.append(
            f'<line x1="{ax0}" y1="{MID_Y}" x2="{ax1}" y2="{MID_Y}" '
            f'stroke="#000000" stroke-width="4" marker-end="url(#arrow)"/>')

parts.append(
    f'<text x="{BOX_X0 + PITCH*4 + BOX_W}" y="454" text-anchor="end" '
    f'font-family="{FONT}" font-size="25" font-style="italic" fill="#444444">'
    f'L0 / L1 / L2 orchestrator</text>')
parts.append('</svg>')

SVG.write_text('\n'.join(parts), encoding='utf-8')
print(f"wrote {SVG}  ({SVG.stat().st_size} bytes)")
print(f"dashed stages (0-indexed): {sorted(UNBUILT)} -> "
      f"{[STAGES[i][0] for i in sorted(UNBUILT)]}")

subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(PDF), str(SVG)],
               check=True)
raw = PDF.read_bytes()
n_img = raw.count(b'/Subtype /Image') + raw.count(b'/Subtype/Image')
print(f"wrote {PDF}  ({len(raw)/1024:.1f} KB)")
print(f"vector check: imageXObjects={n_img}, DCTDecode={raw.count(b'DCTDecode')}"
      f"  -> {'TRUE VECTOR' if n_img == 0 else 'RASTER, INVESTIGATE'}")
