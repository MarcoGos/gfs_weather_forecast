"""Constants for the GFS Forecast integration."""

NAME = "GFS Weather Forecast"
DOMAIN = "gfs_weather_forecast"
MANUFACTURER = "NOAA"
MODEL = "GFS Weather Forecast"
VERSION = "1.0.2"

# Platforms
WEATHER = "weather"

DEFAULT_SYNC_INTERVAL = 15  # seconds

CONF_API_PORT = 8000

DEFAULT_NAME = NAME
FORECAST_URL = "api/forecast"
STATUS_URL = "api/status"