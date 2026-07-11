# ArkUI performance code smells

## State and updates

- Broad app/page state read by a large tree for one small value.
- Mutating state during render or in a lifecycle loop that triggers another render.
- Replacing large objects/collections when a narrow value or immutable slice would suffice.
- Mixing V1/V2 state advice or using compatibility wrappers without checking update semantics.

## Render work

- Sorting, filtering, parsing, formatting, JSON work, I/O, database/network calls, or image processing in `build()`/builders.
- Recreating large models, data sources, option objects, or closures on every build.
- Root-level branch swaps that repeatedly discard expensive subtrees when localized state would work.

## Lists and layout

- Unstable or index-based identity for reorderable/changing items.
- Large eager containers where the collection justifies lazy rendering.
- `LazyForEach` without a correct stable data source and notifications.
- Deep nesting, repeated measurement, unconstrained content, or nested scrolling with competing axes.

## Media and animation

- Decoding/rendering full-size images far above display need.
- Unbounded caches or retaining page-owned media after navigation.
- Animating a broad container/property tree for a local change.
- Continuous timers/animations while offscreen or unchanged.

## Async and lifecycle

- Main-thread CPU/I/O in lifecycle callbacks.
- Duplicate requests/tasks after repeated appearance or state changes.
- Listeners, subscriptions, timers, workers, or native callbacks not released with owner lifetime.

## Fix discipline

For each smell, state the changed input, affected subtree/work, expected cost, and verification plan. Do not recommend an optimization API by name unless it is supported by the target SDK and fits the lifecycle.
