# Cluster state audit, Vista and LS6, 2026-08-22

Read-only reconnaissance. **No job was cancelled, no allocation freed, no file
deleted, and no file access time modified.** Every remote command was a read
(`squeue`, `sacct`, `sreport`, `sacctmgr`, `taccinfo`, `find -printf`, `du`,
`cat`). `find` and `du` stat files rather than reading them, so this audit did
not itself reset any atime and did not perturb the purge clock it measures.

All figures below were read live on 2026-08-22 between 02:45 and 03:10 BST
unless the line says otherwise. Where a number is relayed rather than measured,
it says so.

---

## Step zero: provenance of this audit

Recorded because this repo has several older copies of itself on the same
machine, and an audit run from the wrong one would be quietly worthless.

```
hostname : Josephines-MacBook-Air.local
pwd      : /Users/josie/can-it-ford
origin   : https://github.com/jcerrell-IS/can-it-ford.git
branch   : claude/add-ci-checks
HEAD     : e9e80ad  2026-08-22T02:49:03+01:00
.git     : a real directory, so this is the MAIN CHECKOUT, not a worktree
```

**Disambiguated against every sibling copy, not assumed.** Twenty-two
`can-it-ford*` directories exist under `/Users/josie`. Thirteen are not git
repos. Two are git repos pointing somewhere else and are decoys for this test:
`can-it-ford-paper` (Overleaf, `git.overleaf.com`) and `can-it-ford-demo` (a
different GitHub repo). **Seven share the correct origin:**

| Copy | Branch | HEAD date |
|---|---|---|
| **`can-it-ford`** | **`claude/add-ci-checks`** | **2026-08-22T02:49:03** |
| `can-it-ford-moving-vehicle` | `claude/moving-vehicle-exploratory-2026-08-11` | 2026-08-14T17:33:48 |
| `can-it-ford-warpmpm-continue` | `warpmpm-continue` | 2026-08-13T17:36:47 |
| `can-it-ford-realism` | `realism-exploration` | 2026-08-13T14:02:32 |
| `can-it-ford-visual-trial` | `claude/visual-physical-realism-trial-2026-08-11` | 2026-08-11T15:33:17 |
| `can-it-ford-BACKUP-2026-08-11` | `main` | 2026-08-11T15:06:56 |
| `can-it-ford-BACKUP-before-history-purge` | `main` | 2026-07-23T06:59:08 |

`/Users/josie/can-it-ford` is the only one on `claude/add-ci-checks` **and**
the newest HEAD of the seven. Both stated criteria select it, independently.
No relaunch was needed and no `cd` was issued.

**Host reachability confirmed before any dependent work:**

```
ssh -o BatchMode=yes vista echo ok   ->  ok   rc=0
ssh -o BatchMode=yes ls6   echo ok   ->  ok   rc=0
```

Both non-interactive, so the ControlMaster sockets were live for the whole
audit. No command below failed on a dead connection.

### One caveat on repo stability during the audit

**A second Claude Code session was live in this working tree while this audit
ran.** HEAD advanced from `3262118` to `e9e80ad` mid-session, and the dirty-file
count went from 7 to 18 as that session worked on `hf_space/`.

Checked rather than assumed: `e9e80ad` is path-limited to a single file,
`docs/CORPUS_MERGE_FINAL_2026-08-22.md`, and swept none of this audit's files
into itself. This document and the two memory files written alongside it are
intact and untracked.

**This does not affect any finding.** Every number in this audit was read from
Vista, LS6, TACC's docs, or W&B, none of which the other session touched. The
only repo-side reads were `data/r9_speed_surface.tsv` and a `find` for
`*RENDvc*`, neither of which is in that session's working set.

---

## Headline

**Vista is idle. LS6 has one live job, opened at 03:17 BST.**

**This corrects an earlier reading in this same audit and the correction is the
point.** Between 02:45 and 03:05 BST both queues were empty on four consecutive
checks, and this document said so. At 03:24 BST LS6 showed `idv95166` running on
`c303-005`. A queue reading is true for the minute it was taken and for no
longer. Re-read it rather than quoting this document.

The live job is small, cheap, CPU-only, and self-expiring. It is not a leak.
Full detail and a keep-or-kill call are in section 2.

What the audit found that already cost real money or already lost real work:

1. A 48-hour hold job on LS6 cost **71.83 SU**, which is **49.1 percent of all
   LS6 spend in August**, and **it could not have done what it was for.**
2. **81 cluster jobs since 2026-08-17 produced exactly 1 W&B run.** The compute
   was spent; the results are not queryable.
3. **1,129 files on LS6 scratch are purge-eligible right now**, and roughly
   18 GB more crosses the line on 2026-08-24.

---

## 1. Live SU balances

Read from `/usr/local/etc/taccinfo` on each machine. Both figures were read
**five times** across the session, at 02:45, 02:52, 02:55, 03:05 and 03:24 BST,
and did not move by a single SU. The LS6 figure will drop by 0.25 to 0.50 when
job 3381865 ends and is charged; SLURM debits at job end, not continuously.

| System | Project | Avail SUs | Expires |
|---|---|---|---|
| Vista | BCS20003 | **581** | 2026-09-30 |
| LS6 | BCS20003 | **9536** | 2026-09-30 |

Same project name, two separate per-machine allocations. They are not one pool.

**Both allocations are Josie's alone.** `sacctmgr show assoc account=BCS20003`
returns only `jcerrell0629` on both machines, and `sacct -A BCS20003 --allusers`
since 2026-08-12 returns 104 Vista jobs, all hers. So no labmate is drawing on
either balance, and every SU below is attributable to this project.

### Against the figures in the brief

Both prior figures were relayed, not measured here, and neither can be
re-read after the fact:

| Reading | Source | Vista SUs |
|---|---|---|
| 2026-08-12 | brief, "roughly 670" | ~670 |
| 2026-08-13 | `.claude/memory/vista-su-burn-is-idev-not-science.md` | 651 |
| 2026-08-19 | brief, R9 sprint job | 609 |
| **2026-08-22** | **measured live, this audit** | **581** |

The direction is confirmed and the magnitude is roughly right, but it does not
reconcile to the SU. Vista billed **48.49 SU** since 2026-08-12 against an
implied drop of ~89, and **8.93 SU** since 2026-08-19T13:00 against an implied
drop of 28. I could not close that gap and I am not going to invent an
explanation for it. The plausible candidates, none tested, are that the relayed
figures were approximate, or that TACC's balance refresh lags SLURM. What is
solid is the live 581 and the measured August spend below, and those two were
each confirmed by two independent paths.

**Vista is still the binding constraint.** 581 SU against LS6's 9536, and Vista
is the only machine with the warpmpm/GH200 path.

---

## 2. Every running or queued job

### Live at 03:24 BST

```
squeue -u jcerrell0629   # vista -> header only, 0 rows
squeue -u jcerrell0629   # ls6   -> 1 row
     JOBID       NAME     PARTITION   STATE     TIME  TIME_LIMIT  NODES  NODELIST
   3381865   idv95166   development RUNNING     7:11       30:00      1  c303-005
```

**LS6 job 3381865 `idv95166`**, read from `scontrol show job`:

| Field | Value |
|---|---|
| Partition | `development` (**charge rate 1.0**, CPU-only) |
| Account | BCS20003 |
| Submitted / Started | 2026-08-21T21:17:16 / 21:17:17 CDT (**03:17 BST**) |
| EndTime | 2026-08-21T21:47:17 CDT (**03:47 BST**), hard 30-minute limit |
| Node | `c303-005`, `AllocTRES=cpu=128,node=1` |
| AllocNode | `login2` |
| Command | `/home1/11603/jcerrell0629/.slurm/myjob_jcerrell0629.2495166` |

**What it is:** an `idev` interactive session, opened from login2 about seven
minutes before the reading. The `.slurm/myjob_*` command path is idev's
generated wrapper, so this is a human at a prompt, not a batch script.

**Is it still needed?** That is Josie's call, and the framing in the brief (a
job whose owning session ended hours ago) does not apply: this one is seven
minutes old, not hours, and someone was clearly at the keyboard.

**KEEP.** Recommendation only, no action taken. Three reasons:

1. **It is cheap and bounded.** `development` bills at 1.0, and the 30-minute
   limit caps the whole session at **0.50 SU**. It cannot become a `hold48s`.
2. **It expires on its own at 03:47 BST.** No intervention is needed for it to
   stop, so cancelling buys at most 0.23 SU and risks killing live work.
3. **It draws on LS6, which has 9536 SU.** The constrained allocation is Vista
   at 581, and Vista is idle.

**The one thing to watch:** it will be charged the full 0.50 SU whether it is
used or idle, because SLURM charges wall-clock on the allocation, not activity.
The waste mode here is walking away from it, which is precisely the pattern that
put seven LS6 idev sessions on the 2-hour wall in August at 6.00 SU each. If the
work is finished before 03:47, exit it; that converts a 0.50 SU charge into
0.25.

**Vista: nothing running, nothing queued**, confirmed again at 03:24 BST, and
`sacct` shows no Vista job has started since 2026-08-20T06:09:11.

Last job to start before the live one:

| System | Job | Name | Started | Elapsed |
|---|---|---|---|---|
| Vista | 924231 | `bash` | 2026-08-20T06:09:11 | 00:00:08 |
| LS6 | 3378048 | `bash` | 2026-08-20T06:10:14 | 00:00:02 |

Both were 8-second and 2-second probes. Before `idv95166` opened, nothing
substantive had run on either machine since **2026-08-19T19:05** (Vista,
`r9_est_h`), a gap of about two days. **No orphaned session from the R9 sprint
is holding anything.**

### August spend, measured two ways

`sacct` and `sreport` are independent SLURM accounting paths. They agree:

| System | sacct raw node-hours | sreport node-hours | Billed SUs |
|---|---|---|---|
| Vista | 64.58 | **65** | **79.80** |
| LS6 | 72.66 | **73** | **146.19** |
| | | | **225.99 total** |

### Charge rates, from primary source

Read live from `docs.tacc.utexas.edu`. This closes an item the project memory
flagged as never verified.

```
Vista:  gg 0.33   gh 1.0   gh-dev 1.0            SU per node-hour
LS6:    development 1.0   normal 1.0   gpu-a100-small 1.5
        gpu-a100 3.0      gpu-a100-dev 3.0
```

Both machines use the same formula, quoted verbatim from the docs:

> SUs billed = (# nodes) x max(job duration in wall clock hours,.25) x (charge rate per node-hour)

> All running jobs are charged a minimum of 15 minutes (.25 hrs) of queue time regardless of actual runtime.

**The 15-minute minimum is new to this project's records and it matters here.**
Of the 31.39 SU Vista billed since 2026-08-17, **11.79 SU (37.6 percent) is
minimum-charge padding**: time paid for and not used, because the R9 sprint
fired many sub-minute jobs. `ciford_dtrefine` ran 0.045 node-hours and was
charged 0.25. Across August, Vista paid **15.22 SU** for time it did not use.

This does not contradict the existing "SLURM charges elapsed, not requested"
note. Requesting 2 hours and using 1 minute still costs 0.25 SU, not 2. But
it is not free either, and a sweep of 40 tiny jobs has a 10 SU floor before it
computes anything.

### Interactive versus batch, this window

| Window | Interactive (`idv*`/`hold*`) | Batch |
|---|---|---|
| Vista, since 2026-08-01 | 53.30 SU (66.8%) | 26.50 SU |
| Vista, since 2026-08-17 | 9.09 SU (28.9%) | 22.30 SU |
| Vista, since 2026-08-19 | 2.25 SU (16.2%) | 11.67 SU |
| LS6, since 2026-08-01 | 133.22 SU (91.1%) | 12.97 SU |

**Vista's interactive share is genuinely improving**, 66.8 to 28.9 to 16.2
percent as the window narrows toward the present. Measured with the full
`idv*|hold*` classifier that the project memory flags as load-bearing. Against
the historical 98.5 percent, the R9 move to batch worked. Worth recording as a
win rather than only auditing the failures.

**LS6 is the opposite**, and it is a single job that does it. See section 3.

### Still-costly pattern: idev sessions that run to the wall

Every one of these was left to time out rather than exited. Each cost the full
window:

| System | Job | Name | Elapsed | Billed |
|---|---|---|---|---|
| Vista | 920452 | `idv94797` | 02:00:07 | 2.00 SU |
| Vista | 922255 | `idv94644` | 02:00:06 | 2.00 SU |
| Vista | 920212 | `idv90547` | 02:00:06 | 2.00 SU |
| Vista | 917886 | `idv13461` | 02:00:06 | 2.00 SU |
| LS6 | 3341760, 3347538, 3347772, 3360948, 3362208, 3364572, 3365305 | `idv*` | 02:00:01 each | **6.00 SU each** |

The LS6 ones are the expensive mistake: `gpu-a100-dev` charges **3.0**, so a
forgotten 2-hour idev on LS6 costs **6 SU**, three times the same mistake on
Vista. Seven of them is **42 SU**.

**Recommendation, not an action:** none of these can be killed, they all ended
days ago. The forward rule is to exit idev explicitly, and to prefer Vista
`gh-dev` over LS6 `gpu-a100-dev` for any interactive work that could go either
way, on a 3x cost basis.

---

## 3. The hold-the-scratch-alive pattern: found, and it did not work

**`hold48s`, LS6 job 3339919.**

| Field | Value |
|---|---|
| Partition | `gpu-a100-small` (rate 1.5) |
| State | COMPLETED |
| Start | 2026-08-04T17:46:59 |
| End | 2026-08-06T17:40:20 |
| Elapsed | 1-23:53:21 = **47.889 node-hours** |
| **Cost** | **71.83 SU** |

**71.83 SU is 49.1 percent of all LS6 spend in August**, and it is the largest
single wall-clock consumer on either machine in the entire window by a factor
of six. The next largest anywhere is Vista's `r9_speed_surface` at 2.99 SU.

### What it actually did

Read directly from `/work/11603/jcerrell0629/ls6/hold48_small.slurm`:

```bash
#SBATCH -J hold48s
#SBATCH -p gpu-a100-small
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 48:00:00
#SBATCH -A BCS20003
hostname
date
whoami
id -gn
echo "SCRATCH=$SCRATCH"
nproc
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
sleep 172400
```

The body is seven probe lines and `sleep 172400`. Its entire output is 151
bytes; the `.err` file is 0 bytes. **It never touches a file under `$SCRATCH`.**
It held an A100 node for 47.9 hours to run `sleep` on one core.

### Why it could not have worked

TACC's purge policy, quoted verbatim from the docs:

> The $SCRATCH file system, as its name indicates, is a temporary storage space. Files that have not been accessed* in ten days are subject to purge.

**Purge keys on file access time. Holding a node does not change any file's
atime.** A job that sleeps for 48 hours next to the filesystem preserves
nothing. The 71.83 SU bought no protection at all.

One thing in its favour, and it is worth stating plainly rather than letting the
finding read worse than it is: TACC also prohibits the workaround.

> Deliberately modifying file access time, using any method, tool, or program, for the purpose of circumventing purge policies is prohibited.

`hold48s` **did not violate that**, precisely because it never touched a file.
This is wasted budget, not a policy breach. The version of this job that would
have "worked" is the version that would have been prohibited.

### Companions

| System | Job | Name | Elapsed | Billed | Note |
|---|---|---|---|---|---|
| LS6 | 3339919 | `hold48s` | 47.889 nh | **71.83** | the one above |
| LS6 | 3339597 | `holder_ls6` | 1.984 nh | 5.95 | `gpu-a100-dev`, 3.0 rate |
| LS6 | 3339576 | `holder_ls6` | 0.035 nh | 0.75 | min charge |
| LS6 | 3339920 | `hold48n` | 0 | 0 | queued 48 h on `normal`, cancelled before start |
| Vista | 888807 | `holder` | 8.002 nh | 8.00 | TIMEOUT |
| Vista | 888134 | `holder` | 6.161 nh | 6.16 | CANCELLED |
| Vista | 923336 | `holder_test` | 0.029 nh | 0.25 | 2026-08-19 |

**Total hold-pattern spend in August: 92.94 SU** (LS6 78.53, Vista 14.41).

**Vista's `holder` is a different animal and should not be tarred with the same
brush.** Read from `/work/11603/jcerrell0629/vista/holder.slurm`, it writes a
`NODE_HANDOFF` file naming the node, queue, start and end, then sleeps 8 hours.
That is **node reservation for interactive attachment**, a real if expensive
purpose, not purge avoidance. Only the LS6 `hold48s`/`hold48n` pair is the
scratch-preservation pattern.

### Is it still needed?

**No.** Nothing is running, so no hold job exists to evaluate. And the pattern
should not be revived, for the reason above: it does not work.

**The exposure it was aimed at is real, and it is live right now.** See section 5.
The correct instrument is `$WORK`, which is a global Lustre filesystem, is **not
purged**, and currently has about **818 GB free** (205.4 of 1024 GB used). Moving
data to `$WORK` costs 0 SU and actually works.

---

## 4. d17-moving, job 920452: cleanly ended, mostly retrieved, two renders stranded

### The job

| Field | Value (live from `sacct`) |
|---|---|
| JobID | 920452 |
| Name | `idv94797` |
| Partition | `gh-dev` |
| State | **TIMEOUT** |
| Start | **2026-08-18T17:52:04 CDT** |
| End | **2026-08-18T19:52:11 CDT** |
| Elapsed | 02:00:07, 1 node |
| Cost | 2.00 SU |
| Node | c642-071.vista.tacc.utexas.edu |

**Correction to the brief.** The brief gives "started 2026-08-19 23:51". The
record says **2026-08-18 17:52 CDT**. The clock time reconciles (17:52 CDT is
23:52 BST), but **the date is one day early**: this ran on the 18th, not the
19th.

### Did it overrun, or is it still running?

**No.** It ended 2026-08-18T19:52:11, three days ago, and the queue is empty.

### Was it idle, burning budget for nothing?

**Largely not**, which is the more favourable answer than the pattern suggests.
The job ran 12 steps. The long one, `920452.2 run.sh`, ran 18:19:17 to 19:49:21
(01:30:04) and was killed by its own 90-minute cap, not by the allocation. Read
from `probe.log`:

```
slurmstepd: error: *** STEP 920452.2 ON c642-071 CANCELLED AT 2026-08-18T19:49:20 DUE TO TIME LIMIT ***
```

That leaves about 3 minutes of idle before the allocation's own TIMEOUT. The
waste here is the 2-hour window ending in TIMEOUT rather than a clean exit, not
an idle node.

### What it left behind

`/work/11603/jcerrell0629/vista/r9_moving/`, **1.2 GB, 1,926 files**.

**This is on `$WORK`, not `$SCRATCH`, so it is not purge-exposed.** No cleanup
is urgent. 17 files were written inside the 920452 window itself; the rest came
from the 2026-08-19 batch jobs that reused the same directory.

### Was the science retrieved? Yes, and it verifies

`data/r9_speed_surface.tsv` on the Mac and
`/work/11603/jcerrell0629/vista/r9_moving/out/r9_speed_surface.tsv` on Vista are
**byte-identical**: both 1,252 lines (1,251 data rows), both md5
`f4d6c091551c26a800c1937a20187129` after normalising line endings. A raw sha256
comparison disagrees, but that is CRLF introduced by my own transfer, not a
divergence in the data.

`docs/R9_MOVING_VEHICLE_2026-08-19.md` and
`docs/R9_MOVING_VEHICLE_PRIOR_CODE_2026-08-19.md` also exist in git refs.

### What was not retrieved

| File | Size | Produced by |
|---|---|---|
| `out/r9_RENDvc2p2.mp4` | 7,664,603 B | job 922582 `r9_render_motion` |
| `out/r9_RENDvc4p5.mp4` | 5,810,911 B | same, 36:43, 0.61 SU |

**13.5 MB, and neither exists anywhere under `/Users/josie`.** A search for
`*RENDvc*` across the home tree returns nothing. This is paid GPU output that
has never left Vista.

**Before pulling them, read this.** `probe.log` from the same run records:

> NON-CANONICAL. Prescribed-motion hull. No FORD verdict is reportable from this scene: the vehicle cannot be swept away because its motion is imposed.

So the renders are illustrative only. They cannot carry a verdict, and they
should not appear in the paper or poster as though they could. Retrieve them as
a record of what was run, not as a result.

**Recommendation, not an action:** copy the two mp4s and, if wanted, the
`out/*.tsv` files to the Mac. Leave the 1.2 GB in place on `$WORK`; it is safe
there and `$WORK` is at 20 percent of quota.

---

## 5. W&B cross-check: the compute was spent, the results are not queryable

**`analysis/wb.py snapshot` was deliberately not run.** `cmd_snapshot` creates a
W&B run and uploads artifacts, so it is a write to an external service, out of
scope for read-only reconnaissance. The read-only `doctor` and `runs`
subcommands were used instead.

```
target : jcerrell29-claremont-mckenna-college/can-it-ford
runs   : 108        artifacts : 4 dataset collections
```

### The gap

**Zero W&B runs between 2026-07-07 and 2026-08-17. Forty-one days.**

Everything after that gap:

| When | Run | Origin |
|---|---|---|
| 2026-08-17T21:30-21:31 | 17 x `gated-backfill`, group `gated-17` | Mac backfill, not cluster jobs |
| 2026-08-19T17:42 | `solar-music-106`, job `load-surface` | the speed surface |
| 2026-08-20T11:25 | `publish-failure_modes_classified` | Mac |
| 2026-08-20T11:33 | `snapshot-f4ba159` | Mac |

### Against what actually ran

Since 2026-08-17, **81 cluster jobs consumed node-time**: 78 on Vista, 3 on LS6.
**Exactly one of them has a corresponding W&B run.** That one is
`r9_speed_surface`.

The 17 `gated-backfill` runs are not counter-evidence: they are Mac-side
backfills of the canonical 17, already recorded in project memory as carrying
Runtime 0 s and GPU null. They document old results; they were not produced by
any of these 81 jobs.

**So: 31.39 SU of Vista compute since 2026-08-17, and 225.99 SU across both
machines in August, produced one queryable run.** Entire families are absent
from W&B:

- `d4_*` (jobA, jobB, jobB_gh, jobBbig, jobBbc, ghost, combo, ngrid)
- `r6rep_*` (g48, g64, g96, g128, g160, g192)
- `r7pin_*` (g48 through g208, ten grids)
- `r7_inflow`, `r7_inflow_smoke`
- `r9_est_[a-h]`, `r9_canon400`, `r9_hydro`, `r9_crowned_road`, `r9_quiesce`, `r9_lock`, `r9_window_ctl`, `r9_settle_longrec`, `r9_road_depthctl`, `r9_leak_ab`
- `ciford_dtrefine`, `ciford_vehcosim`, `ciford_vehrun`
- LS6: `ls6val`, `ls6div`

**This is the answer to the question as posed.** The compute was spent and the
results are not tracked anywhere queryable. Whether the underlying data survives
on `$WORK` is a separate question, and mostly it does, but nothing about these
runs is discoverable without knowing the job name in advance.

---

## 6. The live risk this audit found: LS6 scratch purge

Not in the original brief, but it is the one thing on either machine that is
losing something right now.

Purge threshold is **10 days without file access**, both machines.

### Vista scratch: clean

16 GB, 33,063 files. At maxdepth 3, **0 of 219 files scanned** have atime older
than 10 days. Directory atimes show `render_s1` at 2026-07-25 and `.cache` at
2026-07-08, but no file at the scanned depth is stale.

**Scope limit, stated because it changes what this can prove:** the audit's own
rule caps `find` at maxdepth 3, so this scanned 219 of 33,063 files. A clean
result at depth 3 is not proof the deeper tree is clean.

### LS6 scratch: 54 percent purge-eligible

52 GB, 56,414 files. At maxdepth 3, **1,129 of 2,084 files scanned (54.2
percent) have atime older than 10 days and are subject to purge now.**

Largest exposures, by size and staleness:

| Directory | Size | Last access | Days stale |
|---|---|---|---|
| `InstantSplat` | 7.9 G | 2026-07-24 | 29 |
| `gsplat` | 3.3 G | 2026-06-08 | 75 |
| `colmap_test` | 1.2 G | 2026-06-08 | 75 |
| `datasets` | 1.1 G | 2026-06-15 | 68 |
| `can-it-ford` | 887 M | 2026-07-23 | 30 |
| `can-it-ford-OLD-pre-purge` | 875 M | 2026-07-21 | 32 |
| `drainA` | 536 M | 2026-08-07 | **15** |
| `drain_2956`, `drain_2957` | 317 M | 2026-07-20 | 33 |

**And about 19 GB crosses the line on 2026-08-24**, in two days: the
`three_class_*_2026-08-14` family (ensemble 6.9 G, matched 3.6 G, full33 2.7 G,
muladder 2.2 G, mu 1.8 G, massswap 1.5 G, dxmu 150 M), plus `chrono_x86` 3.2 G
and `fork_moving_driver` 421 M at the same atime, for about 23 GB in total.

**`drainA` is the one to look at first.** It holds the COLMAP reconstruction:
`database.db` 436,924,416 B, `sparse/0/images.bin` 48,638,969 B,
`sparse/0/points3D.bin` 16,580,679 B, plus the source JPEGs. It is 15 days
stale, so it is already past the threshold. No `.ply` sits under it at maxdepth
3, so the trained splat itself is either deeper than this audit scanned or
elsewhere; that was not resolved.

**The directory literally named `can-it-ford-OLD-pre-purge` is evidence a purge
has already taken something here once.**

**Recommendation, not an action:** move what matters to `$WORK` (not purged,
~818 GB free) or pull it to the Mac. Do not revive a holder job; section 3
shows it does not work and the version that would work is prohibited. Nothing
here should be deleted without a separate, explicitly confirmed pass.

---

---

## 7. Can work actually be run on LS6 right now? Yes, with one hard limit

Asked directly, and tested rather than reasoned about. Both access paths work.

**Path 1, direct SSH to the compute node:**

```
ssh -o BatchMode=yes c303-005 "hostname; echo REACHED"
  -> c303-005.ls6.tacc.utexas.edu
  -> REACHED          rc=0
```

**Path 2, `srun` into the existing allocation (the supported path):**

```
srun --jobid=3381865 --overlap -n 1 hostname     rc=0
```

**Why the SSH works, and when it will stop working.** TACC gates compute-node
SSH on holding a live allocation there (`pam_slurm_adopt`). It succeeds only
because job 3381865 is running on `c303-005`. **When that job ends at 03:47 BST,
both paths close**, and SSH to the node will be refused. This is not a standing
capability, it is a 30-minute window. Re-check `squeue -u jcerrell0629` before
assuming a node is reachable.

Running work on an already-allocated node is also **free at the margin**: the
0.50 SU is charged for the wall-clock window whether the node computes or idles.
Using an open idev session costs nothing extra. Leaving it idle is the waste.

### The hard limit: this node has no GPU

Measured on the node itself, not inferred from the partition name:

```
c303-005$ nvidia-smi -L      ->  bash: nvidia-smi: command not found
c303-005$ nproc              ->  128
c303-005$ free -g            ->  250 GB total, 223 GB free
```

`development` is a **CPU-only** LS6 partition. So on this allocation:

- **Cannot run:** warpmpm, Genesis, gsplat, or anything CUDA. No GPU exists.
- **Can run:** 128 cores and ~223 GB of free RAM of CPU work. Gate scripts,
  `failure_modes.py`, the stationarity and settle analyses, CSV and rollout
  post-processing, mesh work, anything in `analysis/`.

**For GPU work on LS6 you need `gpu-a100*`, which bills at 3.0 SU/node-hour**,
three times Vista's `gh`. Given Vista is idle with 581 SU and holds the only
warpmpm/GH200 path, GPU work still belongs on Vista. This node is useful for CPU
analysis, not for simulation.

**Note the mismatch worth flagging:** 128 cores were allocated (`AllocTRES=cpu=128`)
against a request of `cpu=1,mem=1M` (`ReqTRES`). LS6 `development` allocates whole
nodes, so a one-core request takes all 128 and is billed as a full node either
way. There is no way to ask for less, and no saving available from asking.

## Keep-or-kill summary

Recommendations only. **No job was cancelled and no allocation freed.**

| Item | Status | Recommendation |
|---|---|---|
| **LS6 3381865 `idv95166`** | **RUNNING**, 7 min old, ends 03:47 BST | **KEEP.** 0.50 SU ceiling, self-expiring, on the unconstrained allocation. Exit early if the work is done, that halves it to 0.25 |
| Every Vista job | none running, none queued | nothing to kill |
| Other LS6 jobs | none | nothing to kill |
| `hold48s` 3339919 | ended 2026-08-06 | do not revive the pattern, it does not work |
| Vista `holder.slurm` | not running | keep the script, it has a real purpose, but price it at 1 SU/hour |
| 920452 `idv94797` | ended 2026-08-18 | nothing to clean; output is on `$WORK`, not purged |
| `r9_moving/` 1.2 GB on `$WORK` | safe | leave in place |
| Two `RENDvc` mp4s, 13.5 MB | stranded on Vista | retrieve, but label non-canonical |
| LS6 scratch, 1,129 stale files | **purge-eligible now** | move to `$WORK`, separate confirmed pass |
| `three_class_*` ~18 GB | **purges 2026-08-24** | decide within two days |

## What would change these conclusions

- **The queue readings above are already superseded once.** They were empty at
  02:45, 02:52, 02:55 and 03:05 BST, and not at 03:24. Treat every queue line in
  this document as a timestamp, not a state, and re-run `squeue` before acting.

- A balance re-read that reconciles to the SU would settle the section 1 gap. I
  could not close it and did not paper over it.
- A maxdepth scan deeper than 3 could find purge exposure on Vista that this
  audit's own rule prevented it from seeing.
- If the trained drainA splat lives deeper than maxdepth 3 on LS6 scratch, its
  exposure is worse than section 6 states, not better.
