# ArkTS diagnostic triage map

| Signal | Inspect first | Avoid |
| --- | --- | --- |
| unsupported syntax/linter rule | exact rule, ArkTS version, grammar references | replacing with `any` or suppression |
| type/overload mismatch | installed SDK `.d.ts`/declaration, generic and nullability context | blind cast or copying old signature |
| ArkUI decorator/state error | component generation, owner/parameter/event semantics, API level | mixing V1/V2 decorators by name |
| API unavailable/missing export | target/compatible SDK, Kit import, SysCap, current docs | guessing package names |
| import/OHM URL/module | root/module package config, normalized path/case, exported index | editing unrelated call sites |
| resource/profile | resource type/name/qualifier and JSON5/profile schema | hardcoded literal as permanent bypass |
| Hvigor/model/product/target | project/task graph, modelVersion, build profile, selected product | using a task from another project |
| native bridge | C/C++ diagnostic, generated bindings, ABI/types/lifetime | fixing only the ArkTS surface |

## Error ordering

Start with the earliest causal error in the first failing task. Rebuild after each small cluster because later errors may be cascades. Preserve the full diagnostic and related notes until the final build is green.

## Recipe policy

DevEco CodeGenie's public `arkts-error-fixes` catalog is useful for candidate categories, but individual API recipes can age. Reproduce every recipe against the installed SDK/compiler before applying it.

## Verified error recipes

Real-build-verified fixes, adapted from DengShiyingA/harmonyos-ai-skill (MIT). Marked with the SDK they were verified on; re-verify on newer SDKs before applying.

### Strict-mode structural errors (stable across SDKs)

- **Object literal as a type** → declare a named `interface`; `parseOutput(): { text: string }` is rejected.
- **`any`/`unknown` escape hatch** → cast immediately at the boundary: `JSON.parse(raw) as AgentTask`.
- **`.navDestination` inline lambda** → must be a top-level `@Builder` function reference.
- **`@Entry` build() root** → must be a container (`Stack`/`Column`/`Row`); a custom component alone is not.
- **user_grant permission entry missing `reason`/`usedScene`** in `module.json5` → both required; `INTERNET` is system_grant and needs neither.

### SDK 6.0.1 / API 21-era recipes (check whether still present on installed SDK)

- **`implements DataChangeListener`** requires both current (`onDataAdd`) and deprecated (`onDataAdded`) method names, plus `onDatasetChange` — on every implementing class including test stubs.
- **`notificationManager.addSlot()`** takes a `SlotType` enum, not a `NotificationSlot` object; annotate stored constants explicitly (`const S: notificationManager.SlotType = …`) to prevent literal-type narrowing.
- **`NotificationRequest.slotType`** is typed against the old `@ohos.notification` module — nominally incompatible with `notificationManager.SlotType`. Omit the optional field; delivery routes via the slot from `addSlot()`.
- **`Permissions` type import** — `@ohos.bundleManager` is not importable; declare a local string-literal union whose values are valid permission names, assignable to the SDK's `Permissions` parameter.
- **`requestPermissionsFromUser` overload intersection** (`void & Promise<…>`) — declare a local result interface and cast the call to `Promise<LocalResult>`.
- **`getContext(this)` deprecated** → `this.getUIContext().getHostContext() as common.UIAbilityContext`; module-level functions take `ctx` as a parameter.
- **`promptAction.showToast()` deprecated** → `getUIContext().getPromptAction().showToast(...)`.
- **`display.width` is px, not vp** — divide by `densityPixels` before comparing against vp breakpoints.
