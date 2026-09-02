---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - workflow/procedure
  - debugging
  - engineering
---

# Procedure: Bug Diagnosis Loop

## Summary

Procedure for bugs, wrong numbers, broken integrations, performance regressions and strange UI/API behavior. The goal is not "try a fix" but: get a reproducible signal fast, find the cause, verify the fix, capture the lesson.

If the `diagnosing-bugs` skill is available, use it for hard bugs.

## Loop

1. **State the symptom**: what exactly is broken, where it shows, expected behavior.
2. **Reproduce**: minimal path, command, endpoint, viewport or user scenario.
3. **Find authority**: code/tests/primary documents beat notes and memory.
4. **Isolate**: narrow to a module, function, endpoint, component or CSS rule.
5. **Create/extend a failing check**: test, build, smoke command, DOM assertion or manual checklist.
6. **Fix narrowly**: change the nearest causal spot; no unrelated refactoring.
7. **Verify**: re-run the same failing check plus a minimal regression set.
8. **Capture**: record the durable fact if the bug teaches a future lesson.

## Before Editing

Check:

- are there uncommitted user changes;
- which repository and branch are active;
- are there secrets/data that must not appear in logs;
- is the symptom actually caused by stale notes.

## Evidence To Collect

- Launch command or endpoint.
- Minimal input.
- Expected vs actual.
- Last known working version, if any.
- Logs without secrets.
- Screenshot/DOM measurements for UI.
- A test reproducing the problem, when reasonable.

## Fix Rules

- Do not rewrite a whole layer when the cause is local.
- Do not fix "by eye" when a verifiable signal is available.
- Do not hide an error with try/catch/log-only if it means data loss.
- Do not change business methodology without a decision note.
- If notes conflict with code, say so and update the notes after verification.

## Verification Sets (adapt to your stack)

Backend:

```powershell
cd none yet\backend
# your test command, e.g.:
# .\.venv\Scripts\python -m pytest
```

Frontend:

```powershell
cd none yet\frontend
# your build command, e.g.:
# npm run build
```

Integration:

- source connection check;
- one sync path at a time;
- sanity-check values, units and currencies;
- no secrets in logs/notes.

## Capture Rules

Update:

- [[30_Tech/Codebase_Map]] for entry points, gotchas, commands, verified bug patterns;
- [[60_Tasks/Task_Log]] for follow-up or unresolved risk;
- [[40_Decisions/Decision_Log]] if the fix changes methodology/architecture;
- the relevant procedure note if the diagnosis changes a repeated checklist.

## Links

- [[70_Resources/Agent_Workflow_Protocol]]
- [[70_Resources/AI_Context_Quality_Guide]]
