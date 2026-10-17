"""Expose the cached full forecast to authenticated dashboard clients."""

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


@callback
def async_setup(hass: HomeAssistant) -> None:
    """Register the forecast command once for the integration."""
    websocket_api.async_register_command(hass, websocket_get_forecast)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/get_forecast",
        vol.Optional("entry_id"): str,
    }
)
@callback
def websocket_get_forecast(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Return the original JSON from the selected integration's cache."""
    coordinators = hass.data.get(DOMAIN, {})
    entry_id = msg.get("entry_id")
    if entry_id is None:
        if not coordinators:
            connection.send_error(
                msg["id"], "not_loaded", "GFS Weather Forecast is not loaded"
            )
            return
        if len(coordinators) != 1:
            connection.send_error(
                msg["id"], "entry_required", "Specify a GFS config entry_id"
            )
            return
        coordinator = next(iter(coordinators.values()))
    else:
        coordinator = coordinators.get(entry_id)
        if coordinator is None:
            connection.send_error(
                msg["id"], "not_loaded", "GFS config entry is not loaded"
            )
            return

    forecast = (coordinator.data or {}).get("full_forecast")
    if not forecast:
        connection.send_error(
            msg["id"], "not_ready", "GFS forecast is not available yet"
        )
        return
    connection.send_result(msg["id"], forecast)
