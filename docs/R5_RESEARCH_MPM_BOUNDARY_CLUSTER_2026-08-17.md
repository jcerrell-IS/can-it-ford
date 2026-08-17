# R5-D1 unit 21: the unread catalog contains the project's own BC anchor, and a 2024 paper that answers its open question

Date 2026-08-17. Branch `claude/r5-research`. **For D4.** Data:
`data/r5_citation_mpm_boundary.tsv`, 17 rows.

Unit 15 read the `Quantitative MPM Wall Penetration` catalog's summary for the
P-2 threshold question. This unit mines its **paper table**, and the table turns
out to be about something else entirely: it is an MPM boundary-condition and
free-surface cluster, which is the project's live physics blocker.

---

## 1. The catalog contains the paper the project is trying to implement

Reference [6] of that 16-paper table is:

> Zhao, Bolognin, Liang, Rohe and Vardon 2019, "Development of in/outflow
> boundary conditions for MPM simulation of uniform and ...",
> `10.1016/j.compfluid.2018.10.007`

That is exactly the citation CLAUDE.md names: "The MPM in/outflow boundary
conditions this project needs are Zhao, Bolognin, Liang, Rohe and Vardon 2019 ...
DOI 10.1016/j.compfluid.2018.10.007, implemented in Anura3D. NOT Kumar."

**The catalog nobody opened contains the project's own BC anchor**, sitting in a
cluster of 15 related MPM boundary and free-surface papers. Checked against the
repo: **only that one of the 16 is cited anywhere (10 files). The other 15 are
uncited.**

## 2. A 2024 paper, same group, uncited, that addresses the open question directly

Chasing catalog entry [15] (Remmerswaal, Bolognin, Vardon, Hicks 2019, listed
with no DOI) surfaced a later and more relevant paper by the same TU Delft group:

> **Remmerswaal, Vardon and Hicks 2024, "Inhomogeneous Neumann boundary
> conditions for MPM and GIMP", *Computers and Geotechnics*,
> `10.1016/j.compgeo.2024.106494`.** Uncited in this repo. `oa_status: hybrid`,
> no free PDF located.

Abstract, READ DIRECTLY:

> As the Material Point Method (MPM) uses both a mesh and a point discretisation
> scheme, **the application of boundary conditions is difficult, currently
> limiting the flexibility of the method.** While many boundary condition options
> have been used in the literature, the accuracy of Neumann boundary condition
> options has not yet been studied. **Four options have here been evaluated for 1D
> and 2D benchmarks, although none of the options were found to be both accurate
> and generally applicable in MPM.** However, **for the generalised interpolation
> material point method (GIMP)**, the application of surface tractions on support
> domain boundaries or on a detected surface are valid options. **Large
> differences between these two accurate options and the application of tractions
> at surface material points, a method regularly used in the literature, have
> been observed.**

## 3. It maps onto the project's own open question, item for item

`docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md` step 3, verbatim:

> Confirm whether the grid in `mpm_solver_warp.py` exposes any node-level hook
> where a velocity or pressure Dirichlet condition could be applied at a domain
> face, versus whether it only supports whole-particle operations. **This
> determines whether the BC has to be a particle-level trick**, matching
> `sim_standing.py`'s existing `_sustain_inflow` pattern but made bidirectional,
> **or whether a real grid-face BC is reachable.**

Against Remmerswaal 2024:

| the project's question | what the paper reports |
|---|---|
| is a particle-level BC trick acceptable? | applying tractions **at surface material points** is measured as **largely different** from the accurate options |
| is a real grid-face BC reachable? | the two accurate options require **GIMP**, not standard MPM |
| how hard is this in general? | "none of the options were found to be **both accurate and generally applicable** in MPM" |

And the project has **no GIMP**: a repo-wide search for `GIMP` outside `.claude/`
returns zero hits. The solver is standard MPM.

So the literature has already studied the exact question the plan proposes to
answer empirically, published it in 2024, from the same group as the project's
anchor citation, and reached a discouraging general conclusion. **That does not
solve the blocker. It means the project should not spend GPU time rediscovering
it.**

## 4. The caveat, and it is a real one

**Remmerswaal 2024 is about Neumann boundary conditions**, that is prescribed
tractions or fluxes. The project's plan step 3 names a "velocity or pressure
**Dirichlet** condition". Those are different boundary-condition types.

A pressure-controlled outflow of the kind Zhao 2019 describes is arguably a
traction condition in this framing, which is why I think the paper transfers, but
**whether the project's inflow and outflow conditions are Neumann or Dirichlet in
Remmerswaal's sense is a physics judgement and it is D4's, not mine.** If they are
strictly Dirichlet, this paper constrains less than section 3 suggests. I am
handing over the source and the mapping, not a conclusion.

## 5. The full cluster, for D4

All 16 catalog entries plus the 2024 find are in
`data/r5_citation_mpm_boundary.tsv`. The ones that look most relevant to the BC
work, by title:

| ref | year | DOI | why |
|---|---|---|---|
| [6] | 2019 | `10.1016/j.compfluid.2018.10.007` | the project's anchor, in/outflow BCs, **the only cited one** |
| 17 | 2024 | `10.1016/j.compgeo.2024.106494` | Neumann BCs for MPM and GIMP, same group, section 2 |
| [15] | 2019 | (none in catalog) | non-trivial BCs in MPM, geotechnical, same group |
| [3] | 2019 | (none in catalog) | a consistent boundary method for MPM using image particles |
| [8] | 2017 | `10.1016/j.jcp.2016.10.064` | incompressible MPM for free surface flow |
| [16] | 2017 | `10.1016/j.proeng.2017.01.041` | dam-break floods with MPM, Zhao and Liang again |
| [7] | 2022 | `10.1016/j.cma.2022.114809` | immersed FE material point for free-surface fluid |
| [13] | 2025 | `10.1016/j.cma.2025.118264` | improved MPM for free-surface based on finite volume |

Two of these have no DOI in the catalog, which is a known gap in that catalog's
records (its summary says so).

## 6. Status

UNVERIFIED:
1. **Abstract only for Remmerswaal 2024.** Hybrid OA with no free PDF found, so
   the four options and the size of the "large differences" are unread.
2. Catalog entry [15]'s DOI is unresolved; my Crossref search returned the 2024
   paper rather than the 2019 one, so [15] may be a conference item outside
   Crossref.
3. Whether the project's BCs are Neumann or Dirichlet in Remmerswaal's sense,
   per section 4.
4. I did not verify the 15 uncited DOIs individually against their registering
   agencies; they are transcribed from the catalog table.
5. Unit 20's open item is unchanged: Kramer 2016's model scale ratios. The
   UNSWorks repository copy is a DSpace 7 app whose REST API returned empty on
   three endpoint forms, and CORE needs a key. Not chased further.
