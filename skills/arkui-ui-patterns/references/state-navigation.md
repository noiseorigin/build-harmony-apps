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

## V1 decorators

| Decorator | Scope | Purpose |
|---|---|---|
| `@State` | component-owned | mutable state, triggers re-render |
| `@Prop` | parent → child | one-way **deep copy** — expensive for large objects |
| `@Link` | parent ↔ child | two-way by reference; pass with `$var` |
| `@Provide`/`@Consume` | ancestor → descendant | keyed implicit binding |
| `@Observed` + `@ObjectLink` | class instances | per-property observation; `@ObjectLink` is read-only (no whole-object reassignment) |
| `@Watch('fn')` | any above | change callback |
| `@StorageLink`/`@StorageProp` | AppStorage | global; avoid for hot data — propagates to all subscribers |
| `@LocalStorageLink`/`@LocalStorageProp` | page LocalStorage | page-scoped |

**Observation depth (V1)**: `@State`/`@Prop`/`@Link` observe first level only. Arrays react to push/splice/reassign/length — not item property mutation; element-level updates need `@Observed` classes rendered via `@ObjectLink` rows (see `state-pitfalls.md`).

Selection priority: parent-child decorators > `@Provide`/`@Consume` > LocalStorage > AppStorage. Batch mutations (build a temp array, assign once) — each `@State` write is a re-render.

## V2 decorators (stable since API 23 — prefer for new code)

| V1 | V2 | Change |
|---|---|---|
| `@Component` | `@ComponentV2` | |
| `@State` | `@Local` | no external init |
| `@Prop` | `@Param` (+`@Once`) | read-only input |
| `@Link` | `@Param` + `@Event` | input + callback out |
| `@Observed`+`@ObjectLink` | `@ObservedV2`+`@Trace` | **deep** observation across nesting |
| `@Watch` | `@Monitor('path')` | deep, precise |
| `AppStorage` | `AppStorageV2.connect(Type, key, factory)` | |
| — | `PersistenceV2.connect(...)` | auto-persisted; `@Type` required on traced fields for serialization |
| `@Provide`/`@Consume` | `@Provider()`/`@Consumer()` | |

`@ObservedV2` and `@Trace` only work together; untraced fields do not refresh UI. Do not mix V1 and V2 decorators in one component. For mid/large apps Huawei recommends `StateStore` (store class with `@ObservedV2`/`@Trace` + methods; thread-safe with TaskPool).

## Navigation + NavPathStack

```ts
@Entry @Component struct App {
  @Provide('pathStack') pathStack: NavPathStack = new NavPathStack();
  build() {
    Navigation(this.pathStack) { /* home */ }
      .navDestination(PageRouter)   // top-level @Builder, not inline lambda
  }
}
```

API: `pushPath({name, param})`, `pushPathByName(name, param, onPop?)`, `pop()`, `replacePath()`, `removeIndex()`, `movePageToTop()`, `getParamByName()/ByIndex()`, `getAllPathName()`, `size()`. Interception: `setInterception({ willShow, didShow })`. Display modes: Stack / Split / Auto (600vp threshold). Since API 23 the stack can bind to the component with a `NavDestination` as home.

`@ohos.router` is legacy — migrate to Navigation per the official transition guide; use it only when maintaining existing router-based pages.

## Cross-layer communication

`UIAbilityContext.eventHub` for UIAbility ↔ page events: `emit(name, data)` / `on(name, cb)` / `off(name)`. Store callback references — anonymous functions cannot be unregistered.

Decorator tables adapted from DengShiyingA/harmonyos-ai-skill (MIT); verify V2 availability against the project's target API.
