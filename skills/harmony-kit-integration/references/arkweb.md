# ArkWeb

Checked 2026-07. Verify with `devecocli docs search ArkWeb` or current docs. API 26 preview upgrades Chromium 132 → 144 — recheck web-behavior assumptions when targeting it.

## Web component

```ts
import { webview } from '@kit.ArkWeb';

controller: webview.WebviewController = new webview.WebviewController();

Web({ src: 'https://example.com', controller: this.controller })
  .javaScriptAccess(true).domStorageAccess(true)
  .onPageBegin((e) => {}).onPageEnd((e) => {})
  .onErrorReceive((e) => { /* e.error.getErrorInfo() */ })
  .darkMode(WebDarkMode.Auto).forceDarkAccess(true)
```

## JS ↔ ArkTS bridge

```ts
Web({ src, controller: this.controller })
  .javaScriptProxy({
    object: { callNative: (msg: string) => 'ArkTS received: ' + msg },
    name: 'NativeBridge', methodList: ['callNative'], controller: this.controller
  })
// page side: window.NativeBridge.callNative('hello')
// ArkTS → JS: this.controller.runJavaScript('window.updateUI("x")', (err, result) => {})
```

Treat every bridge input as untrusted; validate before touching app state or Kits.

## Cookies and User-Agent

```ts
webview.WebviewController.setCustomUserAgent(webview.WebviewController.getDefaultUserAgent() + ' MyApp/1.0');
import { webCookie } from '@kit.ArkWeb';
webCookie.setCookie('https://example.com', 'token=abc; path=/');
webCookie.saveCookieAsync();   // persistence is explicit
```

## Request interception

```ts
.onInterceptRequest((event) => {
  if (event?.request.getRequestUrl().includes('/api/')) {
    const resp = new WebResourceResponse();
    resp.setResponseData('{"intercepted":true}'); resp.setResponseMimeType('application/json');
    resp.setResponseEncoding('utf-8'); resp.setResponseCode(200); resp.setReasonMessage('OK');
    return resp;
  }
  return null;   // load normally
})
```

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official ArkWeb guides.
