from typing import Any

# import requests
import asyncio
import logging
import aiohttp
from .const import DOMAIN, FORECAST_URL, FULL_FORECAST_URL, STATUS_URL

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)


class GFSForecastApi:
    _headers: dict[str, str] = {"User-Agent": "Home Assistant (GFS Weather Forecast)"}
    _raw_data: str = ""
    _daily_forecast: dict[str, Any] = {}

    def __init__(self, session: aiohttp.ClientSession, api_port: int) -> None:
        self._session = session
        self._api_port = api_port

    async def async_get_forecast(self) -> dict[str, Any]:
        """Get forecast from the API."""
        success, forecast = await self.__request_forecast()
        if success:
            return forecast
        else:
            return {}

    async def async_get_status(self) -> dict[str, Any]:
        """Get status the API."""
        success, status = await self.__request_status()
        if success:
            return status
        else:
            return {}

    async def async_get_full_forecast(self) -> dict[str, Any]:
        """Get the complete forecast JSON without transforming its fields."""
        success, forecast = await self.__perform_request(
            f"http://localhost:{self._api_port}/{FULL_FORECAST_URL}"
        )
        if not success or not isinstance(forecast, dict) or not forecast:
            raise ValueError("Full GFS forecast is unavailable")
        if not isinstance(forecast.get("info"), dict):
            raise TypeError("Full GFS forecast info must be an object")
        return forecast

    async def __request_forecast(self) -> tuple[bool, dict[str, Any]]:
        _LOGGER.debug(f"__request_daily_forecast")
        success, forecast = await self.__perform_request(
            f"http://localhost:{self._api_port}/{FORECAST_URL}"
        )
        return success, forecast

    async def __request_status(self) -> tuple[bool, dict[str, Any]]:
        _LOGGER.debug(f"__request_daily_forecast")
        success, status = await self.__perform_request(
            f"http://localhost:{self._api_port}/{STATUS_URL}"
        )
        return success, status

    async def __perform_request(self, url: str) -> tuple[bool, dict[str, Any]]:
        try:
            async with asyncio.timeout(TIMEOUT):
                async with self._session.get(url=url) as response:
                    if not response.ok:
                        _LOGGER.error(
                            "Error: %s - __perform_request %s", DOMAIN, response.status
                        )
                        return False, {}
                    result = await response.json()
                    if not isinstance(result, dict):
                        return False, {}
                    return True, result
        except (aiohttp.ClientError, TimeoutError, ValueError) as exception:
            _LOGGER.warning("Error requesting %s: %s", url, exception)
            return False, {}
