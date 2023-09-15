![Version](https://img.shields.io/github/v/release/MarcoGos/gfsforecast?include_prereleases)

# GFS Forecast

This is a custom integration of the GFS Forecast. It will provide a weather entity based on the information gathered with the GFS Forecast addon.

## Installation

Via HACS:

- Add the following custom repository as an integration:
    - MarcoGos/gfsforecast
- Restart Home Assistant
- Add the integration to Home Assistant

## Setup

During the setup of the integration a region, name, latitude and longitude needs to be provided.

![Setup](/assets/setup.png)

## What to expect

The following sensors will be registered:


The sensor information is updated every 4 hours.

![Sensors](/assets/sensors.png)
