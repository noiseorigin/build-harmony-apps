# Signing and release builds

Device-verified SOP, checked 2026-07. Console flows change — verify current AGC UI labels when steps don't match.

## Why not the IDE Run button

DevEco's default Run normally uses auto signing. Some approved AGC capabilities depend on matching certificate/Profile entitlements and can be absent from an automatically generated test package. When capability evidence differs from the configured Profile, verify with a manually configured, device-authorized package. Keep build mode (`debug`/`release`) separate from distribution Profile type.

## Profile types (the核心 distinction)

| | Debug Profile | Release Profile |
|---|---|---|
| UDID binding | required, per device | none |
| local device install | Expected when the device UDID and signing chain match | Verify against the device/system and distribution channel; do not assume universal installability |
| store upload | Not the normal production submission identity | Normal production distribution identity |
| open capabilities | must be checked here for local testing | must be checked here for release |

## One-time setup (8 steps)

1. DevEco `Build → Generate Key and CSR` → new keystore, validity ≥ 25 years → `signature/app.p12` + `.csr`.
2. AGC 证书 tab → create the certificate type required by the intended test/distribution destination → upload CSR → download `.cer`.
3. AGC 设备 tab: register device UDID (`hdc shell bm get --udid`).
4. For local-device capability testing, create a device-authorized Profile when required → bind app + certificate + registered device UDIDs + **check every approved capability needed by the test** → download `.p7b`.
5. DevEco `Project Structure → Signing Configs → release`: uncheck auto-sign; set p12/passwords/alias, Profile `.p7b`, Certpath `.cer`.
6. `build-profile.json5`: add a release product wired to that signingConfig (keep a separate `appstore` product for the Release Profile).
7. Build: `hvigorw -p product=release assembleHap` → output under `entry/build/release/outputs/release/` (not `outputs/default`).
8. Install: `hdc install -r <hap>`; logs via `hdc shell hilog | grep <bundleName>`.

Incremental loop is fast (~15s change→device); don't avoid it by falling back to auto-sign.

## Store packaging (.app)

```
hvigorw -p product=appstore -p buildMode=release assembleApp --no-daemon
```

- `assembleApp` is **project-level**: no `--mode module` / `-p module=entry@x`.
- Output: project-root `build/outputs/appstore/<App>-appstore-signed.app`.
- Keep separate signing configurations for device-authorized testing and store distribution when both destinations are used; name them by destination to avoid confusing build mode with Profile type.

## Failure table

| Symptom | Root cause | Fix |
|---|---|---|
| 9568322 on install | signature/Profile/device trust mismatch; common causes include a missing device binding or mismatched signing material | inspect the package certificate/Profile and device policy, then regenerate the matching test Profile |
| `failed to install bundle: signature verification failed` | device UDID not in Debug Profile | add UDID in AGC, regenerate `.p7b` |
| upload rejects the package type | artifact does not match the current AGC channel requirement | inspect the console requirement; use project-level `assembleApp` for the normal `.app` submission flow |
| "Profile 不带 entitlement" | capability approved but not checked in Profile | edit Profile, re-check, re-download |
| capability works locally, dead in review build | capability only in Debug Profile | check it in the Release Profile too |
| BUILD SUCCESSFUL but no hap | wrong output dir | `outputs/release`, not `outputs/default` |
| card still white despite transparent config | one of the 5 requirements missing | `../../harmony-kit-integration/references/form-widgets.md` |

Source: operational patterns adapted from chen_jeff/harmony-os-skill (gitee). Error causes and console rules must be verified against the installed DevEco SDK, target device, package signing data, and current AGC flow.
