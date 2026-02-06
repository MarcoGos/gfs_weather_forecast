from datetime import datetime
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import GfsForecastDataUpdateCoordinator

DESCRIPTIONS: list[SensorEntityDescription] = [
    SensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:check-circle-outline",
        options=["loading", "waiting", "finished"],
        device_class=SensorDeviceClass.ENUM,
    ),
    SensorEntityDescription(
        key="loading_date",
        translation_key="loading_date",
        device_class=SensorDeviceClass.DATE,
        icon="mdi:calendar",
    ),
    SensorEntityDescription(
        key="loading_pass",
        translation_key="loading_pass",
        icon="mdi:clock-start",
    ),
    SensorEntityDescription(
        key="loading_offset",
        translation_key="loading_offset",
        icon="mdi:av-timer",
    ),
    SensorEntityDescription(
        key="max_offset",
        translation_key="max_offset",
        icon="mdi:av-timer",
    ),
    SensorEntityDescription(
        key="loading_progress",
        translation_key="loading_progress",
        icon="mdi:download-circle-outline",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="current_date",
        translation_key="current_date",
        icon="mdi:calendar",
        device_class=SensorDeviceClass.DATE,
    ),
    SensorEntityDescription(
        key="current_pass",
        translation_key="current_pass",
        icon="mdi:clock-start",
    ),
    SensorEntityDescription(
        key="used_latitude_longitude",
        translation_key="used_latitude_longitude",
        icon="mdi:crosshairs-gps",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GFS Forecast sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[GFSForecastSensor] = []

    # Add all meter sensors described above.
    for description in DESCRIPTIONS:
        entities.append(
            GFSForecastSensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                description=description,
            )
        )

    async_add_entities(entities)


class GFSForecastSensor(
    CoordinatorEntity[GfsForecastDataUpdateCoordinator], SensorEntity
):
    """Defines a GFS Forecast sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GfsForecastDataUpdateCoordinator,
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize GFS Forecast sensor."""
        super().__init__(coordinator=coordinator)

        self.entity_description = description
        self.entity_id = f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{description.key}".lower()
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status_data = self.coordinator.data.get("status", {})

        if self.entity_description.device_class == SensorDeviceClass.DATE:
            str_value = status_data.get(self.entity_description.key, "")
            if not str_value:
                return None
            value = datetime.strptime(str_value, "%Y-%m-%d").date()
            return value

        if self.entity_description.key == "status":
            return status_data.get("status", "").lower()

        return status_data.get(self.entity_description.key, None)
