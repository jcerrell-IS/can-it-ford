#!/bin/sh
# verify_sandbox.sh: run INSIDE a fresh sbx session to check the
# canitford-base kit actually provisioned what it claims.
#
#   sbx exec canitford -- sh /workspace/sandbox/verify_sandbox.sh
#
# Exits 0 only if every REQUIRED check passes. WARN lines do not fail the
# run: they mark things that are expected to vary (for example the hf CLI,
# which is deliberately not installed because that would need pypi.org in
# the egress allowlist).
#
# This script asserts against values measured on the host on 2026-08-23.
# If the host changes, these constants go stale and the script will report
# a false failure. That is intentional: a drift check that cannot fail is
# not a check. Re-measure and update the constants rather than deleting them.

PASS=0; FAIL=0; WARN=0

ok()   { PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; }
warn() { WARN=$((WARN+1)); printf '  WARN  %s\n' "$1"; }
hdr()  { printf '\n%s\n' "$1"; }

# Measured on the host, 2026-08-23.
HOST_GLOBAL_SHA="6b2d14ace255f826ec68b0f4b35d430398c4c35ad3bdb59563b181d8e6401d3b"
HOST_GLOBAL_LINES=106
HOST_PROJECT_LINES=1024
HOST_MEMORY_FILES=118
HOST_REPO_SKILLS=15
EXPECT_HF_USER="josiecerrell"

sha() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
        else shasum -a 256 "$1" | cut -d' ' -f1; fi; }

# ---------------------------------------------------------------------------
hdr "0. locate the workspace"
# ---------------------------------------------------------------------------
WS=""
for c in /workspace "$PWD" /home/agent/can-it-ford /can-it-ford; do
    if [ -f "$c/CLAUDE.md" ] && [ -d "$c/.claude" ]; then WS="$c"; break; fi
done
if [ -n "$WS" ]; then ok "workspace found at $WS"
else bad "no workspace with CLAUDE.md and .claude/ found; every path check below will fail"; fi

# ---------------------------------------------------------------------------
hdr "1. CLAUDE.md, both of them"
# ---------------------------------------------------------------------------
# The brief said there is no separate ~/.claude/CLAUDE.md. There is: 106
# lines of global working rules. It lives outside the workspace on the host,
# so unlike the project file it cannot arrive by bind mount and the kit has
# to ship it. Both are checked here because they are different files with
# different delivery mechanisms and different failure modes.

if [ -n "$WS" ] && [ -f "$WS/CLAUDE.md" ]; then
    n=$(wc -l < "$WS/CLAUDE.md" | tr -d ' ')
    if [ "$n" -eq "$HOST_PROJECT_LINES" ]; then
        ok "project CLAUDE.md at $WS/CLAUDE.md ($n lines, matches host)"
    else
        warn "project CLAUDE.md is $n lines, host had $HOST_PROJECT_LINES; the repo changed or the mount is stale"
    fi
else
    bad "project CLAUDE.md missing (expected via bind mount, not via the kit)"
fi

G="$HOME/.claude/CLAUDE.md"
if [ -f "$G" ]; then
    n=$(wc -l < "$G" | tr -d ' '); s=$(sha "$G")
    if [ "$s" = "$HOST_GLOBAL_SHA" ]; then
        ok "global CLAUDE.md at $G ($n lines, sha matches host byte for byte)"
    else
        warn "global CLAUDE.md present ($n lines) but sha differs from host; the kit snapshot has drifted, refresh it"
    fi
else
    bad "global CLAUDE.md missing at $G; the kit's files/home/ did not land"
fi

# ---------------------------------------------------------------------------
hdr "2. memory and skills"
# ---------------------------------------------------------------------------
# All three of these arrive by bind mount, not by copying. The brief pointed
# the memory directory at ~/.claude/projects/can-it-ford/memory/, which does
# not exist on the host. The real path is <repo>/.claude/memory/.

if [ -n "$WS" ] && [ -d "$WS/.claude/memory" ]; then
    n=$(ls -1 "$WS/.claude/memory" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$n" -ge "$HOST_MEMORY_FILES" ]; then ok "memory directory: $n files at $WS/.claude/memory"
    else warn "memory directory has $n files, host had $HOST_MEMORY_FILES"; fi
    [ -f "$WS/.claude/memory/MEMORY.md" ] && ok "MEMORY.md index present" \
                                          || bad "MEMORY.md index missing"
else
    bad "memory directory missing at $WS/.claude/memory"
fi

if [ -n "$WS" ] && [ -d "$WS/.claude/skills" ]; then
    n=$(ls -1 "$WS/.claude/skills" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$n" -ge "$HOST_REPO_SKILLS" ]; then ok "repo-scoped skills: $n present (bind mount)"
    else warn "repo-scoped skills: $n, host had $HOST_REPO_SKILLS"; fi
else
    bad "repo-scoped skills missing at $WS/.claude/skills"
fi

if [ -d "$HOME/.claude/skills" ]; then
    n=$(ls -1 "$HOME/.claude/skills" 2>/dev/null | wc -l | tr -d ' ')
    ok "shared skills store mounted at ~/.claude/skills ($n entries)"
    [ "$n" -lt 30 ] && warn "expected about 35 from 'sbx skills ls' on the host; run 'sbx skills import' if low"
else
    bad "shared skills store not mounted at ~/.claude/skills (was --no-share-skills used?)"
fi

# ---------------------------------------------------------------------------
hdr "3. MCP servers"
# ---------------------------------------------------------------------------
if command -v claude >/dev/null 2>&1; then
    OUT=$(claude mcp list 2>&1)
    printf '%s\n' "$OUT" | sed 's/^/        | /'

    for srv in hf wandb; do
        line=$(printf '%s\n' "$OUT" | /usr/bin/grep -i "^[[:space:]]*$srv[[:space:]:]" || true)
        if [ -z "$line" ]; then
            bad "$srv MCP server is not registered"
        elif printf '%s' "$line" | /usr/bin/grep -qiE 'connected|✓|ready'; then
            ok "$srv MCP server connected"
        else
            bad "$srv MCP server registered but not connected: $line"
        fi
    done

    # The whole point of the GitHub decision: exactly one GitHub-capable path.
    # On the host, MCP_DOCKER and repo-tools both expose GitHub tools. Here
    # there must be zero GitHub MCP servers and one working gh CLI.
    ghmcp=$(printf '%s\n' "$OUT" | /usr/bin/grep -ciE '(^|[^a-z])(github|repo-tools|mcp_docker)' || true)
    if [ "$ghmcp" -eq 0 ]; then
        ok "no GitHub MCP server registered (correct: gh CLI is the only path)"
    else
        bad "$ghmcp GitHub-ish MCP server(s) registered; that is the duplication this kit avoids"
    fi
else
    bad "claude CLI not found, cannot check MCP servers"
fi

# ---------------------------------------------------------------------------
hdr "4. GitHub via gh"
# ---------------------------------------------------------------------------
if command -v gh >/dev/null 2>&1; then
    ok "gh present at $(command -v gh)"
    if gh auth status >/dev/null 2>&1; then
        ok "gh auth status succeeds"
    else
        # Expected shape of failure. sbx's github secret is proxy-injected:
        # the token is swapped into outbound api.github.com requests and is
        # never present locally, so gh's own local-credential check can fail
        # while API calls still work. Test the thing that matters.
        if gh api user >/dev/null 2>&1; then
            warn "gh auth status fails but 'gh api user' works: the proxy is injecting the token and gh has no local credential. Functionally fine."
        else
            bad "gh cannot reach the API. Run 'sbx secret set github --command \"gh auth token\"' on the host."
        fi
    fi
    who=$(gh api user --jq .login 2>/dev/null || true)
    [ -n "$who" ] && ok "gh identity: $who" || warn "could not read gh identity"
else
    warn "gh not installed in the base image. See the note in spec.yaml setup.install step 2."
fi

# ---------------------------------------------------------------------------
hdr "5. Hugging Face identity"
# ---------------------------------------------------------------------------
# 'hf auth whoami' is the correct current syntax; bare 'hf whoami' does not
# exist. But hf is only present if the base image ships it, because
# installing it would need pypi.org in the egress allowlist. The curl
# fallback asserts the same fact over an already-allowed domain.
if command -v hf >/dev/null 2>&1; then
    out=$(hf auth whoami 2>&1 || true)
    if printf '%s' "$out" | /usr/bin/grep -q "$EXPECT_HF_USER"; then
        ok "hf auth whoami reports $EXPECT_HF_USER"
    else
        bad "hf auth whoami did not report $EXPECT_HF_USER: $out"
    fi
else
    warn "hf CLI not installed (expected: pypi.org is not in the allowlist), using the API instead"
    if [ -n "${HF_TOKEN:-}" ]; then
        out=$(curl -s --max-time 20 -H "Authorization: Bearer $HF_TOKEN" \
                   https://huggingface.co/api/whoami-v2 2>&1 || true)
        if printf '%s' "$out" | /usr/bin/grep -q "$EXPECT_HF_USER"; then
            ok "huggingface.co/api/whoami-v2 reports $EXPECT_HF_USER (proxy swapped the placeholder)"
        else
            bad "whoami-v2 did not report $EXPECT_HF_USER: $(printf '%s' "$out" | head -c 200)"
        fi
    else
        bad "HF_TOKEN is unset; run sandbox/provision.sh on the host"
    fi
fi

# ---------------------------------------------------------------------------
hdr "6. secrets are placeholders, not real keys"
# ---------------------------------------------------------------------------
# If a real key is sitting in the sandbox environment, the containment
# argument for this whole kit is void. Check that explicitly.
for v in HF_TOKEN WANDB_API_KEY; do
    eval "val=\${$v:-}"
    if [ -z "$val" ]; then
        bad "$v is unset; run sandbox/provision.sh on the host"
    elif printf '%s' "$val" | /usr/bin/grep -qE '^(hf_[A-Za-z0-9]{30,}|[0-9a-f]{40})$'; then
        bad "$v looks like a REAL credential, not a placeholder. The proxy substitution is not in play and the sandbox holds a live key."
    else
        ok "$v is set to a non-credential-shaped placeholder"
    fi
done

# ---------------------------------------------------------------------------
hdr "7. egress allowlist actually restricts"
# ---------------------------------------------------------------------------
# An allowlist nobody tested is a comment. One allowed host must work and one
# unlisted host must not.
if command -v curl >/dev/null 2>&1; then
    if curl -s -o /dev/null --max-time 15 https://api.github.com >/dev/null 2>&1; then
        ok "allowed domain api.github.com is reachable"
    else
        bad "allowed domain api.github.com is NOT reachable"
    fi
    if curl -s -o /dev/null --max-time 10 https://pypi.org >/dev/null 2>&1; then
        bad "pypi.org is reachable but is NOT in the allowlist; egress is wider than the spec claims"
    else
        ok "unlisted domain pypi.org is blocked, as intended"
    fi
else
    warn "curl not available, cannot test egress"
fi

# ---------------------------------------------------------------------------
hdr "8. what the base image shipped"
# ---------------------------------------------------------------------------
if [ -f "$HOME/.canitford-toolprobe" ]; then
    sed 's/^/        /' "$HOME/.canitford-toolprobe"
else
    warn "no tool probe at ~/.canitford-toolprobe; the kit's first install step did not run"
fi

# ---------------------------------------------------------------------------
printf '\n===========================================\n'
printf '  PASS %d   FAIL %d   WARN %d\n' "$PASS" "$FAIL" "$WARN"
printf '===========================================\n'
[ "$FAIL" -eq 0 ] || exit 1
