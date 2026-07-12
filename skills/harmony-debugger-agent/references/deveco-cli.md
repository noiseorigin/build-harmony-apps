# DevEco CLI (`devecocli`)

Official unified CLI from openharmony-sig (npm `@deveco/deveco-cli`; Node ≥ 18, macOS/Windows, DevEco Studio ≥ 6.1 installed). Wraps hvigor/ohpm/hdc/emulator/hilog behind one command. Detect with `devecocli --version`; `../scripts/detect_harmony_env.py` reports it as `devecocli`.

## Position in the tool ladder

| Capability | First | Then | Last |
|---|---|---|---|
| build / install / launch / logs | CodeGenie MCP | `devecocli build/run/log` | raw hvigor + hdc |
| UI tree / tap / input | CodeGenie MCP (only) | — | `devecocli ui screenshot` as evidence |
| ArkTS syntax diagnostics | `devecocli` MCP `check_ets_files` (LSP, faster than a build) | full build | |
| scaffold | `devecocli create` | local template script | |
| doc lookup | `devecocli docs search/read` (local official docs) | web search of official docs | |
| emulator device state (fold/sensors/GPS/battery) | `devecocli emulator …` (only) | — | |

## Command quick-reference

```bash
devecocli create --app-name MyApp [--bundle-name com.x.y] [--api-level 23]
devecocli build [--modules m1] [--product default] [--build-mode debug]   # [outside sandbox]
devecocli run [--device <name|serial>] [--uninstall] [--skip-build]       # [outside sandbox]
devecocli device list | devecocli device view -t <target>
devecocli emulator list | start "Name" | stop <name>
devecocli emulator fold <state> --target <t> | rotate left|right --target <t>
devecocli emulator battery --target <t> --level 20 | geolocation --target <t> --longitude ...
devecocli ui screenshot [--device d] [--path ./shots/a.png]   # dir must exist first
devecocli log [--crash] [--level E] [--bundle-name b] [--from 5m] [--tail 200] [--follow]
devecocli docs search <keywords> [--limit n] | docs read <documentId> | docs catalog
```

`DEVECO_CLI_DEBUG=1` reveals the underlying hdc/emulator commands.

## MCP syntax check

`devecocli serve mcp` hosts a stdio MCP with `check_ets_files` / `check_cpp_files` (LSP-backed diagnostics without a build). It needs project-level env (`PROJECT_PATH`), so it is configured per project — `devecocli init --mcp --agent <agent> --project <path>` — not in this plugin's global `.mcp.json`.

## Hard rules (from upstream troubleshooting)

- `emulator license accept` requires an interactive TTY — hand it to the user; never loop retries.
- `emulator image download` takes 30+ min and must not be auto-retried on failure; give the user the command.
- `emulator create` timeout → ask the user to use DevEco Device Manager; do not edit SDK files.
- Multi-device hosts require explicit `--device`/`-t` — same pinning rule as HDC.
- `run --uninstall` fixes `install sign info inconsistent` after signing-key changes.
- phone/foldable/widefold/triplefold share one emulator image per OS version — download once.

Source: adapted from openharmony-sig/deveco-cli SKILL.md/README (MIT). The npm package was observed at 1.0.0 during the 2026-07 review; commands can still change, so the installed `devecocli --help` is authoritative.
