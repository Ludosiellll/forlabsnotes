---
type: person
status: active
updated: 2026-09-02
tags:
  - people
  - ai/context
  - preferences
---

# User Working Profile

## Summary

Денис operates the AI agents in this workspace. This note records only working preferences and stable interaction style, so agents can help without re-learning it every session. Keep it honest and short; it is not a biography.

## Working Preferences

Replace the examples with what is true for you:

- Prefers direct, pragmatic answers without filler and without artificial agreement.
- For technically complex topics: first explain in plain language (what it means, why it matters, what happens if it breaks), then give commands/details.
- Expects the agent to argue against bad decisions once, to the point, with reasons.
- Values speed, but not at the cost of verifying critical facts, security, or result quality.
- Prefers the agent to take reasonable steps autonomously rather than stopping at suggestions.

## Design Preferences (if the project has UI)

- Example: dislikes generic AI-looking UI — dark template dashboards, gratuitous gradients, glassmorphism, decorative effects without meaning.
- Example: data displays must carry honest labels: real vs demo data, source, verification status.

## AI Tool Preferences

- Which agents are in use (e.g. Claude Code, Codex, Cursor) and which one is primary.
- Cost/token sensitivity: when heavy models are acceptable.
- Preferred verification style: tests, screenshots, smoke checks.

## Risk Sensitivities

- Secrets, API keys, passwords and customer data must never be saved in notes or public places.
- Note any project-specific boundaries (e.g. public demos require hardened auth; internal vs external communication roles — see [[01_Index/People]]).

## How Agents Should Work With Денис

- Start with the concrete conclusion, then the reasoning and the next step.
- When choosing between options, give a recommendation, not a neutral list.
- If the task is feasible, carry it to the end: changes, verification, context update.
- If data is missing, first look in the workspace/code/files; ask only when no safe hypothesis exists.
- After a major task, update the workspace per [[70_Resources/Agent_Context_Automation]] and [[70_Resources/AI_Context_Quality_Guide]].

## Links

- [[01_Index/People]]
- [[70_Resources/AI_Operating_System]]
- [[70_Resources/Agent_Context_Automation]]
