# Preview and verification

## Fixtures

Create deterministic, non-sensitive fixtures for primary, loading, empty, error, long-text, large-list, and selected states that materially affect the component. Inject services/models rather than calling live backends from Preview.

## Verification ladder

1. ETS check/lint for edited sources.
2. Affected module/app build.
3. Preview render for structural states where supported.
4. Runtime launch and current UI tree.
5. Focused actions and post-action assertions/screenshots.
6. Relevant unit/UI test and regression flow.

Use `../../harmony-runtime-preview/SKILL.md` for visual matrices and `../../harmony-debugger-agent/SKILL.md` for runtime control. Compilation alone does not prove layout or interaction.
