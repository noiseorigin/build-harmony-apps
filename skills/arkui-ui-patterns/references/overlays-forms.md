# Overlays and forms

## Overlays

- Model mutually exclusive dialogs/sheets/menus with one selected state rather than unrelated booleans.
- Give the presented surface ownership of its local draft and dismissal behavior where practical.
- Preserve focus and return it predictably after dismissal.
- Use system back/outside-tap behavior intentionally; protect destructive or irreversible work.

## Forms

- Separate raw input, normalized value, validation state, and submission state.
- Validate locally where deterministic and server-side where authoritative.
- Show errors next to the field and provide an accessible summary/focus path for submission errors.
- Disable duplicate submissions while preserving retry and entered data.
- Use the appropriate keyboard/input type and handle keyboard avoid areas.
- Keep secrets out of logs, screenshots, state restoration, and accessibility announcements.

## Feedback

Use inline status for persistent/actionable information and transient feedback for brief confirmations. Error text should explain what happened, impact, and recovery without exposing internals.
