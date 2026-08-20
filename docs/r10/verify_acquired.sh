#!/bin/bash
# Verify every acquired PDF really is the paper its filename claims.
#
# Uses the Swift PDFKit extractor, because filenames and embedded metadata BOTH
# lied tonight in opposite directions and only the page settles it. Matching
# strips whitespace on both sides, since PDFKit returns ligature-heavy text with
# spaces collapsed ("Analysisandmitigationof...").
set -u
W="$1"; D="$2"
SW=/Users/josie/can-it-ford/.claude/worktrees/r9-gapscan/docs/r10/pdftext.swift
printf 'cite_key\tverdict\tfile\twanted_title\n'
for f in "$D"/*.pdf; do
  b=$(basename "$f"); k="${b%%_*}"
  case "$b" in WRONG-FILE*) printf '%s\tQUARANTINED\t%s\t\n' "$k" "$b"; continue;; esac
  [ "$k" = "Schulz2019" ] && k=Sch19e
  want=$(/usr/bin/awk -F'\t' -v K="$k" 'NR>1 && $1==K{print $4; exit}' "$W")
  [ -z "$want" ] && { printf '%s\tNO_WANTED_TITLE\t%s\t\n' "$k" "$b"; continue; }
  txt=$(swift "$SW" "$f" 2 4000 2>/dev/null | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9')
  wn=$(printf '%s' "$want" | tr 'A-Z' 'a-z' | tr -cd 'a-z0-9' | cut -c1-40)
  if [ -z "$txt" ]; then v=NO_TEXT
  elif printf '%s' "$txt" | /usr/bin/grep -qF "$wn"; then v=CONFIRMED
  else v=MISMATCH; fi
  printf '%s\t%s\t%s\t%s\n' "$k" "$v" "$b" "$(printf '%s' "$want" | cut -c1-58)"
done
