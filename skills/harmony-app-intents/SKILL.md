---
name: harmony-app-intents
description: Design, implement, and validate HarmonyOS Intents Kit actions, shared intent data, and InsightIntentExecutor entry points for Celia/Xiaoyi suggestions, voice invocation, local search, recommendations, and other system surfaces. Use when exposing app functions or content outside the app, adding insight_intent profiles, handling system intent calls, or reviewing an Intents Kit integration.
---

# Harmony App Intents

Expose the smallest useful set of actions and entities. Intents Kit is an ecosystem integration with domain, SID, device, and acceptance constraints; a local build alone does not prove system-surface availability.

Read `references/official-integration.md` before editing. Use current Huawei documentation and the official sample as primary sources because domains, accepted intents, schemas, and onboarding requirements change.

## Core workflow

1. Identify one to three high-value verbs that users need outside the app. Do not mirror the navigation tree.
2. Confirm that the target vertical/domain and intent names are currently open and that the app satisfies onboarding, SID, device, system, SDK, and acceptance requirements.
3. Define a narrow parameter/result contract. Keep executor payloads separate from the app's full persistence model.
4. Add or update `resources/base/profile/insight_intent.json` and the matching module/resource declarations using the current official schema.
5. Implement a thin `InsightIntentExecutor` from `@kit.AbilityKit`. Dispatch on the declared intent name, validate `Record<string, Object>` parameters, delegate business logic to an existing service, and return a deliberate `insightIntent.ExecuteResult`.
6. For intent sharing/recommendation scenarios, model `insightIntent.InsightIntent` data and use `insightIntent.shareIntent` from `@kit.IntentsKit` only after validating the official schema and SID flow.
7. Route foreground execution through one predictable UIAbility handoff. Keep system entry handling idempotent and avoid hidden global side effects.
8. Build and run local executor tests or app-level checks. Then perform the required real-device/system-surface validation and acceptance process.

## Strong defaults

- Keep the executor thin; domain logic remains in services or models.
- Use stable identifiers and display-safe entity data.
- Return explicit failure results for unknown intent names or invalid parameters.
- Log intent name and non-sensitive outcome, not private payloads.
- Treat shared intent lifecycle operations—share, refresh, delete—as data lifecycle, not screen routing.

## Evidence levels

- **Implemented:** profile and executor exist and compile.
- **Locally exercised:** the handler ran with representative parameters and produced the expected app result.
- **System verified:** a supported Huawei device/system surface invoked or displayed the intent.
- **Accepted:** the integration completed Huawei's current review/acceptance requirements.

State the achieved level exactly. Never call an integration “available in Xiaoyi/Celia” from compilation evidence alone.

## Anti-patterns

- Inventing a domain or intent name not listed by current official guidance.
- Copying the music sample's names or payloads into an unrelated app.
- Encoding entire database records in an intent payload.
- Duplicating business logic in the executor.
- Claiming emulator support when the chosen capability requires a standard-system Huawei phone or tablet.
