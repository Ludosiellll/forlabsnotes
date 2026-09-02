---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - workflow/procedure
  - agent/coordination
  - ai/context
---

# Procedure: Multi-Agent Review

## Summary

For tasks where one pair of eyes is not enough: architecture decisions, deploys touching real data, calculation methodology, security-sensitive changes, large refactors, external-facing texts with a role boundary. The point is independent criticism *before* a decision becomes a fact.

## When it is mandatory

- The decision will land in [[40_Decisions/Decision_Log]] and is expensive to roll back.
- A deploy or change involves real business data or secrets.
- Disputed methodology (what counts as X in this business).
- External text where the internal/external role boundary matters (see [[01_Index/People]]).

## Roles

| Role | Job | Who (manual mode) |
| --- | --- | --- |
| Builder | Does the work; produces the plan/diff/draft | The main working session |
| Reviewer | Hunts bugs, security holes, conflicts with code and prior decisions; findings with file/line | A **fresh** session, ideally a different agent/tool |
| Product critic | Checks business sense, role boundary, "is this even needed" | A fresh session or the human |
| Archivist | Records the decision, findings and follow-ups; syncs memory | Any session, per [[70_Resources/Agent_Workflow_Protocol]] |

Minimum for "reviewed": Builder + an independent Reviewer. Product critic — for decisions with external/business impact. Archivist — always.

## The loop (manual mode)

1. Builder finishes and prepares a handoff (the `handoff` skill): status, files, commands, assumptions, known risks.
2. Reviewer starts **in a fresh session** — not inside the Builder's warmed-up context, or it inherits the same blind spots. Reads canonical notes + handoff; produces findings: file/line, severity, how verified.
3. Builder answers every finding: fixed, or rejected with a reason. One round of dispute max — after that the human decides.
4. Product critic (when required) looks at the result through the stakeholder's eyes.
5. Archivist: decision -> [[40_Decisions/Decision_Log]] (+ADR), lessons -> [[30_Tech/Codebase_Map]]/procedures, follow-ups -> [[60_Tasks/Task_Log]], memory sync.

## Verification

- Findings carry file/line and a way to verify — not "looks fine overall".
- The outcome is recorded: what was accepted, what was rejected and why.
- Keep a count of real uses; a review procedure that exists only on paper is decoration.

## Links

- [[70_Resources/Agent_Workflow_Protocol]]
- [[40_Decisions/Decision_Log]]
- [[60_Tasks/Task_Log]]
