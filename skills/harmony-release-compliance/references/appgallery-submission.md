# AppGallery submission

Checked 2026-07 against real review cycles. AGC flows change — treat as a gate map, verify current console requirements.

## Material checklist

- Artifact type and signing identity required by the current AGC channel; the normal multi-module AppGallery flow uses a signed `.app` (see `signing-release-build.md`). Check `versionCode` against versions already accepted by that channel.
- App intro (≤80 chars) + description (≤2000) — no absolute claims (「最」「第一」「绝对」).
- Real screenshots (no mocks) matching actual functionality.
- Privacy policy at a reachable public URL — AGC-hosted URL is the most reliable and needs **no ICP filing** (`filing-icp.md`).
- APP 备案 and category qualifications when the app's service scope and current review path require them (`filing-icp.md`); finance/medical/education and other regulated categories need extra verification.
- IAP products ride along with an app version review — they cannot be submitted standalone (`iap-integration.md`).

## Common rejections → avoidance

| Rejection | Avoidance |
|---|---|
| privacy URL unreachable | test from public network before submitting |
| IAP without visible "恢复购买" | prominent restore entry (review rule 3.1.1) |
| crash / main flow broken | self-test main + edge flows: offline, weak network, permission denied |
| screenshots ≠ actual app | re-shoot on the release build |
| open capability not effective | approved capabilities must also be **checked** in the Release Profile |
| versionCode not incremented | bump on every submission |
| exaggerated copy / sensitive words | plain factual descriptions |

## Atomic-service extras

- Card snapshot per supported dimension, strict path/name — missing → **error 13**.
- Package limits: single ≤ 2MB, total ≤ 10MB (build fails, but reviewers also check).
- Card refresh config static scan: `updateDuration` and `scheduledUpdateTime` cannot both be absent while the card claims periodic updates.
- Privacy declaration for purely local/no-network services: declare "不收集" consistently across AGC form and in-app statement — mismatch is a rejection.
- Duration/statistics features are tested under system-clock changes — see the monotonic-clock constraint in `../../harmony-kit-integration/references/atomic-service.md`.

## Facts that counter common folklore

- 软著 (software copyright) is not a universal listing gate, but it can still be requested by category, ownership-proof, dispute, or current review rules. Check the current qualification table instead of repeating either blanket claim.
- Review cycles are typically business-days-scale; plan resubmission buffers rather than exact dates.

Source: adapted from chen_jeff/harmony-os-skill (gitee), from shipped-app review experience.
