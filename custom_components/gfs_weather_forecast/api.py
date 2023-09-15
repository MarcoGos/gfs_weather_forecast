from typing import Any

# import requests
import logging
import aiohttp
import async_timeout
from .const import DOMAIN, FORECAST_URL, STATUS_URL

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)


class GFSForecastApi:
    _headers: dict[str, str] = {
        "User-Agent": "Home Assistant (GFS Weather Forecast)"
    }
    _raw_data: str = ""
    _daily_forecast: dict[str, Any] = {}

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_port: int
    ) -> None:
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

    async def __request_forecast(self) -> tuple[bool, dict[str, Any]]:
        _LOGGER.debug(f"__request_daily_forecast")
        success, forecast = await self.__perform_request(f"http://localhost:{self._api_port}/{FORECAST_URL}")
        return success, forecast

    async def __request_status(self) -> tuple[bool, dict[str, Any]]:
        _LOGGER.debug(f"__request_daily_forecast")
        success, status = await self.__perform_request(f"http://localhost:{self._api_port}/{STATUS_URL}")
        return success, status

    async def __perform_request(self, url: str) -> tuple[bool, dict[str, Any]]:
        with async_timeout.timeout(TIMEOUT):
            response = await self._session.get(
                url=url, #headers=self._headers
            )
        res: dict[str, Any] = {}
        if response.ok:
            res = await response.json()  # .content.decode("utf-8")
            _LOGGER.debug(f"{DOMAIN} - __perform_request succeeded")
        else:
            _LOGGER.error(f"Error: {DOMAIN} - __perform_request {response.status}")

        return response.ok, res
