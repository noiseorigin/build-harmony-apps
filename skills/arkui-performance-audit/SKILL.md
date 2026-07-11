---
name: arkui-performance-audit
description: Audit and improve ArkUI runtime performance from code first, then require DevEco Profiler evidence for unresolved or quantitative claims. Use when diagnosing slow first render, UI freezes, janky List scrolling, excessive component updates, layout churn, high CPU, image pressure, or expensive ArkUI state propagation.
---

# ArkUI Performance Audit

Start from code and a concrete symptom. Use `references/code-smells.md` for detailed checks and `references/report-template.md` for the result. Escalate to `../harmony-profiler-trace/SKILL.md` when runtime evidence is required.

## Workflow

1. Record the exact screen, interaction, device, build mode, data size, and symptom: startup, frame/jank, CPU, memory, freeze, or update storm.
2. Identify the component generation/state model used by the target code. Do not apply V1 decorator advice to V2 code or vice versa.
3. Trace state ownership and fan-out from the changed value to rendered subtrees.
4. Inspect list identity/data-source stability, repeated allocation in `build()`, synchronous work on the UI thread, layout depth, nested scrolling, image decode/resize, and animation scope.
5. Rank findings by expected user impact and evidence strength. Mark each as confirmed by code, plausible, or trace-backed.
6. Apply the smallest targeted fix; avoid architectural rewrites during a performance investigation.
7. Build and run the same flow. If the claim is quantitative or code review is inconclusive, capture comparable Profiler traces.

## Remediation defaults

- Narrow state ownership and observation scope.
- Keep stable identities and avoid recreating data sources or callbacks unnecessarily during render.
- Move parsing, sorting, formatting, I/O, image processing, and large derived work out of `build()` and the UI thread.
- Use lazy containers/data sources for large collections only when their lifecycle and identity rules are satisfied.
- Reduce avoidable layout nesting and measurement loops before adding caches.
- Bound image dimensions and decode work to the rendered need.
- Limit animations to the properties and subtrees that communicate the change.

## Verification

For code-only work, prove build and functional behavior and label performance impact as expected. For measured work, report raw artifacts, exact flow, run count, individual/median values, and before/after deltas under comparable conditions.

Do not claim that fewer lines, more components, a lazy API, or a cache is inherently faster. Require a causal explanation and proportionate evidence.
