# R5-D1 unit 64: our floor friction is nearly double the flood literature's convention

Date 2026-08-19. Branch `claude/r5-research`.
**Section 3 is a claim about verdict direction and is UNREVIEWED pending
physics-skeptic.** Sections 1 and 2 are citation provenance and are not.

The corpus subject index flags one artifact HIGH VALUE: a citation-provenance audit
of **mu = 0.55 in Azhar, Pauwels and Bui (2023)**. That is the same number as
`floor_friction=0.55` in `sim_standing.py:154`, the default for all 17 canonical runs.

---

## 1. What the project already knows, and I am not restating as new

The provenance is **not** unknown here. `docs/LIT_QUEUE_2026-07-30.md:333` already
asks whether Azhar's 0.55 is "a physical Coulomb coefficient or a solver parameter"
and answers **"Physical"**, quoting the rubber-mat sentence. Measured repo-wide:
`azhar` 86 files, `Wong` 13, `Theory of Ground Vehicles` 8, `0.50 to 0.70` 6.

## 2. What is new: the terminus, and the number it is measured against

**The chain, per the audit:**

| hop | source | status |
|---|---|---|
| 0 | Azhar 2023, `10.1111/jfr3.12885` | **MEASURED**, spring balance on their own lab **rubber mat** |
| 1 | Wong, *Theory of Ground Vehicles* (2008) | handbook range **0.50-0.70** peak, wet **asphalt** |
| terminus | **SAE 690214**, Harned, Johnston and Scharpf (1969), GM tyre brake-force testing | primary, **general automotive, not flood** |

Azhar's own words, quoted in the audit: *"a rubber mat has been used as a
representative of the road surface with a wet coefficient of friction of 0.55."*
So 0.55 is a genuine primary measurement **of a laboratory rubber mat**, not of
submerged asphalt.

**The terminus is absent from this repo:** `690214` **0 files**, `Harned` **0 files**,
against `Wong` 13. So the chain is documented for one hop and stops there.

**And here is the number nobody has written down next to ours.** The flood-vehicle
stability literature does not use 0.55. It overwhelmingly uses **0.3**, chosen
deliberately as conservative:

| study | mu |
|---|---|
| Bonham and Hattersley 1967 | **0.3** (measured range 0.3-0.5) |
| Gordon and Stone 1973 | **0.3** |
| Keller and Mitsch 1992 | **0.3** |
| **Shand, Cox, Blacka and Smith 2011 (AR&R Project 10)** | **0.3** |
| Toda et al. 2013 | 0.6 |
| Smith, Modra and Felder 2019 | measured ~0.76; WRL 2017/07 used 0.78 |
| Azhar 2023 | **0.55** |
| published range across the field | **~0.25 to 0.78** |

Shand et al. verbatim, via the audit: *"While the assumed coefficient of friction of
mu = 0.3 is likely conservative, the present lack of suitable data and wide range of
road surfaces and tyre tread conditions prohibits the refinement of the
coefficient."*

**Our 0.55 is 1.83x the value underpinning the very AR&R curves the project compares
its verdicts against.** Measured in `docs/`: the 0.55-versus-0.3 comparison **is not
made anywhere**.

## 3. UNREVIEWED: which way this cuts

**I believe it cuts in the project's favour, and I am flagging it rather than
asserting it**, because it is a claim about verdict direction and my dispatch
requires physics-skeptic before I finalise one.

The reasoning: friction resists sliding, so a **higher** mu makes sliding **harder**.
Our runs use 0.55 and still return **16 SLIDE of 17**. At the literature's 0.3, the
resisting force would be lower, so sliding should be at least as easy. **A SLIDE
verdict obtained at 0.55 would therefore not be overturned by adopting 0.3**, which
would make the published verdicts conservative with respect to this parameter.

**Three reasons I will not state that as established:**

1. **Our 0.55 is not a tyre-road coefficient.** The vehicle is a rigid particle cloud
   resting on a floor plane; there are no tyres and no four contact patches. It is an
   analogue of tyre-road friction, not the same quantity.
2. **The comparison is not one-dimensional.** Buoyancy reduces normal force, and the
   17 runs already fail gate P-2 in 7 cases, so the contact state is not clean.
3. **Nobody has run it.** A mu = 0.3 control is a one-parameter re-run and would
   settle the direction by measurement rather than argument. That is D4's call, not
   mine.

## 4. Status

UNVERIFIED:
1. **Section 3 is UNREVIEWED.** physics-skeptic has not seen it at the time of
   writing.
2. **I have not read Azhar 2023, Wong, or SAE 690214.** Section 2 is the corpus
   audit's reporting, and its quotations are its own. It is one document, and unit
   40 is a standing reminder that a single corpus document can be wrong.
3. The `mu` values in the table are the audit's, cross-checked only against my own
   Elicit extraction, which independently recorded 0.55 measured, 0.3 assumed,
   0.52-0.62, 0.76 and 0.25/0.75 (unit 51's enumeration). **That is partial
   corroboration from a different source, not confirmation of every row.**
4. Repo counts are for the **main checkout on `claude/add-ci-checks`** (unit 63).
5. Whether a mu = 0.3 control is worth GPU time is D4's and Josie's judgement.
