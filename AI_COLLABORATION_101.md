# AI Collaboration 101

How to actually get value out of AI agents in this workspace. Ten habits, each mapped to something this template already enforces. If you are new to working with agents, read this before your first session.

## 1. Don't re-type context — point at it

The single biggest waste in AI work is re-explaining the project in every chat. That is what this workspace kills. Fill the notes once (TEMPLATE_SETUP step 1 — your agent does it during install); after that your prompt is "read the workspace and do X", not three paragraphs of background.

**Bad ask:** "We have a CRM for flower shops, there's a backend in Python, and somewhere in the sync code a bug..."
**Good ask:** "The nightly sync produced wrong totals. Diagnose it. Start from `30_Tech/Codebase_Map.md`."

## 2. One task, one goal, one verification

Agents do best with a clear finish line. Say what "done" means: a passing test, a screenshot, a green check, a note updated.

**Bad:** "Improve the dashboard."
**Good:** "Make the totals tile show a per-week trend. Done = build passes + desktop and 375px screenshots + `Codebase_Map.md` updated."

## 3. Expect pushback — you configured it

This workspace obliges agents to disagree once, with reasons, when you propose something that conflicts with code, decisions or security (the Non-Yes-Man rule in the protocol). If an agent just agrees with everything, that is a failure — run eval E13 and tighten the entry points.

## 4. Never paste secrets

Not into chat, not into notes, not into the memory layer. Agents here are instructed to refuse to store them (eval E05 tests this). Secrets live in environment variables and secret managers. If a key leaks into a chat — rotate it; deleting the message does not un-leak it.

## 5. "How did you verify that?"

The most useful five words in AI collaboration. Agents in this workspace must run a self-audit before finishing substantial tasks (verification, capture, residual risk). If an answer comes without evidence — tests, command output, an opened file — ask for the evidence, not for confidence.

## 6. Memory is a hint, not a fact

Any memory layer (including the optional semantic index here) is navigation. When an agent says "I remember that...", the correct next step is: open the note or the code. The authority ladder is fixed: **code > notes > memory > chat**. Evals E01, E13, E15 test exactly this.

## 7. End sessions with capture

A session that changed something must leave a trace: `Current_Focus.md` updated, a task ticked, a decision recorded, a gotcha written down. Agents are instructed to do this automatically; check the diff. Knowledge that lives only in a closed chat is knowledge you paid for twice.

## 8. When an agent misbehaves, fix the system, not the mood

An agent ignored the freeze? Answered from memory? Installed five tools nobody asked for? Do not just correct it in chat — that fix evaporates. Update the router/protocol/entry points, then re-run the matching eval in a fresh session. That is the difference between prompting and operating a system.

## 9. Right-size the tooling

More tools is not more power. Every skill, memory framework or automation must have: a role, a router entry, and a way to verify it earns its place (eval E10 and E14 exist because this failure mode is universal). One tool piloted properly beats five installed "to be safe".

## 10. Weekly hygiene beats heroic cleanup

Fifteen minutes a week: compact the focus note, close done tasks, run the readiness check, sync the memory index. The health check will nag you about staleness — treat its warnings as todo items, not decoration.

## Mini-glossary

| Term | Meaning here |
| --- | --- |
| Workspace / vault | This folder — the canonical markdown source of truth |
| Entry point | The file an agent auto-loads (`CLAUDE.md`, `AGENTS.md`, Cursor rule) |
| Protocol | The shared agent loop: recall -> read -> challenge -> act -> verify -> capture |
| Skill | A packaged instruction set an agent can apply to a task type |
| Procedure note | A project-specific runbook that beats a generic skill for repeated work |
| Router | The matrix mapping task types to context + skill + verification |
| Eval | A control prompt that tests real agent behavior in a fresh session |
| Health / readiness check | Scripts verifying the workspace and its wiring |
| Memory layer | Optional semantic index over the notes — navigation, never truth |

## Anti-patterns to unlearn

- **Chat as storage** — decisions living in scroll-back die in scroll-back.
- **The giant vague prompt** — ten goals in one message means zero done well.
- **Blind copy-paste** — agent output you did not verify is a liability with your name on it.
- **Tool hoarding** — see habit 9.
- **Trusting "I remember"** — see habit 6.

## Links

- [START_HERE.md](START_HERE.md)
- [TEMPLATE_USAGE_DEMO.md](TEMPLATE_USAGE_DEMO.md)
- [70_Resources/Agent_Workflow_Protocol.md](70_Resources/Agent_Workflow_Protocol.md)
- [70_Resources/AI_OS_Eval_Prompt_Suite.md](70_Resources/AI_OS_Eval_Prompt_Suite.md)
