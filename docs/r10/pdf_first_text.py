#!/usr/bin/env python3
"""
Extract the leading text of a PDF, stdlib only.

There is no pdftotext on this Mac and no numpy in any interpreter, so this
decompresses the PDF's own FlateDecode content streams and pulls the strings out
of the text-showing operators. It is not a general PDF renderer and does not try
to be: it only has to recover enough of the opening page to decide whether a file
is the paper its filename claims.

Why this exists: identity was being checked from filenames and embedded metadata,
and both lied tonight, in opposite directions. A file whose embedded title said
"APPLICATION OF DIGITAL CELLULAR RADIO" was the right paper; a file named for one
DOI was the JCGM metrology vocabulary. Only the page settles it, so the page has
to be cheap to read.
"""
import re
import sys
import zlib


def streams(raw):
    """Yield decompressed content streams in file order."""
    for m in re.finditer(rb"stream\r?\n", raw):
        start = m.end()
        end = raw.find(b"endstream", start)
        if end < 0:
            continue
        blob = raw[start:end]
        try:
            yield zlib.decompress(blob)
        except zlib.error:
            # uncompressed streams are legal and common in older writers
            if b"BT" in blob and b"Tj" in blob or b"TJ" in blob:
                yield blob


def unescape(b):
    out = bytearray()
    i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):  # backslash
            nxt = b[i + 1]
            mapping = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12}
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            if 0x30 <= nxt <= 0x37:  # octal
                j = i + 1
                digits = b""
                while j < len(b) and 0x30 <= b[j] <= 0x37 and len(digits) < 3:
                    digits += bytes([b[j]])
                    j += 1
                out.append(int(digits, 8) & 0xFF)
                i = j
                continue
            out.append(nxt)
            i += 2
            continue
        out.append(c)
        i += 1
    return bytes(out)


def text_of(stream):
    """Pull literal strings out of Tj / TJ / ' / " operators."""
    parts = []
    for m in re.finditer(rb"\((?:[^()\\]|\\.|\([^()]*\))*\)", stream):
        s = unescape(m.group(0)[1:-1])
        parts.append(s.decode("latin-1", "replace"))
    return "".join(parts)


def first_text(path, want_chars=2500):
    raw = open(path, "rb").read()
    got = []
    n = 0
    for st in streams(raw):
        t = text_of(st)
        # skip streams that decompressed to something with no letters
        if not re.search(r"[A-Za-z]{3}", t):
            continue
        got.append(t)
        n += len(t)
        if n >= want_chars:
            break
    out = " ".join(got)
    out = re.sub(r"\s+", " ", out)
    return out[:want_chars]


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("=== %s" % p.rsplit("/", 1)[-1])
        try:
            print(first_text(p)[:700])
        except Exception as e:
            print("   EXTRACT FAILED: %s" % e)
        print()
