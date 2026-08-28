# ROUND 3, D4 REGISTER-RECONCILE

Read `ROUND3_SHARED.md` first. You own the register and this round hands you
four inbound items plus one re-run. You are the only session that edits
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`.

Your point about relay loss is taken and acted on: my relay dropped a
containment qualifier, D2's dropped its own caveat, and both were recoverable
only from source commit bodies. Every item below carries its own qualifier
inline so you do not have to go fetch it.

## 1. The mu = 0.55 consolidation. You own the entry.

Six sessions reached this from six directions with no owner. The full statement
is in shared section 3; do not re-derive it. Write ONE register entry covering:

- the regime table and where 0.55 sits in it (D2);
- that 0.3 is Bonham & Hattersley's 1967 assumption carried forward, not an ARR
  measurement, which you established from the PDF;
- that 0.55 is Azhar, Pauwels & Bui (2023)'s own spring-balance measurement of
  their experimental rubber mat, citing Wong, *Theory of Ground Vehicles*,
  chaining to a 1969 GM tyre brake-force study (D11, corroborated at 22:39
  against artifact 65474f37's own TL;DR, readable at
  `/Users/josie/Claude/reu/compass_artifact_wf-65474f37-*.md`);
- that resolution-dependence is itself friction-dependent, so register J15's
  flip must carry its mu (D5);
- that the moving scene uses COLLIDER_FRICTION 0.4, a fourth live value (D9);
- D2's caveat verbatim, as the entry's own guard: analogous in direction and
  magnitude, not the same quantity, and no claim may say 0.55 "is" a measured
  tyre friction.

State the direction plainly: 0.55 biases away from a slide verdict, so it is
conservative for the 16 SLIDE verdicts and optimistic for the Silverado's flip
into STUCK.

D2, D5, D6, D9 and D11 will each send you a one-paragraph confirm-or-correct on
their own line only. Do not wait for all five to write the entry; mark any
unconfirmed line as such.

## 2. CLAUDE.md carries a wrong citation year. Record it, do not fix it.

D7 established that **Isik and He is 2023**, Computational Particle Mechanics
10(3):503-517, not 2022. The project CLAUDE.md's research-integration section
currently reads "Artificial sound speed can qualitatively flip a rigid-body
outcome, Isik and He 2022".

Record the correction in the register with D7's volume/issue/page evidence.
**Do not edit CLAUDE.md.** A session editing the shared standing rules is the
2026-08-07 breach pattern, and CLAUDE.md is on nobody's ownership list. Flag in
your report that it needs a single-owner edit and name it as an open item for
Josie.

## 3. P-2 may not be commensurable across vehicles. This affects a published item.

D5 found that the P-2 gate's geometric baseline is already **0.0905 to 0.1041**,
so the 0.10 limit sits *inside* the baseline spread. D5 also found that every
matched-dx run fails P-2, and that the one corner with clean P-2 containment is
a SLIDE corner.

CLAUDE.md item 7 publishes "seven of the 17 runs fail gate P-2" and names them.
If the gate's threshold sits inside its own geometric baseline, that failure
list is partly measuring hull geometry rather than water ingress. Verify D5's
baseline numbers against the source yourself, then record whichever way it
falls. Do not soften item 7 without a live measurement.

## 4. Re-run register_integrity.py after D8 patches it

D8 now owns the checker (shared section 2) and will apply its four-point patch
plus extend the probe to the readable mirrors. Your definition of done runs that
checker, which is why nobody wanted to change it mid-reconciliation. Sequence:
D8 applies, D8 tells you, you re-run, and you report whether your reconciliation
numbers move. Until it lands, treat a research-artifact count of 0 as a broken
probe, not evidence.

D11's measurement for your baseline: the tool moved from "10 research-artifact,
1 unresolved" to "0 research-artifact, 11 unresolved" with the register file
unchanged, and only 185968e0 was genuinely unresolved in both runs.

## Skills and state

Call `provenance-audit` for items 2 and 3. Run `physics-skeptic` before
finalising any number that enters the register. Five commits unpushed, one
docs/ file, held pending Josie's per-branch check; do not re-ask each turn.
Vista queue empty at 641 SU, LS6 unreachable, neither needed here.
