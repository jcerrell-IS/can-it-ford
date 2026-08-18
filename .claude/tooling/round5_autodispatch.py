#!/usr/bin/env python3
"""round5_autodispatch.py — a monitor that keeps four sessions rolling by itself.

WHY. Round 3's coordinator broadcast BYTE-IDENTICAL prompts to 13 sessions six
times, so 13 agents duplicated one job. Josie diagnosed it before the
coordinator did. Round 3 also lost most of its session-time to sessions sitting
idle at an empty prompt waiting for a human to notice.

This tool fixes both, mechanically rather than by instruction:

  * IT REFUSES TO REPEAT ITSELF. Every outgoing message is sha256'd. A hash
    already sent to ANY session is never sent again, to anyone.
  * EVERY FOLLOW-UP IS BUILT FROM THAT SESSION'S OWN FACTS: its branch, its
    last commit subject, its uncommitted files, its unpushed count, and what
    its SIBLINGS just did (so it is told what NOT to duplicate).
  * IT ONLY SPEAKS TO IDLE SESSIONS. A working session is left alone.

Usage:
  python3 round5_autodispatch.py --watch          poll forever (default 90s)
  python3 round5_autodispatch.py --once           one pass, then exit
  python3 round5_autodispatch.py --dry-run        print what it WOULD send
  python3 round5_autodispatch.py --status         table only, send nothing

Zero dependencies. Python 3.9 safe.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import time

SESSION = "canford5"
REPO = "/Users/josie/can-it-ford"
STATE = os.path.join(REPO, ".claude", "state")
SENT_DB = os.path.join(STATE, "round5_sent.json")
BOARD = os.path.join(STATE, "round5_board.md")
LOG = os.path.join(STATE, "round5_autodispatch.log")

IDLE_SECONDS = 240        # a session must be still this long before we speak
# ACTIVE-work detector. REWRITTEN 2026-08-16 20:55 after this exact regex cost
# five hours of fleet time, verified by measurement not by reading.
#
# The old form was  r"[A-Z][a-z]+ing…|✻|✶|✢|·\s*\w+ing"  and its fatal member is
# the BARE GLYPH. Claude Code uses ✻/✶/✢ for BOTH states:
#     ACTIVE    "✢ Determining… (7m 16s · ↓ 30.9k tokens)"
#     FINISHED  "✻ Cogitated for 23m 15s"
# so a bare ✻ matches a session that has STOPPED. Widening busy()'s window from
# 8 to 20 lines on 2026-08-16 (a correct fix for a different bug) pulled the
# finished-thought line into view, and from 15:50 to 20:52 all four sessions
# reported "working" while sitting idle at a prompt, three of them with
# un-submitted instructions queued. Zero follow-ups fired. Zero commits landed.
#
# The discriminator is the ELLIPSIS PLUS LIVE COUNTER, which only the active
# form has: "<word>… (" . A finished line reads "<word> for 23m 15s", no "…".
# "esc to interrupt" is kept as an independent second signal.
ACTIVE = re.compile(r"[A-Za-z]+…\s*\(")
SPINNER = ACTIVE  # back-compat for any other reference

DISPATCHES = {
    1: dict(label="MINE-RESEARCH",  wt=".claude/worktrees/r5-research",
            branch="claude/r5-research",
            mission="mine the ~400 research files nobody read, especially the "
                    "Elicit .bib and the 1,345-row extract CSV",
            owns="docs/R5_RESEARCH_*, data/r5_citation_*"),
    2: dict(label="E8-CREDENTIALS", wt=".claude/worktrees/r5-exposure",
            branch="claude/r5-exposure",
            mission="the already-public hull licence decision and the "
                    "credential rotation execution list",
            owns="docs/E8_*, docs/CREDENTIAL_*"),
    3: dict(label="SAFE-THE-WORK",  wt=".claude/worktrees/r5-safekeeping",
            branch="claude/r5-safekeeping",
            mission="bundle 188 unpushed commits, write the push ledger, "
                    "sequence the register collision",
            owns="docs/PUSH_LEDGER_*, bundles/"),
    4: dict(label="PHYSICS-GATE",   wt=".claude/worktrees/r5-physics",
            branch="claude/r5-physics",
            mission="grid-node outflow BC, or first external validation "
                    "against Kramer 2021",
            owns="simulation/r5_physics/, docs/R5_PHYSICS_*"),
}


def sh(cmd, timeout=45):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def log(msg):
    os.makedirs(STATE, exist_ok=True)
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")
    print(line)


def load_sent():
    if os.path.exists(SENT_DB):
        try:
            return json.load(open(SENT_DB))
        except ValueError:
            pass
    return {"hashes": [], "per_session": {}}


def save_sent(db):
    os.makedirs(STATE, exist_ok=True)
    json.dump(db, open(SENT_DB, "w"), indent=1)


def pane_for(d):
    """Resolve dispatch d to its pane IN SESSION `SESSION` ONLY.

    FIXED 2026-08-16, coordinator, verified empirically before any message was
    sent. This used `tmux list-panes -a`, which enumerates EVERY session on the
    machine and returned the first pane whose window_index matched. The Round-3
    session `canford` (14 windows) still exists and sorts first, so `pane_for(1)`
    resolved to `canford:1` = "D1 PUSH-ORPHANED-g128", a live Round-4 session on
    unrelated work. `--watch` would have read git state from the R5 worktrees,
    composed R5 follow-ups, and typed them into Round-4 sessions. That is
    ERRORS_AND_RESOLUTIONS A1 (wrong-target broadcast) reappearing inside the
    tool written to prevent it. `-s -t SESSION` scopes to one session; the
    session_name check below makes a silent cross-session hit impossible even if
    someone reintroduces `-a`.
    """
    out = sh(["tmux", "list-panes", "-s", "-t", SESSION,
              "-F", "#{window_index}|#{pane_id}|#{session_name}"])
    for ln in out.splitlines():
        parts = ln.split("|")
        if len(parts) < 3:
            continue
        idx, pid, sess = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if idx == str(d) and sess == SESSION:
            return pid
    return None


def capture(d, n=60):
    p = pane_for(d)
    if not p:
        return ""
    return sh(["tmux", "capture-pane", "-p", "-t", p, "-S", "-%d" % n])


def idle_age(d):
    """Seconds since this pane's visible content last changed."""
    os.makedirs(STATE, exist_ok=True)
    vis = capture(d, 40)
    h = hashlib.sha1(vis.encode()).hexdigest()
    f = os.path.join(STATE, "round5_hash_%d.txt" % d)
    now = time.time()
    prev, ts = None, now
    if os.path.exists(f):
        try:
            prev, ts = open(f).read().split("\n")[:2]
            ts = float(ts)
        except Exception:
            prev, ts = None, now
    if h != prev:
        open(f, "w").write("%s\n%f" % (h, now))
        return 0, vis
    return int(now - ts), vis


def busy(vis):
    # WINDOW WIDENED 8 -> 20, 2026-08-16, measured not guessed. Claude Code
    # draws the spinner ABOVE the tip box, the prompt box and the two status
    # lines, so on a working session the spinner sits about 10 lines from the
    # bottom and an 8-line window never sees it. Measured live on D4 at 15:49:
    # spinner at line 10 from the bottom, invisible to tail(-8), caught by
    # tail(-20). Consequence of the old value: a session mid-work was
    # classified idle, and a follow-up would be typed into it while it was
    # thinking. That is the interruption family of ERRORS A1/A3.
    tail = "\n".join(vis.strip().splitlines()[-20:])
    if SPINNER.search(tail):
        return True
    if "esc to interrupt" in tail.lower():
        return True
    return False


def awaiting_input(vis):
    tail = "\n".join(vis.strip().splitlines()[-14:])
    return ("Do you want to proceed?" in tail) or ("❯ 1. Yes" in tail)


def gitfacts(d):
    blank = dict(exists=False, branch="", last="", dirty=[], unpushed="0")
    wt = os.path.join(REPO, DISPATCHES[d]["wt"])
    if not os.path.isdir(wt):
        return blank
    br = sh(["git", "-C", wt, "rev-parse", "--abbrev-ref", "HEAD"])
    last = sh(["git", "-C", wt, "log", "-1", "--format=%h %s"])
    dirty = sh(["git", "-C", wt, "status", "--porcelain=v1"])
    unpushed = sh(["git", "-C", wt, "rev-list", "--count", br,
                   "--not", "--remotes=origin"]) or "0"
    return dict(exists=True, branch=br, last=last,
                dirty=[x[3:].strip() for x in dirty.splitlines() if x],
                unpushed=unpushed)


def siblings_line(d):
    """What the OTHER sessions just did, so this one is told what to avoid."""
    bits = []
    for k, v in sorted(DISPATCHES.items()):
        if k == d:
            continue
        g = gitfacts(k)
        if g.get("exists") and g.get("last"):
            bits.append("D%d(%s) last: %s" % (k, v["label"], g["last"][:64]))
    return " | ".join(bits) if bits else "no sibling commits yet"


def compose(d, g, age):
    """Build a follow-up from THIS session's own state. Never generic."""
    m = DISPATCHES[d]
    parts = []
    parts.append("AUTO-FOLLOW-UP for D%d %s. You have been idle %dm."
                 % (d, m["label"], age // 60))
    parts.append("Your branch %s is at: %s."
                 % (g.get("branch", "?"), g.get("last") or "NO COMMITS YET"))
    if g.get("dirty"):
        parts.append("YOU HAVE %d UNCOMMITTED FILE(S): %s. Commit them "
                     "path-limited BEFORE anything else, because uncommitted "
                     "work does not survive a compaction with its reasoning: "
                     "git commit -m \"msg\" -- <paths>."
                     % (len(g["dirty"]), ", ".join(g["dirty"][:4])))
    else:
        parts.append("Worktree clean, %s commit(s) unpushed and HELD (never "
                     "push without Josie's per-branch go-ahead)." % g.get("unpushed"))
    parts.append("YOUR MISSION, unchanged: %s. You own %s and write nowhere "
                 "else." % (m["mission"], m["owns"]))
    parts.append("SIBLINGS, so you do not duplicate them: %s. Read %s before "
                 "starting a new unit and append your own row when you finish "
                 "one." % (siblings_line(d), BOARD))
    parts.append("Pick the single highest-value open item in YOUR scope and "
                 "finish it. If blocked, try a genuinely different second "
                 "approach, then use a connector (canford-corpus for any "
                 "research file, scite or scholar-sidekick for any DOI, "
                 "wolfram for any unit or parameter, canford-tacc for any "
                 "cluster call), and only then write a named flag file and "
                 "keep working on the rest of your scope.")
    parts.append("Before finalising any percentage, force, verdict count or "
                 "distance, run the physics-skeptic subagent; if unavailable "
                 "say so and mark the claim UNREVIEWED rather than faking it. "
                 "Report N and spread, never a single draw, and state the "
                 "settle length any simulation number was measured at.")
    return " ".join(parts)


def send(d, text, dry=False):
    p = pane_for(d)
    if not p:
        log("D%d: no pane" % d)
        return False
    if dry:
        print("\n--- WOULD SEND to D%d ---\n%s\n" % (d, text))
        return True
    subprocess.run(["tmux", "load-buffer", "-b", "r5auto", "-"],
                   input=text, text=True)
    subprocess.run(["tmux", "paste-buffer", "-b", "r5auto", "-t", p, "-d"])
    time.sleep(0.4)
    subprocess.run(["tmux", "send-keys", "-t", p, "Enter"])
    return True


def one_pass(args):
    db = load_sent()
    seen = set(db["hashes"])
    rows = []
    for d in sorted(DISPATCHES):
        age, vis = idle_age(d)
        g = gitfacts(d)
        state = ("MISSING" if not g.get("exists") else
                 "AWAITING-INPUT" if awaiting_input(vis) else
                 "working" if busy(vis) else
                 "idle %dm" % (age // 60))
        rows.append((d, DISPATCHES[d]["label"], state,
                     g.get("unpushed", "-"), len(g.get("dirty", []))))
        if args.status:
            continue
        if not g.get("exists") or busy(vis) or awaiting_input(vis):
            continue
        if age < IDLE_SECONDS:
            continue
        text = compose(d, g, age)
        h = hashlib.sha256(re.sub(r"\s+", " ", text).encode()).hexdigest()
        if h in seen:
            log("D%d: composed message is a DUPLICATE, refusing to send" % d)
            continue
        if send(d, text, args.dry_run):
            # A dry run used to log the words "follow-up sent", identical to a
            # real send, and only the absence of round5_sent.json distinguished
            # them. On 2026-08-16 that cost a coordinator a full forensic pass
            # to establish whether four messages had reached the wrong sessions.
            # The log must say what actually happened.
            log("D%d: %s (%dm idle, hash %s)"
                % (d,
                   "DRY-RUN, nothing sent" if args.dry_run else "follow-up sent",
                   age // 60, h[:10]))
            if not args.dry_run:
                seen.add(h)
                db["hashes"] = sorted(seen)
                db["per_session"].setdefault(str(d), []).append(
                    {"ts": time.strftime("%H:%M:%S"), "hash": h[:10]})
                save_sent(db)

    print("\n  D  %-16s %-16s %-9s %s" % ("LABEL", "STATE", "UNPUSHED", "DIRTY"))
    for d, lab, st, up, dr in rows:
        mark = "!!" if st == "AWAITING-INPUT" else "  "
        print("%s D%-2d %-16s %-16s %-9s %s" % (mark, d, lab, st, up, dr))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=int, default=90)
    a = ap.parse_args()
    if a.watch:
        while True:
            one_pass(a)
            time.sleep(a.interval)
    else:
        one_pass(a)


if __name__ == "__main__":
    main()
