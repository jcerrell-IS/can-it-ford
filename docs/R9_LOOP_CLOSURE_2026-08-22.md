# R9 LOOP CLOSURE, 2026-08-22

Closing the loop on the R9 sprint: thirteen parallel Claude Code sessions that ran on
2026-08-19 and 2026-08-20, whose outputs nobody had confirmed were read, merged or acted on.

**METHOD, so the scope of every claim below is auditable.** The branch set was taken from
`git worktree list` and `git branch -a`, not from the list in the request. Every one of the
thirteen branches' full commit bodies was read (`git log --format='%H%n%B' --name-only`),
187 distinct commits over 140 distinct files. Board coverage was measured against
`.claude/state/r8_board.md`. Merge state, `origin/main`, `overleaf/main`, poster blobs and
licence files were read live from git at the times stamped below. Claims are tagged
**[read]** where I read the source directly, **[relay]** where a commit is the only witness
and I could not reach the primary, and **[infer]** where I reasoned rather than measured.

**LIVE-STATE WARNING, and it moved twice while this was being written.** A concurrent session
merged **nine** of the thirteen branches at 2026-08-22 01:30:01 to 01:30:03, seven minutes
after this session started, and a **tenth** (`claude/r9-jobb-route`) at 01:38:26 while Part 3
was being drafted. Every merge figure below carries the time it was measured and the final
sweep is **01:39:06**. Re-derive before acting; on this repository a count is a timestamped
observation and not a fact, which is d16-landing's rule B5 applying to this document too.

**THE SLOT-TO-BRANCH MAP** (from `scripts/r8/r8_plan.tsv`, read live). The request named
twelve branches; **thirteen exist**. `claude/r9-overleaf` (slot d23-overleaf) was not in the
list and is the one branch whose work reached a shipped deliverable.

| slot | branch |
|---|---|
| d11-accessor | `claude/r9-accessor` |
| d12-kramerdata | `claude/r9-kramer-extract` |
| d13-renders | `claude/r9-renders` |
| d14-corpusbib | `claude/r9-corpus-bib` |
| d15-settle | `claude/r9-settle` |
| d16-landing | `claude/r9-landing` |
| d17-moving | `claude/r9-moving-vehicle` |
| d18-platform | `claude/r9-platform` |
| d19-priorcode | `claude/r9-priorcode` |
| d20-reader | `claude/r9-reader` |
| d21-jobb | `claude/r9-jobb-route` |
| d22-gapscan | `claude/r9-gapscan` |
| d23-overleaf | `claude/r9-overleaf` |

---

## PART 1. UNRESPONDED-TO DECISIONS ADDRESSED TO JOSIE

These are the actual unanswered prompts. Each was written by a session as something it
deliberately did not do because the call was not its to make. None of the ten in section 1.1
has a response in any commit, board row or file I could find.

### 1.1 STILL OPEN

**J1. Whether to contact the Kramer et al. authors about a data defect.**
`claude/r9-kramer-extract`, commit `46929a1`, 2026-08-19 19:06. Verbatim: *"Whether to contact
at all is Josie's decision."* The finding behind it: RANS4 and RANS5 ship gauges in **reversed
radial order**, 3 of 3 series each, while RANS2 (0/3) and RANS3 (0/1) are as declared. The
property is per **code**, not per file, so the other nine series are usable as shipped. Two
draft sentences for a contact, one defensible and one not, are already written into
`docs/R9_KRAMER_FULL_EXTRACT_2026-08-18.md`. The ordering test uses no radii, so it does not
depend on the hand transcription that is the weakest provenance in that document. **[read]**

**J2. Credential rotation, which gates every push.**
`claude/r9-landing`, `docs/R9_LANDING_PLAN_2026-08-18.md` section 5.1, read live today. It
quotes `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`: *"Status: OPEN. Rotation is a Josie action
and has not been done."* The GitHub PAT is the one that matters, because that is the
credential a push authenticates with. Consequence measured live on 2026-08-22:
`claude/add-ci-checks` was **391 commits ahead of `origin/main` and 0 behind** at 01:34 and
**413 ahead** at 01:39, and no `r9-*` branch exists on the remote at all. That 22-commit move
in five minutes is the ahead half doing exactly what rule B5 says it does.
Section 7 of the same plan records that bundling is a treadmill
(a bundle verified complete at 00:14 was stale on 9 branches 40 minutes later) and that *"the
fix is a remote and the remote is blocked on 5.1, which is Josie's."* **[read]**

**J3. The poster on `origin/main` carries two false statements.**
Landing plan section 5.3, sourced to d8-naming's board row.
`public_release/Cerrell_TACC_42x56.pdf`, blob `168879947da7d271e0c17da28f8719c46ee57a68`.
**Verified live 2026-08-22: that exact blob is still on `origin/main`.** Statement (A) is
false only in the word "bit-reproducible", inherited from a field name; its counts, partition
and value are correct. Statement (B) is the Fig 2 caption *"one hull at 1100 kg, all runs
deterministic."* Drop-in replacement text and a standalone erratum already exist in
d8-naming's section 1.4. The slot's own note applies and is the reason this needs a person:
rebuilding locally does not unpublish what GitHub has served. **[read]**

**J4. The LICENSE carve-out is pending your sign-off.**
Landing plan section 5.3, from d10-licence's board rows. `LICENSE`,
`THIRD_PARTY_NOTICES.md` and `citations/README.md` are drafted but carry *"do not edit LICENSE
while Josie's sign-off is pending."* The exposure they cover is **four distinct third-party
sources, 20 image files, 7,213,546 bytes**, of which the Smith, Modra and Felder 2019 set (16
files, 6,215,623 bytes) is closed access. `claude/r8-licence` was merged into
`claude/add-ci-checks` at 2026-08-22 01:30:01, so the text is now on the branch with the
sign-off still outstanding. **[read]**

**J5. `assets/LICENSE.md` was recommended and never written.**
`claude/r9-renders`, commit `bd278a2`, 2026-08-20 00:10, closing register row B6:
*"RECOMMENDED, not done, because assets/ is outside this slot's write scope."* **Verified live
2026-08-22: `assets/LICENSE.md` is ABSENT on `origin/main`, on `claude/add-ci-checks`, on
`claude/r9-renders` and on `claude/r9-platform`, and absent from the working tree.** The
underlying permission question was answered by you: `c0fa82b` records *"Josie confirmed by
email 2026-08-19 that permission is granted for the Asphalt015 maps and the HDRI."* The
residue is one file. d18-platform measured (`c7000ea`) that `assets/` holds **six** tracked
files under **two** naming conventions, and I confirmed the list live:
four `Asphalt015*`, `DaySkyHDRI002A_1K_HDR.exr` (ambientCG naming, CC0 established by
`bd278a2` through byte-identical MD5 against the original downloads), and
`assets/hdri/kloofendal_43d_clear_puresky_2k.hdr`, which carries **Poly Haven** naming and is
covered by neither the CC0 identification nor, on its face, the emailed permission. **[read]**

**J6. Whether `josiecerrell/can-it-ford-results` should be public.**
`claude/r9-platform`, commit `e44b22e`, 2026-08-20 01:07. The repo was recommended for
deletion (`e11db07`: *"NOT DELETED, that is Josie's"*), deleted on your instruction, then
recreated and filled with 107 data files in ten folders, **private**, *"matching its prior
state, since nothing said to make it public; that is one flag if she wants it changed."*
**[relay]**, I did not call the Hugging Face API from this session.

**J7. The public `sweep-v1` MODEL repo serves 36 rows of the superseded box-proxy lineage with
no README.** `claude/r9-platform`, `83e99f5` and `e11db07`. Measured by that slot:
`josiecerrell/can-it-ford-sweep-v1` typed as a **model**, public, 37 real files, no README
(raw README 404), `density_plausible` **false on all 36 rows** by the pipeline's own check, and
its `manifest.csv` byte-identical to the committed `data/track1_sweep_v1/manifest.csv` after
newline normalisation. The fix is a README over already-committed data.
*"it is a public write so not mine."* **[relay]**

**J8. Whether to rebuild the research corpus index.**
`claude/r9-corpus-bib`, `6ff3f14` and `77994af`. The slot deliberately did **not** run
`--build` against the committed index: *"that is the index owner's call, not a side effect of
my unit."* A rebuild moves four numbers CLAUDE.md currently publishes: papers 332 to 319,
cited-anywhere 76 to 66, reader-facing 43 to 52, no-DOI 60 to 47. Its written recommendation,
still unanswered: *"land the tooling WITHOUT rebuilding the index, so the code fix and the
number change stay separately reviewable and separately revertable."* Note that reader-facing
rising 43 to 52 is a measurement change the slot introduced, not new research. **[read]**

**J9. The `ReservePool` row-collision defect.**
`claude/r9-moving-vehicle`, `d3e52fd`, 2026-08-19 00:17: *"ReservePool is deliberately not
used: its row-collision defect presents as physics and is awaiting a decision."* No
response found on any branch or board row. **[read]**

**J10. One paper needs a human with a browser.**
`claude/r9-gapscan`, `5213f6f`. `10.3390/jmse9040416` (Tao21b) is **nominally gold OA** and
MDPI 403s every client the session had, with and without a Referer, versioned and unversioned.
*"the one worth a human minute, since it is gold OA in a fully open journal and a browser will
almost certainly get what curl cannot."* Four other boundary-treatment papers on the same
question are genuinely paywalled and one (`10.1016/j.cpc.2009.05.008`) has an OA record that
is a metadata-only stub. **[read]**

### 1.2 ANSWERED, recorded so they are not asked again

**K1. The Overleaf push was authorised and it landed.** d23-overleaf held a six-edit patch
across three commits and wrote *"NOT PUSHED ... waits on an explicit go from Josie."*
**Verified live**: `refs/remotes/overleaf/main` is `3053956`, 2026-08-20 01:48:02, whose
message quotes you verbatim, *"Apply locally AND push to Overleaf"*, and
`git diff 6466dfa 3053956` shows four changed paragraphs in `conference_101719_1.tex`. This
is the only R9 output that reached a shipped deliverable. **[read]**

**K2. The two paper items "left for Josie" in `cb6617a` were both done in that push.** The
STATIONARY qualifier on the AR&R thresholds, and citing Azhar rather than Smith for the 1.0 to
1.8 drag range, are both present in the pushed diff. **[read]**

**K3. The data licence is now one licence.** d18-platform's `3f66ba1` reported three live
answers at once (CITATION.cff ODC-By-1.0, LICENSE BSD-3-Clause, and two dataset cards
cc-by-4.0 that the slot had itself written) and asked you to settle it in one sentence.
**Answered and applied 2026-08-20 11:53 in `96393ca`**, "BOTH DECISIONS TAKEN BY THE AUTHORS
AND APPLIED", CC-BY-4.0, chosen because the three live Hugging Face datasets already
advertised it so aligning re-licenses nothing already published.
**CAVEAT, measured live 2026-08-22 and worth acting on:** `origin/main:CITATION.cff` still
reads `license: ODC-By-1.0`, `claude/r9-platform:CITATION.cff` still reads `ODC-By-1.0`, and
that branch's unmerged `analysis/hf_dataset_publish.py` still writes `license: odc-by` at
line 288 and asserts ODC-By-1.0 in the card body at lines 416 to 417. Running that publisher
as it stands would republish the retired value. **[read]**

**K4. Asset permission was granted by email 2026-08-19** for the Asphalt015 maps and the HDRI
(`c0fa82b`), which is why `--asphalt-dir` came off its flag and defaults on. The residue is
J5. **[read]**

### 1.3 DECIDED WITHOUT YOU, flagged because the call was framed as yours

**L1. The ladder-stop.** `claude/r9-accessor` `05fb6db` (2026-08-19 18:35) wrote a decision
page for a non-specialist with two options, and refused to choose: Option A accepts job B's
FAIL and stops the ladder per manifest criterion "Any FAIL stops the ladder"; Option B amends
the criterion, and the slot recorded the cost out loud, that the manifest says of these bands
*"These bands are set now and will not be moved"*, so moving them means a band declared
unmovable was moved **after** the result it produced was known. Verbatim: *"I do not choose
between them."* Ten minutes later `0e8ef48` records that **the coordinator** accepted the FAIL
and stopped the ladder. A Claude session took a decision that had been written up for a human,
and the write-up attributes it to the coordinator rather than to you. The FAIL itself is not
in doubt: 24 gradings across six runs and four windows are all FAIL, and an exhaustive scan of
all 184 possible transient-exclusion start frames finds no window anywhere in the data, in the
slot's words *"defensible or not"*, that avoids one. **[read]**

**L2. The 2026-08-22 01:30 merge carried two unreviewed recovery commits past a written
precondition.** Landing plan section 5.4 sets a precondition in terms: `98d4d9d`
(`claude/r9-moving-vehicle`) and `d55ac14` (`claude/r9-renders`), both titled *"RECOVERED from
a crashed session"* and the second adding 621 lines its own message calls **untested**,
*"need their authoring slot's sign-off before the merge that carries them"*, with a named
fallback of merging at `056ba10` and `256d013` instead. **Verified live: both are now
ancestors of `claude/add-ci-checks`.** Those sessions no longer exist to sign off.
Mitigating, and I checked rather than assumed: on `claude/r9-renders`, seven later commits by
the same slot exercise, debug and repeatedly fix `cycles_render.py` and `prep_cycles_scene.py`
(`3d01611`, `52dcf9a`, `03df8f4`, `21bfca3`, `cd52357`, `6a0b52f`, `733c149`), so the untested
621 lines were subsequently tested by their own author; on `claude/r9-moving-vehicle`, 22
later commits supersede `98d4d9d`'s contents. Reported as **precondition unsatisfied but
consequences mitigated**, not as harm. Note also that section 5.4's own table calls both
commits "tip", which was true when written at 19:27 on 2026-08-19 and is stale now. **[read]**

---

## PART 2. THE BRANCH TABLE

"Board row" is measured against `.claude/state/r8_board.md`. **All thirteen slots have board
rows**, so nothing here failed for want of publishing. "Merged" is `git merge-base
--is-ancestor <tip> claude/add-ci-checks`, measured **2026-08-22 01:39:06**. **Merged means
merged into the local integration branch only.** Nothing here is on `origin/main`, which was
still `c7f0a16` of 2026-08-17 at 01:39, with the branch 413 ahead and 0 behind.
The three still unmerged are exactly the three with `changed in both` content conflicts, which
I probed read-only with `git merge-tree`: `r9-corpus-bib` on
`.claude/skills/research-corpus/SKILL.md` and `analysis/research_index.py`, `r9-platform` on
`hf_space/README.md` and `hf_space/app.py`, `r9-settle` on
`analysis/classify_failure_modes.py`. `r9-jobb-route` showed no conflict and merged at 01:38.

| branch | slot | what it concluded | contradicts or corrects | board | merged 01:39 |
|---|---|---|---|---|---|
| `r9-accessor` | d11 | Criterion 3 respecified onto `fz_over_analytic_measured` with window-robustness and stationarity gates; job B FAILS at every one of 24 gradings and at all 184 possible transient starts; the floor leak is a **floor-plane BC defect**, body-independent, 96.40 pct fixed by one character at `mpm_solver_warp.py:1955`; the column **never goes quiet**, KE/PE is 11 orders above the well-balanced reference and **grows**; KE/PE **rises** with particles per cell at 9.89 sigma, excluding quadrature and sampling; the floor writes **velocity, not pressure**, so neither SPH boundary fix has an analogue here | Withdraws its own "the ambient pressure field is exonerated"; withdraws its own NOT-GRADEABLE; withdraws its own "1 dx of surface offset" as a linearisation 34.4 pct too small; withdraws reason 3 of the ladder decision (Kramer 0.3 pct is a **motion** tolerance). **Contradicts d21 on locking, see D1.** **Contradicts d14 on SPH boundary transfer, see D3** | 18 rows | **yes** |
| `r9-jobb-route` | d21 | Hypothesis E1 (near-field surface estimator) **refuted** on six then nine arms; the FAIL is a solver defect, not an instrument artifact; `918450` is a **one-character engine fork**; the floor leak explains about **one third**, and a tank losing no water still fails by 1.4x the band; **two** floor-leak mechanisms, not one, with a ~2.2 pct baseline neither alignment nor the fix touches; volumetric locking **refuted as the dominant term** on its own PPC signature, flat over 19x; a third accessor agrees to under 2 pct | Withdraws two relayed Wal07 claims after reading the paper; withdraws its own non-convergence claim, then withdraws the replacement too; **withdraws its own "the accessor is exonerated" 65 seconds after d12 adopted it, see D2**; Ami15 fails the new scope test on three independent counts | 40 rows | **yes**, 01:38 |
| `r9-settle` | d15 | Velocity equilibrates and displacement **cannot**, replicated on 87 long records from three independent jobs, zero exceptions; a 91-frame displacement record is **too short to detect its own drift** (38/76 pass stationarity at 91 frames, 0/20 and 1/15 at 250); a three-class rule, EVENT / STEADY / **NEITHER**, with two tests needing no new data; `final_disp_mag_m` is class 3 and CLAUDE.md item 5 **understates** it, because at 2337 kg the sign falls on both legs | Corrects register row B4's population from 25 to 21 with every headline surviving; withdraws its own "nobody has ever run a longer one" (35 comparable 250-frame records already existed); withdraws its own N_eff magnitude across 8 specifications; demotes its own "all 30 moves delete a SLIDE and 0 create one" from measurement to **theorem** | 31 rows | **no** |
| `r9-moving-vehicle` | d17 | The v_car by v_water **load surface**, 135 runs, five arms, three seeds: the split matters at every magnitude and S grows with speed (0.76 to 1.28); a standard **2 pct road camber cuts horizontal load 36.5 pct** at fixed flood level, and 18.6 pct survives matching the depth at the vehicle; the depth-matched difference **reverses sign** between 2 and 4 pct at 194 and 41 standard errors; the resolution ladder does not converge | Withdraws its own 2.3x headline pair as a **transient window**, closing d18's C-1; adds a third class to d15's rule (a **comparison** needs a window where the ordering is stable); corrects "the one Al-Qadami et al. 2022 actually drove" (that DOI is numerical) | 23 rows | **yes** |
| `r9-priorcode` | d19 | Prior art is **at least fourteen works**, every DOI resolved against Crossref, and **the shipped paper cites exactly one of them** (`shah2018`); `alqadami2022` is **one key pointing at two different papers** in two copies of the bib; Lyu 2024 (`10.1016/j.compfluid.2023.106144`), an entirely particle-based 3D SPH vehicle-wading model, is absent from the corpus, both bibs and the repo; the canonical bib is `overleaf/main:can_it_ford_references_IEEE.bib`, 15 entries; **four JLR patents** on wading depth exist and **no search this project has run has ever covered patents** | Refutes CLAUDE.md's "eight or nine" prior works with **14**; withdraws its own repo-wide Lyu count as measuring its own activity; withdraws its own "all fourteen cited zero times" to **thirteen of fourteen**. **Partially contradicts d23 on the bib collision, see D5** | 20 rows | **yes** |
| `r9-renders` | d13 | A path-traced Cycles pipeline with five guards each run against the input that breaks it; the **library docstring is wrong** and reading it literally gives one blob per particle while passing every cheap check; the melting hulls are a **mesh-source** defect; register **B6 closed**, the HDRI is ambientCG CC0 by byte-identical MD5; a 22 m domain deletes the surround, taper and patch rectangle together | **Corrects its own published figure**: the 2.8x and 3.3x surface-deviation gap printed on delivered images is mostly a resolution artifact, corrected to 2.19x and 1.77x on mean dihedral; the smoothest Rogue on disk is missing **47.6 pct of the car**, so smoothness selection needs a hard volume gate first | 38 rows | **yes** |
| `r9-platform` | d18 | Published the 368-record speed surface as a HF dataset, a two-tab Space and one W&B run; **"six public empty shells" refuted**, `usedStorage` counts LFS only and the populated repo is the wrongly-typed **model** repo; **the whole R9 wave is invisible to W&B** except one run pushed by hand, because all six `wandb.init` sites are in post-hoc scripts and none in a driver; Zenodo mints a DOI for a **restricted** record, so citability does not require publishing | Overwrote a published L1 physics fix on the public Space and repaired it after d16 caught it; corrects "106 runs each carry one history row" to 36 with one and **70 with no `_step` at all**; introduced the third licence value itself | 22 rows | **no** |
| `r9-corpus-bib` | d14 | **The index holds no full text and never did**: 15 fields, none a body, largest blob 3,477 characters, 110 of 332 with no abstract, so every corpus-sourced method and novelty claim came from titles and abstracts; `--query` **never matched authors**, which is why a zero read as coverage; three trees hold three states of one capability and the **half-fixed** middle one fails silently | Refutes the relayed "none of the six closest prior-art DOIs is in the corpus": **all six present**; identifies the mechanism as **relay amplification**, one session's misread reaching three; makes d16's "neither side is a superset" false by carrying 13 of 13 themes across; measures the false positive too, `--query "bed"` returns 32 of which 11 are the word | 25 rows | **no** |
| `r9-landing` | d16 | A staged landing plan, nine revisions, nothing executed; **rule B5, never state the ahead count without the behind count**, with the measurement that ahead read 64/65/66/67/82/93 and behind read **5 every single time**; all five behind commits touch CI or a public surface; the CI job is **green over a step that exits 1**, predicted before the run that proved it | Refutes register row C1 with a control (content ancestry and merge behaviour are independent); retracts its own "step 19 needs a decision from Josie"; corrects its own "half the workflow cannot return a negative" to two of six | 32 rows | **yes** |
| `r9-reader` | d20 | Nobody had read the whole round and **the index of it covers 38.7 pct** (18 transcripts exist, the TSV names 9); the adversarial reviewer had a **zero percent success rate**, 20 calls, 0 successes, and an explicit model override does not reach it; the eleven-session structure is **justified**, 65 files with one multi-writer; **the single lane violation is the coordinator's**, on the authority skill file | Refutes the corpus document D5's headline novelty claim; corrects the coordinator's own self-description; records its own measurement failing twice first, in the same class it was auditing | 25 rows | **yes** |
| `r9-gapscan` | d22 | A 261-work want list, **68 of 230 reachable and 162 not**, with barriers counted (105 closed, 49 unresolved, 57 open-but-refused); `WebSearch` and `WebFetch` are dead with the **same** model error as the Agent path, so it is not subagent-specific; Sch19e obtained and read, and its von Mises quantity is **blind to the hydrostatic part** a buoyancy force is made of; 38 of 38 acquired PDFs verified against their own text | Withdraws its own 156-on-disk figure (unquoted Spotlight is an OR); withdraws its own "49 works carry no DOI"; finds **two wrong files in thirteen scraped**, a 15 pct rate, and fixes the root cause; catches **its own misquotation** inside quotation marks | 24 rows | **yes** |
| `r9-kramer-extract` | d12 | Kramer's 0.3 pct is the **paper's own abstract**, not external corroboration, and it is **normalisation dependent**, 5.1x to 5.2x larger against the local signal and 53x at worst; criterion 3 **never graded a force**, it graded a normalisation over a shared numerator; criterion 4 is structurally incapable of detecting the error criterion 3 disputes; the free-decay **period** discriminates multiplicative from additive bias | Closes register B3 at its source; **adopts Outcome B and declares the accessor exonerated 65 seconds before d21 withdrew that claim, see D2**; corrects its own pre-registered magnitude for naming no submergence, in the section whose subject was that exact omission | 30 rows | **yes** |
| `r9-overleaf` | d23 | Corrected the shipped paper: ground clearance **was** measured (0.1737 m); the class match is **inverted**, no AR&R class is satisfied on all three axes and the class the paper called its only genuine match fails the axis the same sentence said was never measured; the 0.78 friction figure is **Smith's, not AR&R's**; the paper's fallback quantity is its **least converged**; `force_balance_v2.pdf` is the one figure **nothing in the repo can redraw**, and its caption survives a full recomputation | **Refutes** the dispatched "1.0 to 1.8 becomes 0.98 to 1.83" and made no edit, because the replacement was relayed and the original is near verbatim from Azhar read directly; refutes the dispatched bib collision as not matching the live files | 9 rows | **yes** |

---

## PART 3. LIVE DISCREPANCIES

Reported for a human to resolve. **I have not picked a side on any of these.**

### D1. Volumetric locking: SURVIVES on one branch, REFUTED on another, 46 seconds apart

- `claude/r9-jobb-route` `3f4c1ec`, 2026-08-19 **23:51:18**: *"LOCKING IS REFUTED AS THE
  DOMINANT TERM."* Evidence: force excess **flat** in particles-per-cell over a 19x span up to
  4.78 million particles, log-log slope +0.0596 where locking's first prong requires a rise.
- `claude/r9-accessor` `03cd132`, 2026-08-19 **23:52:04**: *"KE/PE RISES with particles per
  cell at 9.89 sigma."* Evidence: +25.86 pct from 8 to 27 ppc in a body-free hydrostatic
  column, pre-registered with the output unopened, with quadrature and acoustic sampling
  excluded on sign.
- `claude/r9-gapscan` `754af7f`, 23:35: the solver has **no locking mitigation of any kind**,
  and the fluid branch of the stress update is the exact line F-bar replaces; it names d11's
  column as the right test bed.

**Why this is not obviously one error.** The two measurements are different scenes (body-free
column against the sphere scene) and different observables (KE/PE against force excess), and
d11 narrowed the mechanism to the **pressure-oscillation channel** rather than deviatoric
locking, because the fluid's F is forced isotropic. So both may hold. But they are stated in
opposite directions on the same named mechanism, in two documents that will be read together,
and **neither branch's author saw the other's result**. d21 also states plainly *"I have NOT
read Zha22d; the coordinator did"* and *"refuting dominant is not refuting present."* The
decisive test both name and neither ran is a **compressibility sweep**. **[read]**

### D2. "The accessor is exonerated" was adopted into a criterion 65 seconds before it was withdrawn

Exact timestamps, read from git:

| time | branch | event |
|---|---|---|
| 2026-08-20 01:19:25 | `r9-jobb-route` `f7f0c89` | *"A THIRD accessor confirms the force to under 2 percent: the accessor is exonerated."* |
| 2026-08-20 02:08:47 | `r9-kramer-extract` `0024ac1` | *"THE ROUTES AGREE, THE ACCESSOR IS EXONERATED, CRITERION 3-B IS ADOPTED."* Outcome B adopted verbatim from a four-outcome pre-registration. |
| 2026-08-20 02:09:52 | `r9-jobb-route` `87ae518` | *"Both attacks on f7f0c89 land. 'The accessor is exonerated' is WITHDRAWN."* |
| 2026-08-20 02:14:20 | `r9-gapscan` `5213f6f` | Re-aims a whole literature acquisition pass on the same claim, correctly flagged *"Relayed, flagged as under adversarial review, not re-derived by me."* |

The withdrawal's reason, read directly: particle stress is causally downstream of the collider
through the p2g2p substep order, and in a steady state **momentum conservation makes the two
readings approximately equivalent by construction**, so the control-volume reader is not
independent of `sdf_wrench` in the way the pre-registration assumed. What survives is narrower
and d21 states it: agreement under 2 pct excludes the accessor failure modes that would break
the momentum balance, which is most of the ways an accessor is actually wrong, but not a fluid
state that is itself biased. d21 also withdrew the non-tautological byproduct after finding the
implied excluded volume varies by a factor of 1.8 depending on which box measures it, and
identified a further 3 to 12 pct error of its own in `Fz_cv` from using current rather than
initial volume.

**The live discrepancy, and this half closed while the document was being written.** Criterion
3-B is adopted in `docs/R9_JOBC_PREREGISTRATION_AND_BLOCKER_2026-08-19.md`, merged at
01:30:02. At 01:34 the withdrawal in `docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md` was **not**
on the branch, so a reader got the adoption without the retraction; at 01:38:26 the concurrent
session merged `claude/r9-jobb-route` and both are now present. **What does not close is the
substance:** the two documents now sit side by side on one branch, one adopting a criterion on
a claim the other retracts, and **nothing reconciles them**. d12's criterion 3-B1 is an
agreement gate between the two routes at 2 pct, and d21's withdrawal says that agreement is
what momentum conservation forces rather than independent evidence. Someone has to decide
whether 3-B1 still grades anything. d21 also names what would actually settle it: a **pressure
integral over the wetted surface**, which is not forced to agree with a momentum impulse.
**[read]**

### D3. Whether SPH boundary fixes transfer to this floor

- `claude/r9-corpus-bib` `de18180`, 2026-08-20 **02:07**: aims the corpus at the floor and
  names four SPH boundary papers already in an unbuilt export (Mon09, Neg22, Gar19, Jou20),
  with Neg22 first. It carries its own caution: *"three confirmed wall findings ALL SPH is a
  warning as well as a result"*, and flags the tension as **unadjudicated**.
- `claude/r9-accessor` `c621539`, 2026-08-20 **02:06**: measured from the pinned solver that
  the floor writes a **grid-node velocity** and never a pressure; no dummy particles, no
  boundary pressure, no interpolation, no free-surface test, no cutoff. *"THE ABSENCE IS THE
  FINDING: there is no analogue, so there is nothing a C_van or C_cut style fix could be
  ported onto."*

One minute apart, opposite directions, neither author aware of the other. d11 offers a
structural parallel it explicitly declines to call more than a candidate (the `1e-15` mass
guard at `mpm_utils.py:935-941` sits thirteen orders below a full node's mass and gets
**weaker** with refinement), and records the evidence against it in the same commit. **[read]**

### D4. Sch19e and image particles: adjudicated on one branch only

`claude/r9-corpus-bib` records that the 17:44 deep search cites Sch19e for wall momentum
zeroing distorting stress several grid lengths into an object with image particles reducing
it, while d19-priorcode reports `image_particles.py` as run and **refuted**, and calls it
*"same mechanism, opposite directions"*, not adjudicated. `claude/r9-gapscan` `27f0996` then
obtained and read the paper and **does** adjudicate it: the published method is for planar
walls around an **elastic solid** graded on **von Mises stress**, which is by construction
blind to the hydrostatic part a buoyancy force is made of, and the authors state it supports
*"only boxes"*, so a refutation obtained on a curved fluid-immersed body is evidence about
this repo's use of it and not about the method. That adjudication is on `r9-gapscan`, which is
merged; the tension as stated is on `r9-corpus-bib`, which is not. **[read]**

### D5. Two incompatible characterisations of the `alqadami2022` bibliography defect

- `claude/r9-priorcode` `bdb86cb`: *"The SAME citation key resolves to TWO DIFFERENT WORKS in
  two copies of the bibliography"*, `paper/` pointing at `10.1111/jfr3.12828` (2022,
  numerical) and `overleaf_sync/` at `10.3390/su151713262` (2023, 3D CFD), *"and the key
  asserts a year wrong for one of them."*
- `claude/r9-overleaf` `82640de`: *"The dispatched bibliography collision also does not match
  the live files. The shipped bib has no Al-Qadami entry at all ... overleaf_sync's
  alqadami2022 carries no DOI; 10.3390/su151713262 appears only inside its note as an open
  question. The two bibs do not disagree about which work it is, one declines to say."* It
  names a different real defect: a **duplicate key** in `paper/`, `alqadami2022` and
  `alqadami2022moving` being one work under two keys.

Both agree the shipped deliverable is unaffected and that this is a merge hazard rather than a
correctness defect in what compiles. They disagree on what the defect **is**, and both are
now merged into `claude/add-ci-checks`. Cheap to settle by reading the two bib files. **[read]**

### D6. Three live numbers for the count of prior fording or wading work

`CLAUDE.md` currently says *"the deep-search layer puts it at eight or nine"* and to not cite
four. `claude/r9-priorcode` measured **at least fourteen**, every DOI resolved against
Crossref by that session rather than carried from a list, and both those branches are merged.
`claude/r9-moving-vehicle` cites *"at least four published works already simulate or test a
moving vehicle."* Not a contradiction so much as an unpropagated supersession, and CLAUDE.md
is the copy every session loads. d19's own scope sentence must travel with any replacement:
papers only, corpus not a superset of the bibliography, `--query` cannot match authors, and
**patents and OEM specifications have never been searched at all**. **[read]**

### D7. Register row C1 was wrong in both directions inside 18 hours

Coordinator `e0d2beb` (2026-08-19 00:19) refuted its own add/add-conflict claim on
`simulation/openchannel_bc.py` by content identity. Coordinator `7a0d08a` (18:11) re-refuted
that refutation with a control from d16-landing: the path is **absent from the merge base**,
so both sides add it and git has no base blob, and *"lineal content ancestry is invisible to
git unless it is in the DAG."* Self-resolved on the second pass. Recorded because the register
is the corrections authority and this row moved twice in one day. **[read]**

### D8. The unadjudicated boundary in the settle work

`claude/r9-settle` `27b83c2` checked and states that d21's force-accessor finding **does not
reach its own grades** (its four modules read only `dx`, `dmag`, `vx`, `vmag`), but names
where it would: TOPPLE gates on `surge_accel_g` against `ssf` and computes `weight_n`, *"so
anyone extending this to TOPPLE or FLOAT must resolve the denominator question first."* That
branch is **not merged**, so the boundary condition on any future extension is currently
recorded nowhere on the integration branch. **[read]**

---

## PART 4. VERDICT

**Yes. Almost all of it.** Measured live on 2026-08-22: `origin/main` is at `c7f0a16`, dated
2026-08-17, so **not one of the 187 R9 commits is on GitHub main**, and no `r9-*` branch
exists on the remote at all; the poster has not been touched by any commit since 2026-08-15
and still carries, in a public blob whose hash I verified, the two false statements d8-naming
wrote replacement text for; and exactly one R9 output reached a shipped deliverable, d23-
overleaf's six-edit correction to `conference_101719_1.tex`, pushed to Overleaf as `3053956`
on your explicit authorisation. Everything else is in a local branch. That branch,
`claude/add-ci-checks`, was 413 commits ahead of and zero behind `origin/main` at 01:39 after a
concurrent session merged ten of the thirteen R9 branches tonight, which closes the loop
**into the integration branch** and not into anything a reader outside this machine can see,
and which is itself blocked from going further by an unrotated credential that only you can
rotate (J2). What is stranded is not marginal: the paper cites **one** of at least
fourteen prior works and is missing the closest published method to its own (Lyu 2024); a
**2 pct road camber cuts horizontal load 36.5 pct**, which is the round's one genuinely novel
positive result and is cited to a documented absence rather than an assumption; the canonical
runs' headline displacement magnitude is demonstrated to be a quantity **no window can
stabilise**, which the paper now footnotes but the poster does not; the floor leak has a
one-character remedy nobody has landed in the engine; and three branches carrying d15's settle
rule, d14's corpus tooling and d18's platform work are still unmerged on content conflicts,
while the branch a reader picks up today now holds a criterion and the retraction of the claim
it was adopted on, side by side and unreconciled (D2). The honest summary of the sprint is the title
its own coordinator gave it, **The Round That Refuted Itself**: it was extraordinarily
productive at finding and killing its own errors, and it produced almost nothing anyone
outside this repository can currently read. It also ran with **zero adversarial review**, 20
subagent calls and 0 successes across the whole round, so every physics number above remains
**UNREVIEWED** by a second party, and this document does not change that.

---

*Written 2026-08-22 by a session that read all thirteen branches' commit bodies in full and
verified every merge, remote and file-state claim live. Not adversarially reviewed: the
subagent path was not exercised for this document either.*
