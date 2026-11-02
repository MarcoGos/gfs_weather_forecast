"""Constants for the GFS Forecast integration."""

NAME = "GFS Weather Forecast"
DOMAIN = "gfs_weather_forecast"
MANUFACTURER = "NOAA"
MODEL = "GFS Weather Forecast"
VERSION = "1.1.5"

# Platforms
WEATHER = "weather"

DEFAULT_SYNC_INTERVAL = 15  # seconds

CONF_API_PORT: int = 8765

DEFAULT_NAME = DOMAIN
FORECAST_URL = "api/forecast"
FULL_FORECAST_URL = "api/latest"
STATUS_URL = "api/status"
