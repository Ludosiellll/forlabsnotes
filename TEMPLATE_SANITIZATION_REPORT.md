# Template Sanitization Report

How this template was extracted from a live project workspace, what was removed or generalized, and how sterility was verified. This report intentionally names **categories, not originals** — it must not re-introduce what was removed.

## Method

- **Allowlist, not copy-then-clean.** Every note, script and doc in this template was written fresh against the live system's structure. Nothing was bulk-copied except the 15 bundled skills, which were individually scanned before inclusion.
- All project/customer/operator values were replaced by placeholders: `Денис`, `Лабораторные работы по 1С`, `n/a`, `n/a`, `D:\1с лабы`, `none yet`, `aios-4b4830c2bea46660`, `{{MEMORY_TOOL_PATH}}`. The generated dashboard intentionally keeps the template author signature as branding; it is not project context.

## Removed entirely (not carried over)

- Version control history, local state, editor/app state, caches, virtual environments, delivery artifacts, junk folders.
- Real meeting notes and the meeting registry contents.
- Real task log contents, real decision records (ADRs), project history notes.
- Project specification documents and their reviews.
- Real audit reports, maturity assessments and level roadmaps of the source system (they describe a specific project's state).
- The source project's knowledge-graph canvas file.
- An audio-transcription pipeline runbook (contained machine-specific paths; rebuilt generically in 0.1.1 as `70_Resources/Procedure_Meeting_Capture.md`).
- A marketplace-integration procedure note (entirely project-specific).

## Generalized (structure kept, specifics replaced)

- **People**: real names/roles -> placeholder rows and an optional internal/external role-boundary pattern.
- **Working profile**: a specific person's preferences -> a fill-in profile with example shapes.
- **Domain content**: a specific business's balance/marketplace domain -> generic examples and fill-in sections.
- **Eval suite**: prompts referencing a specific product freeze, marketplace and memory tool -> generic restriction/no-edit, data-source and memory-layer wording (all 19 eval intents preserved: source of truth, restriction respect, memory-not-truth, tool hoarding, stale memory, sync discipline, secret refusal, role boundary, people recall, capture discipline, external-fact freshness, and the rest).
- **Skill router**: project-specific rows (marketplace sync, a named deploy target) -> generic "external data sync" and "deploy" rows.
- **Deploy procedure**: a platform-specific runbook -> a fill-in deploy template that keeps the safety gates (public exposure, default credentials, secrets in git).
- **Memory runbook**: a specific tool install log -> a reference-implementation template with the transferable lessons kept (non-English reranker, BOM in config JSON, raw-transcript exclusion, deletion-does-not-sync/orphans, freshness discipline, comma-joined `-Dirs` across process boundaries).
- **Scripts**: hardcoded absolute paths and a hardcoded memory library name -> `tools/ai_os.config.json` (from a template), with "not configured yet" SKIP behavior instead of failures. Scheduled tasks are created only by the generic project-named installer and are validated by path and behavior, not a source-project name.
- **Native app** (`tools/control-center-app/`, added 0.1.14; cross-platform in 0.4.0): its bundle identifier is generic, its default user-facing UI is Russian by product decision, and all strings are scanned for private project data. No workspace-specific paths or memory-library fallback are compiled in — it locates the workspace at runtime and requires that workspace's local memory config. The author-credit line is kept intentionally as branding, matching the generated dashboard.

## Bundled skills scan

- 15 skills bundled after a per-skill scan for personal context, absolute paths and project terms: negative.
- The only scan matches were false positives — short name fragments occurring inside ordinary English words (such as "categories"). Re-scan with word boundaries.
- License notes: bundled `frontend-design` is Apache-2.0 and bundled `obsidian-markdown` is MIT; both ship with `LICENSE.txt`. Two agent skills remain deliberately install-only (one has no license file in its distribution copy, the other is MIT but actively maintained upstream). See `template-skills/SKILLS_MANIFEST.md`.

## Verification performed (at template creation)

- Case-insensitive, word-boundary regex scan of the whole template for: source project names, client/company names, operator names, machine-specific user-profile/application-data paths, source project design-system and branch names, and source memory-tool executable names. **Result: 0 unintended matches**; the only allowed personal attribution is the intentional template author signature in the dashboard.
- Secret-pattern scan (api key/secret/password/token assignments, common token prefixes). **Result: 0 matches.**
- `tools/check_ai_os_readiness.ps1` run inside the template: **exit 0**; all checks OK except one intended WARN ("no recorded eval passes yet").
- `tools/check_agent_health.ps1` run inside the template: **exit 0**; wikilinks all resolve, secret scan clean, memory checks correctly SKIP with a "not configured yet" hint, sync script exits with a friendly message and code 2 when unconfigured.
- Local run artifacts (`.local/`) produced by these verification runs were deleted from the template afterwards.
- The 0.3.2 productization pass keeps the report-only context-hygiene checker and disabled Claude shadow-memory, extends the native Windows installer with a path-scoped multi-workspace registry and one shared supervisor, and includes the guided animated first-run experience with self-hosted OFL-licensed Cyrillic typography. Control Center 0.5.1 adds a Russian first-run/help path, a current dark passport, release-history filtering and reproducible page export for visual QA. The installer payload is rebuilt from this canonical template by allowlist, scans text files for source-project identifiers, verifies bundled executables against publisher checksums, and runs PowerShell/Rust/ten-workspace tests before release. The intentional author signature remains the only personal attribution.
- The 0.4.0 portability pass makes this sanitized directory the versioned release source for both operating systems. Linux x86_64 packages contain only publisher-verified PowerShell Core, MGI-Mind and codebase-memory binaries; the build scans this tree again before packaging. Control Center 0.6.0 and Setup 0.4.0 share code across Windows/Linux while keeping platform registration separate.

## Known limitations / manual review before showing people

- Core workspace scripts run under Windows PowerShell 5.1+ and bundled PowerShell Core on Linux. Task Scheduler and systemd/XDG registration remain separate platform adapters by design. macOS is not a packaged target.
- The bundled skills' inner texts are third-party content — skim them once yourself before distributing to a team, and re-verify licenses if you plan to redistribute publicly rather than internally.
- Placeholder-driven docs read as a template until Step 1 of TEMPLATE_SETUP is done; that is intended.
- The Windows 0.4.5 and Linux 0.4.1 beta packages are not code-signed. Recipients should verify published SHA-256 values; Windows may show SmartScreen and Linux users should install only the matching local `.deb`/AppImage artifact.
