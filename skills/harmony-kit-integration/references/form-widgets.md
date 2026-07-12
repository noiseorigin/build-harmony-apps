# Form Kit service cards (服务卡片)

Checked 2026-07. Cards run in a sandboxed FormExtension process (launcher context) with a restricted ArkUI subset — most pitfalls below come from that isolation. Verify with `devecocli docs search form` or current docs.

## Wiring

- `module.json5` extensionAbility `type: "form"` with metadata `ohos.extension.form` → `resources/base/profile/form_config.json` (`uiSyntax: "arkts"`, `defaultDimension`, `supportDimensions`, `updateEnabled`…).
- `FormExtensionAbility`: `onAddForm(want)` (persist formId→config mapping, return placeholder `formBindingData`), `onUpdateForm(formId)` (pull fresh data, push), `onRemoveForm(formId)` (unregister), `onFormEvent(formId, message)`.
- Card page reads pushed data via `@LocalStorageProp('key')`.

## Refresh model (API 23 hard facts)

Three mechanisms; `onChangeFormVisibility` is **system-app-only** — ordinary apps refresh by pushing.

| Mechanism | Config/API | Constraint |
|---|---|---|
| active push | `formProvider.updateForm(formId, formBindingData.createFormBindingData(data))` | the primary path; push from every business change point AND app entry (`onCreate`/`onNewWant`/`onForeground`) as fallback |
| timed | `form_config.updateDuration` (unit = 30min multiples) | **overrides** `scheduledUpdateTime` when > 0 |
| scheduled | `scheduledUpdateTime: "HH:mm"` (multi: `multiScheduledUpdateTime`, ≤24 points, since API 18) | requires `updateDuration: 0`; static config, no runtime rewrite |
| next-refresh | `setFormNextRefreshTime(formId, minutes)` (`@atomicservice @since 11`) | one-shot, `minutes ≥ 5`; re-arm inside each `onUpdateForm`; works with `updateDuration: 0` |

- **Quota: 50 timed refreshes per card per day** (resets 0:00) — `updateDuration` and `setFormNextRefreshTime` share it; **scheduled-time refreshes do not count**, so use them as free anchors.
- Refresh fires **only while the card is visible**; invisible cards get a catch-up refresh when next visible. There is no mechanism to wake an invisible card at an exact time — design values to be lazily recomputed correct-on-view, not clock-driven.
- AGC review rejects cards where `updateDuration` and `scheduledUpdateTime` are both absent while claiming periodic content.

## Cross-process images (fd + memory://)

`Image('file://…')` fails across the sandbox. Official path: open the sandbox file, pass the fd via `formImages`, render with `memory://`:

```ts
const file = fileIo.openSync(absPath, fileIo.OpenMode.READ_ONLY);
formProvider.updateForm(formId, formBindingData.createFormBindingData({
  imgName: 'figImage',
  formImages: { figImage: file.fd } as Record<string, number>
}));
// DO NOT closeSync the fd — launcher decodes asynchronously; system releases it with the form
```

Card side: `.backgroundImage('memory://' + this.imgName)`. To force re-decode on replacement, timestamp the key (`figImage_${Date.now()}`). If a card "doesn't refresh" despite pushes, the usual root cause is a state-tracking break (see `../../arkui-ui-patterns/references/state-pitfalls.md`), not fd caching.

## Click-through

`postCardAction(this, { action: 'router', abilityName: 'EntryAbility', params: {...} })` — `'router'` brings the app to foreground (own app only); `'message'` does **not** launch the app (common "tap does nothing" root cause; it only reaches `onFormEvent`). Receive params in both `onCreate` and `onNewWant`.

## Card-side layout/runtime limits (real-device verified)

- Effective card canvas ≈ **150vp**, not the 300px of demos — design to proportion, protect fixed bars with `layoutWeight` + `clip`.
- The card cannot measure its own dimension (`onAreaChange` unsupported); FormExtension pushes an `isWide` flag derived from `DIMENSION_KEY`.
- `Path`/`Polygon`/`Polyline` are unavailable — build icons from vp primitives (`Circle`/`Rect` + `rotate`/`clip`); `vp2px` is unusable in form context.
- `Span` has no `.opacity` — use 8-digit hex colors; `size` is a reserved component-member name; `.position()` cannot mix `x` with `bottom` (use `Edges` + translate).
- **No looping animation on cards**: `.animation` `iterations: -1` and `onFinish` re-trigger patterns freeze after one run. Play a single entry animation on the card; hand looping motion to the app page (trigger from `.onAppear`, not `aboutToAppear`). LiveForm overflow animation is unavailable to third-party atomic services.

## Transparent-background cards (5 requirements, any missing → white base)

1. `form_config` `transparencyEnabled: true`; 2. root container `.backgroundColor(Color.Transparent)`; 3. handle `HOST_BG_INVERSE_COLOR_KEY` text inversion; 4. AGC "背板透明卡片" open capability approved and checked; 5. **manual signing with a Debug Profile that binds the device UDID and the capability** — the default auto-debug signature makes the launcher ignore the AGC grant. Release Profiles have no UDID and fail local install (9568322). Full signing SOP: `../../harmony-release-compliance/references/signing-release-build.md`.

## Cross-process preferences consistency

Card process and main app each cache preferences XML: call a wrapped `refreshCache()` before cross-process-critical reads; `put()` is memory-only until `flush()` (a later `refreshCache` wipes unflushed writes); write all related keys then **one** flush (separate flushes get torn by the ~5s form process lifetime); design settlement functions idempotent (same snapshot → same result) instead of relying on locks.

Source: adapted from chen_jeff/harmony-os-skill (gitee; production-verified in shipped apps) and DengShiyingA/harmonyos-ai-skill (MIT). Quota/behavior figures are API 23-era — re-verify on newer SDKs.
