---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

# Canonical skill bridge

The shared implementation for this skill lives at `.agents/skills/handoff/SKILL.md`.
When this skill applies, read that canonical file completely and follow it. Resolve its relative references from `.agents/skills/handoff/`. Do not maintain a second copy under `.claude/skills`.
