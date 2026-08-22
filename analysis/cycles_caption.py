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


def wrap(d, text, font, maxw):
    """Greedy word wrap to a pixel width.

    Added after a caption overflowed the frame and CLIPPED the very figure it had
    just been asked to carry: the 47.6 percent volume loss ran off the right edge.
    A caption that silently truncates is worse than a shorter one, because the
    reader cannot tell that anything is missing. Every block is now measured and
    wrapped rather than trusted to fit.
    """
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def caption_composite(sc, im, a):
    """Caption for a multi-vehicle road scene.

    Says up front that the three vehicles never met: they are three independent
    runs, rigidly translated onto one road. An image of three cars in one flood is
    read as one event unless it says otherwise, and it was not one event.
    """
    W, H = im.size
    pad, lh = int(W * 0.016), int(W * 0.0132)
    vs = sc.get("vehicles", [])
    scratch = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    fb, fs = font(int(lh * 0.74)), font(int(lh * 0.62))
    maxw = W - 2 * pad

    blocks = [(a.title or "Flooded roadway, three vehicle classes", fb, (238, 238, 240)),
              ("THESE THREE VEHICLES WERE NEVER IN ONE SIMULATION. Three independent "
               "warpmpm runs, each rigidly TRANSLATED onto one road: hull and its own "
               "water move together, so every waterline is that run's, unaltered.",
               fs, (206, 176, 176))]
    for v in vs:
        ph = v.get("physics", {})
        blocks.append((
            "   %s  %s   mass %s kg   depth %.3f m at the crown   n_grid %s   "
            "dx %.5f m   render hull %s vertices"
            % (v.get("name", "?"), ph.get("label", ""), ph.get("mass_kg"),
               v.get("still_water_depth_m", 0.0), ph.get("n_grid"),
               ph.get("dx", 0.0), "{:,}".format(v.get("hull_verts", 0))),
            fs, (176, 180, 186)))
    blocks += [
        ("PROVENANCE IS NOT EQUAL ACROSS THESE THREE. Yaris and Silverado derive from "
         "the CCSA/NCAC documented set: teardown or scanning, measured or calibrated "
         "mass and inertia, full-scale NHTSA NCAP validation. The ROGUE IS NOT IN THAT "
         "SET; the documented midsize is a 2012 Camry.", fs, (214, 176, 150)),
        ("MESH LIMIT, AND IT WAS LOOKED AT: the Rogue and Silverado hulls are Poisson "
         "reconstructions and ARE the best of the 19 watertight candidates on this "
         "machine, at 16.6 and 13.5 deg mean dihedral against the Yaris's 7.6. THE "
         "SMOOTHEST ROGUE ON DISK IS MISSING 47.6 PERCENT OF THE CAR: smoothness and "
         "completeness trade off across the reconstruction sweep, so this hull is the "
         "compromise, not an oversight.", fs, (206, 186, 166)),
        ("NO REDISTRIBUTABLE CONVERSION OF ANY OF THESE MODELS HAS BEEN VERIFIED, in "
         "the result set of the one deep search that looked. That is a bounded negative "
         "from a named search, not proof none exists. These hulls are this project's "
         "own conversions and their licence question is OPEN.", fs, (206, 186, 166)),
        ("ROAD: crowned section from simulation/road_geometry.road_profile, width "
         "%.1f m, carriageway %.1f m, cross slope %.3f. The runs used a FLAT floor, so "
         "the crown is PRESENTATIONAL; read no depth off it."
         % (sc.get("road_width_total", 0.0), sc.get("road_carriageway", 0.0),
            sc.get("road_cross_slope", 0.0)), fs, (176, 180, 186)),
        ("ALSO PRESENTATIONAL: vehicle spacing, the flat water between and beyond the "
         "patches (%.4f m apart in height, three runs at three depths), all optics, the "
         "buildings and the road's longitudinal grade. No wheels, no suspension, no "
         "rolling degree of freedom." % sc.get("surround_spread_m", 0.0),
         fs, (176, 180, 186)),
    ]

    laid = []
    for text, f, col in blocks:
        for ln in wrap(scratch, text, f, maxw):
            laid.append((ln, f, col))
    bar = lh * len(laid) + pad * 2
    out = Image.new("RGB", (W, H + bar), (14, 15, 17))
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    for k, (ln, f, col) in enumerate(laid):
        d.text((pad, H + pad + lh * k), ln, font=f, fill=col)
    out.save(a.out)
    print("[caption] wrote %s (%dx%d), %d wrapped lines, nothing clipped"
          % (a.out, out.size[0], out.size[1], len(laid)))


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

    if sc.get("kind") == "road_composite":
        return caption_composite(sc, im, a)

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
