# Permissions

Declaration + runtime flow, checked 2026-07. Verify permission names/levels with `devecocli docs search <permission>` or current docs — availability and grant rules change per API level (e.g. `READ_IMAGEVIDEO` behavior changed under API 26 rules).

## Declaration (`module.json5`)

```json5
"requestPermissions": [
  { "name": "ohos.permission.INTERNET" },                     // system_grant: declaration is enough
  {
    "name": "ohos.permission.CAMERA",                         // user_grant: reason + usedScene REQUIRED
    "reason": "$string:permission_camera_reason",
    "usedScene": { "abilities": ["EntryAbility"], "when": "inuse" }
  }
]
```

Missing `reason`/`usedScene` on a user_grant permission is a build/review failure. The reason string is user-visible and AGC-reviewed — write the actual purpose.

## Runtime flow (check → request → settings fallback)

```ts
import { abilityAccessCtrl, bundleManager, common } from '@kit.AbilityKit';

const atManager = abilityAccessCtrl.createAtManager();

// 1. Check
const bundleInfo = await bundleManager.getBundleInfoForSelf(bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION);
const status = await atManager.checkAccessToken(bundleInfo.appInfo.accessTokenId, 'ohos.permission.CAMERA');
if (status === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) { /* proceed */ }

// 2. Request (first ask)
const result = await atManager.requestPermissionsFromUser(context, ['ohos.permission.CAMERA']);
if (result.authResults[0] === 0) {
  // granted
} else if (result.dialogShownResults?.[0]) {
  // user saw the dialog and denied — show in-app guidance; do NOT re-pop
} else {
  // 3. Permanently denied earlier — settings dialog fallback
  const statuses = await atManager.requestPermissionOnSetting(context, ['ohos.permission.CAMERA']);
  // statuses[0]: 0 granted, -1 denied
}
```

## Rules

- Request at point of use, one capability at a time; batch only permissions serving the same user action.
- Prefer permissionless system surfaces when the task allows: CameraPicker (capture), Scan default UI, PhotoViewPicker/DocumentViewPicker (user-mediated file access) — each avoids a user_grant dialog entirely.
- Secrets go in Asset Store Kit; location has separate `APPROXIMATELY_LOCATION` (coarse) vs `LOCATION` (fine) — request coarse unless fine is justified.
- Permission dialogs require a real device/emulator — the Previewer never shows them; verification must drive the actual grant flow.
- On API 21-era SDKs the `Permissions` type and `requestPermissionsFromUser` overloads have known compile traps — see `../../arkts-error-fixes/references/triage-map.md`.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), aligned with official access-control guides.
