# AGENTS.md

This repository is a project context workspace (markdown vault) and the shared source of truth for AI agents working on Лабораторные работы по 1С.

## Start Here

Before planning or changing anything, read these files in order:

1. `01_Index/AI_Context.md`
2. `10_Project/Current_Focus.md`
3. `10_Project/Project_Brief.md`
4. `30_Tech/Tech_Map.md`
5. `30_Tech/Codebase_Map.md`
6. `40_Decisions/Decision_Log.md`

If the task is domain-heavy, also read:

- `20_Domain/Domain_Map.md`
- `01_Index/Glossary.md`

If the task is about AI workflow, memory, context capture, agent coordination, tool choice, or how Денис wants agents to work, also read:

- `70_Resources/Agent_Workflow_Protocol.md`
- `70_Resources/AI_Operating_System.md`
- `70_Resources/AI_Context_Quality_Guide.md`
- `01_Index/User_Working_Profile.md`

## Working Rules

- Recall gate: before any claim about people, meetings, past decisions or project state — including advice and predictions — search the memory layer (if configured) and open the canonical note (`01_Index/People.md`, `50_Meetings/*`, `40_Decisions/Decision_Log.md`). A prediction about a real person is a factual claim; treat conversation context as stale by default. Time-sensitive external facts (versions, prices, rates, dates) are not in the workspace — verify via web search when they matter, or label them as possibly-outdated model memory.
- Treat source code and primary documents as higher authority than notes.
- Follow the shared agent loop from `70_Resources/Agent_Workflow_Protocol.md`: recall/search context, read canonical sources, challenge weak assumptions, act, verify, capture durable context, then reimport memory when relevant.
- For substantial tasks, use the mandatory preflight from `70_Resources/Agent_Workflow_Protocol.md`: context, skill/procedure, challenge checkpoint, verification target.
- Before the final answer on a substantial task, run the End-Of-Task Self-Audit from `70_Resources/Agent_Workflow_Protocol.md`: context used, skill/procedure, verification, capture, memory sync, residual risk.
- Treat any memory/retrieval layer (semantic memory index, embedding search, summaries) as a navigation aid, not as the source of truth; verify recalled facts against code, primary docs, or workspace notes.
- If notes conflict with code, mention the conflict and update the relevant note after verification.
- Preserve Obsidian wikilinks when editing notes.
- Keep filenames ASCII and stable where possible.
- Add or update links in index notes when creating important new notes.
- Do not put secrets, tokens, passwords, private customer data, or credentials into notes.
- Keep internal collaboration context separate from external-facing materials. If this project distinguishes an internal operator (Денис) from an external-facing representative, drafts for n/a / n/a must be written from the external position; see `01_Index/People.md` for the boundary.

## Installation

If the user asks to install or set up this workspace (any language, any phrasing), the agent is the installer: follow `TEMPLATE_SETUP.md` end-to-end in full-install mode — interview the user for the values only they know, replace placeholders, seed the notes, install the memory and code-intelligence layers, create the daily check, verify, and report honestly.

## System Maintenance Boundary

The OS layer of this workspace is a **stable, versioned system — complete and self-sufficient**: the entry points (`AGENTS.md`, `CLAUDE.md`, the Cursor rule), the workflow protocol and other AI OS resource docs in `70_Resources/`, the skill router, the eval suite, everything in `tools/`, and `.mcp.json`.

Agents working here USE the system: they read context, do project work, capture durable project knowledge into the notes, sync memory, run checks. They do NOT rewrite, extend or "improve" the OS files themselves, do not change the protocol/router/evals/scripts, and do not install additional system-level tools. If a system change ever seems genuinely needed, record it as a proposal in `60_Tasks/System_Proposals.md` (generic wording, no project details — that file travels in feedback reports) and continue working within the current system — OS updates arrive only as new template versions (see `CHANGELOG.md`) and never touch the project notes. The user can send collected proposals and check results to the template author at any time via `tools/make_feedback_report.ps1`.

## Non-conformism

- Push back when you think the user is wrong, technically or architecturally — do not agree just to keep the conversation moving.
- Do not default to the first idea proposed. If a simpler, safer, or more correct alternative exists, say so before implementing what was asked.
- Argue your position with concrete reasoning: tradeoffs, risks, precedent elsewhere in this project.
- Do not be a yes-man. If code, a design, or a decision is bad, say so plainly instead of softening it.
- If the user does something suboptimal (architecture, security, git operations, secrets handling), point it out even if not asked.
- State disagreement once, clearly, with reasoning — then follow the user's explicit decision. This is about substantive pushback, not about seeking permission for reversible actions.

## Local Skills

- Bundled skills and install recommendations live in `template-skills/SKILLS_MANIFEST.md`; routing rules live in `70_Resources/Skill_Router_Matrix.md`.
- Use `obsidian-markdown` when creating or editing Obsidian `.md` notes; preserve wikilinks, properties/frontmatter, embeds and callouts.
- Use `json-canvas` when creating or editing Obsidian `.canvas` files; validate JSON, unique IDs, and edge references after edits.
- Use `graphify` for source-code structure indexes only; it is not for the note graph.
- Use `tdd` for implementation where tests can define behavior.
- Use `diagnosing-bugs` when something fails, produces wrong numbers, or needs a reproducible debug loop.
- Use `to-prd` and `to-issues` after requirements are agreed and need to become implementation work.
- Use `domain-modeling` for project terminology, business rules, and ambiguous domain concepts.
- Use `humanizer` for every user-facing string in interfaces, installers, notifications, help text, and external documents. Prefer direct labels in the user's language; avoid slogans, metaphors, invented operational terms, and unnecessary mixed-language wording.
- Use `handoff` before passing context to another agent or continuing in another tool.
- Use procedure notes in `70_Resources/Procedure_*.md` for repeated workflows such as deploys, integration checks, visual QA, bug diagnosis, meeting capture, and multi-agent review of important decisions.

## Autonomous Context Capture

At the end of any task, update the workspace without waiting for a separate request when the task produced durable context.

Use `70_Resources/AI_Context_Quality_Guide.md` to decide what is durable enough to capture and where it belongs.

Capture durable context when you learn or change:

- current work, blockers, next steps, or waiting items;
- project facts, repositories, services, environments, or commands;
- architecture, code structure, integration points, or operational risks;
- technical or process decisions that will matter later;
- important terms, people, responsibilities, meetings, or resources;
- new important notes that should be discoverable from index notes.

Do not capture:

- throwaway reasoning, failed guesses, temporary command output, secrets, tokens, credentials, or private customer data;
- facts that are not verified or are likely to change immediately, unless marked clearly as open questions.

For every captured update:

1. Update the right note from the Context Update Protocol.
2. Preserve or add Obsidian wikilinks so the note is connected.
3. Update `01_Index/Project_Map.md` or another index note when a new important note is created.

## Context Update Protocol

When you learn durable project context, update the workspace:

- Current work or blockers: `10_Project/Current_Focus.md`
- Architecture or code structure: `30_Tech/Codebase_Map.md`
- Technical decisions: `40_Decisions/Decision_Log.md` plus a decision note
- Terms and concepts: `01_Index/Glossary.md`
- People and responsibilities: `01_Index/People.md`
- Meetings: `50_Meetings/Meeting_Log.md`
- Repeated workflows or runbooks: `70_Resources/Procedure_*.md`

## Note Conventions

Use this shape for important notes:

```md
---
type: project|domain|tech|decision|meeting|task|person|resource
status: draft|active|stable|deprecated
updated: YYYY-MM-DD
tags:
  - project/context
---

# Title

## Summary

## Details

## Links

- [[01_Index/Project_Map]]
```

## Cursor and Claude

Cursor should load `.cursor/rules/context-map.mdc`.
Claude should load `CLAUDE.md`, which points back to this file.
Codex, Claude, and Cursor should converge on `70_Resources/Agent_Workflow_Protocol.md` for shared operating behavior.
