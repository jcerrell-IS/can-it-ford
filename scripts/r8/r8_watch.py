#!/usr/bin/env python3
"""r8_watch.py - detect idle R8 sessions and write a digest. IT NEVER SENDS.

This is deliberately NOT an autodispatcher. The Round 5 autodispatcher ran for
two days firing every 90 seconds at a pane that no longer existed, and every
message it composed was refused by its own dedupe guard. Before that, Round 3's
coordinator broadcast byte-identical prompts to 13 sessions six times.

The failure in both cases was the same: a machine wrote the follow-up. A
follow-up that is worth interrupting a session for has to be written by
something that actually read what the session said.

So this tool does exactly one job. When a session goes idle it assembles
everything needed to write a good follow-up (the session's own last words, the
commands it ran, its live git state, and what its siblings did meanwhile) into
one digest file, and prints ONE line naming that file. A human or an agent reads
the digest and writes the follow-up by hand. Nothing is ever typed into a pane
by this script.

Usage:
  r8_watch.py --watch [--idle-s 120] [--interval 30]
  r8_watch.py --once
  r8_watch.py --status
"""
import argparse
import json
import os
import subprocess
import time

REPO = "/Users/josie/can-it-ford"
PLAN = os.path.join(REPO, "scripts", "r8", "r8_plan.tsv")
STATE = os.path.join(REPO, ".claude", "state")
IDS = os.path.join(STATE, "r8_session_ids.tsv")
DIGESTS = os.path.join(STATE, "r8_digests")
BOARD = os.path.join(STATE, "r8_board.md")
SEEN = os.path.join(STATE, "r8_watch_seen.json")
PROJECTS = os.path.expanduser("~/.claude/projects")


def sh(args, cwd=None):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception as e:
        return f"(command failed: {e})"


def load_plan():
    rows = []
    with open(PLAN) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            if not line.strip():
                continue
            rows.append(dict(zip(head, line.rstrip("\n").split("\t"))))
    return rows


def load_ids():
    d = {}
    if os.path.exists(IDS):
        for line in open(IDS):
            p = line.rstrip("\n").split("\t")
            if len(p) == 2:
                d[p[0]] = p[1]
    return d


def transcript_path(worktree, sid):
    """Claude Code encodes the cwd by replacing / and . with -."""
    enc = worktree.replace("/", "-").replace(".", "-")
    return os.path.join(PROJECTS, enc, sid + ".jsonl")


def read_tail(path, max_events=4000):
    events = []
    try:
        with open(path, errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        return None
    return events[-max_events:]


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c
                         if isinstance(x, dict) and x.get("type") == "text")
    return ""


def has_pending_tool(msg):
    c = msg.get("content")
    if isinstance(c, list):
        return any(isinstance(x, dict) and x.get("type") == "tool_use" for x in c)
    return False


def session_view(row, sid):
    """Everything a follow-up author needs, in one place."""
    tree = row["worktree"]
    tp = transcript_path(tree, sid)
    ev = read_tail(tp)
    v = {
        "slot": row["slot"], "branch": row["branch"], "worktree": tree,
        "session_id": sid, "transcript": tp,
        "exists": ev is not None,
        "idle": False, "last_ts": None, "last_assistant": "", "bash": [],
        "n_events": 0,
    }
    if ev is None:
        return v
    v["n_events"] = len(ev)
    last_assist = ""
    last_ts = None
    bash = []
    pending = False
    for o in ev:
        ts = o.get("timestamp")
        if ts:
            last_ts = ts
        if o.get("type") == "assistant":
            m = o.get("message", {})
            t = text_of(m).strip()
            if t:
                last_assist = t
                pending = False
            if has_pending_tool(m):
                pending = True
            c = m.get("content")
            if isinstance(c, list):
                for x in c:
                    if isinstance(x, dict) and x.get("type") == "tool_use" and x.get("name") == "Bash":
                        bash.append((ts or "")[:19] + "  " + str(x.get("input", {}).get("command", ""))[:220])
        elif o.get("type") == "user":
            pending = False
    v["last_ts"] = last_ts
    v["last_assistant"] = last_assist
    v["bash"] = bash[-14:]
    try:
        v["mtime"] = os.path.getmtime(tp)
    except OSError:
        v["mtime"] = 0
    v["pending_tool"] = pending
    return v


def git_state(row):
    tree = row["worktree"]
    br = row["branch"]
    if not os.path.isdir(tree):
        return "  (worktree does not exist yet)"
    out = []
    out.append("  HEAD        " + sh(["git", "-C", tree, "log", "-1", "--format=%h %ad %s",
                                      "--date=format:%m-%d %H:%M"]))
    out.append("  branch      " + sh(["git", "-C", tree, "symbolic-ref", "--short", "HEAD"]))
    ab = sh(["git", "-C", tree, "rev-list", "--left-right", "--count", f"origin/{br}...{br}"])
    out.append("  vs origin   " + (ab if ab and "failed" not in ab else "(no remote ref yet)"))
    dirty = sh(["git", "-C", tree, "status", "--porcelain"])
    n = len([x for x in dirty.splitlines() if x.strip()])
    out.append(f"  dirty       {n} path(s)")
    if n:
        out.extend("    " + x for x in dirty.splitlines()[:20])
    base = sh(["git", "-C", tree, "merge-base", br, "origin/main"])
    if base and len(base) == 40:
        log = sh(["git", "-C", tree, "log", "--format=  %h %s", f"{base}..{br}"])
        if log:
            out.append("  commits on this branch since origin/main:")
            out.extend("  " + x for x in log.splitlines()[:20])
    return "\n".join(out)


def siblings_since(rows, me):
    """What every OTHER slot committed recently, so the follow-up can say what
    not to duplicate. Cross-session awareness is the whole point."""
    out = []
    for r in rows:
        if r["slot"] == me:
            continue
        tree = r["worktree"]
        if not os.path.isdir(tree):
            continue
        log = sh(["git", "-C", tree, "log", "-3", "--format=  %h %ad %s",
                  "--date=format:%m-%d %H:%M", r["branch"]])
        if log and "failed" not in log:
            out.append(f"  [{r['slot']} / {r['branch']}]")
            out.extend("  " + x for x in log.splitlines())
    return "\n".join(out) if out else "  (no sibling worktrees exist yet)"


def write_digest(rows, ids, v, row, n):
    os.makedirs(DIGESTS, exist_ok=True)
    path = os.path.join(DIGESTS, f"{v['slot']}-{n:03d}.md")
    board = ""
    if os.path.exists(BOARD):
        board = "".join(open(BOARD).readlines()[-30:])
    body = f"""# DIGEST {v['slot']} #{n}

slot         {v['slot']}
branch       {v['branch']}
worktree     {v['worktree']}
session id   {v['session_id']}
transcript   {v['transcript']}
last event   {v['last_ts']}
events       {v['n_events']}

## LIVE GIT STATE (read now, not from the session's claims)
{git_state(row)}

## WHAT THIS SESSION LAST SAID, IN FULL
{v['last_assistant'] if v['last_assistant'] else '(no assistant text found)'}

## THE LAST COMMANDS IT RAN
{chr(10).join('  ' + b for b in v['bash']) if v['bash'] else '  (none)'}

## WHAT ITS SIBLINGS HAVE DONE
{siblings_since(rows, v['slot'])}

## BOARD TAIL
{board if board else '  (board empty)'}

## FOLLOW-UP CHECKLIST, for whoever writes the next message
- Did it actually finish what it claimed, or did it only describe finishing it?
- Does its own git state contradict any claim above?
- Is there a number in its last message that nobody re-derived?
- Is it about to duplicate a sibling's work?
- Is it blocked on something only Josie can do, and if so has it kept working
  on everything else in its scope?
- Does the next step need a GPU node, and is one live?
"""
    with open(path, "w") as f:
        f.write(body)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--idle-s", type=int, default=120)
    ap.add_argument("--interval", type=int, default=30)
    a = ap.parse_args()

    rows = load_plan()
    ids = load_ids()
    seen = {}
    if os.path.exists(SEEN):
        try:
            seen = json.load(open(SEEN))
        except Exception:
            seen = {}

    def pass_once(emit=True):
        changed = False
        for row in rows:
            sid = ids.get(row["slot"])
            if not sid:
                continue
            v = session_view(row, sid)
            if not v["exists"]:
                continue
            age = time.time() - v.get("mtime", 0)
            idle = age >= a.idle_s and not v.get("pending_tool")
            key = row["slot"]
            prev = seen.get(key, {})
            if a.status:
                print(f"{key:14s} idle={idle!s:5s} age={int(age):5d}s "
                      f"events={v['n_events']:5d} last={v['last_ts']}")
                continue
            if idle and prev.get("last_ts") != v["last_ts"]:
                n = prev.get("n", 0) + 1
                p = write_digest(rows, ids, v, row, n)
                seen[key] = {"last_ts": v["last_ts"], "n": n, "digest": p}
                changed = True
                if emit:
                    print(f"IDLE {key} idle_for={int(age)}s digest={p}", flush=True)
        if changed:
            with open(SEEN, "w") as f:
                json.dump(seen, f, indent=1)

    if a.status:
        pass_once(emit=False)
        return
    if a.once:
        pass_once()
        return
    if a.watch:
        while True:
            pass_once()
            time.sleep(a.interval)
    ap.print_help()


if __name__ == "__main__":
    main()
