# Overlays and forms

## Overlays

- Model mutually exclusive dialogs/sheets/menus with one selected state rather than unrelated booleans.
- Give the presented surface ownership of its local draft and dismissal behavior where practical.
- Preserve focus and return it predictably after dismissal.
- Use system back/outside-tap behavior intentionally; protect destructive or irreversible work.

## Forms

- Separate raw input, normalized value, validation state, and submission state.
- Validate locally where deterministic and server-side where authoritative.
- Show errors next to the field and provide an accessible summary/focus path for submission errors.
- Disable duplicate submissions while preserving retry and entered data.
- Use the appropriate keyboard/input type and handle keyboard avoid areas.
- Keep secrets out of logs, screenshots, state restoration, and accessibility announcements.

## Feedback

Use inline status for persistent/actionable information and transient feedback for brief confirmations. Error text should explain what happened, impact, and recovery without exposing internals.

## Current overlay APIs

Do **not** use deprecated `CustomDialog` or module-level `@ohos.promptAction`. Current surfaces:

- **Toast**: `this.getUIContext().getPromptAction().showToast({ message, duration })`.
- **Alert**: `AlertDialog.show({ title, message, primaryButton, secondaryButton })` for simple confirms.
- **Custom dialog**: `ComponentContent` + `wrapBuilder(builder)`, then `uiContext.getPromptAction().openCustomDialog(node, { alignment, isModal, autoCancel })`; close with `closeCustomDialog(node)` passed into the builder params.
- **Bottom sheet**: `uiContext.openBindSheet(node, { title, height: SheetSize.MEDIUM, detents: [SheetSize.MEDIUM, SheetSize.LARGE, 200], preferType: SheetType.BOTTOM }, targetId)`.
- **Full-screen modal**: `.bindContentCover($$this.isPresented, this.builder(), { modalTransition })`.

## Overlay pitfalls (production-verified)

- **One bindSheet, many contents = state-machine mismatch.** A single `bindSheet` whose inner `@Component` swaps per selection intermittently shows the wrong sheet, wrong height, or a dead sheet — and only when alternating between contents (repeating one content never reproduces it). Correct shape: N independent `@State showXxx` flags + N `@Builder`s each wrapping one fixed component + N `.bindSheet` on **separate** trigger nodes.
- **bindContextMenu long-press preview**: use `MenuPreviewMode.IMAGE` (CustomBuilder previews jank); set `.draggable(false)` on `Image` or drag swallows the long-press; don't rely on `MenuItem.onClick` inside `bindContextMenu` — route through the menu action callbacks; a styled inner container inside the system menu produces a double border.
- **Scroll pushes short content down** (centering tendency): first element sits lower on short pages than long ones. Fix at the container: content `Column` inside `Scroll` gets `.constraintSize({ minHeight: '100%' })`. Shared `Scroller` instances keep scroll offset across pages — reset or use separate scrollers.
- **Monochrome SVG icons with hollow centers**: `.fillColor()` tinting fills `fill="none"` circles solid. Hollow geometry must be geometric — two concentric circles with `fill-rule="evenodd"` (ring thickness = router − rinner). Prefer SVG assets + `fill="currentColor"` over composing icons from shape components.
- **Persistent drawer/sheet with slide animation**: keep the component mounted and toggle `.translate()` + `.animation()`; `if (open)` mount/unmount loses the transition.

Overlay API summary adapted from DengShiyingA/harmonyos-ai-skill (MIT); pitfalls from chen_jeff/harmony-os-skill (gitee), device-verified. Verify signatures against the installed SDK.
