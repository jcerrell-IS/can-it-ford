---
name: figure-pdfs-raster-vs-vector
description: "svg_to_paper_pdf.py has two paths, a JPEG-wrapper raster path and an rsvg-convert vector path; the raster path is why some Overleaf figure PDFs are 1600x1600 JPEGs, and captions are always native LaTeX, never baked into pixels"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8df1a68b-f8b8-4f11-b461-c1acf505fb7a
  modified: 2026-07-30T23:13:46.200Z
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
