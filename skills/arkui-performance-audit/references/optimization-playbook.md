# Optimization playbook

Named remedies for confirmed smells. Verify API availability against the target SDK (`devecocli docs search <API>` when installed). Apply only after the audit has identified the cost driver — see `code-smells.md`.

## Long lists

- `LazyForEach` + `IDataSource` with stable unique keys; mutations through the data source listener, never a raw array.
- `.cachedCount(n)` to preload a small off-screen window.
- `@Reusable` row components (`aboutToReuse`/`aboutToRecycle`); same-parent only, no nesting, pairs with LazyForEach.
- `.onVisibleAreaChange([0, 1], cb)` for lazy media load/release and autoplay.
- `List` inside `Scroll` needs explicit dimensions or all children materialize at once.

## Layout cost

- Flatten deep Row/Column/Flex nests with `RelativeContainer` (documented ~26% gain).
- Prefer `Column`/`Row` over `Flex` unless flexGrow/flexShrink is needed (Flex adds a layout pass).
- `if/else` over `.visibility()` — hidden components still measure and lay out.

## Cold start (target < ~1000ms launch → first frame)

- `import lazy` / dynamic `import()` for modules not needed at startup.
- Defer network prefetch until the `loadContent` callback (first frame committed).
- No synchronous work > ~10ms in `onCreate`/`onWindowStageCreate` — move to TaskPool.
- Minimize module-load-time singleton construction; avoid `hilog` in tight render loops.
- Measure with DevEco Profiler Launch task (`../../harmony-profiler-trace/SKILL.md`).

## State updates

- Batch mutations: build a temp collection, assign once — every `@State` write re-renders.
- `@Prop` deep-copies on every update; for large objects use `@Link`/`@ObjectLink` (reference).
- Keep hot data out of `AppStorage`/`@StorageLink` — changes fan out to all subscribers.
- V2 (`@ObservedV2`+`@Trace`) gives property-granular deep observation; trace only fields the UI reads.

## Animation

- Animate transforms (`scale`/`translate`/`rotate`/`opacity`), not layout properties — skips re-layout.

## Memory

- `onMemoryLevel(level)` in UIAbility/AbilityStage: clear caches at `MEMORY_LEVEL_CRITICAL`, trim at `LOW`.
- `util.LRUCache` for bounded image/data caches.
- PixelMaps created with `editable: false` from a decodable source are OS-purgeable and regenerate on access.
- Unregister listeners in `aboutToDisappear`/`onBackground`; avoid capturing `this` in long-lived closures; decode thumbnails at display size, not full resolution.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official performance best practices; figures are Huawei-published and may change.
