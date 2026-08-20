"""
can-it-ford Weights & Biases helper.

Every W&B write from this repo should go through here, so that entity, project
and run metadata are identical whichever pane, worktree or agent made the call.

Use from the shell (auth is resolved for you):

    scripts/wb --py analysis/wb.py doctor
    scripts/wb --py analysis/wb.py runs --limit 10
    scripts/wb --py analysis/wb.py artifact-list
    scripts/wb --py analysis/wb.py artifact-put --path data/all_runs_inventory.csv \
                                                --name all_runs_inventory --type dataset
    scripts/wb --py analysis/wb.py artifact-get --name all_runs_inventory:latest --out /tmp/x
    scripts/wb --py analysis/wb.py log-csv --path data/all_runs_inventory.csv --name inventory
    scripts/wb --py analysis/wb.py snapshot

Use from python:

    import wb
    with wb.run(job_type="analysis", tags=["r10"]) as r:
        r.log({"drift_m": 0.041})
        wb.put_artifact(r, "data/all_runs_inventory.csv", "all_runs_inventory", "dataset")

DEPENDENCIES ARE DELIBERATELY THIN. The canitford-mpm venv has numpy, scipy and
matplotlib but NOT pandas and NOT pyarrow (measured 2026-08-20), so this module
uses stdlib csv and nothing heavier. Do not add a pandas import here without
installing it in that venv first; the failure would only surface at run time.

REPORTS ARE NOT HANDLED HERE. wandb_workspaces is absent from the venv, so
report creation goes through the W&B MCP server's create_wandb_report_tool
instead, which bundles its own copy. See .claude/skills/wandb-ops/SKILL.md.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import os
import pathlib
import subprocess
import sys

# Repo root, resolved from this file so it is worktree-correct rather than
# cwd-dependent. A `cd` elsewhere in the session must not change what this means.
REPO = pathlib.Path(__file__).resolve().parent.parent

ENTITY = os.environ.get("WANDB_ENTITY", "jcerrell29-claremont-mckenna-college")
PROJECT = os.environ.get("WANDB_PROJECT", "can-it-ford")

# The canonical files worth versioning. Each entry is (path, artifact_name, type).
# These are the stores CLAUDE.md and the corrections register treat as canonical;
# versioning them is what lets a figure or a verdict cite a specific data version
# rather than "the CSV as it was that night".
SNAPSHOT_SET = [
    ("data/all_runs_inventory.csv", "all_runs_inventory", "dataset"),
    ("data/failure_modes_by_run_classified.csv", "failure_modes_classified", "dataset"),
    ("data/failure_modes_by_run.json", "failure_modes_raw", "dataset"),
    ("data/research_corpus_index.json", "research_corpus_index", "dataset"),
]


def _wandb():
    """Import wandb with a clear message if the wrong interpreter is in use."""
    try:
        import wandb
    except ModuleNotFoundError:
        sys.exit(
            "wb: no wandb in this interpreter (%s).\n"
            "wb: run it through the wrapper instead:  scripts/wb --py analysis/wb.py ...\n"
            % sys.executable
        )
    return wandb


def _git_sha() -> str:
    """Short HEAD sha, or 'unknown'. Recorded on every run so a result is traceable."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _git_dirty() -> bool:
    """True if the tree has uncommitted changes. A dirty run is not reproducible."""
    try:
        out = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(REPO), "status", "--porcelain"],
            capture_output=True, text=True, timeout=15,
        )
        return bool(out.stdout.strip())
    except Exception:
        return False


def _sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve(p: str) -> pathlib.Path:
    """Accept a repo-relative or absolute path; return an existing absolute path."""
    path = pathlib.Path(p)
    if not path.is_absolute():
        path = REPO / path
    path = path.resolve()
    if not path.exists():
        sys.exit(f"wb: no such file: {path}")
    return path


@contextlib.contextmanager
def run(job_type: str, tags=None, group=None, name=None, config=None, notes=None):
    """
    Start a W&B run with this project's conventions enforced.

    job_type and tags are REQUIRED in spirit: only 18 of 106 existing runs carry
    job_type or group (measured 2026-08-20), which is why the older runs cannot be
    filtered or grouped in the UI. Every new run made through here gets both, plus
    the git sha and dirty flag, so a run always answers "which code produced this".
    """
    wandb = _wandb()
    cfg = dict(config or {})
    cfg.setdefault("git_sha", _git_sha())
    cfg.setdefault("git_dirty", _git_dirty())

    r = wandb.init(
        entity=ENTITY,
        project=PROJECT,
        job_type=job_type,
        group=group,
        name=name,
        tags=list(tags or []),
        config=cfg,
        notes=notes,
        reinit=True,
    )
    try:
        yield r
    finally:
        r.finish()


def put_artifact(r, path, name, art_type="dataset", description=None, metadata=None):
    """Attach a file to a run as a versioned artifact, with its sha256 recorded."""
    wandb = _wandb()
    src = _resolve(path)
    meta = dict(metadata or {})
    meta.update({
        "sha256": _sha256(src),
        "bytes": src.stat().st_size,
        "repo_path": str(src.relative_to(REPO)) if str(src).startswith(str(REPO)) else str(src),
        "git_sha": _git_sha(),
    })
    art = wandb.Artifact(
        name=name, type=art_type,
        description=description or f"{src.name} from can-it-ford @ {meta['git_sha']}",
        metadata=meta,
    )
    art.add_file(str(src), name=src.name)
    r.log_artifact(art)
    return art


def csv_table(path, max_rows=10000):
    """Read a CSV into a wandb.Table using stdlib csv. Numeric cells become floats."""
    wandb = _wandb()
    src = _resolve(path)
    with open(src, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        sys.exit(f"wb: {src} is empty")
    header, body = rows[0], rows[1:max_rows + 1]

    def cast(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return v

    return wandb.Table(columns=header, data=[[cast(c) for c in row] for row in body])


# ------------------------------------------------------------------ subcommands

def cmd_doctor(args):
    wandb = _wandb()
    print(f"interpreter : {sys.executable}")
    print(f"wandb       : {wandb.__version__}")
    print(f"repo        : {REPO}")
    print(f"git         : {_git_sha()}{' (DIRTY)' if _git_dirty() else ''}")
    print(f"target      : {ENTITY}/{PROJECT}")
    api = wandb.Api()
    print(f"viewer      : {api.viewer.username}")
    runs = api.runs(f"{ENTITY}/{PROJECT}", per_page=500)
    allr = list(runs)
    print(f"runs        : {len(allr)}")
    print(f"  with tags     : {sum(1 for x in allr if x.tags)}")
    print(f"  with group    : {sum(1 for x in allr if x.group)}")
    print(f"  with job_type : {sum(1 for x in allr if x.job_type)}")
    user_arts = 0
    for t in api.artifact_types(f"{ENTITY}/{PROJECT}"):
        if t.name in ("wandb-history", "run_table"):
            continue
        n = len(list(t.collections()))
        user_arts += n
        print(f"  artifact type {t.name}: {n} collection(s)")
    print(f"user artifacts : {user_arts}")
    return 0


def cmd_runs(args):
    wandb = _wandb()
    api = wandb.Api()
    rs = api.runs(f"{ENTITY}/{PROJECT}", order="-created_at", per_page=args.limit)
    for i, r in enumerate(rs):
        if i >= args.limit:
            break
        if args.tag and args.tag not in r.tags:
            continue
        print(f"{r.created_at}  {r.name:26s} job={r.job_type or '-':16s} "
              f"group={r.group or '-':24s} tags={','.join(r.tags) or '-'}")
        print(f"    {r.url}")
    return 0


def _collection_versions(collection):
    """
    Versions of an artifact collection, across wandb API generations.

    Measured 2026-08-20 on wandb 0.28.2: ArtifactCollection exposes .artifacts()
    and has NO .versions(); older and newer releases have used .versions(). Calling
    the wrong one raises AttributeError at list time rather than at import, so the
    failure only shows up once someone actually lists artifacts.
    """
    for attr in ("artifacts", "versions"):
        fn = getattr(collection, attr, None)
        if callable(fn):
            return fn()
    return []


def cmd_artifact_list(args):
    wandb = _wandb()
    api = wandb.Api()
    found = False
    for t in api.artifact_types(f"{ENTITY}/{PROJECT}"):
        if t.name in ("wandb-history", "run_table") and not args.all:
            continue
        for c in t.collections():
            found = True
            vers = list(_collection_versions(c))
            latest = vers[0].version if vers else "-"
            print(f"{t.name:14s} {c.name:34s} versions={len(vers):3d} latest={latest}")
    if not found:
        print("no user artifacts yet. create one with:  artifact-put or snapshot")
    return 0


def cmd_artifact_put(args):
    with run(job_type="artifact-publish",
             tags=["artifact", args.type],
             name=f"publish-{args.name}",
             notes=args.desc) as r:
        art = put_artifact(r, args.path, args.name, args.type, description=args.desc)
        print(f"logged {args.name} ({args.type}) from {args.path}")
        print(f"  sha256 {art.metadata['sha256'][:16]}...  {art.metadata['bytes']} bytes")
        print(f"  run: {r.url}")
    return 0


def cmd_artifact_get(args):
    wandb = _wandb()
    api = wandb.Api()
    ref = args.name if ":" in args.name else f"{args.name}:latest"
    art = api.artifact(f"{ENTITY}/{PROJECT}/{ref}")
    out = art.download(root=args.out) if args.out else art.download()
    print(f"downloaded {ref} -> {out}")
    print(f"  metadata: {json.dumps(art.metadata, indent=2)[:600]}")
    return 0


def cmd_log_csv(args):
    with run(job_type="table-publish", tags=["table"], name=f"table-{args.name}") as r:
        tbl = csv_table(args.path)
        r.log({args.name: tbl})
        print(f"logged table '{args.name}' ({len(tbl.data)} rows) from {args.path}")
        print(f"  run: {r.url}")
    return 0


def cmd_snapshot(args):
    """Version every canonical store in one run: the closest thing to a release."""
    present = [(p, n, t) for (p, n, t) in SNAPSHOT_SET if (REPO / p).exists()]
    missing = [p for (p, _, _) in SNAPSHOT_SET if not (REPO / p).exists()]
    sha = _git_sha()
    dirty = _git_dirty()
    if dirty:
        print("WARNING: working tree is DIRTY. This snapshot is not reproducible "
              "from the recorded sha alone.", file=sys.stderr)
    with run(job_type="snapshot",
             group=f"snapshot-{sha}",
             name=f"snapshot-{sha}",
             tags=["snapshot", "canonical-data"],
             notes=args.desc or f"canonical data snapshot at {sha}") as r:
        for path, name, art_type in present:
            put_artifact(r, path, name, art_type,
                         description=f"canonical {name} @ {sha}")
            print(f"  versioned {name:28s} <- {path}")
        r.summary.update({"files_versioned": len(present),
                          "files_missing": len(missing),
                          "git_dirty": dirty})
        print(f"\nsnapshot complete: {len(present)} file(s) versioned at {sha}")
        if missing:
            print(f"  NOT FOUND, skipped: {', '.join(missing)}")
        print(f"  run: {r.url}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wb", description="can-it-ford W&B helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="report account, run and artifact state")

    p = sub.add_parser("runs", help="list recent runs")
    p.add_argument("--limit", type=int, default=15)
    p.add_argument("--tag", default=None)

    p = sub.add_parser("artifact-list", help="list artifact collections")
    p.add_argument("--all", action="store_true", help="include wandb-internal types")

    p = sub.add_parser("artifact-put", help="version a file as an artifact")
    p.add_argument("--path", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--type", default="dataset")
    p.add_argument("--desc", default=None)

    p = sub.add_parser("artifact-get", help="download an artifact version")
    p.add_argument("--name", required=True, help="name or name:version")
    p.add_argument("--out", default=None)

    p = sub.add_parser("log-csv", help="publish a CSV as a wandb.Table")
    p.add_argument("--path", required=True)
    p.add_argument("--name", required=True)

    p = sub.add_parser("snapshot", help="version every canonical data store at once")
    p.add_argument("--desc", default=None)

    args = ap.parse_args(argv)
    return {
        "doctor": cmd_doctor,
        "runs": cmd_runs,
        "artifact-list": cmd_artifact_list,
        "artifact-put": cmd_artifact_put,
        "artifact-get": cmd_artifact_get,
        "log-csv": cmd_log_csv,
        "snapshot": cmd_snapshot,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
