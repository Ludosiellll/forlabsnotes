---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - ai/context
  - ai/memory
  - workflow
  - project/context
---

# AI Operating System

## Summary

The goal of this system is to turn work with Claude, Codex, Cursor and other agents from scattered chats into an accumulating working loop: context is found, verified, used, and returned to the knowledge base.

Main principle: **the workspace vault remains the source of truth; memory/search tools help find context but do not replace verifiable notes, code and primary documents.**

## Architecture

```text
Chats, voice, documents, code, meetings
        v
Capture: transcript, summary, tasks, decisions
        v
Workspace vault: canonical markdown source of truth
        v
Retrieval layer: semantic memory / rg / structure index / search
        v
Execution layer: Claude / Codex / Cursor + skills
        v
Verification: code, tests, screenshots, source docs, user feedback
        v
Context capture back into the workspace
```

## Layer Roles

| Layer | Role | What goes there | What must not happen |
| --- | --- | --- | --- |
| Workspace vault | Main base of truth | decisions, meetings, current focus, architecture, tasks, people, terms | storing secrets, raw guesses, junk logs |
| Product repo | Truth about implementation | code, tests, configs, README, migrations | treating notes as higher than code |
| Memory layer | Fast recall and semantic search | short facts, session summaries, procedure memories, markdown index | making it the only source of truth |
| Skills | Specialized working modes | instructions for design, TDD, bug diagnosis, handoff | using a skill instead of reading the project |
| Meeting/audio capture | Capturing calls | transcript, summary, decisions, tasks, people, risks | keeping private irrelevant details |

## Default Agent Loop

1. **Recall** — find relevant context via search, indexes, or the memory layer.
2. **Read** — open canonical notes/code/docs, not just a snippet.
3. **Challenge** — check for conflict with code, primary documents, security, or the current task.
4. **Act** — do the work as close to existing project patterns as possible.
5. **Verify** — run tests, build, visual check, or another suitable feedback loop.
6. **Capture** — write durable knowledge back into the right notes per [[70_Resources/Agent_Context_Automation]] and [[70_Resources/AI_Context_Quality_Guide]].

The practical shared protocol is [[70_Resources/Agent_Workflow_Protocol]].

## Authority Ladder

If sources conflict:

1. Live code, tests, actual service state, primary documents.
2. Current workspace notes with dates and links.
3. Memory layer / summaries as navigation hints.
4. The current chat and unrecorded guesses.

Memory can suggest where to look, but cannot prove a fact by itself.

## User Layer

For tasks where working style, design, communication, risk or tool choice matters, agents must consider [[01_Index/User_Working_Profile]]. It is a working preference profile, not a biography — it exists so agents stop re-explaining the obvious and hit the right level of directness and detail.

## Memory Layer Position

A semantic memory tool is an optional retrieval layer on top of the vault. Setup and commands: [[70_Resources/MGI_Mind_Local_Setup_Template]].

Until decided otherwise:

- do not treat the memory store as canonical;
- do not write secrets into it;
- for mostly non-English content, disable an English-tuned reranker or replace it with a multilingual one;
- import markdown as an index, not as a replacement for the vault.

## Quality Metrics

The system works well if:

- a new agent enters the project in minutes, not hours;
- the user does not repeat the same context across tools;
- decisions can be reconstructed from links and dates;
- important risks surface before a mistake, not after;
- the context does not become a dump of long logs;
- external texts keep the internal/external role boundary intact.

## Phases

1. **Phase 0** — vault as source of truth; protocol, capture rules, user profile in place. (This template gives you Phase 0 out of the box.)
2. **Phase 1 — retrieval layer**: install a local memory tool, import the vault, verify search quality in your language, keep it only if recall beats plain grep + indexes.
3. **Phase 2 — meeting capture**: transcription pipeline; template-driven extraction of summary/decisions/tasks/risks.
4. **Phase 3 — procedure memory**: procedure notes for repeated workflows; update each after every real run.
5. **Phase 4 — maintenance**: weekly compaction of Current_Focus and Task_Log; decisions moved to the Decision Log; oversized notes split.

## Links

- [[01_Index/AI_Context]]
- [[01_Index/User_Working_Profile]]
- [[70_Resources/Agent_Workflow_Protocol]]
- [[70_Resources/Agent_Context_Automation]]
- [[70_Resources/AI_Context_Quality_Guide]]
- [[70_Resources/MGI_Mind_Local_Setup_Template]]
- [[70_Resources/Agent_Skills_Roadmap]]
