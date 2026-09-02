---
type: resource
status: active
updated: YYYY-MM-DD
tags:
  - workflow/procedure
  - frontend/qa
  - design
---

# Procedure: Frontend Visual QA

## Summary

Visual verification procedure for frontend work: design changes, charts, modals, responsive layouts, dashboard interactions. Use it before declaring any UI work "done".

## Canonical Context

- Frontend architecture and gotchas: [[30_Tech/Codebase_Map]]
- Design preference context: [[01_Index/User_Working_Profile]]
- AI design workflow: [[70_Resources/Agent_Workflow_Protocol]]

## Design Direction

Record your project's direction here so agents aim at it (example shape: "calm professional tool, expressive but honest charts, no dark AI-template look, no decorative gradients, no marketing hero blocks"). Charts and drill-downs must be working tools, not decoration.

## Required Checks

### Static Build

```powershell
cd none yet\frontend
# your build command, e.g. npm run build
```

If the build/type-check fails, the UI is not done.

### Desktop

Check the main screen at desktop width:

- no overflow or horizontal scroll;
- key blocks readable without overlaps;
- tooltips stay inside the viewport;
- modals fit the viewport and do not blow up embedded SVGs;
- switching units/currencies does not break card widths;
- overlays do not fight over z-index.

### Mobile

Minimal viewport: 375px width.

- no horizontal scroll;
- toolbars do not cover content;
- tap targets are large enough;
- cards/modals collapse to one column or fullscreen;
- long names and large numbers do not break layout.

### Charts

- inline SVG must measure its container via layout, not rely on intrinsic viewBox height (`width:100%` + viewBox = surprise giant charts);
- use `clientWidth/clientHeight` for size checks when a transform is active — `getBoundingClientRect()` includes transforms;
- axes, labels and tooltips readable in every supported unit/locale;
- chart colors match the category palette;
- `prefers-reduced-motion` disables decorative animation.

### Interactions

- hover/selection links between related elements;
- modal open/close, Esc, backdrop, focus trap;
- filters/sort in tables;
- search/filter/sort/expand in data explorers;
- active tab/state restore.

## Screenshot / Browser Verification

If a browser preview or Playwright is available, capture at least:

- a desktop screenshot;
- a 375px screenshot;
- one interaction smoke test for the main modal/explorer.

Known environment gotchas:

- CSS/rAF animations freeze in background preview tabs — a "stuck" first frame in screenshots is not necessarily a bug;
- some browsers paint `<button>` text wrong under a dark OS theme unless the page declares `color-scheme`;
- SVG inside CSS grid needs `minmax(0, 1fr)`;
- native `<select>` cannot be styled when open — use a custom component for polished UI.

If the screenshot tool is unstable, use DOM/computed-style measurements and say honestly that no human-eye visual check happened. Do not present a DOM-only check as a full visual review.

## Capture After UI Work

- New durable UI pattern or gotcha -> [[30_Tech/Codebase_Map]].
- Changed design preferences -> [[01_Index/User_Working_Profile]].
- Major design decision -> [[40_Decisions/Decision_Log]] plus a decision note.
- Repeatable check/command -> this procedure note.

## Links

- [[70_Resources/Procedure_Bug_Diagnosis_Loop]]
- [[70_Resources/AI_Context_Quality_Guide]]
