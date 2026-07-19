# Poster Text Draft

Source of requirements: `Instructions.docx.md` (poster spec), items 5 and 6.
Target file name on upload: `Cerrell_TACC_42x56` (PDF, under 40MB, due Monday July 27, 9am CST).

Items marked **[CONFIRM]** are not verifiable from anything in this repo. Check them before printing.

---

## Title

**Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability**

Shorter alternative if the title bar is cramped at 42x56:

**Can It Ford? Finding the Simplest Physics That Answers a Flood-Safety Question**

---

## Authors

Josie Cerrell¹, Hassan Iqbal², Cheng-Hsi Hsiao², Krishna Kumar²

**[CONFIRM]** Author list and order are a guess, not a fact. The repo names Hassan Iqbal, Cheng-Hsi Hsiao, and Sarah Etter as mentors and Krishna Kumar as PI, but no existing file states who goes on the poster. Ask Kumar directly. Sarah Etter is named as a daily mentor in `README.md` and is omitted above only because I could not tell whether her role was technical supervision of this work. Do not let this default silently.

---

## Department / School

¹ Claremont McKenna College, Claremont, CA
² GeoElements Lab, Texas Advanced Computing Center, The University of Texas at Austin

**[CONFIRM]** Kumar's departmental affiliation is likely the Department of Civil, Architectural and Environmental Engineering at UT Austin, but that string appears nowhere in this repo and I did not verify it against a live source. Confirm before use, or drop to "GeoElements Lab, Texas Advanced Computing Center, UT Austin" which is directly supported by `README.md`.

---

## Introduction

*(Covers Instructions.docx.md item 5: full name, major and institution, REU program and mentors, research project.)*

My name is **Josie Cerrell**, and I am an **Integrated Sciences major at Claremont McKenna College**. This work was conducted through the **NSF REU Site: Cyberinfrastructure Research for Societal Advancement**, hosted at the **Texas Advanced Computing Center at The University of Texas at Austin**, in the **GeoElements Lab** under **PI Dr. Krishna Kumar**, with daily mentorship from **Hassan Iqbal** and **Cheng-Hsi Hsiao**.

Flooded roads are a leading cause of flood fatalities: more than half of flood-related drownings happen when a vehicle is driven into hazardous water. A driver cannot judge depth, flow speed, or road condition from appearance alone, and neither can an autonomous vehicle. AI world models that predict what a scene will *look* like inherit exactly this blind spot: they can produce a future that looks plausible while violating the physics that actually decides the outcome.

My project asks one deliberately narrow question: **given a real flooded road reconstructed from video, can a specific vehicle ford it?** Rather than building the highest-fidelity simulation possible, I ask what the *simplest* physical abstraction is that still answers the question correctly. I compare three levels: a static depth threshold (L0), a depth-velocity stability criterion from the Australian Rainfall and Runoff guidelines (L1), and a fully coupled Material Point Method simulation in which buoyancy and lateral drag emerge from the physics itself (L2).

The central result is that **the minimum sufficient abstraction depends on the question being asked**. Deep, still water is resolved correctly by a simple depth threshold. But fast, shallow flow is not: at 0.30 m depth and 1.5 m/s, the depth-velocity criterion returns FORD while the coupled simulation returns NO-FORD, because it detects a continuous lateral drag mechanism the scalar criterion structurally cannot represent.

**[CONFIRM]** The L1/L2 divergence numbers above come from `CLAUDE.md`, which flags them as last verified June 27 and not re-checked. Re-verify against the 36-run sweep (commit `eceebee`) before printing, since that sweep is newer than the finding.

---

## Acknowledgments

*(Covers Instructions.docx.md item 6. The award citation below is required verbatim.)*

This material is based upon work supported by the **National Science Foundation** under the **NSF REU Site: Cyberinfrastructure Research for Societal Advancement, Award # 2447887**. This research was conducted at **The University of Texas at Austin Texas Advanced Computing Center (TACC)**, whose computational resources made this work possible.

I thank my PI, Dr. Krishna Kumar, and my mentors Hassan Iqbal and Cheng-Hsi Hsiao of the GeoElements Lab for their guidance; Cristian Moran for near-peer support; Luke Smith for simulation environment support; and Rosalia Gomez and the TACC education and outreach team for organizing the REU program.

Any opinions, findings, and conclusions or recommendations expressed in this material are those of the author and do not necessarily reflect the views of the National Science Foundation.

---

## Checklist against Instructions.docx.md

| Requirement | Status |
|---|---|
| Full name | Yes, Introduction |
| Major and institution | Yes, Integrated Sciences, Claremont McKenna College |
| REU program named | Yes, NSF REU Site: Cyberinfrastructure Research for Societal Advancement |
| Mentors named | Yes, Kumar, Iqbal, Hsiao. Etter omitted, see [CONFIRM] under Authors |
| Thanks NSF | Yes |
| Thanks UT Austin TACC | Yes, full formal name used |
| Award # 2447887 cited | Yes, verbatim from the instructions |
| Poster size <= 42x60, prefer 42x56 | Not a text item, handle at layout |
| File named Cerrell_TACC_42x56 | Not a text item, handle at export |

---

## Note on the REU program name

`README.md` and `hf_space/README.md` both call this "NSF SCIPE REU 2026". `Instructions.docx.md` calls it "NSF REU Site: Cyberinfrastructure Research for Societal Advancement, Award # 2447887". This draft uses the instructions' wording, since that is the version the program office asked for and the one tied to the award number. The two READMEs may want updating to match, but that is a separate task and was not changed here.
