# Network: HTTP, WebSocket, connectivity, background transfer

Checked 2026-07. Verify with `devecocli docs search <API>` or current docs. All need `ohos.permission.INTERNET` (system_grant). HTTPS only in production; pinning via network_config — see `../../deveco-create-project/references/build-sign-release.md`.

## HTTP (`@kit.NetworkKit`)

```ts
import { http } from '@kit.NetworkKit';
const req = http.createHttp();
try {
  const res = await req.request(url, {
    method: http.RequestMethod.GET,
    header: { 'Content-Type': 'application/json' },
    connectTimeout: 5000, readTimeout: 10000
  });
  return res.result as string;
} finally { req.destroy(); }   // always destroy
```

`@ohos/axios` (ohpm) is the common third-party alternative for interceptors/instances.

## WebSocket

```ts
import { webSocket } from '@kit.NetworkKit';
const ws = webSocket.createWebSocket();
ws.on('open', () => ws.send('hello'));
ws.on('message', (err, data: string | ArrayBuffer) => {});
ws.on('close', (err, { code, reason }) => {}); ws.on('error', (e) => {});
ws.connect('wss://example.com/ws', { header: { Authorization: 'Bearer …' } });
```

## Connectivity monitoring

```ts
import { connection } from '@kit.NetworkKit';
const hasNet = connection.hasDefaultNetSync();
const con = connection.createNetConnection();
con.on('netAvailable', () => {}); con.on('netLost', () => {});
con.on('netCapabilitiesChange', (info) => {
  const wifi = info.netCap.bearerTypes.includes(connection.NetBearType.BEARER_WIFI);
});
con.register(() => {});   // subscriptions inactive until register
// cleanup: con.unregister(() => {})
```

## Background upload/download (`request.agent`, survives backgrounding)

```ts
import { request } from '@kit.BasicServicesKit';
const task = await request.agent.create(context, {
  action: request.agent.Action.DOWNLOAD,       // or UPLOAD with data: FormItem[]
  url: 'https://example.com/file.zip',
  mode: request.agent.Mode.BACKGROUND,
  saveas: './downloads/file.zip', overwrite: true, gauge: true
});
task.on('progress', (p) => {}); task.on('completed', (p) => {});
await task.start();   // upload also supports pause()/resume() with breakpoint
```

Prefer `request.agent` over hand-rolled chunked HTTP for large transfers — it handles resume and background limits.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official NetworkKit guides.
