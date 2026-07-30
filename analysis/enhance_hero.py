import os
import sys

import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S1 = os.path.join(REPO, "renders", "yaris_render_s1")
MP4 = os.path.join(S1, "hero_g64_m1100_FIXED.mp4")
OUT = os.path.join(REPO, "figures", "hero_enhanced.png")
COLW_IN = 16.67
UPSCALE = 2
PAD = 12


def peak_frame_index():
    m = os.path.join(S1, "g64_m1100", "metrics.csv")
    d = np.loadtxt(m, delimiter=",", skiprows=1)
    cols = open(m).readline().strip().split(",")
    dmag = d[:, cols.index("dmag")]
    tcol = d[:, cols.index("t")]
    k = int(np.argmax(dmag))
    return k, float(dmag[k]), float(tcol[k])


def content_rows(img):
    g = img.mean(axis=2)
    bg = np.median(g)
    mask = np.abs(g - bg) > 10
    rows = np.where(mask.any(axis=1))[0]
    return int(rows.min()), int(rows.max())


def main():
    frames = iio.imread(MP4)
    k, dmag, t = peak_frame_index()
    k = min(k, frames.shape[0] - 1)
    img = frames[k][:, :, :3]
    h0, w0 = img.shape[:2]

    r0, r1 = content_rows(img)
    r1 = min(h0, r1 + PAD)
    cropped = img[r0:r1, :, :]
    h1, w1 = cropped.shape[:2]

    im = Image.fromarray(cropped)
    im = im.resize((w1 * UPSCALE, h1 * UPSCALE), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2.4, percent=115, threshold=3))
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im.save(OUT, optimize=True)

    print("source frame        %d of %d  |d| = %.6f m at t = %.3f s" % (k, frames.shape[0], dmag, t))
    print("original            %d x %d px   %.0f dpi at %.2f in" % (w0, h0, w0 / COLW_IN, COLW_IN))
    print("dead rows removed   %d at bottom" % (h0 - r1))
    print("cropped             %d x %d px   aspect %.3f" % (w1, h1, w1 / float(h1)))
    print("enhanced            %d x %d px   %.0f dpi at %.2f in"
          % (im.size[0], im.size[1], im.size[0] / COLW_IN, COLW_IN))
    print("height at %.2f in wide: %.2f in" % (COLW_IN, COLW_IN * im.size[1] / float(im.size[0])))
    print("WROTE %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
