# Media: Camera, Audio, AVPlayer/AVRecorder, Image, Speech

Checked 2026-07. Verify signatures with `devecocli docs search <API>` or current docs.

## Camera

**CameraPicker — no permission needed** (system camera UI):

```ts
import { camera, cameraPicker as picker } from '@kit.CameraKit';
import { fileIo, fileUri } from '@kit.CoreFileKit';

const filePath = context.filesDir + `/${Date.now()}.tmp`;
fileIo.createRandomAccessFileSync(filePath, fileIo.OpenMode.CREATE);
const result = await picker.pick(context,
  [picker.PickerMediaType.PHOTO, picker.PickerMediaType.VIDEO],
  { cameraPosition: camera.CameraPosition.CAMERA_POSITION_BACK, saveUri: fileUri.getUriFromPath(filePath) });
if (result.resultCode === 0) { /* result.resultUri, result.mediaType */ }
```

**Full session** (needs `ohos.permission.CAMERA`; `MICROPHONE` for video audio). Pipeline: `getCameraManager` → `createCameraInput(device).open()` → `getSupportedOutputCapability(device, SceneMode.NORMAL_PHOTO)` → `createPreviewOutput(profile, surfaceId)` + `createPhotoOutput(profile)` → `createSession` → `beginConfig/addInput/addOutput/commitConfig/start` → `photoOutput.capture()`; receive via `photoOutput.on('photoAvailable')` and release the image object. The preview `surfaceId` comes from `XComponent({ type: XComponentType.SURFACE, controller }).onLoad(() => controller.getXComponentSurfaceId())`. Cleanup order: session.stop → input.close → outputs.release → session.release. API 24 adds professional controls and "Follow the Person" subject tracking.

## Audio focus and streams

`StreamUsage` determines volume class and focus: `MUSIC`/`MOVIE`/`AUDIOBOOK`/`GAME` (media), `VOICE_COMMUNICATION` (call), `RINGTONE`/`NOTIFICATION`, `ALARM` (speaker even with BT), `NAVIGATION` (ducks music). Focus is system-managed; handle interruptions:

```ts
renderer.on('audioInterrupt', (e: audio.InterruptEvent) => {
  // forceType INTERRUPT_FORCE: PAUSE / STOP / DUCK / UNDUCK already applied — update UI
  // hintType INTERRUPT_HINT_RESUME: app may restart playback itself
});
```

Custom concurrency: `audioManager.getSessionManager().activateAudioSession({ concurrencyMode: CONCURRENCY_PAUSE_OTHERS | MIX_WITH_OTHERS | DUCK_OTHERS })`; deactivate when done.

**Background playback**: media streams need AVSession **and** an `AUDIO_PLAYBACK` continuous task, or the system silences the app on background — see `push-notification.md`.

## AVPlayer / AVRecorder (`@kit.MediaKit`)

AVPlayer is state-machine driven — react to `stateChange`: `initialized` → `prepare()`; `prepared` → `play()`; `completed` → `release()`. Sources: `avPlayer.url` (network) or `avPlayer.fdSrc = { fd, offset, length }` (local). Video: set `avPlayer.surfaceId` (XComponent) in `initialized` before `prepare()`. Controls: `pause/play/seek(ms)/setSpeed/setVolume/stop/release`. Always register `on('error')` and release there.

AVRecorder: `createAVRecorder` → `prepare(config)` (audio/video source types, codec profile, `url: 'fd://N'`) → for video `getInputSurface()` → `start/stop/release`.

## Image Kit

Decode: `image.createImageSource(path | fd | ArrayBuffer | rawFd)` → `createPixelMap({ editable, desiredPixelFormat })`. Transform (mutates PixelMap): `crop(region)`, `scale(x, y)`, `rotate(deg)`, `flip(h, v)`, `opacity(a)`. Encode: `image.createImagePacker().packing(pixelMap, { format: 'image/jpeg', quality })` → ArrayBuffer → `fs.writeSync`. Release PixelMap/ImageSource/packer explicitly. Decode at display size for thumbnails (memory).

## Core Speech (ASR)

`speechRecognizer.createEngine({ language: 'zh-CN', online: 0 })` — audio **must** be PCM 16kHz mono 16-bit; write 640/1280-byte chunks every 20/40ms.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official Kit guides.
