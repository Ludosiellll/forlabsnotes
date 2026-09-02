# Pitch: an AI Project Workspace, not another chat

## The problem

Everyone on the team already uses AI agents. And every session starts from zero: the agent does not know the project, invents context, agrees with everything, and its work evaporates when the chat ends. Knowledge lives in people's heads and scattered chats; onboarding takes days; the same mistakes repeat.

## The proposal

One workspace folder per project that acts as the **operating system for AI work**:

1. **Source of truth in markdown.** Decisions, current focus, domain terms, architecture, tasks, meetings — dated, linked notes. Code beats notes; notes beat memory; chat beats nothing.
2. **One protocol for every agent.** Claude, Codex and Cursor load entry points that converge on the same loop: *recall -> read canonical sources -> challenge -> act -> verify -> capture*. An agent that finishes a task updates the workspace, so the next session starts warm.
3. **Non-yes-man by contract.** The protocol obliges agents to push back — once, with concrete reasons — when a request conflicts with code, prior decisions, security or a simpler alternative.
4. **Routing instead of vibes.** A skill router matrix maps task types (bug, UI, deploy, domain dispute, secrets, handoff...) to the right skill, context and verification target.
5. **Trust, but verify.** An eval prompt suite tests real agent behavior (does it check sources? refuse to store secrets? respect a code freeze?). Health and readiness scripts verify the workspace itself and can run on a daily schedule with logs.
6. **Optional memory layer.** A local semantic index over the notes for fast recall — explicitly *not* the source of truth, with sync discipline and staleness checks built in.

## What the team gets

- **Onboarding in minutes**: a new person (or agent) reads 5 notes and is productive.
- **No repeated context**: stop re-explaining the project to every tool.
- **Auditable decisions**: every "why did we do X?" has a dated answer with links.
- **Safer AI use**: secrets policy, role boundaries, restriction gates and behavior evals are part of the system, not goodwill.
- **Compounding**: every completed task leaves the workspace smarter; nothing resets.

## What it costs

- A 2–5 minute native Setup flow per project on Windows or Linux; the manual template remains an auditable fallback.
- A weekly 15-minute hygiene pass (compact focus note, close tasks, run checks).
- Discipline: decisions and durable facts go into the workspace, not just chat.

## Proof it works

This template is extracted from a live workspace that ran a real product project. In practice it caught, among other things: an agent-invisible stale memory index, a blocking bug in the sync watcher, false-OK health checks, and secret-pattern leaks in notes — all via its own checks and audits rather than luck.

## Ask

Pilot it on one project for two weeks: install AI OS on Windows x64 or Linux x86_64, create an isolated workspace, use it for real tasks, and run the eval pack at the start and the end. Compare onboarding time, repeated-context pain and decision traceability against any current project.
