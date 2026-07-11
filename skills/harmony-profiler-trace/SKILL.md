---
name: harmony-profiler-trace
description: Capture, convert, inspect, and compare HarmonyOS DevEco Profiler htrace or bytrace performance evidence. Use when profiling startup, UI freezes, janky scrolling, CPU-heavy work, slow interactions, component time, or when a code-first ArkUI performance audit needs trace-backed proof.
---

# Harmony Profiler Trace

Capture one focused flow per trace. Pair with `../arkui-performance-audit/SKILL.md` for code-first hypotheses and `../harmony-debugger-agent/SKILL.md` for an identical build/run/reproduction setup.

## Core workflow

1. Write the exact start state, action, and stop condition. Avoid broad “use the app for a while” traces.
2. Record project revision, module, product, build mode, device model/system, bundle, and whether the run is warm or cold.
3. Build and launch the exact artifact to profile. Stabilize network and data where possible.
4. Capture a DevEco Profiler trace covering only the focused flow. Use the appropriate profiler lane for startup, UI freeze, CPU, component time, network, or memory.
5. Export the trace as `.htrace`/bytrace or an SQLite database. Preserve the raw artifact before analysis.
6. Convert and summarize with the bundled script:

```bash
python3 "<skill-root>/scripts/analyze_htrace.py" \
  "<capture.htrace-or.db>" \
  --out "<run-dir>/summary.md"
```

The script uses DevEco's bundled `trace_streamer` when conversion is required, inventories the schema, and reports duration-bearing tables without assuming one DevEco version's database layout.
7. Map hotspots back to app-owned code and the user-visible flow. Separate named first-party evidence from framework or scheduler noise.
8. Apply the smallest high-impact change, then recapture the same flow with comparable settings.

## Evidence gates

- Do not infer runtime cost from code alone in this skill; label code findings as hypotheses until a trace supports them.
- Do not interpret an empty, truncated, or conversion-failed database.
- Do not compare unlike devices, build modes, data sets, or flow boundaries without an explicit caveat.
- Do not call a table's longest row the root cause until it is mapped to the target process/thread and app-owned work.
- Prefer at least three comparable runs for noisy latency claims; report individual values as well as the median.

## Output

Use `references/report-template.md`. Include raw and derived artifact paths, capture conditions, exact flow, run count, top trace-backed findings, first-party mapping, before/after metrics, and remaining uncertainty.

If automated capture is unavailable, guide the user through DevEco Profiler and continue from the exported artifact. Never fabricate an automated capture capability that the installed MCP does not expose.
