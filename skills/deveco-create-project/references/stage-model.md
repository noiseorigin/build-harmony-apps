# Stage model and project layout

Pattern quick-reference, checked 2026-07. Verify lifecycle/config details with `devecocli docs search stage model` or current Huawei docs.

## Project layout

```
MyApp/
├─ AppScope/
│  ├─ app.json5                 # global app config (bundleName, icon, label)
│  └─ resources/
├─ entry/                       # main HAP (entry module)
│  ├─ src/main/
│  │  ├─ ets/
│  │  │  ├─ entryability/EntryAbility.ets   # UIAbility subclass
│  │  │  └─ pages/Index.ets
│  │  ├─ resources/
│  │  └─ module.json5           # module config, abilities, permissions
│  └─ build-profile.json5
├─ oh-package.json5             # ohpm dependencies
└─ build-profile.json5          # project-level: products, signingConfigs, SDK versions
```

## Component types

- **UIAbility** — UI entry point; one instance per task.
- **ExtensionAbility** — background/extension scenarios: `FormExtensionAbility` (home-screen widget), `WorkSchedulerExtensionAbility` (deferred tasks), `BackupExtensionAbility`, `InputMethodExtensionAbility`; `ServiceExtensionAbility` is system-app only.
- **AbilityStage** — module-level lifecycle container, one per HAP.
- **WindowStage** — window container scoped to a UIAbility.

## UIAbility lifecycle

```ts
import { UIAbility, Want, AbilityConstant } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {}
  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err) => {});
  }
  onForeground(): void {}
  onBackground(): void {}
  onWindowStageDestroy(): void {}
  onDestroy(): void {}
  onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void {}  // singleton relaunch
}
```

Order on cold start: `onCreate → onWindowStageCreate → onForeground`. `onNewWant` fires instead of `onCreate` when a singleton-mode ability is started again.

## Launching another ability

```ts
import { common, Want } from '@kit.AbilityKit';

const ctx = getContext(this) as common.UIAbilityContext;
const want: Want = { bundleName: 'com.example.app', abilityName: 'DetailAbility', parameters: { id: 42 } };
ctx.startAbility(want);   // or startAbilityForResult
```

## module.json5 essentials

```json5
{
  "module": {
    "name": "entry",
    "type": "entry",                // entry | feature | shared
    "deviceTypes": ["phone", "tablet", "2in1"],
    "abilities": [{
      "name": "EntryAbility",
      "srcEntry": "./ets/entryability/EntryAbility.ets",
      "startWindowIcon": "$media:startIcon",
      "startWindowBackground": "$color:start_window_background",
      "skills": [{ "actions": ["action.system.home"], "entities": ["entity.system.home"] }]
    }],
    "requestPermissions": [{ "name": "ohos.permission.INTERNET" }]
  }
}
```

`module.json5` is not `package.json` — permissions, abilities, and device types live here; dependencies live in `oh-package.json5`.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), aligned with Stage-model guides in Huawei docs.
