#!/bin/bash
# r10 step 2: resolve the want list against local disk.
#
# CORRECTED. The first version of this script used a bare 8-word probe, which
# mdfind treats as an OR over the words. That reported 156 of 230 present on
# disk, and it was nonsense: Sch19e "matched" 108 files and its top hit was a
# different paper entirely. That number is withdrawn, not adjusted.
#
# This version quotes the probe, which makes Spotlight do phrase matching, and
# restricts hits to PDFs. Two exclusions matter:
#   - can-it-ford-refs/2026-08-19-r10 is what THIS slot downloaded tonight, so
#     counting it as "already on disk" would be circular
#   - a title phrase found inside another paper's reference list is a citation,
#     not the paper, so every survivor still needs its first page read
set -u
W="$1"
OUT="$2"
SCOPE="/Users/josie"
MINE="can-it-ford-refs/2026-08-19-r10"

printf 'cite_key\tn_pdf_hits\tfirst_pdf_hit\ttitle\n' > "$OUT"

tail -n +2 "$W" | while IFS=$'\t' read -r key year have title rest; do
  probe=$(printf '%s' "$title" | tr -d '"' | /usr/bin/awk '{for(i=1;i<=9&&i<=NF;i++)printf "%s ",$i}' | /usr/bin/sed 's/ *$//')
  hits=$(mdfind -onlyin "$SCOPE" "kMDItemTextContent == \"$probe\"" 2>/dev/null \
         | /usr/bin/grep -i '\.pdf$' | /usr/bin/grep -v "$MINE" || true)
  n=$(printf '%s' "$hits" | /usr/bin/grep -c . || true)
  first=$(printf '%s' "$hits" | head -1)
  printf '%s\t%s\t%s\t%s\n' "$key" "$n" "$first" "$title" >> "$OUT"
done

echo "want-list rows checked: $(($(wc -l < "$OUT") - 1))"
echo "rows with at least one PDF candidate on disk: $(/usr/bin/awk -F'\t' 'NR>1 && $2>0' "$OUT" | wc -l)"
