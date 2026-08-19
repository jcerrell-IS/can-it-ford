# Did the fixes propagate, or were they only recorded? Measured 2026-08-19

Measured at 20:05 BST by slot d20-reader, answering the coordinator's question directly:
whether the fleet's sideways propagation actually improved after the readout and audit went
out, or whether the fixes were only written down.

**Cut point 18:52 BST**, when `a6e9f56` (the cross-session readout) landed. Population: every
commit on every ref since the wave began at 2026-08-18 20:00, deduplicated by SHA.
102 before, 40 after.

## Result 1. Generic sideways propagation did NOT improve, and it did not need to

| measure | before | after | diff | z |
|---|---|---|---|---|
| commits carrying a reference to another slot by name | 41/102 = **0.402** | 19/40 = **0.475** | +0.073 | **0.79** |

z = 0.79 is a null result. **The fleet was already cross-referencing at 40 percent before
any of my documents existed**, through the board.

**This refutes a sentence in my own audit.** `docs/R9_COORDINATOR_AUDIT_2026-08-19.md`
section 3 says the failure was "that nothing propagated sideways between them except an
untracked 226 KB file." That is wrong as written. Findings propagated well, and the
untracked file was the channel doing it. What failed to propagate was **file state**, not
findings: the corrected `SKILL.md` reached one worktree of nine. The two are different
predicates and I merged them, which is the same shape as *reach* versus *cited* and
*assignment* versus *occurrence* elsewhere in this project.

## Result 2. What did change is that the fleet acquired stable identifiers

| measure | before | after | z |
|---|---|---|---|
| commits citing a readout/audit finding id | 7/102 raw | 15/40 raw | 4.54 |
| **after removing artifacts and self-citation** | **0/102** | **6/40** | |

**The raw "before" count of 7 is entirely artifact and I checked rather than reporting it.**
All seven match on `v1`/`v2` (the `can-it-ford-sweep-v1` dataset name) or `A2` (register row
A2, which predates my documents). Zero are references to a finding of mine. The true
baseline is **0**.

The raw "after" count of 15 also needs deflating, and the deflation is the honest part:

| category | n | commits |
|---|---|---|
| coordinator echoing the findings back while implementing | 5 | `505aef7`, `88cba09`, `95167b0`, `e81bc9c`, `c621931` |
| my own commits, self-citation, excluded | 2 | `a6e9f56`, `9c19364` |
| regex artifacts (`v1`, `v2`, `v3` again) | 2 | `ca45222`, `c0fa82b` |
| **genuine slot-to-slot uptake** | **6** | `054594d`, `d363a1d` (d21-jobb), `4d4b57d`, `b65dc0d`, `51c158b` (d17-moving), `5692f1e` (d18-platform) |

**Six commits, from three distinct slots that are not me and not the coordinator.**
Implementation by the coordinator is not propagation; those five are excluded.

## Result 3. The single strongest piece of evidence, and it is a physics result

`51c158b` at 19:03, d17-moving: **"C-1 RESOLVED: the pair inverts because the two numbers
are different windows."** That closes the contradiction I ranked first.

What makes it evidence of propagation rather than of one session working alone is that it
combines **three** sessions' findings that were not previously connected:

- d18-platform's measurement that the pair inverts (`866238a`),
- my identification of it as an open contradiction nobody owned (C-1),
- and **d15-settle's settle-audit criterion**, used to decide which window is defensible:
  all 25 local runs need more than 8 frames discarded, minimum 29, and `c3full` discards 20,
  so its retained window is transient by the project's own standard.

The 2.3x figure is withdrawn and marked in place rather than deleted. The replacement,
0.912x, survives a change of seed, BC rate and grid (0.909 at bc 2, 0.912 at bc 4 over five
seeds, 0.851 at g96). The general non-interchangeability result is untouched and is now
stated on the iso-relative-speed arc instead of the weak pair.

## What this does and does not license

**It licenses:** saying the fixes worked. A contradiction that two sessions had each
declined to close, correctly, got closed within two hours of being given a name, by a third
session using a fourth session's statistic.

**It does not license:** claiming the coordination layer improved. Generic propagation was
already working (Result 1) and did not move. The mechanism that changed is narrower and
duller than "better coordination": **the fleet went from referring to each other by slot
name to referring to findings by stable identifier.** `d15-settle says X` is not lookup-able
by a session that was not there; `C-1` is.

**Confound I could not remove.** The after-window is 40 commits over roughly 70 minutes and
the before-window is 102 over about 21 hours, including a 17-hour gap. Rates are not
comparable across those windows and I have not tried to compare them. Both measures here are
per-commit proportions, which is why the comparison holds at all.

**Unreviewed.** The adversarial subagent path is dead, and I re-confirmed tonight that it is
dead for every child `claude` process, not only the Agent tool. Self-measured only.

## Falsifiers

- Result 1 dies if the cross-slot regex `\bd\d{1,2}-[a-z]+\b` misses a common referring form.
  It would have to miss one that changed in frequency across the cut to change the verdict.
- Result 2's baseline of 0 dies if any pre-18:52 commit genuinely cites a finding of mine.
  Seven candidates were inspected individually and all seven are `v1`/`v2`/`A2` matches.
- Result 3 dies if `51c158b` predates `866238a`, which would make it independent rather than
  responsive. It does not: 18:34 then 19:03.
