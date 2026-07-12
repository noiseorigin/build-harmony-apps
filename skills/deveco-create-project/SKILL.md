---
name: deveco-create-project
description: Create a minimal HarmonyOS Stage-model ArkTS application project with a deterministic template, installed DevEco SDK detection, bundle/name substitution, and integrity checks. Use for new app scaffolding or initializing an empty directory before building with DevEco CodeGenie.
---

# DevEco Create Project

Never reproduce project files from memory. Scaffold order: **official `devecocli create` when installed** (detect via `devecocli --version`) → the bundled deterministic template script → DevEco Studio's New Project wizard for anything beyond a minimal Stage-model app.

```bash
devecocli create --app-name MyApp [--project-path ./dir] [--bundle-name com.x.y] [--api-level 23]
```

`devecocli create` uses Huawei's current official template and API detection (`../harmony-debugger-agent/references/deveco-cli.md`). The bundled script below is the offline fallback; it adapts DevEco CodeGenie's deterministic template-copy pattern while reading installed DevEco metadata. Platform/version context: `references/platform-baseline.md`; Stage-model structure: `references/stage-model.md`; build hardening: `references/build-sign-release.md`.

## Inputs

- Parent directory and app name are required.
- Derive a valid bundle name only when the user has not provided one; default to `com.example.<normalized-name>` and report it.
- Use the installed SDK/API by default. Never guess an API level.
- Use the bundled template for a minimal Stage-model app. For atomic service, HAR/HSP, C++, signing, distribution, or organization-specific architecture, use DevEco Studio's current official wizard/template instead of silently reshaping this template.

## Create

```bash
python3 "<skill-root>/scripts/create_project.py" \
  --parent "<parent-directory>" \
  --name "<AppName>" \
  --bundle "<bundle.name>"
```

Use `--api-level` only when the user explicitly chose a level present in the installed SDK. Use `--force-empty` only for an existing empty destination; never merge a scaffold into a non-empty directory.

## Verify

1. Read the JSON result and require `verified: true`.
2. Confirm `build-profile.json5`, `AppScope/app.json5`, module config, UIAbility, page profile, and entry page exist.
3. Initialize CodeGenie with the generated root and run a clean module/app build through `../harmony-debugger-agent/SKILL.md`.
4. Do not add features until the scaffold builds. If the detected SDK is a beta or preview, report that fact.

## Boundaries

- Do not invent signing credentials or commit `local.properties` with machine-specific SDK paths.
- Do not overwrite a destination containing user files.
- Do not claim a template is future-proof; compare its model/API values with current DevEco metadata on every run.
- If the installed SDK generation is newer than the template contract or the build rejects it, stop and use DevEco Studio's official New Project wizard, then resume from build verification.

Read `references/template-contract.md` for generated structure and adaptation rules.
