# Paper patch: six prior vehicle-flood simulations the paper cites nowhere

Prepared 2026-08-26. **Not applied.** The Overleaf remote shares no ancestor with this
repository, so a push overwrites rather than merges. Apply deliberately, or paste by hand.

## The gap, verified

`overleaf/main:conference_101719_1.tex` carries **14 distinct `\cite` keys** and the shipped
`can_it_ford_references_IEEE.bib` carries **15 entries**. Five prior vehicle fording or wading
simulations appear in neither. A sixth, `xiong2024`, sits in the bib, is cited nowhere, and
therefore does not print, because BibTeX drops uncited entries.

**This gap is load-bearing.** The paper frames its contribution on validation, and Al-Qadami
et al. 2022 claim a moving full-scale vehicle simulation. A reviewer who knows this literature
will notice the omission before they notice anything else.

## How far each was actually read, stated rather than implied

| key | DOI | identity check | depth read |
|---|---|---|---|
| `he2026vehiclewater` | 10.1115/1.4071177 | Crossref, **matched**, high confidence | title, venue, authors only |
| `wasfy2015fording` | 10.1115/DETC2015-47142 | Crossref, **matched**, high confidence | title, venue, authors only |
| `khapane2014wading` | 10.4271/2014-01-0936 | Crossref, **matched**, high confidence | title, venue, authors only |
| `alqadami2022moving` | 10.1111/jfr3.12828 | Crossref, **matched**, high confidence | **full-text excerpts read** |
| `alqadami2023cfd` | 10.3390/su151713262 | Crossref, **matched**, high confidence | **full text read**, local copy |
| `xiong2024` | 10.1029/2023WR036739 | Crossref, **matched**, high confidence | abstract read; **full text also available locally** |

All six: zero retractions, zero corrections, zero expressions of concern. The five new entries
were audited together by Scholar Sidekick and returned `matched: 5, mismatch: 0, ambiguous: 0,
not_found: 0, retracted: 0`.

**Three of the six are cited below on title and venue alone** (`he2026vehiclewater`, `wasfy2015fording`, `khapane2014wading`). The prose is written so that it
does not assert anything about their internal results. Read them before adding any sentence that
does.

## What was read, and what it establishes

**Al-Qadami et al. 2022**, from full-text excerpts: the study's own stated aims are to "employ six
degrees of freedom (DoF) and coupled motion 3D computational fluid dynamics (CFD) simulation to
investigate the responses of the vehicles moving inside floodwaters" and to "assess the different
hydrodynamic forces on a full-scale vehicle body under subcritical and supercritical flows." So it
is 6-DoF CFD on a full-scale moving body. **That is the closest prior work to this project's
framing and it differs on both axes: CFD rather than MPM, and moving rather than stationary.**

**Xiong et al. 2024**, from the Crossref abstract: a two-way coupled 2D shallow-water solver plus
a 3D discrete element method model, with a multi-sphere representation of vehicle shape,
reproducing the Boscastle 2004 flash flood where "over 100 vehicles were moved and carried
downstream."

## Al-Qadami 2023, now read in full, and it calibrates this project's resolution

Read 2026-08-26 from `~/can-it-ford-refs/_fulltext/Alq23_10.3390_su151713262.txt`, 181,816
characters. Read directly rather than relayed:

- Froude number range **0.09 to 2.46**, subcritical through supercritical.
- Floating depth **0.38 m**, buoyancy force **9.2 kN**.
- Sliding instability once the depth-velocity function exceeded **0.36 m2/s**.
- **"the drag force decreased with the increment of the Froude number and flow velocity"**, which
  runs against the intuition behind this project's velocity sweep and should be acknowledged
  rather than quietly contradicted.
- **Mesh cell sizes 0.05 m and 0.025 m.**

**That last line is the useful one and it is not in any prior write-up.** This project's finest
run is `dx = 0.05889 m` (g160). So the closest published CFD comparison works at a cell size
comparable to this project's **coarsest acceptable** rung and refines to less than half of it.
That is a concrete, checkable statement about where this work sits, and it is more informative
than any claim about novelty.

## A trap inside Al-Qadami, do not fall into it

Their text reports a vehicle beginning to float at **0.0457 m** water depth. That is the
**1:10 scale model** of Shah et al. 2020, not a full-scale depth. It is not comparable to the
0.38 m full-scale figure without the scaling applied.

Separately, and already recorded in `CLAUDE.md`: Al-Qadami 2022 reports a minimum depth-velocity
of **0.39 m^2/s** and Al-Qadami 2023 reports **0.36 m^2/s** for the same 0.38 m critical depth.
**Never write "Al-Qadami's D x V" without naming which paper.**

---

## THE EDIT

### 1. Add a subsection to `\section{Prior Work}`, after `\subsection{Flood-Vehicle Stability Criteria}`

```latex
\subsection{Prior Vehicle-Flood Simulations}
Coupled vehicle-floodwater simulation is not new, and this work is not the first to attempt it.
Wasfy et al. coupled multibody vehicle dynamics to smoothed particle hydrodynamics for water
fording \cite{wasfy2015fording}, and Khapane and Ganeshwade set out the practical difficulties of
wading simulation from an automotive engineering standpoint \cite{khapane2014wading}. He et al.
predict vehicle-water interaction in shallow water and report experimental validation alongside
the simulations \cite{he2026vehiclewater}. Xiong et al. couple a 2D shallow-water hydrodynamic
solver two-way to a 3D discrete element model, representing vehicle shape by a multi-sphere
method, and reproduce the Boscastle 2004 flash flood in which over one hundred vehicles were
entrained and carried downstream \cite{xiong2024}. Al-Qadami et al. are the closest in framing:
they run six-degree-of-freedom coupled 3D CFD on a full-scale vehicle body moving through
floodwater under subcritical and supercritical flow \cite{alqadami2022moving}, and follow it with
a CFD study of stability for vehicles exposed to water flows \cite{alqadami2023cfd}.

Two things follow, and both narrow what this paper claims. First, the pipeline is not the
contribution: coupled vehicle-flood simulation has been done, with CFD, with SPH and with
DEM. Second, the closest prior work differs from this one on both axes that matter here.
Al-Qadami et al. simulate a \emph{moving} vehicle with CFD; the runs reported below hold a
\emph{stationary} vehicle as a free rigid body in a material point method tank, which is the
configuration AR\&R's own thresholds were measured in. The contribution claimed here is the
comparison itself, a published decision rule tested against simulation on identical inputs with
every threshold and gate stated, and not the simulation capability.
```

### 2. This resolves `xiong2024`

It is now cited, so BibTeX will print it. **Do not remove it.** It is genuine prior art on
coupled vehicle-flood simulation, and it is already reference 7 on the printed poster, so
removing it from the paper would put the two deliverables into conflict.

### 3. Append the five new entries

Take them verbatim from `paper/prior_art_additions.bib`. They were generated from live Crossref
records and normalised to ASCII, because en-dashes and U+2010 hyphens in the Crossref names
either break `pdflatex` or silently mangle the author list.

### 4. Acknowledgment, a separate obligation, same file

The upstream CCSA README asks that CCSA at GMU and the FHWA be acknowledged in papers and
publications. `FHWA` currently appears **zero times** in the tex. Append to
`\section*{Acknowledgment}`:

```latex
The 2010 Toyota Yaris finite element model used in this work was developed by researchers at the
Center for Collision Safety and Analysis (CCSA) at George Mason University, under sponsorship of
the Federal Highway Administration (FHWA). We acknowledge CCSA at GMU and the FHWA, as requested
by the model distributors. Neither CCSA nor FHWA assumes any responsibility for the validity,
accuracy, or applicability of the results presented here.
```

The Yaris-only wording is correct: `Silverado` appears exactly once in the tex, in Future Work,
and no Silverado-derived result is reported.

## Before pushing

Confirm the target explicitly. The Overleaf remote shares no ancestor with this repository, so a
push **overwrites**. Word count will rise by roughly 260 words, which matters if the venue caps
length.
