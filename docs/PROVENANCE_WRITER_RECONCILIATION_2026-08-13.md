# Reconciling the two run-provenance writers

**Date:** 2026-08-13
**Subject:** two sessions independently wrote a file at `analysis/run_provenance.py`, to
close the same audit item, neither aware of the other existed.
**Method:** both files read side by side, every population enumerated by path on both
machines, the bulk-modulus derivation falsified against the manifests that record both
quantities, and a dry run of the merged writer against all three populations.
**Outcome:** merged into one file. The two writers were never writing about the same runs.

Every claim below is tagged **[read]** (verified live this session, command shown or
re-runnable), **[recalled]** (from context or a prior document, not re-derived here) or
**[inferred]**. Engine tag: every manifest discussed here is **warpmpm**, not Genesis.

---

## FLAGS, raised per operating protocol. None of these stopped the session.

### FLAG A, protocol point 1: `--write` HAS ALREADY BEEN RUN. The dispatch says it was not.

The dispatch states the Mac writer's `--write` was "never run, deliberately, pending
Josie's call". **That is no longer true.** [read]

All 32 `*summary.json` manifests carry a `_provenance_backfill` block with
`"mode": "backfilled_after_the_fact"`, `"date": "2026-08-12"`, and an mtime of
**2026-08-13T00:03:08**. Reproduce:

```bash
python3 -c "import json,pathlib;fs=[p for p in pathlib.Path('/Users/josie/can-it-ford').rglob('*summary.json') if '.git' not in p.parts and 'worktrees' not in p.parts];print(sum('_provenance_backfill' in json.loads(p.read_text()) for p in fs),'of',len(fs))"
```

I did not do this and I have not undone it. **No data was lost:** the write is additive,
every original field is intact, and the block records honest labels. `params_check.py`
now reports only `bulk_modulus missing in 3` instead of five fields missing in all 32,
which is the deliberate orphan refusal and not a gap. [read]

Two consequences, both handled in the merged writer:

1. Any future `--write` is a **re-run**, not a first application. The merged writer is
   idempotent and preserves prior labels, so a re-run cannot silently upgrade a
   `reconstructed` field to `recorded`.
2. **The write destroyed its own evidence basis.** `canitford_git_commit` is
   reconstructed from the manifest's **mtime**, and an in-place back-fill rewrites the
   manifest and therefore updates that mtime. Every one of the 32 now has an mtime of
   2026-08-13, not its run date, so a *fresh* reconstruction would silently resolve
   against the back-fill date. The merged writer detects this and emits
   `mtime_basis_is_reliable: false` rather than using it quietly. The values already in
   place were computed before the rewrite and are unaffected.

### FLAG B, protocol point 3: one edit outside the declared scope, pre-announced

Definition-of-done item 3 requires writing the `aae75abf` artifact id into
`docs/REMEDIATION_PLAN_AUDIT_2026-08-12.md`. That file is outside the write list. The
dispatch authorises it explicitly and states DP-1 does not touch that file. Flagged here
first; the edit is a header addition only, no verdict or finding altered.

### Not a flag, but the dispatch's premise is wrong and the record should say so

The dispatch states "The provenance item is one of the refuted ones." **It is not.** [read]
`docs/REMEDIATION_PLAN_AUDIT_2026-08-12.md:213` lists run provenance as item 1 under
**"Still open, unchanged by this audit"**, and calls it "the largest single obstacle to a
reproducibility claim".

The confusion is real and worth recording, because it will recur: the audit contains
**two separate lists that both number from 1**. The verdict table at `:59-76` numbers the
plan's 18 items, and its item 1 is "Pull TACC job 895378" (REFUTED). The still-open list
at `:211-224` renumbers from 1, and its item 1 is "Run provenance" (open). Reading "item
1 is refuted" off the wrong list inverts the conclusion. This work rests on an open gap,
not a refuted premise.

---

## 1. The three populations, enumerated by path

The dispatch describes "three populations ... nobody has reconciled them", implying
competing counts of one thing. They are not. **The Mac writer's target set and the Vista
writer's target set are DISJOINT: not one file appears in both.** [read]

| glob | on the Mac | on Vista |
|---|---|---|
| `*summary.json`, repo-wide, excluding `.git/` and `worktrees/` | **32** | **0** |
| `data/coupling_validation*/**/*.json`, excluding `*.provenance.json` | **21** | **60** |

Reproduce:

```bash
cd /Users/josie/can-it-ford && find . -name "*summary.json" -not -path "./.git/*" -not -path "*/worktrees/*" | wc -l && find data -path "*coupling_validation*" -name "*.json" ! -name "*.provenance.json" | wc -l
```

So there are **two independent causes**, not one disagreement:

* **32 vs 21 is a different GLOB on the same machine.** Two different artifact families.
* **21 vs 60 is the same glob on a different MACHINE.** `data/` is gitignored, so nothing
  under it propagates; Vista simply has more runs.

`params_check.py` uses `ROOT.rglob("*summary.json")` at
[`.claude/checks/params_check.py:286`](.claude/checks/params_check.py:286), so its 32 is
**the same population and the same glob** as the Mac writer's. Those two never disagreed.
[read]

### Population A, `run_manifest`, 32 files on the Mac

The MPM run manifests. Flat schema: `hull_m3`, `mass_kg`, `n_grid`, `sound_speed_ms`.
Loads a real vehicle hull, so `mesh_sha256` is meaningful.

```
render_s2/multigeom_2026-08-08/{g64_rogue,g64_silverado,g64_yaris_regression}/summary.json   3
renders/yaris_render_s1/_incoming/{g48,g64,g96}_m{1100,1609,2337}/summary.json              9
renders/yaris_render_s1/_incoming/sweepD_g64_d0p{25,35,45}/summary.json                     3
renders/yaris_render_s1/_incoming/sweepV_g64_v{0p5,1p0,2p0,2p5,3p0}/summary.json            5
renders/yaris_render_s1/g64_m{1100,1609,2337}/summary.json                                  3
renders/yaris_render_s1/m{1100,1609,2337}/summary.json          3   <- register D4a orphans
renders/yaris_render_s3_enhanced/results/*_summary.json                                     6
```

### Population B, `coupling_validation`, 21 on the Mac / 60 on Vista

The coupling-validation harness outputs. Nested schema: `geometry.n_grid`,
`geometry.box_mass_kg`, `geometry.sound_speed`, `provenance.pinned_sha`. Procedural cube
collider, so `mesh_sha256` is inapplicable.

The Mac's 21 are `c0`/`c1`/`c1_rigid`/`c1sdf_{box,sdf}`/`c3_fixed2`/`ladder_{b,c,d}` at
g64 and g96, plus 4 under `smoke/`. Vista holds those plus 4 in
`coupling_validation_preclamp_894628/`, 4 in `coupling_validation_894642_nosubmersion/`,
and **31 newer files** from the friction rung (`fric_*`, `smoke_e_g64`) that postdate the
2026-08-12 back-fill. [read]

**Why they differ is not a mystery and needs no reconciliation:** `data/` is gitignored,
so these files exist in no git object and have never propagated between machines. The Mac
is not missing anything it should have; it simply is not where those runs executed.

### Four of Vista's 60 are not run manifests at all

`fric_index{,_hx,_hx2,_nokick}.json` are JSON **arrays** of 10 run summaries each, not
per-run manifests. The merged writer reports them as `not a JSON object` and **skips**
them rather than crashing or, worse, writing a provenance block into a roll-up index.
That leaves **56 usable** of Vista's 60. [read]

---

## 2. The two confidence vocabularies, mapped term by term

| Mac term | Vista term | Merged term | What it actually means |
|---|---|---|---|
| `recorded` | — | **`recorded`** | Present in the manifest under the audited name, written at run time. Untouched. Strongest. |
| `aliased` | `measured` | **`aliased`** | Same quantity, the manifest's own value, different key. Exact, no inference. |
| — | `derived` | **`derived`** | Computed from a value the manifest recorded, by a stated invertible formula. Exact. |
| `resolved` | `recorded` | **`resolved`** | Matched to a primary source by a measured discriminator, or read from a pin file. |
| — | `inapplicable` | **`inapplicable`** | The run genuinely has no such quantity. A positive assertion, never a synonym for absent. |
| `reconstructed` | `inferred` *(undeclared)* | **`reconstructed`** | Inferred after the fact. **Not evidence of what ran.** Weakest. |
| *(a separate `refused` dict)* | `unknown` | **`unknown`** | Could not be established. Value left absent, reason recorded. |

### `recorded` meant opposite things, and that is the collision that mattered

The Mac used `recorded` for its **strongest** label: already in the manifest, written at
run time. Vista used `recorded` for a **middle** label: copied from a pin declared in the
run script.

**The Mac reading survives.** Recorded-versus-reconstructed is the only axis this project
actually needs to police, and it is the axis registers D6a and D6h were written about.
Vista's sense is exactly what the merged `resolved` covers, so nothing is lost.

### Vista's `measured` overstated three fields

Vista labels `grid_density`, `vehicle_mass` and `solver_git_sha` **`measured`** when it
reads them out of the manifest under a different key name. Nothing was measured; a key was
renamed. The merged writer calls these `aliased`, which is what they are. This is a
strictly sharper distinction than either original made on its own.

### Vista emitted a sixth label its own vocabulary did not declare

`analysis/backfill_run_provenance.py:174` emits `"inferred"`, but
`analysis/run_provenance.py:62` declares only
`("measured","derived","recorded","inapplicable","unknown")`. Nothing caught it:
`audit_block()` reads `.get("confidence","unknown")` and passes any string through. [read]

The merged writer routes **every** label through `_label()`, which raises on anything not
in the declared tuple. The undeclared case is renamed `reconstructed` and is the one label
carrying an explicit "not evidence of what ran" warning.

### The first back-fill wrote free-text sentences, not labels

The 32 already-back-filled manifests carry `field_confidence` values like
`"aliased from mass_kg"` and `"RECONSTRUCTED from the manifest's mtime against git
rev-list..."`. Those carry the right meaning but are not drawn from a fixed set, so a
census over them produces one bucket per distinct sentence and cannot be summed. [read]

`normalize_label()` re-expresses them in the controlled vocabulary while preserving the
original sentence under `detail[field]["prior_label"]`. **Prior meaning still wins**, which
is what stops a re-run from relabelling a back-filled field as `recorded`. Confirmed in the
dry run: `canitford_git_commit` reports **`reconstructed=53`**, not `recorded`.

---

## 3. What survives from each writer, and why

**From the Mac:**

* **Hull matching that refuses.** 3 of the 32 are not the Yaris. Stamping the Yaris digest
  across all of them would have fabricated provenance for two runs. An unmatched hull
  leaves `mesh_sha256` absent with the reason recorded.
* **The orphan-rollout refusal** for `renders/yaris_render_s1/{m1100,m1609,m2337}`, per
  register D4a.
* **Atomic writes** via `os.replace`, and **prior-labels-win idempotency**.
* **Scope tested relative to root**, which is what stops a `--root` under any directory
  named `worktrees` from silently matching everything and printing `manifests 0`.

**From Vista:**

* **The exact bulk-modulus derivation**, `bulk = c**2 * rho / gamma`.
* **`inapplicable`** as a first-class category.
* **Run-script hashing** and `tracked_in_git`, the only durable pointer when a script is
  untracked.
* **Dirty-tree capture**, so a commit SHA recorded from a modified tree is not read as
  identifying the code that ran.
* **`_env`** capture: hostname, SLURM job id, python/warp/numpy/torch versions.

**Dropped:** Vista's `analysis/backfill_run_provenance.py` as a separate file. Its logic is
`--backfill` in the merged writer. **Do not port it to the Mac**; two files at two paths
doing one job is how this divergence started. Vista's copy is the only copy in existence
and was left untouched.

### The Mac writer refused a field it could have derived

The Mac writer refused `bulk_modulus` outright, reasoning that without `sound_speed_ms`
there is no input for `K = c^2*rho/gamma`. **That was right for the 3 manifests it
mattered for and too broad for the other 21.** Exactly 3 files lack `sound_speed_ms`, and
they are exactly the 3 D4a orphans, so they still refuse. Every `coupling_validation`
manifest records a sound speed, so for those the field was being needlessly withheld and
is now `derived`. [read]

---

## 4. The bulk-modulus derivation, and the test that had to pass first

Both drivers define the sound speed identically, so the inversion is exact:

```
renders/yaris_render_s1/sim_standing.py:225      c = float(np.sqrt(1.1 * bulk_modulus / water_density))
simulation/validate_coupling_force.py:18,19,22   RHO_W = 1000.0 ; BULK = 1.5e5 ; GAMMA = 1.1
                                                 =>  bulk = c**2 * rho / gamma      [Pa]
```

`rho` and `gamma` are constants read from **driver source, not from any manifest**, so the
derivation is only as trustworthy as those constants. It was therefore **falsified before
being used**, against every manifest that records both quantities:

```
family A: 29 of 32 record BOTH sound_speed_ms and bulk_modulus
          derived == recorded in 29/29, worst relative error 1.242e-16 (one float ULP)
          disagreements: 0
family A:  3 record neither  -> the D4a orphans -> refused, exactly as before
family B: 21 record sound_speed and NO bulk_modulus -> derivation is the only route
```

The constants are validated on the family that records both, then applied to the family
that does not. The round trip is bit-exact: `sqrt(gamma * 150000.0 / 1000.0)` reproduces
the recorded `12.84523257866513` **identically**, and `c**2` is exactly `165.0`. [read]

Every emitted block carries its own cross-check result, so a future manifest that breaks
the relation is **reported**, not silently overwritten. Where a manifest records a bulk
modulus, the recorded value always wins and the derivation is only a consistency check.

---

## 5. Dry run against all three populations

`--write` was **not** run in this session, in any form. All output below is a dry run.

### Populations A and B together, on the Mac

```
$ python3 analysis/run_provenance.py --backfill --root /Users/josie/can-it-ford

root      /Users/josie/can-it-ford
manifests 53
mode      DRY RUN, nothing will be modified

manifests by family
  coupling_validation      21
  run_manifest             32

per-field confidence census
  canitford_git_commit  reconstructed=53
  grid_density          aliased=53
  mesh_sha256           resolved=32, inapplicable=21
  solver_git_sha        resolved=32, aliased=21
  vehicle_mass          aliased=53
  bulk_modulus          recorded=29, derived=21, unknown=3

manifests that would change: 53/53
```

Reading it: **not one field is `recorded`** except the 29 bulk moduli. Every other value
is aliased, resolved, derived or reconstructed. That is the honest state of provenance for
these runs, and it is exactly what a presence-only gate cannot tell you.

### Vista's population, via a read-only local mirror

Vista is read-only this session, so the writer could not be copied there. Its manifests
were mirrored to a scratchpad instead and the dry run pointed at the mirror.

```
$ python3 analysis/run_provenance.py --backfill --root <scratchpad>/vista_mirror

manifests 60
  SKIP data/coupling_validation/fric_index.json: not a JSON object
  SKIP data/coupling_validation/fric_index_hx.json: not a JSON object
  SKIP data/coupling_validation/fric_index_hx2.json: not a JSON object
  SKIP data/coupling_validation/fric_index_nokick.json: not a JSON object

manifests by family
  coupling_validation      56

per-field confidence census
  canitford_git_commit  unknown=56
  grid_density          aliased=56
  mesh_sha256           inapplicable=56
  solver_git_sha        aliased=29, resolved=27
  vehicle_mass          aliased=56
  bulk_modulus          derived=56

manifests that would change: 56/60
```

Two results in that census are worth stating plainly.

**`canitford_git_commit unknown=56` is the cross-repo guard working, not a failure.** The
mirror is not a git repository, so the writer **refuses** rather than resolving the commit
against the wrong tree. This matters: the Vista clone shares no history with this one after
`b00bf7b`, so a commit id resolved from the Mac would be unresolvable on Vista, not merely
imprecise. Run on Vista itself, this column reconstructs from Vista's own history.

**`solver_git_sha aliased=29, resolved=27` is a real regression in the newer runs.** The 29
older manifests record `provenance.pinned_sha` themselves. The **27 newer `fric_*` and
`smoke_e` runs do not record it at all** [read], so the writer falls back to reading this
tree's pin file, which is a strictly weaker claim: it describes the pin as it stands now,
not the pin the run used. Worth fixing at the source in the friction-rung driver.

---

## 6. Decision on Vista's 29 sidecars: **KEEP them. Do not discard or regenerate yet.**

Established live [read]:

* All **29** sidecars map to a manifest that still exists. **Zero are orphaned.**
* They are **non-destructive**: they were written as `*.provenance.json` beside each
  manifest and no manifest was modified.
* They exist in **no git object anywhere**. They are the only copy, and `data/` is
  gitignored, so deleting them is unrecoverable.
* They now cover 29 of what is **56** usable manifests. The 27 uncovered are the newer
  friction-rung runs.

Nothing in them is *wrong*. They are expressed in the older vocabulary, and their
`inferred` label is the undeclared one. Regenerating requires running the merged writer on
Vista, which this session cannot do without write access there.

**Recommendation:** keep them as-is. In a later session with Vista write access, run the
merged writer with `--write-sidecar`, which both re-expresses the 29 in the controlled
vocabulary and extends coverage to the 27 uncovered runs. Until then they remain a valid,
if older, record. Do not delete them to "clean up".

---

## 7. Two premises in Vista's integration note are now stale

`analysis/PROVENANCE_V2_INTEGRATION.md` on Vista lists "two caveats that will keep firing
until they are fixed", and calls them "the real reproducibility gap". Checked live: [read]

1. **"The run script is untracked in git."** **CLOSED on both machines.**
   `simulation/validate_coupling_force.py` is `TRACKED` on the Mac (last touched by
   `79fec32`) and `TRACKED` on Vista. The caveat's premise no longer holds.
2. **"The tree is dirty."** **Still true on Vista**, 63 dirty paths as of this session.
   A recorded HEAD SHA there still describes the last commit, not the code that ran.

The note also says the forward-path patch was "verified but unapplied". **It has since been
applied on Vista:** `simulation/validate_coupling_force.py:1069-1081` calls
`collect_run_provenance` and assigns `res["provenance_v2"]`. The Mac's copy of that same
tracked file carries **no** such hook, so the two copies have diverged on this point.

`simulation/validate_coupling_force.py` is outside this dispatch's write scope (and the
`simulation/coupling_force/**` tree belongs to DP-5), so this is reported, not acted on.

**The merged writer keeps the applied call signature working.** Every keyword
`_provenance_v2_snippet.py` passes (`script`, `mesh_paths`, `solver_source`,
`solver_pinned_sha`, `grid_density`, `vehicle_mass`, `bulk_modulus`) exists in the merged
`collect_run_provenance`, so **the live Vista hook keeps working unchanged** against the
merged file. Verified by signature comparison. [read]

---

## 8. What Josie would run to apply this, and the backup step first

**Nothing here has been applied. `--write` was not run in any form this session.**

### Back up first. This is not optional.

These manifests are untracked and gitignored. There is no `git checkout --` to undo an
in-place edit, and another session is live in this tree.

```bash
cd /Users/josie/can-it-ford && tar czf ~/canitford_manifests_backup_$(date +%Y%m%d_%H%M%S).tgz $(find . -name "*summary.json" -not -path "./.git/*" -not -path "*/worktrees/*") data/coupling_validation
```

Success: a tarball of a few MB whose listing shows 32 `summary.json` plus the
`coupling_validation` tree. Verify with `tar tzf <file> | wc -l` before continuing.

### Then dry run and read the census

```bash
python3 analysis/run_provenance.py --backfill --root /Users/josie/can-it-ford
```

Success: `manifests 53`, and the per-field census above. Most likely failure mode: a
different count, which means the population changed and the census must be re-read before
anything is written.

### Then apply, sidecar mode, which touches no manifest

```bash
python3 analysis/run_provenance.py --backfill --root /Users/josie/can-it-ford --write-sidecar
```

Success: `sidecars written or updated: 53/53`, and `git status` still shows no change to
any manifest. This is the recommended apply: it is additive, reversible by deleting the
sidecars, and cannot corrupt a manifest.

### Only if in-manifest fields are actually required

```bash
python3 analysis/run_provenance.py --backfill --root /Users/josie/can-it-ford --write-in-place
```

This edits the manifests. It is atomic per file and idempotent, but irreversible without
the backup. **It also updates every mtime**, which is the basis `canitford_git_commit` is
reconstructed from, so run it only after the backup exists. Since a back-fill has already
been applied on 2026-08-13, re-running is a re-run: prior labels are preserved and no
field is upgraded to `recorded`.

### On Vista, in a session that has write access there

```bash
cd /work/11603/jcerrell0629/vista/can-it-ford && python3 analysis/run_provenance.py --backfill --write-sidecar
```

Expected: 60 manifests, 4 index files skipped, 56 sidecars, and
`canitford_git_commit` reconstructed from Vista's own git history instead of `unknown`.

---

## 9. Open, not closed by this work

1. **The 27 newer `fric_*` / `smoke_e` runs do not record `provenance.pinned_sha`.** Fix at
   the source in the friction-rung driver so new runs record it rather than relying on a
   back-fill fallback.
2. **Vista's tree is dirty (63 paths).** While that holds, a recorded HEAD SHA there does
   not identify the code that ran.
3. **The Mac's `validate_coupling_force.py` lacks the forward-path hook** that Vista's copy
   has at `:1069-1081`. Out of scope here (DP-5).
4. **Presence is not provenance.** `params_check.py` tests only that the keys exist, so it
   now passes on manifests whose values are `reconstructed` and `aliased`. The gate should
   read `field_confidence`, not just the key set. Until it does, passing it is necessary
   and not sufficient, and that is stated in every block the writer emits.
