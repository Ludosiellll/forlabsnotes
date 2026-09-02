# Template Setup — Full Install

> [!NOTE]
> **Native AI OS Setup is the default onboarding path.** Windows 0.4.5 offers a small online Setup that downloads only missing pinned packages into a shared verified cache, plus a complete Offline Kit. It skips workspace folders that are already registered or contain files. The current verified Linux packages are 0.4.1: use the `.deb` on Ubuntu/Debian or the matching `.AppImage` on another modern Linux x86_64 distribution. The packages perform these steps automatically, keep a local log, support multiple isolated projects through one shared supervisor, support repair, and verify the result. This document remains the auditable agent-driven fallback and the specification behind the installer.

**How the fallback works:** this document is an execution script for an AI agent (Claude Code, Codex, Cursor or compatible) running in this folder — not a manual checklist for a human. The user opens an agent session here and says "set up this workspace". The agent executes this document end-to-end, asking only for values only the user knows.

Token conventions: `{{...}}` tokens are replaced once during Step 1 and stay replaced; `<angle-bracket>` tokens are values the agent substitutes at execution time (e.g. `<workspace>` = this folder's absolute path).

**Agent, read this first:** run the steps in order; do not skip the optional layers unless the user explicitly asks for a minimal install; finish with a green readiness check and an honest report (step 8). While installing you are configuring the system — after setup is complete, the System Maintenance Boundary applies (see `AGENTS.md`): agents use the system and keep project notes updated, but do not modify the OS layer itself.

## Step 0 — Prepare a downloaded copy

On Windows, clear the mark-of-the-web once if this folder arrived through a browser or messenger:

```powershell
Get-ChildItem "<this workspace folder>" -Recurse -File | Unblock-File
```

Also check the execution policy: on a fresh Windows machine it is often `Restricted`, which blocks ALL scripts. If `Get-ExecutionPolicy -Scope CurrentUser` is not `RemoteSigned` (or laxer), set it once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

The workspace scripts deliberately never use `-ExecutionPolicy Bypass`; they rely on this one-time, transparent setting instead.

On Linux, use the native `.deb`/`.AppImage` whenever possible. For the manual fallback, PowerShell Core 7+ must be available as `pwsh`; make only the downloaded AppImage executable (`chmod +x <file>.AppImage`) and never run workspace scripts as root.

One more one-time approval: this workspace ships a small project hook (`.claude/settings.json`) that injects a one-line recall/capture reminder on every prompt. Claude Code will ask once whether to trust the workspace hooks — approve it; the full hook text is open for inspection in that file.

## Step 1 — Interview the user, replace placeholders, seed the notes

Ask the user (in their language) for:

1. Project name -> `Лабораторные работы по 1С`
2. Their name -> `Денис`
3. Client / main stakeholder (or "n/a") -> `n/a`
4. Company / legal entity (or "n/a") -> `n/a`
5. Absolute path of the code repository (or "none yet") -> `none yet`
6. A short name for the memory library (default: project slug) -> `aios-4b4830c2bea46660`
7. Two-three sentences: what the project is, who it is for, what is happening right now.

Then: replace ALL `{{...}}` placeholders across the workspace (`D:\1с лабы` = this folder's absolute path; `{{MEMORY_TOOL_PATH}}` is set in step 5), and fill the four seed notes from the user's answers: `10_Project/Project_Brief.md`, `10_Project/Current_Focus.md`, `30_Tech/Tech_Map.md`, `01_Index/People.md`. Set real dates in `updated:` fields you touch. Short honest drafts beat empty templates — mark unknowns as open questions.

## Step 2 — Activate bundled skills

The template ships skills under `template-skills/` as a clean distribution copy. Activate them for the local agent runtime before the first real work session:

```powershell
$workspace = "<workspace>"
$source = Join-Path $workspace "template-skills"
$canonical = Join-Path $workspace ".agents\skills"
New-Item -ItemType Directory -Force -Path $canonical | Out-Null
Get-ChildItem -Directory -Path $source | ForEach-Object {
    Copy-Item -Recurse -Force -Path $_.FullName -Destination (Join-Path $canonical $_.Name)
}
powershell.exe -NoProfile -File (Join-Path $workspace "tools\sync_agent_skills.ps1") -Root $workspace
```

Why the second command: `.agents/skills` is the one canonical implementation. Claude needs discovery files under `.claude/skills`, so the script creates tiny bridge skills that preserve each skill's description and point back to the canonical file. This avoids two full copies drifting apart. Do **not** delete `template-skills/`; it remains the clean distribution source. Tell the user to restart the agent session after this step so the runtime reloads the skill list.

## Step 3 — Version the workspace

```powershell
git -C "<workspace>" init
git -C "<workspace>" add -A
git -C "<workspace>" commit -m "Initialize AI project workspace from template"
```

The provided `.gitignore` already excludes local state, logs, machine-specific config and raw transcripts. Recommend the user opens the folder as an Obsidian vault (optional).

## Step 4 — Code-intelligence layer (installed by default)

A local code X-ray: call graph, impact analysis, dead code, route inventory.

**Already installed?** If this machine already has the tool (e.g. from another workspace set up earlier), reuse it — check `Test-Path (Join-Path $env:LOCALAPPDATA 'Programs\codebase-memory-mcp\codebase-memory-mcp.exe')`; if it exists, skip the download below, **record that full executable path — it becomes `{{CODE_INTEL_TOOL_PATH}}` in step 5's `.mcp.json`** — and go straight to indexing. The tool is installed once per machine; each workspace only registers and indexes. (After a fresh install below, the same applies: `$cbm` is the value for `{{CODE_INTEL_TOOL_PATH}}`.)

Otherwise install the **quarantine way** — never run its bundled installer (`install.ps1` / the binary's `install` command auto-rewrites agent configs and hooks; we keep entry points under our own control):

```powershell
$rel   = Invoke-RestMethod -Uri 'https://api.github.com/repos/DeusData/codebase-memory-mcp/releases/latest' -Headers @{ 'User-Agent' = 'ai-os-setup' }
$asset = $rel.assets | Where-Object { $_.name -eq 'codebase-memory-mcp-windows-amd64.zip' }
$sums  = $rel.assets | Where-Object { $_.name -eq 'checksums.txt' }
$tmp   = Join-Path $env:TEMP 'cbm-setup'; New-Item -ItemType Directory -Force -Path $tmp | Out-Null
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile (Join-Path $tmp $asset.name) -UseBasicParsing
Invoke-WebRequest -Uri $sums.browser_download_url  -OutFile (Join-Path $tmp 'checksums.txt') -UseBasicParsing
$actual   = (Get-FileHash -Path (Join-Path $tmp $asset.name) -Algorithm SHA256).Hash.ToLower()
$expected = ((Get-Content (Join-Path $tmp 'checksums.txt') | Where-Object { $_ -match [regex]::Escape($asset.name) -and $_ -notmatch '-ui-' }) -split '\s+')[0].ToLower()
if ($expected -ne $actual) { throw 'Checksum mismatch - stop and tell the user.' }
$dest = Join-Path $env:LOCALAPPDATA 'Programs\codebase-memory-mcp'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Expand-Archive -Path (Join-Path $tmp $asset.name) -DestinationPath $dest -Force
$cbm = Join-Path $dest 'codebase-memory-mcp.exe'
& $cbm config set auto_index false
Remove-Item -Recurse -Force $tmp
```

Rules baked into this recipe: checksum is verified; the bundled `install.ps1` inside the archive is **never executed**; auto-index stays off (index explicitly per repo); before indexing a repository that may contain sensitive files, add a `.cbmignore`. If the user gave a real code repo path in step 1, index it now: `& $cbm cli index_repository '{\"repo_path\": \"<repo path with forward slashes>\"}'`. If the answer was "none yet" — skip indexing, and note in the final report that the repo can be indexed later with this one command.

Known tool quirks (verified in the source workspace's pilot): find callers via `query_graph`/`search_code`, not `trace_path direction=callers`; dead React components are found via `search_code` cross-reference, not graph in-degree; `detect_changes` wants a clean git tree.

## Step 5 — Memory layer (installed by default when the tool is available)

The semantic index over the workspace notes. The reference implementation is a local import/search CLI that may be provided together with this template (any tool with "import markdown into a library + search + stats" fits). Worth noting: with only a handful of notes the workspace works fine without this layer — its value grows with the vault (agents stop re-reading everything and can find "where did we decide X" semantically); installing it now costs little and it simply grows in usefulness.

1. Check if the memory tool is already installed (`Get-Command` / known install path). If not, look for a `memory-tool` folder shipped **in the same parent directory as this workspace folder** (the distribution kit unpacks as one folder containing both, e.g. `...\kit\AI_OS_TEMPLATE_v0_1` and `...\kit\memory-tool`); it carries its own install note inside — follow it: copy its files to a `Programs` folder under the user's local application data and use that executable path. If there is no such folder, ask the user: "Was a memory tool provided together with this template?" If neither — **skip this step**, tell the user memory is pending, and continue (the checks will report it honestly).
2. Copy `tools/ai_os.config.template.json` to `tools/ai_os.config.json`; fill `memoryToolPath` and `memoryLibrary`.
3. Copy `.mcp.json.template` to `.mcp.json`; fill the memory tool path AND the code-intelligence path from step 4; remove the `_comment` key. (MCP servers activate on the next agent session — tell the user.)
4. Create the library and run the first import: `powershell.exe -NoProfile -File "<workspace>\tools\sync_mgimind.ps1"`.
5. Non-English notes? If the tool uses an English-tuned reranker, disable it (see `70_Resources/MGI_Mind_Local_Setup_Template.md` — this and other hard-won lessons live there).

## Step 6 — Self-check on autopilot (created by default)

Native Setup configures the correct shared supervisor automatically. The command below is the Windows manual fallback:

```powershell
powershell.exe -NoProfile -File "<workspace>\tools\install_ai_os_scheduled_tasks.ps1" `
  -Root "<workspace>" `
  -ProjectName "<project name>" `
  -IncludeControlCenter `
  -IncludeMemory
```

Use `-IncludeMemory` only when step 5 was completed. If memory was skipped, omit that switch. Use `-IncludeControlCenter` when the bundled app should start in the tray; omit it if the user does not want the app to start automatically.

This one installer creates the readiness check and, when requested, the memory service, memory watcher, and Control Center tasks. It also starts them once so setup verifies the real path instead of merely registering tasks.

Every task is hidden, allowed to start and continue on battery, catches up after a missed trigger, rejects duplicate instances, and retries after a crash. Each long-running service has both a logon trigger and a watchdog trigger. These settings prevent the blank terminal windows and silent battery-related shutdowns found during live testing.

The readiness log is `.local/readiness-scheduled.log`; memory logs are under `.local/mgimind-*.log`. To inspect the installed tasks:

```powershell
Get-ScheduledTask | Where-Object TaskName -like 'AI-OS*'
```

Disable or remove a task with `Disable-ScheduledTask` or `Unregister-ScheduledTask`. Re-run the installer after moving the workspace; it safely replaces this project's tasks with actions pointing at the new path.

On Linux, the package registers `ai-os-supervisor.service` under `systemd --user` and also writes an XDG Autostart fallback. Inspect it with `systemctl --user status ai-os-supervisor.service`; disabling automation from Setup removes the registration but never deletes the workspace.

## Step 7 — Verify

```powershell
powershell.exe -NoProfile -File "<workspace>\tools\check_ai_os_readiness.ps1"
```

Expected after a full install: everything OK; acceptable WARNs are exactly two — "no recorded eval passes yet" (closed during the first week, step 8) and memory-related SKIPs if step 5 was skipped. Any FAIL must be fixed before declaring the install done. The checks deliberately return a non-zero process exit code when even one FAIL exists, so automation cannot report a false green result.

## Step 8 — Final report and first week

Give the user an honest, plain-language report: what is installed and running, what was skipped and why, where the logs live, and what happens daily (the 11:00 self-check) and weekly (15-minute hygiene: compact Current_Focus, close done tasks, glance at the check log).

During the first week, run at least three behavior evals from `70_Resources/AI_OS_Eval_Prompt_Suite.md` (E01, E05, E13) in fresh sessions and record results in `70_Resources/AI_OS_Eval_Run_Log.md`.

## After setup: who changes what

- **The user and their agents**: use the system daily — work, capture decisions/tasks/meetings/gotchas into the project notes, sync memory, run checks. That is what the workspace is for. Project notes are yours and grow with the project.
- **The OS layer** (protocol, router, eval suite, scripts, entry points): arrives complete and stays as delivered — it is a stable, versioned system, not a construction site. If a system change ever seems needed, record it as a proposal in `60_Tasks/System_Proposals.md` and keep working within the current system. OS updates arrive only as new template versions (see `CHANGELOG.md`) and never touch your project notes.
- **Feedback loop**: found a problem or a rough edge in the system? Ask your agent to "make a feedback report" — it runs `tools/make_feedback_report.ps1`, which builds ONE anonymized file (check statuses + your recorded system proposals, no note content, no paths, no secrets) at `.local/feedback-report.md`. Review it and send it to the person who provided this template; fixes come back to everyone as a new template version.

## Optional: the native Control Center app (Windows and Linux)

The workspace ships an optional native desktop app — a "control panel" over the same notes and checks — under `tools/control-center-app/`. It is a convenience layer, **not** a dependency: every part of the system works from any agent/editor without it. The app never edits notes; it reads them and only appends (captures go to `60_Tasks/Inbox.md`).

What it gives a non-technical user: one Russian-first window with **Overview** (real system state, event feed, open tasks and quick capture), **Projects** (open the multi-workspace manager), **Checks** (run self-checks and see history), **Passport** (the current generated report) and **Help** (first install, more projects, requirements and recovery). Questions, semantic lookup and code work stay in Claude Code, Codex or Cursor, where the full workspace context and tools already live. Setup and Control Center versions are shown separately so an old artifact cannot masquerade as the current release.

**A platform binary is included** at `tools/control-center-app/bin/ai-os-control-center.exe` on Windows or `tools/control-center-app/bin/ai-os-control-center` on Linux. The user does not need Rust or build tools:

1. Windows uses the bundled WebView2 runtime. Linux `.deb` installs the required WebKitGTK dependencies through the package manager; the AppImage carries its portable runtime set.
2. Setup launches the correct binary with `AI_OS_ROOT` pointing at this workspace. You normally do not run the binary manually.
3. One shared supervisor starts the active project's Control Center in the tray with `--start-hidden`. Windows uses Task Scheduler; Linux uses `systemd --user` and falls back to the freedesktop XDG Autostart standard.
4. Closing the window hides it without touching notes. Use the tray's **Exit** action to stop it.

**Building from source:** install Rust and the platform's Tauri prerequisites, then run `cargo build --release` under `tools/control-center-app/`. The output is `target/release/ai-os-control-center[.exe]`. Verify it with `cargo run --release -- --selftest`; maintainers can export all seven pages with `ai-os-control-center --render-pages <output folder>`.

macOS is not a packaged target yet. The markdown workspace remains usable there through agents and editors, but native Setup/Control Center parity is not claimed.

## Minimal install (only if the user explicitly asks)

Steps 0-3 and 7-8 only. The workspace is fully functional on notes alone; the memory and code-intelligence layers can be added later by re-running steps 4-6 — nothing else changes. The native app (previous section) is likewise optional and can be run at any time.
