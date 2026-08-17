# R5-D1 unit 47: a corpus file built my deliverable before me, and it names an MPM gap

Date 2026-08-18. Branch `claude/r5-research`.
**For whoever owns the bibliography and the related-work section.**

Unit 45 surfaced a corpus file I had never opened:
`00_CATALOGUED_BUT_NEVER_CITED_2026-08-14.tsv`, with an 85-line README. It is a
**pre-existing, independent build of my own unit-3 deliverable**, made four days
before mine. I read it in full, compared it to my work, and re-tested its findings
against today's repo.

---

## 1. Somebody already did this, on a narrower base, and got a compatible answer

Their build, from the README:

```
catalog rows parsed                     279  (six Undermind reports)
distinct papers carrying a DOI          205
UNCITED anywhere in the repo            138
cited somewhere in the repo              67
cited in docs/, paper/, deliverables/    38
appearing in more than one report        30
rows with NO DOI, not diffable           37
```

**Mine is broader:** 14 catalogs and 489 DOIs against their 6 reports and 205 DOIs.
**Neither supersedes the other**, and the denominators differ, so the two counts are
not directly comparable. What matters is that two independently constructed diffs
agree on the shape: most catalogued papers are uncited.

**They hit the same trap I did, and recorded it.** Their first pass scanned only
`docs/`, `paper/`, `deliverables/`, `overleaf_sync/`, `citations/` and reported 167
uncited, which was "too harsh": Steffen 2008 came back uncited while its DOI is in
**13 repo files**. They kept **two** citation columns for that reason. That is the
same narrow-versus-repo-wide distinction that produced my erratum 4, arrived at
independently.

**Their stated blind spot, which I inherit:** 37 catalog rows carry no DOI and are
**not diffable**. Their README says so plainly: "Absence from this table is not
proof of absence from the catalogs."

## 2. The finding: an MPM method-citation gap, still open today

Their nine highest-signal gaps are papers uncited in the repo **and** surfaced by
more than one report. I re-tested every one against the repo today, four days later,
adding the distinction unit 45 established: **repo presence is not paper citation.**

| DOI | paper | repo | `.tex` | paper `.bib` |
|---|---|---:|---:|---:|
| `10.1016/j.cma.2022.114809` | Immersed FEM material point (IFEMP) for free-surface FSI | 2 | **0** | **0** |
| `10.1016/j.jcp.2016.10.064` | Incompressible material point method for free surface flow | 2 | **0** | **0** |
| `10.1016/bs.aams.2019.11.001` | **Material point method after 25 years** (the standard review) | 1 | **0** | **0** |
| `10.1504/pcfd.2019.10018820` | **Benchmarking MPM for free-surface/body interaction** | 2 | **0** | **0** |
| `10.1007/s00466-019-01783-3` | Stress inaccuracies in MPM, and a proposed solution | **0** | **0** | **0** |
| `10.1016/j.proeng.2017.01.041` | Dam-break flood simulation with MPM | **0** | **0** | **0** |
| `10.1061/(asce)em.1943-7889.0000981` | Improved MPM free-surface flows with adaptive mesh refinement | **0** | **0** | **0** |
| `10.1115/1.4044632` | Hydroelastic effects on impact loads during flat water entry | **0** | **0** | **0** |
| `10.4271/2014-01-0936` | Khapane, **Wading simulation, challenges and solutions** | 3 | **0** | **0** |
| `10.1177/0954407020942005` | Analysis and research on **vehicle wading performance** | 1 | **0** | **0** |

**All ten reach zero `.tex` files and zero entries in the paper's bibliography.
Four have no presence in the repo at all.** So none of the 2026-08-14 gaps has
closed, and the ones that "exist in the repo" exist only in research notes, exactly
the pattern unit 45 documented.

**The substantive point is the top four rows.** This project's central method is
MPM. It does not cite the MPM-after-25-years review, an incompressible-MPM
free-surface method, an immersed-FEM-MPM FSI method, or a **benchmark for
free-surface-plus-body interaction**, which is precisely the problem the 17 runs
solve. That last one is the sharpest: a benchmarking paper for our exact problem
class, sitting in our own catalogs, uncited.

**This is a method-literature gap, not an application-literature gap**, and it is
therefore different from every novelty finding in this dispatch so far, which all
concerned flood-vehicle papers.

## 3. A fifth wading paper, which their README names and the novelty guard does not

`10.1177/0954407020942005`, "Analysis and research on vehicle wading performance",
appears in **two** reports. Their README says it "belongs with Wasfy 2015, Pazouki
2016, Khapane 2014 and He 2026 in related work".

**The novelty guard's origin note names four papers. This is a fifth**, and I would
not have found it from the guard's description alone. It reaches **zero `.tex`**.

## 4. On whether this corroborates unit 45, stated carefully

It partly does, and I want to be precise because this project's claim-discipline
rule says one source cited twice is not two sources.

**Genuinely independent:** the *list* of papers. Theirs comes from diffing six
Undermind catalogs on 2026-08-14; unit 45's came from the guard tool's own
description. Different origins, and Khapane 2014 appears in both.

**NOT independent:** the *check*. Both their diff and my re-test read the same
repository. If the repo were mis-scanned in the same way, both would be wrong
together.

So: independent corroboration that these papers are catalogued-and-uncited,
**not** independent confirmation of the repo-scanning method.

## 5. Status

UNVERIFIED, and the first item is load-bearing:

1. **The `.tex` columns inherit FLAG-6.** The live Overleaf head is unreachable
   (connector authentication fails; the fetched `overleaf/main` ref is 2026-07-31
   and a positive control shows it predates known changes). **So "zero `.tex`" is
   proven for local copies dated 2026-07-30 to 2026-08-02 only**, not for the
   current paper. Unit 46 has the full working.
2. I read the **README**, 85 lines, in full. I have **not** read the TSV's 205 data
   rows, so I have verified their nine highlighted gaps and not their other 129
   uncited entries.
3. Their 37 non-diffable no-DOI rows are a blind spot in their build and therefore
   in my re-test of it.
4. Whether any of these ten *should* be cited is an editorial judgement for the
   paper's owner. I establish only that they are catalogued, that they reach no
   `.tex` in any reachable copy, and that four are absent from the repo entirely.
5. Counts are from `/usr/bin/grep -rlF` over `.md .tex .bib .tsv .csv .py`,
   excluding `.claude/worktrees`. A DOI string present in a file does not prove the
   paper is discussed there, which is their README's own caveat and mine.
