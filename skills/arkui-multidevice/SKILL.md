---
name: arkui-multidevice
description: Adapt and verify ArkUI layouts and interactions across HarmonyOS phones, tablets, foldables, window sizes, orientations, keyboards, and input methods. Use when implementing once-develop-multi-deploy behavior, responsive or adaptive layouts, fold-state changes, avoid areas, freeform windows, mouse/keyboard focus, natural orientation, SysCap checks, or composite multi-device scenarios.
---

# ArkUI Multi-device

Route the request through `references/scenario-router.md`. Use window and capability evidence rather than device-name guesses, and preserve one coherent information architecture across sizes.

## Workflow

1. Record supported device types, resizable-window behavior, minimum/target SDK, orientations, input methods, and required system capabilities.
2. Classify the scenario: size/window, fold state, avoid area/keyboard, input/focus, orientation, hardware/SysCap, or composite.
3. Inspect the current layout, resources, breakpoints/grid strategy, window APIs, and nearby official multi-device examples.
4. Define behavior by available content space and capability. Use project or current official breakpoints; do not infer layout solely from `phone`/`tablet` labels.
5. Keep semantic structure stable while changing arrangement, density, navigation presentation, or secondary-pane visibility.
6. Handle runtime transitions: resize, rotate, fold/unfold, keyboard appearance, pointer/focus changes, and system-bar/avoid-area changes.
7. Gate optional hardware/API paths with capability and availability checks and provide a meaningful fallback.
8. Render the matrix through `../harmony-runtime-preview/SKILL.md` and drive at least the primary action in each materially different layout.

## Strong defaults

- Prefer adaptive constraints, grids, and containers over duplicated device-specific pages.
- Preserve user context, selection, scroll position, and in-progress input across layout transitions when feasible.
- Keep touch, mouse, keyboard, and focus behavior coherent rather than treating desktop-like input as enlarged touch.
- Test localization, text scale, dark mode, and keyboard/avoid areas at the narrowest supported width.
- Use separate implementations only when interaction or capability truly differs, not because dimensions differ.

## Proof

Use `references/test-matrix.md`. Broad “supports phones, tablets, and foldables” claims require evidence for every materially different layout class and at least one transition state. A single preview image is not multi-device proof.
