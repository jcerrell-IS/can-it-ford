# SLOT d4-bcmerge

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-bc-merge, branch
claude/r8-bc-merge, branched off the COMMON ANCESTOR 1a868f3.

You may write ONLY:
  simulation/openchannel_bc.py            (the reconciled module)
  docs/R8_OPENCHANNEL_BC_RECONCILE.md     (new)

NEVER TOUCH claude/add-ci-checks or claude/r7-inflow in any way. Both are owned elsewhere and
r7-inflow has a live session. READ from them with `git show`. Do not merge, rebase, cherry-pick
or push to either.

## WHERE THIS LEFT OFF: NOWHERE. This is a crossover nobody noticed.
simulation/openchannel_bc.py was written TWICE, independently, after a common base of 1a868f3
where the file does not exist:

  claude/add-ci-checks  34941 B  5 commits (be1b138, 7933f1e, 89aae02, 1e6732b, 1315a4a)
     tilted_gravity:51, RecyclingChannelBC:73, depth_profile:214, _selftest:238,
     OverfallBC:341, overfall_metrics:406, discharge_per_width:427, ReservePool:514
  claude/r7-inflow      13725 B  1 commit  (5ecf725 "Port the Zhao 2019 recycling in/outflow BC
                                            to the vehicle scene, without touching the driver")
     tilted_gravity:51, RecyclingChannelBC:73, depth_profile:193, _selftest:217

The shared prefix is NOT byte-identical: depth_profile sits at :214 versus :193, so the
RecyclingChannelBC bodies differ by roughly 21 lines. Ledger row 7 points at the add-ci-checks
copy as the source of the port while r7-inflow wrote its own and declared item 7 closed. A plain
git merge is an add/add conflict at best and a silent overwrite at worst.

## THE RESEARCH
Zhao, Bolognin, Liang, Rohe & Vardon 2019, Computers and Fluids 179, 27-33,
doi 10.1016/j.compfluid.2018.10.007, implemented in Anura3D. This is the in/outflow BC the
project needs and it is NOT Kumar. Translating it into warpmpm is a translation, not a port.
One of only two papers on the corpus inflow-outflow axis, and already cited.

The premise section 6 was written on is now QUALIFIED by r7-inflow itself: "The first wall
reflection arrives at frame 112.3" reproduces ONLY as a still-water shallow-water round trip.
The scene runs at Fr 0.88, where an upstream-travelling wave makes 0.1995 m/s and needs about
478 frames. Do not inherit 112.3 unqualified.

r7-inflow's measured result, which your reconciliation must not contradict: 3 configs x 2
horizons x N=5, NO verdict moves anywhere, while the displacement behind those unmoved verdicts
rises 15 to 521 percent.

## FIRST STEP, before writing any code
  git -C /Users/josie/can-it-ford show claude/add-ci-checks:simulation/openchannel_bc.py > /tmp/a.py
  git -C /Users/josie/can-it-ford show claude/r7-inflow:simulation/openchannel_bc.py > /tmp/b.py
  diff -u /tmp/b.py /tmp/a.py | head -200
Establish which RecyclingChannelBC body is correct where they differ by reading what each does.

## DEFINITION OF DONE
1. A reconciled module whose _selftest passes on the Mac with no solver and no GPU.
2. A document naming, line by line, every disagreement and which version won and why. "The
   longer one" is not a reason.
3. An explicit answer to whether the vehicle-scene port and the overfall/ReservePool extensions
   can coexist in one module or genuinely need to fork, argued.
4. NOTHING pushed to add-ci-checks or r7-inflow.
