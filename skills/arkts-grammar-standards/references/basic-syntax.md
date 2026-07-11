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

Primary source: current ArkTS specification and language guide in Huawei/OpenHarmony documentation. Compiler diagnostics are authoritative for the installed toolchain.
