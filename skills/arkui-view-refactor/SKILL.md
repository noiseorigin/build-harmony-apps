---
name: arkui-view-refactor
description: Refactor large or fragile ArkUI components into explicit, stable, testable structure while preserving behavior. Use when splitting long `.ets` pages, tightening ArkUI state ownership, extracting subcomponents, removing side effects from `build()`, cleaning callback/data flow, or planning a safe V1-to-V2 state-management migration.
---

# ArkUI View Refactor

Preserve behavior, layout, navigation, accessibility, and public APIs unless the user requests a redesign. Read `references/refactor-checklist.md`; read `references/v1-v2-boundary.md` before changing decorators or component generation.

## Workflow

1. Build or capture the current failure first. Record primary flows and rendered states that must remain unchanged.
2. Identify the current V1/V2 model, state owners, inbound parameters, outbound events, services, lifecycle hooks, navigation, overlays, and async tasks.
3. Move non-trivial actions and side effects out of `build()` into named methods; move domain/I/O logic into existing services or models.
4. Extract meaningful subcomponents with narrow typed inputs and events. Prefer a dedicated component for a section with its own state, branching, lifecycle, reuse, or independent test value.
5. Keep state at the narrowest owner. Do not pass the whole parent object when a value and event are sufficient.
6. Stabilize list identity, data sources, callbacks, and top-level component shape.
7. Keep V1/V2 migration separate from ordinary extraction unless migration is the explicit goal. Follow supported interop rules for the project's API level.
8. Build after each structural slice. Run the recorded flows and compare rendered states after the refactor.

## File structure

Use the project's stronger local convention when present. Otherwise order imports, constants/types, component decorators and parameters, local state, derived non-UI values, lifecycle, `build()`, builders/subcomponents, actions, async helpers, then pure helpers.

## Extraction rules

- Extract by responsibility, not arbitrary line count.
- A page above roughly 300 lines deserves review, not automatic fragmentation.
- Keep tiny stateless fragments local when extraction would hide the main hierarchy.
- Move reusable or independently meaningful components to their own files.
- Avoid a forest of computed `@Builder` fragments that preserves the same hidden coupling.

## Verification

Require a clean build, the same navigation and interaction results, matching loading/empty/error states, and a relevant test or runtime verification. If visual evidence exists, compare before/after on the same device and state.

Do not label a refactor successful merely because the file is shorter.
