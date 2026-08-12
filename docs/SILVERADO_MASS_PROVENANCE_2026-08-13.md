# Silverado mass provenance: four numbers, one vehicle, and an inverted hierarchy

Written 2026-08-13. Every claim below was read live from the source named, on the
date named. Nothing here is carried from a summary, a prior session's confidence,
or another audit's conclusion.

## Summary

Four different masses are attached to one Silverado hull across this project.
Three of them are defensible numbers with real sources. The defect is not that a
wrong number was used, it is that `docs/MULTIGEOM_VALIDATION_2026-08-11.md`
labels the weakest-provenance figure "primary" and demotes the strongest one to
`mass_alt_kg`, which inverts the provenance hierarchy.

A secondary finding, independent of the mass question and arguably more useful:
the licence blocker currently applied to this hull appears to be applied to the
wrong Silverado, and may not apply at all.

## A retraction first

An earlier statement in this session claimed that the multigeom run's 2337.0 kg
"is the Dodge Ram's mass applied to a Silverado hull." **That is withdrawn. It is
not supported.** The run's own `summary.json` records
`mass_source = "AR&R large_4wd class figure (gates_both_scenarios.py:23)"`, which
is neither the Ram nor any Silverado spec. The Ram also weighing 2337 kg is a
coincidence, and as shown below it is not even the only coincidence at that value.
The error was reasoning from a number's value instead of reading the field that
records where it came from.

## The four numbers

| kg | What it actually is | Source, read live |
|---|---|---|
| **2270.0** | This specific vehicle's mass, from its own FE deck header | `silverado-coarse-v3a.key:28`, as cited by `MULTIGEOM_VALIDATION_2026-08-11.md` section 1 |
| **2337.0** | The AR&R **large_4wd class** figure used by the canonical 17-run sweep | `renders/yaris_render_s1/gates_both_scenarios.py`, `RUNS` table; cited by the run's own `mass_source` field |
| **2337** | 2007 Chevrolet Silverado curb test weight, CCSA vehicle description table | `vehicle_data_master_reference_2026-07-21.json`, key `pickup_2007_chevrolet_silverado`, on Vista |
| **2367** | 2014 Chevrolet Silverado 1500, a different vehicle | External report `b0d2664f`, line 14 |

For completeness, because it caused the original confusion: `b0d2664f` line 13
gives the **2018 Dodge Ram 1500** as 2,337 kg, class 2270P. The 2014 Silverado is
also class 2270P. **2270P is an NHTSA/MASH vehicle-class code, not a vehicle
identity**, and several pickups carry it. Any argument that reasons from 2270P to
a specific vehicle is invalid.

## Which mass each run actually used

Read live from Vista `summary.json` files, 2026-08-13:

```
class_specific_2026-08-08/class_silverado_g64   mass_kg = 2270.0
  hull_source  $WORK/hulls/silverado_g96_pd8_coarse_watertight.ply
  realized_rho 285.7625139603319

render_s2/multigeom_2026-08-08/g64_silverado    mass_kg = 2337.0
  hull_source  $WORK/can-it-ford/vehicle_geometry_research/silverado_g96_pd8_coarse_watertight.ply
  mass_source  "AR&R large_4wd class figure (gates_both_scenarios.py:23)"
  mass_alt_kg  2270.0
  vehicle_class large_4wd
  realized_rho 294.19691415211264

render_s3_hullsweep/hull_silverado_g96          mass_kg = 1100.0
```

Both hulls are the same file. `MULTIGEOM_VALIDATION_2026-08-11.md` section 1
records `sha256sum` over all four paths and finds the digests pairwise identical,
so the two paths are one mesh and no run used a mesh it did not report. That part
of the document is sound and is not in question here.

## The defect

`MULTIGEOM_VALIDATION_2026-08-11.md` section 2 presents this table:

```
| Silverado mass | 2270.0 kg (primary) | 2337.0 kg (primary), 2270.0 as `mass_alt_kg` |
```

Read left to right as class-specific then multigeom, this says the multigeom run
promoted 2337.0 to primary and demoted the deck-header 2270.0 to an alternate.

That is backwards. The same document, one section earlier, states the correct
hierarchy in its own words:

> **Mass sourcing is asymmetric and must be labelled that way.** Silverado
> 2270.0 kg is primary-sourced from the deck header (`silverado-coarse-v3a.key:28`).

A deck header is the vehicle's own mass, from the FE model the hull was extracted
from. The AR&R `large_4wd` figure is a **regulatory stability class threshold**,
not a property of any vehicle. `vehicle_params.py:218-222` defines `large_4wd`
purely as limit values (`depth_m` 0.50, `velocity_ms` 3.0, `haz_m2s` 0.60,
`kerb_weight_kg_min` 2000), and `vehicle_params.py:42-46` warns explicitly that
the AR&R class keys and the `VEHICLE_PARAMS` keys are two taxonomies and are
**not interchangeable**. Using a class figure as a specific vehicle's mass crosses
exactly the boundary that warning draws.

Consequence for the document's own argument: section 2 concludes the two datasets
"differ by 2.9 percent (Silverado)" in mass and 7.6 percent in displacement, and
uses that to argue they are a different-mass companion rather than replicates.
The conclusion survives, because they genuinely do differ. But the 2.9 percent is
a gap between a vehicle mass and a class threshold, not between two candidate
vehicle masses, and it should not be described as a mass disagreement.

## A separate, unresolved conflict inside the project

The deck header and the CCSA vehicle description table disagree about the same
vehicle:

```
2270.0 kg   silverado-coarse-v3a.key:28          (deck header)
2337   kg   pickup_2007_chevrolet_silverado      (CCSA description table, via
                                                  vehicle_data_master_reference_2026-07-21.json)
```

That is a 2.95 percent disagreement on one vehicle from two primary sources, and
no document in this repo currently records it. It is not resolved here. Whoever
resolves it should open the deck rather than reason from either summary.

Note the trap this creates: 2337 is reachable from **two** unrelated directions,
the AR&R class figure and the CCSA table for the 2007 Silverado, plus a third
from the Dodge Ram. A future audit that finds 2337 and concludes "this traces to
the 2007 Silverado" would be right by accident, since the run that used it cites
the AR&R table.

## Secondary finding: the licence blocker may be on the wrong Silverado

`MULTIGEOM_VALIDATION_2026-08-11.md` section 1 carries this caution forward:

> CCSA-hosted decks (E8 names Rogue, Ram, 2014 Silverado) are licence-silent,
> unlike NHTSA-hosted copies.

and applies it to its own Silverado. But its Silverado deck is
`silverado-coarse-v3a.key`, and the Vista master reference gives the coarse v3a
URL for the **2007** Chevrolet Silverado
(`https://media.ccsa.gmu.edu/model/2007-chevrolet-silverado-coarse-v3a.zip`).

`b0d2664f` line 16 draws the line the other way for that vehicle:

> Practical verdict: NHTSA-hosted models (**older Yaris, 2007 Silverado**) are
> safe to redistribute; CCSA-hosted models (Rogue, Ram, 2014 Silverado) require
> [...] written permission before publishing derived geometry.

So the 2007 Silverado sits in the safe set, and the licence-silent set names the
**2014** Silverado, a different vehicle at a different mass (2,367 kg). If the
hull here is the 2007 coarse v3a, register E8's blocker does not reach it.

**This is inferred, not proven.** The chain is deck filename to master-reference
URL, and no one has opened the deck or diffed it against the 2007 download to
confirm. It matters because E8 gates register item 11 and blocks item 10, the
DesignSafe DOI. Confirming it would unblock the Silverado half of that. The Rogue
is unaffected and stays blocked either way.

## What to do

1. **Correct the section 2 table** in `MULTIGEOM_VALIDATION_2026-08-11.md` so
   2270.0 is labelled primary and 2337.0 is labelled as the AR&R `large_4wd`
   class figure, matching what section 1 and the run's own `mass_source` already
   say. Do not change any run, any CSV, or any verdict. No number is wrong, only
   the label.
2. **Record the 2270 against 2337 deck-vs-table conflict** in the register, as an
   open item. It is currently recorded nowhere.
3. **Settle which Silverado the hull is**, by opening `silverado-coarse-v3a.key`
   or diffing against the 2007 download. This is the one that unblocks something.
4. **Do not touch the verdicts.** Every Silverado run returns NO-FORD at every
   mass tried, 1100.0, 2270.0 and 2337.0 alike, so no verdict in this project
   turns on which figure is used. The defect is in provenance labelling, not in
   any published result.

## Sources, all read live 2026-08-13

- `docs/MULTIGEOM_VALIDATION_2026-08-11.md`, `HEAD` blob, sections 1 and 2
- `data/class_specific_runs_2026-08-08.csv`
- Vista `class_specific_2026-08-08/class_silverado_g64/summary.json`
- Vista `render_s2/multigeom_2026-08-08/g64_silverado/summary.json`
- Vista `render_s3_hullsweep/hull_silverado_g96/summary.json`
- Vista `can-it-ford-OLD-pre-purge/reference_data/vehicle_data_master_reference_2026-07-21.json`
- `renders/yaris_render_s1/gates_both_scenarios.py`, `RUNS` table
- `vehicle_params.py:42-46` and `:218-222`
- `~/Downloads/compass_artifact_wf-b0d2664f-3b65-5bfe-8e3f-f06e77a59f79_text_markdown.md`,
  lines 13, 14, 16
- `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`, E6a and E8
