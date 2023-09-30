import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    DOMAIN as SENSOR_DOMAIN,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature # type: ignore
)
from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    MAJOR_VERSION,
    MINOR_VERSION
)
from .coordinator import GfsForecastDataUpdateCoordinator
from .const import DOMAIN, DEFAULT_NAME

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    
    async_add_entities(
        [
            GfsForecastWeather(
                coordinator=hass.data[DOMAIN][entry.entry_id],
                entry_id=entry.entry_id
            )
        ]
    )


class GfsForecastWeather(WeatherEntity):

    _attr_attribution = "GFS Weather Data via NOAA Nomads server"
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_visibility_unit = UnitOfLength.METERS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY # type: ignore

    def __init__(
        self,
        coordinator: GfsForecastDataUpdateCoordinator,
        entry_id: str
    ) -> None:
        self.coordinator = coordinator

        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME}".lower()
        self._attr_name = f"{DEFAULT_NAME}"
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME}"
        self._attr_device_info = coordinator.device_info
        self._attr_condition = None
    
    def _get_forecast(self) -> list[Forecast] | None:
        forecast_data = self.coordinator.data.get("forecast", {})
        if forecast_data == {}:
            return None

        forecast: list[Forecast] = []
        for key in forecast_data.keys():
            forecast_date = datetime.fromisoformat(key).date()
            if forecast_date > datetime.today().date():
                chance_of_sun = forecast_data[key].get('chance_of_sun')
                min_temperature_daytime = forecast_data[key].get('min_temperature_daytime', -999)
                temperature_min = round(forecast_data[key].get('temperature_min', -999))
                temperature_max = round(forecast_data[key].get('temperature_max', -999))
                rain = forecast_data[key].get('rain', 0)
                chance_of_rain = forecast_data[key].get('chance_of_rain', 0)
                windangle = forecast_data[key].get('windangle', 0)
                windspeed = forecast_data[key].get('windspeed', 0)
                if temperature_max > -999 and temperature_min > -999:
                    next_day: Forecast = {
                        ATTR_FORECAST_TIME: key,
                        ATTR_FORECAST_CONDITION:
                            self._get_condition(chance_of_sun, rain, min_temperature_daytime),
                        ATTR_FORECAST_NATIVE_TEMP_LOW: temperature_min,
                        ATTR_FORECAST_NATIVE_TEMP: temperature_max,
                        ATTR_FORECAST_NATIVE_PRECIPITATION: rain,
                        ATTR_FORECAST_PRECIPITATION_PROBABILITY: chance_of_rain,
                        ATTR_FORECAST_WIND_BEARING: windangle,
                        ATTR_FORECAST_NATIVE_WIND_SPEED: windspeed
                    }
                    forecast.append(next_day)

        return forecast
    
    def _get_condition(self, chance_of_sun: int, rain: float, temperature_min: float) -> str:
        if rain > 0.2:
            if temperature_min > 3:
                if rain > 2:
                    return ATTR_CONDITION_POURING
                else:
                    return ATTR_CONDITION_RAINY
            elif temperature_min >= 0:
                return ATTR_CONDITION_SNOWY_RAINY
            else:
                return ATTR_CONDITION_SNOWY
        else:
            if chance_of_sun <= 10:
                return ATTR_CONDITION_CLOUDY
            elif  chance_of_sun <= 80:
                return ATTR_CONDITION_PARTLYCLOUDY
        return ATTR_CONDITION_SUNNY

    @property
    def icon(self):
        return 'mdi:weather-partly-cloudy'
    
    @property
    def forecast(self) -> list[Forecast] | None:
        if MAJOR_VERSION * 100 + MINOR_VERSION > 202404:
            return None
        return self._get_forecast()
        
    async def async_forecast_daily(self) -> list[Forecast] | None:
        return self._get_forecast()
