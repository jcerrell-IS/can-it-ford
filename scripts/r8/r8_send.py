#!/usr/bin/env python3
"""r8_send.py - deliver ONE hand-written follow-up to ONE session.

Refuses to send when the message was not written for this session. The guards:

  * The target pane must exist and its cwd must equal the slot's planned
    worktree. A follow-up typed into the wrong pane is how Round 3 lost a round.
  * The session must be IDLE. Typing into a working session interrupts a tool
    call and produces exactly the blind, unclear reply this whole system exists
    to avoid. Override with --force only when you know it is parked.
  * The message must not be a repeat of anything sent to ANY slot. Byte-identical
    broadcast is the Round 3 failure.
  * The message must be at least --min-chars long and must name the slot's own
    branch, so a generic nudge cannot be sent by accident.

Every send is appended to r8_send_log.md with its full text, so the follow-up
chain is auditable after the fact.

Usage:
  r8_send.py --slot d2-persist --file /path/to/followup.md
  r8_send.py --slot d2-persist --file - < followup.md
  r8_send.py --slot d2-persist --file f.md --force      (send to a busy session)
  r8_send.py --slot d2-persist --file f.md --dry-run
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

REPO = "/Users/josie/can-it-ford"
PLAN = os.path.join(REPO, "scripts", "r8", "r8_plan.tsv")
STATE = os.path.join(REPO, ".claude", "state")
SENTDB = os.path.join(STATE, "r8_sent.json")
LOG = os.path.join(STATE, "r8_send_log.md")
TMUX_SESSION = "canford8"


def load_plan():
    rows = {}
    with open(PLAN) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            if not line.strip():
                continue
            d = dict(zip(head, line.rstrip("\n").split("\t")))
            rows[d["slot"]] = d
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True)
    ap.add_argument("--file", required=True, help="path to the follow-up text, or - for stdin")
    ap.add_argument("--min-chars", type=int, default=400)
    ap.add_argument("--force", action="store_true", help="send even if the session looks busy")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    plan = load_plan()
    if a.slot not in plan:
        sys.exit(f"REFUSED: unknown slot {a.slot}")
    row = plan[a.slot]

    text = sys.stdin.read() if a.file == "-" else open(a.file).read()
    text = text.strip()

    if len(text) < a.min_chars:
        sys.exit(f"REFUSED: follow-up is {len(text)} chars, minimum {a.min_chars}. "
                 "A short nudge produces a blind reply. Read the digest and write a real one.")

    if row["branch"] not in text:
        sys.exit(f"REFUSED: the follow-up never mentions this slot's branch "
                 f"({row['branch']}). That is the cheapest possible check that it was "
                 "written for THIS session and not copied from another.")

    h = hashlib.sha256(text.encode()).hexdigest()
    sent = {}
    if os.path.exists(SENTDB):
        try:
            sent = json.load(open(SENTDB))
        except Exception:
            sent = {}
    hashes = sent.setdefault("hashes", {})
    if h in hashes:
        sys.exit(f"REFUSED: this exact text was already sent to '{hashes[h]}'. "
                 "Every session gets its own message.")

    # Pane must exist and be in the right place.
    panes = subprocess.run(
        ["tmux", "list-panes", "-a", "-F", "#{session_name}:#{window_name}|#{pane_current_path}|#{pane_current_command}"],
        capture_output=True, text=True).stdout
    target = None
    for line in panes.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        name, path, cmd = parts[0], parts[1], parts[2]
        if name == f"{TMUX_SESSION}:{a.slot}":
            target = (name, path, cmd)
            break
    if target is None:
        sys.exit(f"REFUSED: no tmux pane named {TMUX_SESSION}:{a.slot}")
    name, path, cmd = target
    if path != row["worktree"]:
        sys.exit(f"REFUSED: pane {name} is in '{path}' but slot {a.slot} owns "
                 f"'{row['worktree']}'. Fix the pane, do not send.")

    # The pane must be running CLAUDE, not a bare shell. Measured 2026-08-19: nine
    # sessions failed to start because their --session-id was already used, leaving
    # a zsh prompt in each window. The sender's cwd check passed, so 4 KB of markdown
    # was pasted into a SHELL and executed line by line ("zsh: command not found:
    # --seed"). Prompt text contains backticks and redirects, so this is arbitrary
    # code execution, not just noise. Checking the pane's foreground command closes it.
    if not (("claude" in cmd) or cmd == "node" or re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", cmd)):
        sys.exit(f"REFUSED: pane {name} is running '{cmd}', which is not a Claude "
                 "session. Sending would paste the prompt into a shell and execute it. "
                 "Relaunch the slot first.")

    # Idle check via the watcher's own view.
    if not a.force:
        st = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "r8", "r8_watch.py"), "--status"],
                            capture_output=True, text=True).stdout
        for line in st.splitlines():
            if line.startswith(a.slot):
                if "idle=False" in line:
                    sys.exit(f"REFUSED: {a.slot} is mid-turn ({line.strip()}). "
                             "Interrupting produces the blind reply. Wait, or pass --force.")
                break

    if a.dry_run:
        print(f"DRY RUN, would send {len(text)} chars to {name} at {path}")
        print("---")
        print(text[:1200])
        return

    # Deliver as a BRACKETED PASTE via a tmux buffer, then one Enter.
    #
    # `send-keys -l` with embedded newlines does NOT work here: each newline is
    # delivered as a separate keypress, the client shows "paste again to expand"
    # and the turn never starts. Measured on d2-persist at 21:47. load-buffer
    # plus paste-buffer hands the whole block over as one paste, which is what
    # the input actually expects.
    tmpf = os.path.join("/tmp", f"r8_send_{a.slot}.txt")
    with open(tmpf, "w") as f:
        f.write(text)
    for _ in range(3):
        subprocess.run(["tmux", "send-keys", "-t", name, "C-u"], check=False)
        time.sleep(0.1)
    time.sleep(0.2)
    subprocess.run(["tmux", "load-buffer", "-b", "r8send", tmpf], check=True)
    subprocess.run(["tmux", "paste-buffer", "-d", "-b", "r8send", "-t", name], check=True)
    time.sleep(1.2)
    # NAMED "Enter", not "C-m". Measured 21:52: C-m leaves the text sitting in the
    # input and the turn never starts; Enter submits it. This cost four attempts.
    subprocess.run(["tmux", "send-keys", "-t", name, "Enter"], check=True)
    os.unlink(tmpf)

    hashes[h] = a.slot
    per = sent.setdefault("per_slot", {})
    per[a.slot] = per.get(a.slot, 0) + 1
    with open(SENTDB, "w") as f:
        json.dump(sent, f, indent=1)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"\n\n## {stamp}  ->  {a.slot}  (#{per[a.slot]}, sha {h[:12]})\n\n```\n{text}\n```\n")
    print(f"SENT {len(text)} chars to {name}  (follow-up #{per[a.slot]} for this slot)")


if __name__ == "__main__":
    main()
