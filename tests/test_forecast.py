"""Focused contract tests using small stand-ins for Home Assistant and aiohttp."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


COMPONENT = (
    Path(__file__).resolve().parents[1] / "custom_components/gfs_weather_forecast"
)
PACKAGE = "gfs_test_component"


def load_module(name):
    specification = importlib.util.spec_from_file_location(
        f"{PACKAGE}.{name}", COMPONENT / f"{name}.py"
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


class ForecastTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        package = types.ModuleType(PACKAGE)
        package.__path__ = [str(COMPONENT)]
        aiohttp = types.ModuleType("aiohttp")
        aiohttp.ClientSession = MagicMock
        aiohttp.ClientError = ConnectionError
        self.modules = patch.dict(sys.modules, {PACKAGE: package, "aiohttp": aiohttp})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        load_module("const")
        self.api_module = load_module("api")
        self.session = MagicMock()
        self.response = MagicMock()
        self.response.ok = True
        self.response.json = AsyncMock()
        self.session.get.return_value.__aenter__.return_value = self.response
        self.api = self.api_module.GFSForecastApi(self.session, 8123)
        self.payload = {
            "info": {"date": "2026-10-17"},
            "3": {"tmax": 12, "extra": [1, 2]},
        }

    async def test_full_forecast_preserves_json(self):
        self.response.json.return_value = self.payload
        self.assertEqual(await self.api.async_get_full_forecast(), self.payload)
        self.session.get.assert_called_once_with(url="http://localhost:8123/api/latest")
        self.session.get.return_value.__aexit__.assert_awaited_once()

    async def test_unavailable_or_invalid_full_forecast(self):
        for payload in ({}, [], {"info": "invalid"}):
            with self.subTest(payload=payload):
                self.response.json.return_value = payload
                with self.assertRaises((ValueError, TypeError)):
                    await self.api.async_get_full_forecast()
        self.response.ok = False
        with self.assertRaises(ValueError):
            await self.api.async_get_full_forecast()

    async def test_json_read_is_inside_timeout(self):
        self.response.json.side_effect = TimeoutError
        with self.assertRaises(ValueError):
            await self.api.async_get_full_forecast()
        self.session.get.return_value.__aexit__.assert_awaited_once()

    async def test_cancellation_propagates(self):
        import asyncio

        self.response.json.side_effect = asyncio.CancelledError
        with self.assertRaises(asyncio.CancelledError):
            await self.api.async_get_full_forecast()

    def load_coordinator(self):
        class DataUpdateCoordinator:
            def __init__(self, *args, **kwargs):
                self.data = None

        modules = {
            "homeassistant": types.ModuleType("homeassistant"),
            "homeassistant.helpers": types.ModuleType("homeassistant.helpers"),
            "homeassistant.helpers.update_coordinator": types.SimpleNamespace(
                DataUpdateCoordinator=DataUpdateCoordinator, UpdateFailed=RuntimeError
            ),
            "homeassistant.helpers.entity": types.SimpleNamespace(DeviceInfo=dict),
            "homeassistant.core": types.SimpleNamespace(
                HomeAssistant=MagicMock, callback=lambda function: function
            ),
        }
        sys.modules.update(modules)
        module = load_module("coordinator")
        self.client = MagicMock()
        self.client.async_get_status = AsyncMock(
            return_value={"status": "Finished", "current": {"run": 1}}
        )
        self.client.async_get_forecast = AsyncMock(return_value={"daily": {}})
        self.client.async_get_full_forecast = AsyncMock(return_value=self.payload)
        return module.GfsForecastDataUpdateCoordinator(MagicMock(), self.client, {})

    async def test_cache_refreshes_only_for_new_finished_run(self):
        coordinator = self.load_coordinator()
        data = await coordinator._async_update_data()
        self.assertEqual(data["full_forecast"], self.payload)
        self.assertEqual(data["forecast"], {"daily": {}})
        await coordinator._async_update_data()
        self.client.async_get_full_forecast.assert_awaited_once()
        self.client.async_get_status.return_value = {
            "status": "Loading",
            "current": {"run": 2},
        }
        await coordinator._async_update_data()
        self.client.async_get_full_forecast.assert_awaited_once()
        self.client.async_get_status.return_value = {
            "status": "Finished",
            "current": {"run": 2},
        }
        await coordinator._async_update_data()
        self.assertEqual(self.client.async_get_full_forecast.await_count, 2)

    async def test_startup_during_loading_refreshes_when_finished(self):
        coordinator = self.load_coordinator()
        self.client.async_get_status.return_value = {
            "status": "Loading",
            "current": {"run": 1},
        }
        await coordinator._async_update_data()
        self.client.async_get_status.return_value = {
            "status": "Finished",
            "current": {"run": 1},
        }
        await coordinator._async_update_data()
        self.assertEqual(self.client.async_get_full_forecast.await_count, 2)

    async def test_failed_refresh_retains_cache_and_retries(self):
        coordinator = self.load_coordinator()
        await coordinator._async_update_data()
        self.client.async_get_status.return_value = {
            "status": "Finished",
            "current": {"run": 2},
        }
        self.client.async_get_full_forecast.side_effect = ValueError("Not ready")
        with self.assertRaises(RuntimeError):
            await coordinator._async_update_data()
        self.assertEqual(coordinator._full_forecast, self.payload)
        self.assertEqual(coordinator._current, {"run": 1})
        updated = {**self.payload, "6": {"tmax": 14}}
        self.client.async_get_full_forecast.side_effect = None
        self.client.async_get_full_forecast.return_value = updated
        data = await coordinator._async_update_data()
        self.assertEqual(data["full_forecast"], updated)
        self.assertEqual(coordinator._current, {"run": 2})

    async def test_initial_failure_retries(self):
        coordinator = self.load_coordinator()
        self.client.async_get_full_forecast.side_effect = ValueError("Not ready")
        with self.assertRaises(RuntimeError):
            await coordinator._async_update_data()
        self.assertTrue(coordinator._first_run)
        self.client.async_get_full_forecast.side_effect = None
        self.assertEqual(
            (await coordinator._async_update_data())["full_forecast"], self.payload
        )

    async def test_websocket_cached_data_and_entry_selection(self):
        coordinator = self.load_coordinator()
        coordinator.data = await coordinator._async_update_data()
        websocket = types.SimpleNamespace(
            websocket_command=lambda schema: lambda function: function,
            ActiveConnection=MagicMock,
            async_register_command=MagicMock(),
        )
        sys.modules["homeassistant.components"] = types.SimpleNamespace(
            websocket_api=websocket
        )
        sys.modules["voluptuous"] = types.SimpleNamespace(
            Required=lambda value: value, Optional=lambda value: value
        )
        module = load_module("websocket_api")
        hass = types.SimpleNamespace(
            data={"gfs_weather_forecast": {"first": coordinator}}
        )
        connection = MagicMock()
        module.async_setup(hass)
        websocket.async_register_command.assert_called_once_with(
            hass, module.websocket_get_forecast
        )
        module.websocket_get_forecast(hass, connection, {"id": 1})
        connection.send_result.assert_called_once_with(1, self.payload)
        self.client.async_get_full_forecast.assert_awaited_once()
        hass.data["gfs_weather_forecast"]["second"] = types.SimpleNamespace(data=None)
        module.websocket_get_forecast(hass, connection, {"id": 2})
        self.assertEqual(connection.send_error.call_args.args[1], "entry_required")
        module.websocket_get_forecast(hass, connection, {"id": 3, "entry_id": "first"})
        self.assertEqual(connection.send_result.call_args.args, (3, self.payload))
        module.websocket_get_forecast(hass, connection, {"id": 4, "entry_id": "second"})
        self.assertEqual(connection.send_error.call_args.args[1], "not_ready")
        module.websocket_get_forecast(
            hass, connection, {"id": 5, "entry_id": "missing"}
        )
        self.assertEqual(connection.send_error.call_args.args[1], "not_loaded")
        hass.data["gfs_weather_forecast"].clear()
        module.websocket_get_forecast(hass, connection, {"id": 6})
        self.assertEqual(connection.send_error.call_args.args[1], "not_loaded")
