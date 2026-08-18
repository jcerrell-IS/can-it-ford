# R5-D1 unit 61: the bibliography moved under me, and my entry count was wrong

Date 2026-08-19. Branch `claude/r5-research`.
**Two findings: one where the world moved (good), one where I was wrong (mine).**

Unit 60 established that the live paper uses `deliverables/paper/overleaf/refs.bib`,
not `paper/can_it_ford_references_IEEE.bib`. Checking whether my bibliography
recommendations even target the file in use turned up both of the above.

---

## 1. NOT a false zero: the four fording papers were genuinely absent when I measured

Unit 45 reported the four novelty-guard papers as having **zero** presence in
`paper/can_it_ford_references_IEEE.bib`. They are in it now, as
`he2026vehiclewater`, `khapane2014wading`, `pazouki2016fording`,
`wasfy2015fording`, each with its DOI.

**I checked whether I had published a false zero. I had not.**

```
commit ffc05d9  2026-08-18 00:19:17 +0100  Josephine Cerrell
  "Cite the four prior vehicle-fording works, and the methods this repo now uses"
  paper/can_it_ford_references_IEEE.bib | 144 insertions

He DOI count at ffc05d9^  : 0
He DOI count at ffc05d9   : 1
```

My unit 45 ran at roughly 23:00 on 2026-08-17, **about eighty minutes before that
commit**. The zero was correct when measured.

**Three qualifications, because the temptation here is to claim credit.**

1. **I cannot show my finding caused it.** The timing is suggestive and the commit
   message matches the gap exactly, but that is correlation. Another session may
   have reached it independently.
2. **It is on a different branch.** `ffc05d9` is on `claude/add-ci-checks`, which
   the main checkout currently has checked out. **My branch does not contain it**
   (`git merge-base --is-ancestor` returns false).
3. **The entries are not cited.** All four are `\cite`d in **0** `.tex` files. So
   the bibliography gap has closed and the *citation* gap has not, which is exactly
   the distinction unit 45 was built on and erratum 4 records.

**So unit 45's finding stands as measured, its bibliography half has since been
addressed by someone else, and its sharper half is still open.**

## 2. RETRACTED SAME DAY: this was a BRANCH difference, not a regex bug

> **Unit 62 falsified this section within minutes of writing it, using the
> verification script written to catch exactly this.** The original text is kept
> below because the misdiagnosis is more instructive than the number.
>
> ```
> worktree claude/r5-research    9,503 bytes   naive 21   permissive 21
> main     claude/add-ci-checks 16,906 bytes   naive 36   permissive 36
> ```
>
> **Both regexes agree on both copies.** The file simply differs by branch:
> `ffc05d9` added 144 lines on `claude/add-ci-checks`, which my branch does not
> contain. **So "21 entries" was correct for this branch all along, my regex was
> never too strict, and the "fourth regex failure" I announced does not exist.**
> Units 51, 53 and 54 stand as regex failures; this one does not.
>
> The lesson that survives is the opposite of the one I drew: **a bare entry count
> is branch-dependent in a repo with concurrent sessions on different branches, so
> report the checkout alongside the number.** The script now refuses to assert
> either figure and prints which copy it read.

### Original text, WRONG, retained deliberately

**MY ERROR: the IEEE bib has 36 entries, not 21**

I have reported "21 entries" since unit 3, including in `WHAT_SURVIVES` A6 and in
the consolidated bibliography state in `BIB_DOI_SUPPLEMENT`.

```
python  re.findall(r'@\w+\{([^,]+),')   ->  36 entries
my grep -oE "^@[a-z]+\{[^,]+"           ->  21 entries
```

**The regex was anchored to line start and matched only lowercase entry types**, so
every `@Article{`, `@InProceedings{` and any indented entry was invisible. This is
the same failure mode as the friction count in unit 51, where a too-strict pattern
dropped a real value, and as the em-dash test in unit 53.

Corrected state of the two bibliographies:

| | entries | with `doi=` | with a doi.org URL | carrying `VERIFY` |
|---|---:|---:|---:|---:|
| `deliverables/paper/overleaf/refs.bib` (live) | **11** | 10 | 8 | **0** |
| `paper/can_it_ford_references_IEEE.bib` | **36** | 23 | 0 | **9** |

## 3. My bibliography recommendations mostly target the file NOT in use

Only **six keys are shared** between the two: `azhar2023`, `kramer2016`,
`shand2011`, `xia2010`, `xia2013`, `xiong2024`.

**Three of my bibliography findings concern entries the live paper does not have:**

| my finding | in live `refs.bib`? |
|---|---|
| `ccsa2010yaris` year is 2016, not 2010 (A6) | **absent** |
| `alqadami2022` has a `{{VERIFY: exact title}}` placeholder | **absent** |
| `martinezgomariz2018` referent is unsettled (FLAG-4) | **absent** |

**The live bibliography carries zero `VERIFY` markers at all.** All nine are in the
IEEE file.

**This does not make those findings wrong**, and the IEEE bib is clearly still being
worked on (144 lines added to it yesterday). But their priority is different from
what I implied: they are corrections to a file that the current paper does not
compile from, and I should have established which bibliography was live before
spending three units on the other one.

## 4. Status

UNVERIFIED:
1. **Which bibliography is canonical is still unresolved.** The live paper source is
   gitignored (unit 60), the IEEE bib is tracked and actively edited, and the real
   Overleaf head is unreachable (FLAG-6).
2. I have not re-derived every count in `BIB_DOI_SUPPLEMENT` against the corrected
   36-entry figure. The four verified DOIs and the `ccsa2010yaris` year error are
   unaffected, because both were checked per entry rather than by the total.
3. I cannot establish causation for `ffc05d9`, only sequence.
4. Whether the four new entries *should* be cited in the text is editorial.
