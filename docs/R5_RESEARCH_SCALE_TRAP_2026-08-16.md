# R5-D1 unit 9: the Elicit quote columns, and the model-scale trap quantified

Date 2026-08-16. Branch `claude/r5-research`. Closes a gap in my own
definition-of-done and generalises the row-7 scale problem from units 3 and 4.

---

## 1. A gap in my own work, now closed

My dispatch's definition of done (c) asked for "a table of every depth-velocity
threshold and friction coefficient the literature actually reports ... mined from
all 42 rows". Unit 1 mined columns `[08]` and `[09]`, the summary columns. It did
**not** mine columns `[15]` to `[20]`, which hold the supporting quotes and
reasoning behind each summary. Those are the evidence, and a summary can
under-report its own evidence.

Tested directly: of the 33 rows whose threshold summary reads "Not mentioned",
how many carry a unitted number in their supporting quotes?

```
rows with 'not mentioned' threshold summary but a unitted number in quotes : 3 / 33
rows with 'not mentioned' friction summary but a friction value in quotes  : 0 / 33
```

Hand-checking all three, because a regex hit is not a threshold:

- **Row 9** (`10.5194/PIAHS-373-143-2016`): FALSE POSITIVE of mine. The quotes
  give a dimensionless mobility parameter and a Froude-number curve, not a
  numeric depth-velocity threshold. The summary's "Not mentioned" is correct.
- **Row 13** (`10.1111/jfr3.12737`): FALSE POSITIVE of mine. The quotes describe
  the floating, sliding and toppling mechanisms qualitatively. No threshold.
- **Row 23** (`10.1016/j.rineng.2019.100032`): **GENUINE, the summary
  under-reports.** Verbatim from the quotes: "The buoyancy depth was noticed at
  depths greater than and equal to **0.055 m**" and "the range of water depths
  between 0.047 and 0.089 m, whereas for velocities, it was controlled to be in
  between 0.20 and 0.39 m/s".

So the corrected yield for the CSV is **10 of 42 rows carrying a threshold**, not
9, once the quote columns are mined. Friction is unchanged at 9 of 42: no
friction value hides in a quote column anywhere in the file.

**And row 23's recovered value passes a consistency check.** That paper is
Muzzamil Shah's 1:10 Perodua Viva. Scaling the buoyancy depth linearly,
`0.055 m x 10 = 0.55 m` full scale, which sits inside the 0.5 m (4WD) to 0.60 m
(row 5, float depth) band the full-scale literature reports. An independent
route, arriving in the right place.

## 2. The scale trap, quantified

Unit 3 caught row 7 being 1:24 rather than the remembered 1:10. Row 9's quotes
show the problem is far wider than two papers. Verbatim from row 9:

> The mobility parameter has been calculated for three experimental datasets
> (Shu et al., 2011, Xia et al., 2011, 2014) including seven different car models
> and densities and **three model scales (1 : 14, 1 : 18, 1 : 43)**.

Combined with what units 3 and 4 established, the flood-vehicle experimental
literature this project draws on spans **at least six scales**:

| model scale | source in this corpus | depth factor | velocity factor | **D x V factor** |
|---|---|---:|---:|---:|
| 1:1 | AR&R, Smith 2019, Nihei 2025 | 1 | 1.000 | **1.00** |
| 1:10 | Muzzamil Shah, Perodua Viva | 10 | 3.162 | **31.62** |
| 1:14 | Shu 2011 / Xia | 14 | 3.742 | **52.38** |
| 1:18 | Shu 2011 / Xia | 18 | 4.243 | **76.37** |
| 1:24 | Hamid Shah, die-cast | 24 | 4.899 | **117.58** |
| 1:43 | Shu 2011 / Xia | 43 | 6.557 | **281.97** |

Under Froude similitude, depth scales as the length ratio and velocity as its
square root, so the depth-velocity product scales as `lambda^1.5`. Factors
computed by me.

**The consequence, stated plainly.** A `D x V` threshold quoted from a 1:43 model
and one quoted from a 1:10 model differ by **8.9x** on scale alone, before any
physics. A 1:24 value differs from full scale by **117.6x**. The project's own
threshold table in unit 1 lists row 7's `0.0168 m2/s` beside AR&R's
`0.30 m2/s` and they are not on the same axis at all.

**Therefore: no depth-velocity threshold from this literature may be quoted
without its model scale.** That is a stronger rule than the one unit 3 gave for
row 7 alone, and it is the rule I would want in the paper's own threshold table.

## 2b. The rule needs one more distinction, or it misfires

Stating the scale is not sufficient, and applying `lambda^1.5` to any value
carrying a scale label would be wrong. Row 38, Azhar et al. 2026
(`10.1111/jfr3.70181`), shows why. Its abstract, READ DIRECTLY:

> The numerical model built with smoothed particle hydrodynamics (SPH) is first
> validated for its use in studying unsteady flows by comparing it with **1:14
> scale physical model results**.

The 1:14 is the scale of the **validation experiment**, not of the reported
threshold. Its reported `0.45 m2/s` is a full-scale-equivalent number: scaled up
as a raw model value it would be `0.45 x 14^1.5 = 23.6 m2/s`, which is absurd
against AR&R's 0.30 to 0.60 band. Contrast row 7, whose `0.0168 m2/s` is roughly
twenty times *below* AR&R and is therefore plainly a raw model reading.

So a threshold from this literature needs **two** labels, not one:

1. **the model scale** of the physical work, and
2. **the value basis**: is the printed number a raw model reading, a full-scale
   equivalent the authors already converted, or a criterion quoted from elsewhere?

Four distinct cases actually occur in these 42 rows: raw model values (rows 7 and
23), full-scale-equivalent values validated at model scale (rows 38, 39), full-
scale numerical work (rows 2, 37), and criteria quoted from AR&R by reviews (rows
5, 16, 35).

**Incidental verification.** The same abstract confirms a standing CLAUDE.md
claim at its source: "the hydrodynamic drag can increase by **40%-50%** in
unsteady flows". CLAUDE.md's "Unsteady flow raises drag 40 to 50 percent, Azhar
2026" is correct as written. Azhar 2026 is also SPH, which adds a fourth
particle-method paper to unit 7's list.

## 2c. The deliverable is rebuilt, not just flagged

`data/r5_citation_thresholds.tsv` now carries three new columns, `model_scale`,
`value_basis` and `basis_provenance`, with every entry tagged `R` for read at
source or `I` for inferred. **All 12 rows are mapped; zero UNKNOWN remain.**

| row | DOI | model scale | value basis |
|---|---|---|---|
| 2 | `10.1111/jfr3.12828` | full scale | full-scale numerical (I) |
| 5 | `10.1111/jfr3.12645` | n/a, secondary | full-scale criteria |
| **7** | `10.11113/JT.V80.11198` | **1:24** | **RAW MODEL VALUES** |
| 16 | `10.1111/jfr3.12262` | n/a, review | full-scale criteria |
| **23** | `10.1016/j.rineng.2019.100032` | **1:10** | **RAW MODEL VALUES** |
| 25 | `10.1016/j.rineng.2025.107189` | full scale | full-scale measured |
| 26 | `10.1007/s11069-013-0889-2` | unknown | full-scale equivalent (I) |
| 35 | `10.1111/jfr3.12551` | n/a, review | full-scale criteria |
| 37 | `10.3390/su151713262` | full scale | full-scale numerical |
| 38 | `10.1111/jfr3.70181` | 1:14 (validation only) | full-scale equivalent |
| 39 | `10.1111/jfr3.12885` | laboratory, ratio unstated | full-scale equivalent |
| 40 | `10.4271/961000` | n/a, ATV tyres | **not a vehicle-stability threshold** |

**Exactly 2 of 12 rows carry raw model-scale values**, rows 7 and 23. Those two
are the ones that must never be tabulated beside a full-scale number, and unit 1
did exactly that with row 7. Row 40 gets its own warning: it is ATV tyre friction
against surface anomalies, so its 1.89 is not a flooded-car coefficient and must
not sit in the same column as 0.30 or 0.55.

## 3. What I am not claiming

I am **not** offering scaled-up values as corrected thresholds. Froude similitude
governs the free-surface flow, but these are floating and sliding problems in
which mass and friction also matter, and:

- a die-cast model does not satisfy mass similitude, as unit 3 noted;
- Shah's 1:10 Perodua Viva is described as "ensuring similarity laws", which is a
  claim I have not checked against its methods section;
- row 9's own framing is that the mobility parameter exists precisely because raw
  thresholds do not transfer across scales and vehicle densities.

The defensible output is the negative one: **the scale must be stated, and values
at different scales must never be tabulated together.** The `lambda^1.5` column
above is there to show the size of the error, not to license a conversion.

## 4. Status and UNVERIFIED

1. The 1:14, 1:18 and 1:43 scales are READ DIRECTLY from row 9's quote column,
   which is itself quoting Shu 2011 and Xia 2011/2014. I have **not** opened
   those three papers to confirm the scales at source. Second-hand.
2. Whether Muzzamil Shah's 1:10 work satisfies mass similitude is unchecked.
3. The 0.55 m consistency check in section 1 assumes linear depth scaling and is
   a plausibility check, not a validation.
4. Rows 9 and 13 were my own regex false positives, hand-corrected. The quote
   columns of the other 30 "not mentioned" rows were scanned by the same regex,
   so a threshold phrased without a unit token would still be missed.

No project simulation number is asserted here. The scale factors are arithmetic
on stated model ratios.
