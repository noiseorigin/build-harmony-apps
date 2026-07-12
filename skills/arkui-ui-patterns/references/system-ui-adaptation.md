# System UI adaptation

Immersive window, dark mode, keyboard, and orientation patterns. Checked 2026-07; verify with `devecocli docs search <keyword>` or current Huawei docs.

## Immersive window / safe areas

```ts
// Component-level (simplest)
Column() { /* content */ }
  .expandSafeArea([SafeAreaType.SYSTEM], [SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM])

// Window-level (all pages)
windowStage.getMainWindowSync().setWindowLayoutFullScreen(true);
```

Manual padding from avoid areas:

```ts
const win = await window.getLastWindow(context);
const sys = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
const topVp = px2vp(sys.topRect.height);      // status bar
const bottomVp = px2vp(sys.bottomRect.height); // nav indicator
win.on('avoidAreaChange', (o) => { /* re-pad on split-screen/fold */ });
```

Status bar: `win.setSpecificSystemBarEnabled('status' | 'navigationIndicator', false)` to hide; `win.setWindowSystemBarProperties({ statusBarContentColor: '#FFFFFF' })` for content color. When extending a page background under the status bar, also keep content avoidance — background extension alone leaves text under the clock.

## Dark mode

Resource-qualifier approach (preferred): same-named resources in `resources/base/` (light) and `resources/dark/`; `$r('app.color.bg_color')` auto-switches. Never hardcode hex colors for themed surfaces.

React to changes:

```ts
// EntryAbility
onCreate(): void { AppStorage.setOrCreate('colorMode', this.context.config.colorMode); }
onConfigurationUpdate(c: Configuration): void { AppStorage.setOrCreate('colorMode', c.colorMode); }
// Component
@StorageProp('colorMode') @Watch('onModeChange') colorMode: number = ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET;
```

Programmatic override: `applicationContext.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_DARK)`.

## Soft keyboard

- Avoid mode (UIAbility): `windowStage.getMainWindowSync().getUIContext().setKeyboardAvoidMode(KeyboardAvoidMode.RESIZE)` — `OFFSET` lifts the page (default), `RESIZE` compresses it, `NONE` overlaps.
- Pin a component (e.g. title bar): `.expandSafeArea([SafeAreaType.KEYBOARD]).zIndex(1)`.
- Height monitoring: `win.on('keyboardHeightChange', (h) => this.kb = px2vp(h))`.
- Focus: `TextInput().defaultFocus(true)`; `getFocusController().requestFocus('id')` / `.clearFocus()` (dismisses keyboard).

## Orientation

```ts
const win = await window.getLastWindow(this.context);
win.setPreferredOrientation(window.Orientation.USER_ROTATION_LANDSCAPE); // or ..._PORTRAIT / AUTO_ROTATION
win.on('windowSizeChange', (size) => { /* re-layout; read display orientation */ });
```

Static config: `module.json5` ability `"orientation": "portrait" | "landscape" | "auto_rotation" | "follow_desktop"`. For responsive layout across fold states prefer breakpoints (`../../arkui-multidevice/SKILL.md`) over orientation branching.

## Keep screen on

`win.setWindowKeepScreenOn(true)` during playback/navigation; reset when leaving.

## Immersive status bar — hybrid pattern (production-verified)

Neither official approach alone is sufficient for themed headers: background extension alone puts text under the clock; content avoidance alone leaves a theme-colored gap on theme switch. Combine them:

1. `onWindowStageCreate`: `setWindowLayoutFullScreen(true)` once.
2. Measure the system avoid area, store the top height in `AppStorage` (secondary pages read it from there — they cannot remeasure reliably).
3. Page root as a two-layer `Stack`: background layer extends full-bleed (theme color repaints with zero lag), content layer pads top by the stored status-bar height.
4. Bottom tab bar translucency: `backgroundBlurStyle(BlurStyle.Regular)` on the bar, content scrolls beneath.
5. Sticky headers that fade in blur must be Stack-overlaid on the scroll content, not inline — inline headers jump when the blur activates.

Anti-patterns: hardcoding 38/44vp for the status bar; re-measuring per page; using `Scroll` top-spacers to fake avoidance.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), aligned with official window/UI guides; immersive hybrid pattern from chen_jeff/harmony-os-skill (gitee), device-verified.
