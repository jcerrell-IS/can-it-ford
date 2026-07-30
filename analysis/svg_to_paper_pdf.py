import math
import re
import subprocess
import sys
import zlib
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops

REPO = Path('/Users/josie/can-it-ford')
OUTDIR = REPO / 'paper' / 'figures_review'
ICC_PATH = Path('/System/Library/ColorSync/Profiles/sRGB Profile.icc')
JPEG_QUALITY = 95
PDF_HEADER = b'%PDF-1.3\n%\xc4\xe5\xf2\xe5\xeb\xa7\xf3\xa0\xd0\xc4\xc6\n'

RASTER_LONG_EDGE = {
    'l0l1_two_rules_v2': 1600,
    'l2_divergence_real_v2': 1520,
    'mass_grid_sweep_v2': 1500,
}


def svg_size(svg):
    head = svg.read_text(encoding='utf-8')[:600]
    w = re.search(r'\bwidth="([0-9.]+)"', head)
    h = re.search(r'\bheight="([0-9.]+)"', head)
    if not w or not h:
        raise SystemExit(f'{svg.name}: no width/height on the root svg element')
    return float(w.group(1)), float(h.group(1))


def rasterize(svg, n):
    png = svg.parent / (svg.name + '.png')
    if png.exists():
        png.unlink()
    subprocess.run(
        ['qlmanage', '-t', '-s', str(n), '-o', str(svg.parent), str(svg)],
        check=True, capture_output=True,
    )
    if not png.exists():
        raise SystemExit(f'{svg.name}: qlmanage produced no {png.name}')
    im = Image.open(png)
    if im.size != (n, n):
        raise SystemExit(f'{png.name}: expected {n}x{n} square canvas, got {im.size}')
    return png


def ink_bbox(png):
    im = Image.open(png).convert('RGB')
    white = Image.new('RGB', im.size, (255, 255, 255))
    return ImageChops.difference(im, white).getbbox()


def flatten_to_jpeg(png):
    im = Image.open(png)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        flat = Image.new('RGB', im.size, 'white')
        flat.paste(im, mask=im.split()[-1])
    else:
        flat = im.convert('RGB')
    buf = BytesIO()
    flat.save(buf, 'JPEG', quality=JPEG_QUALITY)
    return buf.getvalue()


def pdf_bytes(jpeg, icc_z, n, box_w, box_h, tx, ty):
    objs = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Count 1 /Kids [ 3 0 R ] >>',
        (f'<< /Type /Page /Parent 2 0 R /MediaBox [ 0 0 {box_w} {box_h} ] '
         f'/Resources << /ProcSet [ /PDF /ImageC ] /XObject << /Im1 5 0 R >> >> '
         f'/Contents 4 0 R >>').encode('ascii'),
    ]
    content = f'q {n} 0 0 {n} {tx} {ty} cm /Im1 Do Q'.encode('ascii')
    objs.append(f'<< /Length {len(content)} >>\nstream\n'.encode('ascii')
                + content + b'\nendstream')
    objs.append((f'<< /Type /XObject /Subtype /Image /Width {n} /Height {n} '
                 f'/ColorSpace [ /ICCBased 6 0 R ] /BitsPerComponent 8 '
                 f'/Filter /DCTDecode /Length {len(jpeg)} >>\nstream\n').encode('ascii')
                + jpeg + b'\nendstream')
    objs.append((f'<< /N 3 /Alternate /DeviceRGB /Filter /FlateDecode '
                 f'/Length {len(icc_z)} >>\nstream\n').encode('ascii')
                + icc_z + b'\nendstream')

    out = bytearray(PDF_HEADER)
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f'{i} 0 obj\n'.encode('ascii') + body + b'\nendobj\n'
    xref_at = len(out)
    size = len(objs) + 1
    out += f'xref\n0 {size}\n'.encode('ascii')
    out += b'0000000000 65535 f \n'
    for off in offsets:
        out += f'{off:010d} 00000 n \n'.encode('ascii')
    out += (f'trailer\n<< /Size {size} /Root 1 0 R >>\n'
            f'startxref\n{xref_at}\n%%EOF\n').encode('ascii')
    return bytes(out)


def build(stem):
    svg = OUTDIR / f'{stem}.svg'
    if not svg.exists():
        raise SystemExit(f'missing source: {svg}')
    n = RASTER_LONG_EDGE.get(stem)
    if n is None:
        raise SystemExit(f'{stem}: no raster long edge registered')

    sw, sh = svg_size(svg)
    if sw < sh:
        raise SystemExit(f'{stem}: portrait svg ({sw}x{sh}) not supported by this crop rule')
    exact = n * sh / sw
    declared_h = math.ceil(exact - 1e-9)
    box_w = n

    print(f'{stem}')
    print(f'  svg            : {sw:g} x {sh:g}  (aspect {sw / sh:.4f})')
    print(f'  raster canvas  : {n} x {n} square, content top-aligned')

    png = rasterize(svg, n)
    bb = ink_bbox(png)
    box_h = max(declared_h, bb[3])

    print(f'  declared box   : {exact:.3f} px exact -> {declared_h}')
    print(f'  ink bbox       : {bb}')
    if bb[3] > declared_h:
        print(f'  OVERFLOW       : ink reaches row {bb[3]}, {bb[3] - declared_h} px past the '
              f'declared height, MediaBox raised to {box_h} so nothing is clipped')
    if bb[2] > box_w:
        raise SystemExit(f'{stem}: ink overflows the canvas width, bbox right {bb[2]} > {box_w}')
    print(f'  MediaBox height: {box_h}')
    print(f'  clearance      : {box_h - bb[3]} px below ink, {box_w - bb[2]} px right of ink')

    jpeg = flatten_to_jpeg(png)
    icc_z = zlib.compress(ICC_PATH.read_bytes(), 9)
    pdf = pdf_bytes(jpeg, icc_z, n, box_w, box_h, 0, -(n - box_h))
    out = OUTDIR / f'{stem}.pdf'
    out.write_bytes(pdf)
    print(f'  jpeg           : {len(jpeg)} bytes at quality {JPEG_QUALITY}')
    print(f'  icc            : {ICC_PATH.name}, {len(icc_z)} bytes deflated')
    print(f'  wrote          : {out}  ({out.stat().st_size} bytes)')
    print(f'  MediaBox       : [ 0 0 {box_w} {box_h} ]')
    print()


if __name__ == '__main__':
    stems = sys.argv[1:] or sorted(RASTER_LONG_EDGE)
    for stem in stems:
        build(stem)
