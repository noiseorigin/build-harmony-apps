# IAP Kit (in-app purchases)

Checked 2026-07. For virtual goods/subscriptions only — physical goods use Payment Kit. Verify current API names with `devecocli docs search IAP` or docs.

## Three setup traps (before any code)

1. **Two agreements in sequence**: AGC merchant approval alone does not activate IAP — the follow-up service agreement must also be signed; the console blocks with a "联系我们" dialog until both are done.
2. **Three names, one path**: business docs, SDK docs, and console use different names for the same integration (IAP Kit is the client API in all cases). Don't split the integration because docs appear to describe different products.
3. **Profile regeneration**: enabling IAP adds an entitlement — the signing Profile must be regenerated with the IAP capability checked and manual signing used (`signing-release-build.md`), or client calls fail on device.

## Client flow

```ts
import { iap } from '@kit.IAPKit';

const products = await iap.queryProducts({
  products: ['product_id_unlock'],
  productType: iap.ProductType.NON_CONSUMABLE   // CONSUMABLE / AUTO_RENEWABLE_SUBSCRIPTION
});

const res = await iap.createPurchase(context, {
  productId: 'product_id_unlock',
  productType: iap.ProductType.NON_CONSUMABLE,
  developerPayload: JSON.stringify({ userId })
});
// res.purchaseToken is a JWS — the SDK provides no decoder; split the three
// base64url segments yourself to read payload (environment === 'SANDBOX' marks sandbox)
await verifyOnServer(res.purchaseToken);        // server-side verification is mandatory
await iap.finishPurchase(context, { purchaseToken: res.purchaseToken, productType: iap.ProductType.NON_CONSUMABLE });
```

## Restore purchases

HarmonyOS has no dedicated restore API — implement by querying owned purchases and re-unlocking. Review **requires** a prominent "恢复购买" UI entry (rule 3.1.1); its absence is a standard rejection.

## Error handling

| Code | Meaning | Handling |
|---|---|---|
| `PRODUCT_OWNED` | already owned | run restore/unlock path |
| `SYSTEM_ERROR` | transient | run restore path (may already be purchased) |
| `USER_CANCEL` | user backed out | silent |
| `NETWORK_ERROR` | connectivity | prompt retry |

## Review coupling

- Products are reviewed **with** an app version — first product submission must ride an app submission.
- Sandbox testing needs an AGC sandbox tester account; sandbox purchases carry `environment: 'SANDBOX'` in the JWS payload.
- Never trust the client JWS alone for entitlement — server verification prevents forged tokens.

Source: adapted from chen_jeff/harmony-os-skill (gitee), production IAP integration experience.
