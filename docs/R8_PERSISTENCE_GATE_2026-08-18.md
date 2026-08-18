# The SLIDE gate reads one channel and the frequency reporter reads another

Slot d2-persist, branch `claude/r8-persistence`, 2026-08-18. Closes ledger item 9
(`docs/HANDOFF_ROUND_7_2026-08-18.md:616`, "Remove persistence from the verdict /
report frequency").

Everything here is reproduced by one command, which reads only and writes nothing:

```
/usr/bin/python3 analysis/r8_persistence_frequency.py --markdown
```

It defaults to `--repo /Users/josie/can-it-ford`, the main checkout, because
`metrics.csv` files are gitignored build artifacts and only 1 of the 37 is
physically present inside a worktree. The root it used is printed on every run.
Pure standard library, no numpy, no uv.

**Every verdict count below is quoted with all four constants that produce it:
`slide_m = 0.05 m`, `slide_speed_ms = 0.05 m/s`, `sustain_frames = 3`. The first
two are cited thresholds by unit; the third is the unsourced one this item is
about, and it is kept beside the counts so a count cannot be lifted away from it.**

---

## 1. The headline: the committed frequency reads a different quantity from the classifier

`simulation/failure_modes.py` gates SLIDE on the SURGE COMPONENT:

| what | where | reads |
|---|---|---|
| axis selector | `failure_modes.py:18` | `SURGE_AXIS = 0` |
| drift channel | `failure_modes.py:168` | `np.abs(kin.disp[:, SURGE_AXIS])`, that is `\|dx\|` |
| speed channel | `failure_modes.py:170` | `np.abs(kin.vel[:, SURGE_AXIS])`, that is `\|vx\|` |
| joint mask | `failure_modes.py:181-183` | comparator `>=` |
| drive guard | `failure_modes.py:178`, used `:195` | `driven_downstream = max(\|surge_force\|) > 0` |

`analysis/probabilistic_verdict.py` gates its `p_move` on the 3D MAGNITUDES:

| what | where | reads |
|---|---|---|
| column guard | `probabilistic_verdict.py:244` | `if "dmag" not in cols or "vmag" not in cols` |
| call site | `probabilistic_verdict.py:247` | `assess(cols["dmag"], cols["vmag"], ...)` |
| joint mask | `probabilistic_verdict.py:146` | comparator `>`, not `>=` |

`dmag` and `vmag` are the Euclidean norms of `(dx,dy,dz)` and `(vx,vy,vz)`. Since
`dmag >= |dx|` and `vmag >= |vx|` elementwise and the joint mask is monotone
increasing in each channel, the surge mask implies the magnitude mask frame by
frame, so

> p_move(magnitude channel) >= p_move(surge channel), for every run, always.

That is an identity, not a result, so the script checks it on every run as a
self-test rather than reporting it as a finding. It **HOLDS on 36 of 36** runs.

The consequence: **every `p_move` this project has published is an upper bound on
the classifier's own gate.**

### 1.1 A claim of mine that was wrong, withdrawn

In my scope confirmation I wrote that nobody had recorded this. **That is false and
I withdraw it.** `docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md:94-95` records it,
correctly and in the right place:

> "Values are not identical because this reads `vmag` where the classifier reads a
> component; treat as corroboration, not reproduction."

What had not happened is that it was never **quantified**, and the caveat did not
**propagate**. Two live sites carry the consequence without it:

- `CLAUDE.md:783-784` restates the derived numbers and says `g96_m2337` "returns
  margin_frames 1, **independently** matching register J15". Same input file, and
  in fact a different channel from the one J15 was computed on.
- `analysis/settle_audit.py:34` asserts the opposite of the truth outright:
  `# Observables worth testing. dmag and vmag are what the verdicts read.`
  The verdicts read `dx` and `vx`. (Its `OBSERVABLES` list at `:35` does include
  `vx`, so the script is less wrong than its comment.)

So the finding is not "undiscovered defect". It is "recorded once as a qualitative
caveat, never measured, and dropped everywhere downstream".

---

## 2. How large the gap is

36 of 37 local runs are classifiable. Full per-run table in section 7 (Table 1).

| statistic | value |
|---|---|
| gap `p_A - p_B`, minimum | 0.00 pp |
| gap, median | 1.10 pp |
| gap, **maximum** | **29.67 pp** |
| gap, mean | 3.54 pp |
| ratio A/B, finite cases (n=32) | min 1.000, median 1.056, **max 14.000** |
| runs where the surge channel NEVER passes but the magnitude channel does | **2** |
| runs where neither channel ever passes (ratio is 0/0, not infinite) | 2 |

The two runs where the magnitude channel manufactures a pass from nothing are
`yaris_L2_d0p30_v1p5` (29.67 percent against 0.00 percent) and, more seriously,
**`sweepV_g64_v0p5`, the single canonical STUCK run** (1.10 percent against 0.00
percent).

### 2.1 The mechanism is the speed channel, and it is vertical bobbing

Of the 116 frames counted by the magnitude gate but not by the surge gate, summed
over all 36 runs:

| the surge channel fails because | frames | share |
|---|---|---|
| surge SPEED is under `slide_speed_ms` while drift clears `slide_m` | **114** | **98.3%** |
| surge DRIFT is under `slide_m` while speed clears `slide_speed_ms` | 1 | 0.9% |
| both surge channels under their own named threshold | 1 | 0.9% |

In **4 of 36** runs `max|vz|` exceeds `max|vx|`. Verified by direct column read on
`renders/yaris_render_s1/m1100/metrics.csv`: `max|vx| = 0.0699 m/s` against
`max|vz| = 0.0791 m/s`. In those runs `vmag` is carried over `slide_speed_ms` by
motion that is not downstream at all.

**Plainly: the committed `p_move` scores vertical bobbing as sliding.** That is a
wrong physical attribution, not merely a loose bound.

### 2.2 The comparator is not the cause

Holding the channel fixed at `|dx|`,`|vx|` and changing only `>` to `>=`:

> max `|p_C - p_B|` over 36 runs = **0.000e+00 percentage points**.

So the entire gap is the channel. The `>` at `probabilistic_verdict.py:146` is a
genuine second disagreement with `failure_modes.py:182` and should still be fixed,
but on this data it moves nothing, because a float landing exactly on a threshold
is measure zero.

### 2.3 The falsifiable test that says which channel is right

Register `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:627` publishes, from
`analysis/slide_verdict_fragility.py` (which reads `dx`/`vx`, per its own
docstring), the m2337 longest-run series across g48/g64/g96 as **11 -> 10 -> 4**.

| channel | m2337 series, g48 -> g64 -> g96 | matches the register |
|---|---|---|
| committed `dmag`,`vmag` | 22 -> 11 -> 4 | **no** |
| corrected `\|dx\|`,`\|vx\|` | **11 -> 10 -> 4** | **yes, exactly** |

`docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md:93-94` reported the committed
series as margins "g48 19, g64 8, g96 1" and called it "qualitatively matching"
J15. Those margins are exactly `22-3`, `11-3`, `4-3`. **The mismatch that was
accepted as unavoidable disappears when the channel is corrected.** This is an
external check: the register's series predates this work and was computed by a
different script.

---

## 3. What changes, and what does not

Every count below carries `slide_m = 0.05 m`, `slide_speed_ms = 0.05 m/s`,
`sustain_frames = 3`.

### 3.1 What does NOT change

- **The published 16 SLIDE / 1 STUCK is untouched**, at `slide_m = 0.05 m`,
  `slide_speed_ms = 0.05 m/s`, `sustain_frames = 3`. Reproducing
  `failure_modes.py` exactly (surge channel, `>=`, plus `driven_downstream`) on
  the 17 canonical runs gives **16 SLIDE / 1 STUCK, STUCK = `sweepV_g64_v0p5`**,
  matching `data/failure_modes_by_run_classified.csv` on **17 of 17 verdicts and
  17 of 17 `onset_frame_slide` values**. The canonical verdicts were never
  affected, because `failure_modes.py` always read the correct channel.
- `g96_m2337` margin: longest run 4, margin 1 over `sustain_frames = 3`, on BOTH
  channels. Register line 627 stands.
- The stationary-window diagnostic quoted at `CLAUDE.md:776`, "5 of 24", is
  **5 of 24 on both channels**. Unchanged.
- `driven_downstream` is True on all 36 runs, so it never altered a verdict here.

### 3.2 What DOES change, all of it in derived `p_move` statistics

Each committed figure was first reproduced exactly on the committed channel, as a
held-fixed control, before recomputing:

| claim, and where | committed channel | corrected channel |
|---|---|---|
| `CLAUDE.md:783`, "17 of 24 runs flip verdict somewhere in p >= 0.01 to 0.50" | 17 of 24 (reproduced) | **15 of 24** |
| `CLAUDE.md:776` and `RESEARCH_TO_IMPLEMENTATION:91`, full-record SLIDE "21 of 24" | 21 of 24 (reproduced) | **19 of 24** |
| `RESEARCH_TO_IMPLEMENTATION:93-94`, m2337 margins "19, 8, 1", "qualitatively matching" | 19, 8, 1 | **8, 7, 1, matching J15 exactly** |

`analysis/settle_audit.py:34`'s comment is false as written and should be corrected
whether or not its conclusions move; its stationarity results are about `dmag` as
an observable in its own right, which is legitimate, but the sentence claims those
channels are what the verdicts read.

---

## 4. The persistence question itself

### 4.1 The literature does not support a persistence requirement at all

Carried from r7 and not re-derived here, with its provenance:

- The project's own 332-paper index returns **zero** matches for "persistence"
  (`python3 analysis/research_index.py --query persistence`).
- Bonham & Hattersley 1967 and Gordon & Stone 1973 restrained their models "by
  fine threads both vertically and laterally", so no motion time series existed
  and **a duration was not measurable in principle**.
- Martinez-Gomariz 2017 (UPCommons postprint, primary): instability is "if the
  model vehicle moved".

`sustain_frames = 3` at `failure_modes.py:52` is 0.1 s at 30 fps and has no
source. Register D6f records the same constant as the only thing keeping TOPPLE
from firing on all 13.

### 4.2 What the constant does to the local set

At `slide_m = 0.05 m` and `slide_speed_ms = 0.05 m/s`, on the 17 canonical runs:

| `sustain_frames` | verdicts |
|---|---|
| 3 | 16 SLIDE / 1 STUCK |
| 4 | 16 SLIDE / 1 STUCK |
| 5 | 15 SLIDE / 2 STUCK |

The canonical 17 are more robust to this constant than the fine-grid ensemble is,
because they exist only at g48/g64/g96. Per grid over all 36 local runs, at the
same two thresholds, SLIDE count at `sustain_frames` 3/4/5: g48 3/3/3 of 3,
g64 13/13/13 of 17, g96 9/9/6 of 9, g128 6/4/4 of 6.

**The g160 result is not mine and is not locally re-derivable.** r7 reports
0 SLIDE / 5 STUCK at every threshold at g160, on branch `claude/r7-pinned-span`
per `docs/HANDOFF_ROUND_7_2026-08-18.md` ledger 3c. No g160 data exists on this
disk: `/usr/bin/grep -rl g160 /Users/josie/can-it-ford/data/` returns nothing, and
the local tree holds only `data/g128_canonical_2026-08-13` and
`data/g128_canonical_repeat`. Cite it to r7, not to this document.

### 4.3 The case for frequency, in one number

At `slide_m = 0.05 m`, `slide_speed_ms = 0.05 m/s`, `sustain_frames = 3`, the
binary assigns the **same label, SLIDE**, to:

- `sweepV_g64_v3p0`, which holds the joint condition on **93.41 percent** of frames, and
- `A:canon_g96_m2337`, which holds it on **4.40 percent** of frames.

A factor of 21 in the underlying quantity, one label. The 16 canonical SLIDE runs
span **4.40 to 93.41 percent**, a range of 89.01 percentage points, all reported as
one word. That is the argument, and it does not depend on `sustain_frames` being
wrong; it only depends on the binary discarding the magnitude of the evidence.

---

## 5. Recommendation, and the mechanism that would refute it

**Recommendation.** Report `p_move` on the surge channel, with its Wilson interval
on effective sample size, ALONGSIDE the deterministic verdict and its threshold
quadruple, rather than instead of it. Do not remove `sustain_frames` from
`failure_modes.py`: it is unsourced, but removing it silently changes published
verdicts, and the honest fix is to report the frequency next to the label and
state the probability cut, as Dancey et al 2002 do.

**The refuting mechanisms, named in advance and then tested.**

**R1, degeneracy.** If `p_move` only ever took the values 0 or 1 it would carry no
more information than the binary. *Does not fire:* 4 of 36 runs sit at exactly 0 or
1; the other 32 are interior.

**R2, no discrimination.** If every run the binary calls SLIDE had the same
`p_move`, frequency would add nothing to the label. *Does not fire:* the 16
canonical SLIDE runs span 4.40 to 93.41 percent, a span of 89.01 pp.

**R3, reproducibility, the one that would actually settle it.** The complaint
against the binary is that it flips under refinement. If the frequency were LESS
reproducible across identical-setting repeats than the binary is, the frequency
would be the worse measure. Tested on the 6 repeat pairs in
`data/g128_canonical_2026-08-13` against `data/g128_canonical_repeat`:

| pair | p_C batch A | p_C batch B | difference | binary agrees |
|---|---|---|---|---|
| `canon_g128_m1100` | 46.15% | 46.15% | 0.00 pp | yes, SLIDE |
| `canon_g128_m1609` | 15.38% | 15.38% | 0.00 pp | yes, SLIDE |
| `canon_g128_m2337` | 3.30% | 3.30% | 0.00 pp | yes, SLIDE |
| `canon_g96_m1100` | 19.78% | 19.78% | 0.00 pp | yes, SLIDE |
| `canon_g96_m1609` | 10.99% | 10.99% | 0.00 pp | yes, SLIDE |
| `canon_g96_m2337` | 4.40% | 4.40% | 0.00 pp | yes, SLIDE |

*Does not fire:* the frequency is exactly as reproducible as the binary on all 6
pairs.

**R3's power, stated because a zero difference is worthless without it.** The two
batches are NOT copies: `/usr/bin/cmp` reports them differing from line 2 onward in
all 6 pairs. Per pair, the largest frame-wise disagreement and the number of frames
close enough to a threshold that they could have flipped the count:

| pair | max delta `\|dx\|` | max delta `\|vx\|` | frames at risk |
|---|---|---|---|
| `canon_g128_m1100` | 1.644e-03 m | 7.634e-03 m/s | 2 of 91 |
| `canon_g128_m1609` | 3.667e-04 m | 1.146e-02 m/s | 1 of 91 |
| `canon_g128_m2337` | 1.750e-03 m | 1.375e-02 m/s | 3 of 91 |
| `canon_g96_m1100` | 2.234e-03 m | 9.731e-03 m/s | 2 of 91 |
| `canon_g96_m1609` | 1.110e-03 m | 1.465e-02 m/s | 3 of 91 |
| `canon_g96_m2337` | 7.167e-04 m | 9.188e-03 m/s | 1 of 91 |

**This is a real test but a weak one.** With only 1 to 3 at-risk frames out of 91
per pair, it rules out a LARGE reproducibility penalty and nothing finer. It should
be repeated on an ensemble with more spread before R3 is treated as settled.

---

## 6. The proposed fix to `analysis/probabilistic_verdict.py`

**I did not apply this.** `probabilistic_verdict.py` is outside slot d2-persist's
write scope, and `simulation/failure_modes.py` is explicitly not to be touched by
this slot. The patch below was produced by editing a copy and diffing against the
committed file, so it is known to apply.

```diff
--- a/analysis/probabilistic_verdict.py
+++ b/analysis/probabilistic_verdict.py
@@ -143,7 +143,10 @@
         start = min(rep["recommended_discard"], n - 12)
     d_w, v_w = dmag[start:], vmag[start:]
 
-    mask = [(d > slide_m and v > slide_speed) for d, v in zip(d_w, v_w)]
+    # Comparator is >=, matching simulation/failure_modes.py:182. A strict > here
+    # silently disagrees with the classifier on any sample landing exactly on a
+    # threshold.
+    mask = [(d >= slide_m and v >= slide_speed) for d, v in zip(d_w, v_w)]
     k = sum(mask)
     nw = len(mask)
     eps = episodes(mask)
@@ -241,10 +244,19 @@
     rows, flippers = [], 0
     for name, path in runs:
         cols = load_metrics(path)
-        if "dmag" not in cols or "vmag" not in cols:
+        # SURGE CHANNEL, not the 3D magnitudes. simulation/failure_modes.py gates
+        # SLIDE on SURGE_AXIS = 0 (its :18), that is |dx| at :168 and |vx| at :170.
+        # Passing dmag and vmag here gates a DIFFERENT quantity: since dmag >= |dx|
+        # and vmag >= |vx| elementwise, it returns an upper bound on the
+        # classifier's own gate. Measured on 36 local runs, the over-count reaches
+        # 29.67 percentage points, and 114 of the 116 over-counted frames are
+        # frames where the vertical or lateral velocity carries vmag over
+        # slide_speed_ms while the surge speed |vx| is below it, that is, bobbing
+        # scored as sliding. See docs/R8_PERSISTENCE_GATE_2026-08-18.md.
+        if not {"dx", "vx"} <= set(cols):
             continue
         try:
-            res = assess(cols["dmag"], cols["vmag"],
+            res = assess([abs(z) for z in cols["dx"]], [abs(z) for z in cols["vx"]],
                          use_stationary_window=args.stationary_window)
         except ValueError:
             continue
```

Two further edits a human should make at the same time, both outside this slot's
scope:

1. `analysis/settle_audit.py:34`, replace `# Observables worth testing. dmag and
   vmag are what the verdicts read.` with a comment saying the verdicts read `dx`
   and `vx` and that `dmag`/`vmag` are tested as observables in their own right.
2. `CLAUDE.md:783-784`, change "17 of 24" to "15 of 24" and drop the word
   "independently", which is the same-input-file error CLAUDE.md August 4 item 12
   already warns about.

Applying the diff changes no published physics verdict. It changes the three
derived statistics listed in section 3.2.

---

## 7. Run enumeration and the full tables

37 `metrics.csv` exist locally, walked from the tree and printed rather than
asserted:

| family | count |
|---|---|
| canonical-17 (`renders/yaris_render_s1/_incoming/`) | 17 |
| g128-batch-A (`data/g128_canonical_2026-08-13/`) | 6 |
| g128-batch-B (`data/g128_canonical_repeat/`) | 6 |
| other-local (elsewhere under `renders/`) | 8 |
| **total** | **37** |

**Excluded, 1:** `renders/mpm-engine-out/flood_vehicle/metrics.csv`, missing
columns `vmag` and `vx`. Its header is the 8-column pre-velocity format
(`t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg`), so no speed channel exists and no
SLIDE condition can be evaluated. **Classified: 36 of 37.**

This also explains a previously unexplained number: `probabilistic_verdict.py`'s
docstring says "the 24 local runs". That is the 25 `metrics.csv` under `renders/`
minus this one file. The 24 was never wrong, it was just never derived.

Grid is read from each run's own `summary.json` `n_grid`, not parsed from the
directory name, because `renders/yaris_render_s1/m*` carry no grid marker in their
names (all three are `n_grid = 64`).

<!-- MARKDOWN TABLES, generated by analysis/r8_persistence_frequency.py -->

### Table 1. The channel gap

| run | frames | p_A (dmag,vmag) % | p_B (\|dx\|,\|vx\|) % | gap pp | A/B |
|---|---|---|---|---|---|
| `yaris_L2_d0p30_v1p5` | 91 | 29.67 | 0.00 | 29.67 | inf |
| `s1/m1100` | 91 | 30.77 | 2.20 | 28.57 | 14.00 |
| `g48_m1609` | 91 | 30.77 | 16.48 | 14.29 | 1.87 |
| `g48_m2337` | 91 | 24.18 | 12.09 | 12.09 | 2.00 |
| `g48_m1100` | 91 | 27.47 | 21.98 | 5.49 | 1.25 |
| `g64_m1609` | 91 | 35.16 | 30.77 | 4.40 | 1.14 |
| `s1/g64_m1609` | 91 | 35.16 | 30.77 | 4.40 | 1.14 |
| `A:canon_g128_m1100` | 91 | 49.45 | 46.15 | 3.30 | 1.07 |
| `B:canon_g128_m1100` | 91 | 49.45 | 46.15 | 3.30 | 1.07 |
| `g64_m2337` | 91 | 14.29 | 10.99 | 3.30 | 1.30 |
| `sweepD_g64_d0p25` | 91 | 29.67 | 26.37 | 3.30 | 1.12 |
| `sweepD_g64_d0p45` | 91 | 83.52 | 80.22 | 3.30 | 1.04 |
| `s1/g64_m2337` | 91 | 14.29 | 10.99 | 3.30 | 1.30 |
| `sweepV_g64_v1p0` | 91 | 27.47 | 25.27 | 2.20 | 1.09 |
| `A:canon_g96_m1100` | 91 | 20.88 | 19.78 | 1.10 | 1.06 |
| `g96_m1100` | 91 | 20.88 | 19.78 | 1.10 | 1.06 |
| `A:canon_g128_m2337` | 91 | 4.40 | 3.30 | 1.10 | 1.33 |
| `B:canon_g96_m1609` | 91 | 12.09 | 10.99 | 1.10 | 1.10 |
| `sweepV_g64_v0p5` | 91 | 1.10 | 0.00 | 1.10 | inf |
| `sweepV_g64_v2p5` | 91 | 93.41 | 92.31 | 1.10 | 1.01 |
| `A:canon_g128_m1609` | 91 | 15.38 | 15.38 | 0.00 | 1.00 |
| `A:canon_g96_m1609` | 91 | 10.99 | 10.99 | 0.00 | 1.00 |
| `A:canon_g96_m2337` | 91 | 4.40 | 4.40 | 0.00 | 1.00 |
| `B:canon_g128_m1609` | 91 | 15.38 | 15.38 | 0.00 | 1.00 |
| `B:canon_g128_m2337` | 91 | 3.30 | 3.30 | 0.00 | 1.00 |
| `B:canon_g96_m1100` | 91 | 19.78 | 19.78 | 0.00 | 1.00 |
| `B:canon_g96_m2337` | 91 | 4.40 | 4.40 | 0.00 | 1.00 |
| `g64_m1100` | 91 | 48.35 | 48.35 | 0.00 | 1.00 |
| `g96_m1609` | 91 | 10.99 | 10.99 | 0.00 | 1.00 |
| `g96_m2337` | 91 | 4.40 | 4.40 | 0.00 | 1.00 |
| `sweepD_g64_d0p35` | 91 | 81.32 | 81.32 | 0.00 | 1.00 |
| `sweepV_g64_v2p0` | 91 | 73.63 | 73.63 | 0.00 | 1.00 |
| `sweepV_g64_v3p0` | 91 | 93.41 | 93.41 | 0.00 | 1.00 |
| `s1/g64_m1100` | 91 | 48.35 | 48.35 | 0.00 | 1.00 |
| `s1/m1609` | 91 | 0.00 | 0.00 | 0.00 | n/a |
| `s1/m2337` | 91 | 0.00 | 0.00 | 0.00 | n/a |

### Table 2. Gate-pass frequency on the classifier's own gate

| run | grid | p_C % | 95% CI on N_eff | N_eff | longest run | sf=3 | sf=4 | sf=5 |
|---|---|---|---|---|---|---|---|---|
| `yaris_L2_d0p30_v1p5` | ? | 0.00 | [0.00, 56.48] | 3.0 | 0 | STUCK | STUCK | STUCK |
| `g48_m1100` | 48 | 21.98 | [4.76, 61.33] | 5.9 | 20 | SLIDE | SLIDE | SLIDE |
| `g48_m1609` | 48 | 16.48 | [3.18, 54.23] | 6.7 | 15 | SLIDE | SLIDE | SLIDE |
| `g48_m2337` | 48 | 12.09 | [1.95, 48.73] | 7.2 | 11 | SLIDE | SLIDE | SLIDE |
| `g64_m1100` | 64 | 48.35 | [13.60, 84.78] | 3.7 | 44 | SLIDE | SLIDE | SLIDE |
| `g64_m1609` | 64 | 30.77 | [7.66, 70.42] | 5.1 | 28 | SLIDE | SLIDE | SLIDE |
| `g64_m2337` | 64 | 10.99 | [1.43, 51.25] | 5.9 | 10 | SLIDE | SLIDE | SLIDE |
| `s1/g64_m1100` | 64 | 48.35 | [13.60, 84.78] | 3.7 | 44 | SLIDE | SLIDE | SLIDE |
| `s1/g64_m1609` | 64 | 30.77 | [7.66, 70.42] | 5.1 | 28 | SLIDE | SLIDE | SLIDE |
| `s1/g64_m2337` | 64 | 10.99 | [1.43, 51.25] | 5.9 | 10 | SLIDE | SLIDE | SLIDE |
| `s1/m1100` | 64 | 2.20 | [0.04, 57.36] | 3.1 | 1 | STUCK | STUCK | STUCK |
| `s1/m1609` | 64 | 0.00 | [0.00, 56.30] | 3.0 | 0 | STUCK | STUCK | STUCK |
| `s1/m2337` | 64 | 0.00 | [0.00, 56.42] | 3.0 | 0 | STUCK | STUCK | STUCK |
| `sweepD_g64_d0p25` | 64 | 26.37 | [6.09, 66.44] | 5.3 | 24 | SLIDE | SLIDE | SLIDE |
| `sweepD_g64_d0p35` | 64 | 81.32 | [32.32, 97.54] | 3.5 | 59 | SLIDE | SLIDE | SLIDE |
| `sweepD_g64_d0p45` | 64 | 80.22 | [32.50, 97.16] | 3.7 | 49 | SLIDE | SLIDE | SLIDE |
| `sweepV_g64_v0p5` | 64 | 0.00 | [0.00, 47.48] | 4.3 | 0 | STUCK | STUCK | STUCK |
| `sweepV_g64_v1p0` | 64 | 25.27 | [5.54, 66.11] | 5.2 | 23 | SLIDE | SLIDE | SLIDE |
| `sweepV_g64_v2p0` | 64 | 73.63 | [27.34, 95.39] | 3.6 | 53 | SLIDE | SLIDE | SLIDE |
| `sweepV_g64_v2p5` | 64 | 92.31 | [41.67, 99.51] | 3.6 | 58 | SLIDE | SLIDE | SLIDE |
| `sweepV_g64_v3p0` | 64 | 93.41 | [44.37, 99.60] | 3.9 | 53 | SLIDE | SLIDE | SLIDE |
| `A:canon_g96_m1100` | 96 | 19.78 | [4.18, 58.21] | 6.3 | 18 | SLIDE | SLIDE | SLIDE |
| `A:canon_g96_m1609` | 96 | 10.99 | [1.67, 47.31] | 7.3 | 10 | SLIDE | SLIDE | SLIDE |
| `A:canon_g96_m2337` | 96 | 4.40 | [0.31, 40.18] | 7.2 | 4 | SLIDE | SLIDE | STUCK |
| `B:canon_g96_m1100` | 96 | 19.78 | [4.09, 58.76] | 6.1 | 18 | SLIDE | SLIDE | SLIDE |
| `B:canon_g96_m1609` | 96 | 10.99 | [1.64, 47.70] | 7.1 | 10 | SLIDE | SLIDE | SLIDE |
| `B:canon_g96_m2337` | 96 | 4.40 | [0.31, 40.42] | 7.1 | 4 | SLIDE | SLIDE | STUCK |
| `g96_m1100` | 96 | 19.78 | [4.13, 58.51] | 6.2 | 18 | SLIDE | SLIDE | SLIDE |
| `g96_m1609` | 96 | 10.99 | [1.62, 48.07] | 7.0 | 10 | SLIDE | SLIDE | SLIDE |
| `g96_m2337` | 96 | 4.40 | [0.26, 45.05] | 5.8 | 4 | SLIDE | SLIDE | STUCK |
| `A:canon_g128_m1100` | 128 | 46.15 | [13.31, 82.72] | 4.1 | 42 | SLIDE | SLIDE | SLIDE |
| `A:canon_g128_m1609` | 128 | 15.38 | [2.97, 51.91] | 7.2 | 14 | SLIDE | SLIDE | SLIDE |
| `A:canon_g128_m2337` | 128 | 3.30 | [0.19, 38.01] | 7.5 | 3 | SLIDE | STUCK | STUCK |
| `B:canon_g128_m1100` | 128 | 46.15 | [13.31, 82.72] | 4.1 | 42 | SLIDE | SLIDE | SLIDE |
| `B:canon_g128_m1609` | 128 | 15.38 | [2.98, 51.86] | 7.2 | 14 | SLIDE | SLIDE | SLIDE |
| `B:canon_g128_m2337` | 128 | 3.30 | [0.18, 39.16] | 7.1 | 3 | SLIDE | STUCK | STUCK |

### Table 3. Per grid

| grid | n | p_C min % | p_C median % | p_C max % | p_A median % | SLIDE at sf=3/4/5 |
|---|---|---|---|---|---|---|
| g48 | 3 | 12.09 | 16.48 | 21.98 | 27.47 | 3/3/3 of 3 |
| g64 | 17 | 0.00 | 30.77 | 93.41 | 35.16 | 13/13/13 of 17 |
| g96 | 9 | 4.40 | 10.99 | 19.78 | 10.99 | 9/9/6 of 9 |
| g128 | 6 | 3.30 | 15.38 | 46.15 | 15.38 | 6/4/4 of 6 |
| unknown | 1 | 0.00 | 0.00 | 0.00 | 29.67 | 0/0/0 of 1 |

---

## 8. Provenance and what is not verified

**Tables in section 7 are generated**, not typed, by
`analysis/r8_persistence_frequency.py --markdown`. Regenerate them rather than
editing them by hand.

**Claim tags.** Every file:line reference in sections 1, 3 and 6 was read directly
from the main checkout during this session. Every percentage, count and verdict in
sections 2, 3, 4, 5 and 7 was measured by running the script or, for the
independently-checked cases, by a separate direct column read. The g160 result in
section 4.2 is recalled from r7's handoff and is explicitly NOT re-derived here.
The literature points in section 4.1 are carried from r7's primary-source reads and
were not re-verified against the primary sources in this session.

**THE PHYSICS-SKEPTIC SUBAGENT WAS UNAVAILABLE THIS SESSION.** Two attempts, the
second with an explicit model override, both terminated with an API error naming a
model this account cannot reach. Per the operating protocol this is stated rather
than faked: **the claims in this document have NOT had an independent adversarial
review.** What they have had instead, done by the same author and therefore not
independent:

- the identity `p_A >= p_B` self-tested on all 36 runs (36/36 hold),
- variant C checked against `data/failure_modes_by_run_classified.csv` on both
  verdict and `onset_frame_slide` (17/17 and 17/17),
- the four headline gap cases re-measured by a direct `csv.DictReader` read that
  does not import this script at all,
- both committed statistics reproduced exactly on the committed channel before
  being recomputed on the corrected one,
- the corrected channel checked against a register series computed by a different
  script before this work existed (section 2.3).

**A reproduction is not a validation.** This script reads the same `metrics.csv`
files the published tables were built from, so agreeing with them cannot be
independent confirmation of the physics. It confirms only that the arithmetic and
the gate definition match. CLAUDE.md August 4 item 12 records this exact trap.

**Not touched by this slot:** `simulation/failure_modes.py` is byte-unchanged,
`analysis/probabilistic_verdict.py` is byte-unchanged, `analysis/settle_audit.py`
is byte-unchanged, `CLAUDE.md` is byte-unchanged. This slot wrote exactly two new
files.
