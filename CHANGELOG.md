# Changelog

## 0.4.5 - Safe folder suggestion

- When the default `Мой проект` folder is already registered or contains files, Setup suggests the first free numbered folder instead of offering the occupied path again.
- Typing the path of an already registered project now gives a clear message and points to **Открыть AI OS** or **Восстановить** instead of starting a duplicate installation.
- Regression tests cover registered, empty and non-empty destination folders.

## 0.4.4 - Pasted paths and per-project passport data

- Setup accepts Windows paths pasted with surrounding double quotes and removes only the outer pair before validation. The same normalization applies to an existing code-repository path.
- The form now distinguishes the new AI OS workspace from the existing folder that contains product code.
- Passport memory totals are read from the active workspace's configured MGI-Mind library instead of combining every project on the computer.
- Regression tests cover quoted paths and dashboard isolation across multiple memory libraries.

## 0.4.3 - Reliable opening, progress and repair

- **Открыть AI OS** now raises the existing window for that project instead of creating another tray icon or a short-lived duplicate process. The local instance protocol also handles commands split across several TCP packets.
- Repair always refreshes managed scripts and the AI OS binary from the verified package, including same-size files with matching timestamps. Project notes, answers and memory identity remain unchanged.
- Setup updates installation progress inside the existing page instead of rebuilding it every few seconds. The 3D brain is loaded only for the first introduction and is disposed before later pages open.
- User-facing labels and Help text now use plain Russian. Obsolete labels such as **Центр проекта**, **Быстрый захват**, **Телеметрия** and **Очередь** are rejected by regression tests.
- The shared supervisor keeps one AI OS process for the active project. Its integration test now uses an isolated lock, so a running production supervisor cannot hide a test failure.
- The standalone template build now finds its own root automatically. It no longer assumes that it is running inside the maintainer repository.

## 0.4.2 - Reliable Windows workspace creation

- Fixed a Windows `RemoteSigned` failure caused by passing PowerShell a verbatim `\\?\C:\...` path to the bundled setup script. Child processes now receive ordinary local paths while the execution policy remains strict.
- Setup now rejects a non-empty workspace folder before starting installation, explains that existing source code belongs in the separate repository field, and preserves every submitted form value after validation.
- Windows OEM-encoded PowerShell logs are decoded correctly. Failed installs open the relevant log automatically and show a plain-language reason without deleting existing files.
- Split Windows delivery into a small online Setup and a complete Offline Kit. Online Setup downloads only missing pinned packages over HTTPS, verifies archive and binary SHA-256 values, resumes interrupted downloads and reuses one shared cache across projects.
- Removed the transition hitch by deferring WebGL render-buffer resizing until the shared brain movement finishes, coalescing later resizes and lowering unnecessary pixel-buffer cost.
- Setup now assigns the current product icon directly to the runtime window as well as the executable and installer, avoiding the stale generic taskbar icon.

## 0.4.1 - Authored setup scene and quieter Control Center

- Rebuilt the installer hero around a Blender-authored anatomical brain source and a lighter runtime GLB. The live Three.js layer now renders up to 32,000 outlined signal triangles instead of generic pyramids.
- The brain disassembly is driven by the actual setup-form scroll position: scrolling down releases the same particles through deterministic paths, and scrolling back up reconstructs the same object. Reduced-motion mode keeps the brain assembled.
- Updated Control Center to 0.6.1. Removed the built-in Search/Ask assistant from the product navigation so users work with Claude Code, Codex or Cursor directly in the workspace.
- Replaced the animated system-map concept with a static operational ledger backed by real context, memory, git, health, task and event state. Removed scan lines, moving packets, cursor-reactive decoration and perpetual UI motion.
- Re-ran Rust tests and wide/compact visual checks for the installer and Control Center; both layouts avoid horizontal overflow.

## 0.4.0 - Linux release and reproducible distribution

- Added one shared Rust/Tauri codebase for Windows and Linux x86_64. Windows keeps the branded `.exe`; Linux ships a native `.deb` for Ubuntu/Debian and a portable `.AppImage` for other modern distributions.
- The Linux package bundles checksum-verified PowerShell Core 7.6.3, MGI-Mind 2.4.0 and codebase-memory-mcp 0.9.0. Users do not need Rust, Python, Node.js or a manual MCP installation to create a workspace.
- Added XDG-compliant state/data paths and a shared Linux supervisor. It uses `systemd --user` when available and an XDG Autostart fallback otherwise, while keeping workspace notes outside the application lifecycle.
- Updated Control Center to 0.6.0: search, Ask AI, CLI discovery/install, project manager launch, timeouts, checks, Passport, Help, tray behavior and file opening now have platform-specific safe paths.
- Fixed project-memory isolation in `sync_mgimind.ps1`: imports now use the `memoryLibrary` from the current workspace config instead of silently importing every project into `agent`.
- Added `tools/build_ai_os_linux.sh` and a GitHub Actions Ubuntu 22.04 build. The release source is the sanitized `distribution/workspace-template`, so clean runners can reproduce the package without the maintainer's personal vault.

## 0.3.2 - Current Control Center and passport

- Updated Control Center to 0.5.1. Setup and app versions are now shown separately, and every user-facing section is generated from the current release contract rather than historical copy.
- Rebuilt the Russian Help page around the real onboarding flow: launch Setup, choose **Начать установку**, complete preflight, select **Создать среду**, then use Projects for every later workspace. Requirements, optional tools, SmartScreen, recovery and project isolation are explained in one place.
- Replaced the old paper-style passport with the same dark technical control-room language as the app. It now identifies Setup 0.3.2 and Control Center 0.5.1, includes a concise installation path, and keeps old release entries in raw logs without presenting them as current UI.
- Removed Gemini CLI from the Ask screen because no verified read-only adapter exists. Every console offered by the UI now has a tested read-only command path.
- Added `--render-pages` to export all seven user-facing pages for deterministic desktop/compact visual QA. Eleven Rust tests cover command safety, workspace isolation, release text, the Help contract and the visual export.

## 0.3.1 - Guided animated setup

- Replaced the immediate form with a three-stage first-run experience: real-resource loading, a focused introduction, and a shared-element transition into setup. The anatomical brain remains the same WebGL object while moving from the hero into the left setup panel.
- Added a staggered GPU reveal for the 8,200 instanced pyramids, pointer response, an interruptible CTA transition, and a complete reduced-motion path without adding another runtime dependency.
- Replaced system-dependent Inter fallbacks with self-hosted Onest variable-font subsets for Cyrillic and Latin. The OFL license ships with the installer; primary text is 15-16 px and visible setup labels no longer drop below 11 px.
- Added explicit wide and compact visual checks for loading, introduction, transition and setup states. The CTA remains in the first viewport and both layouts avoid horizontal overflow.

## 0.3.0 - Multi-workspace manager

- Rebuilt the Windows onboarding as one branded Russian-first product surface. The stock NSIS wizard stays silent and launches the custom setup UI; WebView2 is bundled for offline clean-machine startup.
- The setup preflight distinguishes required and optional components, checks disk space, and explains honest fallbacks for missing Obsidian, Git, AI consoles and internet access.
- Replaced the procedural particle blob with an anatomically authored 3D brain surface rendered as one GPU-instanced field of interactive pyramids. Motion respects `prefers-reduced-motion`; the bundled third-party mesh keeps its MIT notice.
- Redesigned Control Center navigation around daily jobs: Overview, Projects, Search, Ask AI and Checks are primary; Passport and Help are secondary; quick capture remains in Overview instead of occupying a duplicate tab.
- Setup now keeps a registry of every workspace instead of remembering only the last folder. The Russian UI lists projects, marks the active one, and targets open, repair, automation and forget actions by a stable path-derived workspace ID.
- Project names no longer identify memory or automation. Two projects may use the same display name without sharing a memory library or overwriting each other's lifecycle state.
- One global `AI-OS Supervisor` replaces four scheduled tasks per project. It runs one active Control Center, keeps the shared memory service available, watches each enabled workspace, serializes targeted imports and runs readiness when due.
- Existing 0.2.x single-workspace state migrates automatically. Forgetting a workspace removes only its registry entry; user notes are never deleted.
- Added a ten-workspace supervisor contract test and native registry/UI regressions. The builder refuses version drift between the installer and this template.

## 0.2.0 - Native setup and context hygiene

- Added a real per-user Windows product installer (`AI_OS_Setup_v0.2.0_x64.exe`) with a native first-run form, live setup log, checksum-verified bundled MGI-Mind and codebase-memory binaries, skill activation, project-scoped MCP configuration, background checks, final readiness proof, Control Center launch, repair, and safe automation removal. It needs no Rust, terminal, or administrator rights; logins and trust prompts remain explicit user actions.
- Added `tools/install_ai_os_workspace.ps1`, the testable setup engine. Fresh install refuses a non-empty destination; `-Repair` never recopies or replaces project notes; uninstall/automation removal keeps the workspace. `tools/tests/test_ai_os_workspace_installer.ps1` proves those boundaries.
- Added report-only `tools/check_context_hygiene.ps1` plus its regression test. It reports unlinked/stale notes, missing frontmatter, duplicate/cold memory, deleted-source orphans and Claude shadow-memory risk without invoking any mutating memory command.
- Disabled Claude project auto-memory in `.claude/settings.json`. This workspace already has canonical markdown plus a rebuildable retrieval index; a second self-written memory store can silently drift.
- Product build is reproducible through `tools/build_ai_os_installer.ps1` in the maintainer vault: pinned Tauri CLI, publisher checksum verification, sanitization scan, build mutex, MSVC discovery, Rust/PowerShell/self-tests and a published installer SHA-256. The beta is intentionally marked unsigned until a code-signing certificate exists.
- Health reads now share the memory-sync mutex: a scheduled readiness run waits for an active watcher import instead of reporting a false failure while the derived index is being replaced. When a nested health run really fails, readiness surfaces the actual `FAIL` row rather than the first green table rows.
- The destructive cold-start test now stops the watcher and acquires the same sync mutex before terminating Qdrant, so it cannot interrupt an import that the watcher already launched.

## 0.1.16 - Serialized memory sync

- Fixed a real watcher/manual-sync race: all memory imports for the same workspace now share one mutex, so a second sync waits instead of writing to the index concurrently.
- Fixed another false-green edge case: exactly one failed memory import now reliably returns exit code 1.
- Added `tools/tests/test_mgimind_sync_lock.ps1`, which launches two sync processes against a guarded fake importer and separately verifies the single-failure exit code.

## 0.1.15 - Honest checks, isolated memory, resilient startup

- Fixed a false-green bug in both PowerShell checkers: a single `FAIL` now reliably returns exit code 1. Added `tools/tests/test_ai_os_exit_codes.ps1`, which injects exactly one failure into each checker and proves automation cannot silently pass it.
- Added `tools/install_ai_os_scheduled_tasks.ps1` and contract tests. Full setup now creates readiness, memory service, watcher and optional Control Center tasks through one command. Tasks run hidden, work on battery, catch up missed runs, reject duplicates, retry crashes and use a second watchdog trigger. The memory cold-start test verifies a real stopped-to-ready cycle.
- Control Center is now v0.5.0. Ask uses verified hard read-only modes (`codex exec --sandbox read-only --ephemeral`; Claude plan mode with read-only tools), self-test captures only inside a temporary workspace, and startup supports `--start-hidden` for the tray task.
- Closed a cross-project isolation bug: an unconfigured workspace no longer discovers a machine-global `mgimind.exe` and silently searches the default `agent` library. Search is enabled only by this workspace's filled `tools/ai_os.config.json`. Seven Rust tests cover command safety, MCP naming, capture isolation and memory isolation.
- Skill activation now keeps one canonical implementation in `.agents/skills`; `tools/sync_agent_skills.ps1` creates lightweight Claude discovery bridges instead of duplicating every skill tree into `.claude/skills`.
- Distribution provenance is now reproducible. The kit builder downloads official MGI-Mind v2.4.0, verifies the publisher's archive SHA-256, includes its Apache-2.0 license and provenance notice, generates checksums for both executables, verifies ZIP contents, and refuses local/runtime files. The previous untraceable development binary and manually bundled Qdrant/ONNX files are no longer distributed.

## 0.1.14 - Native Control Center app bundled

- The template now ships the optional native desktop app under `tools/control-center-app/` (Rust + Tauri 2, a single `src/main.rs`, server-rendered HTML over a custom `dash://` protocol — no bundled Node/JS). It is a convenience layer over the same notes and checks, never a dependency: the whole system still works from any agent/editor without it, and the app only reads notes and appends captures to `60_Tasks/Inbox.md`.
- Sections: Today (event feed + open tasks + quick capture), Search (meaning-based memory search), Ask (a live agent reads the notes and answers via whichever console is installed — Claude Code / Codex / Gemini, auto-detected, with in-app install and login-open buttons), Capture, Checks (run the self-check by hand, heartbeat history), Passport (the full generated report) and Help. Every section has a plain-language "How this works" explanation.
- A **prebuilt Windows binary** is included at `tools/control-center-app/bin/ai-os-control-center.exe` so a non-technical recipient needs no Rust or build tools — just WebView2 (already on Windows 11 / recent Edge). `TEMPLATE_SETUP.md` gained an "Optional: the native Control Center app" section covering the WebView2 requirement, running it, the desktop shortcut and building from source. `Tech_Map.md` and `Codebase_Map.md` now list the app.
- UI ported to English and de-personalized (identifier `org.aios.controlcenter`); the author-credit line is kept intentionally as template branding, consistent with the generated passport. Verified with `--selftest` before packaging.

## 0.1.13 - Source/kit sync repair

- Fixed a distribution-process bug: the 0.1.11/0.1.12 work (the `obsidian-markdown` skill, the setup-step renumbering, and the manifest/router/AGENTS/roadmap/README/sanitization-report updates) had been edited directly in the already-unzipped Desktop kit copy instead of this canonical template folder, so the canonical source itself was still frozen at 0.1.10. Found by a full recursive diff between the two trees; all 0.1.11/0.1.12 content is now also in the canonical source, and the kit copy is regenerated from it (no more independent copies).
- The same divergence had gone the other way for three smaller items: two "-WindowStyle Hidden is intentional" reminders in `TEMPLATE_SETUP.md` and one matching bullet in `MGI_Mind_Local_Setup_Template.md`, plus an atomic temp-file-then-rename write in `make_dashboard.ps1`, existed only in the canonical source and had been silently dropped from the Desktop copy. Restored in both places.
- Re-verified from a clean run against the canonical source: `check_agent_health.ps1` and `check_ai_os_readiness.ps1` both exit 0 (readiness's one WARN — no recorded eval passes yet — is expected on a fresh template); a full-tree scan for personal/company names, absolute paths and the source project's identifiers found nothing beyond the already-documented, intentional author-credit line in the generated passport.
- Process lesson: always edit this canonical folder and regenerate the Desktop kit copy from it — never hand-edit inside an already-unzipped distribution copy.

## 0.1.12 - Explicit skill activation during setup

- `TEMPLATE_SETUP.md` now has an explicit bundled-skills activation step: copy `template-skills/` into project-local `.agents/skills` and `.claude/skills`, then restart the agent session.
- This removes an onboarding ambiguity: the skills were bundled and documented in the manifest, but the main full-install script did not previously make their activation unavoidable.

## 0.1.11 - Obsidian note editing skill

- Bundled `obsidian-markdown` from `kepano/obsidian-skills` for Obsidian-flavored Markdown notes: wikilinks, properties/frontmatter, embeds and callouts.
- Keeps the intentional system-author signature in the generated passport; this is template branding, not project context.
- Router, AGENTS, roadmap, manifest, README and sanitization report now distinguish note editing (`obsidian-markdown`) from canvas editing (`json-canvas`). Bundled skill count is now 14.
- The upstream MIT license is included as `template-skills/obsidian-markdown/LICENSE.txt`.
## 0.1.10 — Control Center: the technical passport

- `tools/make_dashboard.ps1` fully redesigned after live owner feedback ("too AI-looking"): the dashboard is now a **technical passport of the system** — a drawing-frame cover with a title block, an inspection stamp (INSPECTED / PASSED WITH REMARKS / FAILED INSPECTION / NOT INSPECTED), graph-paper chart panels and 14 numbered sections: plain-words purpose, an honest comparison with ordinary chat, system diagrams, the fresh inspection run, self-check history, autopilots, memory, behavior evals, safety and discipline, a build chronicle assembled from the task log, the system in numbers, the agent journal, computed next steps and a glossary.
- Honesty hardening from a 32-agent review (27 confirmed findings fixed): the self-check schedule description is read from Task Scheduler at build time; the hook claim is verified against `.claude/settings.json`; three comparison-table cells are live (bound to this run's data); the cloud-privacy sentence tells the truth about cloud agents; eval passes are aggregated across ALL run notes; undated task-log entries are counted and disclosed; an empty check run stamps NOT INSPECTED instead of a fabricated green verdict.
- Robustness and design: zero-byte notes no longer crash the build; tables and chart panels scroll inside themselves on narrow screens instead of breaking the page; readable comparison-table contrast; ruled key-figures blocks instead of the generic stat row.

## 0.1.9 — Control Center (stage 1)

- **`tools/make_dashboard.ps1`** — the system got a face: a self-contained health dashboard at `.local/dashboard.html` (no network, no JS, opens with a double click). Shows: fresh check run with a health verdict, autopilot states (watcher/self-check/memory autostart, found by script path), memory index size and last sync, security summary, eval progress, self-check history dots, an agent events feed and computed next steps. Light paper-and-ink design, one accent color.
- **`tools/log_agent_event.ps1`** — unified agent event journal (`.local/agent-events.ndjson`, auto-rotated): any agent (Claude/Codex/Cursor) appends one JSON line per finished task; the protocol's End-Of-Task Self-Audit now includes this step. One journal, one format, every agent visible on the dashboard.
- Both wired into readiness required-files and syntax checks. Known trap documented: PowerShell 5.1 reads BOM-less scripts as ANSI — non-ASCII strings in .ps1 require UTF-8 with BOM (the template scripts are ASCII-safe English).

## 0.1.8 — deep secret scanning (optional layer)

- New `tools/gitleaks.toml` and a `gitleaks-scan` health check: when the single-binary gitleaks is installed, the self-check additionally runs ~170 curated secret detectors (with the same directory exclusions as the built-in scan); reports SKIP while the tool is absent. Install note in `tools/README.md`; also documents a one-off git-history scan command.
- Both scheduled tasks (self-check and watcher) now run with a **hidden window** — previously a visible console appeared and closing it killed the watcher (found live in the source system: exit 0xC000013A).

## 0.1.7 — clock-independent self-check

- The daily readiness task now has TWO triggers: 2 minutes after every logon (laptops switched on at any hour get their check immediately) plus daily 11:00 with missed-run catch-up (always-on machines); overlapping runs are prevented. The self-check no longer depends on when the machine happens to be on.

## 0.1.6 — memory watcher on autopilot

- Full install now also creates the **background memory watcher** task (when the memory layer is configured): notes are reimported into the memory index automatically as they change. Logon trigger + daily keep-alive; a documented Task Scheduler trap (a zero execution-time limit kills the task instantly on current Windows) is avoided with a long explicit limit.
- Watcher hardened for unattended life: single-instance mutex (a second copy exits immediately) and automatic log rotation at ~1 MB.
- Health check gained `watcher-autorun`: OK only while the watcher task is actually Running; SKIP when the memory layer is not configured.

## 0.1.5 — feedback loop

- New `60_Tasks/System_Proposals.md`: agents record OS-layer ideas/problems there (generic wording, no project details) instead of the project task log; all maintenance-boundary texts now point to it.
- New `tools/make_feedback_report.ps1` ("make a feedback report"): builds ONE anonymized file at `.local/feedback-report.md` — template version, check names+statuses (no details), check-history counters and System_Proposals verbatim; no note content, no paths, no secrets; nothing is sent automatically — the user reviews and sends it to the template author manually. Documented in START_HERE and TEMPLATE_SETUP; wired into readiness required-files and syntax checks.

## 0.1.4 — recall gate and audit hardening

- **Recall gate** in all three entry points (top of `CLAUDE.md`, Working Rules in `AGENTS.md`, the Cursor rule): before any claim about people, meetings, past decisions or project state — including advice and predictions — search memory and open the canonical note; predictions about real people are factual claims. Driven by a real incident in the source system where an agent characterized a stakeholder from priors while the meeting notes sat unread.
- New evals **E17-person-projection-trap** and **E18-advice-mode-capture**; readiness now requires E01-E18. New router row for person-questions; capture-quality guide and Meeting_Log now explicitly ban unsourced predictions about real people.
- Setup hardening from a 63-agent audit: execution-policy step added to Step 0 (fresh Windows defaults to Restricted); `{{CODE_INTEL_TOOL_PATH}}` documented in the README placeholder table and wired through Step 3 (including the tool-reuse path); "repo: none yet" case handled; memory-tool kit folder location clarified; token conventions (`{{...}}` vs `<...>`) explained; placeholder note added to START_HERE.
- `tools/sync_mgimind.ps1`: config failures now report WHICH problem occurred (missing file / invalid JSON / unfilled placeholders / bad library name / missing executable) instead of one generic message; library names are validated.
- **Runtime reminder hook** (`.claude/settings.json`): a one-line recall/capture reminder is injected on every user prompt — the rule no longer depends on the agent remembering to apply it. Claude Code asks once to trust the workspace hooks (noted in Step 0). Plus **E19-stale-world-fact** and an external-facts clause in the recall gate: time-sensitive world facts (versions, prices, rates) must be web-verified or labeled as possibly-outdated model memory.

## 0.1.3 — full-install by default and the maintenance boundary

- `TEMPLATE_SETUP.md` rewritten as an agent-executed full-install script: the user says "set up this workspace", the agent interviews them and installs everything — placeholders, seed notes, git init, the code-intelligence layer (quarantine recipe with checksum verification, bundled installer never executed), the memory layer (or an honest skip when the tool is not provided), the daily scheduled self-check, verification and a plain-language report. Minimal install only on explicit request.
- New "System Maintenance Boundary": after setup, agents in the workspace use the system and update project notes, but do not modify the OS layer (protocol, router, evals, scripts, entry points) — the OS is a stable, versioned system; change ideas become Task_Log proposals, and OS updates ship only as new template versions. Encoded in `AGENTS.md`, `CLAUDE.md`, the Cursor rule, the protocol, the router and the AI context note.
- Installation trigger encoded in all three entry points; `START_HERE.md` first message and `README.md` quick start updated; `.mcp.json.template` now covers both servers; the "when is it worth doing" guidance for optional layers lives in setup step 4.

## 0.1.2 — review discipline and code intelligence

- `70_Resources/Procedure_Multi_Agent_Review.md`: Builder/Reviewer/Product-critic/Archivist roles, manual loop, fresh-session requirement for reviewers; wired into the router, entry points and indexes.
- `template-skills/SKILLS_MANIFEST.md`: added `codebase-memory-mcp` as an install-only code-intelligence recommendation with safety notes (installer rewrites agent entry points — diff and re-run readiness after install; `.cbmignore` before indexing; its ADR feature does not replace the Decision Log; pilot on a non-sensitive repo first).
- Router: code-structure row now mentions the optional code-intelligence layer; review row points to the multi-agent procedure.

## 0.1.1 — distribution polish

- `AI_COLLABORATION_101.md`: ten-habit primer for people new to working with agents, with a mini-glossary and anti-patterns.
- `70_Resources/Procedure_Meeting_Capture.md`: generic meeting/voice capture pipeline (local transcription, raw-transcript quarantine, extraction into logs); wired into the router, entry points and indexes.
- `PITCH_FOR_TEAM.ru.md`: Russian version of the team pitch.
- `tools/README.md`: plain-language guide to the scripts, exit codes, logs and the `Unblock-File` step for downloaded copies.
- `TEMPLATE_SETUP.md`: added the mark-of-the-web unblock step for distributed zips.
- `tools/check_agent_health.ps1`: the scheduled-task check now finds the task by the action path of this workspace's wrapper script instead of a fixed task name — no more collisions between multiple workspaces on one machine.
- `TEMPLATE_SANITIZATION_REPORT.md`: updated verification results and limitations.

## 0.1.0 — initial extraction

- Template extracted (allowlist rewrite) from a live AI OS workspace: entry points, workflow protocol, context automation, quality guide, skill router, eval suite E01-E16 + run log, memory-layer runbook template, three procedures, five template-safe PowerShell tools with config-driven memory layer, 13 bundled skills + manifest, onboarding docs and sanitization report.
