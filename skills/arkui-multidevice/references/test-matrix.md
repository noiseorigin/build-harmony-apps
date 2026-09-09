# Multi-device test matrix

Build a matrix from supported behavior rather than testing every device SKU.

| Layout class | Viewport/device | Orientation/posture | Input | Avoid area/keyboard | Primary assertions |
| --- | --- | --- | --- | --- | --- |
| narrow |  |  | touch |  | no clipping; primary action reachable |
| medium |  |  | touch/pointer |  | intended navigation/density |
| wide |  |  | pointer/keyboard |  | panes/focus/context preserved |
| fold transition |  | folded/unfolded | touch | hinge/system areas | no occlusion; state preserved |

Add light/dark, enlarged text, and expansion-prone locale to the classes affected by those dimensions. Capture initial and post-transition frames plus one primary interaction for each materially different layout. Record unsupported combinations explicitly.

## Driving transitions on the emulator (devecocli)

When the official `devecocli` is installed, device-state transitions become scriptable instead of manual (Emulator 7.0+ for scene commands; always pin `--target`):

```bash
devecocli emulator list                                   # find name/serial
devecocli ui screenshot --device <t> --path ./shots/before.png
devecocli emulator fold <state> --target <t>              # fold ↔ unfold transitions
devecocli emulator rotate left|right --target <t>         # orientation
devecocli emulator battery --target <t> --level 15        # low-battery UI
devecocli emulator geolocation --target <t> --longitude 116.40 --latitude 39.90
devecocli ui window list --device <t> --format json
devecocli ui layout --device <t> --format json --mode simplified
devecocli ui screenshot --device <t> --path ./shots/fold-after.png
```

Create the writable `./shots` directory before running the example. `ui screenshot --path` is required. UI commands select the device with `--device`, while emulator state commands use `--target`. Capture before/after frames and re-read `ui layout` before the primary interaction. Foldable device types (`foldable`/`widefold`/`triplefold`) are available via `devecocli emulator create --device-type <type>`. See `../../harmony-debugger-agent/references/deveco-cli.md` for authorization boundaries around license acceptance and image downloads.
