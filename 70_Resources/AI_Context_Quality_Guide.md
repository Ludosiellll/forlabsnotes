---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - ai/context
  - workflow/quality
  - project/context
---

# AI Context Quality Guide

## Summary

Defines what counts as quality context for agents. Goal: keep what helps future work; do not pollute the workspace with temporary logs, guesses and sensitive data.

## Capture Types

| Type | Where | Example |
| --- | --- | --- |
| Current work | [[10_Project/Current_Focus]] | what is built now, what blocks the next step |
| Task / follow-up | [[60_Tasks/Task_Log]] | "rotate the exposed API key", "confirm data source X" |
| Decision | [[40_Decisions/Decision_Log]] + ADR | "this vault stays the canonical source of truth" |
| Architecture / code | [[30_Tech/Codebase_Map]] | endpoints, commands, gotchas, module structure |
| Domain term | [[01_Index/Glossary]] | a business definition agreed with the client |
| Person / responsibility | [[01_Index/People]] | who makes product or technical decisions |
| Meeting | [[50_Meetings/Meeting_Log]] + note | summary, agreements, questions, tasks |
| Preference | [[01_Index/User_Working_Profile]] | stable working preferences of Денис |
| Procedure | `70_Resources/Procedure_*.md` | a verified sequence of commands/checks |

## Capture Rules

- Write short, but concretely enough that the next agent can act.
- Add date, source and status if the fact can go stale.
- Separate verified facts, hypotheses, open questions and decisions.
- Preserve wikilinks.
- If a note becomes central, add it to [[01_Index/Project_Map]].

## Do Not Capture

- Secrets, tokens, passwords, API keys, cookies.
- Private customer data and unnecessary sensitive exports.
- Full raw command logs when a summary is enough.
- Temporary agent reasoning that future work does not need.
- Unverified guesses presented as facts.
- Unsourced predictions about real people's reactions, preferences or decisions: characterizing a person without evidence from meetings or recorded decisions is projection, not context.
- External-facing texts that leak internal roles (see [[01_Index/People]]).

## Good Context Shape

Bad:

```text
Fixed the chart, something about SVG probably.
```

Good:

```text
YYYY-MM-DD: fixed inline-SVG height in the main chart: width:100% + viewBox produced a huge intrinsic height. Solution: measure the container via ResizeObserver, viewBox = actual width x fixed height. Check sizes via clientWidth/clientHeight, not getBoundingClientRect(), when a transform is active.
```

## Memory Layer Rules

If a semantic memory layer is used:

- write short facts/procedures there, but keep the canonical markdown link in the workspace;
- on conflict, markdown/code beat memory snippets;
- never make the memory store the only place a decision lives;
- for non-English content, verify reranker quality before trusting default ranking.

## Weekly Maintenance

Once a week or after a major stage:

1. Compact [[10_Project/Current_Focus]]: move implemented items to roadmap/codebase/decision notes.
2. Close finished tasks in [[60_Tasks/Task_Log]].
3. Pull decisions out of long working notes into [[40_Decisions/Decision_Log]].
4. Check that no secrets or excess sensitive details crept in.
5. Update procedure notes if a real deploy, sync, visual QA or bug diagnosis happened.
6. Update [[01_Index/AI_Context]] if the main reading path changed.

## Links

- [[70_Resources/AI_Operating_System]]
- [[70_Resources/Agent_Workflow_Protocol]]
- [[70_Resources/Agent_Context_Automation]]
- [[01_Index/AI_Context]]
- [[01_Index/Project_Map]]
