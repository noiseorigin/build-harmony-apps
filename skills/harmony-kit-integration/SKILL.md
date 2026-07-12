---
name: harmony-kit-integration
description: Integrate HarmonyOS system Kits into an ArkTS app — Camera, Audio/AVPlayer/AVSession, Image, Scan, Account/Huawei ID login, Payment, Push, Map, Location, Weather, Notification, Core Vision OCR/segmentation, Form Kit service cards (服务卡片), atomic services (元服务), Share Kit, App Linking deep links, relationalStore/preferences/fileIo persistence, HTTP/WebSocket networking, background tasks, ArkWeb. Use when adding a Kit capability, requesting permissions (相机权限/定位权限/麦克风权限), when background audio stops after switching apps (后台播放被静音), when a service card does not refresh (卡片不刷新), when push token errors appear, or when choosing which Kit/import provides a capability.
---

# Harmony Kit Integration

Integrate one system capability at a time with permission, version, and runtime evidence. Read `references/kits-index.md` to route to the Kit cluster; read only the matching cluster file.

## Core workflow

1. **Resolve the capability to a Kit** via `references/kits-index.md`. Prefer the no-permission system surface when one exists (CameraPicker, Scan default UI, pickers) before requesting sensitive permissions.
2. **Check availability against the project baseline**: installed SDK, `deviceTypes`, region constraints (several Kits are China-mainland only), and whether the API is Release or preview (`../deveco-create-project/references/platform-baseline.md`). Verify current signatures with `devecocli docs search <API>` when the CLI is installed, otherwise current Huawei docs.
3. **Declare and request permissions** per `references/permissions.md`: `module.json5` entry (user_grant needs `reason` + `usedScene`) → runtime check → `requestPermissionsFromUser` → settings-dialog fallback. Never ship a flow that re-pops a denied dialog.
4. **Implement the minimal integration** from the cluster reference, keeping Kit calls in a service layer, not `build()`.
5. **Verify on a device or emulator** through `../harmony-debugger-agent/SKILL.md`: drive the actual flow (grant dialog, capture, playback, card add) and capture UI-tree/screenshot/log evidence. Permission dialogs and many Kits do not work in the Previewer.
6. **Report** the Kit + API level used, permission surface, evidence, and any region/device limits that apply.

## Rules

- AGC-backed Kits (Account, Push, Payment, Map) fail without console-side configuration — state the AGC prerequisite instead of debugging the client in circles.
- Background execution is never implicit: pair the capability with the correct background-task type (`references/background-tasks.md`); media playback additionally requires AVSession or the system silences it.
- Named callbacks for every `on()` so `off()` can release them; release engines/sessions (`init`/`release` pairs) with the owning lifecycle.
- Do not claim an integration works from a successful compile — each Kit has a runtime authorization or service dependency that only device evidence can prove.
- For store/review implications of a Kit (privacy labels, permission justification), pair with `../harmony-release-compliance/SKILL.md`.

## Cluster references

- `references/kits-index.md` — full Kit catalog with import keys; start here.
- `references/permissions.md` — declaration + three-step runtime flow + settings fallback.
- `references/media.md` — Camera (picker + session), Audio focus/streams, AVPlayer/AVRecorder, Image Kit.
- `references/push-notification.md` — Push token, Notification slots/publish, AVSession for background audio.
- `references/data-persistence.md` — relationalStore, preferences, fileIo, pickers, sandbox paths, resources.
- `references/network.md` — HTTP, WebSocket, connectivity monitoring, background transfer.
- `references/account-payment.md` — Huawei ID login variants, error codes, Payment Kit.
- `references/map-location-weather.md` — Location, Map component, Weather Service.
- `references/vision-scan.md` — Core Vision OCR/face/segmentation, Scan Kit.
- `references/form-widgets.md` — Form Kit service cards.
- `references/atomic-service.md` — atomic service (元服务) constraints.
- `references/share-linking.md` — Share Kit, App Linking, startAbilityByType, app continuation.
- `references/background-tasks.md` — 4 background task types and modes.
- `references/arkweb.md` — Web component, JS bridge, cookies, interception.
