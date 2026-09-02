---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - workflow/procedure
  - meetings
  - ai/context
---

# Procedure: Meeting And Voice Capture

## Summary

Turn calls, voice notes and meetings into durable workspace context without leaking noise or sensitive fragments into the knowledge base. The flow: record -> transcribe locally -> clean -> extract -> link -> sync.

## Privacy Gate (before anything else)

- Get consent for recording where required; company calls may have rules.
- Raw transcripts often contain secrets, personal remarks and misheard names. They never go into the memory-imported folders or into git (the archive folder is excluded by `.gitignore` and sits outside the import scope).
- Names and disputed terms from noisy speech-to-text are **hypotheses** until confirmed by a participant.

## Steps

1. **Record** the call/voice note.
2. **Transcribe locally.** Reference implementation: a local Whisper-family CLI (e.g. `faster-whisper`) in a dedicated Python venv — no cloud upload of raw audio. Any local STT with acceptable quality in your language works.
3. **Park the raw transcript** in an archive folder outside the memory import scope (e.g. `90_Archive/Audio_Transcripts/` — create it on first use; it is gitignored).
4. **Create a cleaned meeting note** in `50_Meetings/` from [[50_Meetings/Meeting_Note_Template]], named `YYYY-MM-DD-short-topic`. Cleaned means: readable summary, no filler, no sensitive fragments, uncertain names marked as "(unconfirmed)".
5. **Extract into the system:**
   - decisions -> [[40_Decisions/Decision_Log]] (+ ADR if significant);
   - tasks -> [[60_Tasks/Task_Log]];
   - new terms -> [[01_Index/Glossary]];
   - new people/roles -> [[01_Index/People]];
   - register the meeting in [[50_Meetings/Meeting_Log]].
6. **Link** the meeting note from the log and from any notes it affects.
7. **Sync memory** if the memory layer is configured: `tools/sync_mgimind.ps1 -Dirs '50_Meetings,60_Tasks'` (plus whatever else you touched).

## Verification

- The meeting note reads sensibly to someone who was not on the call.
- No raw transcript files under any memory-imported folder — `tools/check_agent_health.ps1` has a check for the common mistake (`transcripts-in-import-scope`).
- Decisions/tasks actually landed in their logs, not only in the meeting note.

## Capture After Runs

After your first real transcription, record here: the exact tool/model used, the command, processing time, and quality notes for your language — the next person should not rediscover them.

## Links

- [[50_Meetings/Meeting_Log]]
- [[70_Resources/AI_Context_Quality_Guide]]
- [[70_Resources/Agent_Workflow_Protocol]]
