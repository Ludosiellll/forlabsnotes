---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - workflow/procedure
  - deploy
  - project/context
---

# Procedure: Deploy (Template)

## Summary

Deploy procedure for Лабораторные работы по 1С. Fill it in after your first real deploy and update it after every one — a deploy runbook that does not match reality is worse than none.

Main risk pattern: a publicly reachable environment with real data must never run on default credentials or weak secrets.

## Canonical Context

- Current product state: [[10_Project/Current_Focus]]
- Repository, commands and constraints: [[30_Tech/Codebase_Map]]
- Tasks and blockers: [[60_Tasks/Task_Log]]

## Preconditions (fill in)

- Local product repository: `none yet`.
- Deploy target and remote name: (e.g. a container platform, a VPS, a PaaS remote).
- Expected branch and push command: record the exact command and always verify the current branch before pushing.
- Secrets are set only in the target's secret manager / environment UI, never in git. List the variable NAMES here (never the values).

## Safety Gate

Stop and check before every deploy:

- Is the target public or private?
- If public: are default credentials disabled and secrets strong?
- Any previously exposed key scheduled for rotation?
- Is the repository free of `.env`, secrets, tokens, and raw customer exports?

If any answer is bad, fix security first, deploy second.

## Steps (adapt)

1. Open the product repository; check `git status -sb` and the current branch.
2. Run the available checks before pushing (tests, build).
3. Push to the deploy target with the recorded command.
4. Watch the target's build/startup logs to completion.
5. Smoke-check the deployed app: login works, health endpoint answers, no default credentials, data sources show expected state.

## Verification (minimal successful deploy)

- backend tests passed;
- frontend build passed;
- the target came up without manual intervention;
- public access is protected (strong credentials or private visibility);
- real data is not visible without authorization;
- startup sync/jobs do not crash the boot on upstream errors.

## Common Failures (extend from experience)

- **Missing secrets on the target**: app boots in demo mode or fails auth — fix in the target's settings, not in git.
- **Wrong branch pushed**: always check the current branch against the recorded expectation.
- **Public target + weak password**: a blocker, not a cosmetic issue.
- **Ephemeral disk on the target**: state resets on restart — plan startup sync or persistent storage.

## Capture After Deploy

- [[10_Project/Current_Focus]] — only the current status;
- [[60_Tasks/Task_Log]] — closed/new follow-ups;
- [[30_Tech/Codebase_Map]] — if a command, port, branch, remote, variable or known failure changed.

## Links

- [[70_Resources/Agent_Workflow_Protocol]]
- [[70_Resources/AI_Operating_System]]
