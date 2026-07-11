---
name: arkts-runtime-fix
description: Parse, triage, fix, and verify ArkTS or JavaScript runtime crashes, jscrash logs, uncaught exceptions, white screens, and post-launch app exits. Use when builds pass but runtime fails, or when the user provides TypeError, ReferenceError, RangeError, BusinessError, faultlogger, hilog, or ArkTS stack evidence.
---

# ArkTS Runtime Fix

Prefer a concrete crash anchor before broad code exploration. This evidence-first workflow adapts DevEco CodeGenie's `arkts-runtime-fix` skill while using a portable local parser and explicit HDC commands.

## Existing evidence

Parse a local file or stdin:

```bash
python3 "<skill-root>/scripts/parse_crash.py" \
  --log "<crash-or-hilog-file>" \
  --bundle "<bundle-name>" \
  --format markdown
```

The structured output includes status, error type/message, suspected file, top frames, and next action. If no crash signature is found, request a narrower reproduction/log instead of guessing.

## No log yet

1. Resolve one explicit device with `../harmony-debugger-agent/SKILL.md`.
2. Reproduce once and record the exact action/time.
3. Inspect recent faultlogger entries first. Fetch the matching file with HDC when permitted.
4. Fall back to a bounded hilog capture only when faultlogger is unavailable or insufficient.
5. Parse the local artifact; do not repeatedly collect wider logs.

## Fix workflow

1. Start from the first app-owned `.ets`, `.ts`, `.js`, or native frame and the exact message.
2. Trace the failing value/API/lifecycle path in a narrow source slice.
3. Check current API preconditions, permissions, threading, and lifecycle timing for `BusinessError` or framework failures.
4. Apply the smallest root-cause fix. Do not replace it with retries, arbitrary delays, blanket null guards, or broad defensive rewrites.
5. Build, run the identical flow, and prove the original signature is absent while intended behavior succeeds.

## Evidence rules

- Prefer user reproduction steps over a simplistic stack-only assumption.
- Treat the first app frame as a starting point, not final causality.
- Separate cold-start, page lifecycle, interaction, async callback, worker, and native-boundary crashes.
- Never claim a fix from source reasoning alone.

Read `references/signatures.md` for common categories and collection boundaries.
