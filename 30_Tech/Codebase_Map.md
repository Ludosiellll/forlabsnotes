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

## Repositories & Structure

| Component | Purpose | Location | Key commands |
| --- | --- | --- | --- |
| Workspace / AI OS | Markdown vault & agent skills | `D:\1с лабы` | `.agents/skills/...`, `tools/...` |
| 1C Cumulative Database | Infobase 1C:Enterprise (`1Cv8.1CD`) | `1С_ЛР4_Файлы\Base1C` (transfers to `ЛР<N>`) | `Запуск_1С_Предприятие.bat`, `Запуск_Конфигуратор.bat` |
| 1C Metadata XML Source | XML sources for batch compilation | `1С_ЛР4_Файлы\src\` | `load-config.ps1`, `dump-config.ps1` |
| EPF Generators | External processors for data population | `1С_ЛР4_Файлы\epf_src\` | `build-epf.ps1` |
| Flash Drive Delivery | Student `.dt` archives for grading | `E:\Программирование 1С\ЛР<N>\` | `DESIGNER /DumpIB` |

## Key Commands

- Run 1C:Enterprise (Thin Client): `D:\1c_app\8.3.27.1508\bin\1cv8ct.exe /F "d:\1с лабы\1С_ЛР4_Файлы\Base1C"`
- Run Designer (Thick Client): `D:\1c_app\8.3.27.1508\bin\1cv8t.exe DESIGNER /F "d:\1с лабы\1С_ЛР4_Файлы\Base1C"`
- Load Config from XML: `powershell -File .agents/skills/1c-batch/scripts/load-config.ps1 -XmlDir 1С_ЛР4_Файлы/src`
- Build EPF: `powershell -File .agents/skills/1c-batch/scripts/build-epf.ps1 -RootXml epf_src/ЗаполнениеЛР4.xml -Output epf/ЗаполнениеЛР4.epf`

## Gotchas / Known failure modes

- **CP866 Cyrillic Encoding in `cmd.exe`**: Console `cmd.exe` corrupts Cyrillic executable paths such as `D:\1cпред`. Use the ASCII junction `D:\1c_app` for platform binaries; never put `chcp 65001` in batch files.
- **Designer CLI project paths and completion**: the ASCII junction for the executable does not fix Cyrillic or spaced paths passed as Designer arguments. Mount the lab folder to an ASCII drive with `subst` per [[40_Decisions/2026-09-23_1C_CLI_Cyrillic_Paths_And_Subst_Bypass]], wait synchronously for Designer to finish, check its exit code, and inspect its output log before using the database.
- **Empty Form Stubs (`<ChildItems/>`)**: Scaffolding via `form-add.ps1` or `meta-compile.ps1` for CommonForm creates empty `<ChildItems/>`. Guard in `load-config.ps1` auto-compiles UI via `form-compile -FromObject`. If custom form is unneeded, let 1C auto-generate forms.
- **Exclusive Database Lock**: File-based `1Cv8.1CD` does not allow concurrent Designer sessions. Close all 1C client processes before running batch scripts.
- **Educational Platform Binaries**: 8.3.27.1508 Educational uses `1cv8t.exe` (fat/designer) and `1cv8ct.exe` (thin client). Standard `1cv8.exe` does not exist in this distribution.
- **Posting Data (`ОбработкаПроведения`)**: Auto-fill scripts (`.epf`) must save documents with `РежимЗаписиДокумента.Проведение`, and the module must set `Движения.ИмяРегистра.Записывать = Истина`, otherwise registers remain empty.
- **UTF-8 with BOM**: PowerShell 5.1 and 1C Designer require UTF-8 with BOM for scripts and BSL modules. Without BOM, Cyrillic text corrupts into ANSI/Windows-1251 mojibake.

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
