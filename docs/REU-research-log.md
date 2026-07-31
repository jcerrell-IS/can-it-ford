# REU Research Log, Josie Cerrell, GeoElements 2026

## STATUS DASHBOARD

- **Project:** Gaussian Splatting + Genesis/MPM physically-viable world models (Can It Ford?), TACC
- **Current phase:** Write-up, submission close
- **This week's goal:** Ship the paper with every citation and figure traceable to a primary source
- **BLOCKED ON:** nothing blocking. One item stays open by choice (Yaris ground clearance, see below)
- **Days to final paper: 1. Due July 31. This is the stipend gate.**
- Poster session was today, July 30, 1-2:30 PM, PCL UFCU Room
- Program ends Aug 1

## DAILY ENTRIES

### 2026-07-30, evening work session, citation and provenance pane

**Did.** Owned citation verification, provenance, and `docs/` while two other panes owned the
Overleaf remote and `origin/main`. Produced three files: a render asset inventory, a rewritten
literature queue, and the submission manifest. Edited no `.tex`, no `.bib`, swapped no figure,
pushed to nothing.

**Learned, the things that actually changed what I believed:**

- **Smith, Modra and Felder 2019 has no Equation 6.** Its equations run to (4), and Equation (4)
  solves for flow velocity V, not displacement. This had been the single load-bearing open
  question since the L2 threshold was first questioned. It is now answered *positively* rather
  than by absence, which is a much stronger position for the paper.
- **That paper was never actually unreachable.** A prior session recorded it
  `UNVERIFIABLE-Wiley-blocked` after a Cloudflare 403. Scite reports it as bronze open access
  with a working URL and served the full text on the first try. A 403 is a property of a
  session, not of a source.
- **The abstract was in the repo the whole time.** `Simulation_Ready_Vehicle_Mesh_Assets.md`
  line 278 *is* Smith 2019, with its correct DOI and title, sitting unread while a later session
  recorded it as unverifiable. Search the repo before searching the web.
- **pyvista was never required for Figure 7.** The finished renders already existed on disk. A
  prior session correctly proved the import fails and then drew the wrong conclusion from it.
- **File size does not prove a render worked.** `hero_probe.png` is a confirmed water-free
  failure at 0.685 bytes/pixel, *higher* than the correct shipped render at 0.568. Only looking
  at the image separates them. Blank renders are detectable by size (all sit at exactly 0.00291),
  water-free ones are not.
- **There is a GL ceiling at 7168x4032.** Every render above it, including the 16384x9216 "max"
  asset, is a uniform blank.

**Decided.**

- Keep the shipped Figure 7. It is the only candidate whose burn-in header and colorbar stay
  legible at IEEE column width, and at 1541 px it sits at 453 dpi, inside the useful band rather
  than three times past it. Swapping is Pane 1's call; I recommended against it and changed
  nothing.
- Do not add Al-Qadami 2023 to the paper tonight. It is a genuine strengthening opportunity, not
  a correction, and adding a citation the night before a deadline is the wrong trade.

**Closed.** Seven of eight literature-queue items. Smith Eq. 6 (positively), the displacement
criterion question (negatively, re-confirmed with my own Consensus query), the NWS
pedestrian-versus-vehicle depth, PhysGaussian's MPM backend (confirmed at the raw GitHub source,
not just DeepWiki), the Genesis paper question (none exists, checked Crossref and OpenAlex), the
FRED entry (confirmed against the PDF's own title page), and SAE 1999-01-1336 (still paywalled,
proven twice, but now moot because the paper's framing no longer depends on it).

Also resolved ledger conflict D5 as a side effect: the NCAC deck reports **1078 kg for the actual
vehicle and 1101 kg for the FE model**. Those two numbers were recorded as a conflict for six
days. They were never in conflict, they are two different quantities in the same table.

**Blocked, one item, by absence not by tooling.** Yaris ground clearance. I fetched the NCAC
deck successfully; `grep -ic clearance` returns 0. It is one of AR&R's three Small Passenger
boundary criteria (< 0.12 m), and secondary sources put a 2007-2011 Yaris near 0.135 m, which
would fail it. Closing it needs the LS-DYNA keyword deck geometry or Toyota's published spec.

**Next.** Nothing from this pane. The paper is shipped at `32b0d12` and verified against the
remote.

---

## Three things I would tell a reviewer are still open

**The force-balance figure cannot be regenerated from what was submitted.** No generator for it
exists on the submitted branch; the script lives only on an unmerged branch that was never
grafted in. Its caption quotes specific quantities, and I was able to confirm tonight with
Wolfram that they are at least mutually consistent: 1100 kg at g = 9.81 gives 10.79 kN, and a
waterplane area of 5.4332 m² makes the 15.99 kN buoyancy figure and the roughly 0.20 m flotation
depth agree to three figures. So the figure is internally sound. What a reviewer cannot do is
reproduce the curve, and that is a real limitation rather than a presentational one. The render
figure has a milder version of the same problem: the simulation and every caption number are
fully traceable, but the cropping step that produced the submitted bytes is unscripted.

**The paper's primary data file is not publicly visible.** `data/all_runs_inventory.csv` backs
the entire coupled sweep and is cited by name twice, but `.gitignore` excludes `data/*`, so
anyone reading the GitHub repository Kumar reads cannot open it. Every number I checked against
it reproduces exactly, so this is a distribution problem and not a correctness one, but for a
group that values reproducibility above almost everything it is the gap I would fix first.

**The L2 threshold still has no empirical footing, and now we know precisely why.** The 0.05 m
drift cutoff is a solver-internal onset-of-motion detector. Tonight's literature work confirmed
from two directions that this is not a gap in our reading: the field uses incipient velocity,
depth-velocity products, or force-balance stability curves, and no source defines instability by
an absolute drift distance. The paper is right not to report an L1-versus-L2 agreement rate for
the coupled sweep. Related and unresolved: `phase_space_results.csv` has never been reconciled
against an explicit L1 calculation, and 7 of 17 runs exceed the 10 percent passthrough gate,
peaking at 15.8807 percent, including the run shown in Figure 7 at 10.67 percent. Those are
flagged rather than excluded, which is the honest choice, but a reviewer will ask about them.

---

## POSTER ASSETS, running list

- `l2_render_g64_m1100_f0045.png`, coupled MPM scene, 1541x664, water speed isosurface. Verified
  this pass against `summary.json` and `metrics.csv`.
- `mass_grid_sweep_v2.pdf`, the 3x3 mass-by-resolution block, true vector.
- `l0l1_two_rules_v2.pdf`, bare versus joint L1 rule across all 70 scenarios, true vector.
- `l2_divergence_real_v2.pdf`, true vector.
- `pipeline_diagram_v2.pdf`, dashed-stage version, true vector.

## OPEN QUESTIONS

- [ ] Q: Yaris ground clearance, to test the AR&R Small Passenger < 0.12 m boundary. Who can
  answer: the LS-DYNA deck itself, or Toyota's published 2010 Yaris spec. Raised: 2026-07-24 as
  ledger flag A5, still open 2026-07-30.
- [ ] Q: Should Al-Qadami 2023 (`10.3390/su151713262`) be cited? It gives an independent 0.38 m
  flotation depth and a 0.36 m²/s D x V threshold from 3D CFD, corroborating Fig. 4 from a
  different method. Who can answer: Kumar. Raised: 2026-07-30.
- [ ] Q: Should `data/*` be un-gitignored, at least for `all_runs_inventory.csv`? Who can answer:
  Kumar. Raised: 2026-07-30.

## DECISIONS LOG

- 2026-07-30 DECIDED: keep the shipped Figure 7, do not swap to a higher-resolution hero. Reason:
  every larger candidate is either illegible at column width or a blank render.
- 2026-07-30 DECIDED: do not add Al-Qadami 2023 to the paper before the deadline. Record it as a
  strengthening opportunity instead.
- 2026-07-30 DECIDED: leave `paper_draft.md` and `PROVISIONAL_STATUS.md` unedited as historical
  records, and flag them from the README rather than rewriting them.
