---
name: harmony-test-triage
description: Discover, run, narrow, and diagnose HarmonyOS ArkTS unit, integration, and Hypium UI tests with project-defined Hvigor tasks and device evidence. Use when tests fail, hang, flake, are not discovered, require a simulator/device, or need a regression check after a code change.
---

# Harmony Test Triage

Use the project's own test configuration and Hvigor task graph. Do not hardcode a test task name from another HarmonyOS or OpenHarmony version.

## Workflow

1. Identify the failing test layer, module, product, target, build mode, device requirement, and exact failure output.
2. Inspect `oh-package.json5`, module manifests, test source sets, and project scripts. Run the project wrapper's `tasks` or `taskTree` to discover supported commands.
3. Reproduce the smallest failing test or suite without changing production code.
4. Classify the failure using `references/failure-taxonomy.md`: discovery/configuration, compile/type, environment/device, fixture/state, timing/async, assertion/product regression, or framework/tooling.
5. Preserve the first actionable stack, assertion, artifact path, and device log window. Ignore repeated wrapper noise.
6. Fix the root cause with the smallest scope. Do not weaken a valid assertion merely to make the run green.
7. Re-run the narrow test, its containing suite, and a proportionate regression set. Build the affected module/app afterward when the test task does not already do so.

## Device tests

- Resolve a single explicit target through `../harmony-debugger-agent/SKILL.md`.
- Establish or reset fixture state through supported app/test APIs. Do not clear unrelated app/device data.
- Re-query UI state before interaction; avoid fixed sleeps when a state or element condition is available.
- Capture screenshot, UI tree, verification log, and hilog only for the failing window.

## Flake rules

- Do not call a failure flaky from one pass and one failure.
- Repeat under the same conditions, record pass/fail sequence and duration, and identify the uncontrolled dependency.
- Replace arbitrary delay increases with deterministic readiness, clock, network, or fixture control.

## Output

Report the discovered command, environment, narrow reproduction, failure class, evidence, change, narrow rerun, broader regression result, and any unverified device/system dependency.
