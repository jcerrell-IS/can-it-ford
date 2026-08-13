# Pending BibTeX entries, 2026-08-13

These two entries could NOT be appended to `paper/can_it_ford_references_IEEE.bib`
by this session. `.claude/hooks/gate_protected_files.sh` denies every `Edit`/`Write`
whose path matches `*/paper/*` or `paper/*`, unconditionally and with no bypass:

```
*/paper/*|paper/*)
  "permissionDecision":"deny",
  "permissionDecisionReason":"paper/ is forbidden to edit per standing rules.
   Get explicit go in chat first, this file mirrors Overleaf."
```

Verified live 2026-08-13 by reading the hook, not assumed. **Josie must apply
these**, or explicitly authorise the write in chat.

They support the limitation paragraph in
`docs/LIMITATION_COUPLING_KINEMATIC_VS_FORCE_2026-08-13.md`.

## Provenance of the two entries

Both were verified 2026-08-13 against the publisher record via the scite MCP
(DOI lookup, not a title search, not memory). Every field below is transcribed
from that record. Neither paper carries a retraction, correction, or expression
of concern in the record returned.

Both are **closed access** (`oaStatus: closed`), so no full text was read here.
The characterisations in the limitation note are **abstract-level**, and the note
says so. Read both in full before the paragraph ships.

Two field corrections were made against the draft note's own reference list,
which is why this file is the authority and not the note's `## Citations` section:

| field | note's draft said | publisher record says |
|---|---|---|
| Akinci month | Aug. 2012 | **2012-07-01, i.e. July 2012** (ACM TOG 31(4) is the SIGGRAPH 2012 issue) |
| DiffFR pages | omitted | **1-17** |
| DiffFR title case | "SPH-based fluid-rigid" | "SPH-Based Fluid-Rigid" |

**KEY DISAMBIGUATED 2026-08-13, do not revert to `akinci2012`.** An adversarial
review caught a live collision: `analysis/render_multigeom_shaded.py:31`, `:270`
and `:562` cite a *different* 2012 paper, "Ihmsen, Akinci, Akinci and Teschner
2012", for the foam/spray diagnostic. A bare `akinci2012` key would collide with
it and invite readers to conflate two different papers that share an author and a
year. The coupling paper is therefore keyed `akinciN2012coupling` (N for Nadir,
the first author). If the foam paper is ever added, key it `ihmsen2012foam`.

## The entries

```bibtex
@article{akinciN2012coupling,
  author  = {Akinci, Nadir and Ihmsen, Markus and Akinci, Gizem and Solenthaler, Barbara and Teschner, Matthias},
  title   = {Versatile Rigid-Fluid Coupling for Incompressible {SPH}},
  journal = {ACM Transactions on Graphics},
  volume  = {31},
  number  = {4},
  pages   = {1--8},
  year    = {2012},
  month   = {jul},
  doi     = {10.1145/2185520.2185558},
  note    = {Cited for: force-based two-way rigid-fluid coupling as the standard SPH alternative to velocity-level coupling. Publisher record verified via scite 2026-08-13; title, authors, journal, vol 31, issue 4, pages 1-8, date 2012-07-01 all confirmed. CLOSED ACCESS, not read in full: the characterisation in the limitations paragraph is abstract-level. Abstract supports "momentum-conserving two-way coupling ... based on hydrodynamic forces" and boundary-particle surface sampling directly.}
}

@article{li2023difffr,
  author  = {Li, Zhehao and Xu, Qingyu and Ye, Xiaohan and Ren, Bo and Liu, Ligang},
  title   = {{DiffFR}: Differentiable {SPH}-Based Fluid-Rigid Coupling for Rigid Body Control},
  journal = {ACM Transactions on Graphics},
  volume  = {42},
  number  = {6},
  pages   = {1--17},
  year    = {2023},
  month   = {dec},
  doi     = {10.1145/3618318},
  note    = {SIGGRAPH Asia 2023. Cited for: gradients of a force-based two-way coupling with respect to rigid-body state are computable stably and cheaply. Publisher record verified via scite 2026-08-13; title, authors, journal, vol 42, issue 6, pages 1-17, date 2023-12-05 all confirmed. CLOSED ACCESS, not read in full: characterisation is abstract-level.}
}
```

## Apply command

Both entries are additive. Nothing existing in the `.bib` is touched. Append to
the end of the file, which currently ends with the `fred2026` entry:

```bash
cat >> /Users/josie/can-it-ford/paper/can_it_ford_references_IEEE.bib < /Users/josie/can-it-ford/docs/pending_bib_2026-08-13.bib
```

To produce that `.bib` fragment from this document without retyping it, run:

```bash
python3 -c "import re,pathlib; s=pathlib.Path('/Users/josie/can-it-ford/docs/PENDING_BIB_ENTRIES_2026-08-13.md').read_text(); b=re.search(r'\`\`\`bibtex\n(.*?)\`\`\`', s, re.S).group(1); pathlib.Path('/Users/josie/can-it-ford/docs/pending_bib_2026-08-13.bib').write_text('\n'+b); print(b)"
```

Verify the append landed, and that no key was duplicated:

```bash
/usr/bin/grep -c "^@" /Users/josie/can-it-ford/paper/can_it_ford_references_IEEE.bib && /usr/bin/grep -n "akinciN2012coupling\|li2023difffr" /Users/josie/can-it-ford/paper/can_it_ford_references_IEEE.bib
```

Success looks like: the `@` count rises by exactly 2, and the second command
prints exactly two lines. The most likely failure mode is a duplicate key if
another session appended these first, which would make BibTeX warn and silently
keep only one, so run the second command even if the first looks right.

## Scope note on "these citations are new"

The draft note claims a live grep for "akinci" across `docs/`, `paper/`,
`citations/` and `CLAUDE.md` returned zero hits. Re-run 2026-08-13 with
`/usr/bin/grep` over the whole repo (excluding `third_party/` and
`.claude/worktrees/`): that claim is **true as scoped**, and both keys are
genuinely absent from the `.bib`. But the scope hides two live mentions:

- `_inbox/Can It Ford? — Comparative Engine, Model, and GH200 Build-Feasibility Sweep for Vehicle-in-Floodwater Simulation.md:56` credits "static and dynamic rigid-fluid coupling (Akinci et al. 2012)" to the PositionBasedDynamics library. This is the same paper, in a directly relevant context.
- `.remember/vista_session_2026-08-12.md:138` cites "Ihmsen, Akinci, Akinci and ..." for a Weber-number criterion, which is a different paper by overlapping authors.

So Akinci 2012 is new to the **bibliography**, not new to the **project's
reading**. State it that way, per CLAUDE.md's standing rule that a count without
its scope is the thing that is wrong.
