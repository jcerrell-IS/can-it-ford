# Figure: traction_bias.pdf

## Caption

**One-sided resolution bias in modeled traction.** Left: solid volume below the 0.30 m
waterline, produced by the column-fill solidifier at three MPM grid resolutions, against the
true submerged volume of the watertight Yaris mesh (0.432718 m3, dashed). Every resolution
over-fills, by 1.95x, 1.49x, and 1.17x respectively. Right: the traction available at the
tire-road interface that follows from those volumes, at mu = 0.55 and a 1100 kg vehicle,
against the value implied by the true geometry (3495.2 N, dashed). All three resolutions
understate traction, by 60%, 30%, and 8.3%. The 2.30x spread across resolutions is therefore
a one-sided bias, not an uncertainty band: the true value lies outside the measured range
entirely, not within it, and refining the grid moves the estimate toward truth from one side
only. The shaded region shows that friction-coefficient uncertainty alone spans 1906.5 N to
3495.2 N at the true geometry, a 1.83x spread, so grid resolution is not the only, and not
obviously the dominant, source of uncertainty in this quantity.

## Method

True submerged volume was obtained by clipping the watertight mesh (655,308 faces,
`trimesh.is_watertight = True`, total volume 3.542739 m3) against the horizontal waterline
plane and integrating with the divergence theorem using the field F = (x, 0, 0), whose flux
through a horizontal cap is identically zero, so no cap polygon triangulation is required.
The routine validates against the closed mesh: evaluated above the roofline it returns
3.542739 m3, matching trimesh's own volume to six decimal places, and evaluated at the road
plane it returns exactly 0.

The mesh was first transformed into the same frame the simulation places it in: rotated to
z-up, rotated about z so the long axis lies along y, centered in x and y, and translated so
its lowest point sits at z = 0.

The comparison is made at z = 0.294426 m rather than z = 0.300000 m. The solidified particle
sets terminate on a cell boundary, and at all three resolutions that boundary falls at
grid_lim/32 = 0.294426 m. Comparing there rather than at the nominal waterline removes a
discretization offset that would otherwise be charged to the over-fill. At the nominal
0.30 m plane the true submerged volume is 0.452204 m3 and the corresponding traction is
3495.2 N, which is the value plotted.

## Assumptions

Ten assumptions, stated in full. Every one of them affects the plotted numbers.

1. Water density is 1000 kg/m3, fresh and clean. Sediment-laden floodwater runs roughly 1050
   to 1200 kg/m3, which would raise buoyancy and lower traction.
2. Gravitational acceleration is 9.81 m/s2.
3. Vehicle mass is 1100 kg, taken from `vehicle_params.py` `compact_sedan.mass_kg`, sourced
   from the NCAC/CCSA 2010 Toyota Yaris FE deck header. This is curb weight: no occupants,
   no cargo, no fuel load beyond what the deck assumes.
4. The friction coefficient is mu = 0.55, which is the **upper** bound of the 0.30 to 0.55
   range this project cites from Azhar et al. 2023. It is therefore the most
   traction-favorable value available, and the reported traction is a best case in mu.
5. The calculation is purely hydrostatic. No drag, no lift, no dynamic pressure, and no
   momentum flux are included. It is valid only at zero flow velocity. Any real current adds
   a downstream force that opposes the available traction computed here.
6. **The vehicle body is treated as a sealed solid that displaces water over its full
   submerged envelope.** A real vehicle floods through door seals, vents, and body cavities
   within seconds of entering standing water, after which the displaced volume collapses
   toward the sealed volumes only. This assumption inflates buoyancy and therefore
   *understates* traction. **It pushes in the opposite direction to the column-fill
   over-fill**, which also inflates buoyancy and understates traction, so the two do not
   cancel: they compound. Neither is corrected for in the plotted values.
7. The vehicle sits level on a flat, rigid road surface, with no suspension compression and
   no tire sinkage into the bed.
8. The road plane is taken as the minimum z of the oriented mesh, that is, the tire contact
   plane.
9. Normal force is computed as N = W - F_b, which places buoyancy and weight on a common
   vertical line. No pitch or roll redistribution of load between axles is modeled.
10. Traction is computed as mu * N applied to the total normal force, which assumes all four
    wheels share the load and none has lost contact with the road.

## Values plotted

| n_grid | submerged volume (m3) | over-fill | buoyant force (N) | normal force (N) | traction at mu=0.55 (N) | understatement |
|---|---|---|---|---|---|---|
| 64  | 0.842252 | 1.95x | 8262.5 | 2528.5 | 1390.7 | 60% |
| 96  | 0.644214 | 1.49x | 6319.7 | 4471.3 | 2459.2 | 30% |
| 128 | 0.506268 | 1.17x | 4966.5 | 5824.5 | 3203.5 | 8.3% |
| true geometry | 0.452204 | 1.00x | 4436.1 | 6354.9 | 3495.2 | reference |

Vehicle weight W = 10791.0 N. At the true geometry, buoyancy supports 41.1% of vehicle
weight at 0.30 m depth, so the vehicle does not float at this depth under these assumptions.

Friction sensitivity at the true geometry: mu = 0.30 gives 1906.5 N, mu = 0.40 gives
2542.0 N, mu = 0.55 gives 3495.2 N, a 1.83x spread.
