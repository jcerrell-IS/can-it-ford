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

---

# Second measurement, 23:50 BST: deliberate relaying. Same method, so the windows compare.

Between the first measurement and this one the coordinator relayed findings between slots
deliberately: Wallstedt and Zhao to d21, Quinlan to d11, the mesh search to d13, the realism
ranking to d17, and d11's own correction back out to d21 and to a board Josie reads. This
measures whether that changed anything, using the identical method and regex.

## The rate did not move. This is a null and it is the honest headline.

| window | span | commits | with a cross-slot reference | proportion |
|---|---|---|---|---|
| W1 pre-readout | wave start to 18:52 | 102 | 41 | **0.402** |
| W2 post-readout | 18:52 to 20:12 | 43 | 20 | **0.465** |
| W3 deliberate relay | 20:12 to 23:50 | 22 | 9 | **0.409** |

    W1 -> W2   z = +0.70
    W2 -> W3   z = -0.43
    W1 -> W3   z = +0.06

**W3 sits on top of W1.** Deliberate relaying did not raise the rate at which sessions
reference each other, and the small W2 bump did not survive. z = +0.06 across the whole
evening is as close to no effect as this measure can produce.

## But the rate is the wrong test, and the right one says four of six relays landed

Rate measures whether sessions talk about each other. It cannot see whether a specific
relayed item was used. Testing each relay against its named recipient's own commits in W3:

| relay | recipient | landed? | evidence |
|---|---|---|---|
| Wallstedt (`Wal07`) | d21-jobb | **YES** | `d826c8a`, tested and partly refuted |
| d11's correction | d21-jobb | **YES** | `d826c8a`, 2 of 3 commits |
| Quinlan | d11-accessor | **YES** | `f673c45`, `c692b21`, cited with full reference, Computers & Fluids 177:33-45, 2018 |
| mesh search | d13-renders | **YES** | `cdcc4a0`, "Read the deep search Simulation Ready Vehicle Mesh Assets directly" |
| Zhao locking / F-bar | d21-jobb | no trace | the work exists but on `add-ci-checks` (`754af7f`), not on d21's branch |
| realism ranking | d17-moving | no trace | 0 of 3 commits |

**A false negative of my own, recorded because it is the round's signature.** My first pass
scored the Wallstedt relay as 0 of 3. It landed; d21 cites the paper as `Wal07`, not by
author surname, and my regex only matched the surname. The corrected pattern found it. A
search that cannot match returns zero, and a zero from it is not an absence, which is the
rule this project already has and which I broke while measuring compliance with it.

## The finding that matters is fidelity, not delivery

Delivery worked, 4 of 6. **Fidelity did not.** Two of the relayed claims about Wallstedt and
Guilkey did not survive the recipient reading the paper, and both were widenings:

- **"For a body held fixed the projection error becomes a constant systematic bias rather
  than noise" is not in the paper.** The paper says accuracy "is strongly dependent on
  particle density and location", and its section 2 carries the opposite emphasis. It would
  not have applied here anyway: the body is fixed, the water particles are not. Withdrawn.
- **The plateau's "O(h)" scaling is not a stated result.** The plateau is real and was quoted
  correctly; its scaling was read off Figure 10 by eye, while the paper's own analytic
  reference is Vshivkov 1996 whose grid term is h^2. It is grid-set, never O(h).

**The chain, which is the structural point.** The first claim originated in a PDF-reading
subagent's own "Application to a Fixed Rigid Body" *reasoning* section, not in the paper's
text. It then went to the coordinator, who passed it to two sessions and to a board Josie
reads. That is **paper, subagent reasoning, coordinator, recipients**: three removes, and the
break happened at the first one, where a subagent's inference was read as the paper's
finding.

**Both were caught by d21-jobb reading the primary source instead of accepting the relay**
(`d826c8a`, 23:42), and the coordinator then owned both in `ac0f0d8` at 23:48, before this
document was written. Credit where it is due: the correction did not need an auditor.

## What the two measurements together license

**Relaying works as a delivery mechanism and failed as a fidelity mechanism.** Four of six
items reached their recipient; two of the claims carried were wider than their source. The
value in W3 came from the recipient **distrusting** the relay and going to the paper, not
from the relay being right.

That inverts the obvious lesson. The instruction should not be "relay more"; the rate shows
relaying more does not move anything. It should be **carry the scope with the claim, name the
remove it came from, and expect the recipient to check it.** A relay that says "Wal07 says X"
and a relay that says "a subagent reading Wal07 inferred X" are different objects, and only
the second one warns the recipient what to verify.

## Unchanged from the first measurement

Generic cross-slot propagation was already working at 40 percent before any intervention and
remains there. Nothing in either measurement supports the claim that the coordination layer
improved. What improved, once, was that a named finding got closed (C-1). What improved
again, tonight, is that a wrong relayed claim got caught in under two hours.

**Unreviewed.** Every child `claude` process on this machine is still dead, so no adversarial
pass was possible. Self-measured only.

---

# Third measurement, 2026-08-20 02:05. The null became a decline.

The second measurement closed W3 at 23:50 with 22 commits. W3 now holds 85. Same method,
same regex, same cut points, so all three windows remain comparable.

| window | span | commits | cross-slot ref | proportion |
|---|---|---|---|---|
| W1 pre-readout | wave start to 18:52 | 102 | 41 | 0.402 |
| W2 post-readout | 18:52 to 20:12 | 45 | 22 | 0.489 |
| W3 deliberate relay | 20:12 to 02:05 | **85** | 26 | **0.306** |

    W1 -> W3   z = -1.36   (was +0.06 when W3 held 22 commits)
    W2 -> W3   z = -2.06

**Cross-slot referencing did not improve under deliberate relaying. It fell.** W2 to W3 is
-2.06 sigma, which is a real move by any ordinary reading and still below the 3 sigma bar this
project uses for a physics claim. The +0.06 I reported at 23:50 was a small-sample artifact of
a 22-commit window, and I am recording that rather than quietly replacing it: **my own second
measurement was underpowered and I published it without saying so.**

## The confound I cannot remove, and it reframes what this metric can answer

**A hub lowers spoke-to-spoke traffic by construction.** If the coordinator relays d15's
statistic to d17 rather than d17 finding it, d17's commit cites the finding and need never
name d15. The intervention and the metric therefore push in opposite directions: successful
relaying *reduces* the need for slots to reference each other.

So the honest statement is not "relaying made propagation worse". It is:

> **Slot-to-slot referencing fell during the deliberate-relay era. That is consistent both
> with relaying failing and with relaying working by centralising, and this measurement
> cannot separate them.**

What it does rule out is the encouraging reading. Nothing here supports "the coordination
layer improved", which is the third measurement in a row to reach that conclusion by a
different route.

## The five refuted relays, verified individually

The coordinator reports five relayed claims that receiving sessions refuted. All five located
and read:

| # | relayed claim | what the paper said | caught by |
|---|---|---|---|
| 1 | Wal07: a fixed body's projection error is a **constant systematic bias** | **Not in the paper.** Its section 2 carries the opposite emphasis | d21 `d826c8a` |
| 2 | Wal07: the plateau scales as **O(h)** | Real and quoted correctly, but `O(h)` was read off Figure 10 by eye; the paper's own analytic reference is h^2 | d21 `d826c8a` |
| 3 | Ami15: ~10 percent above analytic **with the boundary treatment named as the cause** | Half holds. **Purely SPH**, its background grid explicitly "non-computational", for neighbour searching only. Failed on three independent scope grounds, any one sufficient | d21 `aa20be2` |
| 4 | the wall-artefact paper, cited for the P-2 mechanism | "Does not support the claim it was relayed for." The mechanism is real and quoted correctly; three things in the paper stop it applying | d22 `27f0996` |
| 5 | a Smith Cd range for the paper | This project's page-by-page reading of Smith **records no Cd range at all** | `82640de` |

**The coordinator's directional claim holds: five of five leaned toward the stronger version.**
But the mechanism is sharper than distortion, and this is the finding:

> **In four of the five, the quotation was accurate and the SCOPE was dropped.**

Nobody exaggerated a number. A claim was carried with its source's confidence and without its
source's boundary conditions, and the boundary condition is what decided every case. d21
reached the identical conclusion independently and wrote it before I measured it: "All three
had the direction right and the specificity wrong."

## The architectural finding: the fix belongs to the receiver, not the sender

The coordinator proposes that the durable fix is d21's `CANDIDATE_PAPER_SCOPE_TEST.md` rather
than any instruction to itself. **The evidence supports that, and for a reason stronger than
modesty.**

1. **The sender cannot know which scope dimension will matter.** Ami15 failed on
   discretisation, on coupling scheme and on regime, any one sufficient. Which one bites
   depends on what the receiver is doing with it, which the sender does not hold.
2. **Care did not prevent it.** The coordinator self-corrected within an hour on the first
   two, tagged Ami15 as relayed, and still went five for five. An instruction to be more
   careful is an instruction that was already being followed.
3. **The receiver holds the use case**, so only the receiver can test relevance rather than
   truth. Every one of the five was true about its paper and wrong about ours.

d21's five questions (discretisation, boundary or coupling scheme, regime, quantity, evidence
strength) are a receiver-side test, they carry a worked negative example so they are
falsifiable, and the rule attached to them is the right shape: **pass all five to cite as a
mechanism; passing some makes it context, not evidence.**

**The one thing I would add.** The test needs a companion on the sender side that is a
labelling convention, not a discipline: state the remove. "Wal07 says X", "a subagent reading
Wal07 inferred X" and "X, relayed, unverified" are three different objects, and only the last
two tell the receiver which of the five questions to run first. The coordinator already did
this for Ami15 and it worked: d21 knew to read it.

## Three findings closed

- **C-17, skill-drift blindness in the preflight: FIXED.** With a detail worth keeping: the
  first fix compared `wc -l`, and a three-line file differing only in its middle line compares
  equal. Replaced with a content hash. **Length is not identity**, which is the same class as
  reach-versus-cited and lineage-versus-mergeability elsewhere in this round.
- **C-3, stale register rows: CLOSED**, A2 retracted in place rather than deleted.
- **C-2, the dead reviewer: CONFIRMED DEAD FOR A SECOND, INDEPENDENT REASON.** The model pin
  was the first. The account has now hit a **weekly** limit, resetting 2026-08-21 20:00, which
  killed a fourth review attempt mid-sentence. Two independent causes means fixing the model
  pin alone would not have restored review. **Nothing in this round has been adversarially
  reviewed, and nothing can be until 2026-08-21.**
