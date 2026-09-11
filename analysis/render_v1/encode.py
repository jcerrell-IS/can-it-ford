from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frames", required=True)
    p.add_argument("--mp4", required=True)
    p.add_argument("--gif", required=True)
    p.add_argument("--fps", type=int, default=12)
    p.add_argument("--gif-stride", type=int, default=2)
    p.add_argument("--gif-width", type=int, default=1000)
    a = p.parse_args()

    fdir = Path(a.frames)
    pngs = sorted(fdir.glob("f_*.png"))
    if not pngs:
        raise SystemExit("no frames in %s" % fdir)
    print("frames found:", len(pngs))

    rc_mp4 = None
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        print("E1 imageio_ffmpeg binary:", exe)
        cmd = [exe, "-y", "-framerate", str(a.fps), "-i", str(fdir / "f_%04d.png"),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
               "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", a.mp4]
        r = subprocess.run(cmd, capture_output=True, text=True)
        rc_mp4 = r.returncode
        if rc_mp4 != 0:
            print("E1 FAILED rc=%d\n%s" % (rc_mp4, r.stderr[-1500:]))
        else:
            print("E1 OK wrote", a.mp4, Path(a.mp4).stat().st_size, "bytes")
    except Exception as exc:
        print("E1 EXCEPTION", type(exc).__name__, str(exc)[:300])

    sel = pngs[::a.gif_stride]
    imgs = []
    for q in sel:
        im = Image.open(q).convert("RGB")
        w, h = im.size
        nh = int(h * a.gif_width / w)
        imgs.append(im.resize((a.gif_width, nh), Image.LANCZOS).convert(
            "P", palette=Image.ADAPTIVE, colors=192))
    dur = int(1000 / a.fps * a.gif_stride)
    imgs[0].save(a.gif, save_all=True, append_images=imgs[1:], loop=0,
                 duration=dur, optimize=True, disposal=2)
    print("E2 OK wrote", a.gif, Path(a.gif).stat().st_size, "bytes,",
          len(imgs), "frames at", dur, "ms")


if __name__ == "__main__":
    main()
