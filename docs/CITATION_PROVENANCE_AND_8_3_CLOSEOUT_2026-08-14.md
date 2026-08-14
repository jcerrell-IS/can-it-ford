# Primary citation set: what is actually on disk, and 8.3 closeout

2026-08-14. Read-only survey. **This establishes WHAT IS THERE, not what the sources say**:
D2 owns reading the ARR and WRL documents for the depth-versus-DxV question, D7 owns
indexing the corpus, D11 owns ranking Smith 2019. Nothing outside this branch was written
and no corpus file was modified.

---

# TASK 1, provenance of the primary citation set

## Access constraint, stated first because it shapes everything below

`~/Downloads` is **unreadable to this session at the OS level**, not the sandbox level.
`ls`, the Read tool, and a sandbox-disabled shell all return `EPERM: Operation not
permitted`. That is macOS TCC, and only Josie can grant it. Readability of the four named
research locations, tested live:

| location | state |
|---|---|
| `~/Downloads` | **BLOCKED (EPERM)** |
| `~/Documents` | readable, 278 entries |
| `~/Desktop` | readable, 29 entries |
| `~/Claude` | readable, 4 entries |

So the exact paths in the task could not be opened. The second route works and is
arguably better: **the same citation set is committed inside the repo** at
`/Users/josie/can-it-ford/citations/`, 38 files tracked by git, not ignored
(`check-ignore` exits 1), added by commit `37b9c1a` "Add citations evidence folder".
Everything below is read from that tracked copy. **I could not verify byte-identity
between the repo copy and the `~/Downloads` copy**, and do not claim it.

## `citations/ARR_Project_10_Stage2_Report_Final.pdf` — it is a real report

29 pages, 1,115,134 bytes, md5 `88090492e1c3e53dae6493efed1eef2e`. Identity read off
pages 1-3, not inferred:

- **Australian Rainfall & Runoff, Revision Projects, Project 10: Appropriate Safety
  Criteria for Vehicles — Literature Review, STAGE 2 REPORT**
- Report number **P10/S2/020**, dated **21 February 2011**
- **ISBN 978-0-85825-948-5**
- Contractor **Water Research Laboratory**, UNSW, Manly Vale NSW 2093, ref 10023.01
- Authors **T D Shand, R J Cox, M J Blacka, G P Smith**; Engineers Australia, Water
  Engineering; funded via the Department of Climate Change

**A trap worth recording, because I nearly filed the wrong answer.** The PDF's own
metadata is misleading: `kMDItemTitle` is `"Slide 1"` and `kMDItemAuthors` is
`"Microsoft® Office PowerPoint® 2007"`. Read from metadata alone this looks like a
29-slide deck, and I initially recorded it as one. Opening the pages refutes it: page 1 is
a designed cover, page 2 is the formal title block with the ISBN, page 3 is the
acknowledgements. **Metadata described the cover's authoring tool, not the document.** Any
audit that classifies these PDFs by `mdls` will misclassify this one.

This also independently confirms, from the primary artifact, that the ISBN is printed in
the PDF held in `citations/`.

`citations/ARR table 1 - ... vehicle stability.png`: 1018x1252, 237,832 bytes, md5
`96a9c4eeef962c2f9ab05ef7ead048b5`. **Not opened**: what that table says is D2's.

## `citations/Smith-Modra-Felder/` — the full text is there, as page images

**This is the highest-value item for D11.** The directory holds **16 PNG, 6,215,623 bytes
total**, all tracked in git. It is **not** a PDF and **not** a set of notes:

- **15 screenshots are the complete published article, pages 1 through 15.** Captured
  2026-07-03 between 3:15:26 PM and 3:16:16 PM, one page every 3 to 5 seconds. Verified by
  opening both ends: the first is page 1 with the title block, the last is footered
  "15 of 15" and carries the reference list and the publisher's own "How to cite this
  article" box.
- **`smith2019_instability_table.png` is misnamed.** It is **Figure 10 from page 12 of
  15**, a plot, not a table: *"Vehicle stability curves and comparison with Australian
  Rainfall and Runoff curves (Shand et al., 2011); use of average drag coefficient
  C_D = 1.38 and varying friction coefficients."* Its legend names the three tested
  vehicles as **Yaris, Patrol and Festiva**, at C_D = 1.38 with two friction cases,
  0.78 and 0.3. Recorded as identification; what it implies is D11's and D2's.

Bibliographic record, read off page 1 and confirmed against the page-15 citation box:

```
Full-scale testing of stability curves for vehicles in flood waters
Grantley P. Smith, Benjamin D. Modra, Stefan Felder
Water Research Laboratory, School of Civil and Environmental Engineering,
  UNSW Sydney, Manly Vale NSW 2093, Australia
J Flood Risk Management. 2019;12 (Suppl. 2):e12527
DOI 10.1111/jfr3.12527
Received 19 June 2018 | Revised 19 November 2018 | Accepted 29 January 2019
Funding: NSW Office of Environment and Heritage; NSW State Emergency Service
15 pages
```

### A citation defect D11 must not inherit

`citations/README.md:17` records the title as *"Full-scale testing of **vehicle floating
and sliding in flowing floodwater**"*. The paper's own title page and the publisher's
"How to cite this article" string both read *"Full-scale testing of **stability curves for
vehicles in flood waters**"*. **The README title is wrong.** The DOI it gives,
`10.1111/jfr3.12527`, is correct, so anything keyed on DOI is safe and anything keyed on
the README's title string is not. The README also gives the authors as initials only
("Smith, G., Modra, B., & Felder, S.") against Grantley P. Smith, Benjamin D. Modra,
Stefan Felder.

Not fixed here: `citations/README.md` is a shared file and no dispatch owns it, so per the
standing ops rule this is written as a request rather than an edit. **Owner needed for a
one-line title correction at `README.md:17`.**

## The two WRL copies — the question has a different answer than expected

The task asked whether the two WRL copies are byte-identical or divergent. **They are
neither, because they are not two files.** In the research corpus both are **symlinks**:

```
wrl-flood-hazard-techinical-report-september-2014.pdf
  -> /Users/josie/Downloads/wrl-flood-hazard-techinical-report-september-2014.pdf   LIVE
wrl-flood-hazard-techinical-report-september-2014 2.pdf
  -> /sessions/rcw-018wosspwdgoivwo35h8ibzj/mnt/Downloads/wrl-flood-hazard-...pdf   BROKEN
```

The apparent "duplicate" is a **dangling link into a defunct session mount**, pointing at
a path that no longer exists. `stat` reports them as 76 and 106 bytes, which are the
lengths of the target strings, not file sizes. So there is one real file behind one link,
and nothing at all behind the other.

**Ten real copies exist elsewhere and all ten are byte-identical**: md5
`3a8d95a2bc4fc459f0d69f167cebf34d`, 2,821,346 bytes, nine under
`~/Desktop/_ARCHIVE_2026-07-26/…` and one at
`~/Documents/CAN_IT_FORD_ARCHIVE_2026-07-17/research_reports_and_citations/source_pdfs/`.
No divergence anywhere reachable.

**Still unverified**: the `~/Downloads` original itself, because of TCC. Ten independent
copies agreeing makes divergence unlikely, and that is not the same as checked. To close
it, Josie can run:

```
md5 -q ~/Downloads/wrl-flood-hazard-techinical-report-september-2014.pdf
# expect 3a8d95a2bc4fc459f0d69f167cebf34d
```

`citations/WRL reports technical and Research/` in the repo holds **no PDF at all**: three
PNG captures only (Figure 5-5, Table 5-1, Table 5-2).

## A structural finding about the research corpus, for D7

Measured, not sampled, on `~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/`:

| | count |
|---|---|
| regular files | **71** |
| symlinks | **388** |
| of those, live | 278 |
| of those, **broken** | **110** |

The broken links point at `/sessions/rcw-018wosspwdgoivwo35h8ibzj/mnt/Downloads` (102),
the same session's `mnt/Desktop` (7), and `~/Downloads/canitford_tex_backup_2026-08-02`
(1). Of the 278 live links, **153 resolve into `~/Downloads`**, which is TCC-blocked, so
any process without that permission sees them as unreadable rather than missing.

**Consequence for any file-count inventory, including the 264-candidate figure**: the
corpus *holds* 71 files and *points at* 388, and a quarter of the pointers resolve to
nothing. Counting entries overstates what is actually preserved there. Reported, not
acted on: D7 owns that tree.

## A provenance caution that spans all three documents

These are not three independent sources. They are one laboratory:

- ARR P10 Stage 2 (2011): authors Shand, Cox, Blacka, **Smith** — Water Research
  Laboratory, UNSW
- Smith, Modra, Felder (2019): Water Research Laboratory, UNSW, first author **Grantley P.
  Smith**
- WRL flood hazard technical report (2014): Water Research Laboratory

and the link is explicit in the primary text rather than inferred: the 2019 paper's own
reference list cites *"Shand, T. D., Cox, R. J., Blacka, M. J., & Smith, G. P. (2011).
Australian rainfall and runoff revision project 10 … (Stage 2 Report)"*, the very PDF
sitting one directory above it. Against this project's own rule that one source cited
twice is not two sources, agreement between the ARR thresholds and Smith 2019 is **not**
independent corroboration. Whether that matters to any specific claim is D2's and D11's
call, not mine.

---

# TASK 2, closeout of dispatch item 8.3

Re-verified live on **login2.vista.tacc.utexas.edu** at 18:2x CEST. No GPU node touched:
node 911518 is D13's, and all of this is `git` and filesystem work, which belongs on the
login node.

**(a) Does `a231a73` still resolve on Vista?** **Yes, and it is still dangling.**

```
git cat-file -t a231a73                       -> commit
git branch -a --contains a231a73              -> (empty)
git merge-base --is-ancestor a231a73 HEAD     -> NO
```

It resolves as an object, no ref contains it, and it is not an ancestor of the branch. It
is a pre-rebase copy sitting on a different parent, and it carries nothing unique:
`git patch-id --stable` returns `8079edb9e4427b5b8dbde9570e0199d5685fbe9e` for both
`a231a73^..a231a73` and `77d11d4^..77d11d4`. **The dispatch's description of the work as
being "at local commit a231a73" is wrong as to the tip.** The tip is `09d2b8f`, and
exactly two commits were ever unreachable: `09d2b8f` and `77d11d4`. `a231a73` will
disappear at the next `gc`, and losing it costs nothing.

**(b) Did the branch reach any remote?** **It had not; it has now.**

At the time 8.3 was written, `git ls-remote --heads origin` carried no
`track1/sdf-6dof-driver`. It was recovered earlier today by bundling from Vista `$WORK`
(sha256-verified on both sides), fetching into the Mac clone, and pushing. Confirmed from
Vista's own side during this check:

```
git fetch origin --prune
  * [new branch]  track1/sdf-6dof-driver -> origin/track1/sdf-6dof-driver
git rev-list HEAD --not --remotes=origin      -> (empty)
git ls-remote --heads origin track1/sdf-6dof-driver
  09d2b8fb1763ca85ef3e53d4fc71a7d135e126b5  refs/heads/track1/sdf-6dof-driver
```

Vista's clone had never seen the branch on a remote until this fetch, which is the
cleanest available evidence that the push, not a pre-existing copy, is what put it there.

**8.3 is closed.** `simulation/rigid6dof.py`, `tests/test_rigid6dof.py`,
`docs/TRACK1_6DOF_DRIVER_2026-08-13.md` and `run_c4_free_sdf`
(`simulation/validate_coupling_force.py:851`) are all reachable from origin at `09d2b8f`.

One claim stays open and is marked rather than closed: **"25/25 tests passing" is verified
as to the count and unverified as to passing.** 21 `def test_` functions plus one
`@pytest.mark.parametrize` carrying 5 cases collects as 25. It has never been executed
here: Vista's system `python3` has no `pytest` and `$HOME` is 89.15% full, so no install
was attempted.

Incidental, observed in the same fetch and worth one line: Vista also picked up
`claude/rtfd-test-phase-1-4-569130` as a new origin branch, so Dispatch 1's g128 rescue
has landed on the remote too.
