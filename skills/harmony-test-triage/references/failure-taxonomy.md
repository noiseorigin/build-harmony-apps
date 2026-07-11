# Test failure taxonomy

| Class | Evidence | First action |
| --- | --- | --- |
| discovery/configuration | zero tests, wrong source set/module, task missing | inspect manifests, package config, task graph, runner registration |
| compile/type | ArkTS/native diagnostic before execution | use compiler error workflow; do not edit assertions |
| environment/device | no target, incompatible system/SysCap, permission/account state | make environment explicit or select supported target |
| fixture/state | wrong seed, stale app state, order dependency | isolate deterministic setup/cleanup and rerun alone |
| timing/async | timeout, race, element not ready, callback unfinished | wait on observable state; control clock/network/task lifecycle |
| assertion/product | deterministic actual/expected mismatch | decide whether product behavior or expectation is authoritative |
| framework/tooling | runner crash, Hvigor/SDK incompatibility | preserve versions/logs; reproduce with minimal fixture |
| flake | mixed results under nominally identical conditions | repeat, record sequence/duration, find uncontrolled input |

Always preserve the earliest actionable error and the exact command. A later wrapper `BUILD FAILED` line is not the root cause.
