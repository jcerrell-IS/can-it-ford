# Centre panel / abstract paragraph

Written 2026-07-25 for the poster centre panel and the paper abstract. Plain English, no
prior knowledge of the project assumed. Every quantitative claim traces to
`renders/yaris_render_s1/gates_results_both_scenarios.json`.

---

A driver stopped at a flooded road wants one answer: can I cross? The cheapest ways to
answer are rules of thumb. Turn around if the water is deeper than fifteen centimetres.
Multiply the depth by the flow speed and check the product against a published table. These
rules cost nothing, they fit on a road sign, and at the conditions we tested they are
largely right: three of the four methods we compared agree that a thirty centimetre
crossing at 1.5 metres per second should not be attempted, and they agree for every vehicle
we tested. What that agreement conceals is the thing the cheap rules cannot do. Each of them
is a function of the water and nothing else. Change the vehicle from an 1100 kilogram
compact to a 2337 kilogram truck and the depth-times-speed number does not move at all. It
is identical to the last decimal place, because the vehicle enters that rule only as a row
in a lookup table, never as a mass in an equation. Run those same three vehicles through a
full coupled simulation, in which the floodwater actually pushes on the body and the body
pushes back, and how far they are carried downstream spreads out by a factor of nearly five.
That is the boundary we are trying to draw. A cheap abstraction is sufficient when the
question is whether a crossing is dangerous, because danger is set mostly by the water. It
stops being sufficient the moment the question becomes whether the crossing is dangerous
for *this* vehicle, because the cheap rules have no mechanism for answering that. They are
not approximating the vehicle poorly; they are not representing it at all. The expensive
simulation earns its cost in exactly one place, and it is worth being precise about where:
not in deciding whether the water is hazardous, which the fifteen centimetre rule already
does adequately, but in resolving how much that hazard depends on what is doing the
crossing.

---

## Caveats that must not be dropped when this is shortened

- "Three of four agree" is weaker corroboration than it sounds. Three of the four rungs
  (the depth threshold, the depth-velocity product, and the total-head criterion) all take
  the same two inputs, depth and velocity. They are not independent tests. The honest
  reading is that three published criteria built on the same two variables agree with each
  other, and the simulation agrees with them on the verdict while disagreeing on the
  sensitivity.
- The factor of nearly five is 4.86x, and it is a spread in *final downstream
  displacement*, not in a ford verdict. Two of the three masses share the same L2 verdict.
- One geometry, three masses. This is a mass sensitivity study. It is not a comparison of
  three real vehicle classes, and it must never be described as one. See
  `docs/limitations.md` L-3.
