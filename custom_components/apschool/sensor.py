"""Sensor platform for apschool."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.apschool.api.helpers import UserData

from .const import ATTRIBUTION, DOMAIN
from .coordinator import ApschoolDataUpdateCoordinator
from .entity import ApschoolEntity


@dataclass
class ApschoolSensorDescription(SensorEntityDescription):
    """A class that describes sensor entities."""

    # parent_key = name of the UserData field for this sensor. Used to retrieve the native value
    parent_key: str = None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: ApschoolDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        [
            ApschoolSensor(
                user_data=user_data,
                coordinator=coordinator,
            )
            for user_data in coordinator.data
        ]
    )


class ApschoolSensor(ApschoolEntity, SensorEntity):
    """apschool Sensor class."""

    def __init__(
        self,
        user_data: UserData,
        coordinator: ApschoolDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)

        self.has_entity_name = True
        self._attr_unique_id = user_data.id
        self._user_data = user_data
        self._attr_native_unit_of_measurement = CURRENCY_EURO

    @property
    def icon(self) -> str:
        """Shows the correct icon for container."""
        return "mdi:account-school"

    @property
    def name(self) -> str:
        # return self.unique_id
        return f"{self._user_data.firstname} {self._user_data.lastname}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._user_data.balance

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "firstname": self._user_data.firstname,
            "lastname": self._user_data.lastname,
            "school_class": self._user_data.school_class,
            "balance": self._user_data.balance,
            "unread_messages": (
                len(self._user_data.unread_messages)
                if self._user_data.unread_messages is not None
                else 0
            ),
        }

    # @property
    # def suggested_unit_of_measurement(self) -> str:
    #     """Return the unit of measurement this sensor expresses itself in."""
    #     return "€"
