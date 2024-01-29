"""Data update coordinator for Nutrislice."""
from __future__ import annotations

from datetime import date, datetime, timedelta
import logging

from homeassistant.components.calendar import CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .nutrislice.api import NutrisliceAPI

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=12)


class NutrisliceCalendarUpdateCoordinator(DataUpdateCoordinator[CalendarEvent | None]):
    """Class to utilize the calendar dav client object to get next event."""

    def __init__(
        self,
        hass: HomeAssistant,
        school_slug: str,
        menu_slug: str,
        weeks: int,
        api: NutrisliceAPI,
    ) -> None:
        """Set up how we are going to search the WebDav calendar."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Nutrislice {school_slug} - {menu_slug}",
            update_interval=MIN_TIME_BETWEEN_UPDATES,
        )
        self.school_slug = school_slug
        self.menu_slug = menu_slug
        self.weeks = weeks
        self.api = api
        self.events_cache = {}

    async def async_get_events_for_week(
        self, start_of_week: date
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""
        # check if week is already retrieved and cached
        if start_of_week in self.events_cache:
            return self.events_cache[start_of_week]
        # get menu for a specific week based on the specified date
        menu_days = await self.api.get_menu_week(
            self.school_slug,
            self.menu_slug,
            start_of_week.year,
            start_of_week.month,
            start_of_week.day,
        )
        # loop over every menu day and create an event for every section containing the food items for that section
        events = []
        for menu_day in menu_days:
            # parse date
            event_date = date.fromisoformat(menu_day["date"])
            # process all menu sections
            for menu_section in menu_day["sections"]:
                event = self._event_from_section(event_date, menu_section)
                events.append(event)
        # cache
        self.events_cache[start_of_week] = events
        # return
        return events

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""
        all_events = []
        # nutrislice school calendars are retrieved by week, so we need to break down the requested time
        # range into weeks and then get the events for each week
        num_days = (end_date - start_date).days
        for num_day in range(num_days):
            day = start_date + timedelta(days=num_day)
            # get start of the week
            start_of_week_date = day - timedelta(days=day.weekday())
            # get events for specific week week
            events = await self.async_get_events_for_week(start_of_week_date)
            # get events for specific day
            events = [event for event in events if event.start == day.date()]
            all_events.extend(events)
        return all_events

    async def _async_update_data(self) -> CalendarEvent | None:
        """Get the latest data."""
        all_events = []
        # get current week
        today = dt_util.start_of_local_day()
        start_of_week_date = today - timedelta(days=today.weekday())
        # load num_weeks weeks of events
        for week_num in range(self.weeks):
            week_start_date = start_of_week_date + timedelta(days=week_num * 7)
            events = await self.async_get_events_for_week(week_start_date)
            all_events.extend(events)
        return all_events

    def _event_from_section(self, event_date, section):
        event = CalendarEvent(
            start=event_date,
            end=event_date,
            summary=section["text"]
            + " - "
            + ", ".join([f["name"] for f in section["food"]]),
            description=", ".join([f["name"] for f in section["food"]]),
        )
        return event
