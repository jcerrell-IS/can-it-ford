# pysplashsurf aarch64 wheels: contradiction resolved by live check, 2026-08-13

STATUS: RESOLVED. One of the two prior session claims was wrong. Named below.

SCOPE: this decides only whether the render track needs a Rust toolchain on
GH200. It touches no solver code, no gated run, and no verdict.

## The contradiction

Two records in this project disagreed about the same testable fact.

- `.remember/today-2026-08-13.md`, 00:58-01:17 block: "pysplashsurf lacks
  aarch64 wheels (contradicts b0d2664f)".
- The 01:15-01:48 session: "Live PyPI check: 0.14.1.0 ships
  manylinux2014_aarch64 and macosx_14_0_arm64. No cargo build needed."

Neither had been re-derived. Both are paraphrases in a session record, which is
the weakest evidence tier this project recognises.

## The live check, run 2026-08-13

Method, reproducible:

```bash
curl -s https://pypi.org/pypi/pysplashsurf/json | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f['filename']) for f in d['releases'][d['info']['version']]]"
```

Result. Latest version is **0.14.1.0**, uploaded 2026-03-21. It ships 12 wheels
plus an sdist. The ARM-relevant ones, filenames exactly as PyPI returns them:

| Wheel | Target |
|---|---|
| `pysplashsurf-0.14.1.0-cp310-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.whl` | Linux aarch64 (GH200) |
| `pysplashsurf-0.14.1.0-cp310-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl` | Linux aarch64, alternate tag order |
| `pysplashsurf-0.14.1.0-cp310-abi3-macosx_14_0_arm64.whl` | Apple Silicon (this Mac) |
| `pysplashsurf-0.14.1.0-cp310-abi3-win_arm64.whl` | Windows ARM |
| `pysplashsurf-0.14.1.0-cp310-abi3-manylinux2014_armv7l.manylinux_2_17_armv7l.whl` | 32-bit ARM |

The previous release, **0.14.0.0** (2025-09-15), ships the same aarch64 and
macOS-arm64 set. So aarch64 wheels were not a recent addition, and there is no
recent version at which the "lacks aarch64 wheels" claim was true.

The wheels are `cp310-abi3`, i.e. a single stable-ABI build covering CPython
3.10 and newer, so the Python minor version on the target node does not need to
match a specific wheel.

## Which prior claim was wrong

**The `.remember` claim is WRONG.** pysplashsurf does ship aarch64 wheels, and
did at the previous release too. The 01:15-01:48 session claim is correct, and
this check reproduces it independently rather than restating it.

## What b0d2664f actually says, quoted directly

`.remember` framed its claim as contradicting b0d2664f. It does not, because
b0d2664f never made a claim about wheels. b0d2664f is not a commit; it is a
research report on disk at
`~/Downloads/compass_artifact_wf-b0d2664f-3b65-5bfe-8e3f-f06e77a59f79_text_markdown.md`,
dated 2026-08-07. Item 13, verbatim:

> Python bindings exist (pysplashsurf, pip). Being pure Rust with no GPU
> dependency, it builds cleanly on ARM64/aarch64 GH200.

That is a claim about **buildability from source**, not about prebuilt wheel
availability. So the two records were never in direct contradiction on the same
proposition; `.remember` compared a wheel claim against a build claim.

The live result is **stronger than b0d2664f claimed**: you do not need to build
at all, because prebuilt aarch64 wheels exist. b0d2664f's statement is not
refuted, it is superseded by a better outcome.

## Consequence for GH200

**No Rust toolchain, no cargo build, and no source compile is required on GH200
for the render track.** `pip install pysplashsurf` resolves to a prebuilt
manylinux aarch64 wheel.

The one condition a `manylinux_2_17` wheel imposes is glibc 2.17 or newer on the
target node. **Confirmed live on Vista, 2026-08-13**, by
`scripts/tacc.sh vista 'ldd --version | head -1; uname -m'`:

```
ldd (GNU libc) 2.34
aarch64
```

glibc 2.34 clears the 2.17 floor and the arch is aarch64, so the
`manylinux2014_aarch64` wheel is installable on Vista as it stands. Nothing about
this install path is now unverified.

## Standing caveat, unrelated to wheels

Wheel availability says nothing about whether splashsurf is the right tool for
this pipeline. It is a marching-cubes surface reconstructor over a 3D SPH
density field. The render layer's `free_surface()` in
`analysis/render_multigeom_shaded.py` is a 2D column-max heightfield with a
Gaussian blur. Those are different objects and swapping one for the other is a
rewrite, not a drop-in. See `docs/RENDER_REALISM_2026-08-13.md`, the smoothing
section, before treating this install path as a task that is ready to start.
