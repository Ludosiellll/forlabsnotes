---
type: resource
status: stable
updated: 2026-07-12
tags:
  - ai/template
  - ai/memory
---

# Memory Tool Install Note

The adjacent folder contains the official `mgimind.exe` release, its upstream license, provenance notice and checksum. The kit builder verifies the publisher-provided archive SHA-256 before extracting the executable.

## Install

1. Verify `mgimind.exe` against the adjacent `SHA256SUMS.txt`.
2. Copy it to a user-local programs directory such as `%LOCALAPPDATA%\Programs\mgimind`.
3. Run `mgimind init`, `mgimind doctor --fix`, then `mgimind doctor`.
4. Record the verified executable path in `tools/ai_os.config.json` and `.mcp.json`.
5. Create a project-specific library, import only this workspace and run `tools/sync_mgimind.ps1`.

## Safety rules

- Do not pipe remote install scripts directly into PowerShell.
- Keep secrets and private customer exports out of the memory index.
- Treat retrieved snippets as navigation, never as the source of truth.
- For mostly non-English notes, verify retrieval quality and follow the reranker guidance in [[70_Resources/MGI_Mind_Local_Setup_Template]].
- Deleting or renaming a note does not necessarily remove its old indexed chunks; run the documented hygiene procedure.

The exact bundled version is substituted into this note during packaging: `v{{MEMORY_VERSION}}`.

## Links

- [[70_Resources/Template_Kit_READ_ME_FIRST]]
- [[70_Resources/MGI_Mind_Local_Setup_Template]]
- [[70_Resources/Agent_Workflow_Protocol]]
