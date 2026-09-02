# AI Project Workspace Template (AI OS)

A reusable template for running a project with AI agents (Claude Code, Codex, Cursor and compatible tools) without losing context, repeating yourself, or trusting an agent's memory over reality.

This is not a prompt pack. It is an operating system for project context:

```text
Chats, calls, documents, code
        v
Capture: decisions, tasks, facts, procedures
        v
Workspace vault: canonical markdown source of truth
        v
Retrieval layer: semantic memory / grep / structure index (optional)
        v
Execution layer: your AI agents + skills
        v
Verification: tests, builds, checks, source documents
        v
Durable context captured back into the vault
```

## Core principles

1. **Markdown is the source of truth.** Code and primary documents outrank notes; notes outrank any memory layer; memory layers outrank nothing — they only help you find the note.
2. **One protocol for every agent.** Claude, Codex and Cursor all load entry points that converge on the same workflow: recall -> read canonical sources -> challenge -> act -> verify -> capture.
3. **Agents are not yes-men.** The protocol requires pushback (once, with reasons) when a request conflicts with code, decisions, security, or a simpler alternative.
4. **Trust is verified, not assumed.** A skill router says which tool to use when; an eval suite tests agent behavior; health and readiness scripts check the system itself; everything logs.
5. **Capture is automatic.** Agents update the vault at task closeout — decisions, tasks, gotchas, procedures — so the next agent (or person) starts warm.

## What is in the box

| Area | Contents |
| --- | --- |
| Entry points | `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/context-map.mdc`, `.mcp.json.template` |
| Core notes | `01_Index/`, `10_Project/`, `20_Domain/`, `30_Tech/`, `40_Decisions/`, `50_Meetings/`, `60_Tasks/` skeletons with placeholders |
| AI OS resources | Workflow protocol, context automation, quality guide, skill router, eval suite, memory-layer runbook, procedure templates (`70_Resources/`) |
| Tools | Health/readiness checks, memory startup and sync, change watcher, resilient scheduled-task installer, native Control Center (`tools/`) |
| Skills | 15 bundled universal agent skills + manifest with install-only recommendations (`template-skills/`) |
| Onboarding | `START_HERE.md`, `AI_COLLABORATION_101.md`, `TEMPLATE_SETUP.md`, `TEMPLATE_USAGE_DEMO.md`, `PITCH_FOR_TEAM.md` (+ Russian version), `tools/README.md`, `CHANGELOG.md` |

## Quick start

1. **Recommended:** run `AI_OS_Setup_v0.4.5_x64.exe` on Windows. This small online Setup verifies and caches only missing packages; `AI_OS_Offline_Kit_v0.4.5_x64.exe` is the no-network alternative. The current verified Linux packages are version 0.4.1: use `AI_OS_Setup_v0.4.1_linux_x86_64.deb` on Ubuntu/Debian or the matching `.AppImage` on another modern x86_64 distribution. Choose **Начать установку**, enter the project details, then select **Создать среду**. Setup creates an isolated workspace, activates skills, connects verified memory/code-intelligence tools, and registers the project with one shared background supervisor. If the usual `Мой проект` folder is already occupied, Setup chooses the first free numbered folder. Typical first setup: 2-5 minutes plus the first local-model download; later projects reuse the cache.
2. Account sign-in and workspace trust prompts remain explicit user actions. The installer never asks for or stores passwords, API keys, email credentials, or customer data.
3. Read [START_HERE.md](START_HERE.md), then work as shown in [TEMPLATE_USAGE_DEMO.md](TEMPLATE_USAGE_DEMO.md).
4. **Auditable fallback:** if the native installer is unavailable, unpack the manual kit, open an agent in this folder, and say **"set up this workspace"**. The agent follows [TEMPLATE_SETUP.md](TEMPLATE_SETUP.md) end-to-end.

The Windows installer is per-user and bundles WebView2. The Linux `.deb` uses the system package manager for WebKitGTK dependencies; the AppImage is the portable fallback. Open AI OS again to create another project in a different folder; the project list keeps notes, memory and actions separate. Beta packages are not yet code-signed, so verify the published SHA-256 before running them. Removing the app never deletes project notes.

Maintenance model: your project content is yours to grow; the OS layer (protocol, router, scripts, checks) is a stable, versioned system that arrives complete — agents in the workspace use it but do not modify it, and OS updates ship only as new template versions (see "System Maintenance Boundary" in [AGENTS.md](AGENTS.md) and [CHANGELOG.md](CHANGELOG.md)).

## Placeholders used throughout

| Placeholder | Meaning |
| --- | --- |
| `Денис` | The person who operates agents in this workspace |
| `Лабораторные работы по 1С` | The project this workspace serves |
| `n/a` | Client / main stakeholder (if any) |
| `n/a` | Company or legal entity (if any) |
| `D:\1с лабы` | Absolute path to this workspace folder |
| `none yet` | Absolute path to the product code repository |
| `aios-4b4830c2bea46660` | Library name in your semantic memory tool |
| `{{MEMORY_TOOL_PATH}}` | Absolute path to your memory tool executable |
| `{{CODE_INTEL_TOOL_PATH}}` | Absolute path to the code-intelligence executable (filled automatically during setup step 3) |

## One workspace per project

This workspace holds ONE project: its focus note, decisions, tasks and memory library are singular by design. For a new project, run AI OS again and create a fresh workspace — do not mix projects in one vault. Machine-level tools (memory, code intelligence) install once per computer; every following workspace reuses them, so the second setup is much faster. Each workspace gets its own memory library, config and MCP file, while one shared supervisor coordinates enabled projects without multiplying background services.

## Requirements and limits

- Native setup targets Windows 10/11 x64 and Linux x86_64. The Linux `.deb` baseline is Ubuntu 22.04+/Debian 12+; the AppImage targets other modern glibc-based distributions. ARM64 is not a full release target because the pinned MGI-Mind version has no Linux ARM64 binary.
- No Rust, Python, Node.js, preinstalled PowerShell or manual MCP setup is required. Windows needs no administrator rights; installing a Linux `.deb` uses the normal system package-manager authorization.
- Obsidian is recommended for wikilinks and graph view, but optional; without it, notes open in the system Markdown/text editor.
- Git and an AI CLI are optional during setup. Git enables local history; Claude Code, Codex or Cursor can be connected later and used directly from the workspace.
- Internet is needed only for the first memory-model download and for signing in to the chosen AI service. Workspace creation itself can finish offline; pending components are reported instead of hidden.
- Workspace scripts run on Windows PowerShell 5.1+ and the bundled PowerShell Core on Linux. OS-specific task-registration scripts remain intentionally separate.
- The native installer and Control Center support Windows and Linux x86_64 from the same source. macOS remains a future target; the markdown workspace itself is agent/editor agnostic.
- The semantic memory layer is optional. Everything works without it; checks report "not configured" instead of failing.
- Template language is English; write your actual notes in any language (see the memory runbook for a note on non-English rerankers).

## License notes

Bundled skills keep their own licenses (see `template-skills/SKILLS_MANIFEST.md`). The `frontend-design` skill is Apache-2.0 and `obsidian-markdown` is MIT; both ship with `LICENSE.txt` — keep those files with the skill folders.

The template itself ships without a license file: decide the terms (internal-only, MIT, ...) before distributing it beyond your team, and add a `LICENSE` file accordingly.
