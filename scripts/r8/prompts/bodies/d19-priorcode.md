## YOUR SLOT: d19-priorcode, branch `claude/r9-priorcode`, worktree `.claude/worktrees/r9-priorcode`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d19-priorcode` first.

## WHY YOU EXIST

Slot d17-moving is on a GPU node right now writing a moving-vehicle-in-a-flooded-channel driver largely from scratch. Your job is to find out **what other people have already written for this exact problem**, get their code where it is public, and compare it against ours so that d17 is troubleshooting against prior art rather than against its own intuition.

This is a research-grade literature-plus-code survey, and it has a consumer waiting, so bias hard toward things that are actionable tonight.

## THE PRIOR ART THAT IS ALREADY KNOWN, AS A STARTING POINT NOT AN ANSWER

Four prior vehicle fording or wading simulations exist and this project's `paper/` cites NONE of them:

- He et al 2026, `10.1115/1.4071177`
- Wasfy et al 2015, `10.1115/DETC2015-47142`
- Pazouki et al, Semantic Scholar `61da26b6`
- Khapane and Ganeshwade 2014, `10.4271/2014-01-0936`, cited nowhere in the repo at all

Plus, directly on the moving-vehicle question:
- **Al-Qadami et al 2022**, `10.1007/s11069-021-04949-6`, full-scale, found drag increased significantly with flow velocity, Froude number AND vehicle speed. Critical depth near 0.38 to 0.40 m, D x V near 0.36 to 0.39 m2/s. A SEPARATE Al-Qadami paper is `10.1111/jfr3.12828`, Wiley 2022, and a third is `10.3390/su151713262`, 2023. **Do not conflate them; a previous session did.**
- **Shah et al 2018**, `10.1051/matecconf/201820307003`, and Shah et al 2020, `10.1111/jfr3.12657`, which is 1:10 SCALE, so its drive force needs x1000 for full scale. Two separate instructions to relabel Shah 2020 as 2021 were both WRONG.
- **Zhao et al 2019**, `10.1016/j.compfluid.2018.10.007`, the MPM in/outflow BC, implemented in Anura3D. **Anura3D is open source. Get it and read how they actually did it.**
- **Pregnolato et al 2017**, `10.1016/j.trd.2017.06.020`, open access, the depth-only speed advisory.

## YOUR UNIT

1. **Find the code.** Anura3D for the in/outflow BC. Chrono::FSI, which is known to build and run on Vista aarch64 in 94 seconds, so it is a live comparison option not a multi-week port. CB-Geo MPM, NVIDIA Newton, and the vendored trees already under `REU_Knowledge` which include CB-Geo `mpm`, NVIDIA `newton`, `gns`, `diffmpm`, `lbm`, `x2sim` and Kumar's `LearnMPM`. Confirm what is actually there rather than trusting that list.
2. **Compare method by method**, focused on the three things d17 has to get right tonight: how a MOVING rigid body is coupled to the fluid, how inflow and outflow are imposed, and how the hydrodynamic force on the body is extracted. For each, say what the other implementation does, what ours does, and whether the difference matters.
3. **Deliver troubleshooting ammunition.** If Anura3D zeroes an accumulator we do not, or applies a wrench at a different point in the step, that is exactly what d17 needs and it needs it soon. Put anything urgent on the board addressed to d17 by slot the moment you find it, do not wait for your write-up.
4. **Verify every DOI TITLE against the resolved record**, not just that the link resolves. A real DOI with an invented title is the dominant fabrication pattern and this project has been bitten by it. Scholar Sidekick's `verifyCitation` and `auditBibliography` exist for exactly this; `resolveIdentifier` alone does NOT catch it.

## RULES

- A secondary source is not a primary one. Much of this project's corpus is AI-generated research reports; "report X says paper Y reports N" is not "paper Y reports N".
- Query the local corpus before declaring anything novel or missing: `python3 analysis/research_index.py --stats | --method X | --query X`. It holds 332 papers. Note that it is NOT a superset of the bibliography, so its silence is not evidence of absence; slot d14-corpusbib is resolving exactly that.
- You may download and read open-access papers and clone public repositories. Do not commit third-party source into this repo; the licence position is already contested and slot d10-licence spent last night on it.
- No GPU. No push.
