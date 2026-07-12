# Build hardening: security, obfuscation, network config

Build-time hardening quick-reference, checked 2026-07. Release signing SOP and store submission live in `../../harmony-release-compliance/SKILL.md`.

## Security coding rules (official best practices)

1. `exported: false` for non-interactive abilities.
2. Validate every parameter crossing a trust boundary (Want, rpc.RemoteObject).
3. Parameterized queries only — never string-concatenated SQL.
4. HTTPS with certificate validation; no plain HTTP in production.
5. No personal data in the clipboard; no personal data via implicit intents.
6. Asset Store Kit for secrets (passwords, tokens) — not preferences.
7. Precise `InputType` (`.USER_NAME`, `.Password`) for system-level input protection.
8. Obfuscate production builds; never ship debug signatures.

Data encryption levels: EL1 device / EL2 user (default) / EL3 accessible-while-locked / EL4 inaccessible-when-locked.

## Network security config (certificate pinning)

`src/main/resources/base/profile/network_config.json`:

```json
{
  "network-security-config": {
    "domain-config": [{
      "domains": [{ "include-subdomains": true, "name": "api.example.com" }],
      "trust-anchors": [{ "certificates": "/data/storage/el1/bundle/entry/resources/resfile/ca_cert.pem" }]
    }]
  }
}
```

Registered in `module.json5` metadata: `{ "name": "NetworkSecurityConfig", "resource": "$profile:network_config" }`.

## ArkGuard obfuscation

Enable via `build-profile.json5` → `arkOptions.obfuscation`; rules file options:

```
-enable-property-obfuscation
-enable-toplevel-obfuscation
-enable-export-obfuscation
-enable-filename-obfuscation
-compact                            # strips newlines — release stacks lose line info
-remove-log
-print-namecache ./nameCache.json   # REQUIRED per release for crash-stack decoding
```

Must-whitelist (`-keep-property-name`): dynamically accessed properties (`obj['x'+i]`, `defineProperty`), JSON-serialized field names, network payload field names, relationalStore column names, NAPI/.so export names. Auto-preserved: ArkUI decorator properties and SDK API names — but string keys matching SDK constants (e.g. `'ohos.want.action.home'`) are NOT auto-kept.

Must-whitelist (`-keep-file-name`): Worker files and dynamic-import paths (ability entries auto-collected since DevEco 5.0.3.500; route-table paths auto since API 20). Since API 19, `// @KeepSymbol` comments keep individual names.

Gotchas: property whitelisting is **global** (keeping `name` keeps every `name`); save `nameCache.json` with every release; hstack + namecache decode obfuscated crash stacks.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official security/obfuscation best practices.
