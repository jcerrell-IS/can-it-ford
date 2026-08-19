#!/bin/bash
# r10 acquisition: download the open-access subset of the want list.
#
# Destination is OUTSIDE the git repo on purpose. can-it-ford is a PUBLIC
# GitHub repo and licence question E8 is unresolved, so publisher PDFs are
# not committed. The manifest and provenance go in the repo; the bytes do not.
# This follows the convention an earlier slot set at ~/can-it-ford-refs/.
#
# Reads the resolved TSV, skips closed and DOI-less rows, and records for each
# attempt the HTTP code, content type and byte count so a failure cannot be
# mistaken for a success.

set -u
RES="$1"
DEST="/Users/josie/can-it-ford-refs/2026-08-19-r10"
MAN="/Users/josie/can-it-ford/.claude/worktrees/r9-gapscan/data/r10_acquired/acquisition_manifest.tsv"
mkdir -p "$DEST"

printf 'cite_key\tdoi\toa_status\tlicense\thttp\tcontent_type\tbytes\tis_pdf\tfile\tsource_url\n' > "$MAN"

tail -n +2 "$RES" | while IFS=$'\t' read -r key year doi oa lic url title; do
  [ -z "${url:-}" ] && continue
  case "$oa" in closed|NO_DOI|OA_ERR*|"") continue;; esac
  safe_doi=$(printf '%s' "$doi" | tr '/' '_')
  out="$DEST/${key}_${safe_doi}.pdf"
  hdr=$(curl -sS -L -m 120 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
        -w '%{http_code}\t%{content_type}\t%{size_download}' -o "$out" "$url" 2>/dev/null)
  code=$(printf '%s' "$hdr" | cut -f1)
  ctype=$(printf '%s' "$hdr" | cut -f2)
  nbytes=$(printf '%s' "$hdr" | cut -f3)
  if [ -s "$out" ] && [ "$(head -c 4 "$out")" = "%PDF" ]; then
    ispdf=YES
  else
    ispdf=NO
    rm -f "$out"
    out=""
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$key" "$doi" "$oa" "$lic" "$code" "$ctype" "$nbytes" "$ispdf" "$(basename "${out:-NONE}")" "$url" >> "$MAN"
  printf '%-9s %-4s http=%s pdf=%s bytes=%s\n' "$key" "$oa" "$code" "$ispdf" "$nbytes"
done
