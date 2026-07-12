# arkxtest patterns

Framework quick-reference for writing/reading Hypium tests during triage. Verify APIs against the installed `@ohos/hypium`.

## JsUnit (unit)

Tests live in `entry/src/ohosTest/ets/test/`. Mocha-style: `describe`/`it(name, flag, fn)` with `beforeAll`/`beforeEach`/`afterEach`/`afterAll`. Async tests take `done: Function` and must call it.

Assertions: `assertEqual`, `assertContain`, `assertTrue/False`, `assertNull`, `assertUndefined`, `assertNaN`, `assertInstanceOf`, `assertThrowError`, `assertDeepEquals`, `assertClose(v, tolerance)`, `assertLarger/Less`, `not()`, `assertPromiseIsResolved/Rejected`.

## UiTest (UI automation)

```ts
import { Driver, ON } from '@ohos.UiTest';
const DELEGATOR = AbilityDelegatorRegistry.getAbilityDelegator();

beforeAll(async (done: Function) => {
  await DELEGATOR.startAbility({ bundleName: 'com.example.app', abilityName: 'EntryAbility' });
  await new Promise(r => setTimeout(r, 2000));   // let first page render
  done();
});

it('flow', 0, async (done: Function) => {
  const driver = Driver.create();                 // fresh per it-block
  const btn = await driver.findComponent(ON.text('发布'));
  await btn.click();
  await new Promise(r => setTimeout(r, 800));
  const btnAfter = await driver.findComponent(ON.text('发布'));  // refs go stale after state changes
  await driver.pressBack();
  done();
});
```

Rules that explain most flaky failures:

- Every UiTest call must be awaited; a missing `await` produces order-dependent flakiness.
- Component references become stale after any state-changing action — re-`findComponent`.
- UiTest runs only on a real device or emulator; the Previewer does not support it.
- Create `Driver` fresh per `it`; add a render wait after navigation before asserting.
- Selector styles: `ON.text()`, `ON.type()`, `ON.id()`; `getBounds()` for position-based work.

## Hypium integration traps (device-verified)

1. The ohosTest HAP may need `-p product=release`-style packaging matching the app's signing — a debug test HAP against a manually-signed app fails install.
2. `expect` failures **mark**, they don't throw: code after a failed assertion keeps running, and `try/catch` cannot gate on assertion outcomes. Sequence assertions accordingly.
3. Get context in tests via `abilityDelegator.getCurrentTopAbility()` — not component `getContext`.
4. Give test databases their own `dbName` — sharing the app's store corrupts user data and makes runs order-dependent.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT) and chen_jeff/harmony-os-skill (gitee); rules verified against arkxtest/hypium docs at adaptation time.
