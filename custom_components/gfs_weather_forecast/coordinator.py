from datetime import datetime, timedelta
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

    def __init__(self, hass: HomeAssistant, client: GFSForecastApi, device_info: DeviceInfo) -> None:
        """Initialize."""
        self.api = client
        self.platforms: list[str] = []
        self.last_updated = None
        self.device_info = device_info

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SYNC_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            status = await self.api.async_get_status()
            forecast = await self.api.async_get_forecast()
            return {
                "status": status,
                "forecast": forecast
            }
        except Exception as exception:
            _LOGGER.error(f"Error GfsForecastDataUpdateCoordinator _async_update_data: {exception}")
            raise UpdateFailed() from exception
