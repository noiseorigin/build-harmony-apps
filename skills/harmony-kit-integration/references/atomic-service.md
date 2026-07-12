# Atomic services (元服务) constraints

Checked 2026-07. An atomic service (`bundleType: "atomicService"` + `installationFree: true`) is an install-free app behind an **API gateway**: only APIs marked `@atomicservice` in the SDK d.ts are callable; others fail at compile time with **11706010 "can't support atomicservice application"**.

## Availability adjudication (never answer from memory)

1. **d.ts check**: `grep -nE "@atomicservice|@deprecated" <SDK>/ets/api/@ohos.<module>.d.ts` — needs the marker and no `@deprecated`.
2. **Official docs**: the API reference page must carry the 原子化服务API / 卡片能力 label.
3. **Counter-proof**: temporarily set `bundleType: "app"` + `installationFree: false`, clean build — SUCCESS means the code is fine and the gateway is the only blocker.

**Chain rule**: an ExtensionAbility class being `@atomicservice` does not make the capability usable — every link (render entry, data entry) must carry the marker. Example: LiveForm classes are marked, but `UIExtensionContentSession.loadContent/loadContentByName` are not → the whole LiveForm chain is unusable for atomic services.

## Hard limits

- **No monotonic clock**: `systemDateTime.getUptime`/`STARTUP` are gated. Duration statistics must use wall-clock spans between business anchors (anchor → now), never inference across sampling gaps — reviewers test by changing the system clock, and gap-inference collapses.
- **No background self-monitoring** (also true for ordinary third-party apps): accessibility events deprecated, usageStatistics/system-app-only, foreground-app observers need enterprise permissions, static SCREEN_ON/OFF subscription is system-app-only, workScheduler is unavailable to atomic services. Processes freeze in background. The viable pattern is **opportunistic sampling**: record a data point at every wake (card update, card tap, app open).
- Permission-free counters usable to bridge sampling gaps: `batteryInfo.batterySOC`/`chargingStatus` (`@atomicservice @since 12`), `net.statistics.getAllRxBytes/getAllTxBytes` (`@since 15`; the per-app `getSelfTrafficStats` variants are gated). Point-in-time signals (screen state, sensors) cannot fill gaps.
- **Package size**: single package ≤ 2MB, total ≤ 10MB — build fails beyond that; budget image/frame assets.
- **Sandbox**: `hdc file recv` cannot extract `filesDir`/preferences from the namespaced sandbox — debug data must be read back in-app (log panel / hilog mirror). `uinput` works for automated tapping on the service window; pure-function logic can be unit-tested locally without a device.

## Icon and card snapshot (review gate)

- Icon must be produced by DevEco's 元服务图标生成工具 (layered, correct rounding) — hand-made PNGs get rejected; keep `$media` icon resources consistent across scopes (nearest-scope resolution can pick the wrong copy).
- Every supported card dimension needs a same-size snapshot image with strict path/naming — a missing one surfaces as AGC submission **error 13**.

## Store review specifics

AGC review for atomic services adds: refresh-mechanism compliance (see `form-widgets.md`), icon/snapshot consistency, and functional checks under system-clock changes. Route rejection triage through `../../harmony-release-compliance/SKILL.md`.

Source: adapted from chen_jeff/harmony-os-skill (gitee; verified against real AGC review cycles). Gateway markers change per SDK — re-run the d.ts check on the installed SDK before relying on any entry above.
