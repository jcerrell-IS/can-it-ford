# R5-D1 unit 20: Kramer 2016 read, sense A confirmed, and my unit-12 claim needs a qualifier

Date 2026-08-17. Branch `claude/r5-research`. Closes unit 19's UNVERIFIED #1,
which I flagged as load-bearing.

Three results. My unit-19 inference is confirmed at source; CLAUDE.md A-4 is
confirmed at source; and **my unit-12 statement that model-scale thresholds are
non-conservative was unqualified and is wrong as a general claim** because the
sign flips with failure mode.

---

## 1. Sense A confirmed at source

Unit 19 argued that Kramer 2016's "watertightness" means vehicle sealing, not
mesh topology, but rested that on A-4's characterisation plus the title. I found
the abstract through Semantic Scholar (Unpaywall reports it green OA via a UNSW
repository copy, `hdl.handle.net/1959.4/unsworks_55729`). Verbatim:

> experimental investigations on the stability of **two scaled watertight vehicle
> models** and of one **prototype passenger car** are conducted in a laboratory
> flume and a steel tank ... the prototype experiments indicate that **floating
> water depths are higher in prototype than in model scale, which is due to the
> use of a watertight vehicle model**.

"Watertight vehicle model" is a physically **sealed** scale model, contrasted
against a real car. That is sense A, unambiguously. Unit 19's load-bearing
inference is now READ DIRECTLY, and the whole two-senses argument stands on
evidence rather than on inference.

**CLAUDE.md A-4 is also confirmed at source.** It says watertightness assumptions
"materially shift flotation depth". Kramer measures exactly that shift and
attributes it to exactly that cause.

## 2. My unit-12 claim was unqualified, and the sign is mode-dependent

Unit 12 read Nihei 2025's small-car drifting abstract and concluded that
"model-scale thresholds are non-conservative". Set beside Kramer, that is too
broad. **The two point in opposite directions, and each is about a different
failure mode.**

| source | mode | finding | model bias |
|---|---|---|---|
| Nihei 2025, `10.2208/jscejj.24-16110` | **drifting / sliding** | prototype drifts at depth and velocity **smaller** than model experiments | model warns **too late**: NON-conservative |
| Kramer 2016, `10.1016/j.ijdrr.2016.04.003` | **floating** | "floating water depths are **higher** in prototype than in model scale" | model warns **too early**: CONSERVATIVE |

The reasoning is straightforward once both are on the table. A sealed model has
lower effective density than a real car, so it floats in less water: using it
gives a flotation threshold below the truth, which errs safe. Nihei's real car
slides at gentler flow than models suggest, so a model-derived sliding threshold
errs unsafe.

**So "model-scale thresholds are non-conservative" is true for sliding and false
for floating.** Unit 12 stated it without the qualifier, and that is corrected
there and here.

**A boundary D4 drew, and it is worth keeping (`7acb95f`).** This mode-dependent
finding is about **model-scale** experiments. Nihei's *other* 2025 paper, the
`rineng` full-scale sliding study (`10.1016/j.rineng.2025.107189`) that supplies
the 0.0250 / 0.0242 rolling-resistance figures, is **full-scale by its own
title**, so the "model-scale sliding results err unsafe" finding **does not apply
to it** and does not weaken it. D4 flagged that rather than leaving it as an
unexamined adjacency, and they are right: two of my own findings sit next to each
other and only one of them is about scale models.

**Why this matters here specifically:** our dominant published mode is SLIDE, 16
of 17 runs. That is the mode where model-derived thresholds err unsafe. The
qualifier does not soften the concern for this project, it sharpens where the
concern applies.

## 3. Our model is neither of Kramer's two cases

Kramer contrasts a **sealed scale model** against a **real permeable car**. Unit
19 established that our hull is a third thing: a homogeneous solid particle cloud
at a fixed effective density of 310.494 kg/m3
(`sim_standing.py:170-171`, register B5), set once at load.

Kramer's result is that the difference between sealed and permeable is
**measurable and material** for flotation depth. Where a fixed-density solid sits
relative to those two, and in which direction it biases a verdict, is a physics
question. It belongs to D4 and I have not attempted it. What unit 19 and this
unit jointly establish is that the question is **real and quantified in the
literature**, not hypothetical.

## 4. Provenance closed: the total-head criterion is Kramer's

Kramer's abstract ends:

> The recommended safety criteria for passenger cars and emergency vehicles are
> total heads of **hE = 0.3 m** and **hE = 0.6 m**, respectively.

That resolves two loose ends in my own earlier work:

- Unit 16 quoted the `Moving Rigid Body Free Surface Validation` catalog's
  reference [6] as proposing "total-head criteria of 0.3 m for passenger cars and
  0.6 m for emergency vehicles". **Reference [6] is Kramer 2016.**
- Elicit **row 35** lists "Emergency rescue vehicles: H+V^2/2g <= 0.6 m -
  Passenger vehicles: H+V^2/2g <= 0.3 m" among its extracted thresholds with no
  attribution. **That criterion is Kramer's total head**, `h + v^2/2g`.

And it is a fifth instance of the numeral trap: **0.3 m of total head** is a
third distinct quantity sharing the numeral with AR&R's 0.3 m still-water depth
and 0.3 m2/s depth-velocity product. Three different physical quantities, one
number, all for passenger cars. The rebuilt
`data/r5_citation_thresholds.tsv` carries units and basis; this is another reason
to use it rather than any prose table.

## 5. Status

Closed this unit: unit 19's UNVERIFIED #1 (Kramer's sense), and the attribution
of the total-head criterion.

UNVERIFIED:
1. I read Kramer's abstract, not the body. The scale ratios of the "two scaled
   watertight vehicle models" are not stated in the abstract, so Kramer's models
   are **not** in unit 9's scale table and should not be added without checking.
2. Nihei 2025's drifting comparison is against "previous model experiment
   results" that its abstract does not identify, so I cannot confirm the two
   studies' model baselines are comparable. The mode-dependence in section 2
   holds as a statement about each paper's own finding, not as a controlled
   comparison between them.
3. Whether a fixed 310.494 kg/m3 sits closer to Kramer's sealed model or his
   permeable prototype is unresolved and is D4's.
