from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorEntity,
    SensorEntityDescription
)
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
        name="Status",
        icon="mdi:check-circle-outline"
    ),
    SensorEntityDescription(
        key="loading_date",
        name="Loading Date",
        icon="mdi:calendar",
        entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="loading_pass",
        name="Loading Pass",
        icon="mdi:clock-start",
        entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="loading_offset",
        name="Loading Offset",
        icon="mdi:av-timer",
        entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="max_offset",
        name="Maximum Offset",
        icon="mdi:av-timer",
        entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="loading_progress",
        name="Progress",
        icon="mdi:download-circle-outline",
        native_unit_of_measurement=PERCENTAGE,
        entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="current_date",
        name="Current Date",
        icon="mdi:calendar"
    ),
    SensorEntityDescription(
        key="current_pass",
        name="Current Pass",
        icon="mdi:clock-start"
    ),
    SensorEntityDescription(
        key="used_latitude_longitude",
        name="Used Position",
        icon="mdi:crosshairs-gps",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False
    )
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


class GFSForecastSensor(CoordinatorEntity[GfsForecastDataUpdateCoordinator], SensorEntity):
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

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{DEFAULT_NAME}_{description.name}".lower()
        )
        self.entity_description = description
        self._attr_name = description.name # type: ignore
        self._attr_unique_id = f"{entry_id}-{DEFAULT_NAME} {self.name}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status_data = self.coordinator.data.get("status", {})
        if self.entity_description.native_unit_of_measurement == PERCENTAGE:
            default_value = 0
        else:
            default_value = '-'
        return status_data.get(self.entity_description.key, default_value)
