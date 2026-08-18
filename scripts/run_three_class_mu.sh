#!/bin/bash
# ============================================================================
# ARM MU: does the large_4wd STUCK verdict survive the friction assumption?
# NON-CANONICAL.
#
# WHY THIS IS NOT OPTIONAL. The canonical floor_friction = 0.55 is a MEASURED
# value, but of a LAB RUBBER MAT used as a road-surface proxy, measured with a
# spring balance by Azhar, Pauwels and Bui (2023): "a rubber mat has been used as
# a representative of the road surface with a wet coefficient of friction of
# 0.55." Its provenance chain is clean but general-automotive, not flood and not
# submerged: Azhar -> Wong, Theory of Ground Vehicles (2008), wet asphalt peak
# 0.50-0.70 / sliding 0.45-0.60 -> SAE 690214, Harned, Johnston and Scharpf 1969,
# a General Motors tyre brake-force study.
#
# 0.55 IS NEARLY DOUBLE THE FLOOD-SAFETY CONVENTION. The flood-vehicle-stability
# literature uses mu = 0.3: Bonham and Hattersley 1967 (WRL Report 100, measured
# range 0.3-0.5), Gordon and Stone 1973 (73/12), Keller and Mitsch 1993 (UWRAA
# 69), and Shand, Cox, Blacka and Smith 2011 (P10/S2/020), which underpins AR&R
# and states verbatim: "While the assumed coefficient of friction of mu = 0.3 is
# likely conservative, the present lack of suitable data and wide range of road
# surfaces and tyre tread conditions prohibits the refinement of the
# coefficient." Azhar themselves note it "could drop to as low as 0.30 in case of
# poor road conditions."
#
# WHY IT BITES THIS RESULT SPECIFICALLY. Higher mu resists sliding, so a higher mu
# makes a NO-SLIDE (STUCK) verdict EASIER to reach. The headline of
# docs/THREE_CLASS_MATCHED_2026-08-14.md is a STUCK verdict. It was obtained at
# the HIGH end of the published field range, so the assumption points in the
# direction that favours the finding. That must be tested, not disclosed and
# left.
#
# THE TEST. Re-run the flip cell at the flood-safety convention and at the top of
# the measured range, with a Yaris control at the same mu so the direction of the
# response can be checked on a run that is nowhere near the boundary:
#     mu 0.30  Shand/AR&R safety convention, the de facto standard
#     mu 0.78  WRL TR 2017/07, top of the measured range
# Published field range is roughly 0.25 to 0.78 (Shah measured 0.52 sliding, YEAR
# UNRESOLVED and deliberately not silently re-dated: this project has carried 2018,
# 2019, 2020 and 2021 for a Shah paper. The moving-rigid-body catalog gives Shah,
# Mustaffa, Martinez-Gomariz and Yusof 2020, doi 10.1111/jfr3.12657, matching a
# Crossref date of 2020-07-28, confirmed three times independently. Whether that is
# the SAME paper as the 0.52 sliding measurement is NOT established here, so the
# figure is kept and the citation is marked UNRESOLVED rather than attached to it;
# Smith, Modra and Felder 2019 measured about 0.76).
#
# PREDICTION, written before the runs. If the STUCK verdict is an artifact of an
# optimistic mu, silverado at 0.30 returns SLIDE. If it survives to 0.30, the
# verdict is robust across the entire published range and that is a much stronger
# statement than the original.
#
# EVERYTHING ELSE IS HELD FIXED at the matched-dx conditions: n_grid 154/111,
# dx ~0.08486, realized depth ~0.29700, depth 0.30, velocity 1.5, 90 frames.
#
# ENGINE: warpmpm. NOT Genesis.
# ============================================================================
set -uo pipefail
REPO=/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine/src
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
TAG=${1:-2026-08-14}
BASE=/scratch/11603/jcerrell0629/three_class_mu_${TAG}
[ -e "$BASE" ] && { echo "REFUSING: $BASE exists (register item 16)."; exit 3; }
mkdir -p "$BASE"
PY="$VENV/bin/python"; export PYTHONPATH="$ENGINE:$REPO:${PYTHONPATH:-}"
DRIVER="$REPO/renders/yaris_render_s1/sim_standing.py"; PROV="$BASE/00_provenance.txt"
{ echo "start=$(date -Is) host=$(hostname)"
  echo "ARM MU, friction sensitivity of the flip cell. NON-CANONICAL."
  echo "driver sha256: $(sha256sum "$DRIVER")"; echo "runner sha256: $(sha256sum "$0")"
  nvidia-smi --query-gpu=index,name --format=csv,noheader; } >> "$PROV" 2>&1

run_one() {
    local label="$1" vehicle="$2" ngrid="$3" mass="$4" mu="$5" note="$6"
    local out="$BASE/$label"; mkdir -p "$out"
    echo "=== $(date -Is) $label mu=$mu"
    "$PY" "$DRIVER" --vehicle "$vehicle" --grid "$ngrid" --mass "$mass" \
        --label "$label" --out "$out" --depth 0.30 --velocity 1.5 --frames 90 \
        --eta 1.0e-3 --floor-friction "$mu" > "$BASE/${label}.log" 2>&1
    local rc=$?
    { echo "--- $label ---"; echo "MU=$mu VEHICLE=$vehicle N_GRID=$ngrid MASS=$mass NOTE=$note"
      echo "RC_${label}=$rc"
      /usr/bin/grep -h -E '^(FLOOR_FRICTION|INSTRUMENT dx|grid )' "$BASE/${label}.log" 2>/dev/null | sed 's/^/    /'; } >> "$PROV" 2>&1
    return $rc
}

run_one MU_silverado_n154_m2270_mu0p30 silverado 154 2270.0 0.30 "AR&R/Shand safety convention"
run_one MU_silverado_n154_m2270_mu0p78 silverado 154 2270.0 0.78 "WRL TR 2017/07, top of measured range"
run_one MU_yaris_n111_m1100_mu0p30     yaris     111 1100.0 0.30 "control, far from the boundary"
echo "ALLDONE end=$(date -Is)" >> "$PROV"
echo "=== finished $(date -Is), results in $BASE"
