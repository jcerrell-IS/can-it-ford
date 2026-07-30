"""Structural and content invariants for the Can It Ford IEEE paper.

WHAT THIS IS
  A snapshot-and-compare checker. It does NOT compile the document: no TeX
  engine is assumed present. It rules out the mechanical failure classes that
  break a build (unbalanced braces, missing graphics, dangling \\ref, unknown
  \\cite keys) and it pins the content invariants that a prose or reconcile
  pass must not silently change: the numbers, the citation keys, the figure
  targets, and the unresolved-marker counts.

WHY IT EXISTS
  Prose passes and Overleaf/local reconciles move line numbers, so a plain
  diff stops being readable. What matters is not "did lines move" but "did any
  number, citation, figure path, or open FLAG change without being asked for".
  This turns that into a machine check.

USAGE
    python3 tex_invariants.py snapshot BEFORE.json          # capture
    ...edit the .tex...
    python3 tex_invariants.py snapshot AFTER.json           # capture again
    python3 tex_invariants.py compare BEFORE.json AFTER.json
    python3 tex_invariants.py check                         # structure only

  compare exits 1 if any invariant moved, so it can gate a commit.
  Deltas are reported, never auto-accepted: an intentional change shows up as
  a reported delta that a human confirms, which is the point.

SCOPE LIMIT, STATED PLAINLY
  Passing this is not evidence the PDF builds or that the layout is sane.
  Float placement, page count, and overfull boxes need a real engine.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEX = HERE / 'conference_101719_1.tex'
BIB = HERE / 'can_it_ford_references_IEEE.bib'
GRAPHICS_EXTS = ['', '.pdf', '.png', '.jpg', '.jpeg', '.eps']


def strip_comments(s):
    """Drop TeX line comments, keeping escaped \\% intact."""
    return '\n'.join(re.sub(r'(?<!\\)%.*$', '', ln) for ln in s.split('\n'))


def body():
    return strip_comments(TEX.read_text(encoding='utf-8'))


# ----------------------------------------------------------------- extractors

def numbers(src):
    """Every numeric literal in the prose, normalized.

    TeX thin-space and digit-group markers (1{,}609 and 3.54\\,m) are folded
    away first so that a number keeps one identity regardless of how it was
    typeset. Pure float/int tokens only; \\ref and \\cite are excluded by the
    caller stripping them beforehand.
    """
    flat = src.replace('{,}', '').replace('\\,', '')
    flat = re.sub(r'\\(?:ref|label|cite)\{[^}]*\}', ' ', flat)
    flat = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}', ' ', flat)
    return sorted(set(re.findall(r'(?<![\w.])\d+(?:\.\d+)?(?![\w.])', flat)))


def cites(src):
    out = set()
    for m in re.finditer(r'\\cite\{([^}]+)\}', src):
        out.update(k.strip() for k in m.group(1).split(','))
    return sorted(out)


def graphics(src):
    return sorted(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', src))


def markers(src):
    return {tag: len(re.findall(r'\\' + tag + r'\{', src))
            for tag in ('FLAG', 'PLACEHOLDER')}


def brace_depth(src):
    depth = 0
    first_negative = None
    for i, ln in enumerate(src.split('\n'), 1):
        for ch in ln:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth < 0 and first_negative is None:
                    first_negative = i
    return depth, first_negative


def floats(src):
    return [f'{k}[{p or "none"}]'
            for k, p in re.findall(r'\\begin\{(figure\*?|table\*?)\}(?:\[([^\]]*)\])?', src)]


def snapshot():
    src = body()
    depth, neg = brace_depth(src)
    return {
        'tex': TEX.name,
        'lines': src.count('\n') + 1,
        'brace_depth': depth,
        'first_negative_brace_line': neg,
        'numbers': numbers(src),
        'cites': cites(src),
        'graphics': graphics(src),
        'labels': sorted(set(re.findall(r'\\label\{([^}]+)\}', src))),
        'refs': sorted(set(re.findall(r'\\ref\{([^}]+)\}', src))),
        'markers': markers(src),
        'floats': floats(src),
        'sections': re.findall(r'\\(?:sub)?section\*?\{([^}]+)\}', src),
    }


# -------------------------------------------------------------------- checks

def check():
    """Structural checks that can fail on their own, independent of a diff."""
    src = body()
    snap = snapshot()
    fails = []

    print('=' * 70)
    print(f'STRUCTURE  {TEX.name}  ({snap["lines"]} lines)')
    print('=' * 70)

    depth, neg = snap['brace_depth'], snap['first_negative_brace_line']
    ok = depth == 0 and neg is None
    print(f'brace balance      : net {depth}  {"OK" if ok else "UNBALANCED"}')
    if not ok:
        fails.append(f'braces net={depth} first_negative_line={neg}')

    print()
    print('includegraphics targets (resolved relative to the .tex directory):')
    for p in snap['graphics']:
        hit = next((HERE / (p + e) for e in GRAPHICS_EXTS if (HERE / (p + e)).is_file()), None)
        if hit is None:
            print(f'  MISSING  {p}')
            fails.append(f'missing graphic {p}')
            continue
        kind = ''
        if hit.suffix == '.pdf':
            raw = hit.read_bytes()
            n = raw.count(b'/Subtype /Image') + raw.count(b'/Subtype/Image')
            kind = '  [TRUE VECTOR]' if n == 0 else f'  [RASTER {n} img xobj]'
        elif hit.suffix in ('.png', '.jpg', '.jpeg'):
            kind = '  [raster]'
        print(f'  OK       {p:34s} {hit.stat().st_size/1024:8.1f} KB{kind}')

    dangling = sorted(set(snap['refs']) - set(snap['labels']))
    unused = sorted(set(snap['labels']) - set(snap['refs']))
    print()
    print(f'labels={len(snap["labels"])} refs={len(snap["refs"])}')
    print(f'  dangling \\ref (prints "??"): {dangling or "none"}')
    print(f'  labels never referenced    : {unused or "none"}')
    if dangling:
        fails.append(f'dangling refs {dangling}')

    bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', BIB.read_text(encoding='utf-8', errors='replace')))
    unknown = sorted(set(snap['cites']) - bibkeys)
    unusedbib = sorted(bibkeys - set(snap['cites']))
    print()
    print(f'bib entries={len(bibkeys)}  distinct cite keys={len(snap["cites"])}')
    print(f'  cited but NOT in bib: {unknown or "none"}')
    print(f'  in bib, never cited : {unusedbib or "none"}')
    if unknown:
        fails.append(f'unknown cite keys {unknown}')

    print()
    print(f'floats ({len(snap["floats"])}): {", ".join(snap["floats"])}')
    nfull = sum(1 for f in snap['floats'] if f.startswith(('figure*', 'table*')))
    print(f'  full-width={nfull}  single-column={len(snap["floats"]) - nfull}')

    print()
    for tag, n in snap['markers'].items():
        lines = [src[:m.start()].count('\n') + 1 for m in re.finditer(r'\\' + tag + r'\{', src)]
        print(f'\\{tag}: {n}   lines {lines}')

    print()
    print('=' * 70)
    print(f'STRUCTURAL RESULT: {"PASS" if not fails else "FAIL"}')
    for f in fails:
        print(f'  - {f}')
    print('NOT a compile. No TeX engine is invoked by this script.')
    print('=' * 70)
    return 0 if not fails else 1


def compare(a_path, b_path):
    a = json.loads(Path(a_path).read_text())
    b = json.loads(Path(b_path).read_text())
    moved = []

    print('=' * 70)
    print(f'INVARIANT COMPARE   {Path(a_path).name} -> {Path(b_path).name}')
    print('=' * 70)
    print(f'lines {a["lines"]} -> {b["lines"]}   '
          f'({b["lines"] - a["lines"]:+d}; line movement alone is not a violation)')
    print()

    for key in ('numbers', 'cites', 'graphics', 'labels', 'refs'):
        added = sorted(set(b[key]) - set(a[key]))
        removed = sorted(set(a[key]) - set(b[key]))
        if not added and not removed:
            print(f'{key:10s} INVARIANT  ({len(a[key])} items)')
            continue
        moved.append(key)
        print(f'{key:10s} CHANGED')
        if added:
            print(f'    added  : {added}')
        if removed:
            print(f'    removed: {removed}')

    print()
    for tag in ('FLAG', 'PLACEHOLDER'):
        x, y = a['markers'][tag], b['markers'][tag]
        verdict = 'INVARIANT' if x == y else f'CHANGED {x} -> {y} ({y - x:+d})'
        print(f'\\{tag:12s} {verdict}')
        if x != y:
            moved.append(tag)

    if a['floats'] != b['floats']:
        moved.append('floats')
        print(f'\nfloats     CHANGED\n    before: {a["floats"]}\n    after : {b["floats"]}')
    else:
        print(f'\nfloats     INVARIANT ({len(a["floats"])})')

    if a['sections'] != b['sections']:
        moved.append('sections')
        print(f'\nsections   CHANGED\n    before: {a["sections"]}\n    after : {b["sections"]}')
    else:
        print(f'sections   INVARIANT ({len(a["sections"])})')

    print()
    print('=' * 70)
    if moved:
        print(f'DELTAS IN: {", ".join(sorted(set(moved)))}')
        print('Each must be an intended edit. This script does not judge intent.')
    else:
        print('ALL INVARIANTS HELD.')
    print('=' * 70)
    return 1 if moved else 0


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv or argv[0] == 'check':
        sys.exit(check())
    if argv[0] == 'snapshot':
        out = Path(argv[1] if len(argv) > 1 else 'snapshot.json')
        out.write_text(json.dumps(snapshot(), indent=2))
        print(f'wrote {out}')
        sys.exit(0)
    if argv[0] == 'compare':
        sys.exit(compare(argv[1], argv[2]))
    sys.exit(f'usage: {Path(__file__).name} [check|snapshot OUT.json|compare A.json B.json]')
