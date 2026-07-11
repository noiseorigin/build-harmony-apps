# ArkUI native design review

## Hierarchy and platform fit

- Is the primary task obvious and the primary action appropriately emphasized?
- Are native navigation, lists, menus, sheets/dialogs, text inputs, pickers, and feedback patterns used where they fit?
- Does branding live in tokens/components without changing expected system behavior?

## Visual system

- Semantic color roles work in light/dark and contrast states.
- Typography/resource roles preserve hierarchy under text scaling and localization.
- Spacing, shape, imagery, and elevation are consistent and resource-backed.
- Empty/loading/error/disabled/selected states are designed, not accidental.

## Interaction

- Back, focus, pointer/keyboard, touch feedback, destructive confirmation, and interruption recovery are coherent.
- Motion explains state/spatial change, respects user settings where supported, and avoids large render costs.
- System bars, avoid areas, keyboard, fold/window transitions, and overlays do not obscure content.

## Accessibility and content

- Controls have meaningful labels/roles/states and a logical focus/read order.
- Touch targets, color-independent cues, text expansion, bidi/localization, and reduced-motion needs are considered.
- Errors explain recovery; sensitive data is not exposed in screenshots, logs, or accessibility text.

## Sources

- HarmonyOS Design and docs: https://developer.huawei.com/consumer/cn/doc/
- Official component UX examples: https://gitcode.com/HarmonyOS_Samples/HarmonyOSComponentUXExamples
- Official best-practice snippets: https://gitcode.com/HarmonyOS_Samples/BestPracticeSnippets

Use exact current component/API guidance from these sources rather than turning this checklist into invented numeric standards.
