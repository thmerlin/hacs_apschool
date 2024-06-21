"""ApschoolEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME
from .coordinator import ApschoolDataUpdateCoordinator


class ApschoolEntity(CoordinatorEntity):
    """ApschoolEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: ApschoolDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self.unique_id)},
            name=NAME,
            # model=VERSION,
            manufacturer=NAME,
        )
