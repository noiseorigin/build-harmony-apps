# Kit catalog

Import keys and routing, checked 2026-07 against the official SDK catalog. Verify availability with `devecocli docs search <Kit>` or https://developer.huawei.com/consumer/cn/sdk/.

Common imports:

```ts
import { UIAbility, Want, common, abilityAccessCtrl } from '@kit.AbilityKit';
import { window, display } from '@kit.ArkUI';
import { http, webSocket, connection } from '@kit.NetworkKit';
import { photoAccessHelper } from '@kit.MediaLibraryKit';
import { fileIo as fs, picker } from '@kit.CoreFileKit';
import { relationalStore, preferences } from '@kit.ArkData';
import { hilog } from '@kit.PerformanceAnalysisKit';
```

## Routing table

| Capability | Kit (import key) | Cluster file | Notes |
|---|---|---|---|
| photo/video capture | `CameraKit` | `media.md` | CameraPicker needs **no permission** |
| audio play/record, focus | `AudioKit`, `MediaKit` | `media.md` | background audio → `push-notification.md` AVSession |
| image decode/transform/encode | `ImageKit` | `media.md` | |
| gallery picker | `MediaLibraryKit` | `data-persistence.md` | `picker.PhotoViewPicker` from old module is deprecated |
| QR/barcode | `ScanKit` | `vision-scan.md` | default UI needs no permission |
| OCR / face / background removal | `CoreVisionKit` | `vision-scan.md` | on-device; China mainland; no simulator |
| ASR/TTS | `CoreSpeechKit` | `media.md` | PCM 16kHz mono 16-bit input |
| Huawei ID login | `AccountKit` | `account-payment.md` | AGC client_id required |
| Huawei Pay (physical goods) | `PaymentKit` | `account-payment.md` | virtual goods = IAP Kit (`../../harmony-release-compliance/references/iap-integration.md`) |
| push messages | `PushKit` | `push-notification.md` | AGC Push service must be enabled |
| local notifications | `NotificationKit` | `push-notification.md` | |
| background media controls | `AVSessionKit` | `push-notification.md` | mandatory for background audio |
| location / geocoding | `LocationKit` | `map-location-weather.md` | user_grant permission |
| map display / markers | `MapKit` | `map-location-weather.md` | AGC + location permissions |
| weather data | `WeatherServiceKit` | `map-location-weather.md` | |
| SQLite / KV / files | `ArkData`, `CoreFileKit` | `data-persistence.md` | |
| HTTP / WebSocket / net state | `NetworkKit` | `network.md` | |
| background upload/download | `BasicServicesKit` (`request.agent`) | `network.md` | |
| home-screen cards | `FormKit` | `form-widgets.md` | sandboxed process, restricted ArkUI |
| atomic service constraints | — | `atomic-service.md` | |
| system share sheet | `ShareKit` | `share-linking.md` | |
| deep links | App Linking (`AbilityKit` skills) | `share-linking.md` | |
| open nav/browser/email by type | `startAbilityByType` | `share-linking.md` | |
| cross-device continuation | `AbilityKit` (`onContinue`) | `share-linking.md` | |
| transient/continuous/deferred bg work | `BackgroundTasksKit` | `background-tasks.md` | |
| embedded web | `ArkWeb` | `arkweb.md` | |
| secrets storage | `AssetStoreKit` | — | use for tokens/passwords, not preferences |
| clipboard/battery/vibration | `BasicServicesKit` | — | clipboard: `pasteboard.createData/getData` |
| bluetooth/Wi-Fi/NFC | `ConnectivityKit` | — | |
| crypto/keys/certs | `CryptoArchitectureKit` | — | |
| intents / system entries | `IntentsKit` | `../../harmony-app-intents/SKILL.md` | |
| calendar, contacts, ads, IAP, Live View, Pen, Wear Engine, Health, MDM, NearLink, i18n | respective keys | — | check official docs; several need AGC/enterprise qualification |

Region/device caveats worth restating in answers: Payment Kit and Core Vision Kit are China-mainland only; `taskKeeping` background mode is 2-in-1 only; several AI Kits have no simulator support.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), aligned with the official Kit catalog at adaptation time.
