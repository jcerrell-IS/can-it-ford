#!/bin/bash
# ============================================================================
# tacc_submit.sh  submit a batch job to Vista/LS6 from the Mac, then wait.
#
# WHY THIS EXISTS
#   Measured on Vista 2026-08-07 with `sacct -X -S 2026-07-01`:
#
#       interactive (idv/holder)   164 jobs   150.35 node-hours   99.1%
#       batch (science)             23 jobs     1.29 node-hours    0.9%
#
#   80 of the interactive jobs ended in TIMEOUT, meaning they ran to their
#   wall limit with nobody attached. 58 more were allocated and died at
#   00:00:00. The simulations that produced every gated result are the 1-4
#   minute batch jobs (yarisfinal 1:25, yarisford 1:26, f2_three_mass 2:48,
#   yarisv2 2:34, yarisconv 4:03). Interactive sessions cost roughly 117x
#   more node-time than all the science combined.
#
#   idev won that split because it was the only path that worked without
#   ssh gymnastics. This script removes that excuse: one command from the
#   Mac submits, waits, and prints the log, with no shell to leave open and
#   nothing to forget to exit.
#
#   Vista had 673 SUs left on 2026-08-07, expiring 2026-09-30. That is the
#   binding constraint on the rest of this project, so the default here is
#   batch, and an idle interactive session is treated as a bug.
#
# USAGE
#   scripts/tacc_submit.sh <host> <remote-sbatch-path> [--wait] [--tail N]
#   scripts/tacc_submit.sh vista '$WORK/render_s2/conv_2026-07-25.sbatch' --wait
#   scripts/tacc_submit.sh --dry vista '$WORK/render_s2/sweep_2026-07-26.sbatch'
#
#   The remote path is expanded on the remote side, so $WORK and $SCRATCH
#   work. Quote it so the local shell does not expand it first.
#
# EXIT: 0 job completed | 2 usage | 4 submit failed | 5 job failed/timeout
# ============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TACC="$HERE/tacc.sh"
POLL="${TACC_POLL:-20}"       # seconds between squeue checks
MAX_WAIT="${TACC_MAX_WAIT:-7200}"

die() { echo "tacc_submit.sh: $*" >&2; exit 2; }
[ -x "$TACC" ] || die "cannot find $TACC"

WAIT=0; DRY=0; TAIL=40; HOST=""; SCRIPT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --wait) WAIT=1; shift ;;
        --dry)  DRY=1;  shift ;;
        --tail) TAIL="${2:-40}"; shift 2 ;;
        -*)     die "unknown flag '$1'" ;;
        *)      if [ -z "$HOST" ]; then HOST="$1"; else SCRIPT="$1"; fi; shift ;;
    esac
done
[ -n "$HOST" ] && [ -n "$SCRIPT" ] || die "usage: tacc_submit.sh <host> <remote-sbatch-path> [--wait]"

# ---------------------------------------------------------------------------
# Guard 1: refuse to pile a batch job on top of a live interactive session.
# Two jobs on one small allocation is how 673 SUs becomes 0.
# ---------------------------------------------------------------------------
echo "== checking existing queue on ${HOST} =="
EXISTING="$("$TACC" "$HOST" 'squeue -u $USER -h -o "%.10i %.20j %.9T %.10M %.10l %R"' 2>/dev/null)"
if [ -n "$EXISTING" ]; then
    echo "$EXISTING" | sed 's/^/   /'
    if echo "$EXISTING" | grep -qE '(idv|holder)'; then
        echo
        echo "tacc_submit.sh: an INTERACTIVE job is already running on ${HOST}."
        echo "tacc_submit.sh: it is billing whether or not anything is attached."
        echo "tacc_submit.sh: cancel it first (scancel <jobid>) or run with the"
        echo "tacc_submit.sh: batch job knowingly stacked on top of it."
    fi
else
    echo "   queue empty"
fi

# ---------------------------------------------------------------------------
# Guard 2: the script has to exist. sbatch's own error for a missing file is
# easy to miss inside ssh output.
# ---------------------------------------------------------------------------
if ! "$TACC" "$HOST" "test -f ${SCRIPT}" >/dev/null 2>&1; then
    echo "tacc_submit.sh: '${SCRIPT}' not found on ${HOST}." >&2
    exit 4
fi

echo "== allocation before submit =="
"$TACC" "$HOST" '/usr/local/etc/taccinfo 2>/dev/null | grep -A1 "Avail SUs" | tail -1' 2>/dev/null | sed 's/^/   /'

if [ "$DRY" -eq 1 ]; then
    echo "== --dry: resource request that WOULD be submitted =="
    "$TACC" "$HOST" "grep '^#SBATCH' ${SCRIPT}" | sed 's/^/   /'
    exit 0
fi

# ---------------------------------------------------------------------------
# Submit. sbatch prints "Submitted batch job N"; take the last field.
# ---------------------------------------------------------------------------
echo "== submitting =="
OUT="$("$TACC" "$HOST" "sbatch ${SCRIPT}" 2>&1)"
echo "$OUT" | sed 's/^/   /'
JOBID="$(echo "$OUT" | awk '/Submitted batch job/{print $NF}')"
[ -n "$JOBID" ] || { echo "tacc_submit.sh: submit failed, no job id returned." >&2; exit 4; }
echo "   job id: ${JOBID}"

if [ "$WAIT" -eq 0 ]; then
    echo
    echo "Not waiting. Check with:  scripts/tacc.sh ${HOST} 'squeue -j ${JOBID}'"
    exit 0
fi

# ---------------------------------------------------------------------------
# Poll. squeue drops the job the moment it leaves the queue, so an empty
# result means finished, not lost; sacct is then the authority on how.
# ---------------------------------------------------------------------------
echo "== waiting (poll ${POLL}s, cap ${MAX_WAIT}s) =="
WAITED=0
while [ "$WAITED" -lt "$MAX_WAIT" ]; do
    ST="$("$TACC" "$HOST" "squeue -j ${JOBID} -h -o '%T %M'" 2>/dev/null)"
    [ -n "$ST" ] || break
    echo "   ${ST}  (+${WAITED}s)"
    sleep "$POLL"
    WAITED=$((WAITED + POLL))
done

FINAL="$("$TACC" "$HOST" "sacct -X -j ${JOBID} -o State%14,Elapsed,MaxRSS -n" 2>/dev/null | head -1)"
echo "== final =="
echo "   ${FINAL}"

# The sbatch files here write -o/-e to explicit absolute paths, so ask slurm
# where they went rather than guessing a naming convention.
LOGS="$("$TACC" "$HOST" "scontrol show job ${JOBID} 2>/dev/null | grep -E 'StdOut|StdErr'" 2>/dev/null)"
if [ -n "$LOGS" ]; then
    echo "$LOGS" | sed 's/^/   /'
    STDOUT="$(echo "$LOGS" | awk -F= '/StdOut/{print $2}' | tr -d ' ')"
    [ -n "$STDOUT" ] && {
        echo "== last ${TAIL} lines of stdout =="
        "$TACC" "$HOST" "tail -n ${TAIL} ${STDOUT}" 2>/dev/null | sed 's/^/   /'
    }
fi

echo "$FINAL" | grep -q COMPLETED && exit 0
exit 5
