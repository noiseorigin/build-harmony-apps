# Harmony session contract

Resolve once, retain during the task, and update only when the user or build changes it.

| Field | Source priority | Notes |
| --- | --- | --- |
| project root | explicit path → nearest `build-profile.json5` | Initialize CodeGenie with the absolute root. |
| module | user request → root `modules[]` → sole entry module | Usually `entry`, but never assume in a multi-module app. |
| product | user request → selected DevEco product → sole product | Preserve product-specific resources and signing. |
| target | user request → module target applied to product | Distinct from the device. |
| build mode | user request → current task → `debug` | Do not profile/debug a release build by accident. |
| UIAbility | user request → `mainElement`/ability declarations | Use the exact case-sensitive name. |
| bundle name | `AppScope/app.json5` | Do not derive it from a display label. |
| device id/HVD | explicit request → sole connected target → selected simulator | Never mutate several connected targets implicitly. |
| SDK/API | project build profile → installed SDK metadata | Report beta/preview stages. |

## Invariants

- Build, install, launch, logs, UI automation, screenshots, profiling, and tests must refer to the same intended module/product/build/device tuple.
- After a build-configuration change, revalidate the artifact and ability/bundle context.
- If a tool omits a field and uses an implicit default, record the inferred value in the result.
- Do not persist secrets, signing material, or device identifiers in project files for session convenience.
- Direct DevEco-bundled Hvigor may require `DEVECO_SDK_HOME=<DevEco Contents/sdk>` and `JAVA_HOME=<DevEco bundled JBR>` in the process environment. Keep them session-local.
