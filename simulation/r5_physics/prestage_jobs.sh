#!/usr/bin/env bash
# =============================================================================
# D4 pre-staged batch jobs. Companion to docs/R5_PHYSICS_BATCH_MANIFEST.md,
# which carries the pass criteria. Read that first: the criteria are stated
# BEFORE the runs on purpose, so no result can be graded after the fact.
#
# This script does NOTHING without --go. Printing the plan is the default,
# because the whole point is that it is inspectable before it costs anything.
#
# Usage:
#   bash prestage_jobs.sh                 print the plan and run the preflight
#   bash prestage_jobs.sh --preflight     EXECUTE the path/sha/engine checks on Vista,
#                                         exit non-zero if any fails
#   bash prestage_jobs.sh --stage         copy the sphere scene to Vista (jobs B and C)
#   bash prestage_jobs.sh --go A          emit job A's script and submit line
#   bash prestage_jobs.sh --go B          ... job B
#   bash prestage_jobs.sh --go C          ... job C (only after B passes)
#
# NEVER idev. Interactive burned 98.5 to 99.1 percent of Vista node-hours with
# 95 of 184 runs ending in TIMEOUT. Everything here is batch via tacc_submit.
#
# sim_standing.py is NEVER edited: its sha256 stamps every published run.
# There is no --settle-frames and no --seed flag; settle is constructor-only,
# so every canonical-driver run below is at the canonical settle of 8.
# =============================================================================
set -uo pipefail

VISTA_ROOT=/work/11603/jcerrell0629/vista

# THE ENGINE AND THE DRIVER LIVE IN DIFFERENT ROOTS ON VISTA. Verified live
# 2026-08-17 by find + sha256sum over the whole of $WORK:
#   can-it-ford/            has mpm-engine/.venv and mpm-engine/src, and the hull,
#                           but renders/ holds only mpm-engine-out and
#                           multigeom_2026-08-12_render. THERE IS NO DRIVER HERE.
#   can-it-ford-track1-6dof/ has renders/yaris_render_s1/sim_standing.py at exactly
#                           DRIVER_SHA below, but NO mpm-engine.
# The original DRIVER line pointed at can-it-ford/renders/yaris_render_s1/ and
# resolved to "No such file or directory", so every job A run would have died at
# launch. Four other copies carry the same sha (render_s2/multigeom_2026-08-08,
# d5_settle, d5_seedpolicy, can-it-ford-track2-realism); track1-6dof is chosen
# because it is the canonical track-1 tree. Two other hashes exist under $WORK
# (5215c38b in the as_ran_local_copies trees, 7236e474 in class_specific) and
# neither is the published driver.
#
# cd $REPO stays can-it-ford even though the driver is elsewhere, and that is
# correct, not an oversight: sim_standing.py:14 hardcodes
# VEHICLE_DIR = Path("/work/.../vista/can-it-ford/vehicle_geometry_research")
# as an ABSOLUTE path, so the driver is cwd-independent for the hull. Confirmed
# live: the hull is present under both roots.
PY=$VISTA_ROOT/can-it-ford/mpm-engine/.venv/bin/python
ENGINE=$VISTA_ROOT/can-it-ford/mpm-engine/src
DRIVER=$VISTA_ROOT/can-it-ford-track1-6dof/renders/yaris_render_s1/sim_standing.py
REPO=$VISTA_ROOT/can-it-ford
# Jobs B and C originally ran the sphere scene by a path RELATIVE to $REPO, which had
# never been staged: `find $WORK -name sphere_heave.py` returned NOTHING on 2026-08-17.
# This branch is 36 commits ahead of main and unpushed, while Vista's can-it-ford
# checkout sits on main at 15275f2, so the file could not have arrived by any route.
# The scene now lives in its OWN directory and is referenced absolutely, for two
# reasons: writing into Vista's git checkout would leave untracked files in a tree
# other machines and sessions share, and an absolute path cannot be broken by a cd.
# Stage it with --stage.
SCENE_DIR=$VISTA_ROOT/d4_scene
DRIVER_SHA=4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9

# Local helper that owns the pooled SSH ControlMaster. Override with TACC=...
TACC=${TACC:-/Users/josie/can-it-ford/scripts/tacc.sh}

# Repeat count for job A2. Drop to 5 first if the allocation is short.
NREP=${NREP:-10}
# Frames. 250/200 rather than 90: 24 percent of the canonical 91-frame vmag
# series hit the transient cap, and 0 of 17 reach a trustworthy blocking plateau.
FRAMES_CANON=250
FRAMES_SPHERE=200

# PREFLIGHT NOW EXECUTES. It used to `echo` these four lines as strings for a human to
# run, while both this script's usage text ("run ONLY the path/sha checks on Vista") and
# START_HERE section 2 ("Or just: prestage_jobs.sh --preflight") described it as a check.
# It could not fail, so it never reported that DRIVER did not exist. A check that cannot
# fail is not a check. This one exits non-zero.
preflight() {
  echo "# --- PREFLIGHT, executed against Vista, costs nothing ---"
  local rc=0

  echo "== driver identity =="
  local got
  got=$("$TACC" vista "sha256sum $DRIVER 2>&1 | awk '{print \$1}'" 2>/dev/null | tr -d '[:space:]')
  if [ "$got" = "$DRIVER_SHA" ]; then
    echo "  OK   $DRIVER"
    echo "       sha256 $got"
  else
    echo "  FAIL $DRIVER"
    echo "       expected $DRIVER_SHA"
    echo "       got      ${got:-<missing or unreadable>}"
    echo "       STOP: Vista's driver would not be the one that stamped every published run."
    rc=1
  fi

  echo "== scene staged for jobs B and C =="
  if "$TACC" vista "test -f $SCENE_DIR/sphere_heave.py" >/dev/null 2>&1; then
    echo "  OK   $SCENE_DIR/sphere_heave.py"
  else
    echo "  FAIL $SCENE_DIR/sphere_heave.py is absent. Jobs B and C cd to \$REPO and run"
    echo "       it by a RELATIVE path, so they would die at launch. Run: $0 --stage"
    rc=1
  fi

  echo "== engine =="
  "$TACC" vista "$PY -c 'import warpmpm, warpmpm.geometry as g; print(\"  OK   \"+warpmpm.__file__); print(\"       geometry: \"+\", \".join([s for s in sorted(dir(g)) if not s.startswith(\"_\")][:6]))'" 2>&1 | tail -3 || rc=1

  echo "== gpu (login node reports none; this is informational, not a gate) =="
  "$TACC" vista "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1 | head -2" 2>&1 | tail -2

  echo "# preflight rc=$rc"
  return $rc
}

# Stage the scene jobs B and C need. Copies only D4's own files, into a directory this
# branch owns, and never touches sim_standing.py or anything else in the Vista tree.
stage() {
  local here
  here=$(cd "$(dirname "$0")" && pwd)
  echo "# staging $here -> vista:$SCENE_DIR"
  "$TACC" vista "mkdir -p $SCENE_DIR" || return 1
  for f in sphere_heave.py kramer_benchmark.py test_sphere_geometry.py test_sphere_dryrun.py; do
    [ -f "$here/$f" ] || { echo "  skip (absent locally) $f"; continue; }
    scp -q "$here/$f" "vista:$SCENE_DIR/$f" && echo "  sent $f" || echo "  FAILED $f"
  done
  echo "# verify"
  "$TACC" vista "ls -l $SCENE_DIR" 2>&1 | tail -8
}

job_a() {
  cat <<EOF
#!/usr/bin/env bash
# JOB A: brake state (A1) fused with repeats + P2G order-dependence (A2).
# Fused deliberately: A1 is ~45 s of compute against ~80-120 s of warpmpm
# import startup, so its own job would spend more on startup than on physics.
set -uo pipefail
export PYTHONPATH=$ENGINE:\${PYTHONPATH:-}
OUT=$VISTA_ROOT/d4_jobA
mkdir -p \$OUT
cd $REPO

echo "TIMING_ANCHOR_START=\$(date +%s)"   # re-costs the whole manifest on contact
sha256sum $DRIVER

# --- A1: brake-state sweep on sweepV_g64_v0p5's canonical arguments ----------
# mu=0.55 MUST reproduce STUCK or the whole job is void.
# mu=0.0250 tests the INFERRED STUCK->SLIDE flip.
# mu=0.30 is logged INDETERMINATE IN ADVANCE: the bracket (0.369, 0.739]
#         straddles this run's 0.5 m/s, so neither outcome confirms anything.
for MU in 0.55 0.30 0.0250; do
  echo "=== A1 mu=\$MU ==="
  \$( which time ) -p $PY $DRIVER --label brake_mu\${MU} --out \$OUT/brake_mu\${MU} \\
      --depth 0.30 --velocity 0.5 --grid 64 --mass 1100 --eta 1.0e-3 \\
      --frames $FRAMES_CANON --floor-friction \$MU --vehicle yaris
  echo "RC_A1_mu\${MU}=\$?"
done

# --- A2: repeats at FIXED config, no seed change (there is no seed flag) -----
# Targets are the two boundary cases: g96_m2337 at a one-frame margin, and the
# only STUCK. Repeating comfortable runs measures nothing.
for i in \$(seq 1 $NREP); do
  $PY $DRIVER --label rep_g96m2337_\$i --out \$OUT/rep_g96m2337_\$i \\
      --depth 0.30 --velocity 1.5 --grid 96 --mass 2337 --eta 1.0e-3 \\
      --frames $FRAMES_CANON --floor-friction 0.55 --vehicle yaris
  echo "RC_A2_g96m2337_\$i=\$?"
  $PY $DRIVER --label rep_v0p5_\$i --out \$OUT/rep_v0p5_\$i \\
      --depth 0.30 --velocity 0.5 --grid 64 --mass 1100 --eta 1.0e-3 \\
      --frames $FRAMES_CANON --floor-friction 0.55 --vehicle yaris
  echo "RC_A2_v0p5_\$i=\$?"
done
echo "TIMING_ANCHOR_END=\$(date +%s)"
echo ALLDONE
EOF
}

job_b() {
  cat <<EOF
#!/usr/bin/env bash
# JOB B: Kramer sphere hydrostatic pilot. Compare against 69.2180 N, which is
# rho_w=998.2 (Table 1) and g=9.81 (engine). NOT 69.3428, the superseded value.
set -uo pipefail
export PYTHONPATH=$ENGINE:\${PYTHONPATH:-}
OUT=$VISTA_ROOT/d4_jobB
mkdir -p \$OUT
echo "TIMING_ANCHOR_START=\$(date +%s)"
$PY $SCENE_DIR/sphere_heave.py --fixed \\
    --n-grid 64 --lim 1.2 --depth 0.5 --h0-over-d 0.0 \\
    --frames $FRAMES_SPHERE --sdf-res 96 --verbose \\
    --out \$OUT/sphere_fixed_g64.json
echo "RC_B=\$?"
echo "TIMING_ANCHOR_END=\$(date +%s)"
echo ALLDONE
EOF
}

job_c() {
  cat <<EOF
#!/usr/bin/env bash
# JOB C: Kramer free heave decay, three drops. GATED ON JOB B PASSING.
# The 1-DOF integrator and set_sdf_pose have never run; if B fails its collider
# or force criteria, C is not worth the wall clock.
# NOTE: the published time series is still blocked (MDPI /s1, 403), so only the
# self-consistency criteria in the manifest can be graded on arrival.
set -uo pipefail
export PYTHONPATH=$ENGINE:\${PYTHONPATH:-}
OUT=$VISTA_ROOT/d4_jobC
mkdir -p \$OUT
echo "TIMING_ANCHOR_START=\$(date +%s)"
for H0D in 0.1 0.3 0.5; do
  echo "=== C h0/D=\$H0D ==="
  $PY $SCENE_DIR/sphere_heave.py \\
      --n-grid 117 --lim 2.2 --depth 0.5 --h0-over-d \$H0D \\
      --frames $FRAMES_SPHERE --sdf-res 96 --verbose \\
      --out \$OUT/sphere_h0_\${H0D}.json
  echo "RC_C_\${H0D}=\$?"
done
echo "TIMING_ANCHOR_END=\$(date +%s)"
echo ALLDONE
EOF
}

submit_line() {   # $1 = job letter, $2 = walltime
  cat <<EOF

# --- submit via the typed tool, NOT idev, NOT raw srun -----------------------
tacc_submit(
  host     = "vista",
  nodes    = 1,
  walltime = "$2",
  cwd      = "$REPO",
  logfile  = "$VISTA_ROOT/d4_job$1/job$1.out",
  command  = "bash $VISTA_ROOT/d4_job$1/run_job$1.sh"
)
EOF
}

case "${1:-}" in
  --preflight) preflight ;;
  --stage) stage ;;
  --go)
    case "${2:-}" in
      A) job_a; submit_line A "00:45:00" ;;
      B) job_b; submit_line B "00:45:00" ;;
      C) job_c; submit_line C "04:30:00" ;;
      *) echo "usage: $0 --go {A|B|C}" >&2; exit 2 ;;
    esac ;;
  *)
    cat <<EOF
D4 pre-staged batch plan. Nothing runs without --go.

  JOB A  ~0.30 node-h  brake sweep (45 s) FUSED with ${NREP} repeats + P2G onset
  JOB B  ~0.35 node-h  sphere hydrostatic pilot vs 69.2180 N
  JOB C  ~3.7  node-h  sphere free decay, 3 drops at lim=2.2 [gated on B; /s1 blocked]

  Total ~4.3 node-hours against 629 SU remaining. SU is NOT the binding
  constraint; wall clock and socket availability are.

  Drop order if short: C, then NREP 10->5, then B's frames 200->120.
  NEVER drop A1: 45 seconds, and the only item that turns an INFERRED claim
  into a measurement. If only one thing runs, run A1.

  Pass criteria are in docs/R5_PHYSICS_BATCH_MANIFEST.md and are fixed IN
  ADVANCE. Read them before grading anything.

EOF
    preflight ;;
esac
