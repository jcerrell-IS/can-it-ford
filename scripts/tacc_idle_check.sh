#!/bin/bash
# ============================================================================
# tacc_idle_check.sh  find interactive allocations that are burning SUs while
#                     doing nothing, on Vista and LS6.
#
# WHY THIS EXISTS
#   Measured on Vista 2026-08-07 (`sacct -X -S 2026-07-01`): 164 interactive
#   jobs consumed 150.35 node-hours, 99.1% of all node-time since July 1,
#   against 1.29 node-hours for the 23 batch jobs that produced every gated
#   result. 80 of the 164 ended in TIMEOUT, that is, they ran to the wall
#   limit unattended. Nothing in the workflow noticed, because an idle idev
#   session looks exactly like a busy one from the login node.
#
#   This is the detector. It reports; it does not cancel. Cancelling someone
#   else's live session from a script is how you lose an hour of real work,
#   so the scancel line is printed for a human to run.
#
# WHAT "IDLE" MEANS HERE
#   All visible GPUs at 0% utilisation AND 0 MiB used AND 1-minute load
#   below 0.5. Any one of those alone is a bad signal: a job can legitimately
#   sit at 0% GPU between steps, and load alone misses GPU-bound work.
#
# USAGE
#   scripts/tacc_idle_check.sh            # both hosts
#   scripts/tacc_idle_check.sh vista      # one host
#
# EXIT: 0 nothing idle | 1 at least one idle allocation found | 2 usage
# ============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TACC="$HERE/tacc.sh"
[ -x "$TACC" ] || { echo "tacc_idle_check.sh: cannot find $TACC" >&2; exit 2; }

HOSTS=("vista" "ls6")
if [ $# -ge 1 ]; then
    case "$1" in
        vista|ls6) HOSTS=("$1") ;;
        *) echo "tacc_idle_check.sh: unknown host '$1' (vista|ls6)" >&2; exit 2 ;;
    esac
fi

FOUND_IDLE=0

for h in "${HOSTS[@]}"; do
    echo "==================== ${h} ===================="

    SUS="$("$TACC" "$h" '/usr/local/etc/taccinfo 2>/dev/null | awk "/BCS20003/{print \$3}"' 2>/dev/null | tr -d ' ')"
    [ -n "$SUS" ] && echo "SUs remaining: ${SUS}"

    # %.10i jobid  %.20j name  %.10M elapsed  %.10l limit  %R nodelist
    JOBS="$("$TACC" "$h" 'squeue -u $USER -h -o "%i|%j|%M|%l|%R"' 2>/dev/null)"
    if [ -z "$JOBS" ]; then
        echo "queue empty, nothing burning."
        continue
    fi

    while IFS='|' read -r jid jname elapsed limit node; do
        [ -n "$jid" ] || continue
        jid="$(echo "$jid" | tr -d ' ')"; jname="$(echo "$jname" | tr -d ' ')"
        node="$(echo "$node" | tr -d ' ')"
        echo
        echo "job ${jid}  ${jname}  elapsed ${elapsed} / limit ${limit}  on ${node}"

        # Only interactive allocations are suspects. A batch job that is quiet
        # is usually just between stages, and it will exit on its own.
        case "$jname" in
            idv*|holder*) ;;
            *) echo "   batch job, not an idle-session candidate. Skipping probe."; continue ;;
        esac

        # Reachability of the compute node is not guaranteed; degrade loudly.
        PROBE="$("$TACC" "$h" "ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=8 ${node} 'nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null; echo LOADSEP; cat /proc/loadavg; echo PROCSEP; ps -eo comm= --sort=-pcpu | head -5'" 2>/dev/null)"

        if [ -z "$PROBE" ]; then
            echo "   could not reach ${node} from the ${h} login node. State UNKNOWN."
            echo "   Do not assume idle from this: an unreachable node is not evidence."
            continue
        fi

        GPUS="$(echo "$PROBE"  | sed -n '1,/LOADSEP/p' | grep -v LOADSEP)"
        LOAD1="$(echo "$PROBE" | sed -n '/LOADSEP/,/PROCSEP/p' | grep -v -E 'LOADSEP|PROCSEP' | awk '{print $1}')"
        TOPP="$(echo "$PROBE"  | sed -n '/PROCSEP/,$p' | grep -v PROCSEP | tr '\n' ' ')"

        echo "   GPUs (idx, util, mem):"
        echo "$GPUS" | sed 's/^/      /'
        echo "   load1: ${LOAD1:-unknown}   top procs: ${TOPP}"

        BUSY_GPU=$(echo "$GPUS" | awk -F, '{gsub(/[^0-9]/,"",$2); gsub(/[^0-9]/,"",$3); if ($2+0>0 || $3+0>0) c++} END{print c+0}')
        LOAD_OK=$(awk -v l="${LOAD1:-9}" 'BEGIN{print (l<0.5)?1:0}')

        if [ "$BUSY_GPU" -eq 0 ] && [ "$LOAD_OK" -eq 1 ]; then
            FOUND_IDLE=1
            echo "   VERDICT: IDLE. Every GPU at 0% and 0 MiB, load ${LOAD1}."
            echo "   This allocation is billing and producing nothing."
            echo "   To reclaim it:   scripts/tacc.sh ${h} 'scancel ${jid}'"
        else
            echo "   VERDICT: active (busy GPUs: ${BUSY_GPU}, load ${LOAD1}). Leave it alone."
        fi
    done <<< "$JOBS"
done

echo
if [ "$FOUND_IDLE" -eq 1 ]; then
    echo "At least one idle allocation found. Cancelling is a human decision, so"
    echo "no scancel was run. Batch submission avoids the whole class of problem:"
    echo "  scripts/tacc_submit.sh vista '\$WORK/render_s2/conv_2026-07-25.sbatch' --wait"
    exit 1
fi
echo "No idle interactive allocations detected."
exit 0
