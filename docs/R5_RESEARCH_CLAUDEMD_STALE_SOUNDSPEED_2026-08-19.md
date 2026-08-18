# R5-D1 unit 69: CLAUDE.md says the sound speed was never swept. It was.

Date 2026-08-19. Branch `claude/r5-research`.
**For whoever maintains CLAUDE.md. I have not edited it: that file is explicitly
outside my scope.**

---

## 1. The stale line

`CLAUDE.md:523-524`, in the AUGUST 5 2026 RESEARCH INTEGRATION V2 section:

> "Artificial sound speed can qualitatively flip a rigid-body outcome,
> Isik and He 2022, **never swept here**."

**It was swept, on 2026-08-07, in jobs 895330 and 895378.**
`docs/FULL_SESSION_FINDINGS_2026-08-07.md:383` is headed "Results, jobs 895330 and
895378" and its table varies `c` across **three decades**:

```
run              disp (m)    c (m/s)   substeps  cells/depth
ctrl_g64          0.65715      12.85       11      2.038
enh_g96           0.26921      12.85       16      3.057
enh_g96_c10       0.48839     128.45      156      3.057
enh_g128_c10      0.67768     128.45      208      4.076
enh_g96_real      0.28232    1480.98     1797      3.057
enh_g128_real     0.33524    1480.98     2396      4.076
```

**N = 6 runs, 3 sound speeds, 2 grids, including two at physical water sound speed
(1480.98 m/s).** Cost 4 SUs, 23 min 32 s of single-node GH200 time, batch only.

My own session-start reminder already says this: "Sound-speed sweep is DONE, jobs
895330 and 895378. Do not re-propose it as untested." **So the hook and the standing
rules currently contradict each other**, and only the hook is right.

## 2. Why this is worth a line rather than a shrug

CLAUDE.md is the file every pane loads automatically and is told not to restate. A
stale "never swept here" invites exactly one behaviour: a future session proposing
the sweep as new work. It costs GPU time to re-run something that cost 4 SUs and is
already on disk.

**Register G7 at `:278` is NOT stale and should not be changed.** It says Isik and
He is "a neutrally buoyant cylinder in Poiseuille flow, not a vehicle, so magnitudes
do not transfer. No vehicle-flood or MPM study **isolates this parameter**." That is
a statement about **the literature**, which remains true. CLAUDE.md's "never swept
here" is a statement about **this project**, which does not. Two different claims;
only one has gone stale.

## 3. UNREVIEWED: the sweep is non-monotone in c

Computed from the table above:

```
g96 :  c=12.85  -> 0.26921   (baseline)
       c=128.45 -> 0.48839   +81.4%
       c=1480.98-> 0.28232    +4.9%
g128:  c=128.45 -> 0.67768   (baseline)
       c=1480.98-> 0.33524   -50.5%
```

**Displacement rises then falls with increasing c at g96, and falls by half at g128.**
So the response is not monotone in sound speed, and the physical value (1480.98) sits
close to the lowest artificial one at g96 while differing greatly at g128.

**I am not drawing a conclusion from that.** It is arithmetic on a six-row table I
did not produce, at a settle length I have not established, and unit 65 is a fresh
reminder of what happens when I reason about verdict direction from a table. It is
flagged for D4, who owns resolution and convergence.

## 4. Status

UNVERIFIED:
1. **I did not run these jobs or read their raw output.** Section 1 is transcribed
   from `FULL_SESSION_FINDINGS_2026-08-07.md:383-390`.
2. **Settle length not established.** Every displacement above is at whatever settle
   the enhanced driver used, which I have not confirmed is the canonical 8 frames.
3. Section 3 is UNREVIEWED arithmetic, not a physics finding.
4. Whether these six runs constitute a *sufficient* sweep is a separate question from
   whether a sweep happened. I address only the second.
5. I have not edited CLAUDE.md and am not proposing wording; the maintainer should
   decide whether to amend `:524` or to note the 2026-08-07 result beside it.
