---
name: deveco-create-project
description: Create a minimal HarmonyOS Stage-model ArkTS Empty Ability project with the official devecocli first, a deterministic local fallback, and integrity checks. Use for new app scaffolding or initializing an empty directory before building with DevEco CodeGenie.
---

# DevEco Create Project

Never reproduce project files from memory. For a minimal Stage-model ArkTS **Empty Ability**, scaffold in this order: official `devecocli create` 1.3.0+ → bundled deterministic template script → DevEco Studio's New Project wizard. Detect the CLI with `devecocli --version`; for versions other than the verified 1.3.x contract, also inspect `devecocli create --help` before use.

The official CLI creates only the `Empty Ability` template. Use DevEco Studio's current New Project wizard for atomic services, HAR/HSP, widgets/forms, C++/NAPI, ArkUI-X, signing/product-flavor templates, or organization-specific starters.

`devecocli create` uses the official CLI's bundled Empty Ability template and API detection (`../harmony-debugger-agent/references/deveco-cli.md`); it is not the full DevEco Studio New Project wizard. The local script is an offline fallback that reads installed DevEco metadata. Platform/version context: `references/platform-baseline.md`; Stage-model structure: `references/stage-model.md`; build hardening: `references/build-sign-release.md`.

## Inputs and destination

- Let `P` be the parent directory, `N` the app name, and `D = P/N` the final project root. Pass **`D`**, not `P`, to `--project-path`; the CLI uses that path as-is. Omitting the option defaults to `./N`, so prefer an explicit absolute `D`.
- `N` must be 1–200 characters, start with an ASCII letter, and contain only ASCII letters, digits, or underscores: `^[A-Za-z][A-Za-z0-9_]*$`.
- Derive a valid bundle name only when the user has not provided one; default to `com.example.<normalized-name>` and report it.
- Use the installed SDK/API by default. Never guess an API level.
- Before either path, refuse a non-empty `D`; never overwrite or merge into user files.

## Primary: official CLI

```bash
devecocli --version
devecocli create \
  --app-name "Notes" \
  --project-path "/absolute/parent/Notes" \
  --bundle-name "com.example.notes"
```

Omit `--api-level` to use the installed SDK. Pass it only when the user explicitly chose a level supported by the installed SDK. If the CLI reports that no toolchain was found and it is using a placeholder API, stop instead of accepting the implicit API 23 default. Do not bypass CLI validation with the fallback.

The CLI writes human-readable text, **not JSON**. Require a zero exit status, then independently require these files under `D`:

- `build-profile.json5`, `oh-package.json5`, `hvigor/hvigor-config.json5`
- `AppScope/app.json5`, `entry/build-profile.json5`, `entry/src/main/module.json5`
- `entry/src/main/ets/entryability/EntryAbility.ets`
- `entry/src/main/ets/pages/Index.ets`
- `entry/src/main/resources/base/profile/main_pages.json`

Do not treat output text such as `Template integrity check passed` as sufficient filesystem verification.

If the CLI fails, inspect `D` before fallback:

- If `D` exists and is non-empty, stop and report the partial directory. Do not delete it automatically, run the fallback into it, or merge scaffolds.
- If `D` does not exist, fallback is allowed. If `D` exists but is confirmed empty, fallback is allowed only with `--force-empty`.

## Fallback: bundled template

Use only when `devecocli` is unavailable or an environment/tool failure occurred before it wrote project files:

```bash
python3 "<skill-root>/scripts/create_project.py" \
  --parent "<P>" \
  --name "<N>" \
  --bundle "<bundle.name>"
```

This script, unlike the CLI, emits JSON. Require a zero exit status, parse the JSON, require `verified: true`, and confirm `projectRoot` resolves exactly to `D`. Then perform the same filesystem checks listed for the CLI. Use `--api-level` only for a user-selected installed level; use `--force-empty` only for an existing confirmed-empty `D`.

## Build verification

Initialize CodeGenie with `D` and run a clean module/app build through `../harmony-debugger-agent/SKILL.md`. Do not add features until the scaffold builds. If the detected SDK is beta/preview, report it.

## Boundaries

- Do not invent signing credentials or commit `local.properties` with machine-specific SDK paths.
- Do not overwrite a destination containing user files.
- Do not claim a template is future-proof; compare its model/API values with current DevEco metadata on every run.
- If the installed SDK generation is newer than the template contract or the build rejects it, stop and use DevEco Studio's official New Project wizard, then resume from build verification.

Read `references/template-contract.md` for generated structure and adaptation rules.
