---
type: tech
status: active
updated: YYYY-MM-DD
tags:
  - tech/codebase
  - ai/context
---

# Codebase Map

Map of repositories, modules, entry points, commands and gotchas. This is the implemented truth — agents read it before touching code and update it after learning something durable.

## Repositories

| Repository | Purpose | Location | Key commands |
| --- | --- | --- | --- |
| This workspace | Project context and AI OS | `D:\1с лабы` | `tools/check_agent_health.ps1`, `tools/check_ai_os_readiness.ps1`, `tools/sync_mgimind.ps1` |
| Лабораторные работы по 1С | Product code | `none yet` | e.g. `docker compose up --build`, `pytest` |

## Structure of the product repo

- `backend/` — ...
- `frontend/` — ...
- Record the three things future agents always need: entry points, test commands, known gotchas.

## Commands

- Run: ...
- Tests: ...
- Build: ...

## Gotchas / known failure modes

- Example shape: "YYYY-MM-DD: the first run without a filled `.env` fails on required secrets — intended behavior."
- Capture verified bug patterns here after each diagnosis (see [[70_Resources/Procedure_Bug_Diagnosis_Loop]]).

## AI OS tools (this workspace)

- `tools/check_agent_health.ps1` — checks wikilinks/secrets/memory freshness/hygiene.
- `tools/check_ai_os_readiness.ps1` — additionally checks entry points/protocol/router/evals/scripts.
- `tools/install_ai_os_scheduled_tasks.ps1` — installs hidden resilient readiness/memory/watcher/Control Center tasks; see `TEMPLATE_SETUP.md` Step 6.
- `tools/install_ai_os_supervisor_linux.ps1` — registers the shared Linux supervisor through `systemd --user`, with XDG Autostart fallback.
- `tools/start_mgimind.ps1` — starts the configured local memory service and waits for its actual readiness endpoint.
- `tools/sync_mgimind.ps1` — imports workspace markdown folders into the memory library (`-Dirs` accepts a comma-joined string; pass it as ONE string across the `powershell.exe -File` boundary).
- `tools/watch_agent_reimport.ps1` — debounced change watcher, autostarted by full setup when memory is configured.
- `tools/run_scheduled_readiness.ps1` — wrapper for scheduled readiness runs (see `TEMPLATE_SETUP.md` Step 6).
- `tools/control-center-app/` — optional native desktop app v0.6.2 for Windows/Linux x86_64 (Rust + Tauri 2; server-rendered HTML over a `dash://` protocol). The packaged platform binary lives in `bin/`; it is read-only over existing notes except explicit append-only captures, and it only accesses the memory library named by this workspace's local config. Build: `cargo build --release`; self-test: `cargo run --release -- --selftest`; visual export: `ai-os-control-center[.exe] --render-pages <output folder>`.
- `tools/ai-os-installer-app/` — Setup 0.4.5 shared source. The current verified Windows packages are 0.4.5; the current published Linux `.deb`/AppImage packages remain 0.4.1 until the shared source is rebuilt and reverified on Linux. Windows bundles NSIS/WebView2; Linux packages bundle verified PowerShell Core, MGI-Mind and codebase-memory binaries.
- `tools/build_ai_os_linux.sh` — reproducible Linux x86_64 build, workspace contract test and artifact checksums. CI runs it on Ubuntu 22.04.

## Links

- [[30_Tech/Tech_Map]]
- [[01_Index/AI_Context]]
- [[40_Decisions/Decision_Log]]
