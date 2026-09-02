# Start Here

You just received an AI Project Workspace. This page explains what you have and what to do first.

## The fastest way in (Windows or Linux)

Run `AI_OS_Setup_v0.4.5_x64.exe` on Windows. It is the fast online installer: the first project downloads only missing checksum-verified packages, then every later project reuses the shared cache. Use `AI_OS_Offline_Kit_v0.4.5_x64.exe` when the computer must be installed without internet. The current verified Linux release is 0.4.1: install `AI_OS_Setup_v0.4.1_linux_x86_64.deb` on Ubuntu/Debian, or make the matching 0.4.1 `.AppImage` executable on another modern x86_64 distribution. The branded setup opens on both systems: choose **Начать установку**, enter the project name, your name, a new AI OS workspace folder, the existing code-repository path if one exists, and one factual project summary. Setup skips folders that are already registered or contain files. Keep the local components selected, then choose **Создать среду**.

The installer creates a new workspace, activates bundled skills, installs the checksum-verified local tools, configures project-scoped MCP servers, connects the workspace to one shared supervisor, and reports every completed or pending component. Reopen AI OS to create or switch projects; duplicate display names remain isolated by their full paths. Obsidian, Git and an AI CLI are useful but optional at this stage. It does not collect credentials. Account login and one-time trust prompts remain manual by design.

Removing AI OS Setup does not remove your workspace. The project list offers **Восстановить**, which refreshes tools and automation without replacing project notes; **Убрать из списка** never deletes the project folder.

## Manual fallback (agent-driven)

If you received the ZIP kit instead of the native installer, open an agent session **in this folder** (Claude Code, Codex or Cursor) and paste:

```text
Set up this workspace for me — full install, following TEMPLATE_SETUP.md end-to-end.
Interview me for the values only I know (project name, my name, code repo path),
replace all placeholders, fill the seed notes from my answers, install the memory
and code-intelligence layers, create the daily self-check, run the verification,
and finish with an honest report of what is installed and what (if anything) was skipped.
```

You can talk to the agent in any language — the docs are English, the agent translates as it goes. This fallback is slower because the agent performs the same transparent steps one by one.

Until setup runs, the notes contain `Лабораторные работы по 1С`-style tokens throughout — that is normal; the agent replaces them all during step 1.

**After setup**: you and your agents *use* the workspace — work, capture, check. The system itself (protocol, router, scripts, checks) arrives complete and stays as it is: agents will not modify or "improve" it, and if a system change ever seems needed, it gets recorded as a proposal in `60_Tasks/System_Proposals.md` instead (see "System Maintenance Boundary" in [AGENTS.md](AGENTS.md)). OS updates come only as new template versions.

**Found a bug or rough edge in the system?** Say to your agent: *"make a feedback report"*. It builds one anonymized file (check statuses + recorded proposals — no note content, no paths, no secrets), you review it and send it to the person who gave you this template. Fixes return to everyone as the next template version.

## What this workspace does

- Gives every AI agent (Claude Code, Codex, Cursor, ...) the same entry point, the same rules, and the same map of your project.
- Keeps one canonical source of truth: markdown notes in this folder, linked and dated.
- Makes agents verify before acting, push back on bad ideas, and write durable context back after each task.
- Lets you *check* the system instead of trusting it: health script, readiness script, eval prompts.

## The 10-minute tour

| Read | To learn |
| --- | --- |
| [README.md](README.md) | Architecture and principles |
| [AI_COLLABORATION_101.md](AI_COLLABORATION_101.md) | Ten habits that make agent work effective (start here if agents are new to you) |
| [AGENTS.md](AGENTS.md) | The rules every agent follows here |
| [70_Resources/Agent_Workflow_Protocol.md](70_Resources/Agent_Workflow_Protocol.md) | The shared agent loop: recall -> read -> challenge -> act -> verify -> capture |
| [70_Resources/Skill_Router_Matrix.md](70_Resources/Skill_Router_Matrix.md) | Which skill/procedure an agent must use per task type |
| [70_Resources/AI_OS_Eval_Prompt_Suite.md](70_Resources/AI_OS_Eval_Prompt_Suite.md) | How to test that agents actually behave |
| [01_Index/AI_Context.md](01_Index/AI_Context.md) | The note agents read first every session |

## Your first hour

1. **Set up**: use the native Setup app, or follow [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md) as the manual fallback.
2. **Verify**: run `tools/check_agent_health.ps1` and `tools/check_ai_os_readiness.ps1`. Green (or explained SKIP) means the skeleton is coherent.
3. **Demo**: run the first-session script from [TEMPLATE_USAGE_DEMO.md](TEMPLATE_USAGE_DEMO.md) with your agent of choice.
4. **Evals**: pick 3 prompts from the eval suite (E01 source-of-truth, E05 secret refusal, E13 memory-trap) and run them in a fresh agent session. If the agent fails, fix the router/protocol, not the agent.

## Folder map

```text
00 root        entry points, setup docs, pitch
01_Index/      navigation: AI context, project map, people, glossary, user profile
10_Project/    brief, current focus, roadmap
20_Domain/     domain model and business rules
30_Tech/       tech map, codebase map
40_Decisions/  decision log + ADRs
50_Meetings/   meeting log + notes
60_Tasks/      task log
70_Resources/  the AI OS itself: protocol, router, evals, runbooks, procedures
tools/         health/readiness/sync/watch scripts (PowerShell)
template-skills/  bundled agent skills + manifest
```

## Rules that keep this alive

- Every important note gets frontmatter (`type`, `status`, `updated`) and wikilinks.
- Decisions go to `40_Decisions/`, not into chat history.
- Secrets never go into notes. Anywhere. Ever.
- Weekly: compact `10_Project/Current_Focus.md`, close done tasks, run the readiness check.
