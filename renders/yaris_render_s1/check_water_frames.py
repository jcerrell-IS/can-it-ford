import sys

import imageio.v3 as iio
import numpy as np
from skimage.measure import label

MP4 = sys.argv[1] if len(sys.argv) > 1 else "hero_g64_m1100_FIXED.mp4"
WANT = [int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["5", "45", "85"])]
CROP_FRAC = 0.86
COOL_MARGIN = 6.0
YELLOW_MARGIN = 30.0
MIN_BLOB_FRAC = 0.02


def cool_mask(img):
    r = img[:, :, 0].astype(np.float64)
    g = img[:, :, 1].astype(np.float64)
    b = img[:, :, 2].astype(np.float64)
    cool = ((g - r) > COOL_MARGIN) | ((b - r) > COOL_MARGIN)
    yellow = ((g - b) > YELLOW_MARGIN) & ((r - b) > YELLOW_MARGIN)
    return cool | yellow


def main():
    frames = iio.imread(MP4)
    n = frames.shape[0]
    print("MP4 %s  frames=%d  size=%dx%d" % (MP4, n, frames.shape[2], frames.shape[1]))
    print("rule: viridis pixel is (G-R)>%.0f or (B-R)>%.0f or yellow (G-B and R-B)>30; backdrop is warm grey "
          "R>G>B; largest connected blob must exceed %.0f pct of the cropped frame"
          % (COOL_MARGIN, COOL_MARGIN, MIN_BLOB_FRAC * 100))
    print("")
    verdicts = []
    for f in WANT:
        if f >= n:
            print("DEGRADE frame %d beyond end (%d frames)" % (f, n))
            verdicts.append((f, 0.0, 0.0, "MISSING"))
            continue
        img = frames[f][:, :, :3]
        w = img.shape[1]
        crop = img[:, : int(w * CROP_FRAC), :]
        m = cool_mask(crop)
        lab = label(m)
        if lab.max() > 0:
            counts = np.bincount(lab.ravel())
            counts[0] = 0
            big = int(counts.max())
        else:
            big = 0
        total = float(m.size)
        frac_all = float(m.sum()) / total
        frac_big = big / total
        png = "frame_check_f%04d.png" % f
        iio.imwrite(png, img)
        v = "WATER VISIBLE" if frac_big > MIN_BLOB_FRAC else "NO WATER"
        verdicts.append((f, frac_all, frac_big, v))
        print("frame %3d  cool_px=%6.2f pct  largest_blob=%6.2f pct  -> %-14s saved %s"
              % (f, frac_all * 100, frac_big * 100, v, png))
    print("")
    bad = [f for f, _, _, v in verdicts if v != "WATER VISIBLE"]
    if bad:
        print("BLOCKER: frames with no water: %s" % bad)
        return 1
    print("T1.3 WATER CHECK PASS: one connected water body visible in frames %s"
          % [f for f, _, _, _ in verdicts])
    return 0


if __name__ == "__main__":
    sys.exit(main())
