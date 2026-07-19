# Full Equip Pass — July 13, later morning

Covers: status updates to both prior planning documents, the known-mistakes list Claude
Code needs so it stops re-testing dead ends, the variable-relationship rule addressing
"not just moving variables," a reusable kickoff prompt, and a final deployed-everywhere
checklist.

---

## 1. Status update — apply to `2026-07-12_session_audit_and_panel_tasks.md`

Append this as a dated addendum, don't rewrite the original — it's still a valid record
of what was true that night.

```
## STATUS UPDATE — July 13, later pass

Section 1c's overlap hypothesis: TESTED (box reverted to old size, domain kept
widened) and RULED OUT as the sole cause, along with box size independently.
Live suspect is now the domain-widening commit's bounds themselves, not overlap
or geometry. Don't re-run the Pane 0.0 overlap isolation test as originally
specified — it's already answered.

Section 1b's mass fix: target confirmed as 1390kg (not the 1450kg alternative
mentioned). Correct rho = 115.7. Applied-to-live-file status still unconfirmed
as of this update — check before assuming done.

Pane assignments in Section 5: Panes 0.2, 0.5, and 0.6's task lists were never
confirmed as executed. Panes 0.0/0.1/0.3 show partial completion. See
master_outstanding_tasks_audit_july13.md for the full per-pane breakdown.

New finding not in the original document: viability_audit.py globs
particles_d*.npz, which does not match particles_mpm_*.npz output files —
every MPM-track run has been invisible to this audit script.
```

---

## 2. Status update — apply to `2026-07-13_bug_triage_and_panel_execution_plan.md`

Append similarly:

```
## STATUS UPDATE — July 13, later pass

Bug B03 (water/vehicle overlap): RESOLVED AS A HYPOTHESIS, not as a fix — tested
directly and ruled out as the crash cause. Do not run Pane 0.7's overlap
isolation test as originally written; it's already been answered by a
different, equivalent test.

Bug B02 (mass): target resolved to 1390kg, rho=115.7. Fix-applied status to the
live file still unconfirmed.

New live suspect for the crash, not present anywhere in the original triage:
the domain-widening commit itself (lower_bound=(-2.5,-1.0,-0.1),
upper_bound=(4.5,1.0,2.5)). This should become the new B01 test target,
replacing the overlap/mass isolation matrix originally specified for Pane 0.7.

Two new bugs found since this document was written: viability_audit.py's glob
mismatch (see above), and the confirmed root cause of Bug B08 (conda/trimesh
on Mac — `conda run` resolves to system Python, not the environment's
interpreter; the actual fix of getting `conda run` to activate correctly has
not been confirmed applied).
```

---

## 3. Known Dead Ends — add this to CLAUDE.md, Claude Code must check before re-testing anything

```
## KNOWN DEAD ENDS — do not re-attempt these, they are already answered

- Water/vehicle overlap as the sole CUDA crash cause: TESTED, RULED OUT.
- Box size (1.0x1.6x1.5m vs sedan-scale) as the sole crash cause: TESTED, RULED OUT.
- grid_density (64 vs 128) as the sole crash cause: TESTED, RULED OUT.
- Domain padding alone as the crash cause: TESTED, RULED OUT.
- The original hand-rolled sys.argv positional parsing bug: FIXED in 69d27af, do
  not re-diagnose this in can_it_ford_L2.py, can_it_ford_L2_mpm.py, or
  can_it_ford_L2_mpm_ytest.py.
- Assuming `~/can-it-ford` exists on Vista: it does not. Canonical path is
  `/work/11603/jcerrell0629/vista/can-it-ford`.
- Assuming `conda run -n can-it-ford <cmd>` on the Mac actually activates the
  environment: confirmed it does not — resolves to system Python
  (/opt/homebrew/bin/python3) instead. Don't trust its output without checking
  `which python3` first.
- Running `idev` or `ssh` again when already inside an active session of that
  type: check `hostname; pwd` first, always, before either command.
- Trusting a script's printed/echoed parameter values as proof the parsing
  logic is correct: confirmed false once already (the argparse bug). Cross-
  check against what was actually typed, every time.
```

---

## 4. Variable relationships — the "not just moving variables" rule

This directly addresses writing scripts that edit one number without accounting for
what it's coupled to. Add to CLAUDE.md's house rules:

```
## COUPLED VARIABLES — never edit one without checking its dependents

- Box dimensions <-> density (rho) <-> mass: mass = density x volume, always.
  Resizing a collision box without recalculating rho is exactly the bug that
  made the vehicle 5x too heavy. Any time box dimensions change, recompute
  rho for the target mass in the same edit, not as a follow-up task.
- grid_density <-> domain bounds <-> dx (cell size) <-> CFL/substep stability:
  changing any one of these can silently violate the others' assumptions.
  When touching one, state what the other three currently are before
  concluding the change is safe.
- Friction coefficient (coup_friction) is a numerical stability parameter in
  Genesis, not a direct stand-in for a literature-cited physical Coulomb
  friction value, even though this project uses 0.55 for both. Don't assume
  a citation for the physical value automatically justifies the numerical
  parameter's exact value without checking Genesis's own solver documentation.
- Before changing any parameter to "fix" a crash, state explicitly what else
  that parameter is coupled to and confirm those dependents were also
  checked, not just the one value that seemed like the obvious culprit.
```

---

## 5. Reusable Claude Code kickoff prompt

Paste this at the start of any new Claude Code session on this project, in addition
to (not instead of) CLAUDE.md already being read automatically:

```
Before doing anything: read CLAUDE.md, SESSION_STATE.md, PROVISIONAL_STATUS.md,
and kumar_july9_update/STATUS.md in full. Run git log --oneline -15 and git
status, and trust those over any written summary if they conflict. Check for
a KNOWN DEAD ENDS section in CLAUDE.md and treat everything listed there as
already answered — do not re-test it.

State back in 3-4 bullets: what you understand the current goal is, what's
already been ruled out, and what the single highest-value next test is. Wait
for confirmation before running anything.

If you're about to edit a parameter that has known dependents (box size,
density, grid_density, domain bounds — see the COUPLED VARIABLES section),
name the dependents and confirm they're accounted for before editing.

Before running ssh or idev, run hostname; pwd first and only issue the command
that actually applies to where you already are.

If another Claude Code session might be touching the same file right now,
check git status for uncommitted changes before editing it yourself, and
write your findings to a session-specific scratch file (logs/paneX_result.md)
rather than editing shared status files (STATUS.md, SESSION_STATE.md)
directly, unless you've confirmed you're the sole active session.
```

---

## 6. Final deployed-everywhere checklist, as of this pass

| Location | CLAUDE.md status | Skill status |
|---|---|---|
| `/work/11603/jcerrell0629/vista/CLAUDE.md` | Deployed, confirmed via diff/tail screenshot | Unconfirmed which version is installed |
| `/work/11603/jcerrell0629/vista/can-it-ford/CLAUDE.md` | Confirmed does NOT exist as a second file (empty `find` result) — one Vista file is sufficient, no second copy needed unless a later test shows Claude Code doesn't look up to the parent directory | N/A |
| `~/can-it-ford/CLAUDE.md` (Mac) | Built by a different session, never read or reconciled in this thread | Confirmed installed (Mac skills folder, "total 24" check) but which content-version, still unconfirmed |
| Claude Code actually reading the Vista file | **Unconfirmed — the read-behavior test (asking it the crash-status question) was prescribed twice and still hasn't been reported back** | — |
| GitHub | `CLAUDE.md` at the Vista parent level is confirmed NOT in any git repo — it will never appear on GitHub unless deliberately copied into the repo and committed. If you want Kumar or GitHub visibility on this file, that's a deliberate choice to make, not something that happens automatically. | — |
| Skill content parity (chat vs. Claude Code) | Not yet checked — Section "On whether Claude Code has what it needs" above | Real open gap |

**The one thing every remaining step depends on:** confirm the read-behavior test. Everything else in this pass is preparation for that moment, not a substitute for it.
