---
type: tech
status: draft
updated: 2026-09-02
tags:
  - tech/map
---

# Tech Map

Technical map of Лабораторные работы по 1С: architecture, components, integrations, environments, tools. Implemented reality lives in [[30_Tech/Codebase_Map]]; this note holds the architecture-level picture.

## Architecture

- Working architecture (e.g. API + database + SPA + background workers).
- Mark clearly what is confirmed versus what is a draft to validate with the team.

## Main components

- Component 1 — purpose.
- Component 2 — ...

## Integrations

- External API 1: access model (sandbox/read-only/production), status.
- Record what each integration can and cannot provide — API facts versus business methodology.

## Environments

- Local: how to run it.
- Staging/Prod: where they live, who has access.

## Tools

- IDE / AI agents: which are used in this project.
- Documentation: this workspace.
- Skills: bundled set in `template-skills/` (see [[70_Resources/Agent_Skills_Roadmap]] and the manifest).
- Agent workflow: [[70_Resources/Agent_Workflow_Protocol]]; auto-capture: [[70_Resources/Agent_Context_Automation]].
- Memory layer (optional): [[70_Resources/MGI_Mind_Local_Setup_Template]].
- Native app (optional, Windows): `tools/control-center-app/` — a control panel over the same notes/checks; prebuilt binary bundled, see [[30_Tech/Codebase_Map]] and `TEMPLATE_SETUP.md`.

## Links

- [[30_Tech/Codebase_Map]]
- [[10_Project/Project_Brief]]
- [[20_Domain/Domain_Map]]
- [[40_Decisions/Decision_Log]]
