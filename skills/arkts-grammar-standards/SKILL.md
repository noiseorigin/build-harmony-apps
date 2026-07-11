---
name: arkts-grammar-standards
description: Apply ArkTS syntax rules, static restrictions, TypeScript-to-ArkTS differences, Sendable constraints, and syntax-compliance review. Use when writing or reviewing ArkTS, explaining why syntax is accepted or rejected, porting TypeScript/JavaScript, or choosing a valid typed rewrite.
---

# ArkTS Grammar Standards

Prefer the installed compiler and current ArkTS specification over model memory. This skill adapts DevEco CodeGenie's separation between guide-oriented syntax, linter-derived restrictions, and TypeScript migration differences.

Read in this order as needed:

1. `references/basic-syntax.md` for normal authoring.
2. `references/restrictions.md` for forbidden/narrowed forms and `Sendable`.
3. `references/ts-diff.md` for migration rewrites.

## Source discipline

- Label a rule as compiler evidence, official specification/guide, API documentation, project linter policy, or migration guidance.
- Do not present a linter-derived rule as verbatim language specification.
- Check the project's ArkTS/linter version before universal claims; restrictions evolve.
- When code is available, prefer the exact diagnostic plus a minimal compiler-accepted rewrite.

## Response or review shape

State the topic, source class, matching diagnostic/reference, why it applies, and the narrow rewrite. Build or run `check_ets_files` when the user asked for a code change rather than an explanation.

## Boundaries

- Keep syntax guidance separate from framework API availability.
- Do not broaden a syntax fix into architecture or UI refactoring.
- Avoid `any`, `ESObject`, unsafe assertions, or dynamic workarounds merely to silence a diagnostic.
- Preserve runtime semantics while replacing unsupported TypeScript forms.
