# Tools

Plain-language guide to the workspace scripts. Core scripts run on **Windows PowerShell 5.1+** and the **PowerShell Core runtime bundled by Linux Setup**. Platform registration is separate: Task Scheduler on Windows, user systemd/XDG Autostart on Linux.

## If the scripts refuse to run (downloaded template)

Files downloaded from the internet (zip, browser, messenger) get Windows' mark-of-the-web, and PowerShell's default policy (RemoteSigned) then refuses to run them. One-time fix after unpacking:

```powershell
Get-ChildItem "{{PROJECT_ROOT}}" -Recurse -File | Unblock-File
```

Agent-session note: some agent harnesses block commands containing `-ExecutionPolicy Bypass`. Invoke scripts as `& <path>\script.ps1` or `powershell.exe -NoProfile -File <path>` instead — no policy override needed for local (unblocked) scripts.

On Linux, run the native Setup package instead of installing PowerShell manually. For direct diagnostics, use the `powershellPath` recorded in `tools/ai_os.config.json`.

## The scripts

| Script | What it does | When to run | Exit codes |
| --- | --- | --- | --- |
| `check_agent_health.ps1` | Checks workspace content: wikilinks resolve, no secret patterns, canvas validity (if any), Current_Focus/Task_Log hygiene, raw-transcript placement, memory doctor/stats/freshness (when configured) | Weekly, after big note changes, when something feels off | 0 = no FAIL; 1 = at least one FAIL |
| `check_context_hygiene.ps1` | Report-only lint for unlinked/stale notes, missing frontmatter, duplicate/cold/orphan memory entries, and Claude shadow-memory risk; writes `.local/context-hygiene.{json,md}` and never mutates notes or memory | Weekly and before a template release | 0 = report written; 1 = checker execution failed |
| `check_ai_os_readiness.ps1` | Checks the AI OS wiring: required files, entry-point needles (protocol, non-yes-man, self-audit), router coverage, eval suite E01-E19, recorded eval runs, script syntax, .gitignore hygiene; then runs the health check | After changing entry points/protocol/router; daily via the scheduled task | 0 = no FAIL; 1 = FAIL |
| `install_ai_os_workspace.ps1` | Safe engine behind the native Setup app: copies a clean template, applies project answers, activates skills, configures verified local tools, automation and readiness; `-Repair` preserves user notes and `-RemoveAutomation` never deletes the workspace | Normally called by `AI_OS_Setup`; direct use is for audit/testing | 0 = ready; non-zero = setup refused or verification failed |
| `ai_os_package_cache.psm1` | Shared package layer behind Setup: reuses verified binaries, resumes interrupted HTTPS downloads, rejects checksum mismatches and repairs corrupt cache entries | Imported automatically by `install_ai_os_workspace.ps1`; users do not run it directly | throws on unsafe metadata, download or verification failure |
| `install_ai_os_scheduled_tasks.ps1` | Installs resilient hidden tasks for readiness and, when selected, memory service, watcher and Control Center | Once during full setup; again after moving the workspace | 0 = tasks registered and started; non-zero = setup failed |
| `install_ai_os_supervisor_linux.ps1` | Registers the shared supervisor with `systemd --user`, with XDG Autostart fallback | Called by Linux Setup; direct use is for diagnosis | 0 = registered/removed; non-zero = invalid runtime or registration failure |
| `start_mgimind.ps1` | Starts the configured local memory service and waits for its real readiness endpoint | By the scheduled memory-service task or manually while diagnosing startup | 0 = ready; 1 = startup failed or timed out |
| `sync_mgimind.ps1` | Imports workspace markdown folders into the semantic memory library (reads `ai_os.config.json`); serializes concurrent watcher/manual runs per workspace | After editing notes, or targeted: `-Dirs '30_Tech,70_Resources'` | 0 = OK; 1 = import failed or lock timeout; 2 = memory layer not configured |
| `watch_agent_reimport.ps1` | Polls for markdown changes and triggers targeted syncs after a debounce window (single-instance mutex, log rotation) | Autostarted by full install when the memory layer is configured (TEMPLATE_SETUP step 6); can also run manually | runs until stopped; 2 = not configured |
| `make_feedback_report.ps1` | Builds one anonymized feedback file (check statuses, counters, system proposals — no note content/paths/secrets) at `.local/feedback-report.md` | When you want to report a system problem to the template author | 0 = report written |
| `make_dashboard.ps1` | **Control Center**: builds the system's "technical passport" at `.local/dashboard.html` — a 14-section offline report (inspection stamp, plain-words explanation, comparison table, diagrams, live charts, chronicle, agent journal, glossary), every number from real local data | Whenever you want to SEE the system state or show it to someone; add `-Open` to launch the browser | 0 = built |
| `log_agent_event.ps1` | Appends one JSON line about a finished agent task to `.local/agent-events.ndjson` — feeds the Control Center events feed; any agent (Claude/Codex/Cursor) calls it at end of task per the protocol | Automatically by agents; never include secrets | 0 = logged |
| `run_scheduled_readiness.ps1` | Wrapper for the daily scheduled readiness run; full output to `.local/readiness-scheduled.log` (rotated ~512 KB) | Via Task Scheduler or the Linux shared supervisor | mirrors readiness exit code |

## Optional deep secret scan

Install [gitleaks](https://github.com/gitleaks/gitleaks/releases) into `%LOCALAPPDATA%\Programs\gitleaks\` on Windows or `~/.local/share/ai-os/bin/` on Linux. The health check picks it up automatically. Also worth running once on git history: `gitleaks git <workspace> --config tools/gitleaks.toml`.

## Configuration

`ai_os.config.template.json` -> copy to `ai_os.config.json` (gitignored) and fill in the memory tool path and library name. Until then, memory-related checks report SKIP with a hint instead of failing — that is intended.

## Logs

Everything logs to `.local/` (gitignored): `health-check.log`, `readiness-check.log` (summary counters), `readiness-scheduled.log` (full output), `mgimind-sync.log`, `mgimind-watch.log`. A system whose checks never leave traces is a system nobody actually runs.

## Known gotcha worth remembering

When calling `sync_mgimind.ps1` from another process (`powershell.exe -File ...`), pass `-Dirs` as ONE comma-joined string (`'30_Tech,70_Resources'`). A PowerShell array flattens into separate arguments across the process boundary and the second directory fails parameter binding. The watcher does this correctly; keep it that way.

Do not remove the per-workspace mutex from `sync_mgimind.ps1`. It prevents a manual sync and the background watcher from importing into the same memory index at the same time. `tools/tests/test_mgimind_sync_lock.ps1` covers this race and the single-failure exit code.
