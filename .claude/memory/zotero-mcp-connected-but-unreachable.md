---
name: zotero-mcp-connected-but-unreachable
description: "Zotero MCP reports \"Connected\" and a library item count even when Zotero desktop is closed, and every search then silently returns empty instead of erroring"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bf457dae-d4f4-4ee4-83af-0a4635dc08b1
  modified: 2026-07-31T22:25:30.097Z
---

`claude mcp list` showing `zotero: zotero-mcp - ✔ Connected` only proves the MCP
process started. It does NOT prove the library is readable. Verified live
2026-07-31: Zotero desktop was not running, port 23119 was closed, and yet
`zotero_list_libraries` still returned "My Library, 37 items" from a cached read.

The failure is silent and asymmetric:
- `zotero_search_items` returns `No items found matching query` for EVERY query,
  including the single letter `a`. It reads as "not in your library", not as an error.
- `zotero_get_recent` and `zotero_advanced_search` return `[Errno 61] Connection refused`.

So a search-only check produces a confident, completely wrong conclusion: that the
bibliography is absent from Zotero. Before trusting any Zotero result, confirm both:

```bash
pgrep -x Zotero && nc -z -G 2 127.0.0.1 23119 && echo "zotero readable"
```

Fix is to launch Zotero desktop, then Settings, Advanced, "Allow other applications
on this computer to communicate with Zotero".

Fallback verification path that does work offline: the canonical bib on
`overleaf/main` plus the primary PDFs in `citations/` (the AR&R Stage 2 report is
there in full). See [[overleaf-tex-is-canonical]] and [[arr-isbn-and-table3-are-verified]].
