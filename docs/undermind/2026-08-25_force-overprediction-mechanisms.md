# Undermind query: mechanisms other than volumetric locking for force over-prediction

**Run 2026-08-25 via the Undermind connector, workspace "Can it ford"
(`17299f2a-8dc8-438b-8c84-5abf19395e2c`), account jcerrell29@students.claremontmckenna.edu.**

**A NOTE ON THE WIRING TEST, because it gives the wrong answer.** `grep -i undermind .mcp.json`
returns **nothing**: `.mcp.json` declares only deepwiki, scite, wolfram, canford-corpus,
canford-tacc and wandb `[READ]`. Undermind is nonetheless **live in this session as a claude.ai
connector**, so the `.mcp.json` test understates availability. Do not conclude from that grep
that Undermind is unavailable.

**Method: `search_papers`, not `launch_deep_search`.** Semantic search over the global corpus
returns in seconds; a deep search takes 2 to 5 minutes and the workspace already holds 27.
`[INFERRED, per the connector's own orientation guidance]`

## The query as issued

> Velocity-averaging coupling between a material point method fluid and a rigid body
> systematically over-predicts the transmitted force by tens of percent. Because the rigid body
> velocity is obtained by a mass-weighted average of grid momentum rather than by integrating a
> pressure field over the wetted surface, the error does not decrease with particle refinement.
> We discriminate this projection bias from volumetric locking and from quadrature error by
> sweeping particles per cell at fixed grid spacing.

The prompt's literal wording was "mechanisms other than volumetric locking that cause systematic
30 to 60 percent force over-prediction in velocity-averaging MPM rigid-body coupling with no
pressure field, and how they are experimentally discriminated." `search_papers` wants a
sample-abstract, not a question, so the above is that question written as target-paper prose.

## Results, ranked by relevance to the mechanism question

**The four strongest NEW candidates. None of these is in this project's corpus index**
`[READ, checked against `data/research_corpus_index.json`]`.

| cite key | DOI | why it bears on Job B | PDF |
|---|---|---|---|
| `Gis19b` | `10.1145/3284980` | **Interlinked SPH Pressure Solvers for Strong Fluid-Rigid Coupling.** Directly addresses the "no pressure field" half of the defect: it builds the pressure coupling this project's velocity-averaging path lacks. 85 citations. | no |
| `Ben23` | `10.2312/vmv.20231244` | **Consistent SPH Rigid-Fluid Coupling.** The word "consistent" is the claim: it argues prior rigid-fluid coupling is inconsistent and quantifies the error. | **yes** |
| `Raz23` | `10.1145/3606924` | **A Linear and Angular Momentum Conserving Hybrid Particle/Grid Iteration for Volumetric Elastic Contact.** Momentum conservation across a particle/grid contact is exactly the transfer Job B measures. | no |
| `Jia16` | `10.1016/j.jcp.2017.02.050` | **An angular momentum conserving affine-particle-in-cell method (APIC).** The canonical treatment of information lost in the PIC velocity projection, which is the surviving hypothesis after the PPC sweep. 112 citations. | **yes** |

**Three that confirm the search hit the right literature rather than adding new candidates.**

- `Wal07`, `10.3970/CMES.2007.019.223`, **Improved Velocity Projection for the Material Point
  Method**. This is the same Wallstedt and Guilkey paper whose claims `ac0f0d8` withdrew as
  misattributed. **A PDF is available in the workspace**, so the two withdrawn claims could now
  be checked against the source rather than relayed. See FINAL.md section 5.4.
- `Zha22d`, `10.1002/nme.7347`, **Circumventing volumetric locking in explicit MPM**, Zhao,
  Jiang and Choo. PDF available. This is the locking-remedy line the F-bar finding rests on.
- `Bau23`, `10.1002/nme.7217`, already in the corpus at 5 reports and already extracted to full
  text locally. Its appearance here is a consistency check, not a new find.

## What this does and does not establish

**It does not answer the mechanism question.** These are candidate literatures returned by one
semantic search, none has been read, and no claim here is verified against a primary source
`[READ, as metadata only]`.

**What it does establish is that the surviving hypothesis has a literature.** After job 923239's
flat PPC slope refuted locking, the remaining candidate is velocity-projection bias, and
`Jia16` plus `Gis19b` are the two standard treatments of exactly that failure mode. **Both have
been sitting outside this project's corpus the whole time.**

**Cheapest next step, and it costs nothing:** `Ben23` and `Jia16` both have PDFs in the
workspace and can be read with `read_pdfs` now.

## Standing caveat

Metadata only. Nothing here was checked by the physics-skeptic path. Re-run rather than cite.
