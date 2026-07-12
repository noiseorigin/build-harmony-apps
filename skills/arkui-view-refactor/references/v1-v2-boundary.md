# ArkUI V1/V2 boundary

Treat state-management migration as a separate behavior change.

1. Inspect decorators and component declarations across the target and its direct parent/children.
2. Confirm minimum/target API and installed SDK migration guidance.
3. Map each V1 state/input/output dependency to the supported V2 equivalent by semantics, not decorator-name similarity.
4. Trace transitive consumers before changing ownership or mutability.
5. Use documented V1/V2 interop only at explicit boundaries; do not mix generations opportunistically inside a component.
6. Migrate a small connected slice, build, and verify updates in both directions.
7. Preserve initialization, persistence, observation depth, event timing, preview/test fixtures, and lifecycle behavior.

For API levels where mixing is restricted, treat a compiler-passing isolated file as insufficient; build the connected module and drive the update path. Consult current official migration docs because rules differ by API generation.

## Semantic mapping table

V2 decorators are stable since API 23; prefer V2 for new components. Full decision tables live in `../../arkui-ui-patterns/references/state-navigation.md`.

| V1 | V2 | Semantics shift to verify |
|---|---|---|
| `@State` | `@Local` | V2 forbids external initialization — callers passing an initial value must move to `@Param` |
| `@Prop` | `@Param` (+`@Once`) | V1 deep-copied; V2 passes by reference and is read-only — mutation sites must become `@Event` callbacks |
| `@Link` | `@Param` + `@Event` | two-way binding becomes explicit input + output; update timing changes from synchronous binding to event dispatch |
| `@Observed`+`@ObjectLink` | `@ObservedV2`+`@Trace` | observation deepens from first-level to traced-property-any-depth — previously invisible nested writes start triggering renders |
| `@Watch` | `@Monitor('a.b')` | monitor paths are precise; V1 watchers on whole objects may need several monitors |
| `AppStorage`/`PersistentStorage` | `AppStorageV2`/`PersistenceV2` | connect-by-type+key model; `PersistenceV2` requires `@Type` on traced fields to serialize |

The observation-depth change is the most common source of behavior drift after migration: V2 renders on nested writes that V1 silently ignored, which can expose render loops or performance regressions that the V1 code masked.
