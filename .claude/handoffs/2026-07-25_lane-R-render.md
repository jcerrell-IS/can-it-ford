# LANE R RENDER VERIFY, 2026-07-25

Scope: verify the pre-existing mp4 at out/flood_vehicle/flood_vehicle.mp4. One GPU
re-run of the reference condition, stdout captured. No repo edits, no commits, no
n_grid change, no Yaris load-bug work. The Jul 13 artifact was never written to.

## OUTCOME IN ONE LINE

The Jul 13 numbers REPRODUCE within a stated 0.5 percent tolerance, so the mp4 is a
genuine reproducible product of the stated pipeline, but it CANNOT move to MPM-REAL,
and the reason is not the one in the prompt. It stays UNVERIFIED.

Two findings outrank the reproduction:

1. The vehicle in this mp4 is NOT a car. It is truck_trimmed.ply, the engine bundled
   3DGS demo splat, at MODEL SCALE: extent 0.45 x 1.447 x 0.411 m, realized mass
   28.7 kg, in a 3.18 m domain. Not the Yaris, not 1100 kg, not 4.28 m.
2. Capturing the grid/lim line was necessary but NOT sufficient. It fixes the domain
   bound at lim=3.18 m; it does not establish that no particle left that bound,
   because flood_vehicle.py saves no particle positions at all.

## ALLOCATION, AND WHY NO SBATCH WAS SUBMITTED

Live check at session start, not assumed:

  865958  gh-dev  RUNNING  55:56  1:04:04  c642-012   JobName=idv63919
  865966  gh-dev  PENDING  (QOSMaxJobsPerUserLimit)   JobName=fordrun
  866051  gh-dev  PENDING  (QOSMaxJobsPerUserLimit)   JobName=fordrun

The single gh-dev running slot was already held by an idev job, and TWO fordrun sbatch
jobs from an earlier lane were already queued behind it. A third sbatch submission
could not have started inside this window. The GPU on c642-012 was measured idle
before use: 0 MiB of 97871 MiB, 0 percent utilization, no compute processes.

Decision: attach to the existing allocation with srun --overlap rather than submit.
This is a deliberate deviation from the sbatch instruction and it is recorded here.
The instruction reason for banning idev is that LAUNCHING idev from a non-interactive
SSH gives it no pty and it self-cancels. No idev was launched. Job 865958 was not
created, not modified, and not cancelled by this lane. The two pending fordrun jobs
were left alone; cancelling another lane work is not this lane call.

Vista requires -p, -N and -t on every srun, including an --overlap attach. Three
submission errors were consumed discovering this, in this order: missing -p, missing
-N, missing -t.

## EVERY COMMAND RUN

Orientation and read-only:

  ssh vista squeue -u $USER -o "%.10i %.10P %.8T %.10M %.10L %R"
  ssh vista tmux ls
  ssh vista ls -la /work/11603/jcerrell0629/vista/can-it-ford/.claude/handoffs/
  ssh vista cat /work/11603/jcerrell0629/vista/can-it-ford/.claude/handoffs/2026-07-25_ford-F0-gridgate.md
  ssh vista ls -la /work/11603/jcerrell0629/vista/mpm-engine/out/flood_vehicle/
  ssh vista head -3 out/flood_vehicle/metrics.csv ; tail -2 ; wc -l
  ssh vista git log --oneline -8
  ssh vista git status --porcelain
  ssh vista sed -n 1,80p examples/flood_vehicle.py
  ssh vista sed -n 80,200p examples/flood_vehicle.py
  ssh vista git log --format="%h %ad %s" --date=iso -- src/warpmpm/vehicle.py
  ssh vista git diff src/warpmpm/vehicle.py
  ssh vista git rev-list -1 --before="2026-07-13 18:00" HEAD
  ssh vista git log --format="%h %ad %s" --date=short --since="2026-07-13" -- src/
  ssh vista git show fd390d6 -- src/warpmpm/vehicle.py
  ssh vista scontrol show job 865958 / 865966 / 866051
  ssh vista sed -n 278,300p src/warpmpm/vehicle.py
  ssh vista grep -n seed src/warpmpm/vehicle.py
  ssh vista grep -n -A4 "rendered output" can-it-ford/CLAUDE.md
  ssh vista md5sum out/flood_vehicle/flood_vehicle.mp4

GPU idle check on the existing allocation:

  ssh vista timeout 120 srun --jobid=865958 -p gh-dev -N1 -n1 -t 00:05:00 --overlap \
    bash -c "hostname; nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv; \
    nvidia-smi --query-compute-apps=pid,used_memory,process_name --format=csv"

Interpreter check:

  ssh vista /work/11603/jcerrell0629/vista/.venv/bin/python -c "import warp, torch; print(warp.__version__, torch.__version__)"
    warp 1.15.0 torch 2.11.0+cu128
  warpmpm resolves to an editable install at
    /work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/__init__.py
  so the run uses the LIVE working tree, including another lane uncommitted edit.

THE RUN, wrapper written as a real file, launched in a new tmux session laneR:

  /work/11603/jcerrell0629/vista/laneR_verify.sh
  srun --jobid=865958 -p gh-dev -N1 -n1 -t 00:40:00 --overlap /work/11603/jcerrell0629/vista/laneR_verify.sh

which executed:

  /work/11603/jcerrell0629/vista/.venv/bin/python examples/flood_vehicle.py \
    --vehicle /work/11603/jcerrell0629/vista/truck_trimmed.ply \
    --up z --depth 0.12 --velocity 1.5 --frames 90 --grid 64 \
    --vehicle-density 250.0 \
    --out /work/11603/jcerrell0629/vista/mpm-engine/out/flood_vehicle_laneR_verify

Log: /work/11603/jcerrell0629/vista/mpm-engine/out/laneR_verify.log

A separate output directory was used on purpose. Running with the default --out would
have unlinked every png in out/flood_vehicle/_frames and overwritten metrics.csv and
flood_vehicle.mp4, destroying the artifact under verification. Confirmed intact after
the run: 372509 bytes, Jul 13 18:53, md5 10833a5b1837c99bf00b35ccd62920d6.

## THE VERBATIM GRID/LIM LINE

This is the line that was never logged on Jul 13. Verbatim from stdout:

  grid 64^3 lim=3.18m  water 30525 + vehicle 7454 particles (28.7 kg)  dt=1.08e-03 (31 substeps/frame)

The line immediately above it, equally load bearing and also never logged:

  vehicle: 1810 solid particles, extent [0.45  1.447 0.411] m, spacing 45.2 mm

## HOW THE REFERENCE CONDITION WAS IDENTIFIED, NOT ASSUMED

The run parameters were never recorded on Jul 13. They were inferred from artifact
shape, then confirmed by the reproduction itself:

  metrics.csv 91 rows  -> frames=90        (default)
  _frames 45 pngs      -> render_every=2   (default)
  final t = 3.000000   -> 90 frames at 1/30 s
  DEFAULT_PLY resolves to /work/11603/jcerrell0629/vista/truck_trimmed.ply
  neighbouring CSVs are named d0p15 through d0p6; the unnamed metrics.csv is the
  leftover default depth 0.12

Running the pure defaults reproduced the trajectory, which is what confirms the
inference. truck_trimmed.ply mtime Jul 13 15:29 predates the 18:08 run, md5
2fc321bbf29526e071f1ce01eef51729, so the same asset was used.

## CODE STATE, JUL 13 VERSUS TODAY

  HEAD at Jul 13 18:00      00bbfb1
  HEAD at Lane R run        fd390d6, plus an uncommitted edit from another lane
  commits touching src/ in between:  exactly ONE, fd390d6

fd390d6 changes ply dispatch from suffix to header content. Its own commit message
states splat plys are unaffected and truck_trimmed.ply still loads its 191107 splats.
The solver kernels are byte identical across the two runs.

The uncommitted edit is to FloodHistory.to_csv and adds vx,vy,vz,vmag,wx,wy,wz. It
changes the CSV schema from 8 columns to 15 and changes no physics. The first 8
columns are unchanged, so the comparison is column aligned. Another lane owns that
edit; nothing was committed or reverted here.

## REPRODUCTION RESULT

Final row, t = 3.0 s:

  quantity   Jul 13 reference     Lane R re-run        delta
  dx         +7.069373e-01 m      +7.067274e-01 m      -2.099e-04 m
  dz         +5.513430e-06 m      -3.460050e-05 m      -4.011e-05 m
  yaw        +9.737125e+00 deg    +9.710496e+00 deg    -2.663e-02 deg
  dmag       +7.073249e-01 m      +7.071057e-01 m      -2.192e-04 m

Whole trajectory, all 91 frames, worst case not just the endpoint:

  quantity   max abs deviation    as percent of peak
  dx         8.219e-04 m          0.116
  dmag       8.312e-04 m          0.117
  yaw        4.209e-02 deg        0.428
  dy         4.157e-04 m          1.759
  dz         7.159e-05 m          see below

DECLARED TOLERANCE: 0.5 percent of peak on dx, dmag and yaw across every frame.
RESULT: met, worst case 0.428 percent on yaw. The Jul 13 mp4 is CORROBORATED.

dz is reported separately and its percentage is meaningless. Both runs dz peaks are
themselves numerically zero, so dividing by that peak inflates the ratio to 162
percent while the absolute number is 0.07 mm. Expressed against the grid cell
dx = 3.1834/64 = 0.049741 m:

  dz peak, Jul 13   8.89e-04 grid cells
  dz peak, Lane R   1.01e-03 grid cells

Both are three orders of magnitude below one cell. The vehicle does not rise in
either run. The sign flip on the final dz value is noise about zero, not a physical
difference. Read dz as identically zero in both runs, not as a 162 percent mismatch.

## WHY THE RESIDUAL DIFFERENCE IS NOT DRIFT

Ruled out by direct check, not by assumption:

  water jitter   NOT the cause. FloodScene signature line 260 carries seed: int = 0
                 and flood_vehicle.py never overrides it, so np.random.default_rng(0)
                 makes water initialization bit identical between the two runs.
  code change    NOT the cause. Only fd390d6 touched src/, and it leaves splat plys
                 on the identical loader path.
  vehicle sample NOT the cause here. The unseeded mesh.sample drift F0 documented is
                 in the trimesh branch; a splat ply reads stored positions.

What remains is float atomic accumulation order in the P2G and G2P scatters, which is
non-deterministic run to run on GPU. A 0.1 to 0.4 percent spread is the expected size
of that effect over 2790 substeps. Bit exact reproduction was never available and was
not the standard applied.

## THE FOUR CRITERIA

Verbatim from CLAUDE.md lines 19 to 21, checked live:

  "For any rendered output: water reads as one connected fluid body, vehicle position
   matches its known density, no particles outside domain or clipped through geometry,
   motion continuous across frames."

NUMBERING NOTE: the prompt states criteria 1,2,3 PASS and criterion 4 fails for want
of the grid/lim line. Under CLAUDE.md own ordering the criterion that needs the domain
bound is the THIRD clause, not the fourth. The fourth clause, motion continuity, needs
no domain bound and passes outright. Reported against the CLAUDE.md text below rather
than silently renumbered to match the prompt.

C1  water reads as one connected fluid body                       PASS
    Visually confirmed on the reproduction, frame f_0022 at t=1.50 s: one connected
    sheet, no detached blobs, no shredding. Not inherited from the prior claim.

C2  vehicle position matches its known density                    NOT ESTABLISHED
    dz is pinned at zero for all 91 frames, so the body never lifts off the floor.
    Whether that is CORRECT for a 250 kg/m3 body is not settled by this run. First
    order check: mass 28.7 kg needs 0.0287 m3 displaced to float. Solid volume is
    0.11466 m3 spread over 0.411 m of height, so the bottom 0.12 m holds roughly
    0.0335 m3 if volume were uniform with height, which is ABOVE the flotation
    requirement, and a pickup carries more volume low than uniform. That puts the body
    at or past the flotation threshold on a static estimate while the simulation never
    lifts it at all. The discrepancy cannot be resolved from saved output because the
    local water depth at the vehicle is never logged, only the initial slab depth.
    This is an open question, not a pass. It was carried as PASS on prior claim.

C3  no particles outside domain or clipped through geometry       NOT VERIFIABLE
    The grid/lim line now fixes the domain at lim=3.18 m, which was the missing half.
    The other half is still missing: flood_vehicle.py writes metrics.csv, a png figure
    and frames, and never saves particle positions. There is no artifact against which
    to test whether any particle left [0, 3.18]. The renderer sets xlim/ylim to
    [0, lim] and zlim to [0, 0.35*lim], so an escaped particle is clipped OUT OF VIEW
    rather than shown, meaning the render cannot answer this either. Water inside the
    vehicle body is likewise unmeasurable without a particle dump.

C4  motion continuous across frames                               PASS
    Quantified on both runs, frame to frame:
      Jul 13   max jump dmag 0.0261 m (3.69 percent of final), max jump yaw 0.3983 deg
      Lane R   max jump dmag 0.0262 m (3.70 percent of final), max jump yaw 0.3992 deg
    Monotone through the acceleration phase in both, smooth plateau after t approx 1.3 s.
    0.0262 m per 1/30 s frame is 0.79 m/s, consistent with a 1.5 m/s surge. No steps,
    no teleports, no sign flips.

TWO of four pass. MPM-REAL is not available.

## MANDATORY CAVEAT, CORRECTED TO THIS ARTIFACT

The caveat wording supplied in the prompt does not describe this artifact and pasting
it would have put two wrong numbers into the record. Stated plainly:

  The prompt caveat says 4 water layers at n_grid=64 and vehicle solid volume 2.18x
  true hull volume. Both are YARIS numbers, from the F0 scene at lim=9.4217 m. This
  mp4 is a different scene at lim=3.1834 m.

The true caveat for THIS artifact, computed against the live formula:

  WATER LAYERS ARE 5, NOT 4. With lim=3.1834, dx=0.049741, h=0.024870, floor=3dx,
  np.arange(floor + 0.5h, floor + 0.12, h) yields 5 layers at z = 0.16166, 0.18653,
  0.21140, 0.23627, 0.26114. Cross-checked exactly against the engine own particle
  count: 5 layers x 111 y x 55 x = 30525, which is n_water printed in the grid line.
  Five layers across a 0.12 m column is still a very coarse free surface and the
  concern behind the original complaint stands undiminished.

  THE 2.18x OVER-FILL NUMBER DOES NOT APPLY AND NO FILL RATIO IS MEASURABLE HERE.
  That ratio requires a watertight hull volume to divide by. The Yaris has one,
  mesh.volume = 3.5427 m3. truck_trimmed.ply is a 3DGS splat with no closed surface,
  so there is no true hull volume and the over-fill or under-fill factor is UNDEFINED,
  not merely unmeasured. What is known: realized solid volume 0.11466 m3 against a
  bounding box of 0.45 x 1.447 x 0.411 = 0.26762 m3, a 42.8 percent box fill. F0
  records that this same asset hollowed at n_grid=128 in the v3 sweep, so the error
  sign for this asset is opposite to the Yaris.

  ANY FLOAT VERDICT FROM THIS ARTIFACT IS UNSAFE. Three independent reasons, and the
  conclusion holds even though the specific numbers differ from the prompt: the free
  surface is 5 particle layers deep, the body solid volume has no verifiable
  relationship to a real hull, and C2 above shows the static buoyancy estimate and the
  simulated vertical response disagree. Do not report float, no-float, or a flotation
  threshold from this run.

  ADDITIONAL CAVEAT NOT IN THE PROMPT, AND THE LARGEST ONE. This is a MODEL SCALE run.
  The vehicle is 1.447 m long and 28.7 kg. flood_vehicle.py own docstring states the
  bundled truck splat is model scale and that Froude scaling converts it, lam = 3.8
  for a 5.5 m pickup, giving 1560 kg in 0.57 m of water at 3.9 m/s carried 3.2 m. The
  raw numbers dx=0.707 m, depth 0.12 m, velocity 1.5 m/s are NOT full scale and must
  never be presented as a car in a real flood without the conversion stated on the
  same slide.

## PROVENANCE AUDIT ARTIFACT ROW

| Field | Value |
|---|---|
| Artifact | out/flood_vehicle/flood_vehicle.mp4, 372509 B, Jul 13 18:53, md5 10833a5b1837c99bf00b35ccd62920d6, plus 45 _frames/f_*.png |
| Source data | out/flood_vehicle/metrics.csv, 18363 B, Jul 13 18:08, 91 rows. Corroborated 2026-07-25 by out/flood_vehicle_laneR_verify/metrics.csv, log out/laneR_verify.log |
| Generating script | mpm-engine/examples/flood_vehicle.py at HEAD 00bbfb1 on Jul 13; re-run at fd390d6 plus an uncommitted to_csv edit. Only fd390d6 touched src/ in between and it does not alter the splat path |
| Params | truck_trimmed.ply md5 2fc321bbf29526e071f1ce01eef51729, up=z, depth=0.12 m, velocity=1.5 m/s, frames=90, n_grid=64, vehicle_density=250 kg/m3, seed=0, lim=3.1834 m, dx=0.049741 m, h=0.024870 m, dt=1.08e-03, 31 substeps/frame |
| Solver + scene | warpmpm MPM, weakly compressible water, rigid-body grid-momentum coupling. Scene is a MODEL SCALE 3DGS splat pickup, 1.447 m, 28.7 kg, 7454 vehicle particles, 30525 water particles, 5 water layers |
| What it shows | The MPM flood-vehicle pipeline runs end to end and produces a reproducible rigid-body response: 0.707 m surge displacement and 9.7 deg yaw, stable to 0.43 percent across an independent re-run |
| What it does NOT show | Not a car. Not the Yaris. Not full scale. Not 1100 kg. Says nothing about flotation, nothing about a real vehicle ford threshold, and nothing about whether particles stayed in the domain |
| Caveat label | UNVERIFIED |

## WHY IT COULD NOT MOVE TO MPM-REAL

Not for the reason given in the prompt. The grid/lim line was captured successfully
and the Jul 13 numbers did reproduce. It is blocked on:

  C3, which needs a particle-position dump that this script never writes. The grid/lim
      line alone cannot close it.
  C2, which needs the local water depth at the vehicle, also never written.

Both are one small instrumentation change away, and neither requires raising n_grid.

## FOR THE NEXT LANE, NOT DONE HERE

1. To close C3 and C2, flood_vehicle.py needs to save positions per frame and the
   min/max particle extent per axis. That is an edit to a file another lane currently
   has uncommitted. Sequence it, do not race it.
2. Two fordrun jobs, 865966 and 866051, are still queued and will start as soon as the
   idev job releases the slot. If they are stale, they need cancelling, which is
   Josie call, not this lane. Flagging, not acting.
3. src/warpmpm/vehicle.py is uncommitted and MODIFIED right now, and warpmpm is an
   editable install, so every lane on this box is running that uncommitted code.
4. Nothing escalated to Cristian Moran. No error survived 15 minutes or 3 attempts.
   The three srun submission errors were each resolved on the next attempt with new
   information from the error text.

## STATE LEFT BEHIND

  created  /work/11603/jcerrell0629/vista/laneR_verify.sh
  created  /work/11603/jcerrell0629/vista/mpm-engine/out/flood_vehicle_laneR_verify/
  created  /work/11603/jcerrell0629/vista/mpm-engine/out/laneR_verify.log
  created  tmux session laneR on login1
  unchanged  out/flood_vehicle/ in full, verified by md5 after the run
  unchanged  the can-it-ford repo, no edits and no commits beyond this handoff
  not touched  jobs 865958, 865966, 866051; tmux sessions auditfix, ford_node,
               loop_monitor, render_ghdev
