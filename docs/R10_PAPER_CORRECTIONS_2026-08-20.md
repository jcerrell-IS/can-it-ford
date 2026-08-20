# R10 paper corrections, verified 2026-08-20 by slot d23-overleaf

Every claim below is tagged `read-directly`, `inferred` or `relayed`. Nothing here is
carried from a summary without being re-read live.

---

## 0. Which file is the paper. Settled, `read-directly`.

Three candidates were in play. The Overleaf project holds **`conference_101719_1.tex` at
its root**, and nothing else.

| evidence | value |
|---|---|
| `git ls-remote` against `https://git.overleaf.com/6a5958d10484feadf65a934e`, run live 2026-08-20 | `refs/heads/main` = `6466dfa1c9d1adb9753bc5d48d885ab1eee16971` |
| local clone `/Users/josie/can-it-ford-paper` HEAD | the same `6466dfa`, dated 2026-07-31 23:55:54 +0000 |
| tracked files in that clone | 12, all at the root, figure paths therefore FLAT |
| `md5 conference_101719_1.tex` | `518332dc070faf2f8bf1bc18ff3ce9ad` |

**The Overleaf project has not moved since 2026-07-31**, and the local clone is current, so
it can be read as the live paper.

`paper/canonical_2026-08-02/conference_101719_1.tex` is **byte-identical** to it (same md5),
which is why R10 could read the submitted paper from there. That directory is **gitignored**
(`.gitignore:101`, re-derive rather than trust the line number) and therefore does **not
exist in any worktree**. The two other candidates are different documents and are not what
compiles:

| file | md5 | status |
|---|---|---|
| `paper/canonical_2026-08-02/conference_101719_1.tex` | `518332dc…` | the shipped paper, gitignored mirror |
| `paper/conference_101719.tex` | `1586461…` | not the shipped paper |
| `overleaf_sync/conference_101719.tex` | `d9b49da…` | not the shipped paper |

---

## 1. Ground clearance. Defect CONFIRMED, corrected.

`read-directly` from `docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md`, section B7c:
**"Measured native ground clearance: 0.1737 m."** The same section records the method (minimum
z of a central longitudinal strip excluding the wheels) and a validity check against a fake
flat underside (only 4.3 percent of strip vertices within 20 mm of the minimum, z standard
deviation 3.86 mm).

The tex said, verbatim, **"We did not measure ground clearance from the mesh."** That is false
and the measurement predates the 2026-08-02 snapshot by a week.

---

## 2. The class-match conclusion. Defect CONFIRMED, and it is INVERTED, not merely wrong.

`read-directly` from `vehicle_params.py`, the `AR_R_STABILITY_LIMITS` assignment:

| class | length | kerb weight | ground clearance |
|---|---|---|---|
| small_passenger | max 4.3 m | max 1250 kg | **max 0.12 m** |
| large_passenger | min 4.3 m | min 1250 kg | min 0.12 m |
| large_4wd | min 4.5 m | min 2000 kg | **min 0.22 m** |

The hull is 4.2826 m long with measured clearance 0.1737 m, and mass is an override on that
one geometry. `inferred`, by applying the table above to those measured values:

| class | length | kerb weight | clearance | axes |
|---|---|---|---|---|
| small_passenger (1100 kg) | PASS | PASS | **FAIL** 0.1737 > 0.12 | 2/3 |
| large_passenger (1609 kg) | **FAIL** 4.2826 < 4.3 | PASS | PASS | 2/3 |
| large_4wd (2337 kg) | **FAIL** 4.2826 < 4.5 | PASS | **FAIL** 0.1737 < 0.22 | 1/3 |

**No AR&R class is satisfied on all three axes.** The tex claimed "only the 1100 kg
configuration is a genuine class match", which names the one class that fails on the axis the
paper said it had not measured.

### A trap that nearly reversed this finding

`docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md` section B7c ends with the sentence **"large
passenger is the only class satisfied on all three"**, and its table shows large_passenger as
**3/3**. Read alone that contradicts the correction above.

It does not, and the reason is in a column labelled only `lam`, never defined in that
document. `inferred`, and arithmetically exact: `lam` is a uniform geometric scale factor.
4.2826 x 1.144 = 4.899 against the tabulated 4.9000, and 0.1737 x 1.144 = 0.19871 against the
tabulated 0.1987; likewise 4.2826 x 1.214 = 5.199 against 5.2000 and 0.1737 x 1.214 = 0.21087
against 0.2109. **Rows two and three of that table describe hulls scaled up by 14.4 and 21.4
percent. No such hull was ever simulated.** All 17 gated runs use the unscaled hull with a
mass override, which the tex itself states ("The override changes mass but cannot change the
hull").

So the 3/3 is real for a hypothetical scaled vehicle and irrelevant to the runs. Anyone
re-checking this from the reconciliation doc alone will reach the opposite conclusion, which
is why the mechanism is recorded here rather than the verdict alone.

### The verdict flips on the label, and the margin is 1.9 percent

`read-directly` from `data/all_runs_inventory.csv`, row `g64_m1100`: `realized_depth_m`
0.2944294473039918, `velocity_ms` 1.5, `label` `small_passenger`.

`inferred`: D x V = 0.4416441709559877 m2/s. Against the AR&R hazard limits read above:

- as small passenger, limit 0.30 m2/s, **NO-FORD**
- as large passenger, limit 0.45 m2/s, depth 0.2944 < 0.40 and velocity 1.5 < 3.0, **FORD**

The canonical run's L1 verdict therefore flips on a class label that no classifier computes.
`read-directly`: `vehicle_params.L1_verdict` takes `vehicle_class` as a defaulted string and
reads no length, weight or clearance; the inventory's `label` column assigns class by mass
alone. The margin below the large-passenger limit is 0.0084 m2/s, 1.9 percent.

---

## 3. The 0.78 friction value. Defect CONFIRMED, from two independent origins.

The tex attributed 0.78 to `\cite{shand2011arr}` via the phrase "their worst-case bed friction
against 0.78 for concrete". It is Smith, Modra and Felder's measurement.

**Origin 1**, `read-directly` from `citations/smith_modra_felder_2019_velocity_grounding.md`,
which states it was reviewed from the PDF page by page: velocity in Smith's stability curves
is derived from "a drag coefficient C_D = 1.38 measured separately on a 1:18 scale model
Toyota Yaris in a real flume, and **friction coefficients mu = 0.3 (worst case, sand or gravel
bed) or mu = 0.78 (wet or dry concrete)**".

**Origin 2**, `read-directly` from the full text of Azhar, Pauwels and Bui 2023, a separate
peer-reviewed paper, at `~/Zotero/storage/6Y7VPLP7/.zotero-ft-cache`: "**The coefficient of
friction adopted by Smith et al. (2017) was 0.78**, which was higher than the value of 0.55
adopted in this study."

These have genuinely separate origins: one is this project reading Smith's PDF, the other is
an unrelated research group reading Smith and saying so in print.

**Both endpoints of the shaded band belong to Smith.** The register's entry G4 in
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` already records that 0.30 is Smith's sand
and gravel worst case, so the paper's 0.30 has two separate justifications (AR&R adopted it as
an assumption, Smith measured it) and its 0.78 has exactly one, which is not AR&R.

---

## 4. The drag coefficient range "1.0 to 1.8". DEFECT NOT CONFIRMED. NO EDIT MADE.

This was dispatched as a defect to fix, with "1.0 to 1.8" to be replaced by "0.98 to 1.83".
**That edit was not made, and making it would have put an unsupported number into the paper.**

`read-directly` from the full text of Azhar, Pauwels and Bui 2023, same cache as above:

> "Smith et al. (2019) measured the drag force acting on a 1:18 scale model of a Toyota Yaris
> positioned perpendicular to the flow. They tested for both subcritical and supercritical
> flow regimes and **found CD to be randomly ranging between 1.0 and 1.8**."

The tex reads "inside the **1.0 to 1.8** range they report **across subcritical and
supercritical flow**". That is Azhar's sentence, near verbatim, and Azhar is a peer-reviewed
source that read Smith. The tex figure is therefore sourced, not invented.

Against that, the replacement value is weaker on every axis:

- `relayed` is R10's own tag on it. `docs/R10_FULL_CONTEXT_AUDIT_2026-08-19.md` records the
  0.98 to 1.83 figure as `relayed`, not read directly, and in the same breath says the source
  "is internally inconsistent on the ceiling" because Smith's Table 2 gives a subcritical
  ceiling of 1.86.
- The project's own page-by-page reading of Smith, the grounding note cited in section 3
  above, records **no drag-coefficient range at all**. It records a single C_D = 1.38.
- That grounding note **does** record "Supercritical flows: ... **Froude number 1.83 to
  4.16**". `inferred`: 1.83 is a Froude number in the only page-by-page reading of Smith this
  project holds, which is a live candidate explanation for how a 1.83 came to be reported as a
  drag-coefficient endpoint.

**Recommended, not applied:** cite Azhar alongside Smith for the range, since the wording and
both endpoints trace to Azhar's reading rather than to any text of Smith we have read. That is
a provenance improvement, not a correction, and it is left for Josie because it asserts an
origin rather than fixing a falsehood. The number itself should stay at 1.0 to 1.8 until
somebody reads Smith's Conclusions page directly and says which figure is on it.

`C_d = 1.38` itself is correct and correctly attributed: confirmed twice, by the grounding
note and by `docs/LIT_QUEUE_2026-07-30.md` ("average drag coefficient C_D = 1.38"), both about
Smith. Note that `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` reports Nihei et al. 2025
giving C_D = 1.38 +/- 0.18 for a different experiment; do not merge the two.

---

## 4b. A defect nobody dispatched: the paper's fallback lands on its least converged quantity

The tex closes its sweep paragraph with: "until it is placed on an independent empirical
footing **we report displacement magnitudes only**."

The refusal is well reasoned and is left intact: the L2 drift threshold has no empirical
footing, so declining to publish an agreement rate built on it is correct. **The problem is
the fallback.** Displacement magnitude is the one quantity in that block the project's own
data shows is not converged, and the paper reported it without saying so.

`read-directly`, recomputed live from `data/all_runs_inventory.csv` this session:

| mass | g48 | g64 | g96 | g48 to g64 | g64 to g96 |
|---|---:|---:|---:|---:|---:|
| 1100 kg | 0.350717 | 0.658537 | 0.268638 | **+87.8%** | **-59.2%** |
| 1609 kg | 0.256830 | 0.314076 | 0.155959 | **+22.3%** | **-50.3%** |
| 2337 kg | 0.187542 | 0.135559 | 0.089439 | **-27.7%** | **-34.0%** |

The first two rows reproduce CLAUDE.md ground-truth item 5 to the decimal, which is a check on
that item as much as on this one. **The third row is new here and it is the sharper fact: at
2337 kg the sequence is monotone and falls on both legs, so the sign of the resolution effect
is not even consistent across the three masses.** Item 5 records only the two non-monotone
rows, which understates the problem.

### The same number, two routes, and the gap depends on which one you divide by

`read-directly`, parsed live out of `renders/yaris_render_s1/_incoming/g64_m1100/rollout.npz`
this session. There is no numpy on this Mac, so `t.npy` was read by parsing the npy header and
unpacking the raw float32 block with `struct`; the header is `{'descr': '<f4',
'fortran_order': False, 'shape': (90, 3)}`.

| route | final displacement |
|---|---:|
| `summary.json` `final_disp_mag_m` | 0.658537 m |
| `rollout.npz`, recomputed as final $\|t - t_0\|$ | 0.637019 m |
| gap | 0.021518 m |

That gap is **3.268 percent of the summary figure and 3.378 percent of the rollout figure**.
CLAUDE.md item 5 quotes "a 3.4 percent gap", which is the rollout-denominator form. Both are
correct and they answer different questions, so the figure must never be quoted bare.

**This is an independent instance of tonight's recurring defect shape, reached from a
completely different quantity.** d12 and d21 found one force numerator divided by two
denominators. This is one displacement measured by two routes whose disagreement is itself
denominator-dependent. Separate origins entirely: theirs is a sphere validation scene, this is
the canonical vehicle run's own stored particle rollout.

### What is stable, and it is worth saying

`read-directly`, from the same rollout: `g64_m1100` first exceeds the 0.05 m drift detector at
**frame 3 of 90**, and every one of the nine runs in the block has a final magnitude above
0.05 m (the smallest is 0.089439 m). The drift verdict is therefore stable across the whole
block even though the magnitude behind it is not. CLAUDE.md's standing instruction, "cite the
verdict, never the displacement magnitude", is the right rule and the paper had inverted it.

`gates_both_scenarios.py` already computes both routes side by side and stores their
difference as `L2_measure_delta_m`, so the pipeline has known about this. That file is
**untracked and has no commit history** (`git ls-files --error-unmatch` errors, `git log`
returns nothing), exactly as CLAUDE.md warns, so it is evidence of intent rather than a
citable provenance.

### A held-fixed control on section 2's verdict flip

While checking this, `gates_both_scenarios.py` was found to compute `dxv_nominal` from the
**nominal** 0.30 m depth, not the realized 0.2944 m. That raises the obvious question of
whether section 2's verdict flip is an artifact of choosing realized over nominal depth. It is
not. `inferred`, computed both ways against the live limits:

| depth used | D x V | small passenger | large passenger | large 4WD |
|---|---:|---|---|---|
| nominal 0.30 m | 0.450000 | NO-FORD | FORD | FORD |
| realized 0.2944 m | 0.441644 | NO-FORD | FORD | FORD |

The flip is driven by the class label and survives either depth convention. Note the nominal
case sits exactly on the large-passenger limit of 0.45 and passes only because the comparison
in `L1_verdict` is a strict `>`; the realized case clears it by 1.9 percent. Same verdict,
different reasons, so quote the realized one.

---

## 5. The bibliography collision. The dispatched framing does not match the live files.

`read-directly`, all three bib files, 2026-08-20.

| file | entries | `alqadami2022` resolves to |
|---|---|---|
| Overleaf root `can_it_ford_references_IEEE.bib` (**the shipped bib**) | 15 | **no such entry, and no Al-Qadami entry at all** |
| `paper/can_it_ford_references_IEEE.bib` | 42 | `10.1111/jfr3.12828`, full Crossref metadata |
| `overleaf_sync/can_it_ford_references_IEEE.bib` | 21 | **no DOI field at all**; title is the literal string `{VERIFY: exact title}` |

The dispatched framing was that the same key resolves to `10.1111/jfr3.12828` in one bib and
`10.3390/su151713262` in the other. **It does not.** In `overleaf_sync` the string
`10.3390/su151713262` appears **only inside the entry's `note` field**, as an open question
("confirm which is the correct rollover-literature citation"), and the entry itself carries no
DOI. So the two bibs do not disagree about which work `alqadami2022` is; one of them declines
to say.

That is a different and arguably worse failure mode. If `overleaf_sync`'s bib ever compiled,
`\cite{alqadami2022}` would print the literal words **"VERIFY: exact title"** in the reference
list of a submitted paper, rather than pointing at the wrong paper.

There **is** a real duplicate-key problem, in `paper/`: `alqadami2022` and `alqadami2022moving`
are two keys for one work, both carrying `10.1111/jfr3.12828`. That file's own note already
says so and asks for them to be merged onto `alqadami2022moving`.

**Which bib is authoritative: the Overleaf root one, 15 entries.** It is what BibTeX actually
reads when the project builds, it is the only one whose keys the shipped tex's 14 `\cite` keys
resolve against, and it is on the branch that is the paper. Verified `read-directly` this
session: extracting the 14 distinct `\cite` keys from the corrected tex and comparing against
the 15 keys in that bib leaves **zero used-but-missing keys**. The other two files are working
drafts and neither should be pushed to Overleaf.

**Consequence for tonight:** none of the corrections in sections 1 to 3 touch the bibliography,
so they can go in without resolving any of this.

---

## 6. What was changed, and where it is

Six edits, all in `conference_101719_1.tex`, delivered as
`paper/r10_corrections_2026-08-20.patch`. Verified: each search string matched **exactly once**
before replacement; the patch applies cleanly to the Overleaf clone under `git apply --check`;
`$` counts are even and braces balanced on all three touched lines; no em-dash introduced; no
new `\cite` key introduced.

| id | line | change |
|---|---|---|
| A | 205 | "We did not measure ground clearance from the mesh" replaced by the 0.1737 m measurement and its validity check |
| B | 205 | the inverted class-match conclusion replaced by the three-axis result, plus the D x V verdict flip and its 1.9 percent margin |
| C | 147 | 0.78 reattributed from AR&R to Smith, Modra and Felder, with both band endpoints named as Smith's |
| D | 152 | figure caption now cites Smith for the 0.78 upper endpoint of the shaded band |
| E | 205 | the "one inside each of AR&R's three kerb-weight bounds" parenthetical now says that is a bound on kerb weight only, not class membership |
| F | 205 | the "displacement magnitudes only" fallback now carries the non-convergence figures, the two-route gap with both denominators, and the fact that the drift verdict is stable where the magnitude is not |

**NOT PUSHED.** The Overleaf remote shares no ancestor with `origin`, so a push overwrites the
project rather than merging into it. The patch is staged for review and waits on an explicit go
from Josie.

To apply once approved:

    git -C /Users/josie/can-it-ford-paper apply -p1 \
      /Users/josie/can-it-ford/.claude/worktrees/r9-overleaf/paper/r10_corrections_2026-08-20.patch

---

## 7. Unreviewed

The adversarial `physics-skeptic` path is dead fleet-wide. Nothing here has been through it.
Every number above is instead tagged with how it was obtained, and every one of them names a
file that can be re-read in one command.
