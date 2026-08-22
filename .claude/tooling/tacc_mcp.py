#!/usr/bin/env python3
"""TACC MCP server for can-it-ford. Vista (GH200, aarch64) and LS6 (A100, x86).

WHY THIS EXISTS. Every cluster interaction today shells out to scripts/tacc.sh
and parses text. On 2026-08-14 that cost, measured:

  * ~40 min of dead GH200 allocation before anyone discovered that
    `srun --jobid=` into a live idev REQUIRES `--overlap`, or the step sits
    PENDING and dies with "Cancelled pending job step with signal 15".
  * A whole-fleet LS6 outage: 13 sessions multiplexing one SSH ControlMaster
    hit the server session limit, every session lost LS6 at once, and running
    steps died after writing ~1.8 GB that was then orphaned.
  * Long probes killed by tacc.sh's TACC_TIMEOUT=60 default.
  * `import warpmpm` reporting OK on LS6 against a SIX-LINE STUB whose body is
    `raise RuntimeError("stub: solver not needed for the PLY format check")`.
    The coordinator then told every session that environment was verified.

Each of those is a typed field or an auto-injected flag below. Zero deps.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_scaffold import Server  # noqa: E402

REPO = os.environ.get("CANFORD_REPO") or "/Users/josie/can-it-ford"
# ^ env override added 2026-08-18 so the server works from a plugin cache copy
#   and from a fresh clone. Absent the env var, behaviour is byte-identical.
USER = "jcerrell0629"
ACCOUNT = "BCS20003"

HOSTS = {
    "vista": {
        "arch": "aarch64",
        "dev_partition": "gh-dev",
        "python": "/work/11603/jcerrell0629/vista/can-it-ford/mpm-engine/.venv/bin/python",
        "scratch": "/scratch/11603/jcerrell0629",
        "work": "/work/11603/jcerrell0629/vista",
        "warpmpm": True,   # real warpmpm, verified 2026-08-14
        "moving_sdf": True,  # set_sdf_pose / sdf_wrench present
        "notes": "HOME is ~89% full: never pip install into it, build under /work.",
    },
    "ls6": {
        "arch": "x86_64",
        "dev_partition": "gpu-a100-dev",
        "python": "/scratch/11603/jcerrell0629/warpmpm_ls6_env/bin/python",
        "scratch": "/scratch/11603/jcerrell0629",
        "work": "/work/11603/jcerrell0629/ls6",
        "warpmpm": False,  # ONLY a 6-line stub exists; see env_probe
        "moving_sdf": False,
        "notes": "warpmpm is a STUB here. x86 machine: use for Chrono and "
                 "splashsurf (pysplashsurf wheels exclude aarch64).",
    },
}

srv = Server("canford-tacc")


def _ssh(host, cmd, timeout=600):
    """One place where ssh happens, so the ControlMaster is not contended by
    13 independent callers. Returns (rc, stdout, stderr)."""
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host, cmd],
            capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after %ds" % timeout
    except Exception as e:
        return 1, "", str(e)


def _socket_hint(err):
    if "refused by peer" in err or "Permission denied" in err or "ControlMaster" in err:
        return ("SSH ControlMaster is cold or saturated. Run `ssh %s` once "
                "interactively. If it was working a moment ago, this is "
                "CONTENTION: too many concurrent sessions on one socket." )
    return None


@srv.tool(
    "tacc_hostinfo",
    "Static, hard-won facts about each cluster. Read this BEFORE planning any "
    "run. It encodes that LS6 cannot run warpmpm and that Vista is the only "
    "machine with the moving-SDF API.",
    {"type": "object", "properties": {
        "host": {"type": "string", "enum": ["vista", "ls6", "both"],
                 "default": "both"}}},
)
def tacc_hostinfo(host="both"):
    if host == "both":
        return HOSTS
    return HOSTS.get(host, {"error": "unknown host"})


@srv.tool(
    "tacc_alloc_status",
    "Live allocation state as STRUCTURED data: job id, node, partition, "
    "elapsed and REMAINING seconds, plus SU balance. Use remaining_s instead "
    "of estimating elapsed time yourself; on 2026-08-14 a coordinator drifted "
    "its own clock by ~1 hour and time-boxed sessions against a deadline that "
    "did not exist, while `squeue -o %L` had the answer all along.",
    {"type": "object", "properties": {
        "host": {"type": "string", "enum": ["vista", "ls6"]}},
     "required": ["host"]},
)
def tacc_alloc_status(host):
    rc, out, err = _ssh(host, "squeue -u %s -h -o '%%i|%%j|%%P|%%T|%%M|%%L|%%N'" % USER, 60)
    if rc != 0:
        return {"host": host, "error": err.strip()[-400:],
                "hint": _socket_hint(err)}
    jobs = []
    for ln in out.splitlines():
        p = ln.split("|")
        if len(p) < 7:
            continue
        jobs.append({"jobid": p[0].strip(), "name": p[1].strip(),
                     "partition": p[2].strip(), "state": p[3].strip(),
                     "elapsed": p[4].strip(), "remaining": p[5].strip(),
                     "node": p[6].strip()})
    running = [j for j in jobs if j["state"] == "RUNNING"]
    _, out2, _ = _ssh(host, "/usr/local/etc/taccinfo 2>/dev/null | grep -A3 'Name'", 60)
    su = None
    m = re.search(r"(\d+)\s+\d{4}-\d{2}-\d{2}", out2 or "")
    if m:
        su = int(m.group(1))
    return {"host": host, "jobs": jobs, "n_running": len(running),
            "live_allocation": running[0] if running else None,
            "su_remaining": su,
            "pending_blocked": [j for j in jobs if j["state"] == "PENDING"]}


@srv.tool(
    "tacc_env_probe",
    "Verify an interpreter and a module, WITH STUB DETECTION. Returns "
    "source_file, source_lines and is_stub. A bare `import` is not evidence: "
    "on LS6 `import warpmpm` succeeds against a 6-line file that raises "
    "RuntimeError on first use.",
    {"type": "object", "properties": {
        "host": {"type": "string", "enum": ["vista", "ls6"]},
        "module": {"type": "string", "default": "warpmpm"},
        "min_lines": {"type": "integer", "default": 40}},
     "required": ["host"]},
)
def tacc_env_probe(host, module="warpmpm", min_lines=40):
    h = HOSTS[host]
    py = h["python"]
    code = (
        "import importlib,os,sys,json\n"
        "d={'python':sys.executable,'version':sys.version.split()[0]}\n"
        "try:\n"
        "    m=importlib.import_module(%r)\n"
        "    f=getattr(m,'__file__',None); d['module_file']=f\n"
        "    n=0\n"
        "    if f and os.path.exists(f):\n"
        "        n=sum(1 for _ in open(f,errors='replace'))\n"
        "    d['module_lines']=n\n"
        "    d['symbols']=sorted([s for s in dir(m) if not s.startswith('_')])[:15]\n"
        "    d['import_ok']=True\n"
        "except Exception as e:\n"
        "    d['import_ok']=False; d['error']='%%s: %%s'%%(type(e).__name__,e)\n"
        "print(json.dumps(d))\n" % module
    )
    rc, out, err = _ssh(host, "%s -c %s" % (py, json_quote(code)), 180)
    if rc != 0 or not out.strip():
        return {"host": host, "module": module, "error": (err or out).strip()[-400:],
                "hint": _socket_hint(err)}
    try:
        d = json.loads(out.strip().splitlines()[-1])
    except ValueError:
        return {"host": host, "raw": out[-400:]}
    lines = d.get("module_lines", 0) or 0
    d["is_stub"] = bool(d.get("import_ok")) and lines < min_lines
    d["VERDICT"] = ("STUB, DO NOT USE: imports but the source is only %d lines"
                    % lines) if d["is_stub"] else (
        "usable" if d.get("import_ok") else "import failed")
    d["host"] = host
    d["module"] = module
    return d


def json_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


@srv.tool(
    "tacc_submit",
    "Run a command on a live allocation, correctly, detached. Auto-injects "
    "--overlap when an idev is running (without it the step hangs and dies), "
    "always passes both -p and -t (the TACC submit filter rejects srun "
    "without both), and wraps in `setsid nohup ... </dev/null &` so an SSH "
    "socket drop cannot kill the run.",
    {"type": "object", "properties": {
        "host": {"type": "string", "enum": ["vista", "ls6"]},
        "command": {"type": "string", "description": "the command to run on the node"},
        "walltime": {"type": "string", "default": "00:30:00"},
        "logfile": {"type": "string", "description": "absolute path on the cluster"},
        "cwd": {"type": "string", "default": ""},
        "nodes": {"type": "integer", "default": 1}},
     "required": ["host", "command", "logfile"]},
)
def tacc_submit(host, command, logfile, walltime="00:30:00", cwd="", nodes=1):
    st = tacc_alloc_status(host)
    if st.get("error"):
        return st
    live = st.get("live_allocation")
    if not live:
        return {"host": host, "error": "no RUNNING allocation",
                "action": "start one with: idev -A %s -p %s -N 1 -n 1 -t 02:00:00"
                          % (ACCOUNT, HOSTS[host]["dev_partition"]),
                "note": "A fresh sbatch will queue BEHIND your own idev on "
                        "QOSMaxJobsPerUserLimit and never start."}
    part = live["partition"]
    jid = live["jobid"]
    is_idev = live["name"].startswith("idv")
    overlap = "--overlap " if is_idev else ""
    cd = ("cd %s && " % cwd) if cwd else ""
    full = ("%ssetsid nohup srun --jobid=%s %s-p %s -t %s -N%d -n1 %s "
            "< /dev/null > %s 2>&1 & disown; sleep 2; echo LAUNCHED %s"
            % (cd, jid, overlap, part, walltime, nodes, command, logfile, jid))
    rc, out, err = _ssh(host, full, 180)
    return {"host": host, "jobid": jid, "node": live["node"],
            "remaining": live["remaining"], "overlap_injected": bool(overlap),
            "logfile": logfile, "rc": rc,
            "stdout": out.strip()[-300:], "stderr": err.strip()[-300:],
            "next": "poll with tacc_tail(host, logfile)"}


@srv.tool(
    "tacc_tail",
    "Tail a log file on the cluster without a full round trip.",
    {"type": "object", "properties": {
        "host": {"type": "string", "enum": ["vista", "ls6"]},
        "path": {"type": "string"},
        "lines": {"type": "integer", "default": 30}},
     "required": ["host", "path"]},
)
def tacc_tail(host, path, lines=30):
    rc, out, err = _ssh(host, "tail -%d %s 2>&1" % (lines, path), 90)
    return {"host": host, "path": path, "rc": rc, "text": out[-4000:],
            "stderr": err.strip()[-200:]}


@srv.tool(
    "tacc_gpu",
    "GPU utilization on the allocated node. Note an instantaneous 0% does NOT "
    "mean nothing ran: on 2026-08-14 polls landed between 24 consecutive runs "
    "and the coordinator wrongly reported the node idle.",
    {"type": "object", "properties": {
        "host": {"type": "string", "enum": ["vista", "ls6"]}},
     "required": ["host"]},
)
def tacc_gpu(host):
    st = tacc_alloc_status(host)
    live = st.get("live_allocation")
    if not live:
        return {"host": host, "error": "no running allocation"}
    q = ("nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used "
         "--format=csv,noheader")
    rc, out, err = _ssh(host, "srun --jobid=%s --overlap -p %s -t 00:02:00 -N1 -n1 %s"
                        % (live["jobid"], live["partition"], q), 150)
    return {"host": host, "node": live["node"], "rc": rc,
            "gpus": [l.strip() for l in out.splitlines() if "," in l],
            "caveat": "instantaneous sample; 0% is not proof of an idle node",
            "stderr": err.strip()[-200:]}


if __name__ == "__main__":
    srv.run()
