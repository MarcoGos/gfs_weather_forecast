from datetime import timedelta
from typing import Any
import logging

from homeassistant.helpers.update_coordinator import UpdateFailed, DataUpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.core import HomeAssistant

from .api import GFSForecastApi
from .const import (
    DEFAULT_SYNC_INTERVAL,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

class GfsForecastDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""
    _status: dict[str, Any] = {}
    _forecast: dict[str, Any] = {}
    _current: dict[str, Any] = {}
    data: dict[str, Any]

    def __init__(self, hass: HomeAssistant, client: GFSForecastApi, device_info: DeviceInfo) -> None:
        """Initialize."""
        self.api: GFSForecastApi = client
        self.platforms: list[str] = []
        self.last_updated = None
        self.device_info = device_info

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SYNC_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            self._status = await self.api.async_get_status()
            if self._status.get('status', '') == 'Finished' and self._status.get('current', {}) != self._current:
                self._forecast = await self.api.async_get_forecast()
            self._current = self._status.get('current', {})

            status = { k: v for k, v in self._status.items() if not isinstance(v, dict) }
            status |= { "current_" + k: v for k, v in self._status.get('current', {}).items() }
            status |= { "loading_" + k: v for k, v in self._status.get('loading', {}).items() }
            return {
                "status": status,
                "forecast": self._forecast
            }
        except Exception as exception:
            _LOGGER.error(f"Error GfsForecastDataUpdateCoordinator _async_update_data: {exception}")
            raise UpdateFailed() from exception
