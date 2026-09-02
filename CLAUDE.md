# CLAUDE.md

This workspace is a markdown vault used as the durable project context for Лабораторные работы по 1С.

## Recall gate (hard rule — read this first)

Before ANY claim about people, meetings, past decisions or project state — **including advice, predictions, assessments and "just my take"** — search the memory layer (if configured) and open the canonical note (`01_Index/People.md`, `50_Meetings/*`, `40_Decisions/Decision_Log.md`, `10_Project/Current_Focus.md`). A prediction about a real person is a factual claim, not an opinion. Treat conversation context as stale by default. Self-check before sending: if the answer names a real person and no note was opened this turn — stop and recall first. Advisory/strategic conversations are NOT exempt, and they must end with durable conclusions captured into the workspace notes, not only when asked.

The same gate applies beyond people: project facts live in code/notes (open them, don't recite the conversation), and **time-sensitive external facts** (versions, prices, exchange rates, dates, "how X currently works") are NOT in this workspace at all — verify them via web search when they matter, or explicitly label them as model memory that may be outdated. A confident stale fact is worse than an honest "need to check".

Read `AGENTS.md` first, then start with:

- `01_Index/AI_Context.md`
- `10_Project/Current_Focus.md`
- `10_Project/Project_Brief.md`
- `30_Tech/Tech_Map.md`
- `30_Tech/Codebase_Map.md`
- `40_Decisions/Decision_Log.md`

When you discover durable context, follow the Autonomous Context Capture rules in `AGENTS.md` before finishing:

- update the relevant note;
- keep wikilinks connected;
- update index notes for important new notes.

For AI workflow, memory, agent coordination, or user-specific collaboration style, also read:

- `70_Resources/Agent_Workflow_Protocol.md`
- `70_Resources/AI_Operating_System.md`
- `70_Resources/AI_Context_Quality_Guide.md`
- `01_Index/User_Working_Profile.md`

For repeated work, prefer the procedure notes:

- `70_Resources/Procedure_Deploy_Template.md`
- `70_Resources/Procedure_Frontend_Visual_QA.md`
- `70_Resources/Procedure_Bug_Diagnosis_Loop.md`
- `70_Resources/Procedure_Meeting_Capture.md`
- `70_Resources/Procedure_Multi_Agent_Review.md` (for important decisions/deploys/methodology)

If a semantic memory MCP server is available, use it for semantic recall only:

- search memory to find candidate context;
- open the cited workspace markdown note before acting;
- treat markdown/code/primary documents as higher authority than memory snippets;
- prefer read-only recall tools;
- do not use mutating memory tools unless the task explicitly requires memory maintenance and the workspace markdown source has already been updated.

Default loop: recall -> read canonical notes/code -> challenge -> act -> verify -> capture -> reimport changed workspace directories into the memory library when memory freshness matters.

For substantial tasks, use the mandatory preflight from `70_Resources/Agent_Workflow_Protocol.md`: context, skill/procedure, challenge checkpoint, verification target. Before final answer, run the protocol self-audit: context used, skill/procedure used, verification, capture, memory sync, residual risk.

Do not agree automatically (non-yes-man rule): when a request conflicts with code, accepted decisions, security, or a simpler safer alternative, push back once with concrete reasons, then follow the user's explicit decision. Details: "Non-conformism" in `AGENTS.md` and the Non-Yes-Man Rule in `70_Resources/Agent_Workflow_Protocol.md`.

Installation trigger: if the user asks to install or set up this workspace (any language, any phrasing — "set it up", "install everything"), you are the installer: follow `TEMPLATE_SETUP.md` end-to-end in full-install mode, ask the user only for values only they know, and finish with a green readiness check and an honest report.

System maintenance boundary: the OS layer of this workspace (entry points, `70_Resources/Agent_Workflow_Protocol.md` and the other AI OS resource docs, the skill router, the eval suite, everything in `tools/`, `.mcp.json`) is a stable, versioned system — complete and self-sufficient. Use the system and keep project notes updated per the capture rules — but do not rewrite, extend or "improve" the OS files themselves, and do not install additional system-level tools. If a system change ever seems needed, record it as a proposal in `60_Tasks/System_Proposals.md` (generic wording, no project details) and keep working within the current system; OS updates arrive only as new template versions. The user can send proposals to the template author via `tools/make_feedback_report.ps1`.
