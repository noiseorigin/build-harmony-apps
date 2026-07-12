# Platform baseline

Version quick-reference, checked 2026-07. Before pinning versions in an answer, verify with `devecocli docs search <keyword>` when the CLI is installed, or current Huawei release notes.

**Production default: API 24 (HarmonyOS 6.1.1 Release). Treat API 26 as preview-only** — mention it only when the user targets HarmonyOS 7 / API 26 Beta1 adaptation. Never present Beta1 capabilities as generally available.

## Release matrix

| HarmonyOS | API | Status | Released | DevEco Studio |
|---|---|---|---|---|
| 6.0.1 | 21 | legacy | 2025-11-25 | 5.x |
| 6.0.2 | 22 | legacy | 2026-01-23 | 5.x |
| 6.1 | 23 | stable | 2026-04-20 | 6.1 |
| 6.1.1 | 24 | **Release (production baseline)** | 2026-05-26 | 6.1.1 Release (6.1.1.280) |
| 7 / 26.0.0 Beta1 | 26 | developer preview | 2026-06-12 | 26.0.0 Beta1 (26.0.0.461) |

## Toolchain pairing

| Baseline | Hvigor | ohpm | Node.js |
|---|---|---|---|
| API 24 | 6.24.2 | 6.1.2.268 | 18.20.1 |
| API 26 Beta1 | 6.26.1 | 26.0.0.410 | **24.14.1** (18 → 24 jump; custom Hvigor/ohpm plugins need Node 24 adaptation) |

Versioning rule: from API 26.0.0 the developer-kit API version uses SemVer `X.Y.Z` instead of legacy `X.Y.Z(N)`; `compileSdkVersion: "26.0.0"` is the first SemVer-form value.

## Platform constants

- Language: ArkTS (strict TS superset); Cangjie in beta; C/C++ via NAPI. UI: ArkUI declarative.
- App model: **Stage model**. FA model is legacy — official docs moved it under lightweight-wearable development; do not use it in new apps.
- Packaging: HAP (entry/feature), HSP (shared), HAR (static archive), atomic `.app`.
- Package manager: ohpm with `oh-package.json5`.

## What changed per recent API level (selection)

- **API 23**: `Navigation` can bind the route stack to the component and use a `NavDestination` as home; `Menu.anchorPosition`; UDMF/drag-drop/crypto C APIs; `relationalStore` sendable enhancements.
- **API 24**: Camera Kit professional controls and "Follow the Person" subject tracking; `AbilityStage` pre-first-Ability and snapshot-start callbacks; taskpool execute timeouts; Tabs nested scrolling; multiline ellipsis modes; Hot Reload for C++/resources in DevEco.
- **API 26 Beta1 (preview)**: ArkWeb Chromium 132 → 144; `@Reusable`/`@ReusableV2` global reuse pools; `LayoutPolicy.matchParent`; form-control minimum touch target 28vp → 32vp; immersive system material default for dialogs/toasts (disable via metadata `ohos.arkui.UIMaterial.state` = `disable`); `ohos.permission.READ_IMAGEVIDEO` behavior changes. Many of these apply only when `targetSdkVersion >= 26.0.0` — check the official V2 behavior-scope list before predicting impact.

## Answer rules

- State the assumed API baseline when it affects the answer.
- If the project's `build-profile.json5` declares a compile/target SDK, that overrides these defaults.
- A capability introduced in a Beta SDK must be labeled preview and paired with the Release-baseline alternative.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT) platform-snapshot sections, cross-checked against Huawei release notes at adaptation time.
