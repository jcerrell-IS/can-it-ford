# R9 loop closure: status of the eleven decisions, 2026-08-25

Re-checks `docs/R9_LOOP_CLOSURE_2026-08-22.md` against live state three days later.
Investigation pass: read-only. **A later pass the same session applied fixes; see
`Fixes applied` at the end.** Nothing committed or pushed.

**Both source files exist and were read in full**: `docs/R9_LOOP_CLOSURE_2026-08-22.md`
(560 lines, 46,581 bytes, mtime 2026-08-22 03:26) and
`docs/CLUSTER_STATE_AUDIT_2026-08-22.md` (664 lines, 28,269 bytes, mtime 2026-08-22 03:26).
[READ]

**Tagging**: [READ] means I ran the command or read the bytes in this session.
[RECALLED] means it came from a summary or memory and I did not re-derive it.
[INFERRED] means I reasoned rather than measured.

**One incoming premise was wrong.** The chat summary that opened this thread described J11
as "DesignSafe DOI minting". A live grep of `R9_LOOP_CLOSURE_2026-08-22.md` for `designsafe`
returns **zero hits**. J11 is a choice between **Zenodo** and **Hugging Face via DataCite**,
and the document explicitly declines to pick one. Do not carry "DesignSafe" forward. [READ]

**The count is right**: eleven decisions, J1 to J10 in section 1.1 plus J11 introduced in
section 5.6. [READ]

---

## Three things in the document are now false, and they change the verdict

Stated up front because they are the largest movements, and because Part 4's summary rests
on all three.

1. **"No `r9-*` branch exists on the remote at all" is FALSE.** Live
   `git ls-remote --heads origin 'refs/heads/claude/r9-*'` returns **all thirteen**, and each
   tip matches its local tip. The local remote-tracking refs were written **2026-08-22
   14:25 to 14:26**, about twelve hours after the document was finished at 02:26. A push
   happened. [READ]
2. **`claude/add-ci-checks` is itself on the public remote**, at `57db739`, byte-matching
   local. `hull_load_identical` (the d8-naming rename) resolves on
   `origin/claude/add-ci-checks` in ten files. So the R9 work **is** readable outside this
   machine, on GitHub, in a public repository. Part 4's "produced almost nothing anyone
   outside this repository can currently read" was true when written and is now wrong.
   What remains true is the narrower claim: **zero R9 commits are on `origin/main`**, which
   is still `c7f0a16` of 2026-08-17. [READ]
3. **Two branches are unmerged, not three.** `claude/r9-corpus-bib` (`de18180`) was merged
   into `claude/add-ci-checks` by `a83a38b` at 2026-08-24 17:56:42. Still unmerged:
   `claude/r9-settle` and `claude/r9-platform`. [READ]

Backlog count, the item this thread already re-checked: the document read **413** ahead at
01:39 and **419** at 02:21. Live now, `rev-list --left-right --count origin/main...claude/add-ci-checks`
gives **0 behind, 467 ahead**. Moved past, direction unchanged, rule B5 satisfied (the behind
count was read and is zero). [READ]

---

## The eleven decisions

| # | Decision | Status 2026-08-25 | Evidence, live |
|---|---|---|---|
| **J1** | Contact the Kramer et al. authors about the reversed-gauge-order data defect | **STILL OPEN**, unmoved | No commit on any ref since 2026-08-22 matches `kramer` (`git log --all --since --grep`). `docs/R9_KRAMER_FULL_EXTRACT_2026-08-18.md:456-466` still carries both draft sentences and "**Whether to make it at all is Josie's decision**". [READ] |
| **J2** | Rotate the exposed credential, which was said to gate every push | **OPEN AS A ROTATION, BUT ITS STATED CONSEQUENCE IS GONE** | `docs/CREDENTIAL_EXPOSURE_2026-08-13.md:3` still reads "**Status: OPEN. Rotation is a Josie action and has not been done.**" The file is still untracked, so it was not itself published. But the push it was said to gate **happened anyway**: 13 r9 branches plus `claude/add-ci-checks` are live on the public remote. The gate was bypassed, not satisfied. [READ] |
| **J3** | The poster on `origin/main` carries two false statements | **STILL OPEN. Independently re-confirmed from the blob today.** Full detail below, deliberately not compressed | See the J3 section. [READ] |
| **J4** | Sign off the LICENSE carve-out | **STILL OPEN in substance, and now published without sign-off** | The "do not edit LICENSE while Josie's sign-off is pending" marker no longer appears in `LICENSE`, `THIRD_PARTY_NOTICES.md` or `citations/README.md`. All three differ between `HEAD` and `origin/main`, and `THIRD_PARTY_NOTICES.md` is **absent from `origin/main` entirely**. The drafted text is on `claude/add-ci-checks`, which is now on the public remote, with no recorded sign-off anywhere. [READ] |
| **J5** | Write `assets/LICENSE.md` | **STILL OPEN**, unchanged | ABSENT on `origin/main`, `claude/add-ci-checks`, `claude/r9-renders`, `claude/r9-platform` and in the working tree. `assets/` still holds exactly six tracked files: four `Asphalt015*`, `DaySkyHDRI002A_1K_HDR.exr`, and `hdri/kloofendal_43d_clear_puresky_2k.hdr` under Poly Haven naming, which the emailed permission does not on its face cover. [READ] |
| **J6** | Should `can-it-ford-results` be public | **STILL OPEN**, unchanged, and now [READ] rather than [relay] | Hugging Face API, live: typed **Dataset**, **Private**, 107 files, licence `cc-by-4.0`, 3 downloads, updated 20 Aug 2026. The document could only relay this; I called the API. [READ] |
| **J7** | The public `sweep-v1` MODEL repo serves superseded data with no README | **CLOSED. The fix is live.** | `https://huggingface.co/josiecerrell/can-it-ford-sweep-v1/raw/main/README.md` returns **HTTP 200**, not the 404 the document reports. The README carries a `superseded` tag and a body explaining the box proxy, the two kept classes, and what replaced it. Repo updated **21 Aug 2026**, one day **before** the document listed it as open. The document tagged J7 **[relay]** and was honest about it; the relay was already stale when written. [READ] |
| **J8** | Rebuild the research corpus index | **OVERTAKEN BY EVENTS. The decision as framed is moot.** | The index **was** rebuilt: `--stats` prints `index built 2026-08-25 papers 382 abstracts 211 cited 164`, committed at `e1921cf` (2026-08-25 02:15), working tree clean for that path. J8's predicted deltas (papers 332 to 319, cited 76 to 66, reader-facing 43 to 52, no-DOI 60 to 47) **never occurred**, because `e1921cf` fixed the ingest aborting on `MANIFEST.json` and changed what a rebuild produces. Nobody can now choose "land the tooling without rebuilding": both landed. [READ] |
| **J9** | The `ReservePool` row-collision defect | **STILL OPEN**, no fix | No code fix on any ref. The defect survives only in digests and memory: `ReservePool` writes rows `[n_water, n_water+n_reserve)`, which in the vehicle layout **are the rigid body**; `pin_parked` teleports 20 of 37 vehicle rows into the park box and raises nothing; the body keeps the right mass and gets the wrong CG and wrong inertia, which are the quantities deciding topple. The only constructor guard validates the park **box**, never the **rows**. [READ] |
| **J10** | One paper needs a human with a browser | **STILL OPEN**, and the instrument now exists | `10.3390/jmse9040416` (Tao21b) appears only in `docs/r10/*` manifests, `R10_WEB_ACQUISITION_2026-08-19.md` and memory. No PDF under `citations/`. Note that memory `browser-reaches-gold-oa-that-webfetch-cannot` records the in-app browser reaching MDPI gold OA that curl and WebFetch cannot, so this is now a five-minute job rather than a blocked one. [READ] for the absence, [RECALLED] for the browser route. |
| **J11** | Mint a citable DOI, Zenodo or Hugging Face DataCite | **STILL OPEN**, unchanged, blocker still cleared | No `.zenodo.json` tracked on `HEAD`. No `doi` or `identifier` field in `CITATION.cff` on `origin/main`, `claude/add-ci-checks` or `claude/r9-platform`. Its stated precondition (which licence covers the data) remains answered. The document names two routes and picks neither. [READ] |

**Score: seven still open (J1, J2 as a rotation, J3, J4, J5, J6, J9, J10, J11 = nine), one
closed (J7), one moot (J8).** Counting J2 as open on the rotation and closed on the
consequence. No commit anywhere in the repository closes a J-item **by number**: the
`git log --all --grep="J1[0-9]*\b" -E` sweep returned three commits (`6e957e3`, `8590313`,
`b62d554`), all of which match on register rows J15/J16 and none of which references a
loop-closure J-item. `git log --all --grep="loop closure" -i` returns exactly one commit,
`1a1099d`, which is the document itself. [READ]

---

## J3 in full, because it is the highest-stakes item and it is real

**I re-derived this from the committed blob rather than trusting either document.**

The blob on `origin/main` at `public_release/Cerrell_TACC_42x56.pdf` is
`168879947da7d271e0c17da28f8719c46ee57a68`, byte-identical on `claude/add-ci-checks`.
Extracted by SHA with `git cat-file -p`, it is 6,102,270 bytes with sha256
`48685a7dc20b5c4d58eb7d38e8f644b04a8a2246a62a9083eedfe13d65b2ed63`, which matches the value
`docs/R8_DETERMINISM_RENAME_2026-08-18.md` recorded independently on 2026-08-18. [READ]

**The method warning in that document is correct and I confirmed it as a control.**
`/usr/bin/strings <pdf> | grep -c 'all runs deterministic'` returns **0**. PDF text lives in
Flate-compressed streams. Anyone re-checking this with `strings` or `grep` will falsely
conclude the claim is absent. Use `pdftotext`, which returns **1** for each phrase. [READ]

### Statement A, in the poster's `Scope` panel under the sub-heading `ESTABLISHED`

Extracted from the committed blob today:

> ESTABLISHED 20 coupled runs. All 17 that carry a determinism record are bit-reproducible;
> the 3 dry-start runs record none. Mesh containment 100.00 pct of a 2000-particle subsample.
> DxV bit-identical across a 2.1x mass range.

### Statement B, the Fig 2 caption

> Fig 2. Final displacement against surge velocity at fixed realized depth 0.2944 m, grid 64,
> one hull at 1100 kg, all runs deterministic. Vertical rule marks v = 1.0189 m/s, where DxV
> crosses the AR&R small-passenger 0.30 m2/s cap.

### What is actually false, and what is not

The document's characterisation is precise and I am repeating it rather than softening it.
**Every factual component of statement A is correct.** There are 20 records; 17 carry the
field; the 3 dry-start runs carry the literal `"ABSENT"`. The sentence is false **only in the
word "bit-reproducible"**, which was inherited from a field name rather than introduced in the
writing. The field was called `determinism_identical` and compares **a particle count and a
grid limit between two loads of the same hull**, nothing more. It cannot detect whether
trajectories differ, and the trajectories do differ. Statement B repeats the error, and
`ESTABLISHED` is what makes statement A the more serious of the two.

### Has it been corrected anywhere live? Partly, and not where it counts

| remediation | state |
|---|---|
| Field renamed `determinism_identical` to `hull_load_identical` | **DONE on the branch.** 11 files on `HEAD` carry `hull_load_identical`, including `analysis/make_poster_figures.py` and `renders/yaris_render_s1/sim_standing.py`. [READ] |
| Rename reaches `origin/main` | **NO.** `git grep -l hull_load_identical origin/main` returns **zero files**; `determinism_identical` still resolves there in ten. [READ] |
| Poster PDF re-issued | **NO.** Same blob, last touched by `b78bc1e` of **2026-08-02 16:30:43** on both `origin/main` and `claude/add-ci-checks`. [READ] |
| Erratum published | **NO.** No erratum file has ever been added under `public_release/` or `deliverables/`. The only `errata` commit in the repository is `ad9fa20`, `docs/R5_RESEARCH_INDEX_AND_ERRATA_2026-08-16.md`, unrelated. [READ] |

**Scope note on my own first measurement.** My initial
`git log --all -1 -- public_release/...` returned `142b400c` of 2026-08-04, which looked like
it contradicted Part 5.2's `b78bc1e` of 2026-08-02. It did not. `--all` swept a third ref;
per-ref on both `origin/main` and `claude/add-ci-checks` the answer is `b78bc1e` 2026-08-02,
exactly as Part 5.2 states. Part 5.2's correction to Part 4 stands. [READ]

**Ready-to-use replacement text already exists** in `R8_DETERMINISM_RENAME_2026-08-18.md`
section 1.4: a drop-in `ESTABLISHED` line, a drop-in Fig 2 caption clause, and a standalone
erratum paragraph. Nothing needs drafting. [READ]

### The one thing that blocks deciding J3, and it is recorded blank

`docs/SUBMISSION_STATUS.md` exists to answer exactly the question that determines whether J3
needs a re-issue or an erratum. Live, it reads:

```
# Submission status
- Poster uploaded to Final Posters folder before 2026-07-27 09:00 CST: 
- Paper submitted anywhere, and where: 
- Filled in: 2026-08-24
```

Both answers are **empty**, and the block is duplicated twice in the file. Commit `2d4c71a`
(2026-08-25 02:01) is titled "Fill in actual poster and paper submission status" and its diff
replaces the `[YES/NO]` placeholders **with empty strings**. Its predecessor `12486ea` is
titled "Record poster and paper submission status per direct human confirmation". **Two
commit messages assert a human confirmation that the file does not contain.** Whatever was
confirmed was not written down. [READ]

The consequence for J3 is concrete. Re-issuing helps if the poster is still being downloaded
and does not help if it was presented and printed; an erratum is the right instrument in the
second case. Neither the document nor the repository records which case this is. And, as
d8-naming's section 1.5 says and I confirmed independently, rebuilding the PDF locally would
not unpublish what GitHub has already served.

---

## The cluster audit

`docs/CLUSTER_STATE_AUDIT_2026-08-22.md` documents its own SU-balance command as reading
`/usr/local/etc/taccinfo` on each machine, and I re-ran it rather than quoting the file.
**Trap worth recording: `taccinfo` is an executable perl script, not a data file**, so `cat`
returns the source and no balance. Executed live, **Vista reads 571 SU** for BCS20003
expiring 2026-09-30, against the audit's **581** on 2026-08-22, so 10 SU went in three days,
and the same reading shows `/home1` at **90.78 percent** of quota (21.1 GB of 23.3 GB), which
is unchanged since 2026-08-22 and is a live warning printed by TACC itself. **The LS6 balance
could not be re-read**: the ControlMaster socket has expired and re-authentication needs an
interactive TACC token, so `scripts/tacc.sh ls6` returns
`Permission denied (keyboard-interactive)`. The audit's **9536 SU** for LS6 therefore stands
as a 2026-08-22 reading and **is not verified today**; run `ssh ls6` once interactively to
re-enable it. The audit's headline waste finding reproduces from its own primary sources and I
did not re-derive it from the cluster: LS6 job `3339919` (`hold48s`) ran 47.889 node-hours on
`gpu-a100-small` at rate 1.5 for **71.83 SU**, 49.1 percent of all LS6 August spend, executing
seven probe lines and `sleep 172400`, and it could not have worked because TACC purge keys on
**file access time** and holding a node changes no file's atime [RECALLED from the document,
whose own reading of the slurm file and the TACC policy text I did not independently repeat].
The audit is careful to note this is wasted budget and not a policy breach, since the version
that would have worked is the version TACC prohibits. **One time-sensitive item in that
document has now expired**: section 6 warned that about 19 GB of the `three_class_*_2026-08-14`
family plus `chrono_x86` and `fork_moving_driver` would cross the 10-day purge line **on
2026-08-24**, which is yesterday, on top of 1,129 files already purge-eligible including
`drainA` at 536 MB holding the COLMAP reconstruction. Whether that data survived is
unresolved and unresolvable from here until LS6 access is restored, and it is the single most
perishable item in either document.

---

## Effect on the three corpus-merge landing decisions

**Two of the three are already executed, and the third is moot. None of them still needs a
decision, and one of them was resolved differently from how it was framed.** On the
**`--source-audit` rename**, the collision was settled on **2026-08-24 by renaming the other
check, not by choosing a winner**: `analysis/research_index.py:1745` still declares
`--source-audit` as the CI gate that CLAUDE.md and the corrections register already cite, and
the corpus-bib branch's reachability report became **`--ingest-audit`** at line 1773, with the
reasoning written into the source at lines 1764 to 1778 ("this one took the new name because
it has no external citers"). Both checks survive, no external citation broke, and the live
gate prints `FAIL (17 problem(s))`, matching CLAUDE.md's stated 17 as of 2026-08-25 [READ]. On
**landing on `add-ci-checks`**, that also already happened: `claude/r9-corpus-bib` `de18180`
merged at `a83a38b`, 2026-08-24 17:56:42, and is on the public remote; the reason nobody
noticed is that `a83a38b` is titled "Record poster and paper submission status per direct
human confirmation" and says nothing about the merge, which `c82adb7` records as the finding
worth keeping [READ]. On **no index rebuild**, that decision is **superseded and should be
retired rather than re-affirmed**: the index was rebuilt on 2026-08-25 and committed at
`e1921cf`, and it did **not** move to the 319 J8 predicted but to **382 papers, 211 abstracts,
164 cited**, because the same commit fixed the ingest aborting on `MANIFEST.json` and thereby
changed what a rebuild produces. The practical consequence was that **CLAUDE.md was internally
inconsistent on this**: its research-corpus section opened with "**332 RECORDS, which are 319
DISTINCT WORKS**" while correcting itself to 382 fourteen lines below, so the stale figure was
the one a reader met first, and every session loads that file.
**FIXED 2026-08-25 04:2x in this session.** The opening line now states 382 as of 2026-08-25,
keeps the retired wording quoted and dated rather than deleted, and says to run `--stats`
rather than quote any pair including 382. The later dedup clause keeps "332 records / 319
works" as a RULE and retires it as a COUNT, because the duplicate census has not been re-run
against the 382-record index and no replacement works-figure exists. Do not derive one by
subtraction. [READ] Nothing in either 2026-08-22 document argues against any
of the three; what changes is that they are history, not pending decisions.

---

## What is not verified here

- **No adversarial review.** Consistent with both source documents, this pass was not checked
  by a second party. Every physics-adjacent claim it repeats inherits its source's
  **UNREVIEWED** status and this document does not lift it.
- **LS6 is unreachable from this session**, so its SU balance, its scratch purge exposure and
  the fate of the 2026-08-24 purge cohort are all unverified today.
- **J9's ReservePool defect** is reported from digest text, not from reading
  `simulation/openchannel_bc.py` and the pinned solver in this session.
- **The cluster audit's hold48s arithmetic** is relayed from the document. I re-ran only the
  SU balance, which is the one thing it told me to re-run.

*Written 2026-08-25. Read-only: nothing staged, committed or pushed.*


---

## Fixes applied, 2026-08-25, after this document was written

Applied in the working tree only. **Nothing staged, committed or pushed.**

| file | change |
|---|---|
| `CLAUDE.md` | Opening corpus figure corrected from the stale "332 RECORDS / 319 DISTINCT WORKS" to **382 records as of 2026-08-25**, with the retired wording quoted and dated rather than deleted. |
| `CLAUDE.md` | The dedup clause now retires "332 / 319" as a **count** and keeps it as a **rule**, and states that the duplicate census has not been re-run against the 382-record index. |
| `docs/R9_LOOP_CLOSURE_2026-08-22.md` | Dated `SUPERSEDED IN PART` banner listing the five corrected claims. No original text rewritten or deleted. |
| `docs/POSTER_AND_PIPELINE_STATUS_2026-08-25.md` | Section 1's verdict corrected: the shipped paper **does** disclose the splat gap, three times, so the second half of that verdict was withdrawn. |

**Deliberately not applied, and why.**

- **The poster (J3).** Excluded on instruction.
- **`analysis/hf_dataset_publish.py`'s `render_card()`**, which still writes the retired
  `odc-by`. It lives on `claude/r9-platform`, which is **unmerged and conflicted** on
  `hf_space/README.md` and `hf_space/app.py`. Fixing it means resolving that merge first, which
  is a landing decision, not an edit.
- **`CITATION.cff` on `origin/main`**, still `ODC-By-1.0`. Already `CC-BY-4.0` on
  `claude/add-ci-checks`; it reaches main by landing that branch, not by an edit.
- **`assets/LICENSE.md` (J5).** Writing it means asserting a licence for
  `hdri/kloofendal_43d_clear_puresky_2k.hdr`, which is Poly Haven naming and is covered by
  neither the CC0 identification nor, on its face, the emailed permission. That is J5's whole
  question and it is Josie's.
- **The paper abstract's closing "delivers a reconstruct-to-decide pipeline".** A wording
  judgement plus an Overleaf push, which needs explicit authorisation. Flagged, not touched.
- **`docs/SUBMISSION_STATUS.md`.** Poster-scoped, excluded on instruction. Its two answers are
  still blank under two commit messages claiming a human confirmation.
