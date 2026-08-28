# ROUND 3, D2 VISTA-REALISM-TRIAGE

Read `ROUND3_SHARED.md` first.

## Your friction table survived the relay chain. It was the only thing that did.

D4 picked up your regime table from the AR&R primary PDF and carried your caveat
**verbatim**: ARR's coefficient is tyre-on-road across four contact patches in
an analytical force balance, ours is a Coulomb coefficient across the hull's
whole lower particle surface, analogous but not the same quantity. D4 also
flagged that my own relay of it dropped a containment qualifier, and that both
losses were recoverable only by reading the source commit bodies. Keep writing
the caveat into the commit body, not just the document.

Two things sharpen your 0.55 row, both from other sessions:

- D4, from the AR&R PDF itself: the 0.3 is **Bonham & Hattersley's 1967
  assumption carried forward**, not an ARR measurement. Your row label "ARR
  assumed" is right and now has a primary source.
- D11 plus artifact 65474f37: 0.55 is Azhar, Pauwels & Bui (2023)'s own
  spring-balance measurement of their experimental rubber mat, citing Wong,
  *Theory of Ground Vehicles*, chaining out to a 1969 GM tyre brake-force study.
  General automotive, not submerged. Against the 0.3 convention it raises
  T_avail by 83 percent.

## The artifacts you could not read are readable

You reported the compass artifacts and the perplexity directory as `Operation
not permitted`. That is true of `~/Downloads` only. Both exist elsewhere and are
readable right now, verified at 22:38: see shared section 1. 65474f37 is the
one that matters to you.

You said verifying the artifact's figures against the PDF is the stronger
direction because the artifact is secondary. Agreed, and now you can do both:
read the artifact, then check its figures against the primary PDF, and report
where they disagree. A secondary source that reproduces the primary exactly is
worth recording as such.

## Your next scope, and it is a data-loss risk

Vista's checkout at `/work/11603/jcerrell0629/vista/can-it-ford` is **2 commits
ahead of every remote** and carries **4 modified tracked files**, measured live
at 22:41:

    15275f2  settings.json: adopt origin/main's full config as the base, add git-push ask
    e9f3b60  add TACC global-rules import target, citation-verifier subagent, git-push ask rule
    (ahead-of-all-remotes count: 2)

    modified:  CLAUDE.md
    modified:  simulation/can_it_ford_L2_mpm.py
    modified:  simulation/failure_modes.py
    modified:  simulation/validate_coupling_force.py
    untracked: .claude/handoffs/

This is your dispatch's core risk and it is unattended. Three specifics:

1. **CLAUDE.md is modified on Vista and uncommitted.** CLAUDE.md is known not to
   be synced across machines. A Vista-only edit to the standing rules is exactly
   the divergence that produces two sessions obeying different rules. Diff it
   against the Mac's copy and report what differs, line by line. Do not
   reconcile it yourself, and do not copy either direction: report it.
2. **failure_modes.py is modified on Vista.** That file carries the 9.80665
   gravity fork that fed the published 16 SLIDE / 1 STUCK verdicts (CLAUDE.md
   item 15). If Vista's copy differs from the Mac's, the verdicts may not be
   reproducible from either tree. Diff it and say which line moved.
3. **validate_coupling_force.py is modified on Vista.** Committed on the Mac as
   541d832 plus 057b3e9. Same treatment.

Do not push, pull, or overwrite anything on Vista. Diff and report. The 2026-08-13
near-miss on Vista is why: a routine config sync would have destroyed 12 unpushed
commits.

## Skills and machine state

Call `tacc-terminal-and-file-transfer` for the Vista reads. Use
`/Users/josie/can-it-ford/scripts/tacc.sh vista '<cmd>'`; it works
non-interactively right now.

Vista: queue empty, 641 SU, /home1 89.15 percent full so do not install into it.
LS6: unreachable non-interactively, treat as offline.

Four commits unpushed on your branch, docs-only, held pending Josie's per-branch
check. Do not re-ask each turn.
