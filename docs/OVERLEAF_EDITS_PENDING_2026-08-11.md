# Overleaf edit candidates, 2026-08-11

**Status: DRAFT ONLY. Nothing pushed, nothing applied.** Two items. Both were
drafted against live section text pulled this session, not against a
recollection of the paper's structure.

## Before applying, three things to check

1. **Local `.tex` is not authoritative.** The paper builds from
   `conference_101719_1.tex` on `overleaf/main` with flat figure paths. Two local
   copies exist (`paper/conference_101719.tex` and
   `paper/canonical_2026-08-02/conference_101719_1.tex`) and they carry identical
   text for the anchor paragraph below, but the live Overleaf head must be read
   before either edit is applied. Note also that `git push overleaf main`
   overwrites rather than merges, and a fresh Overleaf Git token is needed since
   the old one is off local disk but was never rotated.
2. **`paper/` is write-protected locally.** `gate_protected_files.sh` denies
   writes under `*/paper/*`, so these edits cannot be staged from this repo
   without a deliberate decision about that hook.
3. **The bibliography entry in item (b) does not exist yet** and must be added
   before that sentence will compile.

---

## (a) New paragraph, grid study

**Location, verified live.** `\subsection{Real-Simulation Sweep}`,
`\label{subsec:sweep}`. Insert as a new paragraph immediately **after** the
existing paragraph that ends:

> ...Any mass-sensitivity claim from this work is therefore directional only, and
> treating it as a calibrated effect size would be unsupported.

and immediately **before** the `\begin{figure}` block carrying
`mass_grid_sweep_v2.pdf` / `\label{fig:masssweep}`. In
`paper/canonical_2026-08-02/conference_101719_1.tex` as read on 2026-08-11 that
is between lines 207 and 209.

**Draft text.**

```latex
Two further vehicle classes test whether that non-convergence is a property of
the Yaris hull or of the method. We ran watertight FE hulls for a Nissan Rogue
and a Chevrolet Silverado through the same driver at a common 1100\,kg, once at
fixed \texttt{n\_grid}\,=\,96 and once with \texttt{dx} matched across vehicles
to within 0.4\%. Matching \texttt{dx} rather than \texttt{n\_grid} is necessary
because \texttt{grid\_lim} is derived from the loaded hull's extent, so a fixed
cell count gives each vehicle a different cell size and a different realized
water depth. Refining \texttt{dx} then moves final displacement in opposite
directions for the two hulls: $-26.1$\% for the Rogue across a 9.4\% refinement,
and $+42.7$\% for the Silverado across a 27.8\% refinement, against $-58.9$\%
for the Yaris across the equivalent of its own 64-to-96 step. The displacement
magnitude is therefore not merely unconverged; the \emph{sign} of the resolution
error is vehicle-dependent, so no single grid-correction factor could be applied
across vehicles even in principle. Every one of these runs returns NO-FORD in
both arms and at every resolution tested, so the binary verdict is invariant
across all three geometries while the magnitude is not. These runs are a
companion experiment and are not part of the 17-run gated inventory: three of
the six non-Yaris rows exceed the 10\% passthrough gate and one sank into the
floor plane rather than rising, so they corroborate a known limitation rather
than establishing a converged cross-vehicle comparison.
```

**Every number above traces to `data/class_specific_runs_2026-08-08.csv`**, whose
rows were verified byte-exact against the live Vista `summary.json` this session.
Working is in `docs/MULTIGEOM_VALIDATION_2026-08-11.md` section 5.

**Two judgement calls flagged for review.**

- The paragraph claims "watertight FE hulls" without naming model years. The
  Rogue is sourced in register E6a as a 2020 Nissan Rogue; the Silverado year is
  not established to the standard the rest of the paper uses, so no year is
  asserted.
- Register E8's licence question over CCSA-hosted decks is **unresolved**. This
  paragraph reports numbers derived from those meshes but publishes no geometry.
  Confirm that distinction is acceptable before submission.

---

## (b) Limitations sentence, coupling architecture

**Location problem, reported rather than guessed.** The dispatch asked for a
sentence "for Limitations". **There is no `\section{Limitations}` in the paper.**
Verified live 2026-08-11: the section list is Introduction, Prior Work, Approach,
Results, Conclusions, Future Work, Acknowledgment. A Limitations section was
drafted in an earlier session but the write was blocked and never applied.

Three real homes exist. Pick one deliberately.

1. **Preferred: `\subsection{Vehicle and Scene Representation}`**, which already
   carries the representation limitations and already contains the phrasing
   "This is stated explicitly as a limitation, not glossed over". Append there.
2. `\section{Conclusions}`, in the paragraph beginning "We scope that conclusion
   deliberately", which already enumerates what the result does not establish.
3. Revive the blocked `\section{Limitations}` and place it before
   `\section{Conclusions}`. This is the largest structural change and should not
   be done as a side effect of this edit.

**Draft text, one sentence.**

```latex
The 17 gated runs couple water to the vehicle through a free rigid body that
adopts a mass-weighted average of grid velocity, a path that forms no contact
force and from which any force must therefore be back-computed rather than
measured; a fixed signed-distance-field collider accumulates that force directly
and is the architecture the two-way MPM/rigid-body coupling literature describes
\cite{hu2018mlsmpm}, so the coupling used here is a deliberate architecture
choice whose cross-check against the collider path on these hulls remains
outstanding.
```

**Required bibliography entry** (absent from
`paper/can_it_ford_references_IEEE.bib` and its canonical sibling; author list,
title, venue, volume, pages, year and DOI verified live 2026-08-11 against the
Crossref record for `10.1145/3197517.3201293`):

```bibtex
@article{hu2018mlsmpm,
  author  = {Hu, Yuanming and Fang, Yu and Ge, Ziheng and Qu, Ziyin and Zhu, Yixin and Pradhana, Andre and Jiang, Chenfanfu},
  title   = {A moving least squares material point method with displacement discontinuity and two-way rigid body coupling},
  journal = {ACM Transactions on Graphics},
  volume  = {37},
  number  = {4},
  pages   = {1--14},
  year    = {2018},
  doi     = {10.1145/3197517.3201293}
}
```

**Accuracy note.** The register's shorthand for this paper is "Compatible
Particle-In-Cell". CPIC is the technique introduced in the paper, not its title.
Cite the title above, not the shorthand.

**Scope note.** The sentence says the cross-check "remains outstanding" because
it is. The SDF harness is closed to real hulls: `validate_coupling_force.py`
builds its collider from a hardcoded analytic cube and exposes no mesh argument,
so no such run exists. Do not soften "outstanding" into anything implying the
comparison was attempted on these hulls.
