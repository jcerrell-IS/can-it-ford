# ROUND 3, D13 CHRONO-GH200-GONOGO

Read `ROUND3_SHARED.md` first.

## Yes to the x86 reproduction. Take it, CPU-only.

You asked: "does the GetNormal defect reproduce on x86? If yes it's a general
Chrono/Bullet defect; if no it's aarch64-specific and becomes a real caveat on
the GO verdict. Say the word and I'll take it on a CPU slot, it must not consume
an A100."

**Take it.** It is the single question that decides whether your GO verdict ships
with a caveat, it is cheap, and it is CPU-only so it costs nothing anyone else
wants. Your constraint is respected and is now moot anyway: there are no A100s
to protect. LS6 is unreachable non-interactively (cold ControlMaster socket, it
demands a TACC token at an interactive prompt) and both node allocations have
expired. Vista has 641 SU and an empty queue; use a CPU partition there, batch
not idev.

Report it three ways, since the answer branches:
- reproduces on x86: general Chrono/Bullet defect, and it should go upstream.
- does not reproduce: aarch64-specific, and the GO verdict carries a stated
  caveat naming the architecture.
- cannot be determined: say which step blocked, and leave the defect UNREVIEWED.

Keep the UNREVIEWED mark until it reproduces somewhere other than your own
session. You were right that a claim against a third-party library from one
session should not be cited as a Chrono bug, and the standing rule agrees: one
source cited twice is not two sources.

## Your defect trace is now a design rule for D10, delivered

You pinned it down: Chrono populates the value correctly from Bullet
(`ChCollisionSystemBullet.cpp:402-403`), so the bad value originates in Bullet's
trimesh raycast callback, and it lands on the **NORMAL** rather than the height,
returning 0.9998 off vertical.

D10 has the operational consequence in its own follow-up: on a reconstructed OBJ
scene, use rigid or FEA tyres (they go through the contact engine and never
consult `GetNormal`), or use a heightfield or box patch instead of a trimesh.
D10 has also folded your off-patch result into its five-instance pattern of
"wrong configuration produces a plausible number instead of an error", which it
is writing up as a design rule with numbers from its own arms (excursion 0.664,
0.937, 1.562 m across slope; a margin sized at S=0 is wrong by 2.35x at S=0.06).

## Your ceiling is right and must stay on the front page

Unchanged and not to be softened: Chrono fording is a physics demonstration, not
validated against experimental fording data; its validated strength is soil
terramechanics; no NG-NRMM figure is cited anywhere. **Switching buys
architecture, not validation.**

One sharpening from D11 that belongs beside it, because it is the same
distinction stated from the literature side: no engine has a validated fording
*verdict*. He 2026 validates transient response at model scale, which is why the
correct phrasing is "no validated fording verdict in any engine", not "no
validated fording chain". That was my over-strong wording earlier and you should
not inherit it.

## Your idle-card call was correct and is now overtaken

You said you had nothing GPU-bound, that both probes link only
`-lChrono_core -lChrono_vehicle -lyaml-cpp` with no `Chrono_fsisph` and no CUDA,
that they are Bullet raycast work and pure CPU, and that the A100s should go to
D5's 2x2 and D10's cross-slope sweep.

That was the right read of your own scope. It is overtaken by machine state
rather than by any error: LS6 is offline, so there are no A100s to reallocate,
D5's LS6 job 3364582 is moot, and D10's cross-slope sweep is blocked on
validating its Zhao 2019 outflow BC first, which is CPU-cheap work it can do
without a node. Nobody is waiting on a GPU decision from you.

## Skills and state

Call `bug-triage-protocol` for the x86 reproduction and
`tacc-terminal-and-file-transfer` for the Vista CPU submission. Use
`/Users/josie/can-it-ford/scripts/tacc.sh vista '<cmd>'`, which works
non-interactively right now. Submit batch, never idev: idev burned 98.5 to 99.1
percent of Vista node-hours and 95 of 184 interactive jobs ended in TIMEOUT.

Three commits unpushed (f1cb25b, 840c610, 3372ad9), held pending Josie's
per-branch check; do not re-ask each turn. Vista `/home1` is 89.15 percent full,
so do not install into it; build under `/work`, which is at 5.49 percent.
