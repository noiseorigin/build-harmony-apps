# DevEco CLI (`devecocli`)

Official optional CLI from openharmony-sig (npm `@deveco/deveco-cli`). This integration targets installed version `1.3.0`: Node.js ≥ 22 plus DevEco Studio ≥ 6.0 or Command Line Tools (CLT) ≥ 26.0. macOS and Windows support Studio or CLT; Linux requires CLT and normally `DEVECO_CLI_CLT_PATH`. Detect with `devecocli --version`; `../scripts/detect_harmony_env.py` reports it as `devecocli`. Treat installed `devecocli <command> --help` as authoritative.

## Position in the tool ladder

| Capability | First | Then | Last |
|---|---|---|---|
| build / install / launch / logs | CodeGenie MCP | `devecocli build/run/log` | raw hvigor + hdc |
| UI inspection / interaction / evidence | CodeGenie MCP | `devecocli ui window/layout/click/text/swipe/screenshot` | raw hdc only when needed |
| ArkTS / C++ diagnostics and navigation | CodeGenie MCP | `devecocli` MCP `check` and language tools | full build |
| lint / SDK compatibility | project-defined checks | `devecocli check lint/compat` | full build |
| scaffold | `devecocli create` | local template script | |
| doc lookup | `devecocli docs search/read` (local official docs) | web search of official docs | |
| emulator device state (fold/sensors/GPS/battery) | `devecocli emulator …` (only) | — | |

CodeGenie remains the normal build/run/UI path. Use an already installed `devecocli` only as an optional supplement or fallback; do not install or configure it incidentally.

## Command quick-reference

```bash
devecocli create --app-name MyApp --project-path /absolute/parent/MyApp [--bundle-name com.x.y] [--api-level 23]
devecocli build [--modules m1] [--product default] [--build-mode debug]   # [outside sandbox]
devecocli run [--device <name|serial>] [--uninstall] [--skip-build]       # [outside sandbox]
devecocli device list --format json
devecocli device view -t <target> --format json
devecocli emulator list --format json
devecocli emulator start "Name"
devecocli emulator stop <name>
devecocli emulator fold <state> --target <t>
devecocli emulator rotate left --target <t>               # use right for the opposite direction
devecocli emulator battery --target <t> --level 20
devecocli emulator geolocation --target <t> --longitude <lon> --latitude <lat>
devecocli ui window list --device <d> --format json
devecocli ui layout --device <d> --format json --mode simplified
devecocli ui click --device <d> --id <node-id>
devecocli ui text "value" --device <d> --id <node-id>
devecocli ui swipe --device <d> <x1> <y1> <x2> <y2>
devecocli ui screenshot --device <d> --path ./shots/a.png
devecocli log --device <d> [--crash] [--level E] [--bundle-name b] [--from 5m] [--tail 200] [--follow]
devecocli docs search <keywords> --format json [--limit n]
devecocli docs read <documentId>
devecocli docs catalog --format json
```

For UI commands, use `--device`; emulator state commands use `--target`. `ui screenshot --path` is required and must name a writable directory or PNG path; create the destination directory first. Re-read `ui layout` after navigation or layout changes instead of reusing stale ids or coordinates.

`DEVECO_CLI_DEBUG=1` reveals underlying hdc/emulator commands. The CLI enables anonymous telemetry by default; set `DEVECO_CLI_DISABLE_TELEMETRY=1` when opt-out is desired.

## MCP diagnostics and language tools

`devecocli serve mcp` hosts a stdio MCP and needs project-level `PROJECT_PATH`. Its public diagnostic tool is `check`, with project-relative `files`; it accepts ArkTS and C/C++ files. Do not call the obsolete `check_ets_files` / `check_cpp_files` names. The shell command `devecocli check` is different: it exposes `lint` and `compat`, not LSP syntax diagnostics.

The MCP can also expose `hover`, `definition`, `declaration`, `references`, `implementation`, `workspaceSymbol`, `documentSymbol`, and `callHierarchy`; use `tools/list` because availability depends on the installed Studio LSP. `restart` resets MCP language services after the underlying project/configuration failure is fixed; do not loop it.

Prefer an existing project-scoped MCP configuration. `devecocli init --mcp` modifies agent configuration and must not be run automatically.

## Authorization and failure boundaries

- Never automatically install or update the CLI/toolchain, or run `devecocli update`, `init`, `auth`, `signature`, `emulator license accept`, `emulator image download`, or `run --uninstall`. These mutate the environment, configuration, account, licenses, images, signing state, or app data; require an explicit user request and applicable authorization.
- `devecocli emulator license` displays the agreement and prompts interactively; `emulator license view` is read-only. `emulator license accept` is non-interactive and records acceptance, so never infer consent from a build/run request.
- Image downloads can take 30+ minutes. Do not start or retry one automatically.
- `emulator create` timeout → ask the user to use DevEco Device Manager; do not edit SDK files.
- Multi-device hosts require explicit `--device`/`-t` — same pinning rule as HDC.
- `run --uninstall` can fix `install sign info inconsistent` after signing-key changes; propose it and obtain permission instead of executing it incidentally.
- phone/foldable/widefold/triplefold share one emulator image per OS version — download once.
- If even `--version` or `--help` fails because the sandbox cannot create the CLI's user data/log directory, request an outside-sandbox retry under the host's approval rules. Do not edit CLI files, redirect its home, or fabricate results.

Source: adapted from openharmony-sig/deveco-cli SKILL.md/README (MIT), verified against installed `1.3.0`. Commands can change, so installed help remains authoritative.
