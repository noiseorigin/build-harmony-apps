# Share Kit, App Linking, startAbilityByType, app continuation

Checked 2026-07. Verify with `devecocli docs search <API>` or current docs.

## Share Kit (system share sheet)

```ts
import { systemShare } from '@kit.ShareKit';
import { uniformTypeDescriptor } from '@kit.ArkData';
const data = new systemShare.SharedData({
  utd: uniformTypeDescriptor.UniformDataType.HYPERLINK,   // or PLAIN_TEXT / HTML / IMAGE / FILE (pass uri)
  content: 'https://example.com/article/123',
  title: 'Title', description: 'Preview'
});
new systemShare.ShareController(data).show(this.context,
  { previewMode: systemShare.SharePreviewMode.DEFAULT, selectionMode: systemShare.SelectionMode.SINGLE });
```

Sharing sandbox images requires passing the context so the receiver gets URI authorization — a `show()` without context yields a receiver that cannot read the file.

## App Linking (deep links)

`module.json5` ability skills:

```json5
"skills": [{
  "entities": ["entity.system.home", "entity.system.browsable"],
  "actions": ["ohos.want.action.home", "ohos.want.action.viewData"],
  "uris": [{ "scheme": "https", "host": "example.com", "path": "/detail" }],
  "domainVerify": true
}]
```

Handle in **both** entry paths: `onCreate` (cold start) and `onNewWant` (running). Parse `want.uri` with `url.URL.parseURL`, stash params (e.g. `AppStorage.setOrCreate('linkId', …)`), route in `onWindowStageCreate` (cold) or via a `@StorageLink`+`@Watch` flag (warm). `domainVerify: true` requires the domain's assetlinks file to pass verification.

## startAbilityByType

```ts
context.startAbilityByType('navigation', {
  sceneType: 1, destinationLatitude: 39.9042, destinationLongitude: 116.4074, destinationName: 'Beijing'
} as Record<string, Object>);
// types: navigation, browser, email, finance, transit, ...
```

Opens the user's chosen app of that category — no bundle name coupling.

## App continuation (cross-device, 应用接续)

- `module.json5` ability: `"continuable": true`; different ability names across devices link via `"continueType": ["myApp_main"]`.
- Source: `onContinue(wantParam)` — write migration data (< ~100KB; larger via distributed data object), check target version, return `AGREE`/`MISMATCH`.
- Target: in `onCreate`/`onNewWant`, if `launchParam.launchReason === CONTINUATION`, read `want.parameters` and `this.context.restoreWindowStage(storage)`.
- Gate per page with `setMissionContinueState(ACTIVE | INACTIVE)`.
- Runtime prerequisites (state these when debugging "continuation not offered"): same Huawei account, Wi-Fi+BT on, Continuation enabled in Settings, app installed on both devices.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official guides.
