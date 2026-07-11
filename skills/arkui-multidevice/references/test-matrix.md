# Multi-device test matrix

Build a matrix from supported behavior rather than testing every device SKU.

| Layout class | Viewport/device | Orientation/posture | Input | Avoid area/keyboard | Primary assertions |
| --- | --- | --- | --- | --- | --- |
| narrow |  |  | touch |  | no clipping; primary action reachable |
| medium |  |  | touch/pointer |  | intended navigation/density |
| wide |  |  | pointer/keyboard |  | panes/focus/context preserved |
| fold transition |  | folded/unfolded | touch | hinge/system areas | no occlusion; state preserved |

Add light/dark, enlarged text, and expansion-prone locale to the classes affected by those dimensions. Capture initial and post-transition frames plus one primary interaction for each materially different layout. Record unsupported combinations explicitly.
