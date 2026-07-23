import re
import sys
from pathlib import Path
from collections import OrderedDict

logfile = Path.home() / "can-it-ford" / "_inbox" / "LIVE_SESSION_LOG.md"
archivedir = Path.home() / "can-it-ford" / "_inbox" / "session_archive"
archivedir.mkdir(parents=True, exist_ok=True)

text = logfile.read_text()
pattern = re.compile(r"^# UPDATE: (\d{4}-\d{2}-\d{2}) ", re.MULTILINE)
matches = list(pattern.finditer(text))

if not matches:
    print("No '# UPDATE:' headers found. Nothing to split.")
    sys.exit(1)

boundaries = [(matches[i].start(), matches[i].group(1)) for i in range(len(matches))]
boundaries.append((len(text), None))

by_date = OrderedDict()
for i in range(len(matches)):
    start = boundaries[i][0]
    end = boundaries[i + 1][0]
    date = boundaries[i][1]
    by_date.setdefault(date, []).append(text[start:end])

print(f"Found {len(matches)} update blocks across {len(by_date)} distinct days:")
for date, blocks in by_date.items():
    print(f"  {date}: {len(blocks)} blocks")

total_written = 0
for date, blocks in by_date.items():
    outfile = archivedir / f"LIVE_SESSION_LOG_{date}.md"
    outfile.write_text("".join(blocks))
    total_written += len(blocks)
    print(f"Wrote {outfile} ({len(blocks)} blocks)")

print(f"\nTotal blocks written: {total_written} (should equal {len(matches)} found above)")
print("Original file NOT modified. Verify the split files above before touching it.")
