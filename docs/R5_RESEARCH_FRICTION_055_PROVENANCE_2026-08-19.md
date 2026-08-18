# R5-D1 unit 64: RETRACTED IN FULL

Date 2026-08-19. Branch `claude/r5-research`.

> ## THIS UNIT IS WITHDRAWN. Five blocking issues, and the worst is a rule I have quoted to others.
>
> **I did not read the register before asserting a parameter claim.** CLAUDE.md's
> standing rule is explicit: "Before asserting any parameter, threshold, citation,
> mesh property, or milestone as fact, read
> `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`." I have cited that rule to
> siblings during this dispatch. I broke it, and everything below follows from that.
>
> Nothing in the original document should be used. It is replaced by this record,
> because how it failed is worth more than what it claimed.

---

## 1. My entire "new" finding was register G4a, twelve days old

Register `:270`, **G4a, dated 2026-08-07**, cites **the same external report
`65474f37`** I presented as a discovery, and states the same chain: Azhar
"**measured 0.55 themselves** with a spring balance on the rubber mat", cite Wong
"only to show the value falls inside a handbook range of 0.50 to 0.70", a "**two-hop
chain, terminating in a general-automotive handbook**", and the judgement that it is
"of lab rubber mat, not of submerged asphalt".

G4a even closes the loop I thought I was opening: "The canonical paper at
`paper/canonical_2026-08-02/conference_101719_1.tex:205` **already states exactly
this, independently**."

## 2. I used the exact framing the register warns against

Register `:272`, **G4b**:

> "**0.30 is REFUTED as a measurement and REAL as a convention. Do not collapse the
> two.** ... Anyone reading only the convention half **will try to resurrect 0.30 as
> best-sourced and will be wrong.**"

My document was titled "our floor friction is nearly double the flood literature's
convention" and its headline number was 1.83x against 0.30. **That is the failure
G4b names, described in advance.**

And **G4** at `:266` refutes my premise outright: "`mu_wet ~ 0.30` is **REFUTED** as a
wet-road value ... Model-scale measurements run **0.52 to 0.68**." **0.55 sits inside
the measured band.** G4b supplies comparanda my table omitted entirely: Shu et al.
2011 measured Ford Transit 0.39, Ford Focus 0.50, Volvo XC90 0.68.

## 3. The physics conclusion was backwards, and I verified that myself

I argued 16/17 SLIDE at 0.55 would survive 0.30, making the verdicts conservative.
**The one run that can move is the one I ignored.** `sweepV_g64_v0p5`, the single
STUCK verdict, measured from its own `metrics.csv`:

```
frames with |vx| >= 0.05 m/s : 8
last such frame  : 8    dx = 0.036268   vx = 0.054263
SLIDE needs dx >= 0.05  ->  short by 0.013732 m, 27.5% of threshold
max |dx| overall : 0.056779, reached after vx has fallen to ~0
```

SLIDE requires drift **and** speed simultaneously for 3 sustained frames
(`failure_modes.py:181-183`). This run misses **only** because it decelerates below
the speed gate before drift reaches 0.05 m. **Floor friction is what produces that
deceleration.** Lowering mu extends the window, so 0.30 pushes this run **toward**
SLIDE.

STUCK is the safe verdict. **So at the one run where friction can change the answer,
0.55 gives the safer result: anti-conservative, the exact opposite of what I wrote.**
I reasoned about the 16 that cannot move and silently dropped the 17th, which is the
lowest-velocity and most policy-relevant case.

## 4. Monotonicity does not hold in this solver anyway

**Engine: WARPMPM** (`sim_standing.py:10-12`), which my original never tagged.
`mpm_solver_warp.py:975` applies

```python
J_t = min(v_t_mag / denom_t, mu * J_n)
```

which **saturates**: once `mu*J_n` exceeds the tangential term, raising mu does
nothing. So "higher mu means harder sliding" is not even structurally true here.

And the project's only mu data, `data/mu_sweep_results.csv`, is **non-monotone**:
displacement rises 21.5% from mu 0.0 to 0.3, then falls 0.93% across 0.3 to 0.7.
(That sweep is **GENESIS/SPH** and varies *coupling* friction, not floor friction, so
it is suggestive rather than dispositive. Conflating the two engines is precisely the
risk here.)

## 5. Two claims of absence that were simply false

- **"Nobody has run it."** `data/mu_sweep_results.csv` exists, is in the paper, and
  `docs/CITATION_AUDIT_2026-07-30.md:204-206` already audits it.
- **"The 0.55-versus-0.3 comparison is made nowhere in docs/."**
  `paper/canonical_2026-08-02/conference_101719_1.tex:205` already says AR&R assumed
  0.3, that Shand et al. call it conservative, that the existing sweep "does not
  settle this, because it varied the coupling friction between vehicle and water, not
  the friction between vehicle and ground", and that the direct test is to **"rerun
  the sweep with floor friction set to 0.30 ... We name it here as the first thing to
  check."**

**The paper is deliberately agnostic on direction. I asserted a direction it declines
to claim.** That is a regression against the published text, not an addition to it.

## 6. Smaller errors, recorded

- **Toda et al. 2013 is not 0.6.** Register `:259`: **0.26 at 0 degrees, 0.57 at 90
  degrees.**
- **Keller and Mitsch year:** I wrote 1992 from unit 57's OpenAlex match; the repo
  says 1993 in 3 of 3 occurrences. Still unresolved against the primary source, and I
  should not have propagated either figure into a parameter argument.
- **Smith 2019** is ~0.78 in register G4, not the ~0.76 I quoted.
- **"690214: 0 files"** is a wrong measurement. There are 4 hits, all numeric
  coincidence inside a metrics value. Substantively absent; the count was wrong.
- **My repo counts (azhar 86, Wong 13) do not reproduce** on the same branch under
  either case setting, and I gave no command. Withdrawn.
- I cited `sim_standing.py:154` (the kwarg default) but not `:210-211` (the actual
  `add_plane` call).

## 7. What actually survives

**Almost nothing of mine.** The provenance chain is real but is register G4a's, not
my finding. The one thing I contributed that the register does not already hold is
negative and small: **SAE 690214 and Harned are substantively absent from this repo**,
so the chain's terminus is documented one hop short.

**And one thing worth more than the unit:** `sweepV_g64_v0p5` sits **0.013732 m**
from flipping STUCK to SLIDE, and the margin is friction-mediated. That is a real
sensitivity, it points the opposite way from my claim, and it belongs to **D4**.

## 8. Why this happened

I found a HIGH VALUE flag in the corpus subject index and went straight to the
artifact **without checking whether the register had already absorbed it**. The
register had, twelve days earlier, from the same report ID. Every subsequent error,
the framing G4b predicts, the backwards physics, the two false absences, followed
from starting in the wrong place.

**The rule exists because of exactly this, and I am the one who kept quoting it.**
