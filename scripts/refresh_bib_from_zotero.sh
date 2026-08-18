#!/bin/bash
# Regenerate the paper bibliography from Zotero via the Better BibTeX HTTP endpoint.
#
# Why this exists rather than a BBT "keep updated" auto-export:
#   - BBT auto-export config lives in BBT's internal DB, is GUI-only, and silently
#     froze a stale copy on 2026-08-17 (keepUpdated was false, and skipFields was
#     not applied to the run).
#   - This path is reproducible, greppable, and validates before it overwrites.
#
# The validation that matters: every key cited by the paper's .tex MUST appear in
# the export. A bare entry count cannot catch a wrong collection; set membership can.
#
# Requires Zotero desktop RUNNING (BBT serves the endpoint from the local DB).
# NOTE: the local DB lags web-API edits by roughly 10-60s. If you just changed
# metadata via the API, wait before trusting the output.
#
# Usage:  refresh_bib_from_zotero.sh [--force] [output.bib]
#         --force is required to overwrite an existing output file.

set -euo pipefail

REPO="/Users/josie/can-it-ford"
TEX_REF="overleaf/main:conference_101719_1.tex"   # canonical source of \cite{} keys
COLLECTION="6FSSIWN2"                             # "Paper cited - IEEEtran"
PORT=23119
KEEP_BACKUPS=5
SKIP='^[[:space:]]*(abstract|file|langid|urldate|keywords|shorttitle|primaryclass|eprint|archiveprefix|annotation) = '

FORCE=0
OUT=""
for a in "$@"; do
  case "$a" in
    --force|-f) FORCE=1 ;;
    -*)         echo "unknown option: $a" >&2; exit 2 ;;
    *)          OUT="$a" ;;
  esac
done

STAMP="$(date +%s)-$$"        # pid suffix: two runs in the same second must not collide
RAW=""; CLEAN=""; TMPOUT=""
cleanup() { rm -f "$RAW" "$CLEAN" "$TMPOUT"; }
trap cleanup EXIT             # every die() path below is now leak-free

die() { echo "FAIL: $*" >&2; exit 1; }

# ---- pre-flight -------------------------------------------------------------

# Probe Better BibTeX specifically, not "anything answering HTTP on this port".
# A JSON-RPC reply proves BBT itself is loaded and initialised.
probe=$(curl -s -m 5 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","method":"system.ping","params":[],"id":1}' \
        "http://127.0.0.1:$PORT/better-bibtex/json-rpc" 2>/dev/null || true)
case "$probe" in
  *jsonrpc*) : ;;
  *) die "Better BibTeX is not answering on port $PORT. Open Zotero, wait for it to finish loading, and retry." ;;
esac

if [ -n "$OUT" ]; then
  OUTDIR=$(dirname "$OUT")
  [ -d "$OUTDIR" ] || die "output directory does not exist: $OUTDIR"
  [ -w "$OUTDIR" ] || die "output directory is not writable: $OUTDIR"
fi

# Expected keys come from the paper itself, not a hand-maintained integer.
CITED=$(git -C "$REPO" show "$TEX_REF" 2>/dev/null \
        | grep -aoE '\\cite[tp]?\{[^}]*\}' \
        | sed -E 's/^\\cite[tp]?\{//; s/\}$//' \
        | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' \
        | grep -av '^$' | sort -u) || true
[ -n "$CITED" ] || die "could not read \\cite{} keys from $TEX_REF (is the overleaf remote fetched?)"

# ---- fetch ------------------------------------------------------------------

RAW=$(mktemp -t bbtraw)
URL="http://127.0.0.1:$PORT/better-bibtex/export?/library;id:1/collection;key:$COLLECTION/r$STAMP.bibtex"
curl -sf -m 60 "$URL" -o "$RAW" || die "export endpoint returned an error"

grep -q '^@.*{zotero-item-' "$RAW" && die "an entry exported with a placeholder key (zotero-item-N): incomplete metadata."

# BibTeX, not BibLaTeX. IEEEtran.bst cannot read date=/journaltitle=.
grep -qE '^[[:space:]]*(date|journaltitle) = ' "$RAW" \
  && die "BibLaTeX fields present. Endpoint must end in .bibtex, not .biblatex."

# ---- strip and validate -----------------------------------------------------

CLEAN=$(mktemp -t bbtclean)
grep -vE "$SKIP" "$RAW" > "$CLEAN"

# Line-oriented stripping is only safe while every field value closes on its own
# line. Assert that rather than assume it.
ob=$(tr -cd '{' < "$CLEAN" | wc -c | tr -d ' ')
cb=$(tr -cd '}' < "$CLEAN" | wc -c | tr -d ' ')
[ "$ob" = "$cb" ] || die "unbalanced braces after strip ($ob open, $cb close): a field value spanned multiple lines."

# Guard on the field that carries filesystem paths, not on one host's home prefix.
grep -qE '^[[:space:]]*file[[:space:]]*=' "$CLEAN" \
  && die "a file field survived the strip; it would leak local paths."

# THE check: every cited key must be present. Extra entries are harmless because
# IEEEtran drops uncited ones, so they are reported but not fatal.
EXPORTED=$(grep -oE '^@[a-zA-Z]+\{[^,]+' "$CLEAN" | sed -E 's/^@[a-zA-Z]+\{//' | sort -u)
MISSING=$(comm -23 <(printf '%s\n' "$CITED") <(printf '%s\n' "$EXPORTED") || true)
EXTRA=$(comm -13 <(printf '%s\n' "$CITED") <(printf '%s\n' "$EXPORTED") || true)

if [ -n "$MISSING" ]; then
  echo "cited but NOT exported:" >&2
  printf '  %s\n' $MISSING >&2
  die "export is missing $(printf '%s\n' $MISSING | wc -l | tr -d ' ') cited key(s). Wrong collection? Refusing to write."
fi

# ---- report -----------------------------------------------------------------

echo "cited   : $(printf '%s\n' "$CITED" | wc -l | tr -d ' ')  (from $TEX_REF)"
echo "entries : $(grep -c '^@' "$CLEAN")"
echo "bytes   : $(wc -c < "$CLEAN" | tr -d ' ')"
[ -n "$EXTRA" ] && { echo "extra (uncited, harmless):"; printf '          %s\n' $EXTRA; }
echo "keys    :"
grep -oE '^@[a-zA-Z]+\{[^,]+' "$CLEAN" | sed -E 's/^@[a-zA-Z]+\{/          /' | sort

# ---- write ------------------------------------------------------------------

if [ -z "$OUT" ]; then
  cp "$CLEAN" "/tmp/zotero_bib_$STAMP.bib"
  echo; echo "no output path given; preview at /tmp/zotero_bib_$STAMP.bib"
  exit 0
fi

if [ -f "$OUT" ] && cmp -s "$CLEAN" "$OUT"; then
  echo; echo "unchanged: $OUT"
  exit 0
fi

if [ -f "$OUT" ] && [ "$FORCE" -ne 1 ]; then
  die "$OUT exists and differs. Re-run with --force to overwrite (a timestamped backup is kept)."
fi

if [ -f "$OUT" ]; then
  cp "$OUT" "$OUT.bak_$STAMP"
  echo "backed up -> $OUT.bak_$STAMP"
  # Keep only the most recent $KEEP_BACKUPS; these are gitignored under _inbox/
  # and would otherwise grow without bound.
  ls -t "$OUT".bak_* 2>/dev/null | tail -n "+$((KEEP_BACKUPS + 1))" | while IFS= read -r old; do
    rm -f "$old"
  done
fi

# Atomic: write beside the target, then rename. An interrupted run cannot leave
# a truncated .bib at the canonical path.
TMPOUT="$OUT.tmp.$$"
cp "$CLEAN" "$TMPOUT"
mv "$TMPOUT" "$OUT"
TMPOUT=""
echo; echo "wrote: $OUT"
