## YOUR SLOT: d15-settle, branch `claude/r9-settle`, worktree `.claude/worktrees/r9-settle`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d15-settle` first.

### The contradiction, already measured, never acted on

`sim_standing.py` uses `settle_frames=8`. `analysis/settle_audit.py` applied `analysis/stationarity.py` to all 25 local runs, using the 15-column `metrics.csv` files already on disk, no GPU needed, and found:

- **25 of 25 runs need MORE than 8 frames discarded.** Min 29, median 48, max 80, out of 91 total frames.
- **N_eff is 2.9 to 11.0.** A 91-frame record holds roughly 3 to 11 independent samples, so any uncertainty computed from N=91 is overstated by about 3x to 5x.
- 12 of 25 retained windows are still non-stationary at 5 percent.

Read the live CLAUDE.md section headed "THE FIXED SETTLE LENGTH IS CONTRADICTED BY OUR OWN DATA" at `/Users/josie/can-it-ford/CLAUDE.md` by absolute path, and re-run the audit yourself rather than quoting those numbers from this dispatch.

### The trap that makes this hard, and it is already documented

**DO NOT REMOVE THE TRANSIENT BEFORE A SLIDE VERDICT.** Incipient motion is an EVENT, not a steady state. Removing the transient drops SLIDE from 21 of 24 runs to 5 of 24 and would silently contradict the published 16 SLIDE / 1 STUCK. `probabilistic_verdict.py` defaults to the full record for exactly this reason and `--stationary-window` is a robustness diagnostic only.

So the honest position is asymmetric and your write-up must carry it: **full record for verdicts, demonstrated-stationary window for any convergence or uncertainty claim.** Anyone who applies one rule to both cases gets a wrong answer in one of them.

Also: **MSER minimises standard error, which is not stationarity.** A settle length chosen to stabilise a mean is not evidence the record is stationary; a residual trend can survive inside the MSER-optimal window and only the reverse-arrangement test catches it. `stationarity.py` reports both and carries a self-test for this trap.

### Your unit

Turn a measured contradiction into an executable recommendation.

1. State what `settle_frames` should be, per run or as a rule, with the evidence and the failure mode of the choice.
2. State which published quantities would move and which would not, and quantify it. If the answer is that no verdict moves, that is a strong and publishable result; say it plainly rather than burying it.
3. Say explicitly what CANNOT be fixed by any settle length, namely that a 91-frame record carrying 3 to 11 independent samples is short, which reaches the same conclusion as register D9's 250-frame finding by a different route.

### Boundaries

**Do NOT edit `sim_standing.py`.** It is canonical, it is the driver for all 17 gated runs, and slot d8-naming already holds `renders/**/sim_standing.py` in its write scope. Produce the recommendation and the patch as a diff inside your document. Changing the driver is a separate decision with a re-run cost attached.

Relatedly, slot d3-force measured last night that a DIFFERENT settle mechanism (the pinned-settle quiescence gate in the coupling-force rung, not this one) needs about 2596 frames against a 900 cap to meet its gate. Those are two different settles in two different scenes. Do not merge them into one claim.

No GPU. Everything is on disk.
