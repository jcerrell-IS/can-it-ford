# Trackio on a Vista compute node: can it log fully offline and sync later?

Research and design note only. Nothing was built. The existing W&B pipeline was not
touched. Written 2026-08-27.

Held in the scratchpad rather than in the repo on purpose: a concurrent session ran
`git reset --hard` plus `git clean -fd` on this working tree at roughly 22:05 tonight
and destroyed every untracked file in it. See the session report.

## Verdict

**Yes, with three conditions.** Trackio's local-first mode is a genuine offline mode,
not a degraded online mode, and the deferred upload is a documented first-class
function rather than something that has to be improvised.

## Evidence, all [CONFIRMED] by reading primary source

Repo identity, from the GitHub API on 2026-08-27:
`gradio-app/trackio`, described as "A lightweight, local-first, and free experiment
tracking library from Hugging Face", `archived: false`, last push
`2026-08-27T17:46:31Z`. Actively maintained as of today.

1. **Local-first is the default, and needs no account or network.** README line 26:
   local-first "because you shouldn't need to make an account to log data". Line 175:
   when calling `trackio.init()`, "by default the service will run locally and store
   project data on the local machine". Network involvement begins only when a
   `space_id` or `TRACKIO_SERVER_URL` is passed.

2. **Deferred upload is a documented function, under a heading that names this exact
   use case.** README line 205 is headed "Syncing Offline Projects to Spaces", and
   line 207 reads "If you've been tracking experiments locally and want to move them
   to Hugging Face Spaces for sharing or collaboration, use the `sync` function", with
   the form `trackio.sync(project=..., space_id=...)`. Line 219: "This uploads your
   local project database to a new or existing Space."

3. **Logging cannot block on the network.** README line 306: `trackio.log()` "is a
   non-blocking call that appends to an in-memory queue and returns immediately", with
   a background thread draining to local SQLite every 0.5 s, and "log calls never touch
   the network". Line 308: Trackio-side failures "degrade to warnings and local
   buffering rather than exceptions from your training loop".

4. **The store is a plain SQLite file whose location is overridable by env var.**
   [CONFIRMED] by reading `trackio/utils.py:199-204`, not from docs:

       if os.environ.get("TRACKIO_DIR"):
           return Path(os.environ.get("TRACKIO_DIR"))
       ...
       TRACKIO_DIR = _get_trackio_dir()

   Default is `~/.cache/huggingface/trackio` (README line 407).

## Why this fits Vista better than the W&B offline pattern

The W&B recipe carried in the integration doc is `WANDB_MODE=offline` plus a dependent
`sbatch --dependency=afterok` job running `wandb sync`. That works, but it needs a
second SLURM job, so it spends a second 15 minute billing floor per run.

Trackio's store is one SQLite file on a shared filesystem. `$SCRATCH` and `$WORK` are
visible from both compute and login nodes on Vista, so the sync step does not need to
run in the allocation at all. It can run on the login node afterward, at zero SU cost.
That removes the dependent job entirely.

## The three conditions

**Condition 1: relocate the database off `$HOME`.** The default
`~/.cache/huggingface/trackio` is the wrong place on TACC: `$HOME` has a small quota,
and the point of the exercise is that the login node must be able to read the same
file the compute node wrote. Set `TRACKIO_DIR` to a shared path in the batch script:

    export TRACKIO_DIR="$SCRATCH/can-it-ford/trackio"

`$SCRATCH` is subject to the purge, which keys on file atime, so for anything meant to
outlive a run use `$WORK` instead.

**Condition 2: pin the version.** README line 407 states Trackio "is in pre-release
right now and we may release breaking changes. In particular, the schema of the
Trackio sqlite database may change." A provenance store whose schema can move under
you is a liability, and the note already records that newer databases use a stable
`run_id` plus non-unique `run_name` while older ones are read in a compatibility mode
keyed on `run_name`. Pin an exact version in the environment and record that version in
the run manifest alongside the git SHA.

**Condition 3: the sync step needs an authenticated login node.** README line 189: you
"should be logged in with the `huggingface-cli` locally and your token should have
write permissions to create the Space." That is a login-node prerequisite, and it is a
write-scoped token, so it should not be placed in any tracked file.

## Sketch, not built, not tested

Batch script on the compute node:

    export TRACKIO_DIR="$WORK/can-it-ford/trackio"
    python3 sim_standing.py

Afterward, on the login node:

    python3 -c 'import trackio; trackio.sync(project="can-it-ford", space_id="josiecerrell/can-it-ford-trackio")'

## What was NOT established

- Not tested on Vista. Nothing here was executed on a compute node. The claim that a
  fully offline `trackio.init()` completes with no network is read from source and
  documentation, [DOC] and [CONFIRMED] respectively for the code paths quoted, but it
  is [INFERRED] that it holds under Vista's specific network isolation.
- The premise that Vista compute nodes have no outbound internet is itself carried
  from the integration report and was not measured.
- `trackio.sync` is documented in the README but was not located as a `def sync` in
  `trackio/__init__.py`, so its exact signature and its behaviour on a database that
  has never once had network access are unverified. Test both before relying on them.
- No comparison was run against the existing W&B path on real data. This note argues
  the architecture fits, not that it reproduces current numbers.
