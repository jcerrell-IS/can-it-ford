# Can It Ford — Session Notes Manifest
Last organized: July 13, 2026

This folder holds session notes, audits, and past playbooks moved out of the repo
root so the root stays clean. Everything here is historical/reference. The live,
authoritative file remains `../../CLAUDE.md` at the repo root.

## Active reference files (this folder)

- **2026-07-12_session_audit_and_panel_tasks.md**
  Prior session's 6-pane audit. Historical record of what was found July 12.

- **2026-07-13_bug_triage_and_panel_execution_plan.md**
  Original July 13 triage plan, before the domain-widening finding. Superseded in
  content by CLAUDE.md's Known Dead Ends section, kept for the reasoning trail.

- **2026-07-13_pane0.7_diagnostic_and_gate_status.md**
  Diagnostic findings 1-5, including confirmation of the real `simulation/`
  subdirectory path. Content now folded into CLAUDE.md.

- **cross_session_verification_july13.md**
  Cross-checks between parallel sessions on July 13.

- **full_deployment_playbook_july13.md**
  Deployment steps for pushing corrected files everywhere.

- **deployment_and_troubleshooting_runbook.md**
  Deployment plus troubleshooting runbook. (Was loose at repo root with the same
  July-13 signature as the other session notes; not in the original organize
  script's move list, added here so it did not get stranded.)

- **claude-code-setup-for-debugging.md**
  Setup notes for running Claude Code sessions on this project.

- **master_outstanding_tasks_audit_july13.md**
  Full audit of tasks prescribed but never confirmed done. Check this before
  assuming any prior instruction was completed.

- **full_equip_pass_july13.md**
  Contains the Known Dead Ends list, Coupled Variables rule, and reusable kickoff
  prompt. Most of this is now merged into CLAUDE.md directly.

## Needs a human decision

- **bug-triage-protocol-SKILL_UNMERGED_VARIANT.md**
  A SECOND, different-scoped version of the bug-triage skill. It is NOT the
  installed skill. Do not assume it is stale.
  - Installed skill: `~/.claude/skills/bug-triage-protocol/SKILL.md` (10490 bytes,
    modified 04:21). Project-tuned: "Where this runs", the
    CONTEXT/STANCE/SCOPE/DELIVERABLE skeleton, Vista/LS6/MacBook specifics. This is
    the version currently registered and firing.
  - This variant: 8851 bytes, modified 09:43 (later in the day). Deliberately more
    universal: description says "applies to any coding/debugging problem," Section 0
    is a universal pre-flight and Section 0b quarantines the Can-It-Ford traps.
  - They diverge in scope, not just age. Decide which framing you want (or merge the
    universal Section 0 into the installed one) before overwriting anything. Nothing
    here has been auto-applied to the installed skill.

## Not moved (intentionally left at repo root)

Stable project files, not session notes: README.md, CLAUDE.md, PROVISIONAL_STATUS.md,
PROJECT_FILE_MAP.md, REBUILD_REFERENCE.md, SESSION_STATE.md, paper_draft.md, and the
two older SKILL_*.md references (geoelements, mpm-render-pipeline). `files.zip` (the
bundle these docs shipped in) was also left at root.

## Files the original organize script expected but that were absent

`CLAUDE_md_FINAL_july13.md` and `CLAUDE_md_corrected_july13.md` were not at the repo
root. CLAUDE.md was already in place, so there was nothing to archive or diff and no
`superseded/` folder was created.

## How to use this folder

If Claude Code is about to re-test something, check
`master_outstanding_tasks_audit_july13.md` and CLAUDE.md's Known Dead Ends section
first. If it is about to build a plan from scratch, `full_equip_pass_july13.md` has a
ready kickoff prompt.
