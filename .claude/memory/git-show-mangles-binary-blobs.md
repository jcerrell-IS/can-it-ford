---
name: git-show-mangles-binary-blobs
description: "REFUTED 2026-07-31: git show does NOT corrupt PDFs in this repo. text=auto skips any file with a NUL in the first 8000 bytes, and PDFs have one. The 38217-vs-38926 mismatch was two genuinely different figure revisions"
metadata: 
  node_type: memory
  type: reference
  modified: 2026-07-31T23:06:46.483Z
  originSessionId: 41bfdfd2-0add-4570-8b4c-31203e380cdd
---

**This memory previously claimed `git show <rev>:<file>.pdf` silently corrupts
binary output in `/Users/josie/can-it-ford`. That claim is false.** Retested live
2026-07-31 with git 2.50.1 (Apple Git-155).

The `.gitattributes` observation was accurate: `* text=auto` was set with no
`*.pdf binary` rule, and `git check-attr -a` did report `text: auto`. The
*consequence* was wrong.

**Why no corruption happens.** `text=auto` means auto-detect, not force-text. Git
classifies a buffer as binary if it finds a NUL in the first 8000 bytes and then
skips all conversion. `pipeline_diagram_v2.pdf` has its first NUL at offset 249,
so git treats it as binary regardless of the missing rule. Verified directly:

```
git show overleaf/main:pipeline_diagram_v2.pdf | md5
git cat-file blob 2949b7f9c6b262e6f69c228e0478ec659305c1ef | md5
```

Both give `3ee0c47e1c14a486c435efb9da6b1736` at 38926 bytes. Identical.
`core.autocrlf` and `core.eol` are unset here, so checkout does no conversion
either.

**What the 38217-vs-38926 mismatch actually was.** Three distinct blobs share the
name, and the audit compared two of them:

- `6b96b391` 38217 B at `paper/figures_review/pipeline_diagram_v2.pdf` (this is HEAD)
- `6eb6fb54` 38926 B at `paper/figures_review/pipeline_diagram_v2.pdf`
- `2949b7f9` 38926 B at flat `pipeline_diagram_v2.pdf` on `overleaf/main`

Rendering settles it: HEAD's copy labels stage 4 **"Genesis MPM"**, the
`overleaf/main` copy labels it **"Warp MPM"** (relabeled in `e312809`). They were
never the same file. The CRLF theory also fails arithmetically: the 38217 blob
holds 405 LFs, so full CRLF expansion would reach 38622, not 38926.

The two same-size blobs (`2949b7f9` vs `6eb6fb54`) differ in only 566 bytes, all
inside the trailing FlateDecode object stream and XRef, with `startxref` 38616 vs
38615. That is PDF generator nondeterminism, embedded timestamp or `/ID`, not
encoding damage.

**Standing lesson, which survives the refutation.** Compare binaries by blob hash,
`git rev-parse <rev>:<path>`, since it is cheap and conversion-proof. But confirm
that two paths hold the *same* blob before blaming the transport. A size delta
between two paths is evidence of different content first, and of tooling second.

`*.pdf binary` and friends were added to `.gitattributes` anyway, as hygiene:
explicit beats sniffing for any future PDF lacking an early NUL, and `binary`
implies `-diff` and `-merge`. All 47 committed PDFs were rendered with pdfinfo and
pdftoppm at that time: zero failures, none corrupt.

Related: [[figure-pdfs-raster-vs-vector]], [[gated-runs-are-warpmpm-not-genesis]].
