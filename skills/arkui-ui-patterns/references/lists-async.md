# Lists and async states

Concrete container/row code (LazyForEach, @Reusable, Swiper/WaterFlow/Grid, swipe-delete, pull-refresh, sticky groups) lives in `components-scroll.md`; this file covers the decision rules.

## Lists

- Use stable domain identity; do not use position as identity when items insert, remove, or reorder.
- Choose eager versus lazy containers from expected item count, complexity, and measurement behavior.
- For lazy data sources, implement correct change notifications and owner lifetime.
- Keep row work cheap and avoid hidden network/storage calls during render.
- Preserve selection, focus, scroll, and pagination state across refreshes when required.

## Async state

Represent at least idle/loading/content/empty/error where the feature can reach them. Define refresh, retry, cancellation, stale-result, and owner-destruction behavior before wiring calls.

- Start work from a supported lifecycle/event path, not `build()`.
- Cancel or ignore stale results when inputs or owners change.
- Make duplicate-request behavior explicit.
- Render cached/stale content deliberately instead of accidentally mixing it with a new request.
- Test slow, empty, partial, offline, server-error, cancellation, and retry paths relevant to the feature.
