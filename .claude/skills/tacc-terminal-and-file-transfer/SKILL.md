---
name: tacc-terminal-and-file-transfer
description: "Troubleshooting for SSH, scp, rsync, and terminal errors moving files between MacBook, Vista, and LS6 for Can It Ford. Covers path errors, permission errors, MFA/token issues, and a general failure decision tree."
---

## Safe Resume Protocol
See CLAUDE Code Power Features memory entry for the full text. Applies whenever a session resumes via --continue, --resume, /resume, or a reattached tmux pane. Restate what was mid-task, check git status and running processes, only proceed once confirmed clean.

## Verify background task IDs before trusting them
Task IDs are auto-generated and can coincidentally look meaningful. A stray `find /` search backgrounded tonight got the ID bgv3dygjd, which reads as "v3" if you don't check the actual command behind it. Before treating any background task status as evidence about a real job (a sweep, a training run), pull the literal command line that task is running, don't infer from the label.

## Login node search limits
Two full-filesystem `find` searches ran on Vista's shared login node for 4.5 and 2 hours tonight before being noticed. Long searches belong on a compute node via idev, not the login node, both for your own account's standing with TACC and because it's shared with every other user. Before starting any recursive filesystem search, ask whether it needs to run on login1 at all, or whether `idev` first is one extra step that avoids the risk entirely.

# TACC Terminal and File Transfer Troubleshooting

## Purpose
This is the "something in the terminal broke" skill — path errors, `scp` failures, permission denials, MFA/token timing, and the mechanics of getting a file from Point A to Point B across MacBook, Vista, and LS6. Companion to `geoelements-tech-reference` (account info, high-level paths) and `mpm-render-pipeline` (what to actually run once files are in place). Trigger on any pasted terminal error, not just when she explicitly asks for help.

## The most common error, live-confirmed: placeholder paths pasted literally

**`scp: stat local "/path/to/X": No such file or directory`** almost always means a placeholder path from an instruction (`/path/to/file.py`, `<PWD_PATH>`, etc.) got copy-pasted as if it were real. This is not a permissions or connectivity problem — it's a literal string that was never meant to be typed verbatim. Fix: find the actual file first.

```
ls -la ~/Downloads/<filename>
find ~ -name "<filename>" 2>/dev/null
```
Then use whatever real path that returns, not the placeholder.

## Core file transfer patterns

**MacBook to Vista, single file:**
```
scp ~/Downloads/file.py jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/mpm-engine/
```

**MacBook to LS6, single file:**
```
scp ~/Downloads/file.py jcerrell0629@ls6.tacc.utexas.edu:$SCRATCH/
```

**Vista to MacBook (pulling a result, e.g. a rendered video):**
```
scp jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/mpm-engine/output.mp4 ~/Desktop/
```

**Whole directory, not just one file — add `-r`:**
```
scp -r ~/Downloads/some_folder jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/mpm-engine/
```

**Better for repeated syncs of a working directory (only transfers what changed):**
```
rsync -avz ~/can-it-ford/ jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/
```

**Preferred long-term pattern over ad-hoc scp:** if the file belongs in the git repo, `cp` it into `~/can-it-ford/` locally first, commit/push, then `git pull` on Vista — keeps the file version-controlled instead of a loose untracked copy. Use plain `scp` only for one-off artifacts (renders, data files) that don't belong in git.

## Error decision tree

| Error text contains | Likely cause | First move |
|---|---|---|
| `stat local ... No such file or directory` | Local path is wrong/placeholder | `ls`/`find` locally first, don't touch the remote side |
| `No such file or directory` (remote side, after a successful connection) | Remote path is wrong, or the target directory doesn't exist yet | `ssh` in separately and `ls`/`mkdir -p` the target directory first |
| `Permission denied (publickey,password)` or hangs before a password prompt | Wrong username, wrong host, or a key-based auth attempt failing silently before it offers a password | Confirm `jcerrell0629@vista.tacc.utexas.edu` exactly; try plain `ssh` first to isolate from `scp` |
| Prompts for `Password:` but never reaches `TACC Token:` | Allocation/membership issue, not a password problem | Don't retry the password — this needs TACC/Krishna, not a typo fix |
| `Permission denied` on a path under `/work/10386/lsmith9003/...` (Luke's shared space) | You don't have write access to someone else's directory, expected | Don't debug — Slack Luke Smith |
| Connection just hangs, no prompt at all | VPN/network issue, or TACC-side outage | Check TACC systems status page; try again in a few minutes before assuming your command is wrong |
| `ssh: connect to host ... port 22: Operation timed out` | Off-campus network blocking the port, or hostname typo | Double-check the hostname spelling first (`vista.tacc.utexas.edu` vs `ls6.tacc.utexas.edu`) before assuming a network block |

## General "something broke, which bucket" triage (useful beyond file transfer)

When something fails and it's not obviously one of the above, classify before debugging blind:
1. **Solver/sim issue** (NaN, explosion, particles vanish) — check timestep/substep stability first, then grid resolution, before touching material parameters.
2. **Environment issue** (import errors, silent CPU fallback, container path errors) — check `torch.cuda.is_available()`, check container path exports, before assuming the physics code is wrong.
3. **Geometry/mesh issue** (rigid body missing, wrong scale/position) — check units (meters vs. some other scale) and origin/pivot before assuming the physics coupling is wrong.
4. **Data-handoff issue** (one tool's output doesn't feed cleanly into another) — check array shapes/dtypes at the exact handoff point first; this is the most likely place a bug hides when connecting two tools nobody has published a bridge between before.
5. **Silent-wrong-but-runs issue** (it completes, produces a number, but the number is physically implausible) — re-derive the parameter from source or a citation rather than trusting whatever the code currently has. A sim finishing without an error is not evidence it's correct.

## Standing rules
- **She runs; I diagnose.** Never claim to have run a command on her machines — give the exact command, what it does, and what success looks like.
- **15-minute stuck rule:** Cristian first for anything not resolved by this skill, then group Slack.
- **Permission errors on Luke's shared paths → Slack Luke, don't debug blind.**
- **Known trap, repeat offender:** path errors are the single most common failure category in this project. Always verify the literal path exists (`ls`) before assuming a deeper problem.