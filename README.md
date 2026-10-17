![Version](https://img.shields.io/github/v/release/MarcoGos/gfs_weather_forecast?include_prereleases)

# GFS Weather Forecast

This is a custom integration of the GFS Weather Forecast. It will provide a weather entity based on the information gathered with the GFS Weather Forecast addon.

## Installation

First make sure you installed the GFS Weather Forecast addon, see https://github.com/MarcoGos/ha-addons. After the addon is running you can install this integration.

Via HACS:

- Add the following custom repository as an integration:
    - MarcoGos/gfs_weather_forecast
- Restart Home Assistant
- Add the integration to Home Assistant

## Setup

During the setup of the integration the api port of the addon needs to be provided, the default port is 8000.

![Setup](/assets/setup.png)

## What to expect

The following sensors will be registered:

![Sensors](/assets/sensors.png)

The sensor information is updated every 4 hours.

## Full forecast for dashboard cards

The integration also retrieves the add-on's complete `/api/latest` JSON, including
`info` and all forecast-hour fields. It caches this in Home Assistant at startup
and when the status reports a newly finished forecast run. Status is checked every
15 seconds; card requests read the cache without contacting the add-on.

Authenticated dashboard cards can retrieve the original JSON over Home Assistant's
WebSocket connection:

```javascript
const forecast = await this.hass.callWS({
    type: "gfs_weather_forecast/get_forecast",
});
```

With multiple configured integration entries, include `entry_id` to select one:

```javascript
const forecast = await this.hass.callWS({
    type: "gfs_weather_forecast/get_forecast",
    entry_id: "YOUR_CONFIG_ENTRY_ID",
});
```

The result has the same structure as the add-on's JSON file. No public file URL,
browser access to the add-on, CORS configuration, or large entity attributes are
needed. The existing GFS Weather Card's URL loader must be updated to use this
call; a WebSocket command cannot be entered in its JSON URL field.

If an update fails, the last successful JSON remains available and the integration
retries on the next status poll. Command errors use `not_loaded` for missing or
unloaded entries, `entry_required` for ambiguous selection, and `not_ready` when
no forecast has been cached yet. Unloading an entry removes access to its cache.
