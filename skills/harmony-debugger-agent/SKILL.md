---
name: harmony-debugger-agent
description: Build, install, launch, inspect, automate, and debug HarmonyOS ArkTS apps with the official DevEco CodeGenie MCP, Hvigor, and HDC. Use when compiling or running an app, selecting a device or simulator, inspecting the UI tree, tapping or typing, capturing screenshots or verification logs, reading hilog, or diagnosing runtime behavior.
---

# Harmony Debugger Agent

Use the official `deveco-codegenie` MCP for the normal build/run/UI loop. Use direct Hvigor or HDC only for a capability the MCP does not expose, and keep every device command pinned to an explicit target when more than one target is connected.

Read `references/session-contract.md` before the first build in a task. Read `references/codegenie-tools.md` when choosing MCP parameters or handling a missing tool.

## Core workflow

1. Resolve and retain the session context: project root, module, product, target, build mode, UIAbility, bundle name, and device. Do not rediscover known values on every call.
2. Call `mcp__deveco-codegenie__init_project_path` with the project root.
3. Call `mcp__deveco-codegenie__build_project` with the narrowest appropriate app or module build.
4. Stop on a failed build. Route ArkTS diagnostics through `../arkts-error-fixes/SKILL.md`, patch the smallest cause, and rebuild before touching the UI.
5. Call `mcp__deveco-codegenie__start_app` with the resolved module, target, UIAbility, and device context.
6. Prove launch with `mcp__deveco-codegenie__get_app_ui_tree` or a screenshot-producing action. A successful start call alone is not visual proof.
7. Re-read the UI tree after navigation or layout changes. Prefer element bounds derived from the current tree; never reuse stale coordinates.
8. Use `mcp__deveco-codegenie__perform_ui_action` for focused click, fling, input, key, or screenshot actions. Use `verify_ui` for a bounded natural-language scenario, then save its screenshot and verification log with the returned verification id.
9. If the issue is a crash after a successful build, pair with `../arkts-runtime-fix/SKILL.md`.

## Environment and device checks

Run the detector when paths or targets are unclear:

```bash
python3 "<skill-root>/scripts/detect_harmony_env.py" --project "<project-root>" --probe
```

- If exactly one target is connected, retain it for the task.
- If several targets are connected and the requested target is not inferable, ask which one to mutate before installing, launching, clearing data, or driving UI.
- Starting a stopped simulator through `start_app` is acceptable for an explicit run request. Do not silently substitute a simulator when the user requested a real device.
- Never uninstall, clear app data, reboot a device, or enable root as an incidental debugging step.

## Logs

Prefer the verification log for a `verify_ui` run. For general live logs, use the detected HDC binary and explicit target:

```bash
"<hdc>" -t "<device-id>" hilog
```

Capture only the reproduction window. Filter by bundle, process, tag, or a concrete error signature; do not dump unrelated device logs into the answer. If a crash is involved, inspect faultlogger evidence before treating hilog fragments as the primary anchor.

## Completion evidence

Report the resolved context, build result, launch proof, interactions performed, artifact paths or verification id, relevant log lines, and remaining uncertainty. Never claim that an interaction succeeded without a post-action UI tree, screenshot, assertion, or matching runtime evidence.

## Fallbacks

- If the MCP is unavailable, use project-local Hvigor and the DevEco-bundled HDC discovered by the script. Do not invent task names; inspect `hvigorw tasks` or `taskTree` first.
- For direct Hvigor on HarmonyOS projects, use the detector's `devecoSdkHome` as `DEVECO_SDK_HOME` and its `javaHome` as `JAVA_HOME` when those variables are not already valid. Do not write these machine paths into committed project files.
- If no target is available, finish code/build work and state that runtime verification is pending.
- If UI automation cannot address a system dialog, capture the current frame and request the minimum manual action instead of tapping blindly.
