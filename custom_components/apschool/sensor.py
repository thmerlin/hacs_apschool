"""Sensor platform for apschool."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.apschool.api.helpers import UserData

from .const import ATTRIBUTION, DOMAIN, LOGGER
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
        self._attr_unique_id = user_data.user_id
        self._user_data = user_data
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self.attrs: dict[str, Any] = None

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
        return self._determine_native_value()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""

        # Get the coordinator data for our sensor id
        for data in self.coordinator.data:
            if data.user_id == self._user_data.user_id:
                self.attrs = {
                    ATTR_ATTRIBUTION: ATTRIBUTION,
                    "firstname": data.firstname,
                    "lastname": data.lastname,
                    "school_class": data.school_class,
                    "balance": data.balance,
                    "unread_messages": (
                        len(data.unread_messages) if data.unread_messages is not None else 0
                    ),
                    "due_amount": data.due_amount,
                }
                return self.attrs

        LOGGER.error(
            "extra_state_attributes - Could not find data of our sensor %s from the coordinator", self._user_data.user_id)
        return None

    def _determine_native_value(self):
        """Determine native value."""
        # Get the coordinator data for our sensor id
        for user in self.coordinator.data:
            if user.user_id == self._user_data.user_id:
                return user.balance

        LOGGER.error(
            "determine_native_value - Could not find data of our sensor %s from the coordinator", self._user_data.user_id)

        return 0
