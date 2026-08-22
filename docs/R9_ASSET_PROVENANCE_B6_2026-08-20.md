# Register B6: the HDRI and asphalt provenance, established

Slot d13-renders, 2026-08-20. **Nothing was deleted.** Deleting would not unpublish
anything, and as it turns out there is nothing here to withdraw.

## Answer first

`assets/DaySkyHDRI002A_1K_HDR.exr` and the four `assets/Asphalt015*` files are
**ambientCG assets, published under the Creative Commons CC0 1.0 Universal License.**

CC0 places the work in the public domain worldwide: redistribution is permitted, and no
attribution is required. **Committing them to a public repository is within the licence.**
Register B6 can close as "provenance established, no exposure", not as "risk accepted".

## The evidence, in the order it was gathered

1. **The files themselves carry no provenance.** The EXR header holds only standard
   OpenEXR attributes (`channels`, `compression`, `dataWindow`, `displayWindow`,
   `lineOrder`, `pixelAspectRatio`, `screenWindowCenter`, `screenWindowWidth`): no
   `owner`, no `comments`, no software tag. The Radiance `.hdr` in `assets/hdri/` is
   three header lines with no comment. So nothing could be read off the assets, which is
   why the question stayed open.

2. **Neither does the repository.** `assets/` contains only binary media, no licence or
   readme. The root `LICENSE` is BSD 3-Clause, Copyright 2026 Josie Cerrell, and a live
   search of it returns **no** hits for third-party, asset, hdri, texture, ambient or
   CC0. That is the real defect and it is separate from the licence question: the
   repository never recorded what it was carrying.

3. **The session log records the download, with the URL.** `LIVE_SESSION_LOG_2026-07-22.md`
   captures a tmux pane titled "Download HDR skybox asset for PBR", working directory
   `/Users/josie/Downloads/pbr_assets`, containing the literal string
   `https://ambientcg.com/view?id=DaySkyHDRI002A`, and a note that "AmbientCG only
   bundles it inside a 3MB zip, no standalone .exr. Next: on your go, download the zip,
   extract the .exr, then scp."

4. **The original downloads survive.** `~/Downloads/DaySkyHDRI002A_1K.zip` and its
   extracted directory, and `~/Downloads/pbr_assets/` with the Asphalt015 set.

5. **The committed files are byte-identical to those downloads.** MD5, all four:

   | file | committed | ambientCG download |
   | --- | --- | --- |
   | `DaySkyHDRI002A_1K_HDR.exr` | `6a006d4bf75ec241fedd88c38effcab3` | same |
   | `Asphalt015_1K-JPG_Color.jpg` | `51d31d3962b5abbb0b1796cf10a3d7c5` | same |
   | `Asphalt015_1K-JPG_NormalGL.jpg` | `964b7bccf5a7213e911a36d4f1d453ac` | same |
   | `Asphalt015_1K-JPG_Roughness.jpg` | `d97d50844606a004dba928ffdc5df816` | same |

   This is what makes the identification an identification rather than a name match.

6. **An independent fingerprint inside the bundle.** The Godot resource shipped in the
   zip, `DaySkyHDRI002A_1K.tres`, carries UIDs prefixed `acg_`: `uid://acg_ve01ayr5`,
   `uid://acg_wmq1r6t3`, `uid://acg_3mnlax4p`, `uid://acg_wkmcs7d9`. `acg` is ambientCG.

7. **The licence, read live from source this session.** `https://ambientcg.com/license`
   redirects (302) to `https://docs.ambientcg.com/license/`, which states
   "Creative Commons CC0 1.0 Universal License" and "licensed under the Creative Commons
   CC0 1.0 Universal License". Both asset pages resolve and serve exactly the bundle
   filenames present in `~/Downloads`: `DaySkyHDRI002A_1K.zip` and
   `Asphalt015_1K-JPG.zip`.

**Which view I searched, and what I did not check.** The licence above is ambientCG's
site-wide statement, read from their docs. I did NOT find a per-asset licence string on
the individual asset pages; the stripped HTML did not expose one, and I did not pursue
whether it is rendered client-side. So the correct claim is: ambientCG states CC0 1.0 for
its assets site-wide, and these are ambientCG assets. If a per-asset exception mechanism
exists, I have not ruled it out.

## The separate HDRI, which already had a record

`assets/hdri/kloofendal_43d_clear_puresky_2k.hdr` is a different file and was already
documented: commit `efda6af`, "Track hero-shot HDRI asset, CC0 licensed", and the
session log of 2026-07-23 says "The HDRI is CC0; committing the binary is optional". Its
filename follows Poly Haven's convention. I did not verify that source, because it was
not the asset in question and it already carries a CC0 record.

## The finding worth keeping, which is not about licences

`8cc302c` (2026-07-23, Josie Cerrell) is the commit that added all five ambientCG files.
**The same commit added `vehicle_meshes/` to `.gitignore`.** So in one commit the
licence-uncertain MESHES were deliberately kept out of the repository while five
third-party media assets were committed with no licence record at all.

That is not an oversight about licensing in general. Licensing was actively on the
author's mind in that very commit. It is an inconsistency **within** one commit, and it
is the mechanism worth generalising: a project can have a working licence practice and
still ship an unrecorded asset, because the practice attaches to the category someone is
currently worried about. The meshes were the worry; the textures rode along.

## What should change

1. **Add `assets/LICENSE.md`** naming each asset, its ambientCG ID, its source URL and
   CC0 1.0. Not required by CC0, which waives attribution, but it is what would have
   made this question answerable in thirty seconds instead of an hour of forensics. **I
   have not added it: `assets/` is outside this slot's write scope.**
2. **Close register B6** as provenance established, licence CC0, no exposure.
3. **Do not generalise the all-clear.** This says nothing about the derived vehicle
   hulls, where register E8 remains genuinely open and where the mesh deep search's
   negative result stands, bounded to its own result set.

## Unreviewed

The physics-skeptic subagent is dead fleet-wide, so this is UNREVIEWED. Every step above
is reproducible: the MD5s from the two paths, the log lines by grep, and the licence text
by fetching `https://docs.ambientcg.com/license/`.
