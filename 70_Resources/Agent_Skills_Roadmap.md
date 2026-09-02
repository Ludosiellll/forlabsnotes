---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - ai/skills
  - workflow
  - project/context
---

# Agent Skills Roadmap

## Summary

This workspace uses a project-local set of agent skills. The goal is not quantity but a stable cycle:

```text
context -> spec/PRD -> issues -> code -> tests -> debugging -> review -> context update
```

The authoritative list of bundled skills with purpose, dependencies and licenses is `template-skills/SKILLS_MANIFEST.md`. Routing rules are in [[70_Resources/Skill_Router_Matrix]].

## Bundled now

- `find-skills` — discover and install new skills.
- `grill-me` — stress-test plans and specs (invocation-gated stub; see manifest).
- `json-canvas` — edit Obsidian `.canvas` maps.
- `obsidian-markdown` - edit Obsidian `.md` notes with wikilinks, properties/frontmatter, embeds and callouts.
- `graphify` — build an AST/structure index of real code (requires its CLI).
- `fastapi-python` — FastAPI/Python backend patterns (swap for your stack).
- `frontend-design` — intentional, non-templated UI design (Apache-2.0, keep its LICENSE.txt).
- `playwright` — E2E and browser testing.
- `tdd` — test-first development, red/green/refactor.
- `diagnosing-bugs` — reproduce, hypothesize, fix through a feedback loop.
- `to-prd` — turn agreed context into a PRD.
- `to-issues` — slice a PRD/spec into vertical issues.
- `domain-modeling` — sharpen the domain model, terms and boundaries.
- `handoff` — hand work to another agent.
- `humanizer` — keep interface and external copy direct, consistent and free of AI-like slogans.

## Install-only recommendations

- `ui-ux-pro-max` — external design-intelligence skill (styles, palettes, typography, UX checklists). Install from its own distribution; apply your project's design constraints on top so you do not get a generic AI look.
- `vercel-react-best-practices` — React/Next performance rules from Vercel (MIT). Install fresh from upstream rather than carrying a stale copy.
- `codebase-memory-mcp` — optional code-intelligence layer: a knowledge graph over the codebase (call graph, impact analysis, dead code, architecture). Pilot on a non-sensitive repo first; its installer rewrites agent entry points, so diff them and re-run the readiness check after install. See the manifest entry for safety notes.

## When to use

- After a spec is agreed: `to-prd`.
- When a tracker or task list appears: `to-issues`.
- Implementing backend/calculations/integrations: `tdd`.
- Breakage, mismatched numbers, unstable integrations: `diagnosing-bugs`.
- Disputes about domain terms: `domain-modeling` + update [[01_Index/Glossary]] / [[20_Domain/Domain_Map]].
- Creating or editing workspace notes: `obsidian-markdown`.
- Before passing work between agents: `handoff` + capture durable context.

## Add later (when relevant)

- Code-review / architecture-review skills — once a real product repo exists.
- CI/deploy skills — once CI/CD is confirmed.
- Database best-practice skills — once the storage layer is chosen.

Do not install architecture skills before code exists: they will produce abstract advice.

## Rules

- Skills do not replace workspace context: important decisions go to [[40_Decisions/Decision_Log]].
- Never store tokens, passwords, API keys, customer data or sensitive exports in skills, notes or prompts.
- After installing new skills, restart the agent session so it picks up the list.
- A new skill is incomplete until [[70_Resources/Skill_Router_Matrix]] says when to use it.

## Links

- [[01_Index/AI_Context]]
- [[30_Tech/Tech_Map]]
- [[60_Tasks/Task_Log]]
- [[70_Resources/Skill_Router_Matrix]]
