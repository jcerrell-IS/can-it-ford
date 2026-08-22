# D4: the whole manifest re-costed against 629 SU, with the triage call made in advance

2026-08-17, written 20:55 UTC. **Timestamps in this document are UTC.** This machine's
local zone shifted CEST to BST during the session, so local-time labels in my earlier notes
are inconsistent by an hour across that boundary. Use UTC or a job id, never local time.

---

## 0. The one-line answer

**The full queue costs 4.27 node-hours. It fits inside 629 SU unless Vista charges more
than 147 SU per node-hour, which no plausible rate approaches. Fire everything, in the
order below. If anything is dropped, drop Job C, and drop it for a reason that is not
cost.**

## 1. What changed, and it changed a lot

Correction B3 replaced the group velocity with Kramer's own phase celerity for the
reflection window. That made `lim = 1.2` buy **1.06** clean natural periods rather than the
2.12 I had claimed, so **Job C moved from `lim = 1.2` to `lim = 2.2`**. The scene grew from
606,814 to **2,406,631** water particles at the same 82 substeps.

| | before B3 | after B3 |
|---|---|---|
| Job C | 1.0 node-h | **3.68 node-h** |
| full queue | ~1.6 node-h | **4.27 node-h** |

**Job C is now 86% of the entire queue.** That single convention correction is worth more
than every other cost line combined, which is why the triage below is clean rather than
close.

## 2. The arithmetic, stated rather than asserted

Throughput anchor **8.94e6 particle-substeps/s**, water-only, derived from
`data/g128_canonical_2026-08-13/00_provenance.txt`: 6 runs (3x g96 + 3x g128) between
`start=10:57:44` and `ALLDONE end=11:03:57`, i.e. **373 s**. It is an LS6 job, so treat it
as good to a factor of 2 to 3 on Vista GH200; section 4 shows why that does not matter.

| job | scene | cost |
|---|---|---|
| **A1** brake sweep, 3 mu, 250 frames | g64 canonical, 48,367 particles, 11 substeps | **0.012 node-h** (0.7 min) |
| **A2** repeats n=10, 250 frames | g96 + g64 canonical | **0.265 node-h** (15.9 min) |
| **B** sphere `--fixed`, 200 frames | lim 1.2, n_grid 64, 606,814 particles, 82 substeps | **0.309 node-h** (18.6 min) |
| **C** sphere free decay, 3 drops | lim 2.2, n_grid 117, 2,406,631 particles, 82 substeps | **3.679 node-h** (220.7 min) |
| | **FULL QUEUE** | **4.266 node-h** |

**I still have no primary source for the SU-per-node-hour rate** and will not invent one.
So here is the arithmetic across the plausible span, plus the break-even, which is the part
that actually decides it:

| rate | SU used | % of 629 |
|---|---|---|
| 1 SU/node-h | 4.3 | 0.7% |
| 5 | 21.3 | 3.4% |
| 10 | 42.7 | 6.8% |
| 32 | 136.5 | 21.7% |
| 100 | 426.6 | 67.8% |

**BREAK-EVEN: the full queue exceeds 629 SU only above 147 SU per node-hour.** Dropping
Job C leaves 0.587 node-h, whose break-even is **1,072 SU per node-hour**.

**Confirm the real rate with `tacc_alloc_status` on first contact and multiply.** But the
decision does not hinge on it: no GPU allocation charges 147 SU per node-hour.

## 3. Fire order, and the drop order, decided now

| # | job | node-h | what it converts | drop rank |
|---|---|---|---|---|
| 1 | **A1** | 0.012 | the last **INFERRED** claim into a measurement | **never drop** |
| 2 | **A2** | 0.265 | N = 1 into spread and gate-pass frequency; P2G onset free | drop n=10 to n=5, saves 0.133 |
| 3 | **B** | 0.309 | no external validation into one, **gradeable today** | drop 200 to 120 frames, saves 0.123 |
| 4 | **C** | 3.679 | **nothing gradeable until `/s1` arrives** | **drop first** |

**A1 is 0.012 node-hours. If exactly one thing runs, run A1.** It is the only item that
turns "the STUCK run would flip to SLIDE at rolling-resistance friction" from INFERRED into
measured, and it is fused with A2 so its ~80-120 s of `warpmpm` import startup is not paid
twice.

**Drop C first, and the reason is not its cost.** Its primary pass criterion cannot be
evaluated at all until the Kramer `/s1` supplementary is in hand. Running it now produces a
result nobody can grade, which is precisely what fixing criteria in advance is meant to
prevent. That it is also 86% of the queue makes the call easy rather than making it.

**Everything gradeable today is A1 + A2 + B = 0.587 node-hours.** That is the recommendation
if you want one number.

Batch every job via `tacc_submit`, never idev: interactive burned 98.5 to 99.1% of Vista
node-hours historically, with 95 of 184 runs ending in TIMEOUT.

## 4. Two standing rules, put where a future session will hit them

Both came out of the review passes and both are too general to leave inside one document.

### RULE 1. An argument that reaches the right answer without engaging the refuting mechanism is not verified.

My brake-state argument concluded correctly that no SLIDE verdict can flip, by reasoning
that lower friction increases sliding. But `simulation/failure_modes.py:33` and `:230-234`
make the reported mode a **severity-ranked competition**, `MODE_SEVERITY = (SLIDE, TOPPLE,
FLOAT)` with `mode = reached[-1]`. A SLIDE verdict does not need sliding to stop in order to
flip; **it only needs a higher-ranked mode to trigger.** My argument never touched the only
mechanism that could have refuted it. What actually closes it is the bound: sustained
3-frame acceleration reaches at most `T3 = 0.721`, friction removal adds at most 0.578 g,
and `0.721 + 0.578 = 1.299 < 1.42 = ssf`. (Later refined: the buoyancy-corrected ceiling is
0.215 g, so the margin is larger still.)

**Test: name the mechanism that would refute you, then show it does not fire. If you cannot
name it, you have not verified anything.**

### RULE 2. Two readers independently choosing the same reading of an ambiguous phrase is one guess, not corroboration.

Nihei 2025's "critical sliding velocity approximately **0.3x lower** for unbraked vs
braked" is ambiguous between *a factor of 0.3* and *a 30% reduction*. D1 and I each picked
the factor reading, independently. **That is not two sources agreeing; it is the same guess
made twice**, and the independence makes it feel stronger while adding nothing.

**Test: if the disagreement you are checking for is a reading of ambiguous text rather than
a measurement, independent agreement carries no weight. Go to the primary source or record
the ambiguity.** The corrigendum, `10.1016/j.rineng.2025.107527`, is gold open access and
still unread; it may settle it in one line.

## 5. Status unchanged

Docs remain **REVIEWED-WITH-CORRECTIONS**. The STUCK flip remains **INFERRED** until A1
measures it. Both TACC sockets re-probed and still returning the token prompt, so nothing
here can run yet.
