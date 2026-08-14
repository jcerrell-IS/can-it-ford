"""Turbid-floodwater optical coefficients for the render layer.

SCOPE. Render layer only. Produces coefficients consumed by the shader in
analysis/render_multigeom_shaded.py. Computes no force, changes no verdict,
touches no solver code. warpmpm computes no optics of any kind; these pixels are
an illustration of the simulated free surface, not a simulated radiance field.

WHAT THIS REPLACES. render_multigeom_shaded.py:91-92 carries

    SIGMA_RGB = [0.45, 0.07, 0.03]   # real CLEAR-water absorption, 1/m
    VIS_GAIN  = 9.0                  # display exaggeration, stated in the caption

The clear-water coefficients are right and the exaggeration is honestly
labelled. But the thing being exaggerated is the wrong thing: over a 0.30 m tank
clear water loses about 13 percent of the red and nothing else, so the depth cue
is invisible, and a 9x gain was the available workaround. Real floodwater is not
clear water. Its extinction is dominated by SCATTERING off suspended sediment,
which at realistic flood concentrations exceeds clear-water absorption by one to
two orders of magnitude. Supplying that term removes the need for a fudge factor:
VIS_GAIN can go to 1.0 and the caption can drop the disclaimer.

At zero sediment this module reproduces shaded.py's constants exactly, so it is a
strict generalisation of the existing model rather than a competing one.

MAGNITUDE, AND WHY AN EARLIER DRAFT WAS WRONG. A first draft used a slope of
0.0016 per mg/L per m on the green channel, described as "tuned for visual
plausibility". It is not plausible: it gives c = 0.35 1/m at 120 mg/L, a
black-disc visual range of 13.6 m, i.e. floodwater clearer than a swimming pool.
Two independent routes, computed 2026-08-13, agree it is roughly 45x too
transparent:

  ROUTE A, clarity relationships. Davies-Colley and Smith 2001 give beam
    attenuation c and black-disc visual range y_BD as c * y_BD ~ 4.8, with the
    field relation turbidity(NTU) * y_BD ~ 20 to 50 NTU.m. Taking SSC(mg/L) ~
    turbidity(NTU) to within about 2x for natural sediment, 120 mg/L gives
    y_BD = 0.17 to 0.42 m and c = 11.5 to 28.8 1/m, i.e. c* = 0.096 to 0.24 m2/g.

  ROUTE B, geometric optics. For particles large against the wavelength,
    c = 3*Q*SSC / (2*rho_s*d) with Q ~ 2 and rho_s = 2650 kg/m3. Silt at
    d = 5 to 50 um gives c* = 0.023 to 0.226 m2/g, i.e. c = 2.7 to 27 1/m at
    120 mg/L.

The two overlap on c* ~ 0.1 m2/g, the default below. It sits at the TRANSPARENT
end of the plausible band on purpose: it keeps some depth cue in the frame rather
than rendering a flat opaque slab, and it is the conservative choice when the
grain-size distribution of the modelled flood is not known.

WHERE THE BROWN COMES FROM, PHYSICALLY. Not from the extinction coefficient.
Mineral scattering is near-grey across the visible in this size regime. The
colour enters through the SCATTERING ALBEDO: iron-oxide coatings (hematite,
goethite) absorb strongly below roughly 550 nm via the Fe-O charge-transfer tail
and the Fe(3+) ligand-field transitions, then reflect through a steep edge into
a red/NIR plateau. Brown is dark orange: low reflectance in the blue, a steep
edge at 550 to 600 nm, a high plateau at 600 to 750 nm, all at low luminance.
HUE IS SET BY WHERE THE ABSORPTION EDGE SITS, NOT BY A PEAK.

That distinction is load-bearing, and the source material got it backwards. The
often-quoted "hematite peak 565 nm, goethite 505 and 435 nm" are peaks of the
FIRST DERIVATIVE dR/dlambda, i.e. the steepest points of the absorption edge; at
a genuine reflectance maximum dR/dlambda is zero by definition. Taken as
reflectance maxima those three numbers predict yellow-green, green-cyan and
violet-blue, so the chain "these are the peaks, therefore brown" does not merely
skip a step, it points the wrong way. Goethite is yellow-brown PRECISELY BECAUSE
it absorbs at 435 nm. See REFERENCES["iron_oxide_derivative_peaks"].

WHAT IS CHOSEN RATHER THAN DERIVED, do not oversell:
  - c* = 0.10 m2/g is a central value from a band spanning 0.023 to 0.24 m2/g.
    The band is derived; the point within it is a choice. Grain size, the
    dominant control, is not modelled.
  - SEDIMENT_ALBEDO_RGB is a qualitative colour consistent with the cited
    iron-oxide spectral behaviour, NOT a colorimetric conversion of a published
    reflectance spectrum. That would need CIE colour-matching functions and an
    illuminant choice, neither done here.
  - Sediment extinction is taken as spectrally flat. Real sediment has a weak
    wavelength dependence, small against the grain-size uncertainty above.
  - The near-bed profile's length scale is eps_s/w_s, a physical quantity, but it
    is set here by default rather than computed from a settling velocity.

CITATION CORRECTIONS APPLIED 2026-08-13. Every reference below was resolved
against Crossref. Four defects in the source material were corrected here:
  1. Alexandrov et al. 2003 was cited with a title that DOES NOT EXIST at its
     DOI. The DOI, authors, year and journal were right; the title belonged to a
     different 2007 paper. Corrected below.
  2. That paper's 34,000 mg/L was labelled a "physical upper bound". It is a
     six-year MEAN. The same abstract reports individual flood maxima to
     229,000 mg/L, 6.7x higher, so a mean cannot be the bound.
  3. Stewart/Fox/Harnett 2014 was cited as the justification for attenuation
     LINEAR in SSC. That paper reports the opposite: a POWER LAW, explicitly
     naming nonlinearity from particle shadowing and multiple scattering. The
     citation that does support a linear regime is Stewart and Fox 2017, added
     below with its validity bounds.
  4. The near-bed concentration boost was attributed to the Brisbane flood
     report. That campaign measured a FALLING-STAGE TEMPORAL trend, not a
     vertical profile, using one ADV at two non-simultaneous elevations
     confounded with stage; the authors themselves warn the trend "might be
     linked with the change in ADV sampling volume elevation". It cannot support
     a vertical profile. Reattributed below.
"""
from __future__ import annotations

import warnings

import numpy as np

# --------------------------------------------------------------------------
# references
# --------------------------------------------------------------------------

REFERENCES = {
    "beer_lambert_depth":
        "Stewart, R. L., Fox, J. F., & Harnett, C. K. (2013). Dimensionless "
        "Light Attenuation Number for Modeling Suspended Sediment Concentration "
        "in Open Channels. In World Environmental and Water Resources Congress "
        "2013 (pp. 1698-1708). ASCE. doi:10.1061/9780784412947.167. "
        "CONFERENCE PROCEEDINGS, not a journal article. Supports the "
        "exponential decay with PATH LENGTH; makes no linear-in-SSC claim.",
    "linear_in_ssc":
        "Stewart, R. L., & Fox, J. F. (2017). Light Attenuation Model for "
        "Waters: Linear and Nonlinear Dependencies on Suspended Sediment. "
        "Journal of Hydraulic Engineering, 143(9). "
        "doi:10.1061/(ASCE)HY.1943-7900.0001343. About 90 percent of their data "
        "is linear. VALIDITY: particle size 9 to 90 um, SSC 0 to 670 mg/L.",
    "nonlinear_warning":
        "Stewart, R. L., Fox, J. F., & Harnett, C. K. (2014). Estimating "
        "Suspended Sediment Concentration in Streams by Diffuse Light "
        "Attenuation. Journal of Hydraulic Engineering, 140(8), 04014033. "
        "doi:10.1061/(ASCE)HY.1943-7900.0000887. Reports attenuation varying "
        "NONLINEARLY with SSC as a power law, from particle shadowing and "
        "multiple scattering. Cited here as the bound on the linear model, NOT "
        "as support for it.",
    "scattering_not_absorption":
        "Davies-Colley, R. J., & Smith, D. G. (2001). Turbidity, Suspended "
        "Sediment, and Water Clarity: A Review. JAWRA, 37(5), 1085-1101. "
        "doi:10.1111/j.1752-1688.2001.tb03624.x. Establishes that the effect is "
        "SCATTERING-dominated and that BEAM ATTENUATION (absorption + "
        "scattering), not absorption alone, is the right coefficient; and the "
        "c * y_BD ~ 4.8 clarity relation used as a sanity check below. NOTE: "
        "registry records carry an OCR-corrupted title; the form above is "
        "correct. Citation counts for this paper range 540 to 679 across "
        "databases, so do not quote a single figure.",
    "amazon_optics":
        "Martinez, J. M., Espinoza-Villar, R., Armijos, E., & Silva Moreira, L. "
        "(2015). The optical properties of river and floodplain waters in the "
        "Amazon River Basin: Implications for satellite-based measurements of "
        "suspended particulate matter. JGR Earth Surface, 120, 1274-1287. "
        "doi:10.1002/2014JF003404. SPM range 5-620 g/m3. Reflectance saturation "
        "near 100 g/m3 applies BLUE TO RED ONLY; the same abstract reports no "
        "Kd saturation from green to NIR.",
    "urban_stormwater_ssc":
        "McKee, L. J., & Gilbreath, A. N. (2015). Concentrations and loads of "
        "suspended sediment and trace element pollutants in a small semi-arid "
        "urban tributary, San Francisco Bay, California. Environmental "
        "Monitoring and Assessment, 187. doi:10.1007/s10661-015-4710-4. "
        "Measured SSC 1.4 to 2700 mg/L, varying with storm intensity.",
    "urban_road_flood_ssc":
        "Brown, R., & Chanson, H. (2012). Suspended sediment properties and "
        "suspended sediment flux estimates in an inundated urban environment "
        "during a major flood event. Water Resources Research, 48(11). "
        "doi:10.1029/2012WR012381. Mean SSC rose from about 6 to more than "
        "20 kg/m3 (6,000 to 20,000 mg/L) over the event, instantaneous "
        "estimates 5 to 60 kg/m3, median particle size about 25 um. This is an "
        "ACTUAL FLOODED URBAN ROAD next to Brisbane's CBD, the closest "
        "published analogue to the modelled scenario.",
    "urban_road_flood_report":
        "Brown, R., Chanson, H., McIntosh, D., & Madhani, J. (2011). Turbulent "
        "Velocity and Suspended Sediment Concentration Measurements in an Urban "
        "Environment of the Brisbane River Flood Plain at Gardens Point on "
        "12-13 January 2011. Hydraulic Model Report No. CH83/11, School of "
        "Civil Engineering, The University of Queensland, 120 pages. No DOI "
        "(grey literature); UQ eSpace handle UQ:243550. Its SSC-versus-depth "
        "finding is a FALLING-STAGE TEMPORAL trend, not a vertical profile.",
    "flash_flood_ssc":
        "Alexandrov, Y., Laronne, J. B., & Reid, I. (2003). Suspended sediment "
        "concentration and its variation with water discharge in a dryland "
        "ephemeral channel, northern Negev, Israel. Journal of Arid "
        "Environments, 53(1), 73-84. doi:10.1006/jare.2002.1020. Six-year MEAN "
        "SSC 34,000 mg/L, with individual flood maxima 21,000 to 229,000 mg/L.",
    "vertical_profile":
        "Rouse, H. (1937). Modern Conceptions of the Mechanics of Fluid "
        "Turbulence. Transactions of the ASCE, 102, 463-505. "
        "doi:10.1061/TACEAT.0004872. Origin of the Rouse profile and Rouse "
        "number, the standard description of near-bed sediment enrichment. See "
        "also Garcia, M. H., ed. (2008), Sedimentation Engineering, ASCE MOP "
        "110, doi:10.1061/9780784408148.",
    "iron_oxide_absorption_edge":
        "Schneider, I. L., Teixeira, E. C., Rolim, S. B. A., & Hallouche, B. "
        "(2015). Study of Reflectance Spectroscopy in River Sediments. "
        "International Journal of Advanced Remote Sensing and GIS, 4(1), "
        "1271-1285. doi:10.23953/cloud.ijarsg.117. NOTE the first author is "
        "Ismael L. Schneider; 'I. A. H. Schneider' is a different UFRGS "
        "researcher and was wrong in the source material. The paper reports "
        "iron-oxide features as ABSORPTION features (its abstract says 470-580 "
        "and 650-850 nm; its own body text at p.1281 says 470-600 nm and a "
        "'concavity' at 850 nm, so the two disagree and the abstract is the "
        "weaker source). Measured on DRIED, SIEVED, ORGANIC-STRIPPED bulk "
        "sediment powder, not a suspension in a water column.",
    "iron_oxide_derivative_peaks":
        "Li, C., & Yang, S. (2012). Hematite and Goethite Distribution in the "
        "Yangtze River Sediments by Using Diffused Reflectance Spectroscopy. "
        "Earth Science (Journal of China University of Geosciences), 37(S1), "
        "11-19. The publisher displays DOI 10.3799/dqkx.2012.S1.002 but it DOES "
        "NOT RESOLVE (404 at doi.org, Crossref and DataCite), so cite volume and "
        "pages. NOTE the source material credited this to 'Yang S' alone; Yang "
        "Shou-ye is the SECOND author and Li Chao the first. CRITICAL "
        "MEASURAND CAVEAT: the 565 nm hematite and 505/435 nm goethite figures "
        "are peaks of the FIRST DERIVATIVE dR/dlambda, not reflectance maxima. "
        "A dR/dlambda maximum is the steepest point of the absorption EDGE; at "
        "a true reflectance maximum dR/dlambda is zero by definition. Read as "
        "reflectance peaks these numbers predict yellow-green, green-cyan and "
        "VIOLET-BLUE, i.e. the opposite of the observed colour.",
    "turbid_vs_clear_response":
        "Bartolucci, L. A., Robinson, B. F., & Silva, L. F. (1977). Field "
        "measurements of the spectral response of natural waters. "
        "Photogrammetric Engineering and Remote Sensing, 43. No DOI exists "
        "(pre-digital); NASA NTRS record 19770050800. Reports turbid river "
        "water at 99 mg/L having about 6 percent higher response than clear "
        "lake water at 10 mg/L in the red (0.6-0.7 um) and NIR (0.7-0.9 um). "
        "TWO CAUTIONS: 'about 6 percent' is unit-ambiguous in the source "
        "itself (reflectance points vs relative percent), so it must not be "
        "converted into an RGB multiplier; and the NIR half is invisible in a "
        "visible-light render because pure water absorption rises by roughly "
        "two orders of magnitude from 600 to 800 nm. Its depth finding is also "
        "commonly INVERTED in secondary sources: the source says the river "
        "bottom did NOT influence the spectral response once the water was "
        "DEEPER than 30 cm, and that holds for the 99 mg/L turbid river, not "
        "for water generally.",
    "geometric_optics_route":
        "Guillen, J., Palanques, A., Puig, P., Durrieu de Madron, X., & "
        "Nyffeler, F. (2000). Field calibration of optical sensors for "
        "measuring suspended sediment concentration in the western "
        "Mediterranean. Scientia Marina, 64(4), 427-435. "
        "doi:10.3989/scimar.2000.64n4427. Diamond open access, CC-BY; the PDF "
        "was retrieved and read directly on 2026-08-14 (sha256 98f0f082cd64...). "
        "ADDED 2026-08-14 as the PRIMARY SOURCE for this module's ROUTE B, "
        "which the docstring previously stated with no citation. Their eq. 4 is "
        "SSC = (2 rho_s D / 3Q) alpha_p = B alpha_p, after Spinrad et al. 1983, "
        "i.e. the same relation inverted, with B the calibration slope in g/m2 "
        "and c* = 1/B. Their eq. 5 gives B = k D with k = 1.12 to 3.4 from "
        "laboratory calibrations across grain-size fractions (Moody et al. "
        "1987; Wiberg et al. 1994), so c* falls as grain size rises, which is "
        "the mechanism this module already invokes for field sublinearity. "
        "MEASURED VALUES: BAC 0.4 to 14 1/m across six western-Mediterranean "
        "campaigns; the per-campaign slope B runs 1.32 to 1.71 g/m2 and the "
        "pooled fit is SSC = 1.43 alpha_(p+w) - 0.26, r2 = 0.85, stated as "
        "representative of shelf and slope areas that 'usually have suspended "
        "sediment concentrations lower than 5 mg/l'. Their separate FTU "
        "calibration spans 0.1 to 700 mg/L with slopes 0.24 to 1.71.",
    "colour_gap":
        "NO PRIMARY SOURCE IN THIS SET MEASURES THE COLOUR OF A SEDIMENT "
        "SUSPENSION IN A WATER COLUMN, which is what a fluid shader needs. Two "
        "of the three measure dried mineral powder, whose reflectance is an "
        "upper bound on suspension colour, not equal to it; the third reports "
        "magnitude rather than colour and no mineralogy. Cited honestly they "
        "support only: iron oxides absorb short wavelengths and reflect long "
        "ones, and turbid water is brighter than clear water in the red. That "
        "is CONSISTENT WITH a brown/tan render but does not derive one. "
        "SEDIMENT_ALBEDO_RGB remains a chosen colour.",
}

# --------------------------------------------------------------------------
# suspended-sediment concentrations, from measured field ranges
# --------------------------------------------------------------------------

SSC_PRESET_MG_L = {
    "clear_baseline": 10.0,
    "moderate_flood": 120.0,
    "severe_flood": 1800.0,
    "urban_road_flood": 13000.0,
    "extreme_bound": 34000.0,
}

SSC_PRESET_SOURCE = {
    "clear_baseline":
        "Low end of the Amazon-basin SPM range, Martinez et al. 2015 "
        "(1 g/m3 = 1 mg/L exactly).",
    "moderate_flood":
        "Low-to-mid of the measured urban storm-flow range, McKee and "
        "Gilbreath 2015 (1.4 to 2700 mg/L).",
    "severe_flood":
        "Near the upper end of that same measured urban storm-flow range.",
    "urban_road_flood":
        "Midpoint of the 6,000 to 20,000 mg/L event-mean rise measured on an "
        "actually flooded urban road, Brown and Chanson 2012. THIS IS THE "
        "CLOSEST PUBLISHED ANALOGUE to the modelled scenario and is the "
        "defensible default if the scene depicts a flooded city street.",
    "extreme_bound":
        "Six-year MEAN for semiarid flash floods, Alexandrov et al. 2003. NOT "
        "an upper bound: the same source reports individual flood maxima to "
        "229,000 mg/L.",
}

DEFAULT_PRESET = "moderate_flood"

# --------------------------------------------------------------------------
# extinction
# --------------------------------------------------------------------------

# Clear-water absorption, 1/m, red absorbed hardest. Identical to
# render_multigeom_shaded.py:91 so the two models agree in the zero-sediment
# limit.
CLEAR_WATER_SIGMA_RGB = np.array([0.45, 0.07, 0.03])

# Mass-specific beam attenuation of suspended sediment, m2/g, bounded by the two
# routes in the module docstring. Near-grey across the visible.
#
# STILL A CHOSEN VALUE, NOT A PUBLISHED REGRESSION, and a 2026-08-14 retrieval
# attempt is the reason that sentence has not changed. The primary source for
# ROUTE B was found and read in full (Guillen et al. 2000, see
# REFERENCES["geometric_optics_route"]), which is a real gain: the equation now
# has a citation it did not have. It did NOT settle the coefficient, because the
# retrieved numbers bracket this default from BOTH sides rather than confirming
# it, and the spread is a factor of about 60:
#
#   their pooled field fit, B = 1.43 g/m2                 -> c* = 0.699 m2/g
#   their per-campaign range, B = 1.32 to 1.71 g/m2       -> c* = 0.585 to 0.758
#   their eq. 5 at 25 um, the median grain size Brown and
#     Chanson 2012 measured on the flooded Brisbane road,
#     with k = 1.12 to 3.4                                -> c* = 0.012 to 0.036
#   their eq. 4 direct, rho_s 2650 kg/m3, Q = 2, 25 um    -> c* = 0.045
#
# The field fit is 7.0x ABOVE this default and the grain-size relation at the
# scenario's own grain size is 2.2 to 8.5x BELOW it, so quoting either as "the"
# published value would be worse than quoting a chosen central one. The
# divergence is not a contradiction: their fit is for marine shelf water usually
# under 5 mg/L carrying fine river sediment, and c* ~ 1/D means coarser flood
# load attenuates less per gram. 0.10 stays, still labelled chosen.
#
# Stewart and Fox 2017, the paper that would answer this directly for streams,
# is CLOSED ACCESS: Scite returns contentDenied with no full-text excerpts, and
# the only access route offered is purchase. Marked unretrieved rather than
# guessed. Undermind was also tried and its token had expired.
#
# RENDER CONSEQUENCE, so the open question is scoped rather than alarming: over
# this scene's 0.30 m column at the default camera the image is optically
# SATURATED at about 140 mg/L, so at the severe_flood and urban_road_flood
# presets every c* in the range above renders the identical picture. The choice
# only moves pixels at clear_baseline, and at moderate_flood it moves them for
# this default but not for the higher field value.
SEDIMENT_CSTAR_M2_PER_G = 0.10
SEDIMENT_CSTAR_BAND_M2_PER_G = (0.023, 0.24)
SEDIMENT_SPECTRAL_SHAPE = np.array([1.0, 1.0, 1.0])

# Above this concentration the linear-in-SSC regime is an EXTRAPOLATION.
#
# WHAT THE BOUND IS. 670 mg/L is the upper end of Stewart and Fox 2017's
# CALIBRATION DATASET (with grain size 9 to 90 um), over which about 90 percent
# of their data was linear. It is an empirical range statement, not a measured
# physical threshold where a mechanism switches on.
#
# WHAT THE BOUND IS NOT, corrected 2026-08-13 after an adversarial check refuted
# the earlier wording. This constant previously said the nonlinearity comes from
# "particle shadowing and multiple scattering", i.e. optical crowding. That is
# not the operative mechanism at these concentrations, and the reasoning behind
# it was wrong twice:
#   (a) Scattering dominance does not imply nonlinearity. Under independent
#       scattering c = N <Q_ext pi r^2>, so c is proportional to N for ANY split
#       between scattering and absorption. Linearity is controlled by optical
#       crowding, not by which process dominates.
#   (b) These concentrations are mostly not crowded. Particle volume fraction is
#       SSC/rho_s: 2.53e-4 at 670 mg/L, 23.7x below the ~6e-3 independent-
#       scattering threshold, and still 4.91e-3 (just under it) at the 13,000
#       mg/L urban preset. Near-field particle interaction is therefore ruled
#       out for every preset EXCEPT extreme_bound, which at 34,000 mg/L reaches
#       1.28e-2 and genuinely IS crowded, about 2.1x past the threshold. So the
#       crowding argument acquits the presets that matter and does not acquit
#       extreme_bound; that preset is a context figure, not a render default.
# The likely driver of the sublinearity actually MEASURED in field data is a
# GRAIN-SIZE CONFOUND, not optics: since c* ~ 3Q/(2 rho_s d), c* falls from
# 0.226 to 0.013 m2/g across d = 5 to 90 um, and high-SSC events carry coarser
# load, so c* drops as SSC rises. A second mechanism the crowding argument does
# NOT eliminate is multiple scattering along the path with a finite-acceptance-
# angle detector re-collecting forward-scattered photons, which at optical depth
# ~20 is a real effect but belongs to the measurement geometry rather than to
# the intrinsic coefficient.
#
# RENDER CONSEQUENCE: NONE. At the bound, optical depth over a 0.30 m column is
# 20.1 and transmittance is 1.8e-9. Even assuming a sublinear power law that
# makes this model over-predict c by 3.3x at 13,000 mg/L, transmittance moves
# between 4e-170 and 2e-52, both far below one 8-bit level (3.9e-3). The
# nonlinearity cannot change a pixel. The guard exists so the coefficient is not
# QUOTED as sourced outside its calibration range, not because the image is wrong.
LINEAR_REGIME_MAX_SSC_MG_L = 670.0
LINEAR_REGIME_GRAIN_UM = (9.0, 90.0)

# Scattering albedo endpoints. Clear water scatters weakly and blue-green; the
# sediment endpoint is the brown-tan of iron-oxide-coated mineral particles.
CLEAR_SCATTER_RGB = np.array([0.020, 0.160, 0.200])   # matches shaded.py:94
SEDIMENT_ALBEDO_RGB = np.array([0.340, 0.235, 0.130])

# Molecular (Rayleigh) scattering of pure water, 1/m, at nominal RGB wavelengths
# 650 / 550 / 450 nm. b_w(550) ~ 0.0019 1/m with a lambda^-4.32 shape, Morel 1974.
# Blue scatters most, which is why clear water is blue-green.
WATER_SCATTER_RGB = np.array([0.00090, 0.00190, 0.00452])

# NOTE ON AN ANCHOR THAT WAS REMOVED. An earlier version mixed the scattered
# light colour by SSC / (SSC + 100 mg/L), anchoring the 100 to the reflectance
# saturation Martinez et al. 2015 report near 100 g/m3. That was wrong twice
# over. First, their saturation is stated for BLUE THROUGH RED only, and the same
# abstract reports no Kd saturation from green to NIR. Second, and more
# fundamentally, a saturating REFLECTANCE curve describes how BRIGHT the water
# gets, not how its colour divides between two scattering populations. The
# physically correct weight is the ratio of scattering coefficients, which needs
# no fitted constant at all, and is what `sediment_fraction` now returns. The
# practical consequence is large: at 120 mg/L the old form gave a 0.545 mix and
# rendered a neutral olive, while the scattering ratio gives 0.9998 and renders
# the brown that muddy water actually is.


def check_linear_regime(ssc_mg_l, warn=True):
    """True if SSC is inside the published linear-in-SSC regime.

    Returns a bool (or bool array). Emits a UserWarning once per call when any
    value is outside, because silently extrapolating past a documented
    nonlinearity is exactly the kind of thing that should not be quiet.
    """
    s = np.asarray(ssc_mg_l, float)
    ok = s <= LINEAR_REGIME_MAX_SSC_MG_L
    if warn and not np.all(ok):
        warnings.warn(
            "SSC up to %.0f mg/L is outside the %.0f mg/L calibration range of "
            "Stewart and Fox 2017, so the linear coefficient is EXTRAPOLATED "
            "and must not be quoted as sourced here. Field data go sublinear "
            "above this, most likely because coarser load at higher SSC lowers "
            "c*, so this model probably OVER-predicts extinction. The render is "
            "unaffected either way: transmittance is already below one 8-bit "
            "level at the bound."
            % (float(np.max(s)), LINEAR_REGIME_MAX_SSC_MG_L),
            UserWarning, stacklevel=2)
    return ok


def sediment_extinction_rgb(ssc_mg_l, cstar=SEDIMENT_CSTAR_M2_PER_G, warn=True):
    """Sediment contribution to beam attenuation, 1/m.

    c = c* [m2/g] * SSC [g/m3] -> 1/m. SSC in mg/L is numerically g/m3.

    Scalar SSC returns shape (3,); an (N,) array returns (N, 3).

    BROADCASTING BUG, fixed 2026-08-13. This previously read
    `SEDIMENT_SPECTRAL_SHAPE * (cstar * asarray(ssc))`, which multiplies a (3,)
    spectral vector by an (N,) concentration array. That raises for every N
    except 1 and 3, and for N = 1 or 3 it SILENTLY returns shape (3,), treating
    one concentration per COLOUR CHANNEL instead of one per particle. The unit
    test that was supposed to catch it passed a 3-element array, so it exercised
    exactly the size that fails silently. The explicit `[..., None]` below makes
    the particle axis and the channel axis independent.
    """
    check_linear_regime(ssc_mg_l, warn=warn)
    ssc = np.asarray(ssc_mg_l, float)[..., None]
    return SEDIMENT_SPECTRAL_SHAPE * (float(cstar) * ssc)


def extinction_coefficient_rgb(ssc_mg_l, cstar=SEDIMENT_CSTAR_M2_PER_G, warn=True):
    """Total beam attenuation (clear-water absorption + sediment scattering), 1/m.

    This is the coefficient that belongs in the Beer-Lambert term of a
    single-scattering renderer: it governs how fast the BOTTOM disappears. The
    light removed from that beam is not lost, it is re-scattered toward the
    viewer, which is what `scatter_albedo_rgb` supplies. Using beam attenuation
    rather than absorption alone is the choice Davies-Colley and Smith 2001
    argue for.
    """
    return CLEAR_WATER_SIGMA_RGB + sediment_extinction_rgb(ssc_mg_l, cstar, warn)


# Backwards-compatible alias for the original module's entry point.
attenuation_coefficient_rgb = extinction_coefficient_rgb


def transmittance(path_m, ssc_mg_l, cstar=SEDIMENT_CSTAR_M2_PER_G, warn=True):
    """Beer-Lambert transmittance over a geometric path length in metres.

    Shapes: k is (..., 3) and path is (...), so the path needs its own trailing
    axis before they multiply. Without it an (N,) path against an (N,) SSC
    raises, which is the same broadcasting class as the bug fixed in
    `sediment_extinction_rgb`; it is written explicitly here so the pair cannot
    drift apart again.
    """
    k = extinction_coefficient_rgb(ssc_mg_l, cstar, warn)
    path = np.asarray(path_m, float)
    if np.ndim(k) > np.ndim(path):
        path = path[..., None]
    return np.exp(-k * path)


def sediment_fraction(ssc_mg_l, cstar=SEDIMENT_CSTAR_M2_PER_G):
    """Per-channel share of total scattering contributed by sediment.

    f = b_sediment / (b_sediment + b_water). No fitted constant: both terms are
    scattering coefficients. Returns shape (..., 3), since water's molecular
    scattering is strongly wavelength dependent while sediment's is near-grey.

    Sediment overwhelms molecular scattering at any realistic flood
    concentration: even 10 mg/L gives f > 0.995 in every channel. That is the
    correct physical answer, and it means the scattered-light colour is
    sediment's, not water's, as soon as there is meaningful sediment at all.
    """
    b_sed = SEDIMENT_SPECTRAL_SHAPE * (float(cstar)
                                       * np.asarray(ssc_mg_l, float)[..., None])
    return b_sed / (b_sed + WATER_SCATTER_RGB)


def scatter_albedo_rgb(ssc_mg_l, cstar=SEDIMENT_CSTAR_M2_PER_G):
    """Colour of light scattered back out of the water column.

    Replaces the fixed teal SCATTER_RGB at render_multigeom_shaded.py:94. At
    zero sediment it returns that same teal exactly, so this is a strict
    generalisation of the existing model rather than a competing one.
    """
    f = sediment_fraction(ssc_mg_l, cstar)
    return (1.0 - f) * CLEAR_SCATTER_RGB + f * SEDIMENT_ALBEDO_RGB


def visual_range_m(ssc_mg_l, cstar=SEDIMENT_CSTAR_M2_PER_G, warn=False):
    """Black-disc visual range, m, from c * y_BD ~ 4.8 (Davies-Colley and Smith
    2001). A sanity check: a coefficient set implying metres of visibility in
    muddy floodwater is wrong, and this makes that visible at a glance."""
    return 4.8 / extinction_coefficient_rgb(ssc_mg_l, cstar, warn)[1]


# --------------------------------------------------------------------------
# vertical structure
# --------------------------------------------------------------------------

VERTICAL_PROFILE_BASIS = (
    "Suspended sediment is enriched toward the bed. The standard description is "
    "the Rouse profile (Rouse 1937), a POWER law. The exponential used here is "
    "the exact equilibrium solution of the same suspension balance for a "
    "DEPTH-UNIFORM eddy diffusivity, C(z) = C_a exp(-w_s (z - a) / eps_s), so "
    "its length scale is the physical quantity eps_s / w_s, not a free knob. "
    "It is preferred here only because it is bounded and cheap. An earlier "
    "draft attributed this profile to the Brisbane flood report; that campaign "
    "measured a falling-stage TEMPORAL trend with one ADV at two "
    "non-simultaneous elevations confounded with stage, and its authors warn "
    "the trend 'might be linked with the change in ADV sampling volume "
    "elevation'. It cannot support a vertical profile and no longer does."
)


def near_bed_ssc(ssc_bulk_mg_l, height_above_floor_m, water_depth_m=None,
                 bed_boost=1.6, boost_length_scale_m=0.10):
    """Local SSC given a DEPTH-AVERAGED bulk value and height above the bed.

    NOT WIRED INTO ANY RENDER PATH as of 2026-08-13, verified by grep: the shader
    takes a single bulk SSC. This is stated explicitly because a parameter that
    exists, looks physical and is silently never used is exactly the trap
    CLAUDE.md item 4 records for inertia_kg_m2 and cg_height_m. Do not describe
    a render as carrying a vertical concentration profile.

    Wiring it in would also change nothing visible: at moderate_flood the column
    transmittance is already 0.027, so a 1.6x near-bed enrichment is far below
    the threshold of visibility. It is kept for depth-resolved analysis, not for
    the shader.

    Monotone decreasing in height, so concentration is highest at the bed.

    NORMALISED, unlike the first draft. That version multiplied by a boost
    decaying to 1.0, which made `ssc_bulk_mg_l` the FAR-FIELD value rather than
    the mean, so the column average came out above the named preset and silently
    broke the tie between the presets and the measured concentrations they cite.
    When `water_depth_m` is given, the profile is renormalised so its
    depth-average equals `ssc_bulk_mg_l` exactly.
    """
    z = np.asarray(height_above_floor_m, float)
    L = float(boost_length_scale_m)
    shape = 1.0 + (bed_boost - 1.0) * np.exp(-z / L)
    if water_depth_m is not None:
        H = float(water_depth_m)
        if H > 0:
            # mean over [0, H] of 1 + (b-1) exp(-z/L)
            mean_shape = 1.0 + (bed_boost - 1.0) * (L / H) * (1.0 - np.exp(-H / L))
            shape = shape / mean_shape
    return np.asarray(ssc_bulk_mg_l, float) * shape


# Backwards-compatible alias for the original module's entry point.
depth_graded_ssc = near_bed_ssc


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def preset_ssc(name=DEFAULT_PRESET):
    if name not in SSC_PRESET_MG_L:
        raise KeyError("unknown SSC preset %r, have %s"
                       % (name, sorted(SSC_PRESET_MG_L)))
    return SSC_PRESET_MG_L[name]


def describe(name=DEFAULT_PRESET, cstar=SEDIMENT_CSTAR_M2_PER_G):
    """One-line provenance string for a caption or manifest."""
    ssc = preset_ssc(name)
    k = extinction_coefficient_rgb(ssc, cstar, warn=False)
    extrap = "" if ssc <= LINEAR_REGIME_MAX_SSC_MG_L else \
        " EXTRAPOLATED above the %.0f mg/L linear-regime bound." % LINEAR_REGIME_MAX_SSC_MG_L
    return ("SSC %g mg/L (%s); beam attenuation sigma_rgb = [%.2f, %.2f, %.2f] "
            "1/m = clear-water absorption + c* %.3f m2/g x SSC; black-disc "
            "visual range %.2f m. No display exaggeration.%s"
            % (ssc, name, k[0], k[1], k[2], cstar,
               visual_range_m(ssc, cstar), extrap))


def provenance():
    """Full reference block for a manifest sidecar."""
    return {
        "model": "Beer-Lambert beam attenuation, linear in SSC, "
                 "single-scattering albedo mix",
        "cstar_m2_per_g": SEDIMENT_CSTAR_M2_PER_G,
        "cstar_band_m2_per_g": SEDIMENT_CSTAR_BAND_M2_PER_G,
        "linear_regime_max_ssc_mg_l": LINEAR_REGIME_MAX_SSC_MG_L,
        "linear_regime_grain_um": LINEAR_REGIME_GRAIN_UM,
        "presets_mg_l": dict(SSC_PRESET_MG_L),
        "preset_sources": dict(SSC_PRESET_SOURCE),
        "references": dict(REFERENCES),
        "vertical_profile_basis": VERTICAL_PROFILE_BASIS,
    }
