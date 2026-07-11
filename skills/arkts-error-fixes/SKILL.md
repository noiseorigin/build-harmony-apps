---
name: arkts-error-fixes
description: Diagnose and fix ArkTS compiler, type-checker, linter, resource, module, and ArkUI decorator errors with DevEco CodeGenie checks and rebuild proof. Use immediately after a HarmonyOS build or ETS check fails, or when the user supplies ArkTS diagnostics and wants a fix.
---

# ArkTS Error Fixes

Anchor every fix to the current diagnostic and installed SDK. Do not apply a remembered recipe solely because the message looks similar.

Read `references/triage-map.md`. Pair with `../arkts-grammar-standards/SKILL.md` for language restrictions and `../arkui-view-refactor/SKILL.md` only when the error exposes a structural state-management problem.

## Workflow

1. Preserve the first compiler invocation, error code/message, file, line, related notes, module, product, target, and SDK/build-tool versions.
2. Use `mcp__deveco-codegenie__check_ets_files` for focused ETS diagnostics when available. Use `check_cpp_files` for native sources.
3. Reproduce with the narrowest project-defined build task. Ignore cascades until the earliest causal error is resolved.
4. Classify: ArkTS restriction/type, ArkUI decorator/state, API availability/signature, import/module/OHM URL, resource/profile, Hvigor/configuration, native bridge, or generated code.
5. Inspect the installed SDK declarations or current official API docs for unfamiliar `@kit.*`/`@ohos.*` signatures.
6. Make the smallest semantic fix. Avoid broad casts, suppression, arbitrary defaults, and unrelated formatting churn.
7. Re-run the focused check, then rebuild the affected module/app. If behavior could change, launch and verify the relevant flow.

## Evidence rules

- A disappearing error with a new earlier error is not completion.
- A type assertion is not a fix unless the runtime invariant is demonstrated.
- A code snippet from an older API is only a candidate until it compiles against the current project.
- Resource/profile and module errors require validating the referenced file and package path, not only the ArkTS call site.

## Output

Report the causal diagnostic, category, source evidence, minimal change, focused check result, full build result, and any runtime verification required.
