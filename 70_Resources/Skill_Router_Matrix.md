---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - ai/context
  - ai/skills
  - workflow/protocol
---

# Skill Router Matrix

## Summary

This matrix exists so agents do not pick skills by taste. For each task type it says: which context to open, which skill/procedure to use, where to challenge a bad decision, and how to verify the result.

Rule: if the user explicitly names a skill, the agent must read its `SKILL.md` and apply it. If no skill is named, the agent routes by this matrix.

## Matrix

| Situation | Context | Skill / procedure | Challenge checkpoint | Verification target |
| --- | --- | --- | --- | --- |
| Broad or old context | [[01_Index/AI_Context]], [[10_Project/Current_Focus]] | memory search as navigation, then the canonical note | Never answer from a memory snippet alone | A workspace note or code was opened |
| Questions about a person: reaction, assessment, prediction, relationships (including "just advice") | [[01_Index/People]], `50_Meetings/*`, [[01_Index/User_Working_Profile]] | Memory search -> canonical notes; this is a fact task, not an opinion | Never characterize a real person from conversation context or priors alone | The answer is grounded in a note, or honestly states the notes hold no data |
| AI workflow, memory, agents, tool choice | [[70_Resources/Agent_Workflow_Protocol]], [[70_Resources/AI_Operating_System]], [[01_Index/User_Working_Profile]] | `find-skills`; `grill-me` only on explicit user request (it is invocation-gated — apply the protocol challenge checkpoint instead) | Do not add a fashionable tool without a role and a test | Decision recorded in the workspace |
| Project restriction / freeze / no-edit mode | [[10_Project/Current_Focus]] (Restrictions section) | No code-edit skill unless the user explicitly unlocks | Do not start code/UI changes during a declared freeze | Review-only plan or workspace-only update |
| UI/UX, dashboards, frontend polish | [[01_Index/User_Working_Profile]], [[30_Tech/Codebase_Map]] | `frontend-design`, `humanizer` for all user-facing copy, [[70_Resources/Procedure_Frontend_Visual_QA]]; consider install-only `ui-ux-pro-max` (see manifest) | Do not ship generic AI-looking UI, slogans, invented labels, or unnecessary mixed-language copy | Desktop/mobile visual QA, build/tests; copy was reviewed in its real UI container |
| React/frontend performance or structure | [[30_Tech/Codebase_Map]] | install-only `vercel-react-best-practices` (see manifest), `playwright` where useful | Do not fix visuals at the cost of state/accessibility | Build, focused UI checks |
| Bug, crash, wrong numbers, slowness | Relevant code/note | `diagnosing-bugs`, [[70_Resources/Procedure_Bug_Diagnosis_Loop]] | Reproduce/isolate first, then fix | Failing check becomes passing |
| Backend API, async, DB | [[30_Tech/Codebase_Map]] | `fastapi-python` (or your stack equivalent), `tdd` when behavior is testable | Do not break contracts/APIs silently | Tests / API smoke |
| Deploy | [[70_Resources/Procedure_Deploy_Template]] | Procedure only | Secrets/auth/public-exposure gate before push | Build/tests/smoke/security checklist |
| External data sync / integrations | [[30_Tech/Codebase_Map]], integration procedure note (create one after first real sync) | Procedure + `diagnosing-bugs` on mismatch | Do not treat an API sum as methodological truth | Connectivity/sync/unit sanity checks |
| Domain methodology, terms, disputed business logic | [[20_Domain/Domain_Map]], [[01_Index/Glossary]], [[10_Project/Project_Brief]] | `domain-modeling` | Separate fact, hypothesis, decision | Domain note / glossary updated |
| PRD or requirements packaging | Current conversation + project notes | `to-prd` | Do not turn an immature idea into a "final spec" | PRD linked from the workspace |
| Issue decomposition | PRD / roadmap / task note | `to-issues` | Issues must be independently shippable | Task_Log / tracker references |
| Handoff to another agent/tool | Current task notes and changed files | `handoff` | Do not pass unverified guesses as facts | Handoff includes status, blockers, commands |
| Obsidian markdown notes | Target note + related index notes | `obsidian-markdown` | Preserve wikilinks/properties; do not use generic Markdown habits that break Obsidian | Note renders in Obsidian, frontmatter valid, wikilinks resolve |
| Obsidian canvas / knowledge maps | `*.canvas` file | `json-canvas` | Validate IDs and edge references | JSON parse + no dangling edges |
| Source-code structure exploration | Product repo | `graphify`; optional after a pilot: `codebase-memory-mcp` (see manifest) | Code index is navigation, not truth; pilot before wiring into agents | Structural index created/used |
| External docs, PDFs, sheets | Attached file / source document | document/PDF/spreadsheet skills as applicable | Do not summarize high-stakes docs from memory | Render/parse verification |
| Code review or architecture review | Code + tests + current behavior | Review stance; for important decisions [[70_Resources/Procedure_Multi_Agent_Review]] | Findings first, no cosmetic nitpicking; Reviewer runs in a fresh session | File/line findings and test gaps |
| Secrets, tokens, customer data, public demo | [[10_Project/Current_Focus]], [[70_Resources/AI_Context_Quality_Guide]] | No special skill; the security gate is mandatory | Refuse to store/expose secrets | Secret scan / config check |
| External text for the client/company | [[01_Index/People]], [[01_Index/User_Working_Profile]] | No special skill unless document generation | Respect the internal/external role boundary | Role boundary checked |
| New skill discovery/install | [[70_Resources/Agent_Skills_Roadmap]] | `find-skills`; install only after verification | Do not install skills "just because" | Skill added here with trigger and verification |
| Voice notes, meetings, transcripts | [[50_Meetings/Meeting_Log]] | [[70_Resources/Procedure_Meeting_Capture]] | Raw STT stays out of memory-imported dirs; noisy names are hypotheses | Meeting note + [[60_Tasks/Task_Log]] updated, raw stays in archive |
| AI OS maintenance: health, readiness, memory sync | [[70_Resources/MGI_Mind_Local_Setup_Template]] | `tools/check_agent_health.ps1`, `tools/check_ai_os_readiness.ps1`, `tools/sync_mgimind.ps1` | Green checks do not prove agent behavior; run the eval suite for that | Exit code 0, freshness OK, entry in `.local/*-check.log` |
| Changing the AI OS itself (protocol, router, scripts, evals, entry points) | System Maintenance Boundary in `AGENTS.md` | None — out of scope for project agents | The OS layer is a stable versioned system; do not edit or extend it | Proposal recorded in [[60_Tasks/System_Proposals]] instead of an edit |

## Enforcement Rules

- For any code/UI/deploy/domain/memory task, the agent must state or internally satisfy: context, skill/procedure, challenge checkpoint, verification target.
- If a task matches multiple rows, choose the minimal set that covers the risk.
- A newly installed skill is incomplete until this file says when to use it.
- A procedure note beats a generic skill for repeated local workflows.
- Memory/graph/runtime layers never replace the workspace markdown as source of truth.
- Run `humanizer` on interface, installer, notification, help, and external-facing copy. Use direct labels and the user's language; preserve concrete instructions and limitations.

## Links

- [[70_Resources/Agent_Workflow_Protocol]]
- [[70_Resources/Agent_Skills_Roadmap]]
- [[70_Resources/AI_Context_Quality_Guide]]
- [[70_Resources/AI_OS_Eval_Prompt_Suite]]
