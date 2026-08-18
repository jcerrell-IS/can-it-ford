# Kramer 2021 inter-code comparison: eleven published codes on one benchmark

**Slot** d9-kramer. **Branch** `claude/r8-kramer`, off `claude/r5-physics`.
**Date** 2026-08-18. **Engine relevance:** none of this runs an engine. Every number below
is a reduction of published time series plus, where stated, a reading of the pinned
`warpmpm` wrapper's own source. No Genesis, no GPU, no node hours.

**Every number in this document regenerates.** Nothing is transcribed.

```
V=<a python with numpy; provision with: uv venv /tmp/v && uv pip install --python /tmp/v/bin/python numpy>
K=simulation/r5_physics/kramer_benchmark.py
$V $K                       # experiment, sections 2 and 6
$V $K --intercode           # section 4, the eleven codes
$V $K --place               # section 6, Job B against the envelope
$V $K --wg-verdict --json   # section 8, the radiated-energy budget
$V $K --reflection 0.5402   # section 7, windows at the measured added mass
```

**Source data.** `energies-14-00269-s001.zip`, sha256
`04c4d78d6987e4eec6c31d692d3c5cf5adea2580ffcfe50fbbd44e6589c7623f`, held at
`/Users/josie/can-it-ford-refs/2026-08-16/`, deliberately **outside** this public repo
while register E8 is open. Kramer, Andersen, Thomas, Ferri, Crowley, Stratigaki, Troch
et al. 2021, *Energies* **14**(2):269, doi `10.3390/en14020269`, Gold OA under CC BY 4.0.
CC BY permits redistribution; permission is not obligation, so derived statistics with
attribution appear here and **no Kramer series file enters the repo**.

---

## 0. The five answers

1. **Eleven codes, thirty-one series, unbalanced, and SIX independent groups.** RANS3 ships
   `05D` only. And eleven series are not eleven independent results: LPF0 through LPF4 are
   five configurations by one author, the paper's own first author, and RANS2/RANS3 are one
   Plymouth code with the turbulence model switched. Section 2.
2. **Job B's canonical +50.06 percent is an OUTLIER, not inside the published scatter.** It
   falls outside the full eleven-code envelope on both available attributions and is 15 to
   22 times the worst deviation of every independent group except one. **Two qualifications
   belong beside that sentence every time it is stated, never the headline alone:** on the
   more forgiving isotropic-radius attribution it is **1.03x LPF0**, essentially tied with
   the single code the paper itself says to use with care at large amplitude; and the
   **+18.05 point refinement floor is INSIDE the envelope** while still 6.6x worst-RANS.
3. **The added-mass estimate is good where the project actually runs and bad at the large
   drop.** Measured `a33/m` is 0.540 at 01D against the hardcoded 0.5, and 0.870 at 05D.
4. **A planned configuration does not deliver the reflection window it was designed
   around.** `sphere_heave.py`'s docstring understates its own sensitivity by about two,
   because two of its three windows scale as `1/T_n^2`. Section 7, which exists as its own
   section because the consequence is a scene-sizing decision and not a wording matter.
5. **WG1-3 can separate radiation from viscous damping, on four codes of eleven, to tens of
   percent and not better.** 70 to 76 percent of the body's lost energy is accounted for as
   radiated waves, leaving **24 to 30 percent** non-radiated, with no resolvable trend
   across drop height. Section 8.

**And two things nobody asked for.** Two of the four WG-carrying codes appear to ship their
gauge columns in reversed radial order (section 10). And the single most transferable thing
in this document is a mistake I made and caught (section 9).

## 1. What the archive actually contains

`git grep -I -l "FNPF"` across every local branch head returned zero before today, so the
numerical half of this archive had never been opened in this project.

| subtree | entries | state before 2026-08-18 |
|---|---|---|
| `Datafile/Experimental results` | 28 (27 series + dir) | extracted |
| `Datafile/Numerical results` | 44 (31 series + 11 dirs + xlsx + dir) | **never extracted** |
| `Datafile/Descriptions` | 4 (3 files + dir) | **never extracted** |
| `Datafile/Readme.pdf` | 1 | |

**The design is unbalanced and the imbalance is one code.**

```
FNPF1  01D 03D 05D      LPF3   01D 03D 05D      RANS3  ..  ..  05D   <- 05D ONLY
LPF0   01D 03D 05D      LPF4   01D 03D 05D      RANS4  01D 03D 05D
LPF1   01D 03D 05D      RANS1  01D 03D 05D      RANS5  01D 03D 05D
LPF2   01D 03D 05D      RANS2  01D 03D 05D
```

Thirty-one series, not thirty-three. Measured by `numerical_inventory()`, which walks the
directory rather than asserting a shape. RANS3 is reported as absent in the 01D and 03D
rows rather than silently dropped, because dropping it silently would have made those two
rows look like the 05D row.

**The records are not commensurate.** Row counts run 951 to 19,468 over 6.0 to 10.0 s, a
**20x range in sample density**, and the RANS records are not uniformly spaced in time
(RANS3's first three stamps are 0.000000, 0.005677, 0.006884). Section 2 explains why that
dictated the shape of the statistic.

---

## 2. Who actually wrote the eleven codes

Until this unit, the fidelity families in this document came from **directory names**. That
is provenance by folder. `Datafile/Numerical results/Description of numerical models.xlsx`
is Appendix B's source and it contradicts the folders in three places.

**The archive's own naming is inconsistent with itself.** The spreadsheet holds thirteen
rows for eleven models: it calls the potential-flow code **NLPF1** where the directory says
**FNPF1**, and it carries two extra rows, **UoPLam** and **UoPSST**, with no directory at
all, whose descriptions are word for word those of RANS2 and RANS3. Those are Plymouth's
internal names for the same two submissions. Thirteen rows, two duplicates, eleven models.

| code | alias in xlsx | group | institution | software | turbulence |
|---|---|---|---|---|---|
| FNPF1 | **NLPF1** | Chalmers | Chalmers University of Technology | SHIPFLOW-Motions 6 | n/a, potential flow |
| LPF0 | | **Kramer** | Aalborg University | WAMIT+Matlab | n/a, potential flow |
| LPF1 | | **Kramer** | Floating Power Plant | WAMIT+Matlab/Simulink | n/a, potential flow |
| LPF2 | | **Kramer** | Floating Power Plant | ditto | n/a, potential flow |
| LPF3 | | **Kramer** | Floating Power Plant | ditto | n/a, potential flow |
| LPF4 | | **Kramer** | Floating Power Plant | ditto | n/a, potential flow |
| RANS1 | | Aalborg-CFD | Aalborg University | OpenFOAM-v1912 | **LAMINAR, none** |
| RANS2 | **UoPLam** | Plymouth | Plymouth University | OpenFOAM 5.0 | **LAMINAR, none** |
| RANS3 | **UoPSST** | Plymouth | Plymouth University | OpenFOAM 5.0 | k-omega SST |
| RANS4 | | NREL | National Renewable Energy Lab. | STAR-CCM+ 13.06 | k-omega SST, y+ ~ 30 |
| RANS5 | | Budapest | Budapest Univ. of Technology and Economics | OpenFOAM 7 | **LAMINAR, none** |

**Three things the directory names hide.**

* **Three of the five "RANS" codes run no turbulence model at all.** RANS1, RANS2 and RANS5
  are laminar. "RANS" is the archive's family label, not a statement that a
  Reynolds-averaged closure was used in each.
* **RANS2 and RANS3 are one code in two configurations**, same institution, same solver,
  same mesh, differing only by the turbulence model. The paper uses them as exactly that
  controlled pair (p.23: "An increased accuracy from inclusion of a turbulence model
  (k-omega-SST) can be seen by comparing the RANS2 and RANS3 models"). They are not two
  independent results and must not be counted as two.
* **LPF0 through LPF4 are all by one author**, carried by ditto marks in the spreadsheet's
  Author column, and that author is the paper's own first author. Five of the eleven series
  come from one person, and section 4 shows they are **both ends of the entire inter-code
  envelope**.

**Two configuration details that matter to section 8 and section 10.**

* **RANS5 is a 2D axisymmetric wedge**, one slice of the sphere, **20,000 cells total, run
  on a single laptop core**, and its **tank floor is extended to 1.8 m** against the
  experiment's 0.900 m. Its wave field is represented on one radial ray by construction.
* **RANS4 is the only submission with damping zones**, 2 m at inlet and outlet, where
  RANS1, RANS2 and RANS3 all state perfectly reflective walls.

Encoded as `CODE_META` and `GROUPS`, so `FAMILY` is now derived from the spreadsheet rather
than from a directory-name prefix.

---

## 3. The shared statistic

A statistic applied to the codes but not to the experiment is not a comparison, so the
same function, `reduce_series()`, produces every row in this document: the four
experimental repeats and all thirty-one code series go through the identical code path.

**Damped period.** Unchanged from the module's pre-existing convention: linearly
interpolated zero crossings about the settled level, successive crossing intervals doubled.

**The refactor is non-destructive, and that is checked mechanically rather than by eye:**

```
git show HEAD:simulation/r5_physics/kramer_benchmark.py > /tmp/kb_old.py
diff <(head -17 <($V /tmp/kb_old.py)) <(head -17 <($V simulation/r5_physics/kramer_benchmark.py))
```

Both arms exit 0 and both produce non-empty output (844 and 1254 bytes), so the comparison
distinguishes "equal" from "could not evaluate". The diff is **additions only**: two new
lines appear and **not one of the fifteen lines the old version emitted changes**. Every
experimental number the module published before today reproduces to the printed digit.

**Decay envelope, new today.** The module had `damped_periods()` and `ci95_halfwidth()`
and no envelope or decrement statistic of any kind, so this had to be written.

> **Why the extrema are bracketed by zero crossings.** A peak picked with any fixed-width
> window resolves a densely sampled code's extremum more sharply than a sparse one's.
> The sparse records here are the potential-flow ones and the dense ones are the RANS
> ones, so that artefact would have landed as a clean **FNPF/LPF-versus-RANS damping
> trend**. It would have looked like physics. It would have been the row count. Every
> extremum is therefore bracketed between two interpolated zero crossings, which the
> signal defines and the grid does not, and refined by an exact quadratic through the
> three samples nearest the bracket's argmax.

The `t = 0` release peak is deliberately excluded: it is not bracketed by two crossings,
and it is the imposed drop height rather than a response.

**Experiment, reduced.** Six extrema, three periods.

| drop | H0 | first damped period [s] | decay rate [1/s] | log dec/cycle | zeta | envelope r2 | implied a33/m |
|---|---|---|---|---|---|---|---|
| 01D | 30 mm | 0.7869 [0.7865, 0.7876] | 0.8310 +/- 0.0018 | 0.6315 | 0.1000 | 0.9998 | 0.540 |
| 03D | 90 mm | 0.8093 [0.8088, 0.8099] | 0.8014 +/- 0.0004 | 0.6130 | 0.0971 | 0.9998 | 0.629 |
| 05D | 150 mm | 0.8671 [0.8658, 0.8687] | 0.7548 +/- 0.0020 | 0.5885 | 0.0933 | 0.9984 | 0.870 |

Two things worth keeping. The single-exponential envelope fits at `r2 >= 0.998`, so the
statistic is a good description of the window rather than a forced fit. And the
**four-repeat reproducibility on the decay rate is 0.05 to 0.26 percent**, which is what
makes the inter-code spreads in section 3 interpretable at all.

**The release heights are not the nominal ones and the four repeats scatter.** Measured
releases average 29.124, 89.086 and 150.129 mm against Table 4's stated four-repetition
means of 29.16, 89.18 and 150.06 mm, agreeing to better than 0.1 mm. But the individual
01D repeats span 27.720 to 31.236 mm, a 3.5 mm spread on a 30 mm drop. That is consistent
with Table 4's own 0.8 mm standard uncertainty (a ~1.5 mm sample sigma over four repeats),
and it is why the paper normalises each repetition by its own measured drop height. **All
eleven codes released from exactly the nominal H0.** Absolute-millimetre comparisons carry
that difference and normalised ones do not; both columns are given in section 3.

On period the difference is negligible and quantified: the measured `dT/dH0` between 01D
and 03D is 0.367 s/m, so a 0.78 mm release difference moves the first damped period by
0.29 ms, **0.036 percent of it**.

---

## 4. All eleven codes, one statistic

`T1` is the first damped period, `dT1%` its deviation from the four-repeat experimental
mean, `dtrough` the first-trough deviation in absolute mm, `dnorm` the same deviation
after normalising each series by its own release amplitude (the paper's convention).

### 01D, H0 = 30 mm, 10 codes, RANS3 absent

| code | family | T1 [s] | dT1 % | decay [1/s] | dsig % | a33/m | trough [mm] | dtrough [mm] | dnorm %H0 | WG |
|---|---|---|---|---|---|---|---|---|---|---|
| FNPF1 | FNPF | 0.7859 | -0.13 | 0.8069 | -2.89 | 0.536 | 25.744 | +0.814 | +0.39 | |
| LPF0 | LPF | 0.7609 | -3.31 | 0.7005 | -15.70 | 0.440 | 23.152 | -1.777 | -8.15 | |
| LPF1 | LPF | 0.7781 | -1.12 | 0.7989 | -3.87 | 0.506 | 25.903 | +0.974 | +0.73 | |
| LPF2 | LPF | 0.7813 | -0.71 | 0.8010 | -3.61 | 0.518 | 25.872 | +0.942 | +0.63 | |
| LPF3 | LPF | 0.7870 | +0.02 | 0.8018 | -3.51 | 0.541 | 26.302 | +1.373 | +2.06 | |
| LPF4 | LPF | 0.7915 | +0.58 | 0.7859 | -5.43 | 0.558 | 26.378 | +1.449 | +2.32 | |
| RANS1 | RANS | 0.7844 | -0.32 | 0.8049 | -3.14 | 0.530 | 25.627 | +0.698 | -0.10 | |
| RANS2 | RANS | 0.7840 | -0.37 | 0.7737 | -6.90 | 0.529 | 25.928 | +0.999 | +0.81 | y |
| RANS4 | RANS | 0.7845 | -0.30 | 0.7743 | -6.82 | 0.531 | 25.750 | +0.820 | -0.07 | y |
| RANS5 | RANS | 0.7880 | +0.14 | 0.8350 | +0.49 | 0.544 | 25.725 | +0.796 | +0.48 | y |
| **EXPERIMENT** | | **0.7869** | | **0.8310** | | **0.540** | **24.929** | | | |

Inter-code period spread 0.7609 to 0.7915 s, **3.91 percent** of the mean. Max deviation
from experiment 3.31 percent, median 0.35 percent. Decay-rate spread 17.1 percent.

### 03D, H0 = 90 mm, 10 codes, RANS3 absent

| code | family | T1 [s] | dT1 % | decay [1/s] | dsig % | a33/m | trough [mm] | dtrough [mm] | dnorm %H0 | WG |
|---|---|---|---|---|---|---|---|---|---|---|
| FNPF1 | FNPF | 0.8040 | -0.66 | 0.8117 | +1.29 | 0.608 | 76.436 | +0.707 | -0.20 | |
| LPF0 | LPF | 0.7609 | -5.98 | 0.7005 | -12.59 | 0.440 | 69.457 | -6.272 | -7.56 | |
| LPF1 | LPF | 0.7781 | -3.85 | 0.7989 | -0.31 | 0.506 | 77.710 | +1.981 | +1.32 | |
| LPF2 | LPF | 0.8079 | -0.17 | 0.8167 | +1.91 | 0.623 | 76.800 | +1.070 | +0.31 | |
| LPF3 | LPF | 0.8254 | +1.99 | 0.8189 | +2.18 | 0.695 | 82.245 | +6.516 | +6.36 | |
| LPF4 | LPF | 0.8385 | +3.62 | 0.7008 | -12.55 | 0.749 | 84.425 | +8.696 | +8.74 | |
| RANS1 | RANS | 0.8049 | -0.54 | 0.7998 | -0.20 | 0.611 | 76.077 | +0.348 | -0.67 | |
| RANS2 | RANS | 0.8088 | -0.05 | 0.7830 | -2.29 | 0.627 | 76.920 | +1.191 | +0.70 | y |
| RANS4 | RANS | 0.8069 | -0.30 | 0.7810 | -2.54 | 0.619 | 76.188 | +0.459 | -0.70 | y |
| RANS5 | RANS | 0.8090 | -0.03 | 0.7950 | -0.79 | 0.628 | 76.663 | +0.934 | +0.34 | y |
| **EXPERIMENT** | | **0.8093** | | **0.8014** | | **0.629** | **75.729** | | | |

Inter-code period spread **9.66 percent** of the mean. Max deviation 5.98 percent, median
0.60 percent. Decay-rate spread 15.2 percent.

### 05D, H0 = 150 mm, all 11 codes

| code | family | T1 [s] | dT1 % | decay [1/s] | dsig % | a33/m | trough [mm] | dtrough [mm] | dnorm %H0 | WG |
|---|---|---|---|---|---|---|---|---|---|---|
| FNPF1 | FNPF | 0.8706 | +0.40 | 0.7208 | -4.51 | 0.885 | 126.611 | -2.012 | -1.11 | |
| LPF0 | LPF | 0.7609 | **-12.26** | 0.7005 | -7.19 | 0.440 | 115.762 | -12.860 | -8.23 | |
| LPF1 | LPF | 0.7781 | -10.27 | 0.7989 | +5.85 | 0.506 | 129.519 | +0.897 | +0.65 | |
| LPF2 | LPF | 0.8657 | -0.17 | 0.8418 | +11.53 | 0.864 | 124.659 | -3.963 | -2.56 | |
| LPF3 | LPF | 0.9507 | +9.64 | 0.8555 | +13.34 | 1.248 | 147.919 | +19.296 | +12.96 | |
| LPF4 | LPF | 0.9784 | **+12.83** | 0.7746 | +2.62 | 1.381 | 155.234 | +26.611 | +17.67 | |
| RANS1 | RANS | 0.8692 | +0.23 | 0.7573 | +0.33 | 0.879 | 126.054 | -2.569 | -1.45 | |
| RANS2 | RANS | 0.8652 | -0.22 | 0.7084 | -6.15 | 0.862 | 128.391 | -0.231 | -0.35 | y |
| RANS3 | RANS | 0.8600 | -0.82 | 0.6985 | -7.45 | 0.840 | 126.837 | -1.785 | -1.96 | y |
| RANS4 | RANS | 0.8682 | +0.13 | 0.7226 | -4.27 | 0.875 | 125.396 | -3.226 | -2.41 | y |
| RANS5 | RANS | 0.8655 | -0.19 | 0.7248 | -3.97 | 0.863 | 126.471 | -2.151 | -1.49 | y |
| **EXPERIMENT** | | **0.8671** | | **0.7548** | | **0.870** | **128.622** | | | |

Inter-code period spread **25.10 percent** of the mean. Max deviation 12.83 percent,
median 0.40 percent. Decay-rate spread 20.8 percent.

### The spread is a family effect, so both readings are given

The paper draws this line itself: the LPF and partly the FNPF models "should be used with
care in applications with motions of very large amplitudes, whereas the RANS models, if
proper convergence is reached, are capable of producing accurate results for all drop
heights." Pooling all eleven lets the two amplitude-blind linear models set the width.

| drop | family | n | period spread | max abs dev from experiment | decay spread | max abs trough dev |
|---|---|---|---|---|---|---|
| 01D | FNPF | 1 | - | 0.13 % | - | 0.814 mm |
| 01D | LPF | 5 | 3.93 % | 3.31 % | 13.03 % | 1.777 mm |
| 01D | **RANS** | 4 | **0.51 %** | **0.37 %** | 7.70 % | 0.999 mm |
| 03D | FNPF | 1 | - | 0.66 % | - | 0.707 mm |
| 03D | LPF | 5 | 9.69 % | 5.98 % | 15.43 % | 8.696 mm |
| 03D | **RANS** | 4 | **0.51 %** | **0.54 %** | 2.38 % | 1.191 mm |
| 05D | FNPF | 1 | - | 0.40 % | - | 2.012 mm |
| 05D | LPF | 5 | 25.10 % | 12.83 % | 19.52 % | 26.611 mm |
| 05D | **RANS** | 5 | **1.06 %** | **0.82 %** | 8.13 % | 3.226 mm |

**The five RANS codes agree with each other to about 1 percent on period and sit within
0.82 percent of the physical measurement, at every drop height.** That is the yardstick a
two-phase CFD solver should be held to.

### And the envelope is set at BOTH ends by one group

Section 2 established that eleven series come from six groups. Grouping the deviations that
way is the sharpest single result in this document:

| group | series | span of period deviation, all drops | worst abs | codes |
|---|---|---|---|---|
| Budapest | 1 | -0.19 to +0.14 % | **0.19 %** | RANS5 |
| NREL | 1 | -0.30 to +0.13 % | **0.30 %** | RANS4 |
| Aalborg-CFD | 1 | -0.54 to +0.23 % | **0.54 %** | RANS1 |
| Chalmers | 1 | -0.66 to +0.40 % | **0.66 %** | FNPF1 |
| Plymouth | 2 | -0.82 to -0.05 % | **0.82 %** | RANS2, RANS3 |
| **Kramer** | **5** | **-12.26 to +12.83 %** | **12.83 %** | LPF0 to LPF4 |

**Five of the six independent groups agree with the physical measurement to within 0.82
percent**, across three drop heights, on four different solvers (OpenFOAM v1912, OpenFOAM
5.0, OpenFOAM 7, STAR-CCM+ 13.06) plus a fully nonlinear potential-flow BEM. The entire
`[-12.3, +12.8]` percent envelope is set at **both ends** by the sixth group's five
potential-flow configurations, which are all by one author.

That is not a reason to discard the wide envelope. It is a reason to always quote which one
is meant. Section 6 quotes both.

---

## 5. The reduction is validated against the paper's own published figures

This matters more than any number above: a reduction written from scratch can agree with
itself and still be wrong. Three independent checks, none of which I chose after seeing
the result.

**(a) The linear models must be amplitude-blind, and they are.** LPF0 returns
`T1 = 0.7609 s` and LPF1 returns `0.7781 s` at **all three drop heights**, identical to
four decimals, while every nonlinear code's period rises with amplitude. A linear model
has no mechanism to do otherwise. Nothing in the reduction knows which codes are linear.

**This check got stronger when the spreadsheet was read, and it now runs the other way
too.** The reduction predicted "these two are linear" from the data alone; the xlsx
independently says LPF0 is a "simple analytical equation using linear coefficients from
BEM" and LPF1 has "linear hydrostatics and linear coefficients from BEM". Confirmed. And
the spreadsheet then **predicts the shape of the rest of the LPF ladder, which the data
confirms**: LPF2 adds nonlinear hydrostatics, LPF3 adds a **position-dependent
infinite-frequency added mass**, LPF4 adds **position-dependent radiation functions**. The
measured implied `a33/m` at 05D climbs exactly along that ladder, 0.440, 0.506, 0.864,
**1.248, 1.381**, and the two codes carrying position-dependent added mass are precisely
the two that overshoot the measured period most, at +9.64 and +12.83 percent. The upper
edge of the whole inter-code envelope has a named mechanism, not just a magnitude.

**(b) The paper's own RANS deviation figures.** Kramer 2021 printed page 23: "Troughs and
crests for the RANS models are calculated with deviations of maximally 1 mm, 2 mm, and
4 mm, respectively, for the three drop heights in ascending order." My independently
computed RANS maximum absolute first-trough deviations are **0.999, 1.191 and 3.226 mm**.
Mine are troughs only, so they must be at or below the paper's trough-and-crest maxima,
and they are, at all three drop heights.

**(c) The paper's 0.1D statement.** Printed page 23: "The FNPF and RANS models deviate
with less than 1 mm for H0 = 0.1D." My 01D column gives FNPF1 +0.814, RANS1 +0.698,
RANS2 +0.999, RANS4 +0.820, RANS5 +0.796 mm. All below 1 mm.

**(d) Release heights against Table 4.** Independently extracted means agree with the
paper's stated measured drop heights to better than 0.1 mm, inside Table 4's own stated
standard uncertainties of {0.8, 0.5, 0.3} mm.

---

## 6. Job B, placed

**This is not a re-grade and must never be used as one.** The criterion was fixed in
advance at `docs/R5_PHYSICS_BATCH_MANIFEST.md:214-226` and re-scoring after seeing a
failure is forbidden. What follows is only *where* a given grade sits relative to eleven
published codes on the same benchmark.

### 6.1 The bridge, which is an attribution and not a measurement

Job B is a **hydrostatic** check: manifest criterion 3 grades the steady vertical reaction
of a pinned sphere against 69.2180 N of analytic buoyancy. The eleven codes are compared
above on damped **period**, because that is what a free-decay record measures. Nothing in
the benchmark converts one into the other for free.

`T = 2*pi*sqrt((m + a33)/k)` with `k = rho*g*pi*R^2`, so the bridge is whatever the force
error does to `k`, and that depends on where the error lives:

* **Scale attribution.** The error multiplies the buoyant force without changing the
  geometry: an error in `rho*g`, or in the coupling's force normalisation. Then `k`
  carries it one for one and `e_T = 1/sqrt(1+f) - 1`.
* **Geometry attribution.** The error is an isotropic error in the sphere's effective
  radius in the solver. Then `F ~ R^3` while `k ~ R^2`, so a force excess `f` implies a
  stiffness excess `(1+f)^(2/3) - 1`, which is **smaller**. This is the more forgiving of
  the two and therefore the one an outlier claim must survive.

The added-mass route is deliberately not offered: at `a33/m = 0.5` a 1 percent period
error becomes a 6.03 percent error in `a33`, so routing a force error through `a33`
inflates the equivalent about sixfold, and a hydrostatic check contains no added mass at
all.

### 6.2 The placement

Envelope over 31 series: **all codes -12.26 to +12.83 percent** (low LPF0 at 05D, high
LPF4 at 05D). **RANS only, 13 series: -0.82 to +0.23 percent.**

Every equivalent below is negative, because a force excess shortens the period, so the
bound each must clear is the envelope's **low** edge, `-12.26 percent`. Comparing a
negative equivalent against the positive high edge would flatter it.

| job | F excess | scale T % | inside? | x worst same-sign code | geom T % | inside? | x worst same-sign | x worst RANS |
|---|---|---|---|---|---|---|---|---|
| 918043 | +64.19 | -21.96 | no | 1.79x | -15.23 | no | 1.24x | 18.5x |
| **918240** | **+50.06** | **-18.37** | **no** | **1.50x** | **-12.65** | **no** | **1.03x** | **15.4x** |
| 918450 | +34.35 | -13.73 | no | 1.12x | -9.37 | yes | 0.76x | 11.4x |
| 918722 (n=128) | +23.68 | -10.08 | yes | 0.82x | -6.84 | yes | 0.56x | 8.3x |
| 918722 fitted floor | +18.05 | -7.96 | yes | 0.65x | -5.38 | yes | 0.44x | 6.6x |

Lineage supplied by the coordinator from primary documents and encoded verbatim in
`JOB_B_GRADES`: 918043 is **explicitly superseded** and biased high (predates commit
7c9e0af's `measure_surface` h/2 correction); **918240 is the canonical grade**; 918450 is
a *different configuration*, the boundary-fix treatment, and is not a re-grade of 918240;
918722 is the refinement series whose two-term fit gives an irreducible +18.05 point floor.

### 6.3 The sentence

> **Job B's canonical +50.06 percent is an outlier among published codes, not a point
> inside their scatter.** It falls outside the envelope of all eleven codes on both
> available attributions. On the direct scale attribution it is 1.50 times worse than the
> worst code in the comparison. On the most forgiving geometric attribution it is 1.03
> times that worst code, that is, essentially tied with **LPF0**, a linear potential-flow
> model with a constant added mass that the paper itself says should be used with care at
> large amplitude. Measured against the five RANS codes, the family a two-phase CFD solver
> belongs in, it is **15 to 22 times** their worst deviation.

Stated by group rather than by code, which section 2 shows is the sounder unit: **Job B's
equivalent exceeds the worst deviation of every independent group except one**, and that one
is five configurations of linear and semi-linear potential flow by a single author. The
0.82 percent bound is Plymouth's, so "15.4x and 22.4x the worst RANS code" and "15.4x and
22.4x the worst of the five non-Kramer groups" are the same two numbers.

Two consequences worth keeping.

* **The boundary fix (918450) moves it from "outside on any reading" to "at the edge."**
  It is inside the eleven-code envelope on the geometric attribution and outside on the
  scale one. It remains 11.4 times the worst RANS deviation. It is still a FAIL against
  its own criterion and this changes nothing about that.
* **Refinement alone would land inside the envelope but not inside the RANS family.** The
  fitted +18.05 point floor is inside on both attributions, and still 6.6 times the worst
  RANS deviation. So "refine until it agrees" was never going to reach where the published
  high-fidelity codes sit.

**The honest limit of this framing.** The eleven codes and Job B are not measuring the
same thing, and the conversion above is an assumption, not a measurement. The
attribution-free version, which needs no bridge at all, is weaker but unarguable: the
worst published code in this comparison misses the physical first-trough amplitude by
12.86 mm out of 128.6 mm, **10.0 percent**, and misses the period by 12.83 percent. A
50 percent error on a force ratio is not in that envelope on any reading; the attribution
only sharpens by how much.

---

## 7. THE REFLECTION-WINDOW ERROR, and the planned configuration it invalidates

> **`PLANNED_CONFIGS`' largest entry, `lim = 2.2 m`, delivers 1.7019 clean reflection
> periods at the largest drop height, not the two it was sized for. At the `--lim 1.2`
> default the 05D window is 0.8509 periods, below one.** The sizing was derived at
> `a33/m = 0.5` and does not carry to 05D, where the measured value is 0.870.

That is a scene-sizing consequence, not a wording matter, which is why this has its own
section. `sphere_heave.py` is out of scope for this slot, I have not touched it, and someone
else owns the fix.

`sphere_heave.py:239` hardcodes `added_mass_ratio = 0.5`. Its docstring at `:293-300`
records that this is "an ESTIMATE, not a source", that `T ~ sqrt(1 + a33/m)`, and that
raising it to 0.83 "lengthens T_n by about 10 percent and shortens every reflection window
in periods by the same factor. Any reflection figure inherits this."

`kramer_benchmark.py` already derived `implied_a33_over_m` from the measured damped period
and nothing consumed it. Here is what it says.

| source | a33/m | vs the hardcoded 0.5 |
|---|---|---|
| small-amplitude limit (late-cycle period 0.7646 s) | **0.454** | -9.2 % |
| **01D, H0 = 30 mm**, the default `--h0-over-d 0.1` | **0.540** | +8.0 % |
| 03D, H0 = 90 mm | 0.629 | +25.8 % |
| 05D, H0 = 150 mm | **0.870** | +74.1 % |
| the docstring's own sensitivity value | 0.83 | +66.0 % |

**The 0.5 estimate is well chosen for the configuration the project actually runs.** The
planned drops default to `h0_over_d = 0.1`, which is 01D, where the measurement is 0.540.
The estimate is 8.0 percent low in `a33/m`, which is 1.33 percent on the period. It is also
nicely bracketed: the small-amplitude limit is 0.454 and the first-cycle 01D value is 0.540,
so 0.5 sits inside the physical range rather than outside it. The problem is not the default,
it is applying the default's window to the large drop.

### 7.1 The docstring's sensitivity sentence understates the effect by about two

Reimplemented independently in `reflection_windows()` (importing `sphere_heave` is out of
scope for this slot and it must not be touched). The reimplementation is checked against
the file it reproduces: at `a33/m = 0.5` it returns **`lim >= 2.0850 m` for two clean
periods**, which is `sphere_heave.py`'s own docstring figure of 2.085 m to four digits.

`lim = 1.2` (the `--lim` default), `WALL = 0.100`, `d_wall = 0.500 m`, `g = 9.81` engine:

| a33/m | T_n [s] | dT_n | group [T] | Kramer phase [T] | sqrt(gh) [T] | window change: grp / phase / shallow |
|---|---|---|---|---|---|---|
| 0.500 hardcoded | 0.7770 | - | 2.1220 | **1.0610** | 0.5811 | - |
| 0.454 small-amp | 0.7650 | -1.54 % | 2.1889 | 1.0945 | 0.5902 | +3.15 / +3.15 / +1.56 % |
| 0.540 **01D** | 0.7873 | +1.33 % | 2.0666 | **1.0333** | 0.5735 | -2.61 / -2.61 / -1.31 % |
| 0.629 03D | 0.8097 | +4.21 % | 1.9539 | 0.9770 | 0.5577 | -7.92 / -7.92 / -4.04 % |
| 0.870 **05D** | 0.8676 | +11.66 % | 1.7019 | **0.8509** | 0.5204 | -19.80 / -19.80 / -10.45 % |
| 0.830 docstring | 0.8582 | +10.45 % | 1.7394 | 0.8697 | 0.5261 | **-18.03** / **-18.03** / -9.46 % |

**The docstring is right that 0.83 lengthens `T_n` by about 10 percent (10.45) and wrong
that the windows shorten "by the same factor".** They shorten by **18.03 percent**, not by
about 9.5. The reason is structural, not a rounding matter:

* `c_group = g*T_n/(4*pi)` and `c_phase = g*T_n/(2*pi)` are both **proportional to `T_n`**,
  so the window expressed in periods is `(2*d_wall/c)/T_n ~ 1/T_n^2`.
* `sqrt(g*h)` does not depend on the body at all, so that window alone goes as `1/T_n`.

Measured scaling exponents, computed rather than argued: `group -2.000`,
`kramer_phase -2.000`, `shallow_bound -1.000`. Only the third shortens "by the same
factor". **Every reflection figure produced under that sentence has the sensitivity of two
of its three windows understated by a factor of about two.**

### 7.2 The consequence for tank sizing

| clean periods wanted | a33/m | required `lim` |
|---|---|---|
| 1.0 | 0.5 hardcoded | 1.1425 m |
| 1.0 | 0.540 (01D) | 1.1678 m |
| 1.0 | 0.870 (05D) | **1.3752 m** |
| 2.0 | 0.5 hardcoded | 2.0850 m (matches sphere_heave's docstring) |
| 2.0 | 0.540 (01D) | 2.1355 m |
| 2.0 | 0.870 (05D) | **2.5503 m** |

Because the window in periods goes as `1/T_n^2` while the tank enters linearly, the
required side grows as `(1 + a33/m)`. Two live consequences, both at the largest drop:

* **At `lim = 1.2` and 05D the clean window is 0.8509 periods, below one.** The docstring
  records 1.06 periods; that is the 01D-appropriate estimate applied to every drop.
* **`PLANNED_CONFIGS`' largest entry, `lim = 2.2`, delivers 1.7019 clean periods at 05D,
  not two.** The 2.085 m sizing was derived at `a33/m = 0.5` and does not carry to the
  large drop. Two clean periods at 05D needs `lim >= 2.5503 m`.

I have not edited `sphere_heave.py`. This is the reported delta, as instructed.

---

## 8. WG1 to WG3: four codes of eleven, and what they can separate

### 8.1 Availability is the result, not a caveat

| set | carries WG1-3 |
|---|---|
| experimental `Measured` files | **24 of 24** |
| experimental `CI95` files | **0 of 3** (four columns) |
| numerical series | **10 of 31** |
| numerical **codes** | **4 of 11**: RANS2, RANS3, RANS4, RANS5 |

FNPF1, LPF0 through LPF4 and **RANS1** are two columns, `t` and `x3`. This is not a
corruption on our side: the paper's Appendix A says the WG columns "are included for the
experimental results and for certain numerical results".

**So the radiation-versus-viscous separation is available on four codes of eleven, and
this benchmark cannot perform it for the other seven.** That is a statement about the
benchmark. It also means WG can never be a cross-code discriminator here: any conclusion
drawn from it covers RANS only, which is already the family that agrees best on heave.

### 8.2 The gauge positions, MEASURED off Figure 8

The earlier revision of this document derived the radii from one sentence of prose. They
are now **read directly from Figure 8** of the paper, captioned "Test setup and measurements
of the wave basin. Measurements are given in mm." The figure puts the sphere at the basin
centre, 6500 mm from each concrete wall and 4220 mm from the wavemaker, and the three gauges
on **one radial line running from the sphere toward the wavemaker, in a chain of three
600 mm steps**.

| gauge | **measured** | derived from prose | derived error | in wavelengths | lead periods at the measured radius | paper says |
|---|---|---|---|---|---|---|
| WG1 | **1.800 m** | 1.787 m | -0.72 % | 2.015 | 2.015 | "around 2.0" |
| WG2 | **1.200 m** | 1.162 m | -3.21 % | 1.343 | 1.343 | "around 1.3" |
| WG3 | **0.600 m** | 0.625 m | +4.24 % | 0.672 | 0.672 | "around 0.7" |

**The closure runs both ways and both directions check out.** Every derived value sits
inside the +/-0.045 m that the one-decimal prose implied, so the derivation was sound. And
feeding the measured radii back through the paper's own reflection-lead relation returns
2.015, 1.343 and 0.672 wave periods, which is exactly the "around 2.0, 1.3, and 0.7" the
paper states. `wave_gauge_distances()` is retained as that cross-check; `WAVE_GAUGE_RADII_M`
is now the source.

**The measured radii are independently confirmed by the data itself.** A wrong radius shows
up as gauge-to-gauge disagreement in the energy budget, because an axisymmetric outgoing
field must give the same total through every circle. Switching from derived to measured
**nearly halves that disagreement**: the experiment's mean gauge spread falls from 0.099 to
**0.058** at 03D and from 0.100 to **0.064** at 05D, and RANS2's falls from 0.091 to
**0.039** at 05D. Nothing in the budget was tuned to make that happen.

`lambda = 0.8935 m` at `Te0`, depth 0.900 m, `kh = 6.33`, `tanh(kh) = 0.999994`, so deep
water holds and `c_g = c/2` throughout.

### 8.3 The budget

Body energy is the **exact** hydrostatic potential, not `0.5*k*A^2`. That distinction is not
cosmetic here and section 9 is about why. Over a 150 mm displacement of a 300 mm sphere the
waterplane area goes to **zero**: at H0 = 0.5D the sphere's bottom pole sits exactly on the
free surface at release and the submerged volume is 0.0000 of its equilibrium value.

```
V(z) = pi*(R-z)^2*(2R+z)/3
U(z) = rho*g*[ (2/3)pi R^3 z - (pi/3)( (3/4)R^4 - R(R-z)^3 + (R-z)^4/4 ) ]
```

The closed form is checked against direct numerical quadrature of `rho*g*(V_eq - V(z))` to a
relative error of 5e-12. For a linear deep-water wave the flux per unit crest length is
`rho*g*<eta^2>*c_g`, so the energy through a circle of radius `r` is
`2*pi*r*rho*g*c_g*integral(eta^2 dt)`. Energy that has crossed radius `r` by the end of the
record was shed by the body roughly `r/c_g` earlier, which is **3.05 s at WG1 against a
6.05 s record**, so each gauge gets its own body window ending at `T_end - r/c_g`.

| drop | E0 exact [J] | linear would be | radiated fraction | per gauge WG1 / WG2 / WG3 | spread over 3 gauges | spread over 4 reps | **non-radiated** |
|---|---|---|---|---|---|---|---|
| 01D | 0.293 | +0.63 % | 0.724 | 0.795 / 0.737 / 0.697 | 0.071 | 0.124 | **0.276** |
| 03D | 2.650 | +6.42 % | 0.764 | 0.730 / 0.776 / 0.794 | 0.058 | 0.016 | **0.236** |
| 05D | 6.456 | +19.82 % | 0.697 | 0.665 / 0.696 / 0.722 | 0.064 | 0.005 | **0.303** |

**The three gauges are the check, not three chances at an answer.** They agree to 0.058 to
0.071 across a 3x range of radius, which is the same size as the 01D repetition scatter.

**There is no resolvable trend in the non-radiated share.** It is 27.6, 23.6, 30.3 percent,
not monotone, and the 6.7 point range across drop heights is no larger than the spread
between gauges within one drop. Section 9 is about the earlier version of this paragraph,
which said the opposite.

**A second explanation of mine that the measured radii dissolved.** With the derived radii,
WG3 always read highest and I attributed that to near-field contamination, since WG3 sits
inside one wavelength. With the measured radii **the ordering is no longer consistent**: at
01D it runs WG1 > WG2 > WG3 and at 03D and 05D it runs the other way. There is no longer a
systematic radial trend to explain, because most of it was the radius error. The near-field
caution still stands as a caution, WG3 is at 0.672 wavelengths and no far-field criterion is
satisfied there, but it is no longer needed to explain anything, and I am not going to keep
an explanation alive after its evidence has gone.

**Verdict on item 4.** Yes, WG1-3 can separate radiation from viscous damping on this data,
to **tens of percent and not better**, and only for the experiment and four codes. The
dominant remaining uncertainty is the single-frequency `c_g` against a period that moves
about 13 percent over the record, roughly a 10 percent systematic common to all three
gauges, left in place as instructed. A non-radiated share of roughly a quarter to a third is
a real and reproducible measurement, reproducible to 0.005 across repetitions at 05D. Its
variation with drop height is not.

---

## 9. THE TRAP, which is the most transferable thing here

I wrote a finding down, and then my own correction deleted it. The mechanism is general
enough to state as a rule.

**What I claimed.** "Non-radiated share rises with drop height, 26 / 26 / 40 percent, the
signature of viscous and separation losses growing faster than linearly with amplitude while
radiation stays closer to linear." That is a coherent physical story. It is the story a
reviewer would nod at. It was an artefact.

**What produced it.** I used the linear `0.5*k*A^2` for the sphere's potential energy. Over
a 150 mm displacement of a 300 mm sphere the waterplane area is not constant; it goes to
zero. The linear form is therefore **0.67 percent high at 01D, 6.38 percent high at 03D and
20.00 percent high at 05D**. Those errors inflate the denominator's `E0` and so deflate the
radiated fraction, most at the largest drop.

**The rule.**

> **A linearisation whose error grows with the independent variable will always produce a
> trend in that variable.** If the quantity you are trending against is also the quantity
> your approximation degrades with, the approximation can manufacture the entire trend, and
> it will have the right shape and the right sign to be believed.

Here the independent variable was drop height, and drop height is exactly what drives the
waterplane area away from its linearised value. The two were the same variable, which is the
condition for the trap to close.

**What would have caught it earlier, cheaply.** Not scepticism, which I had. A **no-forcing
control**: compute the same statistic under the exact form and the linear form and difference
them, before interpreting. The difference is 0.67 / 6.38 / 20.00 percent, monotone in the
independent variable, and it is visible in one command without any data at all. The exact
form is four lines of algebra and checks against numerical quadrature to 5e-12.

**Related, same night, same shape.** The near-field explanation in section 8.3 was a second
plausible physical story standing in for evidence, and the measured radii dissolved most of
what it explained. Two for two. The tell in both cases was the same: a story that explained
the data arrived before a test that could have refuted it.

---

## 10. AN APPARENT INCONSISTENCY IN SOMEONE ELSE'S ARCHIVE

**Framing first, because it matters.** What follows is a reproducible inconsistency between
two columns of a published supplementary dataset and the physics those columns must obey.
**It is not an assertion that RANS4's or RANS5's models are wrong.** A column-order or
position convention in a delivered text file is a data-packaging question, entirely separate
from the solver that produced it, and both codes' heave results are among the best in the
comparison: RANS4 is within 0.30 percent of the measurement on period at every drop height
and RANS5 within 0.19 percent, the two best of the six groups. Whether to raise this with the
authors is Josie's decision and I have not acted on it.

**The test needs no gauge positions at all, only their ordering**, so it cannot be an
artefact of section 8.2. Under `1/r` geometric spreading the `eta^2` time integral **must
rise toward the sphere**.

| series | I(WG1) | I(WG2) | I(WG3) | I(near)/I(far) | order matches experiment |
|---|---|---|---|---|---|
| EXPERIMENT 05D rep1 | 6.439e-05 | 1.026e-04 | 2.133e-04 | **3.31** | (reference) |
| RANS2 05D | 7.096e-05 | 1.092e-04 | 2.294e-04 | 3.23 | yes |
| RANS3 05D | 6.308e-05 | 9.895e-05 | 2.144e-04 | 3.40 | yes |
| **RANS4 05D** | 1.949e-04 | 1.059e-04 | 6.791e-05 | **0.35** | **no** |
| **RANS5 05D** | 2.177e-04 | 8.580e-05 | 4.669e-05 | **0.21** | **no** |

Expected from geometry alone at the measured radii: `r(WG1)/r(WG3) = 3.00`. The experiment
gives 3.31 and RANS2/RANS3 give 3.23 and 3.40. **RANS4 and RANS5 invert, at every drop
height.** Read as shipped, RANS4's radiated energy reaches 0.97 to 1.32 times the energy its
sphere lost, exceeding unity, which no passive body can do.

Reassigning the reversed radial order resolves RANS4 completely and RANS5 only partly:

| series | as shipped, per gauge | radii reversed | mean | gauge spread reversed | vs experiment's own spread |
|---|---|---|---|---|---|
| RANS4 01D | 2.77 / 0.91 / 0.28 | 0.85 / 0.91 / 0.92 | 0.891 | **0.072** | 0.071 |
| RANS4 03D | 2.66 / 0.88 / 0.28 | 0.85 / 0.88 / 0.88 | 0.870 | **0.030** | 0.058 |
| RANS4 05D | 1.98 / 0.71 / 0.23 | 0.69 / 0.71 / 0.66 | 0.686 | **0.058** | 0.064 |
| RANS5 01D | 2.12 / 0.53 / 0.14 | 0.42 / 0.53 / 0.70 | 0.550 | 0.282 | 0.071 |
| RANS5 03D | 2.41 / 0.63 / 0.17 | 0.52 / 0.63 / 0.79 | 0.645 | 0.277 | 0.058 |
| RANS5 05D | 2.23 / 0.58 / 0.16 | 0.48 / 0.58 / 0.73 | 0.596 | 0.253 | 0.064 |

**RANS4 reversed lands on the experiment's own gauge consistency at all three drop heights**
(0.072, 0.030, 0.058 against 0.071, 0.058, 0.064) and its 05D radiated fraction becomes 0.686
against the experiment's 0.697. **RANS5 improves by a factor of seven to eight but stays
about four times the experiment's spread**, so a simple relabelling does not explain it.
Section 2 offers a candidate that does: RANS5 is a **2D axisymmetric wedge with the tank
floor at 1.8 m** rather than 0.900 m, so its gauge positions need not correspond to the
experiment's at all, and the archive ships no per-code gauge coordinates to check against.

**The control, because "reversing helps" is only evidence if reversing can also hurt.**
Applying the same reversal to the two codes that were already consistent makes them 29 to 72
times worse, which is what a real discriminator must do:

| code, 05D | gauge spread as shipped | reversed | |
|---|---|---|---|
| RANS2 | 0.039 | 2.129 | **worsens 55x** |
| RANS3 | 0.069 | 2.005 | **worsens 29x** |
| RANS4 | 1.752 | 0.058 | improves 30x |
| RANS5 | 2.077 | 0.253 | improves 8x |

**Anyone using these WG columns naively gets a wrong answer with no error message.**

---

## 11. Review status, self-tests, and what is not verified

### 11.1 ADVERSARIAL REVIEW WAS NOT AVAILABLE. THESE CLAIMS ARE UNREVIEWED BY A SECOND PARTY.

The project's designated `physics-skeptic` subagent was launched three times, once as
`physics-skeptic` on the session default, once as `physics-skeptic` with an explicit
`model: opus` override, and once as `general-purpose` with the same adversarial brief.
**All three terminated with the same API error**, an unavailable pinned model
(`deepseek-ai/DeepSeek-V4-Flash:deepinfra`). The subagent path is broken in this session
regardless of agent type or model override.

**No claim in this document has been independently reviewed.** It is not marked reviewed
and the review was not faked. What follows instead are known-answer self-tests, which are
a weaker check because I wrote both the code and the test, and are reported as such.

### 11.2 Known-answer self-tests, all passed

**Test 1, the extrema picker recovers a planted signal, and does so independently of
sampling.** A damped sinusoid with `T = 0.8671 s` and `sigma = 0.7548 1/s` planted in it,
sampled four ways:

| sampling | T recovered | error | sigma recovered | error |
|---|---|---|---|---|
| uniform, 3000 points | 0.8683 | +0.136 % | 0.7576 | +0.369 % |
| uniform, 500 points | 0.8684 | +0.150 % | 0.7578 | +0.399 % |
| non-uniform, 500 points | 0.8685 | +0.167 % | 0.7583 | +0.463 % |
| non-uniform, 5000 points | 0.8683 | +0.137 % | 0.7576 | +0.372 % |

This is the direct test of the design decision in section 2. Across a **10x change in
sample density and 60 percent time-stamp jitter**, the recovered period moves by 0.03
percentage points and the decay rate by 0.09. The RANS-family inter-code spreads reported
in section 3 are 0.51 to 1.06 percent on period, an order of magnitude above that floor,
so those spreads are signal and not sampling.

The residual **+0.14 percent bias on period and +0.37 percent on decay rate is systematic,
present at every sampling density**, and therefore a property of the estimator rather than
the grid. It comes from the settled-level subtraction: on a decaying record the last 15
percent has a slightly nonzero mean. It is common to the experiment and to every code, so
it cancels to first order in the deviation columns, which are all differences.

**Test 2, `hydrostatic_pe` against direct numerical quadrature.** Closed form against a
200,001-point trapezoidal integral of `rho*g*(V_eq - V(z))`: relative error 1.7e-13 at
01D, 1.6e-12 at 03D, 5.0e-12 at 05D. The `z > R` guard clamps rather than extrapolating.

**Test 3, the Job B analytic target reproduces.** `rho = 998.2`, `g = 9.81` (engine, not
the benchmark's 9.82), `R = 0.150`, half sphere gives **69.2180 N**, matching manifest
criterion 3 to four decimals. This confirms Job B is a hydrostatic check and that section
5.1's attribution is applied to the right quantity.

**Test 4, the reversal control.** Reported in section 10: reversing the two codes that
were already correct makes them 19 to 23 times worse, so the reversal test discriminates.

**Test 5, the reflection reimplementation reproduces the file it describes.** At
`a33/m = 0.5` it returns `lim >= 2.0850 m` for two clean periods, which is
`sphere_heave.py`'s own docstring figure to four digits. This is a real check and not
circular: the docstring figure was computed by different code, and my module never reads
`sphere_heave.py`. It confirms the reimplementation, not the physics claim in section 6.1,
which rests on the analytic `1/T_n^2` scaling and its measured exponent of exactly -2.000.

### 11.3 What is not verified

* **The `c_g` at `Te0` simplification, retained deliberately.** The period moves from 0.867
  to 0.766 s over the record and `c_g` is proportional to period, so section 8.3's fractions
  carry a systematic of order 10 percent, common to all three gauges and therefore unable to
  explain any gauge-to-gauge difference.
* **The 01D radiated fraction is the least trustworthy number here.** Its spread across the
  four repetitions is 0.124, against 0.016 and 0.005 at the larger drops, because the 01D
  releases themselves scatter from 27.720 to 31.236 mm and the wave signals are near the
  0.096 mm measurement uncertainty.
* **RANS5's gauge positions are unresolved.** Reversal improves it 7 to 8 times but leaves it
  about 4x the experiment's gauge consistency. Its 2D axisymmetric wedge geometry and 1.8 m
  floor are a candidate explanation and not a demonstrated one, and the archive ships no
  per-code gauge coordinates.
* **The Solidworks CAD model and the sphere mass-distribution xlsx in `Descriptions/` are
  extracted but not read.** The mass xlsx may carry a measured inertia tensor, which touches
  CLAUDE.md August 4 item 4 and its standing instruction not to wire inertia. Deliberately
  left alone: that item is not this slot's.
* **Figure 8 was read visually, at 2x upscale, from the embedded page image.** The three
  600 mm callouts and the 4220 / 6500 mm basin dimensions are unambiguous, and the reading is
  corroborated two ways in section 8.2 (it reproduces the paper's own "around 2.0, 1.3, 0.7"
  and it nearly halves the measured gauge disagreement), but it is a figure reading and not a
  tabulated value.
* **I did not re-grade Job B and this document must not be used to.** Section 6 places a
  fixed grade; it does not produce one.
* **I did not edit `sphere_heave.py` or `grade_job_b.py`.** Section 7 is a reported delta.
* **The section 10 finding is about a delivered data file, not about anyone's solver**, and
  no one has been contacted.

## 12. Provenance of every claim type in this document

| claim type | how obtained |
|---|---|
| all tables in sections 3, 4, 7, 8, 10 | **read directly**, recomputed from the archive by `kramer_benchmark.py` on 2026-08-18 |
| paper quotations in sections 5, 8.1, 8.2 | **read directly** from the PDF in `can-it-ford-refs/`, page numbers as printed |
| Job B grade lineage in section 6.2 | **supplied by the R8 coordinator** from primary documents, encoded verbatim in `JOB_B_GRADES`, not re-derived here |
| `sphere_heave.py` line numbers and constants | **read directly** from the file, not edited |
| the force-to-period bridge in section 6.1 | **inferred**, and labelled an attribution in both the code and the prose |
| gauge radii in section 8.2 | **read directly** off Figure 8 of the paper, corroborated by the derivation from its Section 3.5 text and by a fall in measured gauge disagreement |
| code attribution in section 2 | **read directly** from `Description of numerical models.xlsx`, the archive's own Appendix B source |
| independent adversarial review | **NONE. UNAVAILABLE.** Three subagent launches failed on a pinned-model API error; see section 11.1. Self-tests only. |
