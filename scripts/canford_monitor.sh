#!/usr/bin/env bash
# ============================================================================
# canford_monitor.sh  control surface for the 13-dispatch tmux session.
#
# It answers four questions the tiled layout could not:
#   1. Is every session actually MOVING, or has one quietly stalled?
#   2. Are two sessions about to overwrite each other?
#   3. Is anything blocked waiting on me?
#   4. How do I read one specific session?
#
#   ./canford_monitor.sh spread          one full window per dispatch (SAFE:
#                                        uses break-pane, kills nothing)
#   ./canford_monitor.sh status          one-shot report
#   ./canford_monitor.sh watch [secs]    looping report (default 20s)
#   ./canford_monitor.sh read <N> [n]    dump last n lines of dispatch N
#   ./canford_monitor.sh reply <N> <txt> type txt into N and submit
#   ./canford_monitor.sh key <N> <key>   send a raw key (Escape, Enter, 3)
#   ./canford_monitor.sh rebaseline      re-freeze the main-tree baseline
#   ./canford_monitor.sh legend          how to read/attach a session
#
# WHY A MAIN-TREE BASELINE
#   Worktrees share one repo. A session that writes via an absolute
#   /Users/josie/can-it-ford/... path lands in the MAIN checkout instead of
#   its own worktree, silently, on whatever branch main has out. That is the
#   2026-08-07 failure. We freeze the main tree's dirty set once, then any
#   NEW entry is an alarm rather than background noise.
# ============================================================================
set -uo pipefail

SESSION=canford
REPO=/Users/josie/can-it-ford
STATE="${TMPDIR:-/tmp}/canford_state"
mkdir -p "$STATE"

# id | label | working dir | expected branch
DISPATCHES='
1|PUSH-ORPHANED-g128|.claude/worktrees/rtfd-test-phase-1-4-569130|claude/rtfd-test-phase-1-4-569130
2|VISTA-REALISM-TRIAGE|.claude/worktrees/fork-vista-triage|claude/fork-vista-triage
3|CREDENTIALS-HARD-STOP|.claude/worktrees/fork-credentials-DO-NOT-PUSH|claude/credential-exposure-2026-08-13-DO-NOT-PUSH
4|REGISTER-RECONCILE|.claude/worktrees/fork-register-reconcile|claude/fork-register-reconcile
5|THREE-CLASS-MATCHED|.claude/worktrees/fork-three-class|claude/fork-three-class
6|POSTER-GRADE-VISUALS|.claude/worktrees/fork-render-3class|claude/fork-render-3class
7|CORPUS-SPRINT2|@/Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13|-
8|PREFLIGHT-RESCUE|@/Users/josie/can-it-ford-moving-vehicle|claude/moving-vehicle-exploratory-2026-08-11
9|MOVING-DRIVER|.claude/worktrees/fork-moving-driver|claude/fork-moving-driver
10|SCENE-AND-DOMAIN|.claude/worktrees/fork-scene|claude/fork-scene
11|MOVING-VALIDATION|.claude/worktrees/fork-validation|claude/fork-validation
12|PROTOCOL-AND-RECHECK|.claude/worktrees/fork-protocol|claude/fork-protocol
13|CHRONO-GH200-GONOGO|.claude/worktrees/fork-chrono-eval|claude/fork-chrono-eval
'

pane_for() {   # dispatch id -> pane id, matched on the D<N> word boundary
  tmux list-panes -a -F '#{pane_id}|#{pane_title}' 2>/dev/null \
    | /usr/bin/python3 -c '
import sys,re
want=sys.argv[1]
for ln in sys.stdin:
    pid,_,title=ln.strip().partition("|")
    m=re.search(r"\bD(\d+)\b",title)
    if m and m.group(1)==want: print(pid); break
' "$1"
}

# ---------------------------------------------------------------- spread ----
# One full window per dispatch. break-pane MOVES a running pane, it does not
# restart it, so no session loses its context or its in-flight turn.
spread() {
  tmux has-session -t "$SESSION" 2>/dev/null || { echo "no session '$SESSION'"; return 1; }
  tmux set -t "$SESSION" -g renumber-windows on

  # Break out every pane except the last one left in each window, then rename.
  for w in $(tmux list-windows -t "$SESSION" -F '#{window_index}'); do
    local name; name=$(tmux display-message -p -t "$SESSION:$w" '#{window_name}')
    [ "$name" = "monitor" ] && continue
    while [ "$(tmux list-panes -t "$SESSION:$w" 2>/dev/null | wc -l | tr -d ' ')" -gt 1 ]; do
      local last; last=$(tmux list-panes -t "$SESSION:$w" -F '#{pane_id}' | tail -1)
      tmux break-pane -d -s "$last" 2>/dev/null || break
    done
  done

  # Name each window after the dispatch its pane carries.
  for w in $(tmux list-windows -t "$SESSION" -F '#{window_index}'); do
    local p t
    p=$(tmux list-panes -t "$SESSION:$w" -F '#{pane_id}' | head -1)
    t=$(tmux display-message -p -t "$p" '#{pane_title}')
    case "$t" in
      *MONITOR*) tmux rename-window -t "$SESSION:$w" "0-MONITOR" ;;
      *) local n; n=$(echo "$t" | /usr/bin/python3 -c 'import sys,re;m=re.search(r"\bD(\d+)\b",sys.stdin.read());print(m.group(1) if m else "")')
         [ -n "$n" ] && tmux rename-window -t "$SESSION:$w" "D$n" ;;
    esac
  done

  # Order: monitor first, then D1..D13, so window index == dispatch number.
  # Two phases via a temp range. A direct move fails whenever the target index
  # is already taken, which it almost always is.
  local mw; mw=$(tmux list-windows -t "$SESSION" -F '#{window_index} #{window_name}' | /usr/bin/grep MONITOR | cut -d' ' -f1)
  [ -n "${mw:-}" ] && tmux move-window -d -s "$SESSION:$mw" -t "$SESSION:100" 2>/dev/null
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13; do
    local sw; sw=$(tmux list-windows -t "$SESSION" -F '#{window_index} #{window_name}' \
      | /usr/bin/grep -w "D$i\$" | cut -d' ' -f1 | head -1)
    [ -n "${sw:-}" ] && tmux move-window -d -s "$SESSION:$sw" -t "$SESSION:$((100+i))" 2>/dev/null
  done
  tmux move-window -d -s "$SESSION:100" -t "$SESSION:0" 2>/dev/null
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13; do
    tmux move-window -d -s "$SESSION:$((100+i))" -t "$SESSION:$i" 2>/dev/null
  done

  # Chrome that survives a detach.
  tmux set -t "$SESSION" -g pane-border-status top
  tmux set -t "$SESSION" -g pane-border-lines heavy
  tmux set -t "$SESSION" -g pane-border-format ' #[bold]#{pane_title} '
  tmux set -t "$SESSION" -g pane-active-border-style 'fg=colour231,bg=colour236,bold'
  tmux set -t "$SESSION" -g mouse on
  tmux set -t "$SESSION" -g status on
  tmux set -t "$SESSION" -g status-interval 5
  tmux set -t "$SESSION" -g status-style 'bg=colour234,fg=colour252'
  tmux set -t "$SESSION" -g status-left '#[bold,fg=colour208] FORD #[default]'
  tmux set -t "$SESSION" -g status-left-length 12
  tmux set -t "$SESSION" -g status-right '#[bold]%H:%M '
  tmux set -t "$SESSION" -g status-right-length 8
  tmux set -t "$SESSION" -g window-status-format '#I'
  tmux set -t "$SESSION" -g window-status-current-format '#[bold,fg=colour16,bg=colour208] #I:#W #[default]'
  tmux set -t "$SESSION" -g window-status-separator ' '
  # Alt-1..Alt-9 jump straight to a dispatch, no prefix needed.
  for i in 1 2 3 4 5 6 7 8 9; do tmux bind-key -n "M-$i" select-window -t "$SESSION:$i"; done
  tmux bind-key -n M-0 select-window -t "$SESSION:0"
  echo "spread: $(tmux list-windows -t "$SESSION" | wc -l | tr -d ' ') windows, one session each"
  tmux list-windows -t "$SESSION" -F '  #{window_index}: #{window_name}  #{pane_width}x#{pane_height}'
}

# ---------------------------------------------------------------- report ----
report() {
  tmux list-panes -a -F '#{pane_id}|#{pane_title}|#{pane_current_path}' 2>/dev/null > "$STATE/panes.txt" || {
    echo "tmux session not reachable"; return 1; }
  DISPATCHES="$DISPATCHES" /usr/bin/python3 - "$REPO" "$STATE" <<'PY'
import subprocess,sys,re,os,time,hashlib,datetime
repo,state=sys.argv[1],sys.argv[2]
W=64
def sh(c,cwd=None,t=15):
    try: return subprocess.run(c,capture_output=True,text=True,timeout=t,cwd=cwd).stdout.strip()
    except Exception: return ""

D=[]
for ln in os.environ["DISPATCHES"].strip().splitlines():
    i,lbl,d,br=ln.split("|")
    D.append((i,lbl,(d[1:] if d.startswith("@") else os.path.join(repo,d)),br))

panes={}
for ln in open(os.path.join(state,"panes.txt")):
    pid,title,path=ln.rstrip("\n").split("|")
    m=re.search(r"\bD(\d+)\b",title)
    if m: panes[m.group(1)]=(pid,path)

ASK=re.compile(r"(Enter to confirm|Do you want|❯ 1\.|\(y/n\)|Press Enter to)")
ERR=re.compile(r"(Traceback|command not found|Permission denied|fatal:|API Error|rate.?limit|No such file)",re.I)

def rule(ch="═"): print(ch*W)
now=time.time()
rows=[];dirty_map={};alive=moving=blocked=0;errs=[]

for i,lbl,d,br in D:
    pid,path=panes.get(i,(None,None))
    if not pid:
        rows.append((i,lbl,"GONE","","","","pane missing")); continue
    vis=sh(['tmux','capture-pane','-t',pid,'-p'])
    alive+=1
    # Activity by content hash, not by spinner word. A spinner regex breaks the
    # moment the client changes its verb list; a hash cannot.
    h=hashlib.sha1(vis.encode()).hexdigest()
    f=os.path.join(state,f"act_{i}.txt")
    prev,ts=("",now)
    if os.path.exists(f):
        try:
            prev,tss=open(f).read().split("\n",1); ts=float(tss)
        except Exception: pass
    if h!=prev:
        ts=now; open(f,"w").write(h+"\n"+str(now))
    age=int(now-ts)
    if   age<60:  st="MOVING"; moving+=1
    elif age<300: st="quiet"
    else:         st=f"STALL{age//60}m"
    ctx=(re.search(r"ctx (\d+)%",vis) or [None,"?"])[1] if re.search(r"ctx (\d+)%",vis) else "?"
    flag=""
    if ASK.search(vis): flag="NEEDS-YOU"; blocked+=1
    elif ERR.search(vis): flag="err?"; errs.append(i)
    livebr=sh(['git','-C',path,'rev-parse','--abbrev-ref','HEAD']) or "-"
    if br!="-" and livebr!=br: flag=("DRIFT "+flag).strip()
    stat=[x for x in sh(['git','-C',path,'status','--porcelain=v1']).splitlines() if x] if br!="-" else []
    staged=len([x for x in stat if x[:1] not in (" ","?")])
    # Commits reachable from NO remote. This, not "ahead of main", is the
    # register-item-16 loss exposure: work that exists on one disk only.
    norem=sh(['git','-C',path,'rev-list','--count',livebr,'--not','--remotes=origin']) if br!="-" else ""
    if staged>8: flag=("STAGED>8-HOOK-WILL-REFUSE "+flag).strip()
    # Uncommitted work that has outlived its own reasoning is the other risk.
    # Age it by the OLDEST dirty file's mtime, not by the branch's last commit:
    # a worktree freshly cut from main inherits main's commit time and would
    # otherwise read as a day stale on its first minute of work.
    if stat:
        ages=[]
        for x in stat:
            fp=os.path.join(path,x[3:].strip().rstrip("/"))
            try: ages.append(now-os.path.getmtime(fp))
            except OSError: pass
        if ages:
            mins=int(max(ages)/60)
            if mins>45: flag=(f"UNCOMMITTED-{mins}m "+flag).strip()
    for x in stat:
        p=x[3:].strip()
        dirty_map.setdefault(p,[]).append(i)
    rows.append((i,lbl,st,ctx,f"{len(stat)}",norem,flag))

rule()
print(f" CANFORD  {datetime.datetime.now():%H:%M:%S}   "
      f"{alive}/13 alive  {moving} moving  {blocked} need you")
rule()
print(" ID  SESSION               STATE   CTX  DIRTY NOREM")
for i,lbl,st,ctx,dty,nr,flag in rows:
    print(f" D{i:<3}{lbl[:21]:<22}{st:<8}{ctx+'%' if ctx!='?' else '?':>4} {dty:>5} {nr:>5}"
          + (f"\n      → {flag}" if flag else ""))
risk=[i for i,_,_,_,_,nr,_ in rows if nr.isdigit() and int(nr)>0 and i!="3"]
if risk: print(f" NOREM>0 on D{', D'.join(risk)}: those commits exist on ONE DISK.")
print(" (D3 is DO-NOT-PUSH by design, its NOREM is correct.)")

# ---- collisions: the only cross-session overwrite signal that matters ------
print()
rule("─")
print(" OVERWRITE CHECK")
clash=[(p,v) for p,v in dirty_map.items() if len(set(v))>1]
if clash:
    for p,v in sorted(clash):
        print(f" !! {p}  edited by D{' D'.join(sorted(set(v)))}")
else:
    print(" ok  no file is dirty in two worktrees at once")

# main checkout: any NEW dirty entry means a session wrote outside its worktree
base=os.path.join(state,"main_baseline.txt")
cur=set(x[3:].strip() for x in sh(['git','-C',repo,'status','--porcelain=v1']).splitlines() if x)
if not os.path.exists(base):
    open(base,"w").write("\n".join(sorted(cur)))
    print(f" ok  main-tree baseline frozen at {len(cur)} pre-existing entries")
else:
    known=set(x for x in open(base).read().splitlines() if x)
    new=sorted(cur-known)
    if new:
        print(f" !! MAIN CHECKOUT got {len(new)} new path(s). A session wrote via an")
        print("    absolute /Users/josie/can-it-ford/... path instead of its worktree:")
        for p in new[:8]: print(f"      {p}")
    else:
        print(" ok  main checkout unchanged since baseline")

# ---- remote work ----------------------------------------------------------
print()
rule("─")
print(" TACC")
for host in ("vista","ls6"):
    q=sh([os.path.join(repo,"scripts","tacc.sh"),host,
          'squeue -u $USER -h -o "%.9i %.9P %.16j %.8T %R"'],t=45)
    if not q.strip(): print(f" {host:<6} queue empty")
    else:
        for ln in q.splitlines()[:4]: print(f" {host:<6}{ln.strip()[:56]}")

print()
rule("─")
print(" READ ONE SESSION")
print("  Alt-1..Alt-9        jump to D1..D9 (no prefix key)")
print("  Ctrl-b '  then 10   jump to D10..D13")
print("  Alt-0               back to this monitor")
print("  Ctrl-b [            scroll back, q to exit scroll")
print("  ./scripts/canford_monitor.sh read 9 120")
print("  ./scripts/canford_monitor.sh reply 9 'your answer'")
rule()
PY
}

read_pane() {
  local p; p=$(pane_for "$1"); [ -z "$p" ] && { echo "no pane for D$1"; return 1; }
  tmux capture-pane -t "$p" -p -S "-${2:-120}"
}

reply_pane() {
  local id="$1"; shift
  local p; p=$(pane_for "$id"); [ -z "$p" ] && { echo "no pane for D$id"; return 1; }
  tmux load-buffer -b canfordreply - <<< "$*"
  tmux paste-buffer -b canfordreply -t "$p" -d
  sleep 1
  tmux send-keys -t "$p" Enter          # C-m does NOT submit in this client
  echo "sent to D$id ($p)"
}

key_pane() {
  local p; p=$(pane_for "$1"); [ -z "$p" ] && { echo "no pane for D$1"; return 1; }
  tmux send-keys -t "$p" "$2"; echo "key '$2' -> D$1 ($p)"
}

# ---------------------------------------------------------------- triage ----
# Classify every pending prompt. Default is REPORT ONLY. --apply answers only
# the ones classified AUTO-OK; anything else is escalated to Josie by design.
# The default verdict is ESCALATE, so a pattern nobody anticipated is never
# auto-answered.
triage() {
  local apply="${1:-}"
  tmux list-panes -a -F '#{pane_id}|#{pane_title}' > "$STATE/panes_t.txt"
  APPLY="$apply" /usr/bin/python3 - "$STATE" <<'PY'
import subprocess,sys,re,os
state=sys.argv[1]; apply=os.environ.get("APPLY","")=="--apply"
def cap(p):
    try: return subprocess.run(['tmux','capture-pane','-t',p,'-p','-S','-40'],
        capture_output=True,text=True,timeout=10).stdout
    except Exception: return ""
ASK=re.compile(r"(Do you want to proceed|Enter to confirm|❯ 1\.)")
# Anything on this list goes to a human no matter what else the command says.
STOP=re.compile(r"(git push|--force|force-push|rm -rf|rm -r |git add -A|git add \.|"
                r"commit -a\b|filter-repo|reset --hard|checkout main|"
                r"token|secret|credential|\.env|chmod|revoke|rotate)",re.I)
# Read-only git and scoped explicit-path commits are safe to wave through.
SAFE=re.compile(r"(git (log|status|diff|show|rev-list|rev-parse|ls-remote|ls-files|"
                r"bundle verify|check-ignore|cat-file)|commit -m .* -- )",re.I)
n=0
for ln in open(os.path.join(state,"panes_t.txt")):
    pid,_,title=ln.strip().partition("|")
    m=re.search(r"\bD(\d+)\b",title)
    if not m: continue
    v=cap(pid)
    if not ASK.search(v): continue
    n+=1
    ctxt=" ".join(v.splitlines()[-30:])
    if STOP.search(ctxt): verdict="ESCALATE (matched a hard-stop verb)"
    elif SAFE.search(ctxt): verdict="AUTO-OK"
    else: verdict="ESCALATE (unrecognised, defaulting to human)"
    print(f"D{m.group(1)}  {verdict}")
    for l in [x for x in v.splitlines() if x.strip()][-8:]: print("      "+l.strip()[:70])
    if apply and verdict=="AUTO-OK":
        subprocess.run(['tmux','send-keys','-t',pid,'1'])
        subprocess.run(['sleep','1'])
        subprocess.run(['tmux','send-keys','-t',pid,'Enter'])
        print(f"      -> approved")
if not n: print("no pane is waiting on a prompt")
PY
}

legend() {
  cat <<'EOF'
HOW TO WATCH
  tmux attach -t canford        attach (window 0 is the monitor)
  Alt-1 .. Alt-9                jump straight to D1..D9
  Ctrl-b ' then 10<Enter>       jump to D10..D13
  Ctrl-b w                      pick from a list of all 14 windows
  Ctrl-b [                      scroll back inside a session, q to quit
  Ctrl-b d                      detach, leaves everything running

WITHOUT ATTACHING
  ./scripts/canford_monitor.sh status        one-shot health report
  ./scripts/canford_monitor.sh read 9 200    last 200 lines of D9
  ./scripts/canford_monitor.sh reply 9 'go'  answer D9

WHAT THE STATES MEAN
  MOVING   output changed in the last 60s
  quiet    no output 1-5 min. Normal during a long tool call or subagent.
  STALLnm  no output for n minutes. Check it; it may be waiting or wedged.
  NEEDS-YOU a prompt is on screen. Nothing progresses until answered.
  DRIFT    the pane left its assigned branch. Investigate BEFORE it commits.
EOF
}

case "${1:-status}" in
  spread)     spread ;;
  status)     report ;;
  triage)     triage "${2:-}" ;;
  watch)      while true; do clear; report; sleep "${2:-20}"; done ;;
  read)       read_pane "${2:?dispatch number}" "${3:-120}" ;;
  reply)      id="${2:?dispatch number}"; shift 2; reply_pane "$id" "$@" ;;
  key)        key_pane "${2:?dispatch number}" "${3:?key}" ;;
  rebaseline) rm -f "$STATE/main_baseline.txt"; echo "baseline cleared, next report re-freezes it" ;;
  legend)     legend ;;
  *)          echo "usage: $0 {spread|status|watch [s]|read N [n]|reply N txt|key N k|rebaseline|legend}"; exit 1 ;;
esac
