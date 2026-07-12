# Core Vision and Scan Kit

Checked 2026-07. Both are on-device; Core Vision is China-mainland only and does not run on the simulator — plan real-device verification. Verify with `devecocli docs search <API>` or current docs.

## Scan Kit

**Default UI (no camera permission)**:

```ts
import { scanCore, scanBarcode } from '@kit.ScanKit';
const result = await scanBarcode.startScanForResult(context,
  { scanTypes: [scanCore.ScanType.ALL], enableMultiMode: true, enableAlbum: true });
// result.originalValue (decoded string), result.scanType
```

**Decode from image**: `detectBarcode.decode({ uri }, { scanTypes, enableMultiMode })` — pair with PhotoViewPicker.

**Custom UI** (needs `ohos.permission.CAMERA`): `customScan.init(opts)` → `customScan.start({ width, height, surfaceId })` (XComponent surface) → flash/zoom/focus controls → `customScan.stop()`/`release()`.

**Generate**: `generateBarcode.createBarcode(content, { scanType: scanCore.ScanType.QR_CODE, width: 400, height: 400 })` → PixelMap usable directly in `Image()`.

Formats: QR, Data Matrix, PDF417, Aztec, EAN-8/13, UPC-A/E, Codabar, Code 39/93/128, ITF-14.

## Core Vision Kit

All engines follow `init()` → operate → `release()`; tie to lifecycle (`aboutToAppear`/`aboutToDisappear`).

```ts
// OCR — zh (simplified/traditional), en, ja, ko; JPEG/PNG, 720p+ recommended
import { textRecognition } from '@kit.CoreVisionKit';
await textRecognition.init();
const r = await textRecognition.recognizeText({ pixelMap }, { isDirectionDetectionSupported: false });
// r.value = full text
await textRecognition.release();

// Face detection
import { faceDetector } from '@kit.CoreVisionKit';
await faceDetector.init();
const faces = await faceDetector.detect({ pixelMap });  // rects, landmarks, euler angles, confidence
await faceDetector.release();

// Subject segmentation (背景抠图) — fully offline, no cloud cost
import { subjectSegmentation } from '@kit.CoreVisionKit';
await subjectSegmentation.init();
const seg = await subjectSegmentation.doSegmentation({ pixelMap },
  { maxCount: 5, enableSubjectDetails: true, enableSubjectForegroundImage: true });
// seg.fullSubject.foregroundImage — PixelMap with background removed
await subjectSegmentation.release();
```

API 26 preview adds image super-resolution and semantic text search — label as preview per the platform baseline.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT) and chen_jeff/harmony-os-skill segmentation practice notes.
