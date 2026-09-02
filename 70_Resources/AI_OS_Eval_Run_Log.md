---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - ai/context
  - ai/evals
---

# AI OS Eval Run Log

Record every eval run here. A suite that is never executed is decoration; the readiness check warns until at least one recorded pass exists.

## Runs

| Date | Eval ID | Agent / model | Result (Pass/Partial/Fail) | Notes |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | E01-context-recall | (agent/model) | (result) | (what it opened, what it missed) |

## Rules

- Run evals in fresh sessions; a warmed-up conversation is not a clean test.
- On Fail: fix the router/protocol/entry points, then re-run the same eval and log both entries.
- Re-run at least E01/E05/E13 after any change to entry points, protocol or router.

## Links

- [[70_Resources/AI_OS_Eval_Prompt_Suite]]
- [[70_Resources/Skill_Router_Matrix]]
