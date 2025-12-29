"""DataUpdateCoordinator for apschool."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api.apschool import (
    ApschoolApiClient,
    ApschoolApiClientAuthenticationError,
    ApschoolApiClientError,
)
from .const import DOMAIN, LOGGER, DEFAULT_SCAN_INTERVAL


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class ApschoolDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: ApschoolApiClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        interval = timedelta(
            minutes=config_entry.options.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        super().__init__(
            hass=hass, logger=LOGGER, name=DOMAIN, update_interval=interval
        )

        self.client = client

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_user_data()
        except ApschoolApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except ApschoolApiClientError as exception:
            raise UpdateFailed(exception) from exception
