# DevEco CodeGenie MCP tools

The plugin pins `@deveco-codegenie/mcp@1.1.11`, the npm `stable` release reviewed on 2026-07-10. Inspect the live tool schema before supplying optional fields because the contract can evolve.

| Tool | Use | Gate |
| --- | --- | --- |
| `init_project_path` | Set the absolute HarmonyOS project root | Call before project tools and after changing projects. |
| `build_project` | Build app/module, optionally clean, choose product/build mode | Stop on nonzero/failure; do not launch stale output. |
| `start_app` | Install/start the already built app on simulator or real device | Build first; supply known module/target/ability/device context. |
| `get_app_ui_tree` | Read simple or full UI hierarchy as JSON | Re-read after layout/navigation changes. |
| `perform_ui_action` | Click, directional fling, input text, key event, screenshot | Use current tree bounds; verify afterward. |
| `verify_ui` | Execute a bounded natural-language UI scenario with validation | Keep plan explicit and deterministic; retain returned id. |
| `save_ui_screenshot` | Save screenshot from a verification run | Requires verification id. |
| `get_ui_verification_log` | Retrieve the verification execution log | Requires verification id. |
| `check_ets_files` | Focused ArkTS/ETS diagnostics | Pair with compiler output, then rebuild. |
| `check_cpp_files` | Focused native-source diagnostics | Pair with native build output. |

## Known boundary

This reviewed MCP version does not expose a general device-list/session-defaults tool, a continuous hilog stream, arbitrary file pull, DevEco Profiler trace capture, or a live browser mirror. Use the DevEco-bundled HDC/Hvigor or a documented manual DevEco step only for those gaps. Do not silently route to an unreviewed community MCP.

Official DevEco CodeGenie listing: https://developer.huawei.com/consumer/cn/deveco-studio/resources/
