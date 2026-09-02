---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - ai/context
  - workflow/automation
---

# Agent Context Automation

## Summary

Claude, Codex, Cursor and other agents maintain this workspace as they work. Durable context, links, decisions and tasks are updated automatically at task closeout, without a separate reminder from the user.

## Details

The shared rulebook is `AGENTS.md`. Tool-specific entry points point back to it:

- Claude loads `CLAUDE.md`.
- Cursor loads `.cursor/rules/context-map.mdc`.
- Codex loads `AGENTS.md`.

The operational workflow is [[70_Resources/Agent_Workflow_Protocol]]: recall/search context, read canonical sources, challenge weak assumptions, act, verify, capture durable context back, and reimport memory when relevant. [[70_Resources/AI_Operating_System]] explains the larger architecture. Use [[70_Resources/AI_Context_Quality_Guide]] for capture quality.

Agents should capture durable context when they learn or change:

- current work, blockers, next steps, or waiting items;
- project facts, repositories, services, environments, or commands;
- architecture, code structure, integrations, risks, or operational notes;
- decisions that should be remembered later;
- important people, terms, resources, meetings, or follow-up tasks.

Agents must not store secrets, credentials, private customer data, throwaway reasoning, or unverified guesses as facts.

If a memory/retrieval layer is available, use it to discover candidate context only. Canonical updates still go into this workspace.

## Where Updates Go

| Context type | Primary note |
| --- | --- |
| Current work and blockers | [[10_Project/Current_Focus]] |
| Tasks and follow-up | [[60_Tasks/Task_Log]] |
| Project summary and sources of truth | [[10_Project/Project_Brief]] |
| Architecture and tools | [[30_Tech/Tech_Map]] |
| Repositories and commands | [[30_Tech/Codebase_Map]] |
| Decisions | [[40_Decisions/Decision_Log]] plus a decision note |
| Terms | [[01_Index/Glossary]] |
| People | [[01_Index/People]] |
| Meetings | [[50_Meetings/Meeting_Log]] |
| Procedures / runbooks | `70_Resources/Procedure_*.md` |

## Links

- [[01_Index/AI_Context]]
- [[01_Index/Project_Map]]
- [[30_Tech/Tech_Map]]
- [[30_Tech/Codebase_Map]]
- [[70_Resources/Agent_Workflow_Protocol]]
- [[70_Resources/AI_Operating_System]]
- [[70_Resources/AI_Context_Quality_Guide]]
