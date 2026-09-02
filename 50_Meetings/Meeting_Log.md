---
type: index
status: active
updated: YYYY-MM-DD
tags:
  - meetings
---

# Meeting Log

Registry of meetings and agreements. Each meeting gets a note from [[50_Meetings/Meeting_Note_Template]] named `YYYY-MM-DD-short-topic`.

Agent rule: before answering any opinion/prediction question about a person from these meetings, open the relevant meeting note — do not answer from priors (see the recall gate in `CLAUDE.md`/`AGENTS.md`).

| Date | Topic | Outcomes | Link |
| --- | --- | --- | --- |
| YYYY-MM-DD | Example: kickoff | Key agreements in one line | [[50_Meetings/Meeting_Note_Template]] |

## After every meeting

- add a short summary;
- extract decisions into [[40_Decisions/Decision_Log]];
- extract tasks into [[60_Tasks/Task_Log]];
- add new terms to [[01_Index/Glossary]];
- add new people to [[01_Index/People]].

## Raw transcripts

Raw speech-to-text output is noisy and may contain sensitive fragments. Keep raw transcripts OUT of the folders imported into the memory layer (use an archive folder excluded by `.gitignore` and the import scope); only cleaned meeting notes belong here. Names and disputed terms from noisy transcripts are hypotheses until confirmed.
