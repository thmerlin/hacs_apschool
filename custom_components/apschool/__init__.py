"""Custom integration to integrate apschool with Home Assistant.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api.apschool import ApschoolApiClient
from .const import DOMAIN, LOGGER
from .coordinator import ApschoolDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up apschool from a config entry."""
    LOGGER.debug("Integration async setup entry: %s", entry.as_dict())
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = coordinator = ApschoolDataUpdateCoordinator(
        hass=hass,
        client=ApschoolApiClient(
            base_url=entry.data["base_url"],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        ),
        config_entry=entry,
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    # https://developers.home-assistant.io/blog/2024/06/12/async_forward_entry_setups
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # for platform in PLATFORMS:
    #     hass.async_create_task(
    #         hass.config_entries.async_forward_entry_setup(entry, platform)
    #     )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    This is called when you remove your integration or shutdown HA.
    If you have created any custom services, they need to be removed here too.
    """

    # Unload services
    for service in hass.services.async_services_for_domain(DOMAIN):
        hass.services.async_remove(DOMAIN, service)

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove the config entry from the hass data object.
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    # Return that unloading was successful.
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    # await async_unload_entry(hass, entry)
    # await async_setup_entry(hass, entry)
    await hass.config_entries.async_reload(entry.entry_id)
