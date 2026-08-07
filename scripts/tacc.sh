#!/bin/bash
# ============================================================================
# tacc.sh  single gated entry point for Vista / LS6 from Claude Code.
#
# WHY THIS EXISTS
#   Vista and LS6 are reachable non-interactively via the ControlMaster
#   sockets defined in ~/.ssh/config (ControlPersist 8h). Before this script,
#   every remote command needed its own literal entry in settings.local.json,
#   so in practice all TACC work got hand-relayed through tmux panes. This
#   gives Claude Code one allowlistable command instead of N literal rules.
#
# WHY THE TIMEOUT IS REMOTE
#   macOS has no coreutils `timeout`. TACC does (/usr/bin/timeout, 8.32).
#   Wrapping remotely also catches the known login-node hang where a
#   warpmpm import blocks ~600 s at near-zero CPU (returns 124, not a stall).
#
# USAGE
#   scripts/tacc.sh <host> <command...>
#   scripts/tacc.sh --status                 # both machines, jobs + quota
#   TACC_TIMEOUT=300 scripts/tacc.sh vista "python3 -c 'import warpmpm'"
#
# HOSTS: vista vista1 vista2 ls6 ls6a ls6b ls6c
# EXIT:  0 ok | 2 usage | 3 refused | 124 remote timeout | else remote rc
# ============================================================================
set -uo pipefail

TIMEOUT="${TACC_TIMEOUT:-60}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=15)

die() { echo "tacc.sh: $*" >&2; exit 2; }

run_remote() {
    local host="$1" cmd="$2"
    # printf %q yields a single bash-safe token for the remote shell.
    ssh "${SSH_OPTS[@]}" "$host" \
        "timeout ${TIMEOUT} bash -lc $(printf '%q' "$cmd")"
    local rc=$?
    if [ $rc -eq 124 ]; then
        echo "[tacc.sh] TIMEOUT: '${cmd}' exceeded ${TIMEOUT}s on ${host}." >&2
        echo "[tacc.sh] Near-zero CPU with a 124 means a blocking call, not contention." >&2
    elif [ $rc -eq 255 ]; then
        echo "[tacc.sh] SSH failed to ${host}. The ControlMaster socket may have expired." >&2
        echo "[tacc.sh] Re-authenticate once interactively:  ssh ${host}" >&2
    fi
    return $rc
}

status() {
    for h in vista ls6; do
        echo "==================== ${h} ===================="
        if ! ssh "${SSH_OPTS[@]}" -o ConnectTimeout=8 "$h" true 2>/dev/null; then
            echo "  UNREACHABLE non-interactively. Run 'ssh ${h}' once to open the socket."
            continue
        fi
        run_remote "$h" '
            echo "login node : $(hostname)"
            echo "WORK       : ${WORK:-unset}"
            echo "SCRATCH    : ${SCRATCH:-unset}"
            echo "--- queue ---"
            squeue -u "$USER" -o "%.10i %.9P %.24j %.8T %.10M %.10l %.6D %R" 2>&1 | head -20
            echo "--- allocation ---"
            (command -v sbatch >/dev/null && /usr/local/etc/taccinfo 2>/dev/null | head -12) || echo "taccinfo unavailable"
        '
    done
}

[ $# -ge 1 ] || die "no host given. Try: scripts/tacc.sh --status"

if [ "$1" = "--status" ]; then status; exit 0; fi

HOST="$1"; shift
CMD="$*"

case "$HOST" in
    vista|vista1|vista2|ls6|ls6a|ls6b|ls6c) ;;
    *) die "unknown host '$HOST'. Allowed: vista vista1 vista2 ls6 ls6a ls6b ls6c" ;;
esac

[ -n "$CMD" ] || die "no command given for host '$HOST'"

# Destructive remote verbs are refused here, not merely prompted. Confirming a
# recursive delete on a shared filesystem belongs in chat, not in a tool call.
case "$CMD" in
    *"rm -rf"*|*"rm -r "*|*"rm -fr"*|*mkfs*|*"chmod -R 777"*|*"> /dev/sd"*|*"dd if="*)
        echo "tacc.sh: REFUSED. '$CMD' contains a destructive verb." >&2
        echo "tacc.sh: Confirm in chat, then run it yourself over a normal ssh session." >&2
        exit 3 ;;
esac

run_remote "$HOST" "$CMD"
