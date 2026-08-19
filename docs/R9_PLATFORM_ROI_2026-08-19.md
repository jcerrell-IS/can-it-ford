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

**The highest-value item on this list is not on the Hub.** It is making the CI
able to fail. Everything below it is an artifact; that one is the thing that
decides whether any future artifact can be trusted.

| capability | verdict | evidence | effort to use |
|---|---|---|---|
| **CI: make `canford-checks` ABLE TO FAIL** | **HIGHEST VALUE, above anything on the Hub** | green at job level for two days while `count_claims` emits 25 BLOCK lines and exits 1 inside it; masked at `canford-checks.yml:25` | ~2 h, and it is two steps in order, see 18a |
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

---

# PART 3, 19:0x. C-1 closed upstream, and a relay I was given was one commit stale.

## 19. THE RULE, in liftable form

For CLAUDE.md, if a slot owns that file. Four lines:

> **Read before you write to a public target.** Before any upload that can
> overwrite a remote file, fetch the remote's current file list and the current
> contents of every path you are about to write, and diff them. A filename
> collision is not a merge conflict: nothing is merging, so nothing warns you.
> The standing "read the board before each commit" rule does not cover this,
> because **a publish is not a commit.**

Applied to this dataset before the most recent upload: fetched the remote
`siblings` list and the live `README.md`, diffed it, confirmed 62 changed lines
and that every file was authored by me in this session with no third-party
content at risk, and only then uploaded.

## 20. C-1 is closed, and the closure I was handed was superseded before I read it

I was told d17-moving's `050ff22` closed C-1 by stating the pair "belongs to the
late window and is **2.24x**, and does not invert", and that both computations
were right with only a missing window label between them.

**That is not what closed it, and it is not the outcome.** Read live:

- `050ff22` computes **a different pair**: pure broadside against the -22.5 deg
  split at fixed |v_rel| 3.0. That is an *arc* comparison. Mine is two *surface*
  cells with **different** |v_rel|, 3.720 and 4.528. That commit says in its own
  body *"I COULD NOT REPRODUCE AN INVERSION... If d18's inversion came from a
  different window, depth or pair, name it."*
- **`51c158b`** is the commit that closes C-1, and it reverses the relayed
  conclusion: *"BOTH ARE CORRECT. They are different windows of the same
  experiment, and the 2.3x is the transient one."* d17 states plainly that their
  own T16 *"answered a DIFFERENT pair and did not close this. That was my
  misreading."*

**The outcome is not "both right, label missing". The 2.3x is WITHDRAWN**, marked
in place at the R5 table so the error stays visible.

I reproduced d17's resolution table independently from the shipped data, and it
agrees to four digits:

| arm | grid | frames/discard | seeds | (2.2, 3.0) | (4.5, 0.5) | ratio |
|---|---|---|---|---|---|---|
| `c3full` | g64 | 60/20 | 1 | 8621.4 N | 3811.1 N | **2.2622** |
| `L2full` | g64 | 400/250 | 1 | 5028.4 N | 5534.7 N | **0.9085** |
| `M1s*` | g64 | 400/250 | 5 | 5176.5 N | 5675.3 N | **0.9121** |
| `M2s*` | g96 | 400/250 | 2 | 5315.9 N | 6246.4 N | **0.8510** |

So the inversion survives a change of seed, of BC rate, and of grid.

**My open confound is also closed, by d17 and correctly.** `hull_y_m` is empty
in exactly twelve arms and all twelve are from their first session; every arm
run since records it *and* records the same value. A recording gap, not a
placement difference. I had labelled it "not recorded rather than a different
placement" and that reading held.

**And d17 is right about something I understated.** The pair was always the
weakest way to state the result, because the two cells differ in *both*
variables **and** in |v_rel|. The iso-|v_rel| arcs hold relative speed exactly
fixed and vary only the split, and that is where the finding actually lives.
The dataset card now leads the arcs and demotes the pair accordingly.

### 20a. Why this belongs in a document about instruments

The relay I was given was accurate about a commit and wrong about the outcome,
because a newer commit on the same branch reversed it. Checking cost one
`git log`. **A claim about a repository's state has a cheap live check, and a
relayed one is stale the moment someone else commits.** That is the same class
as everything in section 18: the difference between a report and a measurement.

## 21. The dataset is PROVISIONAL and deliberately not frozen

Batch `922514 r9_speed_surface` is running and `922515 ciford_dtrefine` is queued
behind it, so the ensembles will grow, including on g128. The card now carries a
**Status: PROVISIONAL** block at the top saying exactly that: the numbers are
measured rather than estimated, but a later version with larger ensembles is the
better one. Freezing it now would have published single-draw language for a
result whose entire argument is that it has distributions.

The reproducibility record now carries **every field the 105-paper search named
as missing from the literature in one place**, and the particle counts, `dx` and
depth-in-cells are measured from the shipped table rather than transcribed:

| | n_grid 64 | n_grid 96 |
|---|---|---|
| water particles | 41,636 to 41,674 | 164,351 to 164,382 |
| cell size `dx` | 0.147215 m | 0.098143 m |
| depth in cells | 2.038 | 3.057 |
| wall clock per simulated second | 0.417 s/s | 2.213 s/s |
| GPU memory | about 630 MiB | (g128 about 3 GB) |

GPU: NVIDIA GH200 120GB, driver 590.48.01, **one card, single GPU**, partition
`gh`. **Peak observed GPU memory across the whole session was 4,069 MiB of
97,871 MiB**, so memory was never the binding constraint, which is more useful
to state than to imply a limit was approached.

---

# PART 4. The tooling and coordination ROI, sourced, and one hazard I measured rather than argued

Source: `~/Downloads/Claude Code for Multi-Pane HPC Simulation Workflows_
Effectiveness, Guardrails, and Coordination Analysis.md`, 134 lines, dated
2026-07-24. **Read live this session**, and all five findings relayed to me
reproduce in it at the lines cited below. This relay checked out, unlike the C-1
one in section 20, which is why both are recorded.

## 22. THE HEADLINE IS NOT ON THE HUB. IT IS THAT CI CANNOT FAIL.

Restated at the top of this part because it outranks every artifact in this
document. `canford-checks` has been **green at job level for two days** while,
inside it, `count_claims` emits **25 BLOCK lines** and exits **1**. Masked by
`continue-on-error: true` at `canford-checks.yml:25`.

**The recommendation is not "make CI run". It runs. It is "make CI able to
fail".** A workflow that never ran supplies no assurance; one that runs and
swallows a failing check supplies **false** assurance, which is worse, and it
has been doing so in production. Sixth instance of this round's dominant defect
and the only one shipping. Ordered fix in section 18a. Owner: d16-landing.

## 23. The five findings, measured against what we actually do

| # | the document says | our measured state | verdict |
|---|---|---|---|
| 1 | ceiling of **~3-5 concurrent agents on a shared codebase** (:16, :110) | 35 worktrees, **33 distinct branches** | **already mitigated, do not cap tonight** |
| 2 | replace a single shared handoff with **append-only, one-file-per-session plus an INDEX** (:107) | one shared board, append-only by policy, **untracked**; 148 of 232 rows exceed the safe append size | **CHEAPEST REAL FIX, do tonight** |
| 3 | destructive-command protection **in hooks, not prose** (:11) | hooks exist and fired 8+ times on my writes tonight | **principle already implemented; the gap is hooks that cannot fail** |
| 4 | **lean CLAUDE.md under 200 lines** (:11, :26, :93) | **939 lines**, and it grew 33 during this session | **worth doing, NOT tonight** |
| 5 | two HPC Claude Code bugs: `XDG_RUNTIME_DIR` on compute nodes (#21026), `claude -p` when interactive exits (#12507) (:87, :119) | absent from every dispatch and from CLAUDE.md | **worth adding, cheap, not my file** |

### 23.1 On the writer cap, the document is being quoted slightly against itself

Its ceiling is explicitly for agents **"on the same shared codebase"**, and the
mitigation it names in the very next breath is the one we already run: *"put
every write-heavy pane in its own git worktree/branch"* (:112). It also says the
twelve-session figure is *"more defensible than typical because they are
heterogeneous"* (:110), which ours are: paper, licence, solver, renders, corpus,
platform, landing.

**So capping writers is the wrong lever.** But the document is right about the
cost, and **the cost is being paid tonight**: it says the binding constraint
becomes *"the human ... merge/review bottleneck"*, and d16-landing found **five
conflicting files across four merges**, one of which silently reverted a
published physics fix on a public page. That is the predicted failure, realised,
in the same round. The lever is to fund the review side, not to reduce the panes.

### 23.2 The board hazard, measured, with a threshold and a control

The document's concern is last-writer-wins on whole-file rewrites. **Ours is a
different and sharper mechanism, and I measured it rather than asserting it.**

Eight concurrent shell processes appending one line each to a shared file,
exactly the board's pattern:

| row bytes | lines written | corrupted |
|---|---|---|
| 200 | 200 | **0** |
| 500 | 200 | **0** |
| 1000 | 200 | **0** |
| 1023 | 200 | **0** |
| 1500 | 200 | 30 |
| 2000 | 200 | 23 |
| 4000 | 200 | 83 |

The mechanism is visible in the wreckage: writes chunk at **exactly 1024 bytes**
and interleave at that boundary. One corrupted line read
`C x 1024, A x 1024, C x 976` — writer A's row spliced into the middle of
writer C's. **The line count stays correct**, so a row count is not a detector.

Against the live board: **232 rows, 148 of them (64 percent) are at or above
1024 bytes**, median 1284, max 5252. My own rows are among the worst offenders.

**No damage has occurred yet.** A splice detector (any row carrying more than
one `| YYYY-MM-DD HH:MM |` header) returns **zero**, and the 35 non-pipe lines
are the file's preamble, not fragments. So this is a **latent** hazard: the
pattern is unsafe at the sizes we use, and we have been lucky or sufficiently
staggered.

Two fixes, and the cheap one needs no infrastructure:

1. **Tonight, zero cost: keep every board row under 1023 bytes.** Measured safe
   at every length tested up to that. Long findings go in a committed document
   and the row cites the path and SHA, which is what a row is supposed to do.
   **I am adopting this for my own rows from here on.**
2. **Next round: one file per session plus an INDEX**, as the document
   recommends, which is conflict-free by construction rather than by discipline.

One more thing the document does not raise: **the board is untracked**. So a
spliced row is unrecoverable, has no history, and is invisible to review or CI.
That is a second reason the long-row pattern is worse here than the document's
own framing implies.

### 23.3 Why the CLAUDE.md diet is right and still not tonight

939 lines against a recommended 200 is a 4.7x overrun, and it grew during this
session. But it is the **highest-risk edit in the repo**: every slot reads it,
its content is quoted verbatim by people outside the repo, and it already
carries a standing rule against positional citation *because it changes several
times a night*. Cutting it 939 -> 200 while eleven sessions are live would
invalidate citations mid-flight, including citations in work being merged
tonight.

**Next round, one owner, and by moving content into referenced files rather than
deleting it.** The facts in it are load-bearing; its length is the problem, not
its content.

## 24. What is actually mine to fix, stated plainly

Of the five, **none of the fixes sits in this slot's write scope**:
`.github/workflows/` is d16-landing's, `CLAUDE.md` and `.claude/hooks/` are
shared and unowned this round, and the board's format is a fleet convention.

What I can do and have done: measure them, give each a threshold and a control
so the next session argues with a number instead of an opinion, and adopt the
one rule that needs no permission, the sub-1024-byte board row.

---

# PART 5. The coordination layer, its failure mechanism, a detector, and the migration

## 25. The mechanism, stated plainly

A shell append (`printf ... >> file`) is atomic only up to a **1024-byte** write
chunk. Above that the kernel splits the write, and a second process appending at
the same moment can land its own chunk **between** the two halves of the first.

Measured, eight concurrent writers, 25 rows each, the board's exact pattern:

| row bytes | lines written | corrupted |
|---|---|---|
| 200 | 200 | **0** |
| 500 | 200 | **0** |
| 1000 | 200 | **0** |
| 1023 | 200 | **0** |
| 1500 | 200 | 30 |
| 2000 | 200 | 23 |
| 4000 | 200 | 83 |

The boundary is sharp and it is exactly 1024. One corrupted line read
`C x 1024, A x 1024, C x 976`.

### 25.1 ROW COUNT IS NOT A DETECTOR, and that is the whole problem

**200 lines went in and 200 lines came out.** The corruption does not change how
many lines exist; it changes what is *inside* them. So every check a person
would naturally run on an append-only log, *"did my row land"*, *"how many rows
are there"*, *"is the file growing"*, **passes on a corrupted file**.

That is what makes this an instrument failure rather than a bug. The artifact
eleven sessions were told to trust for cross-session coordination has a failure
mode that its obvious integrity check cannot see.

### 25.2 Two denominators, both correct, so state which

An earlier figure in this document said 64 percent of rows exceed 1024 bytes.
The checker reports 76 percent. Both are right and they divide by different
things: 64 percent is oversize lines over **all non-blank lines** (which
includes the preamble), 76 percent is oversize rows over **headered rows only**.
The second is the meaningful one, because only a row is written by an appender.
Live at time of writing: **153 of 201 rows, median 1460 bytes, max 5252.**

## 26. The migration, and why it is the fix rather than a mitigation

The corpus document recommends **append-only, one-file-per-session handoffs plus
an INDEX** in place of one shared file. The measurement above is the local
evidence for why that is the right shape and not merely a tidier one:

> **A per-session file has exactly one writer. With one writer there is no
> second process to interleave with, so the failure cannot occur at any row
> size.** The shared file makes correctness depend on every session's discipline
> about row length; per-session files make it structural.

That is a stronger guarantee than the sub-1024-byte rule, which only shrinks the
window. Recommended shape, matching the document:

```
.claude/handoffs/2026-08-19_d18-platform.md     one writer, any row size
.claude/handoffs/INDEX.md                        one short line per handoff
```

The INDEX still has many writers, so **the sub-1024-byte rule still applies
there** and it is easy to honour, because an index line is a path plus a
one-clause summary.

**Interim rule, in force now and costing nothing: keep every board row under
1023 bytes.** Measured safe at every length tested up to that. Long findings go
in a committed document; the row cites the path and the SHA, which is what a row
was always supposed to do.

**Do not rewrite the existing board to fix anything.** It is append-only by
design, and a rewrite is the single operation that would destroy another
session's rows. If a splice is found, append a correction row naming the damaged
line numbers.

## 27. The detector, and the input that makes it fail

`.claude/checks/board_splice_check.py`. Per the falsifier rule added at
`e81bc9c` (*"any commit adding a check must name the input that makes it fail; a
check with no such input cannot fail and is not a check"*), every detector in it
is exercised by an input that makes it fire, and the negative controls prove it
can also stay quiet.

| test | the named input | expected |
|---|---|---|
| T1 | one row's text inserted into the middle of another, so the line carries **two** `\| date time \|` headers | **fires** |
| T2 | two clean, separate rows | silent |
| T3 | a 900-byte line with no header and no leading pipe, i.e. a displaced tail | **fires** |
| T4 | short preamble prose | silent |
| T5 | a row padded past 1024 bytes / a 75-byte row | counted / not counted |
| T6 | **a 1024-byte MIDDLE chunk spliced in, carrying no header** | **NOT detected, by design** |
| T7 | a nonexistent board path | raises, exit 2 |

### 27.1 T6 is the honest part

A splice only carries a header if the interleaved chunk happens to be the
**start** of another row. If it is a middle chunk, byte 1024 onward, it has no
header, the merged line has exactly one header and a leading pipe, and it looks
well formed. **This check cannot see that**, and T6 demonstrates it with a
concrete input rather than describing it in a comment.

So a PASS means *"no splice of the catchable kinds"*, never *"the board is
intact"*. The check prints that sentence on every pass. The oversize-row count
is the only warning that covers the invisible case, which is why it is reported
on every run.

### 27.2 Why oversize rows do not fail the check

76 percent of rows already exceed the boundary. A check that exits non-zero from
birth gets wrapped in `continue-on-error` and stops meaning anything, and this
round has the receipts: that is precisely what happened to `count_claims`.
**Splices fail. Oversize rows are counted and reported.** The check is built to
be able to pass, so that its failing means something.

Live run at time of writing: 240 lines, 201 rows, **0 splices, 0 orphans**, 153
oversize. The hazard is latent, not realised.

## 28. A correction to my own earlier finding, from register `e81bc9c`

Earlier in this round I reported that eleven live worktrees never see the
connector and CI block at session start, and I framed it as a gap.

**The banner those worktrees were missing was itself wrong.** `e81bc9c` records
that `orient_live.sh` printed *"CI NOT LIVE ... so it runs nowhere"* to every
session, while `canford-checks` had in fact run **seven times**, because its
trigger is a bare `on: push:` with no branch filter. *Absent from main* and
*runs nowhere* are different claims and only the first was true.

So the eleven worktrees were **better off** without that line, and my finding
was correct about the mechanism (a tracked hook is frozen at a branch point) and
wrong about the direction of the harm. The measurement stands; the framing does
not, and it is corrected here rather than quietly dropped.

---

# PART 6. The Hub audit, re-measured. "Six public empty shells" is refuted.

## 29. `usedStorage` is LFS-only accounting, not repository content

The audit I was handed reported ten repositories with eight at **0 B**, and
concluded that six public empty shells carry this project's name. **The size
field it used counts LFS-backed storage only.** Files stored in git, which is
every small text and CSV file, report zero while being fully present.

Proved by download, not by argument:

```
GET .../datasets/josiecerrell/can-it-ford-speed-surface/resolve/main/load_surface.csv
  http=200   208,366 bytes   368 data rows
```

That is the repository the audit called empty, and the file it called 0 B is
203 KB of the surface this project believes is the field's open gap.

## 30. Every repository, re-measured by counting files that are not `.gitattributes`

`.gitattributes` is created automatically by the Hub, so a repo holding only
that file is the real definition of empty. Measured live, private ones with
authentication:

| repo | type | vis | real files | actually empty? |
|---|---|---|---|---|
| `hicss-splat-bucket` | bucket | public | 588 MB | no |
| `can-it-ford-page` | space | **private** | **275** | no, a full project page, 50 MB LFS |
| `can-it-ford-sweep-v1` | **model** | public | **37** | **no, and this is the finding** |
| `can-it-ford-sweep-v1` | dataset | public | 1 | no, my placeholder README |
| `can-it-ford` | space | public | 10 | no, the live Space |
| `can-it-ford-speed-surface` | dataset | public | 5 | no, the live dataset |
| `can-it-ford-demo` | space | public | 2 | no, README + `phase_space_results.csv` |
| `can-it-ford-lab` | space | **private** | 7 | no, a Dockerfile app with a login page |
| `can-it-ford-results` | dataset | **private** | **0** | **YES** |
| `can-it-ford-scratch` | bucket | public | **0** | **YES** |

**Two of ten are empty, not eight. One of those two is public, not six.**

## 31. The real finding is the opposite of the one reported

The audit reasoned that the same name existing as both a dataset and a model,
both empty, suggested a creation step that ran twice and a population step that
never ran. **It is the other way round.** The *model* repo is the populated one,
and it is populated with something that needs a decision:

`josiecerrell/can-it-ford-sweep-v1`, **model type, PUBLIC**, 36 runs plus a
manifest:

- 3 vehicle classes: sedan 4.6 m / 1240 kg, suv 4.8 m / 2020 kg, pickup 5.5 m / 1930 kg
- 4 depths x 3 velocities x 3 classes = 36 runs, all `n_grid` 64
- **`density_plausible` is `False` on all 36 rows**, by the pipeline's own check
- densities 336.61, 482.61, 306.51 kg/m^3, none of them the canonical Yaris 310.494
- **no README at all** (`raw/main/README.md` returns 404)
- typed as a **model**, which is the wrong type for a tabular sweep

**Provenance established, and it IS reproducible.** The published `manifest.csv`
is byte-identical to `data/track1_sweep_v1/manifest.csv` after newline
normalisation (published is CRLF, committed is LF, exactly 37 bytes across 37
lines, the same trap as the speed-surface source this morning), and
`data/track1_sweep_v1/` **is tracked on `origin/main`**. So this is committed,
re-derivable data, not an orphan.

**But `track1_sweep_v1` is the box-proxy lineage**, the one CLAUDE.md marks
deprecated and instructs not to cite for a density or a paper figure. So a public
repository under this project's name serves the superseded lineage, with every
row self-flagged implausible, and no README to say any of that.

That is strictly worse than an empty repository, and it is the exact hazard I
wrote the `sweep-v1` dataset README about this afternoon, **while the actual
data was sitting one repo-type away and I did not look.** My placeholder README
says "this repository holds no data", which is true of the *dataset* repo and
misleading now that I know a same-named *model* repo serves 36 runs.

## 32. Recommendation for each, and I have acted on NONE of them

Deleting a public repository and emptying one are different irreversible acts,
and neither is mine. **No repository was created, deleted, emptied or modified in
this part.**

| repo | recommendation | why |
|---|---|---|
| `can-it-ford-sweep-v1` **(model)** | **FILL, highest priority: add a README.** Do not delete | 36 real runs, publicly readable, zero scope attached. The README must say: box-proxy `track1_sweep_v1` lineage, superseded, `density_plausible=False` on every row, not the canonical Yaris, and where the current data is. Artifact exists and is committed: `data/track1_sweep_v1/`, tracked on `origin/main`. Retyping it as a dataset would change its URL and is a second decision |
| `can-it-ford-sweep-v1` (dataset) | **AMEND my README** | it says "holds no data" without mentioning that a same-named model repo does. That is now the misleading half |
| `can-it-ford-results` (dataset, private) | **DELETE, or fill** | genuinely empty, private, so it costs nothing and misleads nobody. Deleting is tidy; leaving it is harmless. **Do not fill it** until there is an artifact: tonight's provenance audit found two headline results whose data lives only on Vista |
| `can-it-ford-scratch` (bucket, public) | **DELETE or make private** | genuinely empty and public. The only true "public empty shell" of the ten |
| `can-it-ford-speed-surface` | **keep, already filled** | 5 files, 368 records, provisional card |
| `can-it-ford` (space) | **keep, already filled** | 10 files, running, two applications |
| `can-it-ford-demo` (space) | **inspect before deciding** | 2 real files; `phase_space_results.csv` may be the superseded bare-hazard rule. Not mine |
| `can-it-ford-page` (private) | **keep private** | 275 files, a real project page. Not mine |
| `can-it-ford-lab` (private) | **keep private** | 7 files, a Dockerfile app with a login page. Not mine |
| `hicss-splat-bucket` | **out of scope** | not can-it-ford named, 588 MB |

**Nothing above should be filled with a number that cannot be re-derived.** The
only fill I recommend is a README, which is prose about data that is already
committed.

## 33. Weights and Biases: what it logs, and the one thing to add

**What it logs now.** `wandb` appears in ten tracked Python files, and across
them there are six `wandb.init`, six `wandb.log` and two `wandb.summary` calls.
The metric keys actually written are seven scalars: `depth_m`, `velocity_ms`,
`dv_product`, `l1_haz_score`, `l1_verdict`, `l2_verdict`, `verdict`. So the 105
runs are a **verdict ledger**: two inputs, one hazard product, three verdict
labels, one row per run. There are no forces, no time series, no retained
window, no seed, no grid, and no thresholds. My run `3w9sk50e` added the first
distribution tables (20 cells x 5 seeds = 100 draws), and it is the only run
carrying an ensemble.

**The single highest-leverage addition: log the deciding thresholds, and the
retained window, as `config` on every run.** A verdict is already logged; the
four literals that decide it (`slide_m`, `slide_speed_ms`, `float_m`,
`sustain_frames`) are not, and neither is the frame window a load was averaged
over. Those are precisely the two "number without its scope" failures this
project keeps paying for: 16 SLIDE / 1 STUCK is threshold-dependent and must
never be quoted bare, and tonight a published 2.3x was withdrawn because it was
a transient window that had not been labelled. Both are cheap, four floats and
two integers, and `config` is queryable, so a threshold change becomes a visible
diff across runs instead of an untracked edit, and any verdict count becomes
re-derivable by filtering rather than by trusting a summary.
