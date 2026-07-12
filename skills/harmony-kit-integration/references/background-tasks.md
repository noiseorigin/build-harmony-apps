# Background tasks

Checked 2026-07. Verify with `devecocli docs search background task` or current docs. Background execution is opt-in per type — anything else is frozen/muted when the app backgrounds.

| Type | API | Duration | Use |
|---|---|---|---|
| Transient | `requestSuspendDelay` | ~3 min | flush data, upload logs |
| Continuous | `startBackgroundRunning` | unlimited, shows notification | music, navigation, recording |
| Deferred | `workScheduler.startWork` | system-scheduled | sync, cleanup |
| Agent reminders | `ReminderRequestTimer/Alarm/Calendar` | system-managed | alarms, timers |

## Continuous task

Requires permission `ohos.permission.KEEP_BACKGROUND_RUNNING` **and** ability `"backgroundModes": ["audioPlayback"]` (or the matching mode) in `module.json5`.

```ts
import { backgroundTaskManager } from '@kit.BackgroundTasksKit';
import { wantAgent } from '@kit.AbilityKit';

const agent = await wantAgent.getWantAgent({
  wants: [{ bundleName: 'com.example.app', abilityName: 'EntryAbility' }],
  actionType: wantAgent.OperationType.START_ABILITY,
  requestCode: 0, actionFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG]
});
backgroundTaskManager.startBackgroundRunning(this.context,
  backgroundTaskManager.BackgroundMode.AUDIO_PLAYBACK, agent);
// stopBackgroundRunning when the task genuinely ends
```

Modes: `dataTransfer`, `audioPlayback`, `audioRecording`, `location`, `bluetoothInteraction`, `multiDeviceConnection`, `taskKeeping` (2-in-1 only). Background **audio** additionally requires AVSession — `push-notification.md`.

## Deferred task scheduling reality

Frequency depends on user engagement bucket: Active ≈ 2h, Frequent ≈ 4h, Regular ≈ 24h, Rare ≈ 48h, never-used apps get none. Do not promise periodic background sync tighter than the bucket allows.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official Background Tasks guides.
