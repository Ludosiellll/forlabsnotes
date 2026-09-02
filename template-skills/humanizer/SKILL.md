---
name: humanizer
description: Review user-facing writing and replace AI-like slogans, invented terminology, vague claims, and inflated phrasing with direct language that fits the product.
license: MIT
compatibility: any-agent
---

# Humanizer

Use this skill for interface labels, buttons, notifications, installer copy, help text, release notes, and external documents.

## Method

1. Preserve the meaning and every concrete instruction.
2. Prefer familiar words and short sentences.
3. Name the action directly: `Create project`, `Open folder`, `Run check`.
4. Use one language per phrase except for established product names and technical identifiers.
5. Remove slogans, metaphors, promotional claims, fake urgency, and invented operational terms.
6. Keep the user's voice when editing personal text. Keep technical text neutral.
7. Read the result in its UI container. Shorten it if a label, button, status, or notification wraps unnecessarily.

## Reject

- Vague labels such as `Telemetry`, `Command center`, `Fast capture`, or `System state` when a plain task name exists.
- Claims such as "the environment remembers your work" when the product actually stores notes and an index.
- Mixed-language labels when a clear local-language term exists.
- A new term used only to make an ordinary feature sound more impressive.

## Verification

- A first-time user can predict what each action does.
- The same feature has the same name in the installer, app, notifications, and help.
- No important limitation or safety detail was removed while shortening the text.
