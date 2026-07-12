# State-tracking pitfalls ("UI not updating" symptoms)

Production-verified failure patterns. Match the symptom first; each pitfall has a distinct signature. Common tell for all of them: **cold start looks correct, staleness appears at runtime; killing the app "fixes" it** — because initialization bypasses change tracking.

## 1. Object-array element mutation not rendering → @Observed + @ObjectLink chain

Symptom: `figures[2].imagePath = newPath` commits, hilog shows `build()` ran, but the row keeps the old value.

V1 decorators observe first-level only. The official pattern requires **all** of:

1. `@Observed` on the data class (generates setter proxies).
2. A dedicated `@Component` row that receives the single object via `@ObjectLink` (`@ObjectLink` is illegal in `@Builder` params — this forces the row to be a component).
3. Intermediate layers pass the array by reference (`@ObjectLink`/`@Link`) — **never `@Prop`**, whose deep copy strips the proxy and breaks the chain.
4. Mutations target the proxied instance, not a copy.

Any missing link breaks the whole chain silently. V2 alternative: `@ObservedV2` + `@Trace` observes nested writes directly.

## 2. @Builder parameter indirection severs tracking

Symptom: state field updates, `build()` re-runs, the new value demonstrably reaches the `@Builder` — but the node using it never repaints; another node reading the same source directly shows the new value (two values on screen).

Root cause: ArkUI's dependency tracker binds a node only to `this.xxx` accessed **directly in the builder's expressions**. A parameter (`imgName`) is a local — `backgroundImage('memory://' + imgName)` binds to nothing.

Fixes: (A) split into parameterless `@Builder`s that read `this.img0`/`this.img1` directly; (B) convert the builder to a `@Component` and pass state through decorated inputs (`@Prop`/`@ObjectLink`); (C) reference `this.xxx` inside the expression. Applies identically to pages (`@State`) and service cards (`@LocalStorageProp`).

## 3. ForEach keys

- key unchanged → instance reused, local refresh; key changed → destroy + recreate (animation replay, local state loss).
- Build keys from the **item's own** identity fields only. Never concatenate parent/global state (theme, editMode) into keys — one global change re-keys every row and the whole list flickers/rebuilds.
- Pure index keys freeze rows against data-recomputation: after the source array is rebuilt (e.g. crossing a daily boundary), directly-bound text updates but ForEach rows keep first-render values. Pair fix: stable domain keys + an explicit reload trigger, because `onPageShow` does **not** fire on unlock or when the app stays foreground across the boundary.
- Verification: mutate 1 of N items — only that row shows a visual transition; the other N-1 must not flicker.

## 4. Toggle isOn is one-way

`Toggle({ isOn: this.flag })` flips visually but never writes back — there is no `$$` sugar for Toggle. Without explicit assignment in `onChange`, AppStorage/persisted state keeps the old value, and background→foreground or restart resurrects the stale setting ("switch had no effect"). Always: `Toggle({ isOn: this.flag }).onChange(v => { this.flag = v; /* persist */ })`; for external writers, drive `isOn` from the stored field to keep both directions in sync.

Source: adapted from chen_jeff/harmony-os-skill (gitee), verified on real devices in shipped apps.
