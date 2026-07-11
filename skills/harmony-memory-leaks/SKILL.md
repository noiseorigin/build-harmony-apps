---
name: harmony-memory-leaks
description: Investigate HarmonyOS memory growth, leaked ArkTS or native objects, retained UI pages, image pressure, and before/after leak evidence with DevEco Profiler snapshots and repeatable comparisons. Use when memory rises across a flow, pages fail to release, the app is killed under pressure, or a leak fix needs proof.
---

# Harmony Memory Leaks

Use DevEco Profiler as the source of runtime memory evidence. This plugin can compare normalized snapshot exports, but it does not pretend to provide an iOS memgraph-equivalent ownership graph when DevEco has not exported one.

## Core workflow

1. Define the expected lifetime of the suspected object: process, account/session, page, component, request, worker, or native resource.
2. Build and launch the exact app configuration. Warm up once if initialization noise is not the target.
3. Capture a baseline after reaching a stable state.
4. Perform the create/use/release flow a fixed number of times, return to the same stable state, and allow expected asynchronous cleanup to finish.
5. Capture the post-flow snapshot with the same Profiler mode and device.
6. Export or normalize rows to `type,count,shallow_size,retained_size`, then compare:

```bash
python3 "<skill-root>/scripts/compare_memory_snapshots.py" \
  "<before.csv-or-json>" "<after.csv-or-json>" \
  --out "<run-dir>/memory-delta.md"
```

7. Inspect the largest growing app-owned types and their ownership/reference evidence in DevEco Profiler. Map the retaining edge back to source.
8. Patch the smallest retaining edge, cleanup omission, subscription, timer, task, listener, image cache, or native handle lifetime.
9. Repeat the identical flow and compare the specific type/path, not only total memory.

## Proof rules

- A smaller peak or heap is not by itself proof of a leak fix.
- Require a credible lifetime violation plus one of: an ownership/reference path, a reproducible per-cycle retained delta, or disappearance of the specific app-owned type/path after the fix.
- Separate retained caches and process-lifetime singletons from leaks; verify whether their lifetime is intentional and bounded.
- Treat lazy allocation as scope reduction, not a fix, unless eager allocation itself violated the intended lifetime.
- For ArkTS/native boundaries, verify both sides: callbacks/references on ArkTS and HandleScope, native allocations, file descriptors, threads, and cleanup on C/C++.
- Keep Debug/Release, device, data, iteration count, and wait interval comparable.

Read `references/capture-protocol.md` before collecting evidence and use `references/report-template.md` for the result. If only memory growth is available and no ownership or repeatability evidence exists, report “suspected growth,” not “proven leak.”
