---
name: figure-pdfs-raster-vs-vector
description: "svg_to_paper_pdf.py has two paths, a JPEG-wrapper raster path and an rsvg-convert vector path; the raster path is why some Overleaf figure PDFs are 1600x1600 JPEGs, and captions are always native LaTeX, never baked into pixels"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8df1a68b-f8b8-4f11-b461-c1acf505fb7a
  modified: 2026-07-31T00:32:02.509Z
---

`analysis/svg_to_paper_pdf.py` builds the paper's figure PDFs from hand-emitted
SVGs and has **two different output paths**:

- `build()` (raster): SVG -> `qlmanage` PNG -> `flatten_to_jpeg()` at quality 95
  -> a hand-assembled PDF wrapper around the JPEG. Produces a PDF whose only
  content is one big DCTDecode image.
- `build_vector()` (correct): shells out to `rsvg-convert -f pdf`, producing a
  true cairo vector PDF, typically 63-64% smaller.

The generators themselves (`paper_fig_l0l1_two_rules_v2.py`,
`paper_fig_l2_divergence_v2.py`, `paper_fig_mass_grid_sweep_v2.py`) are
**stdlib-only SVG emitters** because there is no system matplotlib on this Mac
(`python3 -c "import matplotlib"` fails). `plot_l1_three_class.py` is the
exception: it uses matplotlib and writes vector PDF directly, so it needs a venv
(`python3 -m venv`, `pip install matplotlib`) to run.

**Why:** on 2026-07-30 a forensic audit of the compiled PDF reported that Fig 1
and Fig 2 were "welded into one 1600x1600 JPEG with both captions drawn into the
pixels." That diagnosis was wrong and cost real time. Measured directly:
`pdftotext` recovers every caption as selectable text, so captions are native
`\caption{}`; and each image object is exactly one figure. The 1600x1600 object
was `l0l1_two_rules_v2.pdf` alone, with vector Fig 1 merely sharing the page.
Two figures on one page is not two figures in one image.

**How to apply:** to test this claim, never reason from page numbers. Run
`pdfimages -list` on the individual figure PDF, not on the compiled paper: zero
rows means pure vector. Confirm captions with
`pdftotext paper.pdf - | grep "<caption phrase>"`. To fix a raster figure,
prefer re-running `rsvg-convert -f pdf` on the existing SVG over redesigning the
figure, since the SVG already carries the approved layout. Related:
[[overleaf-tex-is-canonical]].

**Live state as built from `conference_101719_1.tex` (measured 2026-07-30):** 7
figures, 7 native captions, and only 3 image objects in the whole paper. Four
figures are already true vector. The two raster ones were Fig 3
(`L1_three_class_corrected.png`) and Fig 4 (`force_balance.jpg`); Fig 7 is a
legitimately raster MPM render. So "every figure is a flattened screenshot" was
never true of any build in the repo.

**Fig 4 had no generator at all.** `force_balance.jpg` was orphaned output with
no script behind it, which is why it could not simply be re-exported. Its legend
(N=2796 N, F_fric=979 N at 0.15 m) back-solves to **mu = 0.35**, a value matching
neither AR&R's 0.30 nor Azhar's 0.55, so any "reconcile 0.55 against 0.30"
framing was arguing about a number the figure never used. Replaced by
`analysis/paper_fig_force_balance_v2.py`, which asserts its own anchors and emits
vector in single- and double-column layouts. Note its buoyancy at 0.30 m is
**16.14 kN**, not the 15.99 kN the old caption quotes: the old model used an
effective plan area of 5.433 m2 (footprint 7.244 m2), while the sourced bbox
4.30 x 1.70 m over 0.75 gives 5.4825 m2. Caption needs that one number updated.
