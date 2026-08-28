# LIVE NODES AND THE GPU WORK THAT GOES ON THEM, 2026-08-14 22:50 CEST

Verified live by `squeue -u jcerrell0629` on both machines at 22:49. Do not
re-derive, do not guess, and do not submit a fresh sbatch: it will queue behind
these and never start.

    VISTA   job 912094   node c642-012   gh-dev         2:00:00, started 22:47
            1x GH200 120GB (97871 MiB), aarch64
    LS6     job 3365305  node c301-002   gpu-a100-dev   2:00:00, started 22:46
            3x A100-PCIE-40GB, x86_64 (confirmed live: uname -m = x86_64)

Both expire around **00:47 CEST**. Roughly 115 minutes of wall clock remain.

## How to get work onto them

The allocations already exist, so `srun --jobid=` is the only way in. A fresh
`sbatch` or `idev` will block: you already have a PENDING job on each machine
hitting `QOSMaxJobsPerUserLimit` and `Priority`.

    /Users/josie/can-it-ford/scripts/tacc.sh vista "srun --jobid=912094 -p gh-dev -t 00:30:00 -N1 -n1 <cmd>"
    /Users/josie/can-it-ford/scripts/tacc.sh ls6   "srun --jobid=3365305 -p gpu-a100-dev -t 00:30:00 -N1 -n1 <cmd>"

TRAP, already cost us once: the TACC submit filter rejects `srun` without
**both** `-p` and `-t`, even though the allocation exists. "srun: fatal: No
command given to execute" means you passed no command after the flags.

TRAP 2: `tacc.sh` defaults to `TACC_TIMEOUT=60`, which kills long probes. Export
`TACC_TIMEOUT=600` for anything that runs more than a minute.

## THE HARD CONSTRAINT THAT DECIDES WHICH MACHINE

Verified live earlier today, not recalled:

    VISTA  /work/11603/jcerrell0629/vista/can-it-ford/mpm-engine/.venv/bin/python
           warp 1.15.0   set_sdf_pose TRUE   sdf_wrench TRUE   no trimesh
    LS6    /scratch/11603/jcerrell0629/warpmpm_ls6_env/bin/python
           warp 1.12.1   set_sdf_pose FALSE  sdf_wrench FALSE
           needs PYTHONPATH=/scratch/11603/jcerrell0629/instantsplat_probe_2026-08-13
           code lives in $SCRATCH, not $WORK

**LS6's warpmpm has no moving-SDF API.** Any moving-vehicle run must go to
Vista. Any stationary run can go to either, and LS6 has three times the GPUs.

Vista `/home1` is 89.15 percent full. Do not pip install into it. Build under
`/work` (5.49 percent used).

## TWO PENDING JOBS THAT NEED A DECISION FROM THEIR OWNERS

    VISTA  912095  "normcheck"  PENDING (QOSMaxJobsPerUserLimit)   D13
    LS6    3364660 "d9_yaris"   PENDING (Priority), 3:00:00        D9

`912095` is blocked by your own idev holding the one-job-per-user slot. It will
not start while the idev lives. Run its work through `srun --jobid=912094`
instead.

`3364660` requests 3:00:00 on `gpu-a100` and is queued on Priority. It will
almost certainly not start before the idev expires. **If it is a moving-vehicle
run it will fail on LS6 regardless**, because `set_sdf_pose` is False there.
D9: verify which it is before spending anything on it.

## MAXIMISING LS6: THREE GPUs, RUN THREE THINGS AT ONCE

One `srun` gives you the whole node. Pin three workloads to three GPUs inside
it rather than running them one after another:

    srun --jobid=3365305 -p gpu-a100-dev -t 00:45:00 -N1 -n1 bash -c '
      CUDA_VISIBLE_DEVICES=0 <cmd_a> > a.log 2>&1 &
      CUDA_VISIBLE_DEVICES=1 <cmd_b> > b.log 2>&1 &
      CUDA_VISIBLE_DEVICES=2 <cmd_c> > c.log 2>&1 &
      wait'

Confirm you actually got three with `nvidia-smi --query-gpu=index,name,memory.used
--format=csv` inside the allocation. Earlier today all three read 0 percent and
0 MiB, which is the signature of a node sitting idle while work queued elsewhere.

## THE RESEARCH THAT TURNS INTO GPU RUNS

Read live at 22:50 from the reports on this machine. Paths given so you can
check me rather than take my word.

`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/`
  `01_Solver_Physics_and_Coupling/2026-08-14_undermind-report_multi-resolution-mpm-large-domain-flooding_CURRENT.md`
  `01_Solver_Physics_and_Coupling/2026-08-14_undermind-report_settling-and-force-reporting-free-surface_CURRENT.md`
  `01_Solver_Physics_and_Coupling/2026-08-14_undermind-report_quantitative-mpm-wall-penetration_CURRENT.md`
  `04_Validation_Literature_and_Citations/2026-08-14_undermind-report_moving-rigid-body-free-surface-validation_CURRENT.md`
  `04_Validation_Literature_and_Citations/UNDERMIND_FINDINGS_DEPLOYMENT_ORDER_2026-08-08.md`
  `09_Claude_and_AI_Tooling_HowTo/2026-08-08_undermind-report_trustworthy-ai-assisted-scientific-simulation_CURRENT.md`
Plus 63 Claude compass artifacts at `/Users/josie/Claude/reu/`.

### R1. Fixed particles-per-cell loses convergence under refinement. TESTABLE TONIGHT.

Multi-resolution report, ranked evidence, item [4], quoted: "fixed
particles-per-cell can lose convergence under grid refinement. Methods must
co-refine/control PPC; otherwise AMR silently changes quadrature and transfer
conditioning."

This project runs **fixed PPC = 8**. That is the named mechanism for D9's
non-monotone Yaris (gate error 63.3, 37.1, 52.3, improving then worsening) and
for D12's finding that dx is fully confounded with dt, substeps, h and particle
count.

The falsifiable test: **re-run the Yaris ladder with PPC co-refined instead of
held at 8.** If the non-monotonicity flattens, the mechanism is confirmed and
CLAUDE.md item 5's non-monotone grid study gets a cause. If it persists, the
mechanism is refuted for this scene, which is equally worth having. This is a
no-forcing control, not a plausible claim.

The same report also says standard MPM, GIMP, CPDI and B-spline MPM cannot be
treated interchangeably, and that nonuniform grids already produce projection
error. Record which basis this engine uses before quoting any of it.

### R2. Independent-start ensembles beat repeat counts. RUNS ON THREE GPUs AT ONCE.

Settling report, numerical reproducibility section, quoted: "Repeated runs
should report outcome spread and gate-pass frequency; no universal repeat count
exists, while independent-start ensembles are the stronger convergence check."

Same section: "Non-associative, order-dependent reductions can produce small
drift or alter discrete gates; fixed-order/sorted or reproducible reductions and
higher-precision accumulation mitigate this."

That second sentence is a direct hit on this project: a discrete SLIDE / STUCK /
FLOAT gate is exactly the kind of gate a reduction-order drift can flip. Three
independent starts on three A100s, one srun, reporting outcome spread and
gate-pass frequency, is the strongest single use of the LS6 slot tonight.

### R3. There is no settling threshold to look up. Only a protocol.

Settling report headline, quoted: "No universal frame count or force-settling
threshold emerges: the defensible protocol is to detect and exclude
initial/final transients, demonstrate stationarity for the reported observable,
and attach uncertainty based on correlated samples."

Named methods: autocorrelation and integrated correlation time, blocking,
bootstrap, confidence intervals, to convert a stationary record into an
effective sample size. Also: report a prespecified constant-speed interior
window, its mean, and its filter and window sensitivity.

Stop looking for a threshold. Implement the protocol.

### R4. The wall-penetration plateau has NO literature anchor. It must be measured.

Wall-penetration report, quoted: "the supplied records contain no paper that
explicitly demonstrates the requested ~0.93-1.01-grid-spacing penetration
plateau" and "No retrieved record reports calibration/subtraction of a smeared
wall layer, an accepted correction protocol, or a defensible minimum number of
cells across shallow water."

So 0.321 against 0.702 against 0.93 cannot be settled by citation. Only a
held-fixed comparison settles it. That is the clamp-disabled run, and it is now
the only route.

### R5. Validation targets that exist, with numbers.

Moving-rigid-body report, quoted: "[6] proposes total-head criteria of 0.3 m for
passenger cars and 0.6 m for emergency vehicles. **Still-water depth limits must
not be conflated with depth-velocity products.**" And: "[9] reports simulated
critical depth 0.38 m and minimum depth x velocity 0.39 m2/s against prior
experiments." And: "[20] provides an unusually precise public benchmark, with
approximately 0.3 percent experimental uncertainty."

Also stated plainly: "no validated vehicle-fording MPM chain is identified", and
"The supplied records do not establish an experimental basis for the 1.5 m/s
rule". Both belong in the limitations section as citable, not asserted.

[20] at 0.3 percent experimental uncertainty is the locked free-surface
regression case the deployment order asks for in Phase 1. Identify it and use it.

### R6. The vehicle-class geometry gap, and the fact that D5 has already closed it.

`UNDERMIND_FINDINGS_DEPLOYMENT_ORDER_2026-08-08.md` Phase 0, quoted: all 17
gated runs "represent all three AR&R mass classes (1100 / 1609 / 2337 kg) using
one hull, the Yaris, with mass relabeled only", and buoyancy, drag and lift
lever arms, wheel normal loads, and sliding/float/roll thresholds "depend
jointly on displaced volume, underbody shape, wheelbase and track, and center of
mass, not on mass alone".

It offers Path A (wire a `--vehicle` flag, run real Rogue and Silverado hulls,
report genuinely class-specific results) or Path B (an explicit limitations
sentence). **D5 has executed Path A.** The three-class matched-dx set uses real
Rogue and Silverado hulls at a common dx. That is the strongest single result
this project has and nobody has connected it to the gap it closes.

Secondary citation from the same file, needing a check before use: Allen, Klyde,
Rosenthal and Smith 2003, SAE 2003-01-0966, regressions for CoG height and
yaw/roll inertia. It warns this is a **different** paper from the SAE
1999-01-1336 already in project files, and that the two must be confirmed
distinct before either is cited as settled.

### R7. Phase 1 metamorphic tests. None exist. All three are GPU runs.

From the deployment order, Phase 1, quoted as "none currently exist as automated
checks":

  - same scene at 2x grid resolution
  - **same scene mirrored left-right, must give a mirror-symmetric result**
  - same scene with vehicle mass held fixed but density varied inversely with
    volume, must be invariant

The mirror test is the cheapest falsifiable control available and it has never
been run. An asymmetric result on a symmetric scene is a defect, full stop, with
no interpretation needed.

Also flagged there and cheap: does `summary.json` record the git SHA of
`sim_standing.py` **at the moment the run executed**, not at commit time? The
deployment order calls this "the single cheapest provenance win available, one
field."

### R8. Citations for limitations already known to be true.

Roache 1994 (Grid Convergence Index) and Celik, Ghia, Roache and Freitas 2007
for how a resolution study should be reported: this project reports
verdict-invariance, not a formal GCI number, and the gap should be stated.
Bai and Schroeder 2022 and Sun, Shinar and Schroeder 2020 derive the
sound-speed-to-CFL relationship formally, which is the anchor for the
sound-speed sweep result. Steffen, Kirby and Berzins remains the correct anchor
for grid-crossing error and is the most-cited MPM numerics paper across all four
reports.

## STANDING, UNCHANGED

Batch or srun into an existing allocation, never a new idev. Stage explicit
paths, max 8 files per commit, hold every push pending Josie's per-branch check.
E8: no derived hull geometry and no rendered artifact reaches the public repo.
Anything you cannot verify, mark UNREVIEWED rather than faking the review.
