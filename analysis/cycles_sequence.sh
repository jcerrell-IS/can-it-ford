#!/bin/bash
# Render a warpmpm rollout as a path-traced SEQUENCE, then encode it.
#
#   analysis/cycles_sequence.sh <run_dir> <hull.ply> <work_dir> [stride] [samples]
#
# WHY A SEQUENCE AND NOT A STILL. A still of a hull in water asserts a result; a
# sequence shows it. The canonical runs are not static: g64_yaris_regression's
# vehicle slides 0.638 m over its 90 frames, which IS the SLIDE verdict this
# project publishes, and the free surface goes from flat to disturbed. Neither is
# visible in one frame.
#
# EVERY FRAME IS RECONSTRUCTED SEPARATELY. prep_cycles_scene.py runs splashsurf on
# that frame's own particle positions, so the water is not a deforming template
# carried between frames and nothing is interpolated. That is why this is slow, and
# it is the reason the motion in the water is the solver's rather than the
# renderer's.
#
# COST, measured on an M-series Mac with Blender 5.2 on Metal: about 30 s per frame
# at --cube-mult 0.75 and 56 samples at 960x600, so a stride-2 pass over 90 frames
# is roughly 22 minutes. Raise the stride before raising the samples.
set -euo pipefail

RUN=${1:?run directory containing rollout.npz}
HULL=${2:?hull .ply, READ not copied}
WORK=${3:?work directory}
STRIDE=${4:-2}
SAMPLES=${5:-56}

HERE=$(dirname "$0")
UV=${UV:-/opt/homebrew/bin/uv}
BLENDER=${BLENDER:-/opt/homebrew/bin/blender}
HDRI=${HDRI:-$HERE/../assets/DaySkyHDRI002A_1K_HDR.exr}

mkdir -p "$WORK/frames" "$WORK/scene"
i=0
# 90 frames is the canonical length; a shorter run simply stops early.
for f in $(seq 0 "$STRIDE" 88); do
  "$UV" run --quiet --with numpy --with scipy --with trimesh --with matplotlib \
      --with pysplashsurf python3 "$HERE/prep_cycles_scene.py" \
      --run "$RUN" --frame "$f" --hull "$HULL" \
      --outdir "$WORK/scene" --half 4.2 --cube-mult 0.75 >/dev/null
  printf -v n "%04d" "$i"
  "$BLENDER" --background --python "$HERE/cycles_render.py" -- \
      --scene "$WORK/scene" --out "$WORK/frames/frame_$n.png" \
      --hdri "$HDRI" --wet 0.85 --far-water \
      --samples "$SAMPLES" --res 960 --res-y 600 \
      --cam-elev 6.0 --cam-azim 137 --cam-dist 12.4 --lens 78 >/dev/null
  i=$((i + 1))
  echo "frame $f -> $n"
done

ffmpeg -y -framerate 12 -i "$WORK/frames/frame_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 19 \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$WORK/motion.mp4"
echo "wrote $WORK/motion.mp4 from $i frames"
