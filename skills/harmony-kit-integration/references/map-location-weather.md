# Location, Map, Weather

Checked 2026-07. Verify with `devecocli docs search <API>` or current docs.

## Location Kit

Permission: `ohos.permission.APPROXIMATELY_LOCATION` (user_grant; add `LOCATION` only when fine accuracy is justified).

```ts
import { geoLocationManager } from '@kit.LocationKit';
const pos = await geoLocationManager.getCurrentLocation({
  priority: geoLocationManager.LocationRequestPriority.FIRST_FIX,
  scenario: geoLocationManager.LocationRequestScenario.UNSET,
  timeoutMs: 10000
});
const addrs = await geoLocationManager.getAddressesFromLocation({ latitude: pos.latitude, longitude: pos.longitude, maxItems: 1 });
// GeoAddress: administrativeArea(省) → subAdministrativeArea(市) → locality(区) → subLocality → placeName
```

Continuous background location needs the `location` background mode + continuous task (`background-tasks.md`).

## Map Kit

AGC-configured app + `LOCATION`/`APPROXIMATELY_LOCATION` permissions for my-location layers.

```ts
import { mapCommon, map } from '@kit.MapKit';
MapComponent({
  mapOptions: { position: { target: { latitude: 39.9042, longitude: 116.4074 }, zoom: 12 } },
  mapCallback: (err, controller) => { if (!err) { this.mapController = controller; } }
}).width('100%').layoutWeight(1)
// controller.addMarker({ position, title, snippet })
```

## Weather Service Kit

```ts
import { weatherService } from '@kit.WeatherServiceKit';
const weather = await weatherService.getWeather({
  location: { latitude: 39.9042, longitude: 116.4074 },
  limitedDatasets: [weatherService.Dataset.CURRENT, weatherService.Dataset.DAILY,
                    weatherService.Dataset.HOURLY, weatherService.Dataset.ALERTS]
  // also INDICES (life indices), TIDES, MINUTE (precipitation)
});
// weather.currentWeather.temperature/.humidity/.conditionCode
// weather.dailyForecast?.days[], weather.hourlyForecast?.hours[], weather.weatherAlerts?.alerts[]
```

Location permission required when the request uses device location. Request only the datasets the UI shows.

Source: adapted from DengShiyingA/harmonyos-ai-skill (MIT), derived from official Kit guides.
