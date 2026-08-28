# D13 -> D11: one LS6 launch, the x86 GetNormal reproduction

D13 is barred from LS6 under the 23:14 serialization rule. This is the whole
request: **one script, one launch, one poll.** Everything else is already staged
on LS6 from D13's earlier session.

## What this decides

Chrono's `RigidTerrain::GetNormal` returns a wrong normal when a ray lands exactly
on a mesh **vertex**. Measured on Vista aarch64, 10,800 samples:

| class | samples | bad | rate | worst angle |
|---|---|---|---|---|
| ON-VERTEX (both coords on a grid line) | 3600 | 3600 | **100.0%** | **88.85 deg** |
| ON-EDGE (one coord on a grid line) | 3600 | 0 | 0.0% | 1.02 deg |
| INTERIOR (neither) | 3600 | 0 | 0.0% | 1.09 deg |

If x86 shows the same 100 / 0 / 0 split, it is a **general Chrono/Bullet defect**
and should go upstream. If x86 is clean, it is **aarch64-specific** and D13's GO
verdict ships with an architecture caveat. Either answer closes the question.

The build is controlled to isolate the ISA: **same Chrono SHA
`1b90a9f9854575f1ce1287d359d957b0273c075f`, same gcc 13.2.0, same cmake 4.1.1,
same Eigen 3.4.0** as the Vista build. Only the architecture differs.

## THE BUILD IS ALREADY DONE. This is now a ~1 minute job.

A D13 build launched before the serialization rule completed successfully on
c301-002 at 16:13. Captured output, verbatim:

    node c301-002.ls6.tacc.utexas.edu  arch x86_64
    g++   (GCC) 13.2.0        cmake 4.1.1
    chrono HEAD: 1b90a9f9854575f1ce1287d359d957b0273c075f
    CONFIGURE RC=0            BUILD RC=0
    libChrono_core.so  libChrono_vehicle.so  libChrono_vehicle_cosim.so

So `Chrono_core` and `Chrono_vehicle` already exist on x86_64 at
`/work/11603/jcerrell0629/ls6/chrono_x86_build/lib/`. The script below **detects
this and skips straight to the measurement**: generate mesh, compile one file,
run. Roughly one minute, not ten.

    /scratch/11603/jcerrell0629/chrono_x86_2026-08-14/chrono   source, exact SHA
    /work/11603/jcerrell0629/ls6/chrono_x86_build              BUILT, do not rebuild
    /scratch/11603/jcerrell0629/make_obj_portable.py           mesh generator

**Do not re-clone and do not delete the build directory.**

## Two traps D13 already paid for

1. The build directory must NOT be on LS6 `$SCRATCH`. CMake's `file(COPY)` fails
   there with "cannot set modification time" while copying Chrono's `data/`.
   The script below puts it on `$WORK`, which works.
2. `nohup` alone does not survive; use the `setsid ... < /dev/null & disown` form.

## Step 1, copy the script

    scp /Users/josie/can-it-ford/.claude/dispatch_prompts/d13_x86_normal_test.sh \
        ls6:/scratch/11603/jcerrell0629/

## Step 2, launch it, durable form

    TACC_TIMEOUT=600 /Users/josie/can-it-ford/scripts/tacc.sh ls6 \
      "cd /scratch/11603/jcerrell0629 && setsid nohup srun --jobid=3365305 --overlap \
       -p gpu-a100-dev -t 00:40:00 -N1 -n1 bash /scratch/11603/jcerrell0629/d13_x86_normal_test.sh \
       < /dev/null > /scratch/11603/jcerrell0629/d13_x86.log 2>&1 & disown; sleep 2; echo LAUNCHED"

**CPU only. It sets no CUDA and touches no GPU**, so it will not contend with any
A100 work. Build is roughly 5 to 10 minutes on 16 cores.

## Step 3, poll, one short call

    TACC_TIMEOUT=90 /Users/josie/can-it-ford/scripts/tacc.sh ls6 \
      "tail -20 /scratch/11603/jcerrell0629/d13_x86.log"

## What to send back

The block under `=== RESULT TABLE ===`, verbatim. That is the entire deliverable.
If the build fails instead, the last 20 lines of the log are equally useful and
D13 will report it as "cannot be determined" with the blocking step named.
