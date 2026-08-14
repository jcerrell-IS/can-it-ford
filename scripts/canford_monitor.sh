#!/usr/bin/env bash
# Health monitor for the canford dispatch session.
# Answers one question per pane: is it alive, is it working, is it still in its lane?
#   ./canford_monitor.sh          one-shot report
#   ./canford_monitor.sh watch    refresh every 20s (used by the monitor window)
set -uo pipefail
REPO=/Users/josie/can-it-ford

report() {
  tmux list-panes -a -F '#{pane_id}|#{pane_title}|#{pane_current_path}|#{pane_dead}' 2>/dev/null > /tmp/canford_panes.txt || {
    echo "tmux session not reachable"; return 1; }
  /usr/bin/python3 - "$REPO" <<'PY'
import subprocess,sys,re,datetime
repo=sys.argv[1]
def sh(c,cwd=None):
    try: return subprocess.run(c,capture_output=True,text=True,timeout=15,cwd=cwd).stdout.strip()
    except Exception: return ""
# expected branch per dispatch label, so drift is detectable
EXP={"D1":"claude/rtfd-test-phase-1-4-569130","D2":"claude/fork-vista-triage",
 "D3":"claude/credential-exposure-2026-08-13-DO-NOT-PUSH","D4":"claude/fork-register-reconcile",
 "D5":"claude/fork-three-class","D6":"claude/fork-render-3class","D7":"(no repo)",
 "D8":"claude/moving-vehicle-exploratory-2026-08-11","D9":"claude/fork-moving-driver",
 "D10":"claude/fork-scene","D11":"claude/fork-validation","D12":"claude/fork-protocol",
 "D13":"claude/fork-chrono-eval"}
BUSY=re.compile(r"(Synthesizing|Thinking|Exploring|Reading|Searching|Running|Pondering|Working|Divining|Musing|Cogitating|Deliberat|Comput|Analyz|Reticulat|Herding|Puzzl|Noodl|Wrangl)",re.I)
ERR=re.compile(r"(Traceback|command not found|Permission denied|fatal:|error:|API Error|rate.?limit)",re.I)
print("="*104)
print(f"CANFORD MONITOR  {datetime.datetime.now().strftime('%H:%M:%S')}")
print("="*104)
print(f"{'PANE':<26}{'CTX':>5}  {'STATE':<10}{'BRANCH OK':<10}{'DIRTY':>6}  {'AHEAD':>5}  NOTE")
print("-"*104)
alive=busy=drift=err=0
for line in open('/tmp/canford_panes.txt'):
    pid,title,path,dead=line.strip().split('|')
    km=re.search(r"\bD(\d+)\b",title)
    if not km: continue          # skip the monitor pane and anything unlabelled
    key="D"+km.group(1)
    t=title[km.start():].strip()
    cap=sh(['tmux','capture-pane','-t',pid,'-p','-S','-60'])
    if not cap:
        print(f"{t:<26}{'-':>5}  {'DEAD':<10}"); continue
    alive+=1
    m=re.search(r"ctx (\d+)%",cap); ctx=m.group(1)+"%" if m else "?"
    state="working" if BUSY.search(cap.splitlines()[-6:] and "\n".join(cap.splitlines()[-6:])) else "idle"
    if state=="working": busy+=1
    br=sh(['git','-C',path,'rev-parse','--abbrev-ref','HEAD']) or "(no repo)"
    exp=EXP.get(key,"?")
    ok = "yes" if (br==exp or (exp=="(no repo)" and br=="(no repo)")) else "DRIFT"
    if ok=="DRIFT": drift+=1
    dirty=len([x for x in sh(['git','-C',path,'status','--porcelain=v1']).splitlines() if x]) if br!="(no repo)" else 0
    ahead=sh(['git','-C',path,'rev-list','--count','main..HEAD']) if br!="(no repo)" else ""
    note=""
    tail="\n".join(cap.splitlines()[-25:])
    if ERR.search(tail): note="ERROR-TEXT"; err+=1
    if "Do you want" in tail or "❯ 1." in tail: note=(note+" AWAITING-INPUT").strip()
    print(f"{t:<26}{ctx:>5}  {state:<10}{ok:<10}{dirty:>6}  {ahead:>5}  {note}")
print("-"*104)
print(f"alive {alive}/13   working {busy}   branch-drift {drift}   panes-with-error-text {err}")
if drift: print("!! BRANCH DRIFT: a pane left its assigned branch. Investigate before it commits.")
PY
}

case "${1:-}" in
  watch) while true; do clear; report; sleep 20; done ;;
  *)     report ;;
esac
