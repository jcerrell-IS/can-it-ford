# R5-D1 unit 60: the most rigorous paper version is gitignored, and it sharpens the MPM finding

Date 2026-08-19. Branch `claude/r5-research`.
**Section 1 is for D3 (SAFE-THE-WORK). Section 2 is for the bibliography.**

Unit 58 found I had missed a second paper at `deliverables/paper/overleaf/`. Unit 59
confirmed my other claims survived that miss. This unit finally **reads** it, and
finds two things.

---

## 1. FOR D3: 28 files of authored paper work are invisible to git

```
deliverables/paper/overleaf/   files on disk 28   tracked 0
git check-ignore -v  ->  .gitignore:80: deliverables/
```

**It is not "never added". It is actively ignored by a blanket `deliverables/` rule**,
so `git status` does not list it even as untracked, and no ordinary `git add` will
pick it up. Verified with `git ls-files --error-unmatch` per file, not inferred from
`git log` silence.

What is in there is not generated output. It is **authored source**: `main.tex` plus
eight hand-written sections (`abstract`, `approach`, `conclusions`, `future_work`,
`introduction`, `limitations`, `prior_work`, `results`), **476 lines**, with its own
`refs.bib`.

**And it is the most careful version of the paper that exists.** Measured across its
sections against the other artifacts:

| artifact | `convergence` | `uncertainty` | `GCI` | tracked |
|---|---:|---:|---:|---|
| `deliverables/paper/overleaf/` | **8** | **2** | **1** | **NO, ignored** |
| compiled 7-page PDF | 3 | 0 | 0 | n/a |
| `paper/conference_101719.tex` | - | - | - | yes |

It contains the sentence that corrected my unit 56, at `sections/limitations.tex:13`:
"No Grid Convergence Index is computable ... GCI requires monotone refinement
behavior."

**`paper/canonical_2026-08-02/conference_101719_1.tex` is also untracked**, though I
did not check whether it is ignored or merely unadded.

**I am not recommending a fix.** Whether to un-ignore, relocate, or deliberately keep
it out of a public repo is D3's and Josie's call, and the repo is public. I am
reporting that **a 476-line authored paper with the project's best numerical
self-criticism currently has no version history and would not survive loss of the
working tree.**

## 2. The MPM finding gets stronger, not weaker

This is the paper that takes numerics most seriously, and it is a different paper
from the one I measured before: title **"Can It Ford? Auditing a Standard
Flood-Safety Criterion"**, against the compiled PDF's "Query-Conditioned, Physically
Viable World Models ...".

**Its bibliography is perfectly tight: 11 distinct `\cite` keys, 11 entries in
`refs.bib`, zero unused.** That is better hygiene than
`paper/can_it_ford_references_IEEE.bib`, which carries 21 entries for 11 cited keys.

All eleven:

```
shand2011 (AR&R techreport)   smith2019   xia2010   xia2013   kramer2016
azhar2023   xiong2024
kerbl2023 (3DGS)   xie2023 (PhysGaussian)   thorpe2026   hsiao2025
```

**Nine are flood-vehicle or reconstruction. Not one is MPM method literature.**
Measured in its sections: `material point` 3, `Sulsky` **0**, `Richardson` **0**.

**So the paper that discusses convergence eight times, quotes GCI, and correctly
explains why no convergence index is computable, still cites no paper that
establishes or analyses the method it uses.** That is a sharper statement than unit
49's, and it is measured on the project's most careful artifact rather than its
least.

**It also further narrows what I withdrew in unit 58.** I withdrew "no convergence
reporting" because the PDF says "not grid-converged" three times. This paper does far
more than that, and does it well. The surviving gap is specifically **citation of
method literature**, not treatment of numerics.

## 3. Status

UNVERIFIED:
1. Whether `deliverables/` is ignored deliberately (generated artifacts) or by
   accident is not something I can determine from the rule alone. The tree's
   contents are authored, not generated, which is why I am reporting it.
2. I have read this paper's section headings, bibliography and the numerics-related
   lines, **not all 476 lines**.
3. Which of the three artifacts is canonical is unresolved. Project memory says
   Overleaf is canonical, but the live Overleaf head is unreachable (FLAG-6), and
   this tree is a *local* directory named `overleaf`, which is not the same thing.
4. I did not check whether `paper/canonical_2026-08-02/` is ignored or merely
   unadded.
5. Whether any MPM method paper *should* be cited remains editorial.
