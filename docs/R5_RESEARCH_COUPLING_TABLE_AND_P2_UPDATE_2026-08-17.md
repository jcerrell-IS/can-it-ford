# R5-D1 unit 25: the coupling catalog's table, and a P-2 number I quoted that has been superseded

Date 2026-08-17. Branch `claude/r5-research`.

Two things. A number I propagated from D4 has been corrected by D4's own
re-derivation, and I have updated both places I used it. And the most on-topic
catalog's **table**, which unit 15 left unmined, turns out to hold the project's
own verification anchors.

**The headline of the second half is a negative: I went looking for a missing
citation and mostly did not find one.**

---

## 1. A number I quoted has been superseded, upward

Unit 24 recorded D4's P-2 reframing and I quoted their transparent-box null
baseline as **10.3 to 11.0%**. D4's `5dbe04d` then re-derived the whole finding
independently, from the rollout artifacts with no shared code path, because as
they put it they had been carrying it "on the reviewer's word, which is one
source cited twice".

The re-derivation **confirms the reframing and sharpens it against the gate**:

| quantity | first figure (reviewer) | re-derived (`5dbe04d`) |
|---|---|---|
| bounding-box void share | 78 to 97% | **77 to 97%** |
| transparent-box null baseline | 10.3 to 11.0% | **11.30 to 14.90%** |
| relation to the 0.10 gate | straddles it | **exceeds it in 17 of 17 runs** |
| share genuinely inside the hull | 0.23 to 3.43 pp | median **6.50%**, range 3.27 to 22.84% |

The tighter baseline uses the water's own footprint extent at the frame rather
than the whole domain area, which is the more defensible null. N = 17, at frame
89 where the vehicle cloud is stored exactly.

**Both of my documents that carried the old figure are updated**, with the
supersession stated rather than the number silently swapped. The direction
matters: the earlier figure made the gate look like it sat *on* its null; the
re-derived one puts the null *above* the gate for every run, which is a stronger
version of the same conclusion.

Worth noting for my own practice: I propagated a figure from a sibling without
re-deriving it, and the sibling then caught that themselves. My unit 24 did
verify the *mechanism* at source (`sim_standing.py:463-465`) but took the
*numbers* on trust. Verifying the mechanism is not verifying the measurement.

## 2. The coupling catalog's table holds the project's verification anchors

`Validated MPM Vehicle Water Coupling`, 60 rows parsed against 60 claimed. Unit
15 read its summary; this is the table. It contains, among others:

| ref | paper | DOI | cited outside `.claude`? |
|---|---|---|---|
| [47] | Celik, Ghia, Roache, Freitas, uncertainty due to discretization | `10.1115/1.2960953` | **yes**, `docs/LITERATURE_CI_GATES_2026-08-08.md` |
| [49] | Roache 1994, uniform reporting of grid refinement studies | `10.1115/1.2910291` | **yes**, same file |
| [36] | Hu et al. 2018, MLS-MPM with displacement discontinuity (CPIC) | `10.1145/3197517.3201293` | **yes**, 6 files |
| [44] | Oberkampf, Trucano, Hirsch 2004 | `10.1115/1.1767847` | no |
| [45] | Roy and Oberkampf 2011, comprehensive VVUQ framework | `10.1016/j.cma.2011.03.016` | **no** |
| [39] | Allen et al. 2003, passenger vehicle inertial properties | `10.4271/2003-01-0966` | catalog only |
| [26] | Canelas et al. 2018, DualSPHysics with a differential variational inequality | `10.1016/j.apor.2018.04.015` | **no** |

**The negative finding, and it is the useful one.** The project runs a
`lit:resolution_convergence_gci` gate (`params_check.py:416`). I expected its GCI
sources to be undocumented, given how many other anchors in this dispatch turned
out to be uncited. **They are not.** Celik and Roache are both in
`docs/LITERATURE_CI_GATES_2026-08-08.md`, which CLAUDE.md already names as that
gate suite's citation bank. **There is no gap here and nobody should go fixing
one.** Recording it so the absence of a finding is on the record too.

Three that are genuinely uncited and plausibly useful:

1. **`10.1016/j.cma.2011.03.016`, Roy and Oberkampf 2011**, a comprehensive VVUQ
   framework. Note this is **not** the same work as register G11's "Oberkampf and
   Roy 2010", which is the book. Same authors, different item, and this is the
   fourth same-author-different-work pair in this dispatch.
2. **`10.4271/2003-01-0966`, Allen et al. 2003.** CLAUDE.md A-3 already names it
   as the citable regression method for provisional CoM and inertia by class, but
   its only appearance in the repo is inside a catalog file that happens to live
   here, not as a citation. A-3 knows it; the bibliography does not.
3. **`10.1016/j.apor.2018.04.015`, Canelas et al. 2018**, DualSPHysics extended
   with a differential variational inequality for rigid-body coupling. Relevant
   to CLAUDE.md L-8, which records the decision not to switch to DualSPHysics on
   aarch64 grounds. It does not reopen that decision, which was about
   portability, but it is the substantive coupling work behind the engine L-8
   declines.

## 3. Status

UNVERIFIED:
1. I have not opened any of the 60 papers. Titles, DOIs and authors are
   transcribed from the catalog table.
2. The "cited outside `.claude`" column is a string search over `.md`, `.bib`,
   `.tex` and `.py`. Per unit 7, string presence is not the same as a `\cite`, and
   I did not repeat the bibliography-structure analysis for these.
3. D4's re-derived P-2 figures are theirs, re-derived by them, not by me. I have
   verified the mechanism at source but not the numbers.
4. Whether Canelas 2018 has any bearing on the engine choice is a physics and
   portability judgement, not mine.
