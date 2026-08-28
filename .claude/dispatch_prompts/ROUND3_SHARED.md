# ROUND 3 SHARED ADDENDUM, 2026-08-14 22:40 CEST

From the coordinating session, after reading all 13 panes live and verifying
every claim below against the filesystem or git. Read this, then read your own
`ROUND3_D<N>.md` in the same directory.

## 1. THE ~/Downloads BLOCK IS NOT A CONTENT BLOCK. IT NEVER WAS.

Five of you (D1, D2, D7, D9, D11) reported research artifacts as unreadable
because `~/Downloads` returns `Operation not permitted`. That is a real TCC
denial and it is still real. It is also **irrelevant**, because every artifact
you named exists in full outside that directory.

Verified live by `find` at 22:38, all readable, all `head`-confirmed:

    /Users/josie/Claude/reu/                     63 .md artifacts
    /Users/josie/Documents/Claude/reu/           mirror
    /Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/   sorted by topic

Specific ids that were reported blocked and are readable right now:

    65474f37  Citation Provenance Audit: the mu = 0.55 friction coefficient in
              Azhar, Pauwels & Bui (2023). Confirmed by reading its own H1.
    5e706c91  forensic friction audit, vendored engine vs this repo
    c963203d, a1fd6fdc, d50d614c
    8f2c67a9
    82c51733  Code-Level Analysis: PLY Loading in kks32/mpm-engine, splats
              module and load_vehicle. Confirmed by reading its own H1.

Canonical readable path form:

    /Users/josie/Claude/reu/compass_artifact_wf-<ID>-..._text_markdown.md

Use `find /Users/josie/Claude /Users/josie/Documents /Users/josie/Desktop
-maxdepth 5 -name '*<8-hex-id>*'` to resolve any id.

**Do not report an artifact as unreadable again without running that find
first.** "Absent from the one directory I checked" is not "absent", and this
round it produced five independent false negatives.

The perplexity directory is also readable, at
`/Users/josie/Documents/CAN_IT_FORD_ARCHIVE_2026-07-17/research_reports_and_citations/perplexity_research`.

## 2. register_integrity.py: THE OWNERSHIP DEADLOCK IS BROKEN, D8 OWNS IT

D1, D8 and D11 each independently found that when `~/Downloads` is denied, the
checker reports real citations as "may be fabricated", and each of you declined
to fix it on ownership grounds. Three declines is a deadlock, not caution.

D11 measured it precisely: the tool moved from "10 research-artifact, 1
unresolved" to "0 research-artifact, 11 unresolved" **with the register file
unchanged**. 10 + 1 = 11 exactly. Only 185968e0 was genuinely unresolved in
both runs.

Decision: **D8 applies its own four-point patch.** D8 wrote it, D8 has 0
unpushed commits, and the file is tooling, not a claims file. D4 re-runs the
checker afterwards and reports whether its reconciliation numbers move. Nobody
else touches it.

Interim rule until that lands, for everyone: **a research-artifact count of 0
is a broken probe, not evidence about the register.** Section 1 above means the
probe should now also search the readable mirrors, not only `~/Downloads`.

## 3. THE mu = 0.55 CONVERGENCE, SIX SESSIONS, ONE FINDING, NO OWNER

Six of you reached the same conclusion from six different directions and none of
you consolidated it. Restated so nobody has to re-derive it:

- D2  regime table: skidding 0.16-0.48, ARR assumed 0.3, this project 0.55,
      Smith 2019 swept 0.3 and 0.78, stationary flooded 0.85-1.15. 0.55 sits in
      the gap between the two measured regimes.
- D2's caveat, load-bearing, carry it verbatim: ARR's is tyre-on-road across
      four contact patches in an analytical force balance; ours is a Coulomb
      coefficient in the MPM floor contact across the whole hull underside.
      Comparable in direction and magnitude, **not the same quantity**. No claim
      may say 0.55 "is" a measured tyre friction.
- D4  from the AR&R primary PDF: the 0.3 is Bonham & Hattersley's 1967
      assumption carried forward, not an ARR measurement.
- D11 provenance chain: a spring-balance measurement of a lab rubber mat,
      chaining to a 1969 GM tyre brake-force study, general automotive, not
      submerged. Against the 0.3 convention it raises T_avail by 83%.
      Corroborated independently at 22:39 by reading artifact 65474f37's own
      TL;DR: mu = 0.55 is Azhar, Pauwels & Bui (2023)'s own laboratory
      measurement of their experimental rubber mat, citing Wong, *Theory of
      Ground Vehicles*.
- D5  resolution-dependence is itself friction-dependent: at mu = 0.30 a 37%
      refinement moves the margin 10 to 11 frames. **Register J15's finding must
      therefore carry its mu.**
- D6  the caveat is now on every rendered frame. All three panels read NO-FORD,
      the conservative direction. It is the Silverado's flip into STUCK that
      sits on the optimistic side of a friction value near double the
      convention.
- D9  the moving scene uses COLLIDER_FRICTION 0.4, a **fourth** value, not yet
      reconciled with the 0.55 floor or the 0.3 convention.

Direction is consistent across all six: **0.55 biases away from a slide verdict,
and 16 of 17 gated verdicts are SLIDE.** That is the conservative direction for
the published verdicts and the optimistic direction for the Silverado flip.

Owner: **D4** writes the single consolidated register entry. D2, D5, D6, D9 and
D11 each confirm or correct only their own line above, in one paragraph, and do
not restate the whole thing. Nobody edits CLAUDE.md.

## 4. LIVE MACHINE STATE, MEASURED 22:35, NOT RECALLED

    Vista   queue EMPTY, 641 SU, expires 2026-09-30
            /home1 89.15% full (20.8 of 23.3 GB). Do NOT pip install into it.
            /work 5.49% used, /scratch effectively unlimited.
    LS6     UNREACHABLE non-interactively. The ControlMaster socket is cold and
            cannot be warmed from a tool call: it demands a TACC token at an
            interactive prompt. Josie must run `ssh ls6` once in a terminal.
            Until then, treat LS6 as offline. Do not queue work behind it.

Both previous node allocations (Vista 911518 / c642-011, LS6 c301-004) have
**expired**. There is no live node. Anything GPU-bound needs a fresh `sbatch`,
not `srun --jobid=`.

Submit BATCH, never idev: idev burned 98.5-99.1% of Vista node-hours and 95 of
184 interactive jobs ended in TIMEOUT.

## 5. PUSH STATE

Josie's standing answer is "authorize, but I verify each first". So: **hold, and
stop re-asking each turn.** The gate is `scripts/canford_monitor.sh pushcheck
<branch>`, which blocks mesh, artifact and credential paths. Unpushed counts
measured live at 22:34:

    D1 1   D2 4   D3 5 (DO-NOT-PUSH, correct)   D4 5   D5 5   D6 5
    D8 0   D9 10  D10 7   D11 0   D12 8   D13 3

Note D5: you reported six, `rev-list --not --remotes=origin` says five. Re-check
before quoting the number.

## 6. STANDING, UNCHANGED

Never `git add -A` / `git add .` / `git commit -a`. Stage explicit paths and
commit with the `-- path` form. Max 8 staged files per commit (pre-commit hook).
Push needs `PUSH_OK=1` and Josie's per-branch go-ahead. Writing to an absolute
`/Users/josie/can-it-ford/...` path lands in the MAIN checkout, not your
worktree: main is frozen at 26 dirty entries and a 27th is an alarm. E8: derived
hull geometry and rendered artifacts never reach the public repo. No em-dashes.
