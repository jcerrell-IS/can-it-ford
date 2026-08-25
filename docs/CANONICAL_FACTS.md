# Canonical facts, with the command that proves each one

Every number here was measured live on 2026-08-26 by running the command beside it. Nothing was
copied from a summary. If you are about to write one of these numbers into the README, the paper,
the poster, a Hugging Face card, a resume bullet or a W&B description, run the command first.

Tags used below: **[CONFIRMED]** re-run in this session, **[HOOK]** from the session-start live
check, **[UNVERIFIED]** stated but not re-measured here, and said so rather than implied.

---

## 1. The gated study

**17 gated MPM runs.** [CONFIRMED]

```bash
python3 -c "import csv;print(len(list(csv.DictReader(open('data/all_runs_inventory.csv')))))"
```
Returns `17`.

**3 grid levels x 3 masses, plus a depth sweep and a velocity sweep at n_grid 64.** [CONFIRMED]
Grids `{48, 64, 96}`, masses `{1100.0, 1609.0, 2337.0}` kg.

```bash
python3 -c "
import csv;r=list(csv.DictReader(open('data/all_runs_inventory.csv')))
print(sorted({x['n_grid'] for x in r}), sorted({x['mass_kg'] for x in r}))"
```

**Largest single run: 180,067 water particles.** [CONFIRMED] It is a three-way tie across
`g96_m1100`, `g96_m1609` and `g96_m2337`, which is expected: the water field does not depend on
vehicle mass.

**1,349,907 particles across the study, and say what that number contains.** [CONFIRMED]
It is water **plus** vehicle: 1,151,002 water and 198,905 vehicle. Quoting it as a water-particle
count overstates water by 17.3 percent.

```bash
python3 -c "
import csv;r=list(csv.DictReader(open('data/all_runs_inventory.csv')))
w=sum(int(x['n_water']) for x in r); v=sum(int(x['n_vehicle']) for x in r)
print('water',w,'vehicle',v,'total',w+v,'max single-run water',max(int(x['n_water']) for x in r))"
```

## 2. The solver, and the conflation to avoid

**The 17 gated runs use warpmpm, from `kks32/mpm-engine`, via
`renders/yaris_render_s1/sim_standing.py`.** [CONFIRMED, and it is already stated correctly in
`hf_space/app.py`]

**Genesis is the abandoned box-proxy path and the 9-condition SPH pilot only. No Genesis scene has
ever loaded the Yaris hull.** Never write "Genesis" and "the 17 runs" in the same sentence.

```bash
sed -n '10,12p' renders/yaris_render_s1/sim_standing.py    # imports warpmpm.core.solver
/usr/bin/grep -n 'warpmpm\|Genesis' hf_space/app.py | head
```

## 3. Verdicts, and the thresholds that produce them

**16 SLIDE, 1 STUCK.** [CONFIRMED]

```bash
python3 -c "
import csv,collections
print(collections.Counter(r['mode'] for r in csv.DictReader(open('data/failure_modes_by_run_classified.csv'))))"
```
Returns `Counter({'SLIDE': 16, 'STUCK': 1})`.

**Never quote that count bare.** It is threshold-dependent, and the thresholds are this project's
own, not published values:

| literal | value | unit |
|---|---|---|
| `slide_m` | 0.05 | metres |
| `slide_speed_ms` | 0.05 | **metres per second** |
| `float_m` | 0.05 | metres |
| `sustain_frames` | 3 | frames, and it has no source at all |

Three of those share one numeral across two units. A find-and-replace on "0.05" would silently
convert a speed into a distance and change the 16 of 17 published outcomes. **Deduplicate by name
and unit, never by value.**

```bash
sed -n '48,52p' simulation/failure_modes.py
```

## 4. The analytical sweep

**70 conditions. FORD counts 14 / 19 / 26 by AR&R class.** [CONFIRMED]

```bash
python3 -c "
import csv,collections
s=list(csv.DictReader(open('data/scenario_sweep.csv')))
print('rows',len(s))
for c in ['L1_verdict_small_passenger','L1_verdict_large_passenger','L1_verdict_large_4wd']:
    print(c, dict(collections.Counter(r[c] for r in s)))"
```
Returns 70 rows; small passenger 14 FORD, large passenger 19, large 4WD 26.

Use the 10-column live `scenario_sweep.csv`, never the 5-column snapshot.

## 5. Compute, and the number not to inflate

**Single node, single GPU, throughout.** [CONFIRMED] Every `.sbatch` in the repository carries
both `-N 1` and `-n 1`: **26 of 26**, scope excluding `.claude/worktrees/` and `third_party/`.

```bash
TOT=0; ONE=0
for f in $(find . -name '*.sbatch' -not -path '*/.claude/worktrees/*' -not -path '*/third_party/*'); do
  TOT=$((TOT+1))
  /usr/bin/grep -qE '^#SBATCH\s+-N\s*1\b' "$f" && /usr/bin/grep -qE '^#SBATCH\s+-n\s*1\b' "$f" && ONE=$((ONE+1))
done; echo "$ONE of $TOT"
```

**So the phrase "multi-node HPC" is false.** Hardware was NVIDIA GH200 on TACC Vista and A100 on
TACC Lonestar6.

**Do not present the August job count as successful runs.** [CONFIRMED, re-measured
2026-08-26] The figure carried in earlier write-ups was 201 jobs / 105 COMPLETED / 52.2 percent.
Live today it is **204 jobs, 108 COMPLETED, 52.9 percent**:

| host | jobs | COMPLETED | CANCELLED | TIMEOUT | FAILED |
|---|---|---|---|---|---|
| Vista | 157 | 92 | 31 | 30 | 4 |
| LS6 | 47 | 16 | 14 | 15 | 2 |
| **total** | **204** | **108** | 45 | 45 | 6 |

The counts moved, the lesson did not: **about half of all submitted jobs completed.** Re-measure
rather than quoting 204 or 201:

```bash
scripts/tacc.sh vista 'sacct -S 2026-08-01 -E now -X --format=JobID,State -P'
scripts/tacc.sh ls6   'sacct -S 2026-08-01 -E now -X --format=JobID,State -P'
```

**A collision to watch.** The number of COMPLETED August jobs (108) and the number of W&B runs
(108) are equal by coincidence. They count different things and are not each other's evidence.

## 6. Weights and Biases

**108 runs in four labelled cohorts** (70 L0/L1, 9 Genesis pilot, 17 gated warpmpm, 9 early
untagged, 3 admin). [HOOK, session-start live check, 2026-08-26]

**`has_history` is false, so there are no training curves.** The 17 gated runs are Mac backfills:
Runtime 0 s and GPU null. The dashboard number reflects the backfill script, not the simulation.
**108 is a run count across four cohorts, not 108 simulations.**

## 7. The reconstruction front end, stated the same way everywhere

**The reconstruct-to-decide front end is DESIGNED AND NOT BUILT. No gsplat reconstruction has ever
entered a simulation.** The splat pipeline was trained and validated in isolation.

Measured live on LS6, 2026-08-26:

| metric | value |
|---|---|
| PSNR | 22.735628 |
| SSIM | 0.824878 |
| LPIPS (alex) | 0.311224 |
| Gaussians | **1,147,694** across 3 rank shards |

**The Gaussian-count trap.** `stats/val_step29999.json` reports `num_GS: 399491`. That is rank 0's
shard alone. The total is only recoverable by summing the three `train_step29999_rank*.json`
files: 399,491 + 374,677 + 373,526 = 1,147,694. Reading the val file by itself understates the
model by 2.87x.

```bash
scripts/tacc.sh ls6 'cd /scratch/11603/jcerrell0629/gsplat/examples/results/drainA
  cat stats/val_step29999.json
  for r in 0 1 2; do cat stats/train_step29999_rank$r.json; echo; done'
```

The poster already states this correctly, under Scope: "OPEN No reconstructed scene has entered a
simulation." Use those words.

## 8. Phrases that are false, and what to say instead

| do not write | why | write instead |
|---|---|---|
| "multi-node HPC" | every job is `-N 1 -n 1`, 26 of 26 | "single-GPU jobs on GH200 and A100" |
| "end-to-end video-to-verdict" | no splat has entered a simulation | "a reconstruction stage and a simulation stage, not yet connected" |
| "108 simulations" | 108 is a run count across four cohorts, with no history | "108 W&B runs across four cohorts" |
| "204 runs" | only 108 of 204 August jobs COMPLETED | "204 jobs submitted, 108 completed" |
| "85,000 lines of code" | inflated by ~15,500 lines of duplicated generated Plotly HTML | "61,889 lines of Python across 242 tracked files" [UNVERIFIED here] |
| "the 17 Genesis runs" | the 17 are warpmpm | "the 17 gated warpmpm runs" |
| "1.35 M water particles" | that total includes vehicle particles | "1,151,002 water particles, 1,349,907 including the vehicle" |

## 9. Where this file is not the authority

`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` outranks this file on anything it covers.
This file exists to put the handful of numbers that reach a public surface in one place with their
commands attached. It does not replace the register, and it is not a physics reference.
