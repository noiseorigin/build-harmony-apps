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
