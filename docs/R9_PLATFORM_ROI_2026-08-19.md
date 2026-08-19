# R9 d18-platform: what the platforms are actually worth

Slot `d18-platform`, branch `claude/r9-platform`, 2026-08-19.

The question was return on investment, not integration. A connector that works but
produces nothing anyone will look at is a negative result, so the negatives below are
written up with the same care as the positives.

Every claim is tagged **[read]** (read live this session), **[recalled]** (from context,
not re-verified), or **[inferred]**. Nothing here is carried from a summary.

---

## 1. The verdicts, in one table

| platform | verdict | effort | why |
|---|---|---|---|
| **Zenodo DOI** | **WORTH IT, do this first** | ~1 h | the only item that produces a thing a paper can cite, and it does **not** require publishing the data |
| **HF dataset + card** | **WORTH IT, built** | done, ~2 h | the card is the deliverable; the upload is trivial |
| **HF Space** | **WORTH IT, built** | done, ~2 h | the only artifact a reader can interrogate rather than read |
| **W&B grouped runs + tables** | **WORTH IT, built** | done, ~1 h | shows repeats as ensembles; but see the naming correction in §4 |
| **W&B Reports** | **worth it, cheap** | ~1 h | a linkable write-up next to the runs |
| **GitHub Actions** | **worth it, NOT MINE** | d16-landing | with a warning in §6 that it currently cannot fail |
| **W&B Artifacts** | **not worth it, yet** | ~2 h | the tables are 12 KB and git already versions them |
| **GitHub Releases** | **NOT WORTH IT, and unsafe today** | ~1 h | public repo means public assets; wrong fix for the real risk |
| **GitHub Pages** | **not worth it** | ~2 h | public by construction, and strictly worse than the Space |
| **HF model hosting** | **not worth it** | n/a | there is no model to host |
| **HF Inference** | **not worth it** | n/a | there is nothing to run inference on |

**Nothing was published. No remote repository was created, no Space deployed, no Release
cut, no DOI minted.** Everything below is built, tested locally, and waiting on Josie.

---

## 2. What was verified live, and how the checks were made falsifiable

The self-audit rule for this slot was specific: testing a token by "the call succeeded"
does not distinguish a working credential from a call that never left the machine. So
every auth check below was run **with an unauthenticated control on the same endpoint**.
No credential value was printed, read, or committed; only presence and response were used.

| platform | authed result | unauthenticated control | verdict |
|---|---|---|---|
| Hugging Face | HTTP 200, `name = josiecerrell`, 0 orgs | HTTP **401** | **valid** [read] |
| GitHub | `gh api user` returns `jcerrell-IS` | HTTP **401** | **valid** [read] |
| Weights and Biases | HTTP 200, `viewer.username = jcerrell29` | HTTP **200**, `viewer = null` | **valid** [read] |

**The W&B row is the one worth keeping.** The unauthenticated GraphQL call also returned
**HTTP 200**. A status-code-only test would have passed a completely absent credential.
The discriminator is the `viewer` field being non-null, not the status code. Any future
health check that asserts `wandb == OK` from an HTTP status is measuring nothing. This is
the same failure class the discrepancy register's Class D records: a check that cannot
distinguish "working" from "could not evaluate".

**The existing session-start check was then tested against that finding, and it passes**
[read]. `.claude/hooks/orient_live.sh:99` does **not** read a status code: it greps the
response body for `"runCount"`. Running its exact query unauthenticated returns
`{"data":{"project":null}}`, which contains no `runCount`, so it correctly reports
NOT REACHABLE without a credential. **The hook is sound and needs no fix.** I had
initially recorded a doubt about it without testing; testing it took one command, and the
doubt was wrong. The general warning above stands for anything written in future.

**But eleven live worktrees never run that check at all** [read]. `orient_live.sh` exists
in **two distinct contents** across 29 copies, compared by content hash rather than mtime:

| version | lines | connector + CI block | copies |
|---|---|---|---|
| `f31356f1` | 129 | **yes**, added by `3714aec` | 11, including the main checkout |
| `9e38a7e0` | 32 | **no**: zero occurrences of `wandb`, `connector` or `CI NOT LIVE` | 18 |

The hook is tracked, so a worktree branched before `3714aec` is frozen without the block.
That is the standing worktree-frozen-at-branch-point property, not a new defect.

Live slots **without** the block: `r7-collect`, `r7-inflow`, `r7-pinned-span`,
`r8-bc-merge`, `r8-force`, `r8-kramer`, `r8-licence`, `r8-persistence`, `r8-priorart`,
`r9-accessor`, `r9-kramer-extract`. `r5-research` has no hook file at all.

**This is a silent absence, not a false OK**, which is the safer failure. But it means
eleven sessions are never told `CI NOT LIVE` at startup, which is exactly d16-landing's
subject, and it means **a slot cannot infer connector health from its own banner being
quiet**. Not fixed here: `.claude/hooks/` is outside this slot's write scope and is shared
by every worktree.

Other live reads:

- Repo `jcerrell-IS/can-it-ford` is **PUBLIC** [read].
- **Zero GitHub Releases exist**, and **no GitHub Pages site exists** (HTTP 404) [read].
- W&B project `jcerrell29-claremont-mckenna-college/can-it-ford`, **105 runs, 0 sweeps**
  [read]. Runs are already tagged `warpmpm`, so the engine distinction survives in the
  telemetry, which is better than the repo managed for a long time.
- HF account has **0 organisations** [read], so any repo lands in the personal namespace.

---

## 3. Zenodo, and why it goes first

**Verified live [read]:** a Zenodo query for `access_right:restricted` returns records
that carry DOIs, including a native Zenodo DOI (`10.5281/zenodo.14014709`) on a
restricted record.

That resolves the coordinator's first hypothesis and makes it **stronger** than it was
stated. The hypothesis was that a DOI-bearing archived dataset is the thing a paper can
cite. It is, and the important part is that **minting the DOI does not require opening
the data**. A restricted Zenodo record gives a citable, permanent identifier while access
stays controlled.

That matters here specifically, because the two things blocking publication (the
unrotated credential exposure and the unresolved asset licence) both block *openness*,
not *citability*. Zenodo separates them. Nothing else on this list does.

**Effort:** about an hour. `CITATION.cff` already exists with authors, title and
keywords, so the metadata is largely written [read].

**One blocker, and it is small but real.** `CITATION.cff` declares
`license: ODC-By-1.0` while the repository's `LICENSE` file is **BSD-3-Clause**, and
`hf_space/README.md` also declares `bsd-3-clause` [read, all three]. Code under BSD and
data under ODC-By is a perfectly normal split, so this is probably deliberate rather than
a defect, but a Zenodo record and a dataset card each demand a single answer. **Josie
should state which licence covers the data**, in one sentence, before either is created.
I have not changed any licence field.

**Do not use the Zenodo GitHub integration.** It archives a **public GitHub Release**,
which is exactly the action ruled out below. Upload the dataset directory directly
instead.

---

## 4. Weights and Biases, with a correction to the framing

The dispatch asked for "a W&B sweep view of the matrix". **A sweep is the wrong
primitive, and using one would actively damage the result.**

In W&B, a *sweep* is a hyperparameter search in which an agent chooses the parameter
combinations. The `v_car` x `v_water` matrix is **pre-registered**: d17-moving committed
the exact cells and the pass criteria before the first GPU run, specifically so the
result cannot be graded against a target chosen after seeing it [read,
`docs/R9_MOVING_VEHICLE_2026-08-19.md` section 3, commit `d3e52fd`]. Handing cell
selection to a search agent would dissolve that guarantee.

What is actually wanted is **grouped runs plus tables**: the matrix is fixed, and the
interesting axis is the repeat ensemble within each cell. That is what
`analysis/wandb_speed_surface.py` does.

The module logs, per cell, the mean, the min, the max, the range, the count, **and every
individual draw** as a second table, so a reader sees the ensemble rather than its
summary. And it refuses to compute a standard deviation below three draws, reporting a
range and a count instead. That refusal is not stylistic:

> **Measured [read]:** the only repeat draws that exist for the canonical scene today are
> **n = 2**, for three `g96` configurations. Two samples give a range, not a
> distribution.

**Verdict: worth it.** Built and tested. Dry run is the default; `--log` is required to
write anything, and an empty input refuses to create a run at all, because an empty W&B
run is a permanent artifact asserting a measurement that was never made.

**W&B Artifacts: not worth it yet.** The tables are 12 KB and git already versions them.
Artifacts earn their keep on large, frequently-revised binaries. Revisit if the large
rollout files ever need versioned distribution.

---

## 5. Hugging Face

### 5.1 Dataset, WORTH IT, built

`analysis/hf_dataset_publish.py` builds the dataset locally. Three tables and a card:

| table | rows | note |
|---|---|---|
| `canonical_runs.csv` | 17 | the gated warpmpm runs |
| `verdict_sensitivity.csv` | 17 | the SLIDE call across a threshold sweep |
| `load_surface.csv` | **0** | schema committed, data pending d17-moving |

**The card is the deliverable, not the upload.** It states the engine, the thresholds
with their units, the prescribed-not-free status of the load surface, the resolution
limitation, and the fact that no gate is a physics validation.

Two design choices worth defending:

**The empty table ships empty.** `load_surface.csv` has correct headers and zero rows.
Committing the schema before the data means d17's output cannot be graded against a
schema invented after seeing it, and it drops in without a translation layer because the
columns mirror their pre-registration exactly.

**A finding the sensitivity table surfaced by itself [read].** `sweepV_g64_v0p5` records
a peak surge drift of **0.0568 m**, which *exceeds* the 0.05 m distance threshold, yet
its published mode is **STUCK**, not SLIDE. That is the persistence count doing the work,
and it is a live demonstration that the distance threshold alone does not decide the
verdict. Six of the 17 runs change their distance-test answer somewhere in the swept
range. The card therefore states that the sweep **bounds the sensitivity from below**,
because it varies one threshold at a time and this project has already published and
retracted a claim built on a one-at-a-time sweep.

### 5.1a A PUBLIC, EMPTY DATASET ALREADY EXISTS, and it was not created by this session

Found while confirming that nothing had been published [read]:

```
josiecerrell/can-it-ford-sweep-v1
  private      : False          <- PUBLIC
  gated        : False
  files        : ['.gitattributes']   <- no data, no card, no licence
  downloads    : 22
  created      : 2026-07-14
```

**It is public, it is empty, and it has 22 downloads.** It contains a single
`.gitattributes` file: no data, no README, no licence tag. It is a name reserved on a
public index with the project's identity on it and nothing behind it.

Three consequences:

1. **It is the obvious place a future session would push**, and its name says
   `sweep-v1`. The v1 and v2 sweeps are the superseded box-proxy lineage, not the hull
   runs. Anything pushed there under that name inherits a misleading label.
2. **Publishing my dataset would create a second public repo** rather than resolving
   this one, leaving two dataset names for one project.
3. **22 downloads of an empty repository** means it is being fetched by something,
   probably indexers. Whatever pushes there first becomes what those fetches return.

**I did not touch it.** Deleting or renaming a public repository is irreversible and
outward-facing, so it is Josie's call. **The recommendation is to decide this before
creating anything new**: either reuse it with a corrected name and a real card, or delete
it. Creating a second dataset while this one sits empty and public is the worst of the
three options.

### 5.2 Space, WORTH IT, built and launched

`hf_space/` was rewritten. **It launches and serves HTTP 200 locally**, every callback
exercised, no deprecation warnings [read, run this session].

Design follows the sharpened brief: a Space that renders one surface is a picture, so
this one shows the spread and the threshold flips instead.

- **Where the verdict flips**: a slider on the distance threshold, bars turning red where
  the distance test disagrees with the published label.
- **Load surface**: the pre-registered matrix as a lattice. **Every cell currently reads
  "planned, no data".** The code will not interpolate a surface from an empty table. A
  smooth plausible surface drawn from nothing would look exactly like a result, which is
  the most damaging thing this page could do.
- **Repeat spread**: the measured n=2 ranges.
- **Limitations**: its own tab, not a footnote.

**A real result from this project's own data, found while building the spread panel
[read].** The three repeat pairs give ranges of 0.54, 0.06 and **4.51** percent on final
displacement. The widest belongs to `g96_m2337`, which is also the run register J15
records at a **one-frame verdict margin**. The run closest to flipping is the run whose
repeat draw moves the most. That is the argument for ensembles over points, made from
this project's own numbers rather than asserted.

### 5.3 Three false claims on the old Space, corrected

The handoff said two README claims were wrong. **There are three** [read, all against
canonical sources]:

1. **"Genesis MPM"** given as the L2 engine. The gated runs are **warpmpm**. This is the
   engine conflation CLAUDE.md forbids in a README by name.
2. **"rho = 115.7, giving the roughly 1390 kg target mass used across the project."**
   Neither figure is canonical. `vehicle_params.py:125` reads **1100.0** kg, and 115.7 is
   a superseded box-proxy value; the 1390 kg box traces to a sweep the project marks
   deprecated and says not to source figures from.
3. **"L2 has not produced a published verdict."** Stale. Seventeen gated runs exist with
   classified outcomes.

All three are corrected, and the corrections are **recorded on the page** rather than
quietly applied, so a returning reader can see what changed.

### 5.4 Model hosting and Inference, NOT WORTH IT

There is no model. This project produces simulation records and geometry, not trained
weights. The nearest thing to a hostable artifact is the Gaussian splat geometry, whose
licence status is part of the same unresolved asset question as §6. Effort would be
non-trivial and the output would be zero. **Do not build this.**

---

## 6. GitHub, where two of three are negatives

### 6.1 Releases, NOT WORTH IT, and unsafe today

This was the coordinator's second suspicion: that Releases plus a bundle would fix
fifteen branches existing on one disk. **The risk is real and the fix is wrong.**

`jcerrell-IS/can-it-ford` is **PUBLIC** [read]. A Release asset on a public repository is
world-readable and permanent, and this account has already served a removed blob by SHA
after a history rewrite. Cutting a Release of a full-history bundle would publish every
branch of tonight's unreviewed work, permanently, while a credential exposure is
unrotated.

I did verify the bundle hygiene properly, because it decides the recommendation:

> **[read]** `ALL-refs-MINUS-credentials-0529.bundle` excludes
> `refs/heads/claude/credential-exposure-2026-08-13-DO-NOT-PUSH`, and the exclusion is
> **object-level, not merely ref-level**: cloning it into a virgin mirror and asking for
> that commit by SHA returns absent. **Positive control:** the same query against the
> unscrubbed bundle returns present, so the test can detect presence and its negative
> means something.
>
> Incidentally the scrubbed bundle is 207,783 bytes **larger** than the unscrubbed one
> despite carrying 22 fewer refs. That is a packing artifact, not a sign the scrub
> failed, and the object-level test is what settles it. A size comparison would have been
> the wrong check.

So a safe artifact exists. It still should not go to a public Release, because scrubbing
one branch does not make fifteen branches of unreviewed work ready for permanent
publication.

**Better fixes for the actual risk, in order:** a second physical disk or an external
drive (zero exposure); a **private** HF dataset repository, which the working HF
credential already reaches; or a private GitHub repository. All three address
single-disk risk without publishing anything.

### 6.2 Pages, not worth it

Public by construction, and strictly worse than the Space for this content: it would be
static where the whole value is letting a reader move the threshold. **Skip it.**

### 6.3 Actions, worth it, but it is not mine and it has a defect

`.github/workflows/` is **d16-landing's**. I checked the board before touching anything
and found **zero rows for d16-landing and zero mentions of `github/workflows` or
`canford-checks`** [read], so it is unclaimed but unconfirmed. I edited nothing there.

**A warning to hand to whoever lands it.** A CI checkout sees the repository the way a
worktree does, so checks that count declaration sites across untracked files behave
differently there than in the main checkout, and the workflow uses `continue-on-error`,
which converts a failing check into a green tick. **Landing CI in that state produces a
check that cannot fail**, which is worse than having no CI, because it looks like
assurance. This is [recalled] from prior project findings and I have **not** re-derived
it live this session, so d16-landing should verify it before relying on it.

---

## 7. Constraint compliance

**Constraint 1, licence-unresolved assets.** Enforced in code, not by convention.
`hf_dataset_publish.py` carries an asset gate that raises on any path matching `assets/`,
`hdri`, `ambientcg`, `texture`, `renders/`, or any image, mesh, video or binary suffix.
It runs twice: once on intended filenames and once on what actually reached disk, and a
third time at the network boundary. The self-test proves it blocks the real HDRI path,
**and a positive control proves it still passes ordinary CSVs**, so a pass is not just
the gate blocking everything.

**Correction to the B6 row [read].** The register names one file. Live,
**six files are tracked on `origin/main` under `assets/`**: four `Asphalt015*` textures
(AmbientCG naming), `DaySkyHDRI002A_1K_HDR.exr`, and
`assets/hdri/kloofendal_43d_clear_puresky_2k.hdr` (Poly Haven naming). The decision Josie
is being asked for is six files wide, not one, and the two naming conventions suggest two
different upstream sources with potentially different terms. Neither has been verified
against its upstream licence and I did not attempt to; that belongs to the licence owner.

**Constraint 2, credentials.** No credential value was printed, echoed, logged or
committed anywhere. Auth was tested by response, with unauthenticated controls. Nothing
built here publishes by default: the dataset publisher requires **two** flags and prints
exactly what it would do when given only one; the W&B logger dry-runs by default; the
Space is a local directory.

---

## 8. What flips public, and what has to be true first

| item | currently | flips public when | who decides |
|---|---|---|---|
| `can-it-ford-sweep-v1` | **already PUBLIC and EMPTY** | n/a. Decide reuse or delete **before** creating anything new (§5.1a) | Josie |
| HF dataset | not created | licence question in §3 answered; card reviewed | Josie |
| HF Space | local only | dataset decision made; three corrections reviewed | Josie |
| Zenodo record | not created | licence answered. **Access can stay restricted** | Josie |
| W&B runs | project exists | already scoped to her account; no new exposure | Josie |
| GitHub Release | none | **credential rotation confirmed**, and a decision that fifteen branches are fit to publish | Josie |
| `assets/` six files | already public | B6 resolved. Note they are **already published**; a decision now changes the future, not the past | Josie |

The last row matters and it is uncomfortable: **the six asset files are already on a
public remote**. Removing them from `HEAD` would not unpublish them, for the same reason
a removed key stayed retrievable by SHA. The open decision is about what happens next,
not about containing something that is still contained.

---

## 9. The two hypotheses I was asked to test

**"A DOI-bearing archived dataset is the thing a paper can cite."** **Supported, and
strengthened** [read]. Restricted Zenodo records carry DOIs, so citability is available
without openness. This is the highest-value item on the list and the cheapest.

**"A Space is the thing a reviewer will actually click."** **Not verified, and I cannot
verify it.** It is a claim about reviewer behaviour and I have no evidence for it. What I
can say is bounded: the Space is built, it runs, it costs nothing to keep private, and
its content is defensible. Whether a reviewer clicks it is untested, and it would take a
reviewer to test. Treated as a reasonable bet, not a finding.

---

## 10. What I could not verify, stated plainly

- **HF Spaces hardware cost and private-Space limits.** [recalled], not checked live. The
  free CPU tier is assumed adequate because the app is a few CSV reads and three plots,
  but I did not confirm current pricing or private-Space quotas.
- **The CI defect in §6.3** is [recalled] from prior project findings, not re-derived
  this session.
- **The upstream licences of the six asset files.** Not investigated. Out of scope and
  owned elsewhere.
- **The physics-skeptic subagent was not run**, because I was directed not to call
  subagents. No claim here was adversarially reviewed by it; the numbers were instead
  checked by positive-control tests and by two independent code paths agreeing on the C2
  criterion. **Mark the percentages in §5.2 as unreviewed by that route.**

---

## 11. Method notes, including one I got wrong

Every self-test in the three modules carries a **positive control**, because a check that
cannot distinguish "blocked" from "could not evaluate" is worse than no check. Concretely:
the asset gate is tested both for blocking the HDRI and for *not* blocking a CSV; the
sigma withholding is tested at n=2 and n=3 in the same run so the difference proves the
mechanism; the threshold reclassifier is tested at both extremes and asserted to differ.

The pipelines were then run **end to end against synthetic populated data** in the
scratchpad, never committed, because "it handles the empty case" is not evidence it
handles data. Both paths work, and two independently written code paths agree on the C2
criterion value from the same input.

**One method failure of my own, recorded because it is the same class as the register's
Class D.** An unquoted URL containing a `?` was glob-expanded by zsh and the command
failed with "no matches found". It failed loudly, so it cost nothing, but it is the third
costume of the same zsh property the register already documents twice. Quote URLs.

---

## 12. If only one thing gets done

**Mint the Zenodo DOI as a restricted record.** It is an hour, it needs no rotation and
no licence audit beyond one sentence from Josie about which licence covers the data, and
it produces the single artifact a paper can actually cite. Everything else on this list is
either built and waiting, or a negative.

---

# PART 2, 2026-08-19 evening. Published, and one rule that would have prevented my worst mistake of the night.

## 13. READ BEFORE YOU WRITE TO A PUBLIC TARGET. One command.

**This is the most transferable thing in this document and it exists because I
broke a public page.**

Before any upload to a public target, read what is already there and diff it
against what you are about to send:

```bash
# Hugging Face, any repo type. Do this BEFORE `hf upload`.
curl -s "https://huggingface.co/api/spaces/<owner>/<name>" \
  | python3 -c "import json,sys; print([s['rfilename'] for s in json.load(sys.stdin)['siblings']])"
# then, for any filename you are about to overwrite:
curl -s "https://huggingface.co/spaces/<owner>/<name>/raw/main/<file>" -o /tmp/live_<file>
diff /tmp/live_<file> <your local file>
```

**What it would have caught.** The public Space `josiecerrell/can-it-ford` was
serving `origin/main:hf_space/app.py`, a 125-line **AR&R stationary-vehicle
verdict calculator** carrying `f6348c7` and PR #11, *"Space L1 used the Large
4WD threshold for a Yaris and dropped two of three conditions"*. That is a
**published physics fix**. My branch has a completely different application at
the same path. I uploaded mine over it and silently reverted the correction on a
public page.

**A filename collision is not a merge conflict.** Nothing warned me, because
nothing was merging. Two applications shared one name and the second one won.

The repair is in `bef6da0`: both applications now ship, the AR&R logic lives in
`hf_space/arr_verdict.py` **copied verbatim rather than re-implemented**, and the
extraction was checked byte-for-byte against `origin/main` from `AR_R` onward.
Re-implementing would have been precisely the mistake PR #11 exists to fix,
since a paraphrase of that rule was already wrong once.

**Credit where it belongs:** d16-landing found this by testing feature branches
against the integration target, wrote it on the board with the three options and
their consequences, and recommended the one I ended up taking. I had already
executed the option their plan labels *"do not choose without a deliberate
decision"* before I read their row.

### How the repair was verified, method attached

Not "verified live". Specifically:

| step | method | result |
|---|---|---|
| the fix is real, not cosmetic | recomputed the joint rule against the superseded hazard-product-alone form at the Large 4WD limit | **4 of 5 test cases flip** from FORD to NO-FORD |
| the function is not stuck on one answer | positive/negative control | 0.05 m at 0.5 m/s -> FORD; 1.20 m at 3.5 m/s -> NO-FORD |
| the extraction is faithful | string equality of the functional segment against `origin/main:hf_space/app.py` | identical |
| the app actually builds | **real gradio 6.24.0**, not a stub | `app.build()` returns a `Blocks` |
| the tab populates on load, not on tab click | read the built `demo.config['dependencies']` | 7 deps, all `(0, 'load')`, `trigger_mode once` |
| it is live on the public page | fetched `/raw/main/arr_verdict.py` from the Hub | HTTP 200, joint rule present |

The four flipping cases, for a `small_passenger` Yaris:

| D (m) | V (m/s) | D x V | joint rule | old D x V vs 0.60 |
|---|---|---|---|---|
| 0.35 | 1.00 | 0.350 | NO-FORD | FORD **wrong** |
| 0.20 | 2.00 | 0.400 | NO-FORD | FORD **wrong** |
| 0.45 | 1.20 | 0.540 | NO-FORD | FORD **wrong** |
| 0.30 | 1.50 | 0.450 | NO-FORD | FORD **wrong** |
| 0.30 | 3.00 | 0.900 | NO-FORD | NO-FORD |

## 14. What is live now, and how each was confirmed

Every one confirmed by re-reading the remote, never by a command exiting 0.

| artifact | URL | confirmation |
|---|---|---|
| dataset | `huggingface.co/datasets/josiecerrell/can-it-ford-speed-surface` | **unauthenticated** HTTP 200 listing 5 files, which also proves public visibility |
| Space | `huggingface.co/spaces/josiecerrell/can-it-ford` | 10 files, `RUNNING_BUILDING`, joint rule fetched from `/raw/main/` |
| W&B run | `wandb.ai/.../can-it-ford/runs/3w9sk50e` | API read: state `finished`, 20 cells, **100 draws**, sigma on all 20, C2 S = 1.2809 |
| placeholder | `huggingface.co/datasets/josiecerrell/can-it-ford-sweep-v1` | README present, still 22 downloads, still public |

## 15. The `can-it-ford-sweep-v1` decision, options and what I chose

The repo is public, was empty but for `.gitattributes`, created 2026-07-14, and
has **22 downloads**. Its name belongs to the **superseded box-proxy lineage**.

| option | consequence |
|---|---|
| delete it | breaks whatever is behind 22 downloads, silently. Irreversible. |
| rename it | HF leaves a redirect, but the name still reads as canonical, and it moves a public identifier Josie did not choose to move |
| populate it with hull data | attaches **correct data to a wrong name**, which is this project's signature failure: a number travelling without its scope |
| **publish elsewhere and label this one** | two public names exist, but only one is canonical and the other says so |

**Chosen: label it.** It now carries a README stating it holds no data, that
`sweep-v1` names the superseded box-proxy lineage, and where the current data
is. It explicitly says the **referent of the name is inferred from the naming
convention, not read from contents, because there are no contents** to read.
Nothing was deleted or renamed. Reversible in one commit.

## 16. A published surface is the transient one, and the settled one inverts its headline pair

Found while ingesting d17-moving's data, and **it is not mine to close**.

d17's R5 publishes a 20-cell surface measured over frames 20-60. The same 20
cells at frames 250-400 are in the same shipped table, as `L2full` (one seed)
and `M1s0..M1s4` (five seeds). `/usr/bin/grep` for `L2full`, `5028`, `5534`,
`9577` and `30211` in their document returns **zero**.

R5 states as *"the contribution stated as a number"* that (v_car 2.20, v_water
3.00) at |v_rel| 3.720 carries 2.3x the load of (v_car 4.50, v_water 0.50) at
|v_rel| 4.528.

| window | lower-|v_rel| cell | higher-|v_rel| cell | ratio | seeds |
|---|---|---|---|---|
| transient f20-60 (**published**) | 8621.4 N | 3811.1 N | **2.262** | 1 |
| settled f250-400 | 5176.5 +/- 4.0 N | 5675.3 +/- 13.0 N | **0.912** | 5 |

The ratio crosses 1, so the direction of that specific comparison reverses.
Per-cell seed spread is 0.066 to 0.338 percent, so it is not noise.

**The general claim survives and strengthens.** S = (max-min)/mean across an
iso-|v_rel| arc is 0.76, 0.97, 1.07, 1.12, 1.28 at |v_rel| 1.0, 2.0, 3.0, 4.5,
6.0 m/s. The split matters at every magnitude measured, and the effect **grows
with speed**. Only the specific pair fails.

Same hull, grid and depth in both windows: `fz_settle_N` 9149.19 and
`f_buoy_analytic_N` 4468.622 in both, and those DO discriminate elsewhere in the
same file (fidC 9966/2529.5, fidF 14512/2476.0, g96 7494). The one confound I
could **not** close: `hull_y_m` is empty in `c3full`, which I read as *not
recorded* rather than as a different placement.

**Reviewed by nobody.** The `physics-skeptic` subagent was unavailable this
session: three launches, all terminated on the same model API error, including
one with an explicit model override. These numbers are self-verified and
**unreviewed**, and I am saying so rather than substituting a review that did
not happen.

## 17. Connector and capability audit, tested not assumed

Only what I actually exercised this session appears with a verdict. The rest is
listed as untested, because an untested connector reported as working is the
same defect this document is about.

| capability | verdict | evidence | effort to use |
|---|---|---|---|
| **`hf` CLI + Hub API** | **WORTH IT** | created a dataset, uploaded 3 repos, verified each by re-reading | minutes; already authenticated, write scope |
| **Weights and Biases** | **WORTH IT, and the gap is now filled** | run `3w9sk50e`, 20 cells x 5 seeds = 100 draws logged as a distribution table | ~20 min; the script existed, only its column names were stale |
| **Scholar Sidekick** | **WORTH IT, and it earned its keep immediately** | `checkRetraction` on the Nihei DOI returned the correct title and surfaced an **erratum** I would otherwise have cited past | seconds per citation, works anonymously |
| **DeepWiki** | **WORTH IT as a hypothesis generator** | answered a `gr.Blocks`/`gr.Tab` load-event question; I then **verified it against the built config** rather than trusting it | seconds, but always budget the verification |
| **HF Spaces** | **WORTH IT** | Space builds and serves two applications | ~1 h including the mistake and its repair |
| **`physics-skeptic` subagent** | **UNAVAILABLE THIS SESSION** | 3 launches, all failed on the same model API error; a `model:` override did not displace it | blocked, not a cost question |
| **Zenodo DOI** | **WORTH IT, still the cheapest high-value item** | verified earlier: Zenodo mints a DOI for a **restricted** record, so citability does not require publishing | ~1 h, not yet done |
| GitHub Releases | **NOT WORTH IT yet** | a Release is a public publication and the credential exposure is unrotated; d16-landing owns bundles | n/a |
| GitHub Pages | **NOT WORTH IT** | the Space already does the interactive job, better | n/a |
| HF model hosting / Inference | **NOT WORTH IT** | there is no model; this is a simulation dataset | n/a |
| Zotero, Undermind, Scite, Wolfram, Consensus, Elicit | **UNTESTED this session** | not exercised, so no verdict claimed | unknown |

## 18. SIX instruments that reported without evaluating, in one round, and now one is the CI

This is the pattern worth carrying past tonight. In every case the instrument
produced output that **looked like a result** and could not have produced any
other answer.

| # | slot | the instrument | why it could not fail |
|---|---|---|---|
| 1 | **d18 (mine)** | connector health table | `c=$(grep -c ... \|\| echo 0)` made `c` the two-line string `"0\n0"`; `[ "0\n0" -gt 0 ]` **errors**, the `if` fell to `else`, and every "NO" was printed by a failed comparison rather than a test. **Correct by luck**; reversed branch order would have printed the opposite conclusion with equal confidence. |
| 2 | **d15-settle** | `asymmetry()` | **printed** "a verdict is only ever DELETED, never created" as narration while the code counted only whether a verdict *moved*. No input could have contradicted the sentence. Measuring it properly gave 30 deleted, 0 created. |
| 3 | **d12-kramerdata** | `--uncertainty` mode | a loop variable `c` shadowed the parameter `c`, so it crashed **after** printing the header. The author had already declared the mode working from a `sed -n '20,36p'` read that stopped before the crash. |
| 4 | **d18 (mine, tonight)** | `iso_vrel_criterion` | searched for cell ids `A0..A4` from a placeholder schema that the real data does not use. It printed "C2 NOT COMPUTABLE" **every time, forever**, while reading as a criterion under evaluation. Now reads the real families and returns a verdict. |
| 5 | **d18 (mine, tonight)** | `read_surface` / `surface.py` Panel 2 | returned `[]` for a missing file, which downstream is indistinguishable from present-but-empty **and** from a schema mismatch. Panel 2 would have reported "not computable" forever without ever saying it could not read the file. |
| 6 | **THE CI ITSELF** | `canford-checks` | see below |

### 18a. The CI is instance six, and it is the worst kind

Measured live, two independent origins:

- d16-landing read the **CI log**: the job is green, and inside it `count_claims`
  emits **25 BLOCK lines** and `##[error]Process completed with exit code 1`.
- I ran the checker **locally in this worktree**: 25 BLOCK lines, and the
  script's **true exit code is 1**. It fails correctly.

So the checker is not broken. The masking is at
`.github/workflows/canford-checks.yml:25`, `continue-on-error: true`, commented
*"accepts 22/23/24 by scope, see CLAUDE.md item 13"*.

**And that comment's rationale no longer describes what happens.** In a
tracked-only checkout the checker computes defensible totals of **16 and 17**,
not 22/23/24, because `_inbox/` and `data/` are physically absent from a
worktree or a fresh CI clone, so declaration sites are undercounted. The
tolerance the comment claims is being applied is not the tolerance in play.

**This changes the recommendation.** Making the CI *execute* was never the gap;
it runs and reports success. Making it **able to fail** is the gap. A workflow
that never ran gives no assurance. A workflow that runs, swallows a failing
check, and reports green gives **false** assurance, which is worse.

Two fixes, and they are not the same:
1. Remove `continue-on-error` from `count_claims` **only after** the
   tracked-only undercount is fixed, or every CI run goes red for a reason that
   is not a real defect.
2. Fix the undercount first: the checker needs to state the **scope it actually
   measured**, so a 16/17 result in a partial view is reported as *"could not
   see `_inbox/` and `data/`"* rather than as a defensible total.

That second fix is the same rule as everything else in this section: **an
instrument must distinguish "measured" from "could not measure".**

`.github/workflows/` belongs to d16-landing this round, so this is written as a
finding and not acted on.

### 18b. And once more in my own hands, tonight, while writing this

Checking the CI claim, I ran the checker through `tail` and read `$?`, which is
**`tail`'s** exit code, not the script's. It printed `rc=0` next to the words
"blocking defects 25". I nearly wrote that the checker exits 0. Re-measured with
the pipeline removed, the true code is 1.

Three separate defences caught things tonight, and they generalise:
- **a positive control**: a check that never returns the other answer is not a check
- **a negative control**: an empty selection must raise, not return `[]`
- **compare at the level you claim**: my first CRLF/LF comparison normalised away
  the exact thing that differed and printed "no columns differ". `cmp` found it
  at byte 513.
