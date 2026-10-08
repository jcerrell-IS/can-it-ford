# How this work compares with published studies

This page lists where my simulation setup and results line up with published measurements, where
they fall short, and how the project sits next to earlier vehicle-in-floodwater work. Every number
here was checked against the full text of the cited paper and against a file in this repository.
None of it is a validation: no simulation here has been compared against a matching experiment and
passed.

## Where it lines up

**The car's mass distribution matches a measured 2010 Yaris.** The CCSA/NCAC model release
([doi:10.13021/G8JS5D](https://doi.org/10.13021/G8JS5D), slide 7) gives a measured inertia of
388 (roll), 1498 (pitch) and 1647 (yaw) kg m². The solver's particle cloud of the hull gives
395.0, 1501.5 and 1685.4 kg m², within 0.2 to 2.3 percent. A plain box of the same size would be
19 to 26 percent off. Source: the notes in [`vehicle_params.py`](../vehicle_params.py).

**The density is what the inputs say it should be.** 1100 kg over the hull's 3.542739 m³ is
310.5 kg/m³, and every one of the 17 runs uses the same hull volume
([`data/all_runs_inventory.csv`](../data/all_runs_inventory.csv), checked by
[`tests/test_runs_inventory.py`](../tests/test_runs_inventory.py)).

**The move-or-stay pattern is in the same order as a published CFD study, and follows a published
flume finding.** These 17 runs were later withdrawn as verdicts (they measure the start of the flow,
see [`FINDINGS.md`](../FINDINGS.md)), so this is a sanity check on ordering, not a result.

- Al-Qadami et al. 2023 ([doi:10.3390/su151713262](https://doi.org/10.3390/su151713262), Table 2)
  simulated a small car that stayed put at 0.29 m and 0.66 m/s and slid at 0.30 m and 1.35 m/s.
  In my runs at 0.294 m, the car stayed put at 0.5 m/s and moved at 1.5 m/s. Their car (a Perodua
  Viva) and floor friction differ from mine.
- Kramer et al. 2016 ([doi:10.1016/j.ijdrr.2016.04.003](https://doi.org/10.1016/j.ijdrr.2016.04.003),
  section 2.4) found in a flume that a car's instability is mostly about buoyancy below a Froude
  number of about 0.5, and that sliding takes over above it. My only run where the car stayed put is
  at Froude 0.29; every run where it moved is between 0.59 and 1.77 (Froude = speed / sqrt(g x depth),
  from the inventory).

**Refining the grid keeps the decision but not the size of the motion.** Across the three grids
(48, 64, 96 cells) the move-or-stay answer is the same while the displacement changes by 1.9 to 4.9
times. Syamlal, Celik and Benyahia 2017
([doi:10.1002/aic.15868](https://doi.org/10.1002/aic.15868)) note that a quantity that is still
changing in time is not expected to converge under grid refinement, which is why I quote the
decision and not the displacement.

## Where it falls short

- **Resolution.** Al-Qadami et al. 2023 tested four mesh sizes (0.1 to 0.025 m) and chose 0.05 m
  because it differed from 0.025 m by an average of 1 percent. My grid spacing is about 0.15 m at
  64 cells, the water is about 2 cells deep, and the results are not grid-converged.
- **Sound speed.** Particle methods for water usually set the numerical sound speed at 10 or more
  times the fastest flow. Mine is below that in 15 of the 17 runs, as low as 4.3 times.
- **Water inside the car.** Kramer et al. 2016 found a real car floated 12 to 18 cm deeper than a
  sealed model predicted. My hull is not sealed at the cabin and underbody, so it does not match
  either case exactly.
- **The movement threshold.** I call a run "moved" when the car drifts more than 0.05 m. That
  number is a project choice with no published source.
- **No benchmark has passed.** A public floating-sphere dataset with about 0.3 percent uncertainty
  (Kramer et al. 2021, [doi:10.3390/en14020269](https://doi.org/10.3390/en14020269)) exists and has
  not been run here yet.

## Earlier work on vehicles in floodwater

Simulating a vehicle in floodwater is not new. Earlier studies include Wasfy et al. 2015 (particle
water with a full multibody vehicle, [doi:10.1115/DETC2015-47142](https://doi.org/10.1115/DETC2015-47142)),
Khapane and Ganeshwade 2014 (CFD wading, [doi:10.4271/2014-01-0936](https://doi.org/10.4271/2014-01-0936)),
Pazouki, Jayakumar and Negrut 2016 (particle water with point-cloud coupling), Al-Qadami et al. 2022
(full-scale CFD of a moving car, [doi:10.1111/jfr3.12828](https://doi.org/10.1111/jfr3.12828)) and
He et al. 2026 (checked against flume experiments, [doi:10.1115/1.4071177](https://doi.org/10.1115/1.4071177)).
A learned model that predicts loads on a vehicle in shallow water also exists
([doi:10.1115/1.4064971](https://doi.org/10.1115/1.4064971)).

What this project adds is narrower:

- It uses the material point method, which none of the studies above uses (in the project's
  literature index, not a search of everything published).
- It checks three answers to the same question (a depth rule, the AR&R guideline, and a simulation)
  against each other on the same 70 cases.
- It keeps a public record of what each run saved, what was filled in later, and which results
  were withdrawn and why.

He et al. 2026 compared their simulations against experiments and this project has not, so it
claims no experimental validation. It also does not simulate a car driving under its own power.
