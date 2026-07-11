---
name: harmony-runtime-preview
description: Render, inspect, and compare HarmonyOS ArkUI screens on previewers, simulators, or devices with DevEco CodeGenie screenshots, UI trees, verification runs, and optional Hvigor hot reload. Use when the user wants to see a screen, iterate on UI, compare phone/tablet/foldable layouts, create browser-visible screenshot proof, or validate a visual change outside static code review.
---

# Harmony Runtime Preview

Produce visual proof from the smallest useful surface. Pair with `../harmony-debugger-agent/SKILL.md` for build, launch, target selection, and UI driving; pair with `../arkui-multidevice/SKILL.md` for responsive behavior.

## Choose the mode

- **DevEco Previewer:** fastest component or page iteration when the project supports Preview. Use DevEco's multi-device preview for size-class comparison.
- **Running app:** use CodeGenie `start_app`, UI tree, actions, and verification screenshots for behavior requiring a real runtime.
- **Hot reload:** when the project's Hvigor tasks support it, use the project wrapper with `--watch --hot-compile` or its documented hot-reload task. Treat a successful compilation message plus a changed frame as proof.
- **Screenshot gallery:** after saving multiple proof images, generate a local browser gallery with `scripts/build_preview_gallery.py`.

## Workflow

1. Define the page, visual state, device classes, theme, locale, font scale, and expected change.
2. Build before runtime preview. A compiler failure blocks visual claims.
3. Establish a stable initial state and capture a baseline screenshot and UI tree.
4. Make one focused UI change.
5. Refresh Previewer or rebuild/hot reload the app, then capture the same state again.
6. For an interactive flow, use `verify_ui` with explicit actions and assertions; save its screenshot and log.
7. Compare structure as well as pixels: clipping, text wrapping, safe/avoid areas, focus, touch targets, and scroll reachability.
8. For multiple images, run:

```bash
python3 "<skill-root>/scripts/build_preview_gallery.py" \
  --output "<artifact-dir>/index.html" \
  --title "<flow and build>" \
  <image paths...>
```

Serve the artifact directory with a local HTTP server only when browser viewing is useful. Keep the server bound to loopback.

## Proof rules

- A loaded Previewer, started app, or generated HTML file is not proof by itself; confirm a real, current frame.
- Label each image with device, viewport, theme, locale, and state.
- Do not call the screenshot gallery a live simulator mirror. This plugin does not provide iOS `serve-sim`-style streaming.
- Do not claim hot reload if the project performed a full reinstall or relaunch.
- Do not edit project build files merely to force Preview support unless the user asked for that integration.

Read `references/preview-matrix.md` for the minimum state/device matrix and artifact naming.
