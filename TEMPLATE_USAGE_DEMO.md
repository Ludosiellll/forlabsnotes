# Usage Demo: a day with the workspace

A realistic walkthrough of how this workspace behaves once set up. Agent lines are illustrative; the point is the *shape* of the interaction.

## Session 1 — cold start, new agent

**You:** "What is this project and what should we do next?"

**A well-behaved agent:**
1. Reads `CLAUDE.md`/`AGENTS.md` -> `01_Index/AI_Context.md` -> `10_Project/Current_Focus.md`.
2. Answers from the notes, with links, and names the current blockers — no invention.
3. If asked about something older or broader, searches the memory layer first, then **opens the cited note** before answering.

That is eval E01 passing in the wild.

## Session 2 — a bug report

**You:** "After the last sync the numbers look wrong."

**Expected behavior (router row: bug/wrong numbers):**
1. Agent picks the `diagnosing-bugs` skill + `Procedure_Bug_Diagnosis_Loop`.
2. Reproduces before fixing; finds authority in code/tests, not in notes.
3. Fixes narrowly, re-runs the failing check, then **captures** the gotcha into `30_Tech/Codebase_Map.md` and any follow-up into `60_Tasks/Task_Log.md`.

## Session 3 — someone tries a shortcut

**You (or a teammate):** "Let's just treat the memory index as the source of truth, it's faster."

**Expected behavior (eval E13):** the agent declines once, with reasons — memory is a navigation layer; markdown/code are truth — and points to the decision in the workflow protocol. If you insist, it records the risk and follows your explicit decision.

## Session 4 — end of task, capture

After any substantive task the agent runs its self-audit (from the protocol):

- context used, skill/procedure used, verification done, notes updated, memory re-synced, residual risk stated.

You will see the diff: `Current_Focus.md` updated, a decision note added, a task ticked. That diff **is** the system working.

## Weekly hygiene (15 minutes, human or agent)

1. Compact `10_Project/Current_Focus.md`; move finished stories to the roadmap/decision notes.
2. Close done items in `60_Tasks/Task_Log.md`.
3. Run `tools/check_ai_os_readiness.ps1` (or let the scheduled task do it) and glance at `.local/readiness-check.log`.
4. If notes changed a lot, run `tools/sync_mgimind.ps1` so the memory index stays fresh — the health check will warn you if you forget.

## Monthly confidence pass

- Re-run 3-5 prompts from `70_Resources/AI_OS_Eval_Prompt_Suite.md` in fresh sessions; log results in `AI_OS_Eval_Run_Log.md`.
- Read the last few entries of `.local/health-check.log` — a system that is only ever checked manually is a system that decays.
