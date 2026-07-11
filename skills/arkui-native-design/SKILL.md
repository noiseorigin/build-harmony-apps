---
name: arkui-native-design
description: Implement and review ArkUI interfaces for a native HarmonyOS look and interaction model. Use when applying HarmonyOS design guidance, choosing platform components, refining hierarchy, color, typography, shape, motion, accessibility, system bars, safe or avoid areas, dark mode, or replacing web/iOS-looking UI with HarmonyOS-native patterns.
---

# ArkUI Native Design

Prefer current HarmonyOS Design guidance and native ArkUI components over imitation of another platform. Preserve the product's brand while making system behavior, accessibility, and device adaptation predictable.

Read `references/review-checklist.md` for a full review. Pair with `../arkui-ui-patterns/SKILL.md` for component implementation and `../arkui-multidevice/SKILL.md` for layout adaptation.

## Workflow

1. Inspect the target device classes, minimum SDK, existing design tokens, nearby screens, and current ArkUI generation.
2. Identify the screen's primary task and information hierarchy before changing visual treatment.
3. Prefer an appropriate native component or composition from official docs/samples. Do not build custom controls for a standard interaction without a product reason.
4. Define semantic roles for color, typography, spacing, shape, elevation, and feedback; avoid one-off literals when the project has tokens/resources.
5. Integrate system surfaces deliberately: status/navigation areas, avoid areas, keyboard, focus, back behavior, dialogs, sheets, menus, and notifications.
6. Add interaction states: pressed, focused, disabled, loading, empty, error, selected, and destructive confirmation where applicable.
7. Verify dark mode, text scaling, localization expansion, screen reader labels, focus order, touch targets, motion reduction, and high-contrast needs supported by the project.
8. Render and inspect the result with `../harmony-runtime-preview/SKILL.md`.

## Strong defaults

- Use resource references for strings, dimensions, colors, and media that require localization or theming.
- Use platform navigation and overlay behavior unless the product has a validated alternative.
- Keep hierarchy clear with fewer competing accents; reserve high emphasis for the primary action or state.
- Use motion to explain state and spatial continuity, not as decoration. Avoid broad animations on large trees.
- Keep brand styling at the token/component layer rather than reimplementing system behavior.

## Evidence rules

- Cite current Huawei design/docs or an official HarmonyOS sample when recommending a platform-specific behavior.
- Distinguish a design judgment from a documented platform constraint.
- Never invent fixed pixel values, breakpoints, or accessibility thresholds and label them “HarmonyOS standard.” Use project tokens or current official guidance.
- Do not claim visual completion without inspecting at least one rendered state; use the relevant device/state matrix for broad claims.
