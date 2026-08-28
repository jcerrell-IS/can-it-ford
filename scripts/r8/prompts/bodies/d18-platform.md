## YOUR SLOT: d18-platform, branch `claude/r9-platform`, worktree `.claude/worktrees/r9-platform`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d18-platform` first.

## YOUR JOB IS RETURN ON INVESTMENT, NOT INTEGRATION FOR ITS OWN SAKE

Josie asked what Hugging Face, Weights and Biases, GitHub and similar platforms can actually do for this project. Your unit is to find the answers that are worth the effort and to say plainly which ones are not. A connector that works but produces nothing anyone will look at is a negative result and should be written up as one.

## WHAT IS ALREADY TRUE, VERIFIED, DO NOT REDISCOVER IT

- **Weights and Biases is live and healthy.** 105 runs, most recent 2026-08-17. The key ending `iNbz` is DEAD and returns 401; the live one ends `ipS9`. `~/.netrc` and `.zshrc` held the dead one until it was fixed on 2026-08-17. **W&B already links every run to its GitHub commit, so do not build that.**
- **Hugging Face auth is OK as `josiecerrell`.** But the hub-sync workflow previously mirrored all 407 MB including licence-unresolved NCAC models, so fixing the token alone made things worse. The workflow was rewritten to push `hf_space/` only, and the Space is kept PRIVATE until two README claims are corrected. **Find out whether those two claims are still wrong before you make anything public.**
- **CI EXISTS BUT RUNS NOWHERE.** `.github/workflows/canford-checks.yml` is on `claude/add-ci-checks` and NOT on `origin/main`, so it has never executed. Slot d16-landing is writing the landing plan for that; coordinate through the board rather than duplicating.
- **The repo is PUBLIC.** Every push is world-readable and permanent, and GitHub has served removed blobs by SHA in this account.
- **There is an unrotated credential exposure**, roughly a dozen items across three machines including an active GitHub PAT. It is unresolved and it is Josie's decision. **Nothing you build may depend on publishing before rotation.** Design for private-by-default and say what flips it public.

## THE HIGH-VALUE TARGET, and it is specific

Slot d17-moving is on a GPU node right now producing something this field does not have: a **(vehicle speed x flow velocity) load surface** for a vehicle crossing a flooded roadway. The literature is entirely binary thresholds; no paper outputs a graded safe crossing speed as a function of both depth and flow velocity.

That artifact is worth publishing well, and it is the thing to design your platform work around:

1. **A Hugging Face dataset** of the run records, with a real dataset card: variables, units, what the numbers do and do not mean, the fact that the vehicle is PRESCRIBED not free, and the known limitations. This project's own history says the danger is a number travelling without its scope, so the card is the deliverable, not the upload.
2. **A Hugging Face Space** that renders the surface interactively, so the result can be looked at rather than read about. Keep it PRIVATE until Josie says otherwise.
3. **A W&B sweep view** of the matrix, so the repeats show as distributions rather than points. This project's own argument is that its repeat ensembles are the ingredient the field lacks, so a plot of single points would undercut it.

## WHAT TO INVESTIGATE AND REPORT ON, WITH A VERDICT EACH

Go and find out, do not assume: Hugging Face datasets, Spaces, model hosting, and inference; W&B sweeps, reports and artifacts; GitHub Actions, Releases and Pages; Zenodo or similar for a DOI on the dataset. For each, write **worth it and why**, or **not worth it and why**, with the effort estimate. A short honest list beats a long speculative one.

Two the coordinator suspects are high value but has NOT verified, so treat them as hypotheses: a DOI-bearing archived dataset is the thing a paper can cite and a Space is the thing a reviewer will actually click; and GitHub Releases plus a bundle would fix the fact that fifteen branches of tonight's work exist only on one disk.

## HARD LIMITS

- **Do not publish anything publicly.** Not a Space, not a dataset, not a Release. Build it, make it work, keep it private, and hand Josie the switch. Publishing is an outward-facing irreversible action and it is hers.
- **Do not print, echo, or commit any credential value.** Test for presence, never read the value.
- Do not edit `.github/workflows/` if d16-landing has claimed it on the board; check first.
- `uv` at `/Users/josie/.local/bin/uv` for any Python dependency. Josie has authorised installing what you need.
