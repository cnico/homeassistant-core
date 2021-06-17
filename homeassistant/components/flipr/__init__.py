"""The Flipr integration."""
from datetime import timedelta
import logging

from flipr_api import FliprAPIRestClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CONF_FLIPR_IDS, DOMAIN, MANUFACTURER, NAME

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=60)


PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flipr from a config entry."""
    _LOGGER.debug("async_setup_entry starting")

    hass.data.setdefault(DOMAIN, {})

    flipr_ids = entry.data[CONF_FLIPR_IDS].split(",")

    # Create all flipr_ids coordinators & devices present in the ConfigEntry
    for flipr_id in flipr_ids:
        coordinator = FliprDataUpdateCoordinator(hass, entry, flipr_id)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id][flipr_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class FliprDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to hold Flipr data retrieval."""

    def __init__(self, hass, entry, flipr_id):
        """Initialize."""
        username = entry.data[CONF_EMAIL]
        password = entry.data[CONF_PASSWORD]
        self.flipr_id = flipr_id

        _LOGGER.debug("Config entry values : %s, %s", username, self.flipr_id)

        # Establishes the connection.
        self.client = FliprAPIRestClient(username, password)
        self.hass = hass
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=f"Flipr data measure for {self.flipr_id}",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        return await self.hass.async_add_executor_job(
            self.client.get_pool_measure_latest, self.flipr_id
        )


class FliprEntity(CoordinatorEntity):
    """Implements a common class elements representing the Flipr component."""

    def __init__(self, coordinator, flipr_id, info_type):
        """Initialize Flipr sensor."""
        super().__init__(coordinator)
        self._unique_id = f"{flipr_id}-{info_type}"
        self.info_type = info_type
        self.flipr_id = flipr_id

    @property
    def unique_id(self):
        """Return a unique id."""
        return self._unique_id

    @property
    def device_info(self):
        """Define device information global to entities."""
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.flipr_id)
            },
            "name": NAME,
            "manufacturer": MANUFACTURER,
        }
