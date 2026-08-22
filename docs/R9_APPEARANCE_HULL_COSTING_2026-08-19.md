# Pricing the split: physics on the CCSA-derived hulls, appearance on a licensed scan

Slot d13-renders, 2026-08-19. This is a COSTING, not an implementation. Nothing was
swapped and no asset was downloaded.

Prompted by the deep search "Simulation Ready Vehicle Mesh Assets" in workspace
`17299f2a-8dc8-438b-8c84-5abf19395e2c`, created 2026-07-21 10:21 and completed 10:38.
It is one of the searches the corpus index cannot reach, so it had not been read.
Every claim attributed to it below was read from the search itself, not relayed.

## 1. What the search actually establishes

Three findings, quoted in substance from its own summary:

- **The documented class set is Yaris, Camry, Silverado.** The CCSA/NCAC
  reverse-engineered LS-DYNA vehicles are the 2010 Toyota Yaris sedan, the 2012 Toyota
  Camry midsize sedan and the 2007 Chevrolet Silverado quad-cab light pickup, each tied
  to teardown or scanning, measured or calibrated mass and inertia and subsystem
  behaviour, and full-scale NHTSA NCAP validation `[Mar13, Mar13b, Mar14b, Moh10]`. The
  Camry was dismantled part by part, parts catalogued, scanned, thickness-measured and
  material-classified, with model mass and inertia checked against the production
  vehicle `[Mar14b]`. **This project's midsize is a Rogue, which is not in that set.**
- **No redistributable conversion is verified.** In its words, no citable, publicly
  redistributable OBJ/PLY/glTF/USD conversion of the specified Yaris, Silverado or
  Rogue models is verified. **Scope matters and must be carried with the claim: the
  search says "in this result set".** That is a bounded negative from a named search,
  which is far stronger than an assumption and still not proof of non-existence.
- **Redistributable alternatives exist and are appearance-grade.** DrivAerML ships
  CC-BY-SA open-format meshes but they are 500 parameter-morphed generic DrivAer
  variants rather than measured production vehicles `[Ash24]`. 3DRealCar supplies
  smartphone scans with real-world dimensions, good exterior geometry, no documented
  mass or structural mechanics `[Du24b]`.

## 2. The part that is already free

The pipeline does not need new code to render a hull the simulation never used.
`prep_cycles_scene.py` already carries `--foreign-hull`, written for exactly this: it
places a hull at native scale resting on the floor, applies NO pose from the run, and
records in `scene.json` that the frame carries no physics claim for that vehicle. The
caption generator already prints the hull filename and vertex count per vehicle.

So the code cost of "draw a different car" is approximately zero. **The cost is
entirely in what the substitution does to the one thing these frames carry.**

## 3. The price, measured

The only physics visible in a still is the WATERLINE: where the free surface meets the
body. Everything else in the frame is either invented optics or arrangement. So the
question is how much a hull substitution moves the waterline.

Measured on the canonical Yaris hull at its own run's free surface:

- The free surface sits **0.2030 m above the floor**, so the waterline crosses the hull
  at 0.203 m: the **rocker and sill**, not a vertical door panel.
- Over the 71,285 faces within 5 cm of that height, the surface angle from horizontal
  is p5 **2.1 deg**, p25 **14.2 deg**, median **34.2 deg**, p75 57.0, p95 80.2.
- A shape difference `d` normal to the surface moves the visible waterline along the
  body by `d / sin(theta)`. That is **1.78x at the median, 4.08x at p25, and 27x at
  p5**.
- **45.2 percent of the waterline contact is shallower than 30 degrees**, where the
  amplification is 2x or worse.

**That is the price and it is unusually bad.** A substitution is most damaging exactly
where this waterline sits, because at 0.203 m the water meets the shallowest part of
the body. On a deeper run, where the water reached the door skin, the same substitution
would cost roughly 1x rather than 1.8x to 27x. So the penalty is depth-dependent and
this depth is close to the worst case.

For scale-matching, the derived hull measures **1.8227 x 4.3028 x 1.5180 m**
(width x length x height), read live from the placed mesh. Any scan would have to be
brought to that box, not to a catalogue figure. NOTE: I have a recollection of the
published 2010 Yaris sedan being about 4.30 x 1.69 x 1.46 m, which would make the
derived hull some 7 percent over in width and 4 percent in height, but **I did not
verify those published figures and they should not be used until someone does.**

## 4. What option 3 would actually take

In dependency order, with the honest blocker named first.

1. **Decide whether a substituted waterline is acceptable at all.** It is not a
   rendering question. Either the caption says the waterline is the simulated one, in
   which case the appearance hull must BE the physics hull, or it says the body is a
   stand-in and the waterline is indicative, in which case the frame stops carrying the
   result it was made to carry. There is no third option, and picking one is Josie's
   call, not mine.
2. **Acquire and licence-check one asset.** 3DRealCar for a production-shaped body,
   DrivAerML if a generic shape is acceptable. Neither is in the repo; both are
   downloads with their own terms, and the round has just spent effort closing exactly
   that kind of question.
3. **Add a fitting mode.** `place_hull` currently chooses rotation by nearest-neighbour
   fit and then HARD-ASSERTS that the placed hull encloses the particle cloud it was
   solidified from. A different vehicle will fail that assert, correctly. A substitution
   needs a separate path that scale-matches to the physics hull's bounding box and
   reports the residual, rather than relaxing the enclosure guard, which exists to catch
   a misplaced hull.
4. **Report the substitution error.** With both meshes present, the surface difference
   at the waterline band can be measured directly and multiplied by the amplification
   above to give a millimetre figure for how far the drawn waterline sits from the
   simulated one. That number belongs in the caption. Until it exists, the honest
   caption cannot say more than "stand-in".

Steps 3 and 4 are perhaps half a day. **Step 1 is the whole decision and step 2 is
outside this slot.**

## 5. The recommendation, and it is not option 3 for the comparison frames

Split the deliverable rather than the hull:

- **The three-class COMPARISON frames keep the CCSA-derived hulls**, lumps and all,
  with the caption stating provenance per class as it now does. They exist to be
  measured against, and a substituted body destroys the only measurable thing in them
  to fix a cosmetic one.
- **A separate scene-setting image may use a licensed scan**, clearly captioned as
  carrying no waterline claim. That is where a smooth body buys something real: it is
  the picture people look at, and it is not the picture anyone measures.

That keeps the honest artifact honest and gives the pretty artifact a licence it can be
published under, which is what the search actually unlocks. It also matches the pattern
the rest of this pipeline already follows: the matplotlib renderer stayed as the
instrument when Cycles became the picture.

## 6. Unreviewed

The physics-skeptic subagent is dead fleet-wide this round, so every number here is
UNREVIEWED. The waterline geometry is reproducible from `scene_yaris/hull.ply` and
`scene.json` with the script recorded in the session; the search claims are reproducible
by reading the search itself.

## 7. Which view I searched, stated correctly

A dispatch reached this slot asserting that none of the six closest prior-art DOIs is in
the 332-record corpus and that a query for Al-Qadami returns zero. **That was withdrawn
by its author, and it is false: d14-corpusbib measured all six present, 6 of 6, with
five records carrying Al-Qadami in the authors field.** No caption or document in this
slot ever repeated it; checked by search across every file authored here, zero hits.

What survives is a different and narrower statement, and it is the one to carry:

- `analysis/research_index.py --query` matches **title and abstract only, never
  authors**, so an author query returns zero regardless of what the index holds.
- On `origin/main` **the tool does not exist at all**; the author-search fix is on an
  unmerged branch.

So the correct sentence is not "the corpus lacks this project's prior art", which is
untrue, but "the query predicate does not match authors, and on origin/main the tool is
absent entirely". Only the second is a statement about the instrument rather than about
the literature, and only the second is true.

The same discipline applies to the mesh search this document rests on. Its negative
result is bounded to its own result set, which is why every mention of it here carries
that scope, and it is a statement about what one named search retrieved, not about what
exists.
