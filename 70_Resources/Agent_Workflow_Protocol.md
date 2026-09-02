---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - ai/context
  - workflow/protocol
  - agent/coordination
---

# Agent Workflow Protocol

## Summary

The single working protocol for Claude, Codex, Cursor and future agents in `D:\1с лабы`.

In short: an agent should not re-read the whole workspace every time. It should quickly decide whether context is needed, find it via the indexes or the memory layer, open the canonical markdown/code/source, do the work, verify the result, and write durable knowledge back.

## Source Of Truth

Order of authority:

1. Live code, tests, the actual state of services, and primary documents.
2. Workspace markdown notes with dates, links and wikilinks.
3. Semantic memory / summaries as a navigation layer.
4. The current chat and guesses.

The memory layer helps find a note; it does not prove a fact by itself.

## Default Context Loading

For a non-trivial task, before planning or changes, read:

- `AGENTS.md`
- [[01_Index/AI_Context]]
- [[10_Project/Current_Focus]]
- [[10_Project/Project_Brief]]
- [[30_Tech/Tech_Map]]
- [[30_Tech/Codebase_Map]]
- [[40_Decisions/Decision_Log]]

If the task is narrow and obvious, read only the relevant minimum — but never ignore the source of truth when there is a risk of conflict.

For tasks about the domain, terms, people or business logic, additionally read:

- [[20_Domain/Domain_Map]]
- [[01_Index/Glossary]]
- [[01_Index/People]]

For tasks about working style, design, risk or AI tool choice, read:

- [[01_Index/User_Working_Profile]]

## Recall Strategy

Use the cheapest sufficient method:

- known file -> open the file directly;
- exact term/path -> text search (`rg`/grep);
- broad/old context -> semantic memory search, then open the cited workspace note;
- code structure -> a structure index tool (e.g. the `graphify` skill), only for source code;
- UI/design -> the relevant design skills plus canonical project notes;
- bug/failure -> [[70_Resources/Procedure_Bug_Diagnosis_Loop]].

## Mandatory Preflight

Before a substantial task, the agent must explicitly determine:

- which canonical context is needed;
- which skill is needed, if the task matches a skill trigger;
- which procedure note is needed, if the task is repeatable;
- why a skill/procedure is NOT needed, if the agent picks none;
- the main risk, weak assumption, or simpler alternative that must be checked.

Minimal formula in the working message:

```text
Context: ...
Skill/procedure: ...
Challenge checkpoint: ...
Verification target: ...
```

For small answers this can be done mentally, but for code/UI/deploy/domain/memory tasks the preflight is mandatory.

## Non-Yes-Man Rule

The agent must not agree automatically.

Before implementing or recommending, check:

- is there a simpler or safer path;
- does the request mix internal and external-facing roles (see [[01_Index/People]]);
- does the request lead to secret leakage, public data exposure, wrong methodology, or pointless UI;
- does the request contradict code, primary documents, or an accepted decision note.

If there is a problem, say it directly once, with the reason and a proposed alternative. If the user then explicitly chooses the risky path, execute the decision within safe boundaries and record the risk.

## Agent Loop

1. **Recall**: find candidate context.
2. **Read**: open canonical notes/code/docs.
3. **Challenge**: check weak spots, conflicts, security, scope.
4. **Act**: make the minimal sufficient change.
5. **Verify**: tests, build, screenshots, API check, JSON validation or another feedback loop.
6. **Capture**: update durable context in the workspace.
7. **Sync memory**: if a memory layer is used, reimport the changed directories.

## End-Of-Task Self-Audit

Before the final answer on a substantial task, check:

- context opened: which canonical notes/code/docs were actually used;
- skill/procedure: what was chosen and why;
- verification: which tests/checks/smoke/validation passed, or why none ran;
- capture: which workspace notes were updated;
- memory sync: is a reimport needed, was it done;
- residual risk: what remains unverified;
- event log: append one line about the task to the Control Center journal — `tools/log_agent_event.ps1 -Agent <name> -Task "..." -Actions ... -Value "..."` (never include secrets).

## End-Of-Task Capture

If the task produced durable context, update the right note:

- current work/blockers -> [[10_Project/Current_Focus]]
- tasks/follow-up -> [[60_Tasks/Task_Log]]
- architecture/code/commands -> [[30_Tech/Codebase_Map]]
- decisions -> [[40_Decisions/Decision_Log]] plus a decision note
- meetings -> [[50_Meetings/Meeting_Log]]
- people/terms -> [[01_Index/People]] / [[01_Index/Glossary]]
- workflow/procedures -> `70_Resources/Procedure_*.md`

New central notes must be added to [[01_Index/Project_Map]].

## Tool-Specific Entry Points

- Codex: `AGENTS.md`
- Claude: `CLAUDE.md`
- Cursor: `.cursor/rules/context-map.mdc`

All three must point to this protocol and to [[70_Resources/Agent_Context_Automation]].

## Procedure Notes

- [[70_Resources/Procedure_Deploy_Template]]
- [[70_Resources/Procedure_Frontend_Visual_QA]]
- [[70_Resources/Procedure_Bug_Diagnosis_Loop]]

## System Maintenance Boundary

The OS layer of this workspace (entry points, this protocol, the router, the eval suite, `tools/`, `.mcp.json`) is a stable, versioned system — complete and self-sufficient. Agents use the system and update project notes per the capture rules; they do not modify the OS layer or install additional system-level tools. A needed system change becomes a proposal in [[60_Tasks/System_Proposals]] (generic wording — that note travels in feedback reports); OS updates arrive only as new template versions.

## Role Boundary

- If the project separates an internal operator from an external representative, external materials are written from the external position; the internal operator is not mentioned without an explicit request. The boundary is defined in [[01_Index/People]].
- Never store secrets, private customer data, credentials, or raw sensitive exports.

## Links

- [[70_Resources/AI_Operating_System]]
- [[70_Resources/Agent_Context_Automation]]
- [[70_Resources/AI_Context_Quality_Guide]]
- [[70_Resources/MGI_Mind_Local_Setup_Template]]
