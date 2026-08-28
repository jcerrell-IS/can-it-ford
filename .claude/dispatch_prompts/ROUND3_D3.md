# ROUND 3, D3 CREDENTIALS-HARD-STOP

Read `ROUND3_SHARED.md` first. Your scope is unchanged: **diagnosis only.** No
rotation, no revocation, no deleting an export line, no credential value in any
file. Your branch stays DO-NOT-PUSH. `ls-remote` empty is correct and must stay
correct.

## On the two things you reported against yourself

Both were the right call and both should stay in the document.

**The transcript leak.** Printing 70 characters of context to identify a key
name captured a complete Hugging Face token from the same `.env`. You abandoned
the technique and added HF_TOKEN to the revocation list. That is the correct
handling, and recording it is right because it demonstrates the mechanism better
than the argument did: investigating a credential exposure extends it.

Two consequences you have not yet drawn, and they are yours:

1. **This session's transcript is now a credential-bearing file.** It belongs in
   your inventory as a location, with its path, its mode, and whether it is
   iCloud-synced. You already have a precedent for this: the 0644 iCloud-synced
   token in the existing write-up. Add it.
2. **Adopt a matcher that cannot leak.** Never print surrounding context again.
   Emit only `path:line` and the variable NAME, never any part of the value, and
   never a fixed-width window around a match. Write the matcher so that the
   value is structurally unreachable, not so that you remember to avoid it.

**The discarded false zero.** A background prefix-grep returned 0 hits with exit
0 when three hits were already proven in `~/Documents`, and grep exits 1 on no
match. You threw it out. Correct, and it is the same failure class the shared
addendum records five instances of this round: an absent result from a partial
or broken view read as evidence of absence. Bank the rule, not just the
instance.

## Your next scope: finish the sweep, chunked

You swept 9 of 89 `$HOME` top-level directories and found three unknown
credentials in those nine. Your own conclusion is the right one: the other 80
cannot be assumed empty. A single run times out at 9m30s.

Chunk it. Concretely:

- Partition the 80 remaining roots into batches sized to finish well inside
  9m30s each. Measure one batch first and size the rest from that measurement,
  do not guess the batch size.
- Persist per-batch results to disk as each batch finishes, so a timeout costs
  one batch rather than the run.
- Record which roots were skipped and why (over 8 MB, cache, vendor tree), so
  the coverage floor stays stated rather than implied.
- `~/Downloads` is TCC-denied to some sessions and readable to others. Record
  its state at the time you sweep it, and if it is denied, say so as
  "unchecked", never as "clean". See shared section 1: this exact conflation
  produced five false negatives elsewhere today.

## The escalation Josie needs from you

You now count eight-plus outstanding credentials and **zero rotated**. That is
the number that matters and it is buried in prose. Produce, as a distinct
section at the top of your document:

> A numbered rotation list. One row per credential. Columns: which service,
> which file holds it, file mode, whether the location is cloud-synced, whether
> it is in git history, and the exact rotation URL or CLI command Josie runs.
> No values. Ordered by blast radius, worst first.

Josie performs every rotation. You produce the list and nothing else. State
plainly at the top that nothing has been rotated and the exposure is growing on
its own through backups and session transcripts.

## Skills and machine state

Call `directory-provenance-audit` for the sweep structure. No GPU, no
allocation, and none is needed. Vista queue empty at 641 SU; LS6 unreachable.

Five commits on the DO-NOT-PUSH branch, correctly unpushed. Main tree still 26.
