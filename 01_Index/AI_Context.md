---
type: index
status: active
updated: YYYY-MM-DD
tags:
  - ai/context
  - index/core
---

# AI Context

This note is the main entry point for Claude, Codex, Cursor and other assistants.

## How to read context

1. Read [[10_Project/Current_Focus]].
2. Check [[10_Project/Project_Brief]].
3. Check [[30_Tech/Tech_Map]] and [[30_Tech/Codebase_Map]].
4. Check [[40_Decisions/Decision_Log]].
5. If the task is domain-related, read [[20_Domain/Domain_Map]] and [[01_Index/Glossary]].

## Current short context

Keep this list short (10-20 dated bullets max). Newest facts on top of their topic; prune superseded lines during weekly maintenance.

- Project: Лабораторные работы по 1С for n/a / n/a. Example: "MVP of an internal analytics tool; scope agreed on YYYY-MM-DD".
- User: Денис operates the AI agents in this workspace; working preferences: [[01_Index/User_Working_Profile]].
- The main goal of this workspace: find context fast and keep a connected knowledge graph.
- YYYY-MM-DD: the workspace runs as a layered AI operating system: this vault is the canonical source of truth, a semantic memory index is an optional retrieval layer, agents follow recall -> read -> challenge -> act -> verify -> capture. Shared protocol: [[70_Resources/Agent_Workflow_Protocol]]. Memory runbook: [[70_Resources/MGI_Mind_Local_Setup_Template]].
- Enforcement baseline: [[70_Resources/Skill_Router_Matrix]] routes skills/procedures, [[70_Resources/AI_OS_Eval_Prompt_Suite]] tests agent behavior, `tools/check_agent_health.ps1` and `tools/check_ai_os_readiness.ps1` verify the workspace itself.
- Active restrictions: record here any freeze/no-edit windows or approval gates (see the Restrictions section of [[10_Project/Current_Focus]]).
- Standing restriction: the AI OS layer (entry points, protocol, router, evals, `tools/`) is a stable, versioned system — use it and capture project context, but do not modify the system itself; ideas go to [[60_Tasks/System_Proposals]] (see "System Maintenance Boundary" in `AGENTS.md`).

## Mandatory sources

- [[10_Project/Project_Brief]]
- [[10_Project/Current_Focus]]
- [[10_Project/Roadmap]]
- [[01_Index/Project_Map]]
- [[20_Domain/Domain_Map]]
- [[30_Tech/Tech_Map]]
- [[30_Tech/Codebase_Map]]
- [[40_Decisions/Decision_Log]]
- [[60_Tasks/Task_Log]]
- [[70_Resources/Agent_Workflow_Protocol]]
- [[70_Resources/Agent_Context_Automation]]
- [[70_Resources/AI_Operating_System]]
- [[70_Resources/AI_Context_Quality_Guide]]
- [[70_Resources/Skill_Router_Matrix]]
- [[70_Resources/AI_OS_Eval_Prompt_Suite]]
- [[70_Resources/Agent_Skills_Roadmap]]
- [[70_Resources/MGI_Mind_Local_Setup_Template]]
- [[70_Resources/Procedure_Bug_Diagnosis_Loop]]
- [[70_Resources/Procedure_Frontend_Visual_QA]]
- [[70_Resources/Procedure_Deploy_Template]]
- [[70_Resources/Procedure_Meeting_Capture]]
- [[70_Resources/Procedure_Multi_Agent_Review]]
- [[70_Resources/Procedure_1C_Lab_Execution]]

## When to update this note

Update it when a new primary context source appears, the project direction changes, or a critically important agreement is made.
