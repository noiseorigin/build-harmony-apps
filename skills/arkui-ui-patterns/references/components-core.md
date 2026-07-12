# Core components and layout

Pattern quick-reference, checked 2026-07. Verify current signatures with `devecocli docs search <component>` when installed, or current Huawei docs.

## Component lifecycle

| Callback | When | Constraint |
|---|---|---|
| `aboutToAppear()` | after creation, before first `build()` | state changes here apply in first build |
| `onDidBuild()` | after `build()` completes (API 12+) | no state changes, no `animateTo` |
| `aboutToDisappear()` | before destruction | no state changes (especially `@Link`), no async |
| `aboutToReuse(params)` | reusable component re-added from cache | update state from params |
| `aboutToRecycle()` | moving to reuse cache | release heavy resources |

`@Entry` only: `onPageShow()` / `onPageHide()` / `onBackPress(): boolean` (return `true` to consume Back).
Cold-start order: parent aboutToAppear → parent build → parent onDidBuild → child aboutToAppear → child build → child onDidBuild → onPageShow.

## Layout containers

| Container | Use | Performance |
|---|---|---|
| `Column`/`Row` | linear | best — single-pass |
| `Stack` | overlap; `alignContent` 9 positions, `zIndex` | good |
| `Flex` | stretch/shrink needed | slower — second pass for flexGrow/flexShrink; prefer Column/Row otherwise |
| `RelativeContainer` | flatten deep nesting; children need `.id()`, anchor `__container__` | good — documented ~26% gain over deep nests |
| `GridRow`/`GridCol` | responsive multi-device | good |

Utilities: `Blank()` fills remaining main-axis space (`Row { Text; Blank(); Text }`); `.layoutWeight(n)` proportional sizing; `.displayPriority(n)` lower-priority children auto-hide when the container shrinks.

Layout rules: keep nesting ≤ ~3 levels; prefer `if/else` over `.visibility()` (hidden components still lay out); give `List` inside `Scroll` explicit dimensions or all children load at once.

## Reusable styling

```ts
class PrimaryButton implements AttributeModifier<ButtonAttribute> {
  applyNormalAttribute(i: ButtonAttribute): void { i.height(48).fontColor(Color.White).backgroundColor('#007DFF'); }
  applyPressedAttribute(i: ButtonAttribute): void { i.backgroundColor('#0056B3'); }
}
Button('Submit').attributeModifier(new PrimaryButton())
```

Also: `@Builder` (parameterized subtree), `@Styles` (common attributes, no params), `@Extend(Component)` (component-specific chain).

## Tabs (bottom navigation)

```ts
Tabs({ barPosition: BarPosition.End }) {
  TabContent() { HomePage() }.tabBar(this.tabBuilder(0, 'Home', $r('sys.symbol.house')))
  TabContent() { MinePage() }.tabBar(this.tabBuilder(1, 'Me', $r('sys.symbol.person')))
}
.barHeight(56).onChange((i) => { this.currentIndex = i; }).scrollable(false)
```

Custom tab bar via a `@Builder` that reads `this.currentIndex` for selected styling. Glass-blur bar: `.barOverlap(true).barBackgroundBlurStyle(BlurStyle.Thin)`.

## Text input and form controls

```ts
TextInput({ placeholder: 'Enter username' })
  .type(InputType.Normal)            // .Email .Number .Password .PhoneNumber
  .maxLength(20)
  .onChange((v: string) => { this.username = v; })
TextArea({ text: $$this.desc }).maxLength(200).showCounter(true)
```

`$$` gives two-way binding without `onChange`. Control quick-list: `Checkbox` (`select`/`onChange`), `Toggle` (`type(ToggleType.Switch)`, `isOn` — see state-pitfalls for one-way trap), `Radio` (`value`/`group`), `Select` (`options`/`selected`), `Slider` (`min`/`max`/`step`), `DatePicker`/`TimePicker` (`selected`), `Search` (`onSubmit`), `Progress` (`value`/`total`), `LoadingProgress`.

## Animation

- Explicit: `this.getUIContext()?.animateTo({ duration, curve, onFinish }, () => { /* state changes animate */ })`.
- Implicit: `.animation({ duration, curve })` applies to *preceding* attributes.
- Curves: `Curve.EaseOut` etc.; spring strings `'springMotion(response,dampingFraction)'`.
- Shared element: same `.geometryTransition('id')` on source and target, state change wrapped in `animateTo`.
- Keyframes: `keyframeAnimateTo({ iterations }, [{ duration, event }...])`.
- Prefer transform properties (`scale`/`translate`/`rotate`/`opacity`) over layout properties (`width`/`height`/`margin`) — transforms skip re-layout.

## Blur / material effects

`.backgroundBlurStyle(BlurStyle.Thin, { colorMode, adaptiveColor, scale })` (API 9+); `.foregroundBlurStyle` (API 10+); `.backgroundEffect({ radius, saturation, brightness, color })` (API 11+); `.backdropBlur(radius)`/`.blur(radius)` (API 7+). `pointLight` is system-app-only; `hdsMaterial.systemMaterialEffect` is HarmonyOS-SDK-only (API 23+), not OpenHarmony.

## Gesture conflict

| `hitTestBehavior` | Behavior |
|---|---|
| `Default` | self responds, blocks siblings |
| `Transparent` | self responds AND passes through |
| `None` | skips self, passes to siblings |
| `Block` | only self, stops propagation |

Binding: `.priorityGesture()` parent wins; `.parallelGesture()` both respond; `.gesture(g, GestureMask.IgnoreInternal)` blocks child. `GestureGroup(GestureMode.Sequence | .Parallel | .Exclusive, …)`. System gestures (onClick/onTouch/drag/bindMenu) always beat same-type custom gestures.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official ArkUI docs and best practices.
