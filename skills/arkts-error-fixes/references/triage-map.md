# ArkTS diagnostic triage map

| Signal | Inspect first | Avoid |
| --- | --- | --- |
| unsupported syntax/linter rule | exact rule, ArkTS version, grammar references | replacing with `any` or suppression |
| type/overload mismatch | installed SDK `.d.ts`/declaration, generic and nullability context | blind cast or copying old signature |
| ArkUI decorator/state error | component generation, owner/parameter/event semantics, API level | mixing V1/V2 decorators by name |
| API unavailable/missing export | target/compatible SDK, Kit import, SysCap, current docs | guessing package names |
| import/OHM URL/module | root/module package config, normalized path/case, exported index | editing unrelated call sites |
| resource/profile | resource type/name/qualifier and JSON5/profile schema | hardcoded literal as permanent bypass |
| Hvigor/model/product/target | project/task graph, modelVersion, build profile, selected product | using a task from another project |
| native bridge | C/C++ diagnostic, generated bindings, ABI/types/lifetime | fixing only the ArkTS surface |

## Error ordering

Start with the earliest causal error in the first failing task. Rebuild after each small cluster because later errors may be cascades. Preserve the full diagnostic and related notes until the final build is green.

## Recipe policy

DevEco CodeGenie's public `arkts-error-fixes` catalog is useful for candidate categories, but individual API recipes can age. Reproduce every recipe against the installed SDK/compiler before applying it.
