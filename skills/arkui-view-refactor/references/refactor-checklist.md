# ArkUI refactor checklist

## Before

- Clean baseline build or captured existing failure.
- Current V1/V2 generation and API boundary identified.
- State owners/readers/writers, services, navigation, overlays, async work, and lifecycle mapped.
- Primary flows and visual states recorded.

## During

- `build()` remains declarative and free of I/O/business side effects.
- Extracted components receive narrow typed values/events.
- State is not duplicated or moved to a longer lifetime without need.
- List identity/data-source and callback behavior remain stable.
- Lifecycle/task cleanup remains paired with ownership.
- Public routes, resource identifiers, accessibility labels, and test selectors are preserved unless intentionally changed.

## After

- Focused ETS check and full affected build pass.
- Loading/content/empty/error and overlay/navigation flows match baseline.
- Visual comparison uses the same device/state.
- Relevant tests pass; no new warnings are hidden.
- File length decreased only as a consequence of clearer ownership, not as the success metric.
