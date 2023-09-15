![Version](https://img.shields.io/github/v/release/MarcoGos/gfs_weather_forecast?include_prereleases)

# GFS Forecast

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
