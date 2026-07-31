# Figure 1: fig1_l1_three_class.pdf

## Caption

**Vehicle class decides the verdict in 12 of 70 flood scenarios.** Each cell is one
(depth, velocity) scenario on a 10 x 7 grid: floodwater depth 0.1 to 1.0 m in 0.1 m steps,
floodwater flow velocity 0.0 to 3.0 m/s in 0.5 m/s steps. Velocity is the speed of the water,
not of the vehicle. Fill darkness gives how many of the three AR&R vehicle classes are cleared
to ford that scenario at L1. The 12 hatched cells are class-sensitive: the verdict flips on
vehicle class alone, with no change whatsoever to the flood. Seven of the twelve are cleared
only for a Large 4WD; the other five are cleared for a Large 4WD and a large passenger
vehicle but not for a small passenger vehicle. In 14 cells all three classes are cleared, and
in 44 no class is. Lines mark each class's two AR&R caps: vertical lines are the maximum depth
(0.30, 0.40, 0.50 m) and curves are the maximum depth-velocity product (0.30, 0.45,
0.60 m2/s), which plot as hyperbolas v = cap / d. A class is cleared only where it satisfies
both its depth cap and its D x V cap, so each class's cleared region is the intersection of
the area left of its vertical line and the area below its curve. The classes nest strictly:
anything a small passenger vehicle can ford, a large passenger vehicle and a Large 4WD can
also ford. The hatched band is the scientific point of the figure. At L1, "can it ford" is not
a property of the flood alone, and a single-threshold answer conceals a verdict that changes
across roughly one scenario in six.

## Citation

Shand, Cox, Blacka and Smith 2011, AR&R Project 10 Stage 2, P10/S2/020, Table 3, page 14.

The report presents these as draft interim stability criteria for **stationary** vehicles. They
are not an endorsed safety standard, and the figure should not be presented as one. The class
names in the figure are the report's own Table 3 names: Small passenger, Large passenger,
Large 4WD.

## Method

Verdicts are read directly from `data/scenario_sweep.csv`, which is produced by
`scripts/gen_scenario_sweep.py` and evaluated by `L1_verdict()` in `vehicle_params.py`. That
function returns NO-FORD if depth exceeds the class depth cap, or velocity exceeds the class
velocity cap (3.0 m/s for all three classes, never binding on this grid), or the
depth-velocity product exceeds the class hazard cap. The figure computes nothing physical of
its own: it reads the three per-class verdict columns and the `L1_class_sensitive` column and
renders them.

`analysis/plot_l1_three_class.py` gates on the source data before it draws anything. It exits
with a STOP message rather than emitting a figure if the row count is not 70, if any per-class
FORD count is not 14 / 19 / 26, if the class-sensitive count is not 12, or if any cell shows a
non-nested combination of class verdicts. The figure in this repository was produced against
`data/scenario_sweep.csv` at md5 `4bf0c759611508190ef71822998391d3`, 4506 bytes, mtime
2026-07-25 17:11:09 CDT. Regenerate with:

```
python analysis/plot_l1_three_class.py
```

The output is a single-page vector PDF, 1344.02 x 979.2 pt (18.667 x 13.6 in), with no raster
content and all three font subsets embedded. It is authored at exactly one third of the 56 in
board width, so it is placed at 1:1 and the specified point sizes are the printed point sizes:
34 pt title, 30 pt axis labels, 26 pt tick labels, 22 pt legend, 16 pt source note. Being
vector, the text carries no resolution ceiling at 300 dpi or any other output resolution.

## Known issue in the source data, RESOLVED 2026-07-25

Four of the 70 cells used to be decided by floating-point representation rather than by the
AR&R criterion. That is fixed and this figure is drawn from the corrected data.

`vehicle_params.py` compared the raw IEEE-754 double `depth_m * velocity_ms` against the class
hazard cap. The bound was written to be inclusive, but four cells whose D x V is mathematically
exactly equal to a cap produced a double one unit in the last place above it, so they returned
NO-FORD:

| depth (m) | velocity (m/s) | class | cap (m2/s) | double product | old verdict | now |
|---|---|---|---|---|---|---|
| 0.1 | 3.0 | small_passenger | 0.30 | 0.30000000000000004 | NO-FORD | FORD |
| 0.2 | 1.5 | small_passenger | 0.30 | 0.30000000000000004 | NO-FORD | FORD |
| 0.2 | 3.0 | large_4wd | 0.60 | 0.6000000000000001 | NO-FORD | FORD |
| 0.4 | 1.5 | large_4wd | 0.60 | 0.6000000000000001 | NO-FORD | FORD |

The fix rounds the product before comparison, which makes the DV bound inclusive as commit
`63e677f` already claimed it was. Exactly four rows changed, all NO-FORD to FORD, none in
reverse. Per-class FORD totals moved from 12 / 19 / 24 to **14 / 19 / 26**. The class-sensitive
total stays **12**, but membership changed exactly as this section previously predicted:
(0.1, 3.0) and (0.2, 1.5) left the set, and (0.2, 3.0) and (0.4, 1.5) entered it. Two of the
twelve hatched cells are therefore different cells than in the figure dated 2026-07-25 06:17.

The superseded figure is the 35,261-byte version with mtime 2026-07-25 06:17, produced against
CSV md5 `40b7c3a8c8976e12878d3fb56db69afb`. Do not reuse it. Any panel still quoting
12 / 19 / 24, or 12 all-three and 46 none, predates this fix.

## Values plotted

| classes cleared | cells | scenarios |
|---|---|---|
| all three | 14 | depth <= 0.3 m with D x V within the 0.30 m2/s cap |
| Large 4WD and large passenger | 5 | class-sensitive, hatched |
| Large 4WD only | 7 | class-sensitive, hatched |
| none | 44 | every scenario at depth >= 0.6 m, and the high-velocity remainder |

Per-class totals over the 70 cells, as shipped:

| class | depth cap (m) | D x V cap (m2/s) | velocity cap (m/s) | FORD cells |
|---|---|---|---|---|
| Small passenger | 0.30 | 0.30 | 3.0 | 14 |
| Large passenger | 0.40 | 0.45 | 3.0 | 19 |
| Large 4WD | 0.50 | 0.60 | 3.0 | 26 |

Class-sensitive cells: 12 of 70, which is 17.1% of the grid. The velocity cap of 3.0 m/s is
never binding, because the grid's maximum velocity is 3.0 m/s and the bound is inclusive.

The 12 class-sensitive cells, as shipped:

(0.2, 2.0), (0.2, 2.5), (0.2, 3.0), (0.3, 1.5), (0.3, 2.0), (0.4, 0.0), (0.4, 0.5),
(0.4, 1.0), (0.4, 1.5), (0.5, 0.0), (0.5, 0.5), (0.5, 1.0), given as (depth m, velocity m/s).

Note that (0.4, 0.0), (0.5, 0.0), (0.4, 0.5), (0.5, 0.5), (0.4, 1.0) and (0.5, 1.0) are
class-sensitive on the depth cap alone, at or near zero velocity, where the hazard product is
small or zero. In still water the depth cap is the only thing separating the classes.

## Design notes

Fills are a single-hue sequential ramp on the count of classes cleared, validated for
colorblind separation and for normal-vision adjacent-pair separation against a white surface.
Class-sensitive cells carry a hatch and a heavy outline in addition to fill, so identity never
rests on color alone and survives grayscale printing. Cap lines carry a white halo so they
stay legible where they cross the darkest fill. No text sits on a dark background anywhere in
the figure.
