"""The Nutrislice Food Calendars integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_ORGANIZATION, DOMAIN
from .nutrislice.api import NutrisliceAPI

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nutrislice Food Calendars from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # create nutrislice api
    api = NutrisliceAPI(entry.data[CONF_ORGANIZATION])
    # store so platforms can access
    hass.data[DOMAIN][entry.entry_id] = {"api": api}

    # setup platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
