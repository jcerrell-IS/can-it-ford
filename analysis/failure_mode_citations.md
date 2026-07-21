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

1. DOIs for Xia et al. 2011, Xia et al. 2013, and Kramer et al. 2016 are not yet
   confirmed here and should be filled in and checked against the primary papers before
   any of this reaches a poster, the paper, or Kumar.
2. Year reconciliation: the project already cites "Xia et al. 2014"
   (DOI 10.1007/s11069-013-0889-2) in `SESSION_STATE.md`, `README.md`, and
   `PROVISIONAL_STATUS.md` for incipient-motion physics. The 2011 (slide) and 2013
   (topple) attributions above may or may not be the same Xia work; the existing DOI's
   `-013-` stem suggests a 2013 online-first article assigned to a 2014 issue. Confirm
   whether these are one paper or several before citing distinct years.
3. Froude gating is described in the literature (Kramer et al. 2016) but is NOT computed
   in code. `failure_modes.py` uses a force-direction proxy (a nonzero upward net force
   for FLOAT, a nonzero downstream net force for SLIDE) because flow depth, flow
   velocity, and a vehicle length scale are not passed into the classifier. This is a
   deliberate approximation, not a computed Froude number, and should be labeled as such
   anywhere the Froude framing is claimed.
