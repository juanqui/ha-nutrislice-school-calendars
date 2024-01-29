from __future__ import annotations

import datetime

from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import NutrisliceCalendarUpdateCoordinator
from .nutrislice.api import NutrisliceAPI


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Demo Calendar config entry."""

    # get api
    api: NutrisliceAPI = hass.data[DOMAIN][config_entry.entry_id]["api"]

    # get list of school calendars by firs getting list of all schools
    # in the organization and then selecting the available calendars for
    # the configured school
    schools = await api.list_schools()
    # select school
    school = next(s for s in schools if s["slug"] == config_entry.data["school_name"])
    # create calendars
    entities = []
    for school_menu in school["menus"]:
        # coordinator
        coordinator = NutrisliceCalendarUpdateCoordinator(
            hass,
            school_slug=school["slug"],
            menu_slug=school_menu["slug"],
            weeks=1,
            api=api,
        )
        # calendar entity
        device_id = f'{school["slug"]}_{school_menu["slug"]}'
        entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, device_id, hass=hass)
        calendar = NutrisliceCalendarEntity(
            name=school_menu["name"],
            entity_id=entity_id,
            school_slug=school["slug"],
            menu_slug=school_menu["slug"],
            coordinator=coordinator,
        )
        # append
        entities.append(calendar)
    # create entities
    async_add_entities(entities)


class NutrisliceCalendarEntity(
    CoordinatorEntity[NutrisliceCalendarUpdateCoordinator], CalendarEntity
):
    """Representation of the Nutrislice calendar/menu."""

    def __init__(
        self,
        name: str,
        entity_id: str,
        school_slug: str,
        menu_slug: str,
        coordinator,
    ) -> None:
        """Initialize Nutrislice calendar."""
        super().__init__(coordinator)
        self.entity_id = entity_id
        self._school_slug = school_slug
        self._menu_slug = menu_slug
        self._attr_name = name

    @property
    def event(self) -> CalendarEvent:
        """Return the next upcoming event."""
        # return None for now
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return await self.coordinator.async_get_events(hass, start_date, end_date)
