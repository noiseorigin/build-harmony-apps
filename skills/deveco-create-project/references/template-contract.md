# Template contract

The bundled template creates one Stage-model HarmonyOS application with:

- root `build-profile.json5`, `oh-package.json5`, `hvigorfile.ts`, and Hvigor config
- `AppScope/app.json5` and app resources
- one `entry` HAP module and `default` target/product
- one exported `EntryAbility`
- one ArkUI page and page profile
- phone and tablet device declarations

The creation script substitutes app name, bundle, API/SDK string, and model version derived from the installed DevEco Studio. It uses legacy `platform(api)` SDK values below API 26 and the full MSF value used by API 26+. It refuses a non-empty destination and verifies required files after copying.

## Use another official template for

- atomic service, HAR/HSP, shared library, widget/form, cross-platform ArkUI-X, C++/NAPI, enterprise template, custom signing, or product flavors
- organization-mandated architecture or design-system starter
- an installed SDK generation rejected by this template's compatibility check

## Source and adaptation

The deterministic copy/detect/verify method comes from DevEco CodeGenie's `deveco-create-project` at commit `2a9a5193c122798a451520cf6a4a5a0553e62f93`. The upstream API 17–22 template is not copied. The local template is independently reduced and aligned with DevEco's current New Project/Empty Ability shape, then build-tested by this plugin's tests.
