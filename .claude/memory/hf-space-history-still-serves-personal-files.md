---
name: hf-space-history-still-serves-personal-files
description: "Removing the ADHD/profile files from HEAD did not unpublish them; both HF and GitHub still serve them at old revisions, and the two need separate remediations"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8f984cdd-e1ce-4e58-a2a6-040a3a1c08ef
  modified: 2026-08-04T15:56:08.730Z
---

Verified live 2026-08-04. The three personal-profile files (`files/CLAUDE_md_CANONICAL_july13.md`,
`CLAUDE_md_FINAL_july13.md`, `CLAUDE_md_corrected_july13.md`, each carrying "WHO JOSIE IS", ADHD,
processing-speed and GPA content) are 404 at HEAD on both platforms but return HTTP 200,
unauthenticated, at historical revisions:

- HF Space `josiecerrell/can-it-ford` rev `4a9ba70c21aa710bd8909769df0a456bad4643a9`
- GitHub `jcerrell-IS/can-it-ford` commit `b141c48`

Byte-identical across both by sha256: `8f8b5f2a...e014c79`, `f48c1f54...ceaa025`, `245b8661...50f2739`.
Negative controls at the same revisions return 404, so these 200s are real content.

**Why:** the `git rm` on 2026-07-23 changed HEAD only. Both platforms serve any revision by sha,
so removal from HEAD unpublishes nothing. This is [[git-show-mangles-binary-blobs]]'s sibling
lesson: what a command *appears* to do to history is not what the hosting platform actually stops
serving.

**How to apply:** treat the HF Space and the GitHub repo as two independent exposures needing two
independent remediations. Making the GitHub repo private does nothing for the Space; making the
Space private does nothing for GitHub. Never conclude "the leak is fixed" from a HEAD-only check,
always probe a pre-removal revision with a negative control alongside. Also: `hf repo settings
--private` is silently ignored on an already-existing repo (its own `--help` says so), use the web
UI or `HfApi().update_repo_settings(..., private=True)` and verify by re-reading the API's
`private` field, never by exit code.

Related: the Space is also in `CONFIG_ERROR` because a GitHub sync overwrote its README front
matter; that is cosmetic next to this. Its `qr_gradio.png` encodes the Space URL exactly, but no
QR appears in the shipped poster `Cerrell_TACC_42x56.pdf`, so nothing distributed points at it.
