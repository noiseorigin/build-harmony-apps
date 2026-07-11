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

Use current Huawei multi-device guidance and official examples:

- https://developer.huawei.com/consumer/cn/best-practices/multidevice/
- https://gitcode.com/HarmonyOS_Samples/multi-news-read
- https://gitcode.com/HarmonyOS_Samples/multi-ticket-class

Do not copy their breakpoints or layouts without checking the current product and SDK.
