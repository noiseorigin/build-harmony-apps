---
name: deveco-create-project
description: Create a minimal HarmonyOS Stage-model ArkTS application project with a deterministic template, installed DevEco SDK detection, bundle/name substitution, and integrity checks. Use for new app scaffolding or initializing an empty directory before building with DevEco CodeGenie.
---

# DevEco Create Project

Use the bundled script instead of reproducing project files from memory. This workflow adapts DevEco CodeGenie's deterministic template-copy pattern while reading the currently installed DevEco metadata.

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
