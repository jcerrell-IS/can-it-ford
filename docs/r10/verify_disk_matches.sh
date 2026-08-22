#!/bin/bash
# r10 step 2, verification stage.
#
# A phrase hit inside a PDF is NOT a match. The project's own paper, the
# research dossier, and other people's reference lists all contain these
# titles. Verified live: /Users/josie/Downloads/1909.04504v3.pdf came back as a
# candidate for Las09 and its embedded title is "PySPH: a Python-based
# framework for smoothed particle hydrodynamics", a different paper entirely.
#
# So every candidate is re-tested against the PDF's own embedded title, which
# is what the typesetter wrote, not what the downloader named the file. A
# candidate counts as ON DISK only if some hit's embedded title matches the
# wanted title.
set -u
W="$1"

printf 'cite_key\tverdict\tmatched_file\tembedded_title\n'

tail -n +2 "$W" | while IFS=$'\t' read -r key year have title rest; do
  probe=$(printf '%s' "$title" | tr -d '"' | /usr/bin/awk '{for(i=1;i<=9&&i<=NF;i++)printf "%s ",$i}' | /usr/bin/sed 's/ *$//')
  hits=$(mdfind -onlyin /Users/josie "kMDItemTextContent == \"$probe\"" 2>/dev/null \
         | /usr/bin/grep -i '\.pdf$' | /usr/bin/grep -v 'can-it-ford-refs/2026-08-19-r10' || true)
  [ -z "$hits" ] && continue
  # normalise for comparison: lowercase, alphanumeric only
  wantn=$(printf '%s' "$title" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9' | cut -c1-45)
  verdict=CITATION_ONLY; mf=""; et=""
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    t=$(mdls -raw -name kMDItemTitle "$f" 2>/dev/null)
    [ "$t" = "(null)" ] && continue
    gotn=$(printf '%s' "$t" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9' | cut -c1-45)
    case "$gotn" in
      "$wantn"*) verdict=ON_DISK; mf="$f"; et="$t"; break;;
    esac
    case "$wantn" in
      "$gotn"*) verdict=ON_DISK; mf="$f"; et="$t"; break;;
    esac
  done <<EOF
$hits
EOF
  printf '%s\t%s\t%s\t%s\n' "$key" "$verdict" "$mf" "$et"
done
