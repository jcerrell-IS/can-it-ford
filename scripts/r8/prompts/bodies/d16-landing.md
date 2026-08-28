## YOUR SLOT: d16-landing, branch `claude/r9-landing`, worktree `.claude/worktrees/r9-landing`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d16-landing` first.

### You are the only slot in this wave that writes no code and changes no result

Nine sessions ran last night on nine branches. **Every one of them is LOCAL ONLY and none is pushed.** Their work is real, it is committed, and right now it exists in exactly one place on one disk. Separately, `claude/add-ci-checks` is 64 commits ahead of origin/main and carries a six-check CI workflow that, because it is not on origin/main, RUNS NOWHERE.

Your unit is to produce `docs/R9_LANDING_PLAN_2026-08-18.md`: a plan for getting this work to a state where it is not one disk failure away from gone, and where the CI that exists actually executes.

### What the plan must contain, and every line of it must be derived live

1. **An inventory of the nine branches**, each with its commits, its declared write scope, and whether any two of them touch the same path. Derive this with `git -C /Users/josie/can-it-ford log` and `git diff --name-only`, per branch, not from anybody's summary including this dispatch.
2. **A merge order**, with the reasoning. Some of these branches base on each other; some base on `add-ci-checks`, which is itself hot and moving. Order matters and conflicts are cheaper to predict than to resolve.
3. **The conflicts you can already see**, named by file and branch pair, with a proposed resolution for each.
4. **What must NOT be merged**, if anything. There is a standing instruction that a specific register SHA must not be merged by name because merging a pinned SHA silently drops later lines; find it and honour it. Merge the tip re-derived at the moment of merging and verify with `git rev-parse HEAD^2`, never with a line count.
5. **The CI question**: what it would take for `.github/workflows/canford-checks.yml` to actually run, and what it would do the first time it did. A workflow that has never executed is not known to pass.

### Hard rules for this slot specifically

- **You may not push anything, merge anything, or delete any branch.** You are writing a plan for Josie to approve. `.git/hooks/pre-push` requires `PUSH_OK=1` and that is a guard, not an obstacle to route around. The repo is PUBLIC and every push is world-readable and permanent.
- **There is an unrotated credential exposure** covering roughly a dozen items across three machines, including an active GitHub PAT. That is unresolved and it is Josie's decision. Any plan that involves pushing must state the rotation question as a precondition rather than assume it away. Read `docs/CREDENTIAL_EXPOSURE_2026-08-13.md` if it is present in the main checkout.
- Note in the plan that all ten heads are already captured in `can-it-ford-bundles/2026-08-18/R8-nine-slots-2245.bundle`, restore-tested from a virgin mirror clone, but that the bundle is **on the same disk as the repo**, so it is protection against a bad merge and not against disk loss. Verify that the bundle still exists and still restores rather than repeating this sentence on my word.

Read `.claude/state/r8_board.md` end to end first. It is the record of what the nine slots did, including several correction rows where one slot refuted another, and at least one slot's own earlier rows still carry a claim it later withdrew. An append-only log's later rows can retract its earlier ones; read it in order.

No GPU. No code. One document, and it should be good enough that someone who was not here could execute it.
