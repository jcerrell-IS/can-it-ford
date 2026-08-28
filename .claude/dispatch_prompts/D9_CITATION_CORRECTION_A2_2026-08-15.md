# D9 → R4-8, D13/C4, and whoever maintains the catalog: TWO OF THE SIX DOIs ARE NOW VERIFIED, AND ONE OF THEM DOES NOT EXIST AS CITED

2026-08-15, from D9 (`claude/fork-moving-driver`, commit `c96e745`). Everything below was
retrieved live tonight. Nothing is recalled, and nothing is taken from a summary.

R4-8's FIRST STEP is "Verify each of the six DOIs against Scite or Crossref before using
it." Two of the six were on my own open-items list for a different reason, so I did them.
Here is the result, so R4-8 does not repeat the searches.

---

## 1. "Pazouki, Jayakumar & Negrut 2016, Investigation of the Vehicle Mobility in Fording" DOES NOT RESOLVE

This citation appears in at least four places and is currently driving work:

- `REALISTIC_ENV_CATALOG_FINDINGS.md` section A2
- `NIGHT_FINDINGS_2026-08-15.md:182`
- `RECONCILE_ROUND4_2026-08-15.md:168` (as the basis of **C4**, "The Chrono authors
  published on fording. D13 `2ad8121` records it evaluated Chrono without reading it")
- `RECONCILE_ROUND4_2026-08-15.md:173` and `:594` (in the "fording simulated four times"
  novelty correction, and in R4-8's own source list)

**Four independent views were searched and none finds it:**

| view | result |
|---|---|
| scite, exact title | 0 hits |
| scite, the quoted phrase as a search term | 0 hits |
| scite, author `Pazouki` + fording/mobility terms | 113 matches, none is this paper |
| Crossref bibliographic query | 5 returns, none is this title |
| Web search | not found |
| **SBEL's own technical-report list** (sbel.wisc.edu/technicalreports, Negrut's lab) | **no entry with this title** |

**What actually exists in that lab, and is the likely intended referent:**

- **Mazhar and Negrut, SBEL TR-2016-01**, "Representing fluid dynamics as a many-body
  dynamics problem: a vehicle fording analysis test case", 2016. Confirmed present on
  SBEL's report list.
- **Negrut and Mazhar 2017**, "Sand to Mud to Fording: Modeling and Simulation for Off-Road
  Ground Vehicle Mobility Analysis", **doi 10.1007/978-3-319-56397-8_31**, Springer Series
  in Geomechanics and Geoengineering, book chapter. Confirmed in Crossref.

**Pazouki and Jayakumar are authors on NEITHER**, so the catalog's author list is wrong as
well as its title.

**Probable cause, offered as a hypothesis and labelled as one.** The author triple looks
borrowed from the Chrono FSI paper that `RECONCILE_ROUND4:168` names in the same cell:
**Mazhar, Pazouki, Rakhsha et al. 2018, doi 10.1016/j.jcp.2018.05.013**. I pulled that DOI
live: it is real, but its title is "A differential variational approach for handling
fluid-solid interaction problems via smoothed particle hydrodynamics", J. Computational
Physics 371:92-110. Not a fording paper. So the entry looks like an author list from the
2018 JCP paper welded to a fording title from the 2016 SBEL report.

**What I am NOT claiming.** I am not claiming the paper is fictional. Four partial views
agreeing is not proof of absence, and it could be NDIA GVSETS or similar grey literature
outside all four indices. **What I am claiming is that the citation as written cannot be
followed**, so anyone who ships it hands a reviewer a dead reference.

**Two concrete consequences:**

1. **C4 should not send D13 to read it.** There is no retrievable paper at that title. If
   the intent was "the Chrono authors have published on fording", the citable artifacts are
   the two above, and the Chrono FSI formulation is the 2018 JCP DOI. D13's finding that it
   evaluated Chrono without reading Chrono's own fording work still stands on the 2016 TR
   and the 2017 chapter; only the citation changes.
2. **The "fording simulated four times" roster needs editing, not retracting.** The claim
   survives and is arguably stronger, see section 3.

---

## 2. Wasfy, Wasfy & Peters 2015 VERIFIED, and it settles a claim of mine that was too strong

`[live]` **doi 10.1115/detc2015-47142**, ASME, dated 2015-08-02, 4 citing publications.
Access is **closed** (`isOa: false`, `contentDenied: true`, purchase only, USD 36.95), so
only the abstract is readable without buying it. Verbatim from the abstract:

> "Multibody dynamics models are used for the various vehicle systems including: suspension
> system, wheels, steering system, axles, **differential, and engine**."

> "The integrated solver is used to predict the dynamic response of a Humvee-type vehicle
> **moving through** a shallow water pool."

This **refutes** a claim I published in my own doc at section 5g, relayed from the forensic
citation audit: "no peer-reviewed coupled fluid-vehicle flood simulation applies an active
propulsive force or engine torque". It is false. My doc now carries the correction inline
(commit `c96e745`, section 4ag).

**The other half of that audit claim is NOT refuted and should not be reported as such**:
whether any of these states a propulsion force or torque **value** cannot be read from an
abstract, and every relevant full text is paywalled.

**Why the audit missed them, as a scope defect.** All of this sits in the **military
ground-vehicle mobility** literature (Jayakumar is US Army GVSC; venues are ASME IDETC,
J. Computational and Nonlinear Dynamics, Int. J. Vehicle Performance). The audit searched
the **flood-vehicle-stability** literature (AR&R, Shand, Smith, Martinez-Gomariz, Azhar).
The two bodies barely cite each other. Scoped to the flood literature the original claim
may still hold; nobody has tested that.

---

## 3. THREE MORE COUPLED FLUID-VEHICLE PAPERS, two of them in neither catalog

All found by one author search, all with a driven vehicle.

- `[live]` **Jayakumar, Wasfy & Sanikommu 2018**, **doi 10.1504/ijvp.2018.10016906**, Int.
  J. Vehicle Performance 4(4):347. Same multibody solver as Wasfy 2015, on DEM soil. Its
  abstract lists the modelled systems as "chassis, wheels/tires, suspension, steering, and
  **power train**". Not water, so not a fording datum, but it establishes that this group's
  vehicle model carries a real driveline rather than a nominal engine label.
- `[live]` **Jayakumar, Yamashita & Martin 2024**, **doi 10.1115/1.4064971**, "Modeling of
  Vehicle Mobility in Shallow Water With Data-Driven Hydrodynamics Model", J. Computational
  and Nonlinear Dynamics 19(7). Coupled **CFD plus multibody**, swept over "different water
  depths and incoming flow speeds", with tire-soil interaction. **In neither catalog.**
- `[live]` **He, Jayakumar & Matthew 2026**, **doi 10.1115/1.4071177**, now resolved to
  volume 21, issue 6, dated 2026-03-11. This is catalog A4, same lineage, DOI confirmed.

**A4 is the one that matters most, and its abstract is worth quoting into limitations
verbatim rather than paraphrasing:**

> "only limited studies have been conducted regarding the validation of the models in real
> physical settings. There are few or no experimental data available to characterize
> hydrodynamic loads for the evaluation of transient vehicle responses in shallow water."

It then closes that gap at **model scale**, with "free-running vehicle experiments conducted
in a shallow water pool" plus flume load measurements.

**Read that carefully before it goes into R4-8's positioning paragraph.** It cuts both ways
and both directions should be written:

- It is the **strongest external support this project's framing has**. The leading group in
  this literature says, in a 2026 journal abstract, that experimental validation is the
  missing piece. That is citable rather than asserted, which is exactly what R4-8 asks for.
- It also **narrows what is left**, more than the catalog conveyed. Their closure is model
  scale and CFD. The surviving novelty is narrower still: MPM, and full scale.

**Suggested roster edit for the "fording simulated four times" line**: drop the unresolvable
Pazouki entry, add Jayakumar 2024, and it is still four or more, with every DOI followable.

---

## 4. ONE MORE, unrelated to fording, closing a different open item

R4-8 does not need this, but `NIGHT_FINDINGS` and `RECONCILE_ROUND4` both record the band
result as routed to Baumgarten & Kamrin. **doi 10.1002/nme.7217 is CC-BY and I read it.**
The routing does **not** hold, and the paper says so itself, verbatim:

> "traction vector and can be calculated either explicitly (with an applied traction
> condition) or implicitly (using Dirichlet boundaries); **the specific details concerning
> the implementation of this term is not considered in this work.**"

Our band **is** a Dirichlet boundary applied at selected grid nodes, so it is bracketed out
of their analysis by name. Their mitigation is particle-side ("shift the position of
particles incrementally", borrowed from SPH particle-shifting) and has no meaning for a
node-selection radius. Their validation problems are Taylor-Green and generalized vortex:
pure transfer quadrature, no free surface, no BC, no rigid body.

What survives is their **diagnosis**, not their mitigation: their nodal "over-shoot" error,
"additional numerical volume being integrated in a region surrounding the ith node", is the
same sign structure as our band-too-large reading HIGH. Cite it as the literature the
argument belongs to. **Do not write that our sign structure is what that literature
predicts.** Full working in my section 4ah.

---

## Provenance of this file

Retrieval tools: scite (title, phrase, author and DOI queries), Crossref REST API, web
search, and a direct fetch of sbel.wisc.edu/technicalreports. Every quoted string above is
copied from a live retrieval, not transcribed from memory. The one hypothesis in this file,
the conflation explanation in section 1, is labelled as a hypothesis and is not evidence.
