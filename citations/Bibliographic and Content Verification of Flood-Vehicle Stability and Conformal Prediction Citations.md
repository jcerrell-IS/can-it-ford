# Bibliographic and Content Verification Report: Flood-Vehicle Stability and Conformal Prediction Citations

## TL;DR

- Two of the seven cited references contain material bibliographic errors: the **Azhar et al. (2023)** citation uses an incorrect title and wrong first-author initials, and **SAE 1999-01-1336** is a 496-vehicle NHTSA parameter database, not a matched three-vehicle SSF study — the “1.43 sedan / 1.04 SUV / 1.19 pickup matched set” framing is contradicted.
- The **Luo et al. (2024)** conformal-prediction paper is verified as purely a warning-system paper (driver alerts + robotic grasping) and cannot support any physically-viable-world-model, Gaussian-splatting, or Material-Point-Method claim; the friction values in **Xiong et al. (2024)** (μwet=0.3, μdry=0.68 baseline) and the D×V limits attributed to **Shand et al. (2011)** (0.30/0.45/0.60 m²/s) are confirmed.
- All seven DOIs are **clean** — no retraction, correction, or erratum notices in Crossref (empty `relation` field, no `update-to`). The Smith, Modra & Felder (2019) Equation (6) could not be retrieved verbatim, but the evidence strongly rules out the alleged “0.05 m lateral displacement” mis-citation: the paper’s equations are velocity/Froude/force relations.

## Key Findings

Verdicts by item: (1) CONFIRMED; (2) CONTRADICTED (bibliographic) + PARTIALLY CONFIRMED (0.55 value); (3) CONFIRMED (friction) + PARTIALLY CONFIRMED (model claim); (4) CONTRADICTED; (5) PARTIALLY CONFIRMED (prior art exists for the physics, but not the exact “structural blind-spot” framing); (6) CONFIRMED (values + disclaimer) / NOT VERIFIED (exact table/page); (7) CONTRADICTED (the 0.05 m mis-citation) / NOT FOUND (verbatim Eq. 6); (8) all CLEAN.

## Details

### ITEM 1 — Luo et al. (2024) conformal prediction paper — scope check

**(a) Bibliographic verification: MATCH.** Crossref confirms every detail exactly. Authors: Rachel Luo, Shengjia Zhao, Jonathan Kuck, Boris Ivanovic, Silvio Savarese, Edward Schmerling, Marco Pavone.  Title: “Sample-efficient safety assurances using conformal prediction.” *The International Journal of Robotics Research*, volume 43, issue 9, pages 1409–1424. DOI 10.1177/02783649231221580.  Published in print August 2024 (online 17 December 2023). Affiliation: Stanford University (Kuck at Dexterity, Inc.). Funded by NASA University Leadership Initiative (80NSSC20M016). 

**(b) Direct quote of scope (abstract):** “When deploying machine learning models in high-stakes robotics applications, the ability to detect unsafe situations is crucial. Early warning systems can provide alerts when an unsafe situation is imminent (in the absence of corrective action)… we present a framework that combines a statistical inference technique known as conformal prediction with a simulator of robot/environment dynamics, in order to tune warning systems to provably achieve an ε false negative rate using as few as 1/ε data points. We apply our framework to a driver warning system and a robotic grasping application, and empirically demonstrate the guaranteed false negative rate while also observing a low false detection (positive) rate.” 

The paper contains **no content** relating to (a) query-conditioned physically viable world models (PVWM), (b) Gaussian splatting, or (c) Material Point Method simulation. Its 43 references are entirely in conformal prediction, robotics, and grasping. The applications are strictly a driver warning system and robotic grasping.

**(c) VERDICT: CONFIRMED (as suspected).** This paper CANNOT support a PVWM framework citation, nor any Gaussian-splatting or Material Point Method claim. It can only legitimately support a conformal-prediction methodology/validation citation (e.g., the “as few as 1/ε data points” sample-efficiency result relevant to an N≥19 conformal-prediction workflow).

### ITEM 2 — Azhar et al. (2023) — friction coefficient 0.55 check

**(a) Bibliographic verification: DISCREPANCY (two errors).**

- **Title is wrong.** The citation gives “Confirmation of vehicle stability criteria for flood conditions using different pairs of hydrodynamic and stability parameters.” The actual title per Crossref/Wiley is **“Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements.”** 
- **First author initials are wrong.** The citation gives “Azhar, N.S.” The actual first author is **Fatima Azhar (F. Azhar)**, with co-authors Valentijn R. N. Pauwels and Ha H. Bui (all Monash University).
- Correct: DOI 10.1111/jfr3.12885; *Journal of Flood Risk Management*, volume 16, issue 2, article e12885; 2023 (received 11 July 2022, accepted 11 January 2023, published 24 January 2023). 

**(b) The 0.55 value.** From the full text (methodology / numerical-model setup section): “The vehicle has a COG height of 0.45 m, a weight of 1097 kg and a coefficient of friction of 0.55 in accordance with [prior work].” The value appears as an **adopted model parameter** for the SPH simulation of the 1:14-scale vehicle (COG 0.45 m at 1:1 scale; front/rear weight distribution 60/40). The phrase “in accordance with” indicates it was taken from prior literature rather than being an original, novel measurement produced by the authors’ own scale-model traction testing.

**(c) VERDICT: PARTIALLY CONFIRMED.** The exact value 0.55 does appear in the paper as the friction coefficient used for the vehicle, but it is presented as an adopted/borrowed model input “in accordance with” existing literature, not as an original measured value unique to Azhar et al.’s own testing. The bibliographic citation itself is CONTRADICTED (wrong title, wrong first-author initials).

### ITEM 3 — Xiong et al. (2024) — friction values and vehicle-model validation

**(a) Bibliographic verification: MATCH.** Crossref confirms: Yan Xiong, Qiuhua Liang, Jinhai Zheng, Gang Wang, Xue Tong. “Simulation of the Full-Process Dynamics of Floating Vehicles Driven by Flash Floods.” *Water Resources Research*, volume 60, issue 10, article e2023WR036739 (2024). DOI 10.1029/2023WR036739.  (The citation’s short form “Xiong et al. (2024), Water Resources Research, DOI 10.1029/2023WR036739” is correct.)

**(b) Friction values.** From the full text (sensitivity-analysis section): “the result produced by the 150-vehicle simulation with **μwet = 0.3 and μdry = 0.68** is taken as the baseline for comparison. Four simulations with varying the wet- and dry-bed dynamic friction coefficients are considered, that is, μwet = 0.3, μdry = 0.3; μwet = 0.3, μdry = 0.75; μwet = 0.25, μdry = 0.68; μwet = 0.68, μdry = 0.68 (Gerard, 2006; Gou et al., 2022; Martínez-Gomariz et al., 2017).” So μwet=0.3 and μdry=0.68 are confirmed as the **baseline** friction coefficients (with the other values used only in sensitivity runs).

**Vehicle-model representation.** The model is a **two-way coupled 2D finite-volume shock-capturing shallow-water hydrodynamic model + 3D discrete element method (DEM)**,  NOT smoothed particle hydrodynamics (SPH). From the abstract: “A multi-sphere method is further embedded in the DEM model to better represent vehicle shapes. New calculation modules are further implemented to represent the vehicle entrainment, contact and stopping motions.”   Validation was against the 2004 Boscastle (UK) flash flood: the paper (p.10) records that after the event 84 wrecked cars were recovered from the bridges and streets and a further 32 cars floated out to the harbour (i.e., 116 vehicles), with >100 vehicles reported to have blocked two bridges (citing HR Wallingford, 2005). The paper concludes: “The model well predicts the hydrodynamics, interactive transport process and the final locations of vehicles.” 

**(c) VERDICT: friction values CONFIRMED; vehicle-model claim PARTIALLY CONFIRMED / needs qualification.** The paper does validate a simplified rigid vehicle representation (a rigid multi-sphere clump of overlapping spheres) against a real flood event, but this is done in a **coupled shallow-water/DEM** framework — it is DEM, NOT SPH, and the representation is a “multi-sphere” rigid body rather than literally a “rigid-linked-block.” A citation stating that this paper “validates a simplified rigid vehicle representation for SPH flood modeling” would be inaccurate; “for coupled shallow-water/DEM flood modeling” is correct.

### ITEM 4 — SAE 1999-01-1336 — Static Stability Factor values

**(a) Bibliographic verification: MATCH (authors/year) but the paper’s NATURE contradicts the claim.** Crossref confirms: Gary J. Heydinger, Ronald A. Bixel, W. Riley Garrott, Michael Pyne, J. Gavin Howe, Dennis A. Guenther. “Measured Vehicle Inertial Parameters-NHTSA’s Data Through November 1998.” SAE Technical Paper 1999-01-1336 (1999). DOI 10.4271/1999-01-1336. 

**(b) What the paper actually is.** Per its abstract, the paper is “primarily a printed listing of the National Highway Traffic Safety Administration’s (NHTSA) Light Vehicle Inertial Parameter Database… This paper contains 82 new entries, for a total of 496.”  It plots SSF versus vehicle mass across classes (“Passenger cars, as a class, show the highest SSF values, while SUVs have the lowest”).  It is a **496-vehicle database**, not a matched study of one sedan, one SUV, and one pickup. There is no evidence of a table presenting exactly 1.43 (sedan), 1.04 (SUV), and 1.19 (pickup) as a matched set.

The individual-vehicle nature of these values is confirmed by the companion NHTSA report DOT HS 809 868 (Walz, “Trends in the Static Stability Factor of Passenger Cars, Light Trucks, and Vans,” NHTSA Technical Report, June 2005), which states verbatim in footnote 23: “Literature states 1979–81 Mustang had 1.43 SSF; exact model year of test vehicle not specified.” For the low value, the same report’s SUV table attributes SSF ≈ 1.01 to a 1972–75 Jeep CJ-5 (footnote 57) and defines the 1.04 figure as an average of individual model-year vehicles (footnote 58: “1.04 SSF is average of 1981 (1.033) and 1983 (1.0505) vehicles”). DOT HS 809 868 also frames the class trend as: “Passenger cars, as a group, have the highest average SSF… SUVs have substantially improved their SSF values over time, especially after model year 2000, whereas those of pickup trucks have remained consistent,” with SSF across all types typically ranging from ~1.00 to 1.50 and most passenger cars in the 1.30–1.50 range.

**(c) VERDICT: CONTRADICTED.** The three numbers do not exist as “a matched set from the same study” in this paper. The paper is a large multi-vehicle parameter database; the values map to individual, differing vehicles (1.43 ≈ 1979–81 Ford Mustang; ~1.01–1.04 ≈ Jeep CJ-class), not class-average figures for a sedan/SUV/pickup drawn from one matched experiment. The specific trio 1.43/1.04/1.19 could not be located as a discrete table anywhere in SAE 1999-01-1336.

### ITEM 5 — Buoyancy-blind-spot hypothesis — prior-art search

The underlying **physics** is well established in the peer-reviewed flood-vehicle literature:

- **Teo, Falconer, Lin & Xia (2012), “Investigations of hazard risks relating to vehicles moving in flood”:** “studies have also shown that deep water depths and high velocities can cause as much hazard risk if compare to shallow water depths and low velocities. In fact, it can be seen that deep water and low velocities can cause as much flood damage as shallow water… the downward force is countered by increased buoyancy, whereas increases in the depth lead to a corresponding decrease being required in the velocity.” 
- **Bocanegra & Francés (2021), JFRM, DOI 10.1111/jfr3.12738:** “For slow velocities, the water depths that brought about vehicle destabilization tended to move closer to the values at which the vehicle would float under conditions when water was still.” 
- **Lazzarin, Viero, Molinari, Ballio & Defina (2022), “Flood damage functions based on a single physics- and data-based impact parameter that jointly accounts for water depth and velocity,” *Journal of Hydrology* 607:127485, DOI 10.1016/j.jhydrol.2022.127485:** the depth×velocity (Y·U) product “does not represent any physically relevant principle and requires thresholds on both water depth and velocity to provide a measure of the risk degree in general conditions.” 
- The Australian Rainfall & Runoff guidance itself (via Shand et al. 2011 and Cox et al. 2010) imposes **separate limiting still-water depths** (0.3/0.4/0.5 m) on top of the D×V limits — an implicit acknowledgment that D×V alone does not capture the buoyancy/flotation limit at low velocity.

**(c) VERDICT: PARTIALLY CONFIRMED as prior art.** The general mechanism (buoyancy reduces effective weight → reduces normal force → reduces friction/sliding resistance; deep-slow water can be as dangerous as shallow-fast; D×V alone is insufficient and needs a separate depth cap) is repeatedly and explicitly stated in prior literature and is embedded in operational guidelines via separate buoyancy-depth caps. However, the **specific, sharpened articulation** — that the D×V metric has a *structural blind spot* wherein low velocity keeps the D×V score low even as submerged volume approaches displaced weight (near-buoyancy) — does not appear to have been stated verbatim/explicitly in those exact terms in the peer-reviewed record found. It would be a novel *framing/formalization* of an already-recognized concern rather than a wholly new physical mechanism.

### ITEM 6 — Shand et al. (2011) — D×V table values, final lock

**(a) Bibliographic verification: MATCH.** Shand, T.D., Cox, R.J., Blacka, M.J., & Smith, G.P. (2011). Australian Rainfall and Runoff Revision Project 10: Appropriate Safety Criteria for Vehicles — Literature Review (Stage 2). Report No. P10/S2/020, Water Research Laboratory, UNSW. ISBN 978-0-85825-948-5.

**(b) The D×V values.** Multiple independent sources reproduce the criteria: the stability limit is reached when the product of depth and velocity (D×V) equals **0.30 m²/s for small passenger vehicles, 0.45 m²/s for large passenger vehicles, and 0.60 m²/s for large 4WD vehicles**, with maximum buoyancy depths of 0.3/0.4/0.5 m respectively and a maximum flow velocity of 3.0 m/s for all vehicles (per Martínez-Gomariz et al. review; MDPI *Water* 2024; the NZ Envirolink report; and the ARR guidance).

**Disclaimer language.** These criteria are consistently described as **interim/provisional/draft**. The UNSW WRL Technical Report 2014/07 (Smith et al. 2014) states: “Based on available experimental and analytical data, draft criteria for stationary vehicle stability (Table 4-2) are proposed for three vehicle classes (small passenger, large passenger and 4WD).”  Azhar et al. (2023) label the reproduced figure “Interim safety criteria for stationary vehicles (after Ball et al., 2019; Shand et al., 2011).”  Bocanegra & Francés (2021) note the criteria have a provisional nature, and the MDPI *Water* review states “The AR&R defined a provisional stability criterion for stationary vehicles.” 

**(c) VERDICT: CONFIRMED (values and disclaimer) / NOT VERIFIED (exact table number, page, caption).** The three D×V limits (0.30/0.45/0.60 m²/s) and the interim/provisional/draft character are confirmed through multiple corroborating secondary sources. However, I could not access the primary P10/S2/020 report PDF to confirm that these values appear specifically in “Table 3,” to quote the exact table caption, or to give an exact page number, nor to quote the report’s own verbatim disclaimer sentence. Those specific primary-source locators remain unverified.

### ITEM 7 — Smith, Modra & Felder (2019) — Equation (6) confirmation

**(a) Bibliographic verification: MATCH.** Smith, G.P., Modra, B.D., & Felder, S. (2019). “Full-scale testing of stability curves for vehicles in flood waters.” *Journal of Flood Risk Management*, 12(S2), e12527. DOI 10.1111/jfr3.12527. 

**(b) Equation (6).** The verbatim text of Equation (6) could NOT be retrieved — the Wiley full text is behind bot detection and no open-access copy reproduces the numbered equation. Evidence from the authors’ companion WRL Technical Report 2017/07 (same methodology) shows the analytical framework is a force balance yielding velocity/Froude relations: its equations run F_H > F_F (drag exceeds friction), F_F = μ(W − B − L), F_H = ½ρA C_D v², a combined stability inequality, and the Froude number Fr = V/√(gD). The 2019 journal paper (a longer, renumbered treatment) therefore has an Equation (6) that is most plausibly a limiting/critical velocity or limiting Froude-number relation. The paper defines instability physically as a traction/force condition and documents the “just above the floor pan” buoyancy transition, not a fixed displacement in metres.

**(c) VERDICT on the mis-citation: CONTRADICTED; verbatim equation NOT FOUND.** There is no support for the claim that Equation (6) yields a “0.05 m lateral drift/displacement threshold.” The paper’s equation set consists of velocity/Froude/force relations, and its reported outputs are depth–velocity thresholds (e.g., instability at ~0.15 m depth for a small passenger vehicle in fast-flowing water, ~0.30 m for a 4WD), not a lateral displacement in metres. The specific “0.05 m displacement” reading is therefore almost certainly a mis-citation. However, I cannot present the exact verbatim Equation (6) text or its two bracketing sentences, so that portion of the request is NOT FULLY VERIFIED.

### ITEM 8 — Retraction/correction/erratum sweep

Crossref records were retrieved for all seven DOIs. In every case the `relation` object is empty (`{}`) and there is no `update-to` field, indicating no retraction, correction, or erratum:

- **10.1111/jfr3.12527** (Smith, Modra & Felder 2019) — CLEAN.
- **10.1111/jfr3.12885** (Azhar, Pauwels & Bui 2023) — CLEAN.
- **10.1029/2023WR036739** (Xiong et al. 2024) — CLEAN.
- **10.1007/s11069-013-0889-2** (Xia, Falconer, Xiao & Wang 2014, *Natural Hazards*)  — CLEAN.
- **10.1051/matecconf/201820307003** (Shah, Mustaffa, Kim & Yusof 2018, *MATEC Web Conf.*)  — CLEAN.
- **10.1177/02783649231221580** (Luo et al. 2024) — CLEAN (has a routine SAGE Crossmark update-policy link but no actual update-to notice).
- **10.4271/1999-01-1336** (Heydinger et al. 1999) — CLEAN.

**VERDICT: All seven DOIs CLEAN.** No editorial notices detected.

## Recommendations

1. **Fix the two hard bibliographic errors before publication.** Correct the Azhar citation to its real title (“Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements”) and first author (F. Azhar, not N.S. Azhar). Re-scope any citation to SAE 1999-01-1336 — do not present 1.43/1.04/1.19 as a matched sedan/SUV/pickup set; cite it only as a source of individual measured vehicle inertial/SSF parameters, or cite the vehicle-specific NHTSA reports (e.g., DOT HS 809 868) instead.
1. **Restrict the Luo et al. citation** to conformal-prediction methodology/sample-efficiency (the “1/ε data points” guarantee) and never to any PVWM, Gaussian-splatting, or MPM claim.
1. **Qualify the Xiong et al. citation** as coupled shallow-water/DEM (multi-sphere rigid vehicle), not SPH; the μwet=0.3/μdry=0.68 baseline values are safe to cite.
1. **For the buoyancy blind-spot claim,** position it as a novel *formalization/sharpening* of a recognized concern, and cite the prior art (Teo et al. 2012; Bocanegra & Francés 2021; Lazzarin et al. 2022; ARR’s separate depth caps) to establish that the physics is not new — this protects against a “not novel” reviewer objection while preserving a legitimate contribution claim.
1. **Obtain primary-source confirmation** for two unresolved locators: (a) the exact “Table 3”/page/caption in Shand et al. 2011 P10/S2/020, and (b) the verbatim Equation (6) in Smith, Modra & Felder 2019 — both require authenticated library access to lock down. Benchmark that would change the verdicts: if the primary Shand report shows the values in a table numbered other than 3, or if Smith Eq. (6) turns out to be something other than a velocity/Froude relation, update Items 6 and 7 accordingly.

## Caveats

- Wiley and AGU full texts are protected by bot detection; several quotes rely on indexed snippets and open-access mirrors (Ovid, ResearchGate, institutional repositories) rather than the publisher PDF. Where a quote is from a secondary/mirror source it is noted.
- The Smith, Modra & Felder (2019) Equation (6) was not read verbatim; the conclusion that it is a velocity/Froude relation (and not a 0.05 m displacement) is a strong evidence-based inference from the authors’ companion technical report and the paper’s abstract/results, not a direct reading of the journal PDF.
- The exact table number, page, and caption of the Shand et al. (2011) D×V limits, and the report’s verbatim disclaimer sentence, could not be confirmed from the primary report.
- SSF values 1.43/1.04/1.19 could not be located as a discrete table in SAE 1999-01-1336; the contradiction verdict rests on the paper’s documented structure (a 496-vehicle database) and NHTSA’s attribution of those values to individual vehicles.

## References (APA)

Azhar, F., Pauwels, V. R. N., & Bui, H. H. (2023). Confirmation of vehicle stability criteria through a combination of smoothed particle hydrodynamics and laboratory measurements. *Journal of Flood Risk Management, 16*(2), e12885. <https://doi.org/10.1111/jfr3.12885>

Bocanegra, R. A., & Francés, F. (2021). Assessing the risk of vehicle instability due to flooding. *Journal of Flood Risk Management, 14*(4), e12738. <https://doi.org/10.1111/jfr3.12738>

Heydinger, G. J., Bixel, R. A., Garrott, W. R., Pyne, M., Howe, J. G., & Guenther, D. A. (1999). *Measured vehicle inertial parameters—NHTSA’s data through November 1998* (SAE Technical Paper 1999-01-1336). SAE International. <https://doi.org/10.4271/1999-01-1336>

Lazzarin, T., Viero, D. P., Molinari, D., Ballio, F., & Defina, A. (2022). Flood damage functions based on a single physics- and data-based impact parameter that jointly accounts for water depth and velocity. *Journal of Hydrology, 607*, 127485. <https://doi.org/10.1016/j.jhydrol.2022.127485>

Luo, R., Zhao, S., Kuck, J., Ivanovic, B., Savarese, S., Schmerling, E., & Pavone, M. (2024). Sample-efficient safety assurances using conformal prediction. *The International Journal of Robotics Research, 43*(9), 1409–1424. <https://doi.org/10.1177/02783649231221580>

Shah, S. M. H., Mustaffa, Z., Kim, D. K., & Yusof, K. W. (2018). Instability criteria for vehicles in motion exposed to flood risks. *MATEC Web of Conferences, 203*, 07003. <https://doi.org/10.1051/matecconf/201820307003>

Smith, G. P., Modra, B. D., & Felder, S. (2019). Full-scale testing of stability curves for vehicles in flood waters. *Journal of Flood Risk Management, 12*(S2), e12527. <https://doi.org/10.1111/jfr3.12527>

Xia, J., Falconer, R. A., Xiao, X., & Wang, Y. (2014). Criterion of vehicle stability in floodwaters based on theoretical and experimental studies. *Natural Hazards, 70*(2), 1619–1630. <https://doi.org/10.1007/s11069-013-0889-2>

Xiong, Y., Liang, Q., Zheng, J., Wang, G., & Tong, X. (2024). Simulation of the full-process dynamics of floating vehicles driven by flash floods. *Water Resources Research, 60*(10), e2023WR036739. <https://doi.org/10.1029/2023WR036739>

*Note on non-DOI primary sources referenced but not independently paginated during this research:* Shand, T. D., Cox, R. J., Blacka, M. J., & Smith, G. P. (2011). *Australian Rainfall and Runoff Revision Project 10: Appropriate safety criteria for vehicles — Literature review (Stage 2)* (Report No. P10/S2/020). Water Research Laboratory, UNSW. ISBN 978-0-85825-948-5. Walz, M. C. (2005). *Trends in the static stability factor of passenger cars, light trucks, and vans* (Report No. DOT HS 809 868). NHTSA. These two documents were verified via multiple corroborating secondary citations rather than direct full-text retrieval.