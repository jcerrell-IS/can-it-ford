STANDING OPS ADDENDUM, from the coordinating session. 12 other Claude Code
sessions are live RIGHT NOW in sibling worktrees of this same repository. This
is not a new task. It is how to keep your own work safe and how to unblock
yourself without stopping.

1. WHAT "DIRTY" MEANS, AND THE THREE WAYS IT BITES
   Dirty = uncommitted entries in YOUR worktree (modified + untracked). Normal
   mid-task. It is a hazard in exactly three ways, all of them self-fixable:
   (a) Uncommitted work does not survive a context compaction with its reasoning
       intact. Commit each coherent unit AS YOU FINISH IT, not at the end.
   (b) .git/hooks/pre-commit REFUSES any commit with more than 8 staged files.
       Stage in batches of 8 or fewer. If a commit is rejected and the reason is
       not obvious, that is the reason.
   (c) .git/hooks/pre-push requires PUSH_OK=1 in the environment.

2. COMMIT THE SAFE WAY, EVERY TIME
     git -C <your worktree> status --porcelain=v1      # re-check IMMEDIATELY before
     git -C <your worktree> commit -m "msg" -- path1 path2
   The trailing `-- path` form is load-bearing: a bare `git commit -m` can sweep
   in entries another session already staged. Never `git add -A`, `git add .`,
   or `git commit -a`. Confirm a push LANDED with `git ls-remote --heads origin`,
   never with the exit code.

3. THE ONE MISTAKE THAT SILENTLY CORRUPTS ANOTHER SESSION
   Writing to an ABSOLUTE path under /Users/josie/can-it-ford/... lands in the
   MAIN checkout, not in your worktree, on a branch that is not yours. Use paths
   relative to your own worktree root. The main tree's dirty set is frozen at 26
   pre-existing entries and a 27th raises an alarm within 20 seconds.

4. FILE OWNERSHIP, so you can resolve a collision yourself instead of stopping
   docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md   D4 only
   docs/CREDENTIAL_EXPOSURE_2026-08-13.md              D3 only
   analysis/vehicle_mesh_transform.py, flood_water_optics.py   D6 only
   simulation/moving_vehicle_driver.py and the SDF driver      D9 only
   simulation/fork_scene/                              D10 only
   analysis/stationarity.py, analysis/floor_penetration_*      D12 only
   ~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/   D7 only
   data/all_runs_inventory.csv and
   renders/yaris_render_s1/gates_results_all_runs.json  FROZEN, nobody writes
   If you need a change inside someone else's file, write the request into your
   OWN findings doc and name the owning dispatch. Do not edit it yourself.

5. WHEN YOU ARE BLOCKED, DO THIS BEFORE YOU STOP
   Try a second genuinely different approach, not a variation of the first.
   Then check: DeepWiki for how a library actually behaves (treat its answer as
   a hypothesis and verify against source), Wolfram for any physical parameter
   or unit conversion, Scite or Scholar Sidekick for any DOI, and the
   physics-skeptic subagent before finalising any percentage, force, verdict
   count or distance. If a connector is unavailable, say so and mark the claim
   UNREVIEWED rather than faking the review. Then keep working on the rest of
   your scope: one blocked item does not end the session.

6. LIVE CLUSTER STATE, checked 2026-08-14 17:35. Use this, do not guess.
   Vista  gh-dev        15 nodes IDLE      643 SU
          $HOME is 89.15% FULL (20.8 of 23.3 GB). Do NOT pip install into it.
   LS6    gpu-a100-dev   4 nodes, ALL ALLOCATED    9591 SU
          gpu-a100      73 nodes, all allocated
          gpu-h100       4 nodes, all allocated
   LIVE GPU ALLOCATION on Vista, added 17:42 CEST:
     JobId 911518, node c642-011, gh-dev, NVIDIA GH200 120GB / 97871 MiB,
     2:00:00 limit started ~17:37, so it EXPIRES AROUND 19:37 CEST.
     ASSIGNED TO D13. Everyone else: login-node work stays on the login node,
     per CLAUDE.md. Do not consume it.
     Reach it (both verified live):
       ssh v-c642-011 '<command>'
       scripts/tacc.sh vista "srun --jobid=911518 -p gh-dev -t 00:10:00 -N1 -n1 <cmd>"
     TRAP: the TACC submit filter rejects srun without BOTH -p and -t, even
     though the allocation already exists.
   In flight: LS6 3364497 "3class" PENDING on Resources (D5).
   Account BCS20003 on both, both expire 2026-09-30.
   Reach either machine non-interactively:
     /Users/josie/can-it-ford/scripts/tacc.sh vista '<command>'
     /Users/josie/can-it-ford/scripts/tacc.sh ls6   '<command>'
   Submit BATCH, not idev: idev burned 98.5 to 99.1% of Vista node-hours and 95
   of 184 interactive jobs ended in TIMEOUT. LS6 shows 0 batch timeouts.
