# ArkTS basic syntax

Guide-oriented summary adapted from DevEco CodeGenie's ArkTS grammar skill. Verify against the current ArkTS specification/compiler.

## Declarations and types

- Prefer `const` for unchanged bindings and `let` otherwise; do not use `var`.
- Use explicit types at public boundaries, for fields, and when inference obscures intent.
- Prefer named interfaces/classes for reusable contracts and data models.

## Classes and interfaces

- Declare fields in the class and initialize a valid state in the constructor.
- Use named interfaces for contracts and explicit `implements` relationships.
- Prefer constructor-based instances and declared members over loose structural mutation.

## Functions

- Use methods, top-level functions, or arrow-function values supported by the project's ArkTS version.
- Give non-obvious/public return types explicitly.
- Avoid JavaScript coercion and dynamic reflection; use typed conversions and direct property access.

## Object literals

Provide an explicit contextual named type. Avoid using an inline object-literal type as a long-lived public model.

## Naming and formatting (official coding style)

| Element | Convention | Example |
|---|---|---|
| Classes, structs, enums | UpperCamelCase | `PersonInfo`, `ColorType` |
| Variables, parameters, methods | lowerCamelCase | `userName`, `getUserInfo()` |
| Constants | UPPER_SNAKE_CASE | `MAX_VALUE` |
| Booleans | `is`/`has`/`can` prefix | `isVisible`, `hasPermission` |

2-space indent, max 120 chars/line, K&R braces, always `{}` for if/for/while.

## High-performance rules (official best practices)

1. `const` for unchanging values — enables engine optimization.
2. Never mix int and float in one variable (`let n = 1; n = 1.1;` boxes).
3. TypedArrays (`Int8Array`, `Float32Array`) for numeric computation.
4. No sparse arrays — `arr[9999] = 0` degrades to hash-table storage.
5. No mixed-type arrays — `[1, "a", 2]` deoptimizes.
6. Cache property lookups outside hot loops.
7. No exception throwing in perf-critical loops — use sentinel values.
8. Minimize closures in hot paths — pass values as parameters.
9. Prefer built-in Array methods (`forEach`/`map`/`filter`/`reduce`).
10. Keep `build()` pure — load data in `aboutToAppear()`.
11. `HashMap` over `Record` for heavy key-value operations.
12. Reduce multi-level indirect exports; prefer direct `export { foo } from './module'`.
13. `import lazy { Foo } from './heavy'` for modules not needed at startup.

Primary source: current ArkTS specification and language guide in Huawei/OpenHarmony documentation. Compiler diagnostics are authoritative for the installed toolchain. Performance rules adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official best practices.
