# ArkTS runtime signatures

| Signature | Common category | Evidence to inspect |
| --- | --- | --- |
| `TypeError` property/call | null/undefined, wrong payload, lifecycle order | message, first app frame, value initialization and producer |
| `ReferenceError` | wrong scope/import, stale generated symbol, callback capture | module path, bundle build, closure owner |
| `RangeError` | index/bounds, recursion, oversized operation | input size, loop/stack, collection bounds |
| `BusinessError`/parameter error | framework precondition, permission, unsupported state/API timing | numeric code, current API docs, permissions, lifecycle/thread |
| white screen without exit | render exception, routing/resource failure, blocked UI thread | faultlog/hilog window, page load result, profiler if frozen |
| native signal/abort | NAPI/C++ lifetime, thread/ABI, invalid memory | native tombstone/stack and symbols; do not diagnose from ArkTS alone |

## Collection boundary

Prefer, in order: user-provided crash artifact, matching recent faultlogger file, bounded hilog around a fresh reproduction. Record device, bundle, app revision, system, exact action, and timestamp. Redact tokens, personal data, and unrelated app logs.

## Verification

The original action must complete, the original signature must be absent, and a relevant regression path must still work. A defensive guard that hides the crash while dropping the user action is not a valid fix.
