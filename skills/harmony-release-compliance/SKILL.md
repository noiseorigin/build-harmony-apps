---
name: harmony-release-compliance
description: Sign, package, submit, and triage review failures for HarmonyOS apps and atomic services — signing certificates and Profiles, real-device package verification, assembleApp and AppGallery artifacts, AGC submission checks, IAP Kit review requirements, APP 备案 vs ICP 备案 scope, and rejection diagnosis. Use when signature verification fails (including code 9568322), a package or version is rejected, a Profile lacks an entitlement, an app is preparing 上架/提审, virtual goods need 内购/买断/订阅, or an AGC review result needs a current evidence-backed root cause.
---

# Harmony Release Compliance

Take an app from working build to store-approved release with evidence at each gate. Read only the reference matching the current gate.

## Workflow

1. **Signing setup** (`references/signing-release-build.md`): generate .p12/CSR, AGC certificate + Profile. Match the certificate/Profile type, registered devices, capability entitlements, distribution channel, and installed device policy. Treat 9568322 as a signature/Profile/device-trust mismatch to verify, not proof of one universal cause.
2. **Local capability verification**: when auto-signing lacks an approved AGC capability, build the intended product/build mode with a manually configured, device-authorized Profile and install it with hdc. Do not confuse release build mode with a Release distribution Profile.
3. **Store packaging**: inspect the project's Hvigor task tree and the current AGC channel requirements. For the normal multi-module AppGallery flow, run project-level `assembleApp` and submit the resulting signed `.app`; use a different artifact only when the target console explicitly requests it.
4. **Submission** (`references/appgallery-submission.md`): material checklist, privacy policy hosting, screenshots, versionCode increment, capability checkboxes.
5. **Qualifications** (`references/filing-icp.md`): determine whether the app provides internet information services in mainland China, where its web content is hosted, and whether its category or review path requests additional qualifications. Never present APP 备案, ICP 备案, or 软著 as an unconditional universal rule.
6. **IAP** (`references/iap-integration.md`) when the app sells virtual goods; physical goods use Payment Kit (`../harmony-kit-integration/references/account-payment.md`).
7. **Rejection triage**: map the rejection text to the checklist rows in the submission reference; for atomic-service-specific gates (snapshot error 13, package size, card refresh compliance) pair with `../harmony-kit-integration/references/atomic-service.md`.

## Rules

- Never invent signing material or commit machine paths/credentials; `.p12`/`.cer`/`.p7b` stay out of version control unless the project already has a policy.
- Before uploading a replacement package, compare `versionCode` with the versions already accepted by the target AGC channel and increment when required; never lower or reuse a code that the console rejects.
- AGC open capabilities require three states: applied, approved, **and checked in the Profile** — an approved-but-unchecked capability silently fails on device.
- Review verdicts are evidence: when a rejection cites behavior, reproduce it on a manually-signed release build before disputing or patching.
- Store/review policies change frequently — treat the references as a map of gates, and verify current requirements in AGC/official docs (`devecocli docs search` covers developer docs, not AGC console flows).
