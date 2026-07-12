# Multi-device scenario router

| Scenario | Inspect | Design response | Required transition |
| --- | --- | --- | --- |
| size/window | available content bounds, resizable mode, grid/breakpoints | rearrange density/navigation/panes by space | narrow ↔ wide resize |
| fold state | fold posture/display region/hinge where exposed | avoid occlusion; preserve context across posture | fold ↔ unfold/half-fold |
| avoid area/keyboard | system bars, cutouts, keyboard/insets | keep actions/content reachable; scroll/focus input | keyboard/system UI show ↔ hide |
| input/focus | touch, mouse, keyboard, focus graph | explicit hover/focus/shortcuts without breaking touch | pointer/key focus ↔ touch |
| orientation | natural orientation and app policy | reflow rather than rotate fixed dimensions | portrait ↔ landscape |
| hardware/SysCap | declared device types and runtime capabilities | gate optional feature and provide fallback | available ↔ unavailable |
| composite | several of the above | define precedence and stable semantic structure | representative combined transitions |

## Implementation patterns

Breakpoints (verify thresholds against current guidance): `sm` < 600vp (phone portrait), `md` < 840vp (phone landscape / small tablet), `lg` ≥ 840vp (tablet / unfolded foldable).

```ts
import { display } from '@kit.ArkUI';
export function getBreakpoint(): string {
  const d = display.getDefaultDisplaySync();
  const widthVp = d.width / d.densityPixels;   // display.width is px, not vp
  return widthVp < 600 ? 'sm' : widthVp < 840 ? 'md' : 'lg';
}
```

- Fold/unfold: `display.on('change', listener)` in `aboutToAppear`, `display.off` in `aboutToDisappear`; the callback receives `(id: number)` — keep a named reference to unregister.
- Switch layouts with `if/else` on the breakpoint, never `.visibility()` (hidden branches still lay out).
- Responsive grids: `GridRow({ columns: { sm: 1, md: 2, lg: 3 }, breakpoints: { value: ['600vp', '840vp'] } })` with `GridCol` children. GridRow/GridCol does **not** support `LazyForEach` — use `ForEach` over a `@State` array refreshed by a `DataChangeListener` when the source is lazy.
- Share the breakpoint via `@Provide('breakpoint')` at the `@Entry` root and `@Consume` in `NavDestination` children (same subtree).

Use current Huawei multi-device guidance and official examples:

- https://developer.huawei.com/consumer/cn/best-practices/multidevice/
- https://gitcode.com/HarmonyOS_Samples/multi-news-read
- https://gitcode.com/HarmonyOS_Samples/multi-ticket-class

Do not copy their breakpoints or layouts without checking the current product and SDK.
