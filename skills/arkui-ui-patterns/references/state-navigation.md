# State and navigation

## State ownership

- Identify owner, readers, writers, lifetime, and persistence requirement before choosing a decorator.
- Keep transient interaction state at the smallest component that owns it.
- Pass narrow typed values downward and events upward; inject shared services through the project's established mechanism.
- Keep domain state and I/O outside `build()` and UI-only wrappers.
- Follow one ArkUI generation inside a component. Verify V1/V2 decorators and interop against target API.

## Navigation

- Establish one route owner per navigation surface and typed destinations/parameters.
- Separate route state from display state and business data.
- Handle external/system entry through one validated handoff path.
- Preserve back behavior, restoration/deep-link requirements, and per-pane/per-tab history deliberately.
- Validate unknown/missing parameters and avoid sensitive values in routes/logs.

## App shell

Keep root composition small: app-wide dependencies, theme/resources, navigation owner, and top-level surfaces. Feature services/models should be testable without reconstructing the entire root UI.
