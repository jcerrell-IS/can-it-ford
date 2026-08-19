#!/usr/bin/env python3
"""Stamp a Cycles frame with the numbers that let a reader falsify it.

    cycles_caption.py --scene DIR --image FILE --out FILE

WHY A CAPTION IS PART OF THE RENDER AND NOT AN EXTRA
  A path-traced frame is far more persuasive than the matplotlib diagnostic it
  replaces, and persuasiveness is the hazard. The diagnostic renderer earned trust
  by printing its gate numbers next to the picture; this one has to do the same or
  it is a nicer picture with less evidence behind it. Every number in the strip is
  copied from the run's own summary.json or measured by prep_cycles_scene.py, and
  the strip states plainly which parts of the image are solver output and which
  are appearance invented in the renderer.

WHAT IS DELIBERATELY IN THE STRIP
  The hull vertex count and its source file, because the three vehicle classes are
  NOT matched on mesh quality and a reader comparing the frames will otherwise
  read a mesh-provenance difference as a physics difference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = (
    "/System/Library/Fonts/Supplemental/Andale Mono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
)


def font(sz):
    for f in FONTS:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hull-verts", type=int, default=0)
    ap.add_argument("--title", default="")
    a = ap.parse_args()

    sc = json.loads((Path(a.scene) / "scene.json").read_text())
    ph = sc.get("physics", {})
    im = Image.open(a.image).convert("RGB")
    W, H = im.size

    pad, lh = int(W * 0.018), int(W * 0.0165)
    bar = lh * 5 + pad * 2
    out = Image.new("RGB", (W, H + bar), (14, 15, 17))
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    fb, fs = font(int(lh * 0.70)), font(int(lh * 0.58))

    hull = Path(sc.get("hull_ply_source", "")).name
    title = a.title or "%s, %s" % (ph.get("label", "?"), sc.get("run", "?"))
    d.text((pad, H + pad), title, font=fb, fill=(238, 238, 240))

    def fmt(v, f="%.4g"):
        return "n/a" if v is None else (f % v if isinstance(v, (int, float)) else str(v))

    l2 = ("PHYSICS, from the solver: mass %s kg   nominal depth %s m   "
          "inflow %s m/s   n_grid %s   dx %s m   %s water layers   rho %s kg/m3"
          % (fmt(ph.get("mass_kg")), fmt(ph.get("depth_m")), fmt(ph.get("velocity_ms")),
             fmt(ph.get("n_grid")), fmt(ph.get("dx"), "%.5f"),
             fmt(ph.get("water_layers")), fmt(ph.get("realized_rho"), "%.2f")))
    l3 = ("MEASURED HERE: free surface %.4f m above floor   surround %.4f m   "
          "rigid-transform residual %.2e m   frame %d of %d at %d fps"
          % (float(sc.get("still_water_z", 0)) - float(sc.get("floor_z", 0)),
             float(sc.get("surround_z") or 0.0),
             float(sc.get("transform_max_err_m", 0)), int(sc.get("frame", 0)),
             90, int(sc.get("fps", 0))))
    l4 = ("RENDER HULL: %s, %s vertices. NOT the simulation's collider resolution; "
          "the three classes are not matched on mesh quality."
          % (hull, "{:,}".format(a.hull_verts) if a.hull_verts else "?"))
    l5 = ("APPEARANCE, invented in the renderer and carrying NO data: all optics, "
          "the paint/glazing/tyre split, and the flat water beyond the solver "
          "domain. warpmpm computes no optics.")

    for i, t in enumerate((l2, l3, l4, l5)):
        d.text((pad, H + pad + lh * (i + 1)), t, font=fs, fill=(176, 180, 186))

    out.save(a.out)
    print("[caption] wrote %s (%dx%d)" % (a.out, out.size[0], out.size[1]))


if __name__ == "__main__":
    main()
