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

## Production red lines (device/build-verified)

- `throw` only `Error` instances (`arkts-limited-throw`); encode error codes as message prefixes for upstream branching.
- `PersistentStorage.persistProp` calls belong at file top level, before `@Entry` — inside a component they run too late.
- `@Builder` is for static composition only; anything needing data reactivity, internal state, or lifecycle must be a `@Component` (see also the builder-parameter tracking trap in arkui-ui-patterns `state-pitfalls.md`).
- No leading statements inside `build()` — precompute in `aboutToAppear` or getters.
- `$rawfile()` accepts literals only, not computed strings.
- Color literals are `#AARRGGBB` (alpha first); gradient `colors` arrays take strings, not ints.
- Every `ResultSet` closes in `try/finally`.
- `blur`/`backdropBlur` are real-time render costs — never inside scrolling list rows.
- `@LocalBuilder` binds `this` to the owning component; plain `@Builder` passed across components changes the receiver.
- `Record<string, X>` is the dictionary type; `object`/`any` are rejected.

Source class: linter/compiler-derived guidance adapted from DevEco CodeGenie; red lines from chen_jeff/harmony-os-skill (gitee), build-verified. Name the source class when citing a restriction.
