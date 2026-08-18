# The Kramer 2021 archive, extracted in full: what survives, what is refined, what breaks

**Slot** d12-kramerdata. **Branch** `claude/r9-kramer-extract`, off `claude/r8-kramer`.
**Date** 2026-08-18. **Engine relevance:** none. Nothing here runs an engine. Every number is
a reduction of a published archive. No Genesis, no warpmpm, no GPU, no node hours.

**Every number in this document regenerates.** Unlike the document it audits, that sentence
is now true of the metadata as well as the time series, which is the point of the exercise.

```
V=<a python with numpy, openpyxl; uv venv /tmp/v && uv pip install --python /tmp/v/bin/python numpy pandas openpyxl scipy>
X=analysis/kramer_extract_numerical.py
$V $X --model-table --cost   # section 1, the sheet with cell addresses
$V $X --audit                # section 2, CODE_META against the sheet
$V $X --groups --envelope    # section 3, the grouping key result
$V $X --manifest             # section 4, all 58 series
$V $X --order                # section 5, RANS4 and RANS5
$V $X --sphere               # section 6, the workbook nobody opened
$V $X --descriptions         # section 7
$V $X --all --json           # everything, machine readable
$V $X --self-test            # section 11, proves every fail-loud guard fires
```

**Source.** `energies-14-00269-s001.zip`, sha256
`04c4d78d6987e4eec6c31d692d3c5cf5adea2580ffcfe50fbbd44e6589c7623f`, held at
`/Users/josie/can-it-ford-refs/2026-08-16/`, deliberately **outside** this public repo while
register E8 is open. Kramer, Andersen, Thomas, Ferri, Crowley, Stratigaki, Troch et al. 2021,
*Energies* **14**(2):269, doi `10.3390/en14020269`.

**Licence, verified primarily and not from a project file.** The dispatch told me to check
the licence file. **There is no licence file.** `unzip -Z1` on the archive returns zero
entries matching licen, copyright, terms or CC BY, and there is none anywhere under
`can-it-ford-refs/`. `PROVENANCE.txt` asserts CC BY 4.0 but it is a file this project wrote,
so it is not a primary source for its own claim. The status is confirmed from the article
PDF itself, which states: *"distributed under the terms and conditions of the Creative
Commons Attribution (CC BY) license (https://creativecommons.org/licenses/by/4.0/)"*. **CC BY
4.0 holds.** One trap for whoever checks this next: page 1 of the on-disk PDF is a DTU Orbit
cover sheet carrying DTU's repository boilerplate, including *"You may not further distribute
the material"*. That is the repository's terms for its own portal, not the article's licence,
and citing it would reverse the answer. Policy unchanged: derived statistics with attribution
go in this repo, **no Kramer series file does**.

---

## 0. The answers

1. **The premise I was dispatched on was false, and I checked before building on it.** The
   dispatch said 44 numerical entries and 4 descriptions "have never been extracted at all"
   and that everything in the prior slot's work "rests on the subset" of 28 experimental
   entries. It does not. `kramer_benchmark.py` reads all 31 numerical series at runtime.
   Section 4.
2. **But a real gap was underneath it, and it was worse than the stated one.** The one file
   that IS metadata rather than time series was read once by hand and **transcribed** into a
   literal. It is load bearing: it supplies the family split and the group split, which is
   the headline. Section 2.
3. **The transcription is sound. 43 of 44 fields match the sheet exactly.** This is a
   confirmation and I am reporting it with the same energy I would a refutation. The single
   difference is a silent typo correction. Section 2.
4. **The section 4 headline is GROUPING DEPENDENT and the document never says which key it
   used.** "Five of six groups agree to within 0.82 percent" and "the envelope is set at both
   ends by one group" are both TRUE under the author key and both FALSE under the institution
   key the sheet actually ships. Section 3. This is the most consequential finding here.
5. **The RANS4/RANS5 reversal is UNIVERSAL.** All six series reverse, all strictly
   monotone, experiment as-declared on all twelve repetitions. Section 5. **The follow-up
   test that tried to explain RANS4 as a pure column swap does NOT survive its own control
   and I have withdrawn it**, see section 5.1: it passed only against a band pooled across
   drop heights, and against its own drop height RANS4 misses on all three. The two codes
   still differ by a lot in degree, but "consistent with a column swap" was my sentence and
   it was wrong.
6. **An entire workbook of measured physical properties is opened by no committed code in this repo**, including a
   CAD-derived inertia tensor and a CoG, on a benchmark where this project has spent
   considerable effort establishing that estimated tensors must not be called measured.
   Section 6. Two of the three checks I first built on it are **downgraded** there: the
   Archimedes agreement is circular, and the added-mass cross-check is the same source read
   twice, not a second source.

---

## 1. The sheet, with cell addresses

`Numerical results/Description of numerical models.xlsx`, sheet `Sheet1`, headers on **row 4**,
columns C to H: `Model name@C4, Institution@D4, Author@E4, Software@F4, Description@G4,
Computational effort@H4`.

Three things bite a naive reader, and the extractor handles each explicitly rather than
silently:

**It has 13 rows for 11 models.** `UoPLam` and `UoPSST` carry Plymouth's internal names and
have no directory in the archive. Their Description cells are word-for-word those of RANS2
and RANS3, which is how the duplication is detected here: by description text, not by
guessing from names. `RANS3`'s own description cell G9 even reads *"Same as UoPLam, but with
SST turbulence model"*, referring to the other row by name, which is direct evidence the RANS
rows were copied from the UoP rows. The extractor returns all 13 and flags the two duplicate
groups, because "13 rows, 2 duplicates, 11 models" is itself the finding and a silent drop
would hide it.

**Ditto marks appear in two columns and do not span the same rows.**

| column | ditto rows | resolves to | value |
|---|---|---|---|
| Author | E14:E17 | **E13** | Morten Kramer |
| Software | F15:F17 | **F14** | WAMIT+Matlab/Simulink |

`F13` is `WAMIT+Matlab`, **without** Simulink. So a single resolution rule applied to both
columns, or a rule that walks to the top of the block, would give LPF1 through LPF4 the wrong
software string. The extractor walks up per column independently and records the source cell
of every resolution.

**There is a second, unrelated table on the same sheet** at G25:H31, titled `Computational
time` at G25, headers `Model type | Order of CPU hours needed for one case` at G27:H27. It is
read by nothing before this and gives the authors' own cost expectations by class:

| model type | order of CPU hours | cells |
|---|---|---|
| CFD 3D (possibly with symmetry along one or two planes) | ~3000 hours | G28:H28 |
| High order potential code | ~6 hours | G29:H29 |
| CFD 2D (using rotational symmetry) | ~1 hour | G30:H30 |
| Linear based | ~few seconds | G31:H31 |

Useful to this project directly: it is a published, author-stated cost scale for exactly the
family of methods the ladder work keeps having to justify node hours against.

---

## 2. The transcription audit: CONFIRMED, 43 of 44

`kramer_benchmark.CODE_META` (`simulation/r5_physics/kramer_benchmark.py:135`) is a hand
transcription. That it is a transcription was not previously recorded anywhere, and two
written claims say the opposite:

- `docs/R8_KRAMER_INTERCODE_2026-08-18.md:7` reads **"Every number in this document
  regenerates. Nothing is transcribed."**
- `simulation/r5_physics/kramer_benchmark.py:15` reads **"Nothing here is transcribed."**

Measured, not assumed: `/usr/bin/grep -c` against that module returns `openpyxl` 0, `pandas`
0, `zipfile` 0, `Readme` 0, `Solidworks` 0, `mass distribution` 0, `densities` 0. The single
`xlsx` hit is inside a comment. The module opens no spreadsheet at any point.

**Both sentences are false as written, and both are narrowly false.** They are true of every
number in the time-series reduction, which is what their authors meant and which is the great
majority of both artifacts. They are false of the metadata. The fix is a qualifier, not a
retraction, and the exact replacement text is in section 9.

**Now the audit result, which is the part that matters.** 44 fields checked across 11 codes
(institution, author, software, turbulence):

```
fields checked 44, findings 1 (1 DRIFT, 0 COSMETIC)
  [DRIFT] RANS5.institution
      in_code_meta   Budapest University of Technology and Economics
      in_sheet       Budapest Univeristy of Technology and Economics
      sheet_cell     D11
```

**One difference in 44 fields, and it is the transcription silently correcting a typo in the
source.** The archive misspells "Univeristy" at D11. Substantively this is nothing. As a
provenance matter it is worth one sentence: a transcription that silently normalises its
source cannot be diffed against it mechanically, and the only reason this one was catchable
is that the checker compares strings rather than meanings.

**Everything load bearing is confirmed.** In particular the turbulence classification, which
the extractor derives independently by keyword from the authors' own free-text Description
cells rather than from the transcription, agrees with `CODE_META` on all eleven:

| code | cell | classified from the authors' own words |
|---|---|---|
| RANS1 | G7 | LAMINAR (*"Laminar simulations"*) |
| RANS2 | G8 | LAMINAR (*"Run without a turbulence model"*) |
| RANS3 | G9 | SST |
| RANS4 | G10 | SST |
| RANS5 | G11 | LAMINAR (*"Laminar simulations."*) |
| FNPF1, LPF0 to LPF4 | G12 to G17 | n/a, potential flow |

**Three of the five "RANS" codes run no turbulence model. CONFIRMED**, independently of the
transcription, from the cells themselves.

---

## 3. THE GROUPING KEY, which is where the headline actually moves

`R8_KRAMER_INTERCODE_2026-08-18.md` section 4 states two things:

> Five of the six independent groups agree with the physical measurement to within 0.82
> percent [...] The entire `[-12.3, +12.8]` percent envelope is set at **both ends** by the
> sixth group's five potential-flow configurations, which are all by one author.

**The sheet ships two grouping keys. They give the same COUNT and a different MEMBERSHIP,
and the document never states which one it used.**

```
by author: 6 groups          by institution: 6 groups
  Morten Kramer                Aalborg University        LPF0, RANS1
    LPF0 LPF1 LPF2 LPF3 LPF4   Floating Power Plant      LPF1 LPF2 LPF3 LPF4
  ...                          ...
same count      True
same membership False
```

The period deviations are not recomputed here. They come from `kramer_benchmark.intercode()`,
which already reduces all 31 series with one statistic; re-deriving them in a second place
would create exactly the fork CLAUDE.md item 16 records for `gates.py`. Only the grouping is
redone:

| key | groups within 1 % | low end set by | high end set by | both ends one group |
|---|---|---|---|---|
| author | **5 of 6** | Morten Kramer | Morten Kramer | **True** |
| `CODE_META.group` | **5 of 6** | Kramer | Kramer | **True** |
| **institution, as shipped** | **4 of 6** | **Aalborg University** | **Floating Power Plant** | **False** |

Under the institution key the table reorders substantially:

| group | codes | n series | min % | max % | worst abs |
|---|---|---|---|---|---|
| Budapest Univeristy of Technology | RANS5 | 3 | -0.19 | 0.14 | 0.19 |
| National Renewable Energy Lab. | RANS4 | 3 | -0.30 | 0.13 | 0.30 |
| Chalmers University of technology | FNPF1 | 3 | -0.66 | 0.40 | 0.66 |
| Plymouth University | RANS2, RANS3 | 4 | -0.82 | -0.05 | 0.82 |
| **Aalborg University** | **LPF0, RANS1** | 6 | **-12.26** | 0.23 | **12.26** |
| **Floating Power Plant** | LPF1 to LPF4 | 12 | -10.27 | **12.83** | **12.83** |

**VERDICT: REFINED, not refuted, and the refinement needed a fact that was in neither the
module nor the document.** The author key is the defensible one for an independence claim,
and I can now say why from a primary source rather than by preference. The paper's own
affiliation list, page 2, gives **"Morten Bech Kramer 1,2"** where 1 is *Department of the
Built Environment, Aalborg University* and 2 is *Floating Power Plant (FPP)*. **Kramer holds
both affiliations.** Corroborated from a second artifact with a separate origin: the
`Kramer Sphere Cases` slide deck shipped in `Descriptions/` carries the byline **"Morten
Kramer, Floating Power Plant & Aalborg University"** (section 7). So the institution column is not recording two independent groups at
all; it is recording one person filing under each of his own two affiliations, and the author
key is the one that answers the question "how many independent results are there".

Two things follow, and the second is the useful one:

1. The claim **stands**, under the key that should be used.
2. It stood **for a reason nobody had written down**, and a reader who grouped by the
   Institution column exactly as the archive ships it would have got 4 of 6 and two different
   groups at the two ends, with nothing in either artifact to tell them they had used the
   wrong key. A conclusion that depends on an unstated choice is one refactor away from
   flipping. Section 9 gives the sentence to add.

Independent side result: `CODE_META`'s hand-assigned `group` field reproduces the author
partition **exactly**, same membership and same numbers to the digit. That is a second, and
this time genuinely independent, confirmation of the transcription.

---

## 4. The dispatch premise, tested and refuted

The dispatch: *"44 numerical entries plus 4 descriptions have never been extracted at all.
Everything above rests on the subset."*

**The arithmetic is right and the conclusion is wrong.** `unzip -Z1` gives 78 entries, which
is **63 files plus 15 directory entries**. By subtree: 44 numerical, 4 descriptions, 28
experimental, plus `Datafile/` and `Datafile/Readme.pdf`. So the counts reproduce exactly,
under a convention that counts directory entries. What they count is not what the sentence
claims:

| subtree | zip entries | of which directories | actual files |
|---|---|---|---|
| Numerical results | 44 | 12 | **31 series + 1 xlsx** |
| Descriptions | 4 | 1 | **3** |
| Experimental results | 28 | 1 | **27 series** |

And the 31 numerical series are not unextracted. `numerical_inventory()` at
`kramer_benchmark.py:242`, `intercode()` at `:579` and `wg_verdict()` at `:891` all walk the
tree and read every series on disk at runtime. The published envelope is computed over all of
them. Re-derived here from a walk of the tree, agreeing with that module:

```
numerical present 31, absent 2 ['RANS3/01D', 'RANS3/03D']
experimental      27
total series      58
numerical rows    951 to 19468, ratio 20.5x
codes with WG     ['RANS2', 'RANS3', 'RANS4', 'RANS5']  (10 series)
```

**CONFIRMED from the full set, all of them:** eleven codes; 31 series not 33; RANS3 at 05D
only; WG on four codes of eleven; the 20x row-count range that makes fixed-width peak picking
an artifact generator. The declared column sets are uniform within each form, so no series
disagrees with its neighbours about what its columns mean:

| form | declared columns | count |
|---|---|---|
| numerical, no gauges | `t [s], x3 [m]` | 21 |
| numerical, with gauges | `t [s], x3 [m], WG1 [m], WG2 [m], WG3 [m]` | 10 |
| experimental Raw | same five | 12 |
| experimental Normalized | `t/Te0, x3/H_{0,m}, WG1/H_{0,m}, WG2/H_{0,m}, WG3/H_{0,m}` | 12 |
| experimental CI95 | `t/Te0, x3/H_{0,m} (mean), Lower 95% CI bound, Upper 95% CI bound` | 3 |

One number I would have got wrong by assuming: **22 of the 31 numerical series are not
uniformly sampled in time**, including every RANS series and all of LPF1, LPF2 and LPF3. Only
9 are uniform. Any resampling step that assumes a fixed `dt` touches most of the archive.

---

## 5. RANS4 and RANS5: universal, and NOT the same case

The test needs no gauge positions, which is what makes it safe to run against an archive
whose gauge positions were measured off a drawing. A wave radiating from a compact source
spreads as 1/sqrt(r) in amplitude, so the time integral of eta^2 must **rise** toward the
sphere. Every WG file declares its columns as `WG1 WG2 WG3`, and Figure 8 puts WG1 farthest.
So the integral must rise from column WG1 to column WG3.

Two things this adds to the prior slot's check, which compared only the first and last gauge
and reported per code:

- **monotonicity**, so a series cannot pass with its middle gauge out of order
- **per series**, because a code-level verdict is an OR over its series and cannot separate
  "always reverses" from "sometimes reverses", and those have completely different
  consequences for a reader

| series | WG1 | WG2 | WG3 | WG3/WG1 | verdict |
|---|---|---|---|---|---|
| RANS2/01D | 4.1031e-06 | 6.3917e-06 | 1.2973e-05 | 3.162 | AS DECLARED |
| RANS2/03D | 3.2089e-05 | 4.9782e-05 | 1.0677e-04 | 3.327 | AS DECLARED |
| RANS2/05D | 7.0959e-05 | 1.0917e-04 | 2.2936e-04 | 3.232 | AS DECLARED |
| RANS3/05D | 6.3084e-05 | 9.8951e-05 | 2.1440e-04 | 3.399 | AS DECLARED |
| RANS4/01D | 1.3124e-05 | 6.4724e-06 | 4.0090e-06 | 0.305 | **REVERSED** |
| RANS4/03D | 1.0725e-04 | 5.3379e-05 | 3.4359e-05 | 0.320 | **REVERSED** |
| RANS4/05D | 1.9491e-04 | 1.0586e-04 | 6.7907e-05 | 0.348 | **REVERSED** |
| RANS5/01D | 9.8699e-06 | 3.7126e-06 | 1.9508e-06 | 0.198 | **REVERSED** |
| RANS5/03D | 9.5537e-05 | 3.7576e-05 | 2.0501e-05 | 0.215 | **REVERSED** |
| RANS5/05D | 2.1769e-04 | 8.5796e-05 | 4.6687e-05 | 0.214 | **REVERSED** |

**Every one of the ten is strictly monotone.** Not one is ambiguous or borderline.

**The experimental control**, which the prior work did not run and which is what makes the
above interpretable rather than merely odd: all twelve experimental repetitions are AS
DECLARED, with WG3/WG1 spanning **2.655 to 3.418**. So the declared order is not a convention
the archive is loose about. It is what the measurement does, on every repetition, at every
drop height.

**VERDICT on item 4 of my dispatch: the reversal is UNIVERSAL where it occurs.** RANS4
reverses on 3 of 3, RANS5 on 3 of 3, RANS2 on 0 of 3, RANS3 on 0 of 1. `codes_inconsistent`
is empty. That is the outcome that strengthens the case for contacting the authors, and it is
the less alarming of the two possibilities the dispatch named.

### 5.1 THE SWAP HYPOTHESIS, PROPOSED AND THEN WITHDRAWN BY ITS OWN CONTROL

I built a follow-up test and it broke. It is written up here in full rather than deleted,
because the way it broke is more useful than the test was.

**The idea.** If a series reverses *only* because its columns are written in the opposite
order, then undoing the swap must reproduce the measured radial gradient, not merely its
sign. So invert each ratio and ask whether it lands in the experimental band.

**The first version pooled all twelve repetitions** into one band, `[2.655, 3.418]`, and
gave a clean-looking answer: RANS4 inside on all three drops (3.274, 3.122, 2.870), RANS5
outside on all three. I wrote that up as "RANS4 is consistent with a pure column swap".

**Then I ran the control I should have run first.** The experimental ratio is not a single
population. It varies systematically with drop height:

| drop | experimental WG3/WG1, four repetitions | band |
|---|---|---|
| 01D | 2.655, 3.255, 3.016, 3.003 | [2.655, 3.255] |
| 03D | 3.302, 3.177, 3.373, 3.253 | [3.177, 3.373] |
| 05D | 3.312, 3.323, 3.328, 3.418 | **[3.312, 3.418]** |

Pooling imports 01D's scatter into the 05D comparison, and the entire extra width comes
from **one repetition**, `01D_rep1` at 2.655. Against its own drop height:

| series | 1/ratio | inside pooled band | inside its OWN drop's band | miss |
|---|---|---|---|---|
| RANS4/01D | 3.274 | yes | **no** | +0.7 % |
| RANS4/03D | 3.122 | yes | **no** | +1.7 % |
| RANS4/05D | 2.870 | yes | **no** | **+13.3 %** |
| RANS5/01D | 5.059 | no | no | +68.0 % |
| RANS5/03D | 4.660 | no | no | +40.5 % |
| RANS5/05D | 4.663 | no | no | +37.6 % |

(Miss is the distance outside, as a percentage of the lower edge of that drop's own band.)

**`swap_consistent_codes_drop_matched` is empty.** RANS4 fails all three. **"RANS4 is
consistent with a pure column swap" is WITHDRAWN.** The script now computes both comparators
and reports `comparator_changes_the_verdict: True`, so the failure cannot be quietly lost.

**What actually survives, stated as weakly as the evidence supports.** The two codes still
differ by a large factor in *degree*: RANS4 misses its own drop's band by 0.7, 1.7 and 13.3
percent, RANS5 by 37.6 to 68.0 percent. So RANS5 is far further from anything a relabelling
could reach than RANS4 is. That is a real and reproducible difference. It is **not** a
finding that RANS4's columns are merely swapped, and nobody should carry it forward as one.

**Two further limits on the test, which stand whatever the comparator.**

- **It is blind to WG2.** The ratio uses only the outermost and innermost gauge, so a full
  three-column reversal and a WG1/WG3 transposition are indistinguishable by it. The
  monotonicity column in section 5 does use WG2, and all ten series are strictly monotone,
  which is the only reason the three-column reading is preferred.
- **It cannot separate a labelling fault from a genuinely different wave field.** A code with
  different tank geometry can produce a different radial gradient for real physical reasons.
  RANS5's own description cell G11 says it is a 2D axisymmetric wedge of 20,000 cells with
  *"Tank floor extended to 1.8m depth to allow space for mesh motion"*. Water depth changes
  the dispersion relation and therefore the radial decay, so a genuinely different gradient
  is physically available to that configuration. **I have not tested this and it must not be
  reported as the explanation.**

**Consequence for the authors question.** The thing worth raising with Kramer et al is the
finding in section 5, which is solid: RANS4 and RANS5 ship gauge columns whose radial
ordering contradicts their own headers, universally, on every series, against an experiment
that is as-declared on all twelve repetitions. The swap diagnosis is mine and it did not
survive, so it should not be put to them as though it had.

---

## 6. The workbook no committed code in this repo has opened

`Descriptions/Details on sphere mass distribution and densities.xlsx`, three sheets: `Weights
and ballast`, `Densities`, `Inertia moments`. No committed code in this repo has ever opened
it. Selected values, each with its cell:

| quantity | value | cell |
|---|---|---|
| water density | **998.21** kg/m3 | D3 (*"fresh water at 20 degrees"*, measured 20 +/- 2 C) |
| aluminium | 2718.65 kg/m3 | D4 |
| stainless steel | 7905.447 kg/m3 | D5 |
| sphere, no ballast | 5368.10 g | E20 |
| **sphere, with ballast** | **7055.72 g** | E29 |
| **CoG z** | **-0.03479 m** | D5, `Inertia moments` |
| Ixx and Iyy | 0.098252280525 kg m2 | D7 |
| Izz | 0.07305192931 kg m2 | D8 |
| CAD volume | 2181782.94 mm3 | B24 |

Two small forks against `kramer_benchmark.py`, both immaterial and both worth recording so
nobody rediscovers them as bugs: the module uses `RHO_W = 998.2` against the sheet's 998.21
(0.001 percent) and `M_SPHERE = 7.056` against the sheet's 7.05572 (0.004 percent).

**Checks run against these values, with the two that do NOT hold up marked as such.**
Benchmark gravity 9.82 m/s2 is Table 1's.

1. **Archimedes. ARITHMETIC CORRECT, INFERENCE CIRCULAR, DOWNGRADED.** Displaced volume at
   equilibrium is m/rho = 0.00706837 m3 against half the sphere's 0.00706858 m3, **0.0030
   percent apart**. I first wrote this up as confirming half-draft flotation "independently
   from mass and density alone". **That is circular and the workbook says so on its own face.**
   The `Weights and ballast` sheet lists thirteen ballast blocks plus two washers and a nut,
   spanning **1.53 g to 1780.80 g, a factor of 1164**, carrying 1687.62 g of the 7055.72 g
   total. A graduated trim set with a 1.53 g finest step exists for exactly one purpose: to
   hit a target. The sphere floats at half draft because the authors ballasted it to, and an
   agreement at 0.0030 percent measures their success at that, not a law of physics.
   **What the check is still worth:** it is a genuine data-integrity check on the archive. A
   transcription error in either the mass or the density would break it, and it does not
   break. Cite it as that and never as a physics validation.
2. **Waterplane stiffness.** k = rho g pi R^2 = **692.892 N/m**. Undamped period with no
   added mass 0.6340 s; with a33/m = 0.5, 0.7765 s. The archive's Te0 = 0.7561 s sits
   between them. This one is arithmetic and stands.
3. **Added mass implied by Te0. STANDS AS A NUMBER, WITHDRAWN AS INDEPENDENT SUPPORT.**
   a33 = k (Te0/2pi)^2 - m gives **a33/m = 0.4221**, below the prior slot's measured 0.540
   at 01D and 0.870 at 05D. I first called this an independent corroboration of the Te0 trap
   from a different artifact. **It is not independent, and the project has a standing rule
   against exactly this.** Recomputing with `kramer_benchmark.py`'s own Table 1 constants
   (`RHO_W = 998.2`, `M_SPHERE = 7.056`) instead of the workbook's (998.21, 7.05572) gives
   **0.422007 against 0.422077, a relative difference of 0.017 percent**. The workbook is
   the same quantities to four or five significant figures, read from a second location in
   the same archive. That is one source cited twice.
   **What survives:** the number is right and the Te0 conclusion is right, but it rests on
   the prior slot's time-series measurement alone, which is where it always rested.

4. **The hollow-sphere trap.** The CAD volume is 0.00218178 m3, **15.4 percent** of the
   enclosing sphere's 0.01413717 m3. It is shell plus ballast, not displacement. Anyone
   reaching for "volume" in this workbook to get a density gets one about six times too high.

**Why this matters beyond the benchmark.** CLAUDE.md item 4 spends considerable space
establishing that `compact_sedan`'s inertia tensor is a box formula presented as if measured,
that no measured Yaris tensor exists, and that the correct response is not to wire an
estimate. Here is a benchmark case where the tensor genuinely is derived from a CAD model of
the built article, with a measured mass and a measured CoG offset, sitting unread. It is the
natural validation target for any future rigid-body inertia work, and nothing in this repo
currently points at it.

---

## 7. Descriptions and the CAD archive

| file | bytes |
|---|---|
| 3D CAD model in Solidworks.zip | 2,753,162 |
| Details on sphere mass distribution and densities.xlsx | 112,988 |
| Highly accurate experimental tests with a floating sphere - Kramer Sphere Cases.pdf | 11,854,853 |
| Datafile/Readme.pdf | 317,861 |

**`Readme.pdf` is now read, and it confirms two findings from a primary source.** Written by
"Morten Kramer and Jacob Andersen, 2021-01-05", it reproduces the paper's Appendix A. Two
sentences matter:

> Eleven numerical modelling approaches were performed on the test case, and thus eleven
> subdirectories are located under Numerical results.

> The three columns WG1, WG2, and WG3 [m] contain the surface elevation time series at three
> wave gauges locations [...] and are **included for the experimental results and for certain
> numerical results.**

So "eleven codes" and "WG on only some numerical results" are both the authors' own
statements, not inferences from the directory listing. It also records that the work was
carried out under the **IEA OES Wave Energy Converters Modelling Verification and Validation**
working group, which is the provenance for calling this a blind inter-code comparison.

**The Kramer Sphere Cases PDF is now read too, and it answers the gauge-radius question in
the negative.** It is a 27,523-character slide deck, *"Highly accurate experimental tests with
a floating sphere / Kramer Sphere Cases"*, by **"Morten Kramer, Floating Power Plant & Aalborg
University"**, presented at the **OES TASK 10 WEC Modelling Workshop 3, 14 to 15 November
2019, Amsterdam**.

**It contains no gauge-radius statement.** Searched for `1800`, `1200`, `600`, `1.8 m`,
`1.2 m`, `0.6 m`, `distance from` and `radial`: no hit. I had predicted in an earlier revision
of this document that this PDF was "where a gauge-radius statement would be if one exists".
**That prediction was wrong and the search is the reason I can say so.** Combined with the
sheet search in section 10, this now closes the question: **no artifact in the archive ships a
gauge radius.** Figure 8 of the paper, a drawing, is the only source there is, and the
prior slot's measured literal is the best available provenance rather than a shortcut.

**One sentence in it is worth more than the rest, and it is dated.** Under "Wave measurements":

> Wave measurements from 3 wave gauges are part of the dataset, but **the measurements have
> not yet been analysed.**

**That is November 2019 and it is partly superseded**, so it must not be quoted bare. The 2021
paper does use the gauge data, for reflection assessment (Section 3.5 and Figure 19). What the
paper does **not** do, and what my section 4 manifest shows it could not do, is compare
numerical gauge columns across codes: the WG columns exist on only 4 of the 11 codes, so a
cross-code gauge comparison is not available even in principle. **So there is a plausible route
by which a column-order error in a submitted numerical file reaches publication uncaught: no
published analysis ever compares a code's gauge columns against the experiment's.** Stated as a
route, not as the cause. I have not established that this is what happened.

The CAD zip holds **24 entries**, suffixes `.sldprt` and `.sldasm` only, listed but not
extracted. Cross-checking the workbook's `Name in Solidworks` column against that listing:
**14 of 22 found**. The misses are naming variants, not missing parts: the workbook writes
`O-ring` where the CAD has `O_ring.SLDPRT`, and `MarkerShort` where the CAD has
`ShortmarkerStick.SLDPRT` and `MarkerBall.SLDPRT`. **Reported as a partial match rather than
smoothed to a pass**, because the honest statement is that the two artifacts refer to the
same parts under different names, and a reader should not take "14 of 22" as evidence of
missing data.

---

## 8. Every prior conclusion, tested against the full set

| # | conclusion in `R8_KRAMER_INTERCODE_2026-08-18.md` | verdict against the full set |
|---|---|---|
| 1 | 11 codes, 31 series not 33, RANS3 at 05D only | **CONFIRMED** |
| 2 | 6 independent groups | **CONFIRMED as a count**, under any key |
| 3 | LPF0 to LPF4 all by one author via ditto marks | **CONFIRMED**, dittos resolve E14:E17 to E13, and Kramer's dual affiliation is confirmed from the paper |
| 4 | RANS2/RANS3 one code, turbulence switched | **CONFIRMED** from duplicate description text at G5/G8 and G6/G9 |
| 5 | 3 of 5 RANS codes laminar | **CONFIRMED** independently, by keyword on the authors' own cells |
| 6 | envelope -12.26 to +12.83 on 05D period | **CONFIRMED**, reproduces to the digit |
| 7 | 5 of 6 groups within 0.82 %, envelope set at both ends by one group | **REFINED. True under the author key, FALSE under the institution key the sheet ships (4 of 6, two different groups at the two ends). The document does not say which key it used.** |
| 8 | WG on 4 codes of 11 | **CONFIRMED**, 10 series |
| 9 | row counts span 20x, fixed-width peak picking is an artifact generator | **CONFIRMED**, 951 to 19468, and **22 of 31 are non-uniformly sampled**, which the prior work noted for RANS only |
| 10 | Te0 is a fixed normalising constant, not a measured period | **CONFIRMED.** The mass-workbook route gives a33/m = 0.4221, matching no measured drop, but it is NOT independent corroboration: see section 6, it re-reads the same quantities. |
| 11 | RANS4 and RANS5 apparently reverse their gauge columns | **CONFIRMED AND SHARPENED. Universal, 3 of 3 each, all strictly monotone, experiment as-declared on all 12 repetitions.** My own follow-up (the swap diagnosis) is WITHDRAWN by its own drop-matched control, section 5.1. |
| 12 | "Nothing is transcribed" | **REFUTED.** `CODE_META` is a hand transcription. Section 2. |
| 13 | Job B placement | **NOT RE-EXAMINED.** Withdrawn by `b6fe951`, stays withdrawn, out of my scope and not reopened. |

Nine confirmed, two refined, one refuted, one deliberately untouched. **None of the
prior slot's conclusions was overturned by the full set.** The one thing this unit
overturned is a claim I made myself tonight, section 5.1.

---

## 9. The two sentences, and the sentence that should be added

**These edits are OUTSIDE my declared write scope** (`analysis/kramer_extract_numerical.py`
and this file). I have not made them. Exact text so that whoever owns those files can apply
them in one step.

`docs/R8_KRAMER_INTERCODE_2026-08-18.md:7`, currently *"Every number in this document
regenerates. Nothing is transcribed."* Replace with:

> **Every number in this document regenerates.** No time-series number is transcribed. The
> one exception is the model metadata in `CODE_META` (institution, author, software,
> turbulence family), which was read once from `Description of numerical models.xlsx` and
> transcribed. It is audited against the sheet at runtime by
> `analysis/kramer_extract_numerical.py --audit`, which reports 43 of 44 fields matching
> exactly.

`simulation/r5_physics/kramer_benchmark.py:15`, currently *"Nothing here is transcribed."*
Replace with:

> Nothing in the time-series reduction is transcribed. `CODE_META` below IS a transcription
> of `Description of numerical models.xlsx`; run `analysis/kramer_extract_numerical.py
> --audit` to diff it against the sheet.

And the sentence section 4 of that document is missing, which is the one I would prioritise:

> Grouping is by **author**, which is what `CODE_META.group` encodes. The Institution column
> the sheet ships gives a different partition with the same count, under which this table
> reads 4 of 6 rather than 5 of 6 and the two ends of the envelope fall in two different
> groups. Author is the right key because the paper's affiliation list gives Morten Kramer as
> `1,2`, Aalborg University and Floating Power Plant, so the institution split separates one
> person from himself rather than separating independent results.

---

## 11. THE SELF-AUDIT RULE APPLIED, AND IT CAUGHT ME TWICE

The coordinator's standing rule for this unit: *an extractor that opens the wrong sheet and
finds no rows must not report "no such series". Assert on zero rows, loudly, per series.*

**I probed my own committed script for that defect before adding any guard, and found it in
my most prominent claim.** Pointing `radial_order()` at an empty directory:

```
radial_order() RETURNED NORMALLY. It did not raise.
  n series analysed                     : 0
  codes_reversed_on_every_series        : []
  codes_inconsistent                    : []
  reversal_is_universal_where_it_occurs : True
```

**A headline verdict produced from zero data, and nothing in the output distinguished it from
a real result.** `audit_code_meta()` had the same shape, returning `NO SUBSTANTIVE DRIFT`
after checking zero fields, which would have made the `CODE_META` audit, the whole point of
this unit, unfalsifiable. `cost_classes()` returned a silent empty.

**What changed.** An `ExtractionError` that is caught nowhere, `_require`, `_require_count`
and `_require_nonempty`, and an `EXPECTED` block recording the archive's own counts (13 sheet
rows, 11 models, 31 numerical series, 27 experimental, 10 WG series, 12 experimental
repetitions, 3 densities, 4 cost entries, 24 CAD entries). Per series, `radial_order()` now
requires nonzero rows, nonzero samples at `t >= 0`, and strictly positive eta^2 integrals,
because the ratio divides by those and a zero column would have produced an `inf` verdict
rather than an error. The headline field is now `"UNDEFINED, no code in this set reverses"`
when no code reverses, instead of `True`.

**And the guard immediately caught a second defect, this one already committed and already in
this document.** On the real archive, `--all` failed with:

```
ExtractionError: inertia label 'Ixx and Iyy' not found.
```

The sheet merges `B7:B11` for the words "Inertia moments", so on row 7 the first populated
cell is `B7` and the label sits in `C7`. My parser scanned only the first populated cell of
each row, **skipped that row entirely, and dropped `Ixx and Iyy` from its output while still
reporting the other six inertia entries and looking complete.** Section 6's table quotes
`Ixx and Iyy = 0.098252280525 kg m2`, and until this fix **that number came from a scratch
probe, not from the committed script.** The value was right. It did not regenerate, which is
the one property this document claims for every number in it. Parser fixed to scan every cell
in the row; it now extracts from `D7` and matches.

**Proof the guards work, because an assertion nobody has seen fail is decoration.**
`--self-test` breaks one input per case and requires an `ExtractionError`:

| case | result |
|---|---|
| `radial_order` on an empty numerical tree | fires: expected 10, found 0 |
| `series_manifest` on an empty numerical tree | fires: expected 31, found 0 |
| `model_table` with the header row moved | fires: names the missing headers |
| `model_table` with zero data rows | fires: expected 13, found 0 |
| `cost_classes` with no second table | fires: "is EMPTY" |
| `audit_code_meta` with `CODE_META` empty | fires: "checked ZERO fields" |

**6 of 6 fire, 6 of 6 message-match, `--self-test` exits 0.** It exits 1 if any guard stops
firing, so this cannot silently rot.

**The transferable form.** The rule that catches this is not "add assertions". It is that a
check must be able to report *"I could not evaluate this"*, and that state must not be
representable as a pass. Both of my false passes came from a boolean derived from an empty
collection: `not []` is `True`, and `all(...)` over nothing is `True`. **Any verdict computed
as a negation or an `all()` over a collection that could be empty is a false pass waiting to
happen**, and both of mine were exactly that.

---

## 10. Review status and what is not verified

### ADVERSARIAL REVIEW WAS NOT AVAILABLE. THESE CLAIMS ARE UNREVIEWED BY A SECOND PARTY.

The `physics-skeptic` subagent was invoked twice and **failed both times** with
`Agent terminated early due to an API error: There's an issue with the selected model
(deepseek-ai/DeepSeek-V4-Flash:deepinfra)`, once on its own definition and once with an
explicit `opus` override. A general-purpose adversarial reviewer was then launched as a
substitute and **failed with the identical error**. Subagent review is broken in this session,
not merely unavailable for this agent type. **No second party has checked anything below.**

**So I ran the attacks against myself instead, and wrote out the prompts I would have sent.**
Three landed, and all three were against my own claims:

| attack | target | outcome |
|---|---|---|
| pooled versus drop-matched band | the swap hypothesis | **BROKE IT**, section 5.1, claim withdrawn |
| was the ballast tuned | the Archimedes check | **BROKE THE INFERENCE**, section 6 check 1, downgraded to a data-integrity check |
| same source read twice | the a33 cross-check | **BROKE THE INDEPENDENCE CLAIM**, section 6 check 3, downgraded |

Self-attack is not a substitute for review and I am not presenting it as one. It found three
defects, which is evidence the claims needed review, not evidence they no longer do. **The
highest-value thing a reviewer could still do is attack section 3**, the grouping result,
which is the one load-bearing claim in this document that nothing has yet been thrown at.

Every number above is reported with the command that regenerates it.

**Registered upstream.** This document's `CODE_META` finding is **row B3** of
`docs/R9_DISCREPANCY_REGISTER_2026-08-19.md`. The coordinator has also corrected its own
outward report, which had described the six-groups attribution as "derived"; it is
transcribed, and the audit in section 2 is what makes it checkable.

**Self-checks that passed.**

- ditto resolution verified by inspection against the printed cells: Author E14:E17 to E13,
  Software F15:F17 to F14, and F13 confirmed to differ from F14
- the duplicate-row detection finds exactly the two pairs the prior slot found, by a
  different route (description text rather than name)
- `envelope_by_grouping` under the `code_meta_group` key reproduces the prior slot's section
  4 table to the digit, which is a regression test on my regrouping code
- the radial-order test reproduces the prior slot's per-code verdicts before adding
  monotonicity and the per-series split
- Archimedes check independently lands the sphere at half draft to 0.0030 percent
- both `--all` and `--all --json` exit 0, and every subcommand exits 0 individually
- `--self-test` exits 0 with 6 of 6 guards firing and message-matching (section 11)
- the `Ixx and Iyy` value in section 6 now regenerates from the committed script rather
  than from a scratch probe, which is what the guard exposed

**What is NOT verified.**

- **The RANS5 depth hypothesis is untested** and is written above as a hypothesis. Do not
  promote it.
- **Gauge radii remain measured off a drawing, and that is now known to be unavoidable.**
  `kramer_benchmark.py:1060` carries 1.800, 1.200, 0.600 m sourced from Figure 8. I checked
  both routes per my dispatch: **no sheet ships a gauge radius column, and neither PDF states
  one** (section 7). The dispatch's phrase "measure them from the sheet as
  shipped" describes something that does not exist, and the prior slot's "provenance by
  spreadsheet" refers to code authorship, a different quantity. A value read off a printed
  figure carries a reading uncertainty that nothing in the pipeline currently propagates.
  **None of my results depend on it**: the radial-order test uses ordering only and no radii.
- **Both PDFs are now read** and quoted in section 7. What remains genuinely unread in the
  archive is only the CAD geometry itself.
- **The CAD parts are listed, not opened.** No geometry is read from `.sldprt`.
- **I did not re-derive the period deviations.** They come from `kramer_benchmark.intercode()`
  by import, deliberately, to avoid forking the statistic. If that reduction is wrong, my
  section 3 tables inherit the error. What I re-derived independently is the grouping, the
  radial order, the sheet metadata and the sphere physics.
- **The 0.3 percent uncertainty qualifier** is inherited from `PROVENANCE.txt` and was not
  re-checked here.
