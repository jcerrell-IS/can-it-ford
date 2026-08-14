# `register_integrity.py` calls 11 register citations possibly fabricated. None is.

2026-08-14, measured live. **No file was edited.** `register_integrity.py` is a shared
checker that D4's definition of done depends on, so this is a diagnosis plus a proposed
patch, not a change.

## What the checker currently reports

```
hex tokens   30 cited: 15 git, 4 upstream-pinned, 0 research-artifact, 11 unresolved
blocking defects  0
```

Each of the 11 gets a WARN saying it *"resolves as none of: a git object in this clone, an
upstream pinned solver SHA … or a research artifact at
`~/Downloads/compass_artifact_wf-<id>-*`. It may live on an unfetched remote, or it may be
**fabricated**."*

**Zero of the 11 are fabricated.** Ten are real files on this machine. The eleventh is a
correctly-cited hash of a kind the checker has no category for.

## Result, per token

| id | real file at `~/Claude/reu/` | verdict |
|---|---|---|
| `045982be` | yes | real research artifact |
| `211aad60` | yes | real research artifact |
| `266e9a8a` | yes | real research artifact |
| `289743f7` | yes | real research artifact |
| `5e706c91` | yes | real research artifact |
| `63a4b5d4` | yes | real research artifact |
| `65474f37` | yes | real research artifact |
| `b0d2664f` | yes | real research artifact |
| `baa355db` | yes | real research artifact |
| `c963203d` | yes | real research artifact |
| `185968e0` | no | **not an artifact id at all**, see below |

Scope of that claim, stated because it is narrower than it looks: **a file with that id
exists at that path.** I did not open the ten and confirm their contents match what the
register cites them for. Existence kills the fabrication hypothesis; content
correspondence is a separate check and has not been done.

This independently reproduces register **K0** (line 648), which recorded on 2026-08-08
that *"All ten ids cited in this register resolve."* Ten then, ten now. The count matches
exactly, which also tells us the eleventh token entered the register after K0 was written.

## Defect 1: one hardcoded directory, and a silent failure mode

`register_integrity.py:60-62`, re-derived with `/usr/bin/grep -n`:

```python
RESEARCH_ARTIFACT_GLOB = os.path.expanduser(
    "~/Downloads/compass_artifact_wf-%s-*_text_markdown.md"
)
```

used at `:244`, with the path repeated in the warning text at `:340`.

`~/Downloads` is unreadable to at least some sessions at the OS level (macOS TCC). The
failure is silent, and that is the part that matters:

```
os.path.isdir('~/Downloads')  ->  True          # so no "directory missing" signal
glob.glob('~/Downloads/compass_artifact_wf-b0d2664f-*')  ->  []   # empty, NO exception
```

So the checker cannot distinguish **"the file is absent"** from **"the directory is
unreadable"**, and reports the second as the first. Every research-artifact lookup fails
at once, which is exactly the observed `0 research-artifact`. The warning then directs the
reader to the one path they cannot open.

The same ids resolve immediately one directory over:

```
~/Claude/reu/compass_artifact_wf-b0d2664f-3b65-5bfe-8e3f-f06e77a59f79_text_markdown.md
```

**Counts, stated precisely, because I got this wrong once today and am correcting it.**
`~/Claude/reu/` holds **40 files matching the artifact pattern, 34 distinct ids, 6
duplicate copies**. An earlier figure of 208 in this session came from a looser
`find -iname "compass_artifact*"` across four roots including Desktop and Documents
archive snapshots; 208 is the correct answer to that wider question and the wrong answer
to "how many artifacts are in `~/Claude/reu`". K0 recorded 33 on disk on 2026-08-08
against 34 distinct today.

## Defect 2: a fourth kind of hex token with no category

`185968e0` is the one that does not resolve as an artifact, and it should not: it is not
an artifact id. In the register it is cited as a **file content hash**:

> `realism_track/FINDINGS.md` had also diverged on both clones from a shared base
> (`02f08eb` = `cdcdf9d`, sha256 `185968e0`)

The checker's own comment block at `:50-58` enumerates exactly four kinds of hex token:
git object, upstream pinned SHA, research artifact, unresolved. A **truncated sha256 of a
file's contents** is a fifth kind, and it can never resolve as any of the first three, so
it is permanently mislabelled as possibly fabricated. I am claiming only its category,
which the citation context makes unambiguous; I did not recompute the hash.

## Proposed patch, not applied

Ownership: `register_integrity.py` is on nobody's list, and D4's definition of done runs
it. Changing its output mid-flight while D4 reconciles three register versions would
muddy D4's results, so this is left for the owner to apply.

1. **`:60-62`** — replace the single glob with a root list and try each:
   `~/Downloads`, `~/Claude/reu`. Both are real locations for the same files.
2. **Add a readability probe** before concluding "unresolved". If a root satisfies
   `os.path.isdir(root)` but not `os.access(root, os.R_OK | os.X_OK)`, report it as
   **unreadable, permission denied** and say which root. A checker that cannot read a
   directory must not report its contents as missing, and must never escalate that to
   "may be fabricated".
3. **`:340`** — make the message name the roots actually searched, rather than one
   hardcoded path.
4. **Add a fifth token category, content-sha256**, or exempt tokens whose citation
   context already says `sha256`, so `185968e0` stops reading as suspect.

Until 1 and 2 land, **treat a `research-artifact` count of 0 as a broken probe, not as
evidence about the register.**

## Why this matters beyond the tooling

The warning text is unusually persuasive: *"A fabricated SHA reads exactly like a real
one, so resolve it before citing it as evidence."* That is good advice and it is currently
attached to ten citations that are fine. The standing risk is that a session acting on
these warnings deletes or softens ten real, resolvable register citations. Two of the ten
are directly load-bearing elsewhere: `65474f37` is the provenance audit for the friction
coefficient that is the canonical `floor_friction`, and `5e706c91` is the forensic code
audit of friction in the vendored engine against this repo.
