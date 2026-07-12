# Push, Notification, AVSession

Checked 2026-07. Verify with `devecocli docs search <API>` or current docs.

## Push Kit

```ts
import { pushService } from '@kit.PushKit';
// EntryAbility.onCreate — refresh token every launch and upload to your server
const token = await pushService.getToken();
```

- AGC console must have Push Service enabled first — otherwise `getToken()` fails with **1000900010**.
- Token changes on reinstall/factory reset/`deleteToken()`; never cache it as permanent.
- Receiving: ability `skills` entry `{ "actions": ["action.ohos.push.listener"] }` in `module.json5`.
- Message classes: notification, voice broadcast, card refresh, background message, Live View, in-app call.

## Notification Kit

```ts
import { notificationManager } from '@kit.NotificationKit';
await notificationManager.addSlot(notificationManager.SlotType.SOCIAL_COMMUNICATION); // once at init
const enabled = await notificationManager.isNotificationEnabled();
if (!enabled) { await notificationManager.requestEnableNotification(); }
await notificationManager.publish({
  id: 1001,
  // omit slotType — old-module type mismatch trap, see arkts-error-fixes triage map
  content: {
    notificationContentType: notificationManager.ContentType.NOTIFICATION_CONTENT_BASIC_TEXT,
    normal: { title: '标题', text: '正文' }
  }
});
await notificationManager.cancel(1001);
```

## AVSession — mandatory for background audio

Without an active AVSession **plus** an `AUDIO_PLAYBACK` continuous task, the system force-pauses media-stream audio when the app backgrounds. Symptom: "音乐切到后台就停" — the fix is integration, not stream tweaking.

```ts
import { avSession as AVSessionManager } from '@kit.AVSessionKit';

const session = await AVSessionManager.createAVSession(context, 'MyPlayer', 'audio');
await session.setAVMetadata({ assetId: 'song_001', title: '...', artist: '...', duration: 240000 }); // required or controls don't show
await session.setAVPlaybackState({ state: AVSessionManager.PlaybackState.PLAYBACK_STATE_PLAY, position: { elapsedTime: 0, updateTime: Date.now() }, speed: 1.0 });
session.on('play', () => {}); session.on('pause', () => {}); session.on('seek', (ms) => {}); // register BEFORE activate
await session.activate();
session.off('playPrevious'); // unregister unsupported commands — system grays out the button
```

Continuous task request (`KEEP_BACKGROUND_RUNNING` permission + `backgroundModes: ["audioPlayback"]`): see `background-tasks.md`.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official Kit guides.
