# Failure-mode classifier: taxonomy and citations

Companion note to `simulation/failure_modes.py`. The classifier carries no inline
comments or docstrings by project house rule, so the reasoning and its sources live
here instead.

## Taxonomy: three hydrodynamic instability modes plus a stable baseline

The classifier follows the three-mode hydrodynamic vehicle-instability taxonomy of
Shand et al. 2011 (Australian Rainfall & Runoff, Project 10, "Appropriate Safety
Criteria for People and Vehicles"). Shand recognizes three instability modes, not four.
The fourth label in the code, STUCK, is not a fourth force-balance mode: it is the
stable / no-instability baseline reported when none of the three criteria trip.

| Code mode | Physical meaning | Criterion in code | Primary source |
|-----------|------------------|-------------------|----------------|
| STUCK | Stable, no instability onset | none of the three below sustained | Shand et al. 2011 (baseline = absence of the three) |
| SLIDE | Hydrodynamic drag exceeds tire-ground friction, vehicle slips downstream | sustained surge (cross-stream) drift and surge speed above tolerance, with a downstream driving force present | Xia et al. 2010 |
| TOPPLE | Overturning moment exceeds the vehicle's stability limit | sustained surge acceleration (in g) at or above the vehicle Static Stability Factor (SSF) | Xia et al. 2013 |
| FLOAT | Buoyancy plus hydrodynamic lift exceeds vehicle weight, vehicle lifts off | sustained vertical lift and rise speed above tolerance, with an upward driving force present | Kramer et al. 2016 |

## Severity ordering

`MODE_SEVERITY = (SLIDE, TOPPLE, FLOAT)`, ascending. FLOAT is the most severe: once a
vehicle floats it has lost all ground contact and is fully carried by the flow, whereas
sliding and toppling retain partial contact. When more than one criterion trips in a
run, the classifier reports the single highest-severity mode reached, together with the
frame index and time at which that mode's criterion was first sustained.

Kramer et al. 2016 is cited specifically for the physical distinction between the
sliding and floating regimes being governed by the flow Froude number (the ratio of
flow inertia to gravity), which is what justifies treating float as a separate, more
severe end state rather than a variant of slide.

## Magnitude reporting

For any tripped mode the classifier reports the threshold exceedance two ways, per
Kumar's July 3 request:

- percent over threshold: `(value / threshold - 1) * 100`
- absolute distance past threshold: `value - threshold`, in the mode's native units
  (metres for SLIDE and FLOAT, g for TOPPLE)

STUCK reports no exceedance magnitude, because nothing was violated.

## Open provenance items (do not treat as verified until closed)

These are flagged rather than asserted, consistent with the project's DRIFT_THRESHOLD
provenance discipline.

1. DOIs for Xia et al. 2010, Xia et al. 2013, and Kramer et al. 2016 are now confirmed in the bib (xia2010, xia2013).
   confirmed here and should be filled in and checked against the primary papers before
   any of this reaches a poster, the paper, or Kumar.
2. Year reconciliation: the project already cites "Xia et al. 2014"
   (DOI 10.1007/s11069-013-0889-2) in `SESSION_STATE.md`, `README.md`, and
   `PROVISIONAL_STATUS.md` for incipient-motion physics. The 2010 (slide) and 2013
   (topple) attributions above may or may not be the same Xia work; the existing DOI's
   `-013-` stem suggests a 2013 online-first article assigned to a 2014 issue. Confirm
   whether these are one paper or several before citing distinct years.
3. Froude gating is described in the literature (Kramer et al. 2016) but is NOT computed
   in code. `failure_modes.py` uses a force-direction proxy (a nonzero upward net force
   for FLOAT, a nonzero downstream net force for SLIDE) because flow depth, flow
   velocity, and a vehicle length scale are not passed into the classifier. This is a
   deliberate approximation, not a computed Froude number, and should be labeled as such
   anywhere the Froude framing is claimed.

## Separate citation audit: coup_friction = 0.55 (Azhar et al. 2023). Status: UNRESOLVED

Scope note: this item is about the coupling-friction parameter, not the failure-mode
taxonomy above. It is recorded here because this is the project's active citations doc.

The claim under audit, as it currently appears in code and docs (README.md,
PROVISIONAL_STATUS.md, kumar_july9_update/STATUS.md, and the live sim files
`simulation/can_it_ford_L2_mpm.py` line 28 and `..._ytest.py` line 45): coup_friction is
set to 0.55, attributed to Azhar, Pauwels & Bui 2023 (DOI 10.1111/jfr3.12885) as "the
exact matched-scale-model coefficient."

Verified live (July 20, via scite metadata plus Exa/WebSearch):

- The DOI is correct and resolves to the cited paper: Azhar, Pauwels & Bui 2023,
  "Confirmation of vehicle stability criteria through a combination of smoothed particle
  hydrodynamics and laboratory measurements," Journal of Flood Risk Management 16(2):e12885,
  CC BY-NC-ND (open access). Authors and journal match the citation exactly.
- The method matches how it is cited: DualSPHysics (SPH) plus a 1:14 scale physical model,
  Toyota Yaris. Road-condition-dependent friction is a genuine theme of the paper (the
  abstract states the ARR stability curve "can shift depending on the road conditions that
  affect the vehicle's sliding mechanism").

NOT verified (this is the open item):

- The exact numeral 0.55 could NOT be confirmed in the primary full text through available
  tools. Wiley returns HTTP 403 to crawlers, Ovid returns HTTP 402 (paywall), and scite has
  no open-access full-text index for this paper. The only source asserting 0.55 is a
  machine-generated web-search summary, which reported "a friction coefficient of 0.55
  between the tyre and pavement... could drop to as low as 0.30 in case of poor road
  conditions." That is a secondary paraphrase, not a verified quote, so it does not close the
  audit. The user's original concern (0.55 seen only in an abstract snippet, never in the full
  text) therefore stands: whether 0.55 is a stated model input or an inference from the
  paper's SPH calibration range remains OPEN.

Context on plausibility (does not substitute for confirmation): 0.55 sits squarely inside
the tyre-ground friction range reported across the flood-vehicle literature. Martinez-Gomariz
et al. measured 0.52-0.62 for 1:14 scale models; Smith et al. 2017 measured about 0.76 full
scale; Smith et al. adopted a conservative 0.3; Toda et al. measured 0.26-0.57 for a sedan
depending on flow orientation. So 0.55 is physically defensible and in-range, but in-range is
not the same as "this is the number Azhar used."

Standing conceptual caveat (independent of the numeral, do not lose it when this closes):
even if 0.55 is confirmed as Azhar's physical Coulomb tyre-pavement coefficient, Genesis
`coup_friction` is a numerical coupling-impulse coefficient, not a Coulomb friction
coefficient. Feeding one into the other is a separate open modeling question, already flagged
in the provenance-audit skill and the COUPLED VARIABLES notes.

Per instruction, the code value was NOT changed. It remains 0.55.

To close this item, get the primary full text one of these ways and read the SPH/contact
setup section for the friction value and how it was chosen (set input vs calibrated):
- The open-access Wiley PDF via an authenticated route (browser login), not a crawler.
- Azhar's open Monash PhD thesis, the fuller version of the same work: DOI 10.26180/25100753
  (Monash Bridges / figshare), download the thesis PDF and read the model-setup chapter.
- The 2026 follow-up paper (DOI 10.1111/jfr3.70181) reuses the same validated SPH model and
  may restate the friction value in its methods.
