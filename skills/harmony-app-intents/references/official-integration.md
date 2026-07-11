# Intents Kit official integration notes

Verify current details before implementation:

- Product page: https://developer.huawei.com/consumer/cn/sdk/intents-kit/
- Official sample: https://gitcode.com/HarmonyOS_Samples/intents-kit-samplecode-clientdemo-arkts
- Huawei developer documentation: https://developer.huawei.com/consumer/cn/doc/

## Confirmed sample structure

The reviewed official sample uses:

- `insightIntent` from `@kit.IntentsKit` for `InsightIntent` data and `shareIntent`.
- `InsightIntentExecutor` and `insightIntent` from `@kit.AbilityKit` for invocation.
- `resources/base/profile/insight_intent.json` entries containing intent name, domain, version, executor source, UIAbility, and execute modes.
- An executor method named `onExecuteInUIAbilityForegroundMode` in the current sample source. Check the installed SDK declaration for exact casing/signature before editing.

The sample is a music-domain example. Reuse its structure, not its intent names or payload.

## Integration checklist

1. Confirm open vertical/domain and exact intent names.
2. Confirm required SDK/system/device and whether simulator testing is supported.
3. Confirm SID/account/agreement and application/acceptance steps.
4. Declare profile entries and module resource references.
5. Implement foreground/background modes supported by the chosen intent.
6. Validate parameters, privacy, error results, idempotency, and app handoff.
7. Test locally, then on a supported standard-system Huawei device and the intended system surface.

The official sample reviewed in July 2026 states that developers cannot independently complete all intent sharing/call acceptance and require Huawei contact assistance. Recheck this restriction; do not assume it has remained unchanged.
