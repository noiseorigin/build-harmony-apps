---
name: arkui-ui-patterns
description: Build and refactor ArkUI screens with HarmonyOS-native component, navigation, overlay, state, async, list, form, accessibility, preview, and resource patterns. Use when implementing a new ArkUI page or feature, choosing components and state ownership, wiring navigation or dialogs, or seeking example-driven ArkTS UI guidance.
---

# ArkUI UI Patterns

Use the project's SDK, ArkUI state-management generation, and nearby code as the first compatibility boundary. Use current Huawei documentation and official HarmonyOS samples as primary examples.

Read `references/components-index.md` and then only the relevant reference. Pair with `../arkui-native-design/SKILL.md` for visual quality, `../arkui-multidevice/SKILL.md` for device adaptation, and `../arkui-view-refactor/SKILL.md` for behavior-preserving structural cleanup.

## Existing project

1. Identify the feature shape: list/detail, editor/form, settings, tabs, search, dashboard, or immersive content.
2. Inspect `build-profile.json5`, module config, minimum/target SDK, and nearby pages for V1/V2 state management, routing, resources, and injection conventions.
3. Define state ownership before choosing decorators. Keep transient UI state local; pass narrow values/events; keep domain and I/O logic in services or models.
4. Choose native components and a pattern from the index. Reuse project components/tokens when behavior matches.
5. Implement loading, content, empty, error, disabled, and retry states as applicable.
6. Build after the structural skeleton, then after behavior wiring. Resolve compiler errors before expanding the feature.
7. Add accessibility labels, deterministic test identifiers where the project uses them, and preview/test fixtures.
8. Render and drive the primary path with CodeGenie tools.

## New project

Use `../deveco-create-project/SKILL.md`; then establish one app shell, one navigation owner, one resource/token layer, and one service composition root before adding feature pages. Do not impose Clean Architecture or MVVM unless the project requirements justify them.

## General rules

- Do not mix ArkUI V1 and V2 decorators inside one component without a documented interop path supported by the target API.
- Prefer typed, explicit ArkTS data over dynamic object shapes.
- Keep `build()` declarative and side-effect free; run async work from supported lifecycle/task paths and make cancellation/lifetime explicit.
- Prefer stable component trees and localized conditional sections over wholesale root replacement when practical.
- Use resources for localizable/themeable values and preserve project formatting/lint rules.
- Verify API availability against the installed SDK or current official API reference before introducing a newer API.

## Anti-patterns

- Giant pages mixing UI, networking, storage, navigation, formatting, and business rules.
- Multiple booleans representing one mutually exclusive overlay or navigation state.
- Side effects or heavy derived work triggered from `build()`.
- Global state for feature-local values.
- Copying sample code without adapting SDK constraints, permissions, device types, resources, and error paths.
