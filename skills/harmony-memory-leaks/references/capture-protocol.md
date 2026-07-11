# Memory capture protocol

## Stabilize

1. Use the same app revision, module/product/build mode, device/system, account/data set, and Profiler mode.
2. Define the stable baseline screen and expected lifetime of the target type.
3. Warm up unrelated one-time initialization when it is not under test.

## Exercise

1. Capture baseline at the stable state.
2. Perform a fixed flow for a fixed iteration count.
3. Return to the same stable state after each cycle.
4. Wait for known async cleanup using a state or completion signal, not an arbitrary long sleep.
5. Capture count/size snapshots and, where available, allocation/reference evidence.

## Normalize

The comparator accepts CSV or JSON rows and recognizes common header aliases, but the unambiguous canonical columns are:

`type,count,shallow_size,retained_size`

Sizes are raw bytes. Preserve original exports beside normalized files.

## Diagnose

- Prefer app-owned types with monotonic per-cycle growth.
- Inspect references, listeners, timers, tasks, workers, caches, resources, and native handles.
- Establish intended lifetime before calling retained data a leak.
- Repeat after the patch using identical cycles.
