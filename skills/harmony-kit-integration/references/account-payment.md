# Account Kit (Huawei ID) and Payment Kit

Checked 2026-07. Both require AGC console configuration; verify with `devecocli docs search <API>` or current docs.

## Prerequisites

`module.json5` module `metadata`: `{ "name": "client_id", "value": "<AGC client id>" }`. Signature fingerprint must match AGC (error **1001500001** otherwise).

## Login variants

| Variant | Who | Returns |
|---|---|---|
| One-click login (`QUICK_LOGIN`) | enterprise developers, non-game | anonymous phone display + auth code → server fetches full phone + UnionID |
| Standard login (`LoginType.ID`) | all developers | auth code → server exchanges for UnionID/OpenID |
| Silent login (`forceLogin: false`) | all | auth code for returning users, no UI |

```ts
import { authentication } from '@kit.AccountKit';
import { util } from '@kit.ArkTS';

// One-click step 1: anonymous phone for the login page
const authReq = new authentication.HuaweiIDProvider().createAuthorizationWithHuaweiIDRequest();
authReq.scopes = ['quickLoginAnonymousPhone'];
authReq.state = util.generateRandomUUID();
authReq.forceAuthorization = false;   // must be false for one-click
const resp = await new authentication.AuthenticationController().executeRequest(authReq);
const anonPhone = resp.data?.extraInfo?.quickLoginAnonymousPhone as string;

// Step 2: LoginWithHuaweiIDButton({ params: { loginType: loginComponentManager.LoginType.QUICK_LOGIN, ... }, controller })
// callback → authorizationCode → server /oauth2/v6/quickLogin/getPhoneNumber

// Silent login
const loginReq = new authentication.HuaweiIDProvider().createLoginWithHuaweiIDRequest();
loginReq.forceLogin = false; loginReq.state = util.generateRandomUUID();
// error 1001502001 → not logged in, show alternate methods
```

ArkGuard: whitelist `quickLoginAnonymousPhone` under `-keep-property-name` when property obfuscation is enabled.

## Error codes

| Code | Meaning | Action |
|---|---|---|
| 1001502001 | not logged in | show other login methods |
| 1001502005 | network | retry / fallback |
| 1001502012 | user cancelled | none |
| 1001500001 | fingerprint mismatch | fix signing vs AGC |
| 1001502014 | missing scopes | AGC permission approval |
| 1005300001 | protocol not agreed | show agreement |

Identity scoping: **OpenID** per-app, **UnionID** per-developer (prefer for cross-app continuity), GroupUnionID per account group.

## Payment Kit (physical goods/services; China mainland)

Virtual goods must use IAP Kit instead (`../../harmony-release-compliance/references/iap-integration.md`) — mixing them up is a review rejection.

```ts
import { paymentService } from '@kit.PaymentKit';
// orderStr built SERVER-side: pre-order via /api/v2/aggr/preorder/create/app → prepay_id → signed JSON
await paymentService.requestPayment(context, orderStr);
```

Never sign orders client-side; the signature key stays on the server.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official Account/Payment guides.
