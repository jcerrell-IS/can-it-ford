## YOUR SLOT: d12-kramerdata, branch `claude/r9-kramer-extract`, worktree `.claude/worktrees/r9-kramer-extract`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d12-kramerdata` first.

### What exists already, do not rebuild it

Your branch is based on `claude/r8-kramer`, so you inherit `simulation/r5_physics/kramer_benchmark.py` and `docs/R8_KRAMER_INTERCODE_2026-08-18.md` from a slot that finished last night. READ BOTH BEFORE YOU START. That slot established, from the Kramer 2021 supplementary `energies-14-00269-s001`:

- eleven codes, six independent groups, with RANS2 and RANS3 both Plymouth and LPF0 through LPF4 all by the paper's own first author via ditto marks
- the 05D envelope is -12.26 to +12.83 percent on damped period, and the entire width is contributed by the LPF group; RANS spans only -0.82 to +0.23
- RANS4 and RANS5 ship their gauge columns in REVERSED radial order, so read as shipped RANS4 appears to radiate more than its sphere lost
- row counts across series span a factor of 20, so fixed-width peak picking manufactures a PF-versus-RANS damping trend that is an artifact

That slot also WITHDREW its headline placement of Job B against this envelope. Do not restate the placement. Read the withdrawal in the document before you write anything that mentions Job B.

### The gap that is actually open

The supplementary holds 78 entries. Only the 28 experimental ones were extracted. **44 numerical entries plus 4 descriptions have never been extracted at all.** Everything above rests on the subset.

### Your unit

Extract the remaining entries and find out whether the conclusions survive contact with the full set. Specifically:

1. Build the extractor as a committed script, not as throwaway shell. It must be re-runnable by someone who was not here, and it must state which sheet and which columns each series came from.
2. For every conclusion in `docs/R8_KRAMER_INTERCODE_2026-08-18.md` that was drawn from the 28, say whether the full set confirms it, refines it, or refutes it. A refutation is a better outcome than a confirmation and should be written up with the same energy.
3. The reversed-column finding on RANS4 and RANS5 was established on the extracted subset. Check it against every series those two codes ship. If the reversal is universal, that strengthens the case for contacting the authors. If it is inconsistent across series, that is a much more serious finding and it changes what a reader can trust.
4. Do not derive gauge radii; measure them from the sheet as shipped, which is what the prior slot did and why its provenance is by spreadsheet rather than by folder.

The source data is at `/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001`, already extracted from the zip, with `PROVENANCE.txt` alongside. The licence is CC BY 4.0. You may read and quote it with attribution; check what the licence file actually says rather than trusting this sentence.

No GPU. `uv` provisions numpy, pandas, openpyxl and scipy in about fifteen seconds; the prior slot's module runs that way.
