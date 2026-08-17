# R5-D1 unit 29: sweeping the non-catalog corpus, and a third filter defect of my own

Date 2026-08-17. Branch `claude/r5-research`. Data:
`data/r5_citation_noncatalog_prose.tsv`, 109 rows.

Unit 27 mined one non-catalog corpus document by hand and found two real gaps.
This is the systematic version: extract every DOI from the corpus's **prose**
documents, the ones that are not paper catalogs, and cross-reference them the way
unit 1 did for the catalogs.

**Headline: the corpus prose contains 109 DOIs that appear in no catalog at all,
and 88 of them are cited nowhere in the repo.**

---

## 1. A filter defect of mine, caught before reporting

My first pass reported "137 new DOIs, 101 uncited". **Both numbers were wrong**,
and I nearly posted them.

The DOI regex was capturing two kinds of junk:

- **Bare journal stubs.** `10.1007/s11069` and `10.1111/jfr3` are journal
  prefixes that appear in prose as partial references. Worse, because the
  cross-reference is a substring match, `10.1111/jfr3` matched **47 repo files**,
  since it is a substring of every real DOI in that journal. That single artifact
  would have inflated the "cited" count on its own.
- **Markdown and punctuation tails.** `10.1111/jfr3.12527**`,
  `10.13021/g8js5d.**`, `10.1177/02783649231221580”` are the same DOIs wearing
  bold markers and a curly quote.

My first fix then **over-corrected**: a rule dropping any DOI that is a prefix of
another removed `10.1111/jfr3.12527` and `10.1080/1573062x.2017.1301501`, which
are real, because their markdown-decorated twins survived cleaning. I only found
that by printing what each rejected DOI was supposedly a prefix *of*.

Final cleaner: strip trailing `} ) ] * . , ; : > " ' _` and curly quotes
repeatedly to a fixed point, require at least 6 characters after the slash with a
digit in them, then drop strict prefixes. After that, exactly **one** DOI is
rejected as a prefix, `10.1007/s11069`, which is the genuine stub.

This is the third filter defect I have caught in my own work, after the `\bcar`
boundary bug that matched Carlisle and Carolina (unit 5) and the contaminated
pool behind the withdrawn 27.1% (also unit 5). The pattern is consistent enough
to be worth stating as a rule: **a regex over a heterogeneous corpus needs its
rejects printed, not just its accepts.** Both of my errors here were visible only
in the rejected set.

## 2. The measurement

```
corpus prose documents carrying at least one DOI :  92
unique clean DOIs in them                        : 162
  already in the 489-DOI catalog corpus          :  53
  NOT in any catalog                             : 109
    cited anywhere in the repo                   :  21
    reaching paper/ overleaf_sync/ deliverables  :   5
    UNCITED                                      :  88
```

So the project's own research corpus carries **109 DOIs that no Undermind catalog
contains**, and **88 of those are cited nowhere**. That is a further, independent
confirmation of unit 3's finding that the catalogs are not a census, reached from
a different direction: not by citation-graph traversal, but by reading what the
project's own prose documents cite.

Combined with earlier units, the running total of catalog-absent material is now
109 from prose plus the 28 from graph and author sweeps.

## 3. Where the citation-rich prose documents are

Ranked by catalog-absent DOIs contributed:

| new DOIs | document |
|---:|---|
| 25 | `05_Abstraction_Ladder_Framing_and_Positioning/combined_SET_C_kumar_pvwm_reference.md` |
| 20 | `01_Solver_Physics_and_Coupling/combined_SET_B_genesis_mpm_parameters.md` |
| 18 | `10_Claude_Code_Session_Transcripts/Untitled 3.txt` |
| 16 | `_BUILD_LOG/sprint3_loose_extract_batch2.txt` |
| 7 | `04_Validation_Literature_and_Citations/Ground-Material Friction and Road-Camber Physics...` |
| 7 | `03_Gaussian_Splatting_and_Reconstruction/2026-08-12_readme_flood-render-realism-optics...` |
| 7 | `02_Vehicle_Geometry_and_Mass/GNN Surrogates for Fluid-Rigid Coupling & NCAC/CCSA Vehic...` |

Two of these are pointed straight at live project questions and are worth reading
before the rest:

- **`Ground-Material Friction and Road-Camber Physics`**, 7 catalog-absent DOIs.
  Friction is the parameter this dispatch has spent the most units on
  (`floor_friction = 0.55`, the 0.3-assumed finding, Nihei's brake state), and a
  document specifically about ground-material friction has never been opened.
- **`GNN Surrogates for Fluid-Rigid Coupling & NCAC/CCSA Vehicle...`**, 7
  catalog-absent DOIs. It touches both the coupling question and the NCAC/CCSA
  geometry provenance that register E8 and unit 16 section 5 turn on.

`combined_SET_C_kumar_pvwm_reference.md` tops the list at 25, and unit 27 already
established that its positioning conclusions are canonical as register G12 and
G13. Its 25 DOIs are a separate matter and are in the data file.

## 4. Status

UNVERIFIED:
1. **88 files were skipped** as oversize or unreadable, including an 86,000-line
   session transcript. Their DOIs are not in this sweep, so 109 is a floor.
2. **None of the 109 has been verified against a registering agency**, and none
   has been read. This is an inventory, not an assessment.
3. The "cited anywhere" column is the same DOI-string method unit 28 audited: it
   means no DOI-string match in the repo, not "unknown to the project". Unit 28
   found that distinction matters for at least one paper.
4. I swept only the Desktop corpus root. `corpus_inventory` lists five others,
   including `~/Downloads` at 591 files, which are not covered here.
5. The two documents flagged in section 3 are flagged on their titles and DOI
   counts. I have not opened either.
