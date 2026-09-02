# Skills Manifest

Bundled and recommended agent skills for this workspace. Routing rules live in `70_Resources/Skill_Router_Matrix.md`; this manifest is the inventory.

How to activate bundled skills: copy the skill folders into the location your agent tooling reads project-local skills from (commonly `.agents/skills/` or `.claude/skills/` in the workspace root), then restart the agent session. They are shipped under `template-skills/` so that YOU decide which agent runtime gets them.

## Bundled skills

### diagnosing-bugs
- **Purpose**: disciplined diagnosis loop for hard bugs and performance regressions (reproduce -> hypothesize -> verify).
- **When to use**: anything broken, throwing, failing, slow, or producing wrong numbers.
- **Dependencies**: none (optional helper shell script template inside).
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Bug, crash, wrong numbers, slowness".

### domain-modeling
- **Purpose**: build and sharpen the project's domain model, ubiquitous language and ADRs.
- **When to use**: disputed terminology, business-rule ambiguity, recording architectural decisions.
- **Dependencies**: none.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Domain methodology, terms, disputed business logic".

### fastapi-python
- **Purpose**: FastAPI/Python backend best practices (async, Pydantic, SQLAlchemy patterns).
- **When to use**: backend API work on a FastAPI stack. Swap for your stack's equivalent if you are not on FastAPI.
- **Dependencies**: a FastAPI project to apply it to.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Backend API, async, DB".

### find-skills
- **Purpose**: discover and install new agent skills on demand.
- **When to use**: "is there a skill for X?", extending capabilities.
- **Dependencies**: network access to skill registries at install time.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "New skill discovery/install".

### frontend-design
- **Purpose**: intentional, non-templated visual design guidance (aesthetic direction, typography).
- **When to use**: building new UI or reshaping existing UI.
- **Dependencies**: none.
- **Status**: bundled.
- **Privacy/license**: **Apache-2.0 — `LICENSE.txt` ships inside the skill folder and must stay with it.**
- **Router mapping**: "UI/UX, dashboards, frontend polish".

### graphify
- **Purpose**: build a structural AST index (classes, functions, imports, call graph) of source code.
- **When to use**: exploring unfamiliar codebases; before broad code searches.
- **Dependencies**: **requires the `graphify-ts` CLI** (installed separately).
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Source-code structure exploration". Not for the note graph.

### grill-me
- **Purpose**: a relentless interview to stress-test a plan or design.
- **When to use**: only when the user explicitly invokes it (the skill is a stub with `disable-model-invocation: true` — agents cannot trigger it themselves; the protocol's challenge checkpoint covers the automatic case).
- **Dependencies**: an agent runtime that supports user-invoked skill sessions.
- **Status**: bundled (tiny stub), with this honest limitation note.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "AI workflow..." row (explicit user request only).

### handoff
- **Purpose**: compact the current conversation into a handoff document for another agent.
- **When to use**: passing work between agents/tools; ending a session mid-task.
- **Dependencies**: none.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Handoff to another agent/tool".

### humanizer
- **Purpose**: replace AI-like slogans, metaphors, invented labels and inflated copy with direct user-facing language.
- **When to use**: every interface, installer, notification, help page, release note and external document.
- **Dependencies**: none.
- **Status**: bundled.
- **Privacy/license**: generic template-authored content, MIT.
- **Router mapping**: "UI/UX, dashboards, frontend polish" and any user-facing writing.

### json-canvas
- **Purpose**: create/edit JSON Canvas (`.canvas`) files with validation (unique IDs, edge references).
- **When to use**: knowledge maps, flowcharts, Obsidian canvases.
- **Dependencies**: none.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Obsidian canvas / knowledge maps".

### obsidian-markdown
- **Purpose**: create and edit Obsidian-flavored Markdown notes: wikilinks, properties/frontmatter, embeds and callouts.
- **When to use**: creating or editing workspace `.md` notes, especially connected notes that must render well in Obsidian.
- **Dependencies**: none.
- **Status**: bundled.
- **Privacy/license**: MIT upstream (`kepano/obsidian-skills`); `LICENSE.txt` ships inside the skill folder and must stay with it.
- **Router mapping**: "Obsidian markdown notes".

### playwright
- **Purpose**: modern E2E testing with cross-browser automation.
- **When to use**: E2E checks of web apps and demo scenarios.
- **Dependencies**: **requires Playwright** installed in the project.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "React/frontend performance or structure" (verification), "UI/UX" checks.

### tdd
- **Purpose**: test-driven development, red/green/refactor, integration-test guidance.
- **When to use**: features/fixes where tests can define behavior first.
- **Dependencies**: a test runner in the project.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Backend API, async, DB" and any testable implementation work.

### to-issues
- **Purpose**: slice a plan/spec/PRD into independently shippable vertical issues.
- **When to use**: after requirements are agreed; when a tracker exists.
- **Dependencies**: an issue tracker (or the workspace Task_Log).
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "Issue decomposition".

### to-prd
- **Purpose**: synthesize the current conversation into a PRD.
- **When to use**: after requirement discussions converge.
- **Dependencies**: none.
- **Status**: bundled.
- **Privacy/license**: generic content, no license file included by upstream.
- **Router mapping**: "PRD or requirements packaging".

## Install-only recommendations (not bundled)

### ui-ux-pro-max
- **Purpose**: large UI/UX knowledge base — 50+ styles, 161 palettes, 57 font pairs, UX guidelines, chart types across 10 stacks; Python search scripts over CSV data.
- **When to use**: making dashboards/charts expressive without a generic AI look; apply your project's design constraints on top.
- **Dependencies**: Python for its search scripts.
- **Why install-only**: external distribution (search for `ui-ux-pro-max` via `find-skills`; a widely-installed public skill); no license file ships in the copy we had, so redistribute-by-template is not clean. Install fresh from its source.
- **Privacy note**: prior local security review of the distribution found no network/shell/eval behavior in its scripts; re-verify on install.
- **Router mapping**: "UI/UX, dashboards, frontend polish".

### vercel-react-best-practices
- **Purpose**: ~70 React/Next.js performance rules from Vercel Engineering, prioritized by impact.
- **When to use**: writing, reviewing or refactoring React/Next code.
- **Dependencies**: none.
- **Why install-only**: MIT-licensed (bundling would be legal) but actively maintained upstream — install fresh instead of carrying a stale copy.
- **Router mapping**: "React/frontend performance or structure".

### codebase-memory-mcp (code intelligence layer)
- **Purpose**: MCP server that builds a persistent knowledge graph of a codebase — call graph, imports, HTTP routes, impact analysis, dead code, architecture overview. 158 languages (tree-sitter) + lightweight type resolution for 10 major ones; local SQLite storage; MIT; mature (25k+ stars, thousands of tests).
- **When to use**: "what calls this function", "what breaks if I change X", "where is dead code", "how is this repo structured" — a code X-ray, NOT a memory for notes and NOT a source of truth.
- **Dependencies**: single static binary; per-repo indexing.
- **Why install-only**: its installer auto-configures MCP entries, **instruction files and pre-tool hooks** for up to 11 agents — that rewrites the entry points this workspace carefully controls. Install only after reading the install script, then diff your entry points and re-run `tools/check_ai_os_readiness.ps1`.
- **Safest path (verified against its README)**: skip the installer entirely — download the signed release binary manually, register it yourself project-scoped in `.mcp.json`, keep auto-index off. All 14 MCP tools work without the installer's hooks, and nothing touches your entry points; full rollback = remove the `.mcp.json` entry, the binary folder and its cache dir.
- **Safety notes**: keep auto-index off until trusted; add a `.cbmignore` before indexing anything sensitive; its ADR feature must not replace [[40_Decisions/Decision_Log]]; the team-shared graph artifact (compressed DB in the repo) needs a security review before enabling; pilot on a non-sensitive repo copy first and compare against `graphify`/grep on 5 tasks (architecture overview, call trace, impact, dead code, cross-service links).
- **Router mapping**: "Source-code structure exploration".

## Manual review needed

- None at template creation time. All bundled skills were scanned for personal/project context and absolute paths before inclusion; the only matches were false positives where a short name fragment happened to occur inside an ordinary English word (such as "categories"). Use word boundaries when re-scanning.

## Rules

- A skill enters this manifest only together with a router mapping.
- A skill with unclear license or embedded personal/project context is never bundled — install-only or excluded.
- Re-run a quick content scan on any new skill before adding it here.
