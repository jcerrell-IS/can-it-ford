# DRIFT_THRESHOLD = 0.05 m Grounding

Question asked: is `DRIFT_THRESHOLD = 0.05` (simulation/can_it_ford_L2_mpm.py:183)
a citable number, a different single number citable, or a per-vehicle-class family
of numbers, when checked against the ARR Project 10 Stage 2 report, the Smith,
Modra and Felder (2019) full-scale tests, and the WRL 2014 combined-hazard tables?

Sources read in full for this note, not secondhand:
- citations/ARR_Project_10_Stage2_Report_Final.pdf (all 29 pages, text extracted)
- citations/smith_modra_felder_2019_velocity_grounding.md
- citations/WRL reports technical and Research/Table 5-1 ... .png
- citations/WRL reports technical and Research/Table 5-2 ... .png
- citations/WRL reports technical and Research/Figure 5-5 Combined flood hazard curves.png

Reviewed July 16, 2026.

---

## What the code actually compares 0.05 to

simulation/can_it_ford_L2_mpm.py:
- line 183: `DRIFT_THRESHOLD = 0.05`
- line 181, 215, 217: `max_x_disp` is the running maximum of `abs(dx)`, where
  `dx = current_pos[0] - initial_pos[0]`, i.e. the vehicle's peak lateral
  displacement along x, in METRES.
- line 252: `verdict = "NO-FORD" if max_x_disp > DRIFT_THRESHOLD else "FORD"`.

So 0.05 is a **lateral displacement distance in metres** (5 cm). If the rigid
vehicle body drifts more than 5 cm sideways at any point in the 500-step run, the
run is called NO-FORD.

This matters because it decides which sources can possibly ground it. A source can
only ground 0.05 m if that source defines a **distance the vehicle is allowed to
move**. Sources that define the flow condition at which motion *begins* are a
different physical quantity and cannot supply this number, no matter how relevant
they are to the project overall.

---

## Honest bottom line, stated first

**0.05 m as written is NOT directly citable to any of these three sources, and no
different single displacement number is citable from them either.** None of the
three defines a permitted lateral-displacement distance for a vehicle. All three
define loss of stability at **incipient motion**, the instant the vehicle starts to
slide or float, not after it has travelled some distance.

What IS citable from these sources is a **per-vehicle-class family of depth-velocity
(D x V) product limits**, in units of m^2/s, not metres of displacement. That family
is a real, sourced, quotable thing. It just answers a different question than the one
the 0.05 m line answers.

So the correct framing for 0.05 m is the one already in CLAUDE.md and the README: it
is a numerical **onset-of-motion detection tolerance** internal to the solver (a small
distance used as a proxy for "did it start to move"), not a physical safety criterion
lifted from a paper. These sources support the *concept* (failure = incipient motion)
but do not hand over the *number*. If a citation is wanted for the concept, cite Xia
et al. 2014 and Shah et al. 2018 (incipient-motion physics), as already recorded in
citations/README.md.

---

## Source 1: ARR Project 10 Stage 2 (Shand, Cox, Blacka, Smith 2011)

Report P10/S2/020, 21 February 2011, Water Research Laboratory, UNSW.

### It defines stability at incipient motion, not by displacement distance

Every criterion in this report is a boundary in the depth-velocity plane. The equation
of stability is force balance at the point of sliding, `mu * F_H / F_V = 1`
(Table 2, printed p.11 / PDF p.21), and floating is `F_V <= 0` (printed p.9 / PDF p.19).
There is no "allowable displacement" quantity anywhere in the report. So it cannot
ground a 0.05 m distance. Searched the full text; the word set is depth, velocity,
D x V, floating depth, limiting velocity, never a permitted travel distance.

### The citable per-class family (this is the real answer)

Table 3, "Proposed DRAFT Stability Criteria for Stationary Vehicles" (printed p.14 /
PDF p.24, repeated in the Executive Summary table printed p.vi / PDF p.9):

| Class | Length | Kerb weight | Ground clearance | Still-water float depth (V=0) | Limiting depth at V=3 m/s | Limiting velocity | D x V limit |
|---|---|---|---|---|---|---|---|
| Small passenger | < 4.3 m | < 1250 kg | < 0.12 m | 0.3 m | 0.1 m | 3.0 m/s | **D x V <= 0.3** |
| Large passenger | > 4.3 m | > 1250 kg | > 0.12 m | 0.4 m | 0.15 m | 3.0 m/s | **D x V <= 0.45** |
| Large 4WD | > 4.5 m | > 2000 kg | > 0.22 m | 0.5 m | 0.2 m | 3.0 m/s | **D x V <= 0.6** |

Footnotes (printed p.14/15): 1 = at velocity 0 m/s; 2 = at velocity 3 m/s; 3 = at low depth.

Units are m^2/s (a depth-velocity product), not metres. This is a family of numbers,
one per vehicle class, exactly as the question anticipated. It grounds an L1-style
hazard verdict, not the L2 displacement detector.

### The 0.60 figure is specifically Large 4WD, and the report brands its own numbers

Confirmed exactly as CLAUDE.md and README already state:

- **0.60 m^2/s is the Large 4WD row of Table 3**, not a generic all-vehicle cutoff.
  Small passenger is 0.3, large passenger is 0.45. Using 0.60 implicitly assumes the
  vehicle is a Large 4WD (>4.5 m, >2000 kg, >0.22 m clearance). If the reconstructed
  vehicle in the project is a sedan, 0.60 is the wrong row; 0.3 or 0.45 would apply.

- **The report explicitly calls these "Draft, interim, informal."** Direct quotes:
  - Executive Summary, printed p.vi (PDF p.8): "Draft, interim criteria for stationary
    vehicle stability are proposed for three vehicle classes."
  - Executive Summary recommendation, printed p.vii (PDF p.9), item 1: "The draft
    stability criteria presented below are adopted as **interim, informal values**."
  - Same recommendation repeated printed p.16 (PDF p.26), item 1.
  - Executive Summary caveat, printed p.vi (PDF p.8): "it is the author's opinion that
    the available experimental data is being applied beyond its limits to provide these
    Draft criteria and that they are **unlikely reliable enough to be adopted permanently
    as safety criteria**."
  - Disclaimer printed under Figure 11, printed p.15 (PDF p.25): "the Water Research
    Laboratory **does not endorse their use** in defining safe depths for vehicle traffic
    and assumes no liability."

### Watch out: a second, different 0.6 lives in the same report

The OLD 1987 AR&R guideline, which this report reviews and criticises, is quoted printed
p.3 (PDF p.13): "Where vehicles alone are affected, a higher depth-velocity product,
**0.6 or 0.7 m^2 s^-1 depending on vehicle size**, is appropriate." This appears again in
Table 1 (historic guidelines, printed p.4 / PDF p.14) as "0.6 to 0.7 depending on vehicle
size."

Do not conflate the two. The report's whole argument is that this ARR87 0.6-0.7 generic
value is **non-conservative** and should be revised (printed p.13, p.16). The project's
0.60 matches the NEW Stage-2 draft **Large 4WD** row (Table 3), which is the defensible
attribution. Cite Table 3, not the ARR87 Table 1 value, when justifying 0.60.

---

## Source 2: Smith, Modra and Felder (2019)

Per citations/smith_modra_felder_2019_velocity_grounding.md, already reviewed page by page:

- Full-scale prototype tests were **stagnant water only**, vehicles towed sideways by
  winch to measure static traction force. No flowing-water displacement was measured.
- The paper's usable output is Equation 6 (p.12), an invertible limiting curve
  `d - d_pan = 0.414 - 0.244 * Fr`, i.e. a depth-Froude stability boundary. That is again
  an **onset-of-instability** boundary, not a permitted displacement distance.
- An earlier attempt to cite this paper's Eq. 6 as the 0.05 m source was already checked
  on July 7 and rejected (README.md): the paper states no finite displacement criterion.

Conclusion: this paper does not ground 0.05 m either. It grounds a depth-velocity (via
Froude) limiting curve, same category as ARR Table 3, different quantity from a distance.

---

## Source 3: WRL Combined Flood Hazard tables (WRL Technical Report 2014/07)

From the page footer visible in the Table 5-1 PNG: "WRL Technical Report 2014/07 FINAL
September 2014," p.38. This is a separate, later WRL document from the 2011 ARR Stage 2
report above. Tables and figure read directly from the PNGs.

### Table 5-1 (p.38): hazard classes, qualitative

| Class | Description |
|---|---|
| H1 | Generally safe for vehicles, people and buildings. |
| H2 | Unsafe for small vehicles. |
| H3 | Unsafe for vehicles, children and the elderly. |
| H4 | Unsafe for vehicles and people. |
| H5 | Unsafe for vehicles and people. All buildings vulnerable to structural damage; some less robust buildings subject to failure. |
| H6 | Unsafe for vehicles and people. All building types vulnerable to failure. |

### Table 5-2: the classification limits

| Class | Limit (D and V in combination) | Limiting still-water depth D | Limiting velocity V |
|---|---|---|---|
| H1 | **D x V <= 0.3** | 0.3 m | 2.0 m/s |
| H2 | **D x V <= 0.6** | 0.5 m | 2.0 m/s |
| H3 | **D x V <= 0.6** | 1.2 m | 2.0 m/s |
| H4 | **D x V <= 1.0** | 2.0 m | 2.0 m/s |
| H5 | **D x V <= 4.0** | 4.0 m | 4.0 m/s |
| H6 | D x V > 4.0 | (none) | (none) |

Figure 5-5 is the same information drawn as depth-versus-velocity hazard curves.

### What this gives, and does not give, for 0.05 m

Same story a third time: every limit is a **D x V product in m^2/s** plus depth and
velocity caps, never a displacement distance. It cannot ground 0.05 m.

What it does give is another per-class family for the ford/no-ford *flow* question:
- Vehicles (all) are safe only in **H1, D x V <= 0.3**.
- **H2, D x V <= 0.6**, is where small vehicles become unsafe (the 0.6 boundary recurs,
  but here it is the small-vehicle limit, not the 4WD limit as in ARR Table 3).
- **H3 and above**, all vehicles unsafe.

Note the two 0.6 values across the two documents describe different vehicle classes
(ARR Table 3: 0.6 = Large 4WD upper limit; WRL Table 5-2: 0.6 = boundary at which SMALL
vehicles become unsafe). They are numerically equal by coincidence of rounding, not the
same criterion. State the source and class whenever 0.6 is used.

---

## Verdict on the three options in the question

1. **Is 0.05 m itself citable?** No. No source defines a permitted lateral-displacement
   distance. 0.05 m is a solver-internal onset-of-motion tolerance, defensible only as
   such, not as a literature threshold.

2. **Is a different single number citable?** No, not for displacement. Every number in
   every source is a D x V product (m^2/s), a floating depth (m), or a limiting velocity
   (m/s). None is a displacement distance, so no single displacement value can be lifted
   from them.

3. **Is a per-vehicle-class family citable?** Yes, but only for the D x V hazard limit,
   which is a different quantity than the code's 0.05 m displacement. The citable family:
   - ARR Stage 2 Table 3 (printed p.14 / PDF p.24): Small 0.3, Large passenger 0.45,
     Large 4WD 0.6 m^2/s, all draft/interim/informal.
   - WRL 2014/07 Table 5-2 (p.38): H1 0.3, H2/H3 0.6, H4 1.0, H5 4.0 m^2/s.

### Practical recommendation

- Keep 0.05 m in the code as what it is, a numerical onset detector, and describe it that
  way in the paper. Do not attach an ARR/WRL/Smith citation to the 0.05 m number itself.
  For the incipient-motion concept it stands in for, cite Xia et al. 2014
  (DOI 10.1007/s11069-013-0889-2) and Shah et al. 2018
  (DOI 10.1051/matecconf/201820307003), per README.md.
- If a D x V hazard threshold is wanted anywhere (e.g. the L1 layer or a cross-check),
  cite the class-specific value and say "draft, interim, informal" out loud. Use 0.60
  only if the vehicle is genuinely a Large 4WD; for a sedan use 0.45 (large passenger)
  or 0.3 (small passenger).
