# TypeScript to ArkTS differences

Migration guidance adapted from DevEco CodeGenie. ArkTS shares syntax with TypeScript but does not support every dynamic TypeScript/JavaScript pattern.

## Preferred rewrites

- inline object shape → named interface/class
- loose structural object → explicit declared contract and constructor
- function expression → supported arrow function or named declaration
- nested function declaration → method, top-level function, or arrow value
- destructuring → explicit local bindings
- `delete`/shape mutation → construct/update an explicitly modeled value
- dynamic index/property reflection → typed field/method or bounded mapping
- catch type annotation → unannotated catch plus supported narrowing
- `typeof` type query → explicit intended type when the query form is unsupported

## Migration workflow

1. Preserve tests/behavior and capture compiler diagnostics.
2. Replace one unsupported pattern with a typed equivalent.
3. Run ETS check and module build.
4. Verify serialization, undefined/null behavior, callback binding, and API payload shape where semantics can differ.

Do not translate syntax mechanically across an entire codebase before proving a representative connected slice.
