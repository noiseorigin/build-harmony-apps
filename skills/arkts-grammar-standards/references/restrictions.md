# ArkTS restrictions

These are linter/compiler-oriented summaries, not verbatim specification text. Verify rule names and exceptions with the current project.

## Common narrowed forms

- `var`, destructuring declarations/parameters/assignment, `delete`, `for...in`, generator functions, class expressions, and dynamic property modeling are commonly rejected or restricted.
- Avoid `any`/`unknown` as escape hatches; use an explicit model and narrowing supported by ArkTS.
- Avoid inline object type declarations and untyped object literals for reusable data.
- A catch clause should not add an unsupported explicit exception type annotation.
- Free functions must not depend on standalone `this`; pass the context explicitly.

## Function/object modeling

- Prefer named declarations and arrow-function values where the compiler requires them.
- Prefer direct property access with known identifiers over dynamic index access.
- Preserve runtime semantics when rewriting TypeScript patterns; “compiler accepts” is necessary but not sufficient.

## Sendable

- Use explicit field types and only supported sendable field/value types.
- Check constructor/initialization, capture, inheritance, and collection rules in the current ArkTS specification.
- Do not assume an object/array literal or ordinary class becomes sendable through an assertion.

Source class: linter/compiler-derived guidance adapted from DevEco CodeGenie. Name that source class when citing a restriction.
