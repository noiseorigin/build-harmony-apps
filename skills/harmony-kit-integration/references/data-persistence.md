# Data persistence: relationalStore, preferences, fileIo, pickers, resources

Checked 2026-07. Verify with `devecocli docs search <API>` or current docs.

## Choosing

| Data | Use |
|---|---|
| structured/queryable | `relationalStore` (SQLite) |
| small KV settings | `preferences` |
| reactive persisted UI state | `PersistenceV2` (see arkui-ui-patterns state reference) |
| files/blobs | `fileIo` under Context dirs |
| secrets | Asset Store Kit — never preferences |

## relationalStore

```ts
import { relationalStore } from '@kit.ArkData';
const store = await relationalStore.getRdbStore(ctx, { name: 'my_db.db', securityLevel: relationalStore.SecurityLevel.S1 });
await store.executeSql('CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, title TEXT, timestamp INTEGER)');
await store.insert('records', { id: '1', title: 'Hello' } as relationalStore.ValuesBucket);
const p = new relationalStore.RdbPredicates('records'); p.orderByDesc('timestamp');
const rs = await store.query(p, ['id', 'title']);
while (rs.goToNextRow()) { const id = rs.getString(rs.getColumnIndex('id')); }
rs.close();  // always close result sets
// update/delete take a ValuesBucket / predicates with equalTo etc.
```

Predicates only — no string-concatenated SQL. Column names must be in the ArkGuard whitelist when property obfuscation is on. API 23+ enhances `sendable` result passing across threads.

## preferences

```ts
import { preferences } from '@kit.ArkData';
const store = await preferences.getPreferences(ctx, 'user_settings');
const v = (await store.get('sort_order', 'time_desc')) as string;
await store.put('sort_order', 'time_asc');
await store.flush();   // put() alone does not persist
```

Single-process by default — for cross-process consumers (service cards) see `form-widgets.md`.

## fileIo

```ts
import { fileIo as fs } from '@kit.CoreFileKit';
const f = fs.openSync(context.filesDir + '/data.json', fs.OpenMode.CREATE | fs.OpenMode.READ_WRITE);
fs.writeSync(f.fd, JSON.stringify(data)); fs.closeSync(f);
// read: openSync(READ_ONLY) + readSync(fd, buf); also accessSync/listFileSync/copyFileSync/unlinkSync/statSync
```

Context paths: `filesDir` (persistent), `cacheDir` (system may purge), `tempDir` (cleared on exit), `databaseDir`, `preferencesDir`, `bundleCodeDir` (read-only), `distributedFilesDir` (cross-device). Encryption levels EL1–EL4 apply per directory root.

## Pickers (user-mediated access, no storage permission)

```ts
// Photos — current API (old picker.PhotoViewPicker module path is deprecated)
import { photoAccessHelper } from '@kit.MediaLibraryKit';
const r = await new photoAccessHelper.PhotoViewPicker().select({ MIMEType: photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE, maxSelectNumber: 9 });
// r.photoUris — temporary read permission; open with fs.openSync(uri, READ_ONLY)

// Documents
import { picker } from '@kit.CoreFileKit';
const uris = await new picker.DocumentViewPicker(context).select({ fileSuffixFilters: ['.pdf'] });
const dest = (await new picker.DocumentViewPicker(context).save({ newFileNames: ['export.pdf'] }))[0];
```

## Resources

`$r('app.string.name')` / `$r('app.color.x')` / `$r('app.media.icon')`; format args `$r('app.string.greeting', 'Alice', 5)`; plurals `$r('app.plural.item_count', n, n)`; raw `$rawfile('path')`; system tokens `$r('sys.color.ohos_id_color_emphasize')`; cross-HSP `$r('[moduleName].string.x')`. Qualifier dirs: `base/`, locale (`zh_CN/`), `dark/`, density; `rawfile/` uncompiled, `resfile/` sandbox-installed. Programmatic: `context.resourceManager.getStringByNameSync/getRawFd`.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official ArkData/CoreFileKit guides.
