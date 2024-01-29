import logging

import aiohttp

from .exceptions import InvalidOrganiztion
from .types import MenuDay, MenuFood, MenuSection, OrgSettings, School, SchoolMenu

_LOGGER = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


class NutrisliceAPI:
    def __init__(self, org_id: str) -> None:
        self.org_id = org_id

    async def get_settings(self) -> OrgSettings:
        """Get nutrislice settings for a specific org_id."""
        # build url
        url = f"https://{self.org_id}.api.nutrislice.com/menu/api/settings"
        # make request
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=DEFAULT_HEADERS) as resp:
                    # get json
                    resp_payload = await resp.json()
                    _LOGGER.debug(
                        "Got response data: %s",
                        resp_payload,
                    )
                    # map to org settings
                    org_settings = OrgSettings(
                        org_id=self.org_id,
                        district_name=resp_payload["district_name"],
                        address1=resp_payload["address_1"],
                        address2=resp_payload["address_2"],
                        city=resp_payload["city"],
                        state=resp_payload["state"],
                        zip=resp_payload["zip_code"],
                        contact_email=resp_payload["contact_email"],
                        director_name=resp_payload["director_name"],
                    )
                    return org_settings
            except aiohttp.ClientConnectorError as e:
                _LOGGER.error("Error connecting to %s: %s", url, e)
                raise InvalidOrganiztion(self.org_id) from e

    async def list_schools(self) -> list[School]:
        """List schools for a specific org_id."""
        # build url
        url = f"https://{self.org_id}.api.nutrislice.com/menu/api/schools"
        # make request
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=DEFAULT_HEADERS) as resp:
                    # get json
                    resp_payload = await resp.json()
                    _LOGGER.debug(
                        "Got response data: %s",
                        resp_payload,
                    )
                    # parse schools
                    schools: list[School] = []
                    for school_raw in resp_payload:
                        school = School(
                            id=school_raw["id"],
                            name=school_raw["name"],
                            slug=school_raw["slug"],
                            menus=[],
                        )
                        # parse menus
                        for menu_raw in school_raw["active_menu_types"]:
                            school["menus"].append(
                                SchoolMenu(
                                    id=menu_raw["id"],
                                    name=menu_raw["name"],
                                    slug=menu_raw["slug"],
                                )
                            )
                        schools.append(school)
                    return schools
            except aiohttp.ClientConnectorError as e:
                _LOGGER.error("Error connecting to %s: %s", url, e)
                raise InvalidOrganiztion(self.org_id) from e

    async def get_menu_week(
        self, school_slug: str, menu: str, year: int, month: int, day: int
    ) -> list[MenuDay]:
        """Get menu for a specific week based on the specified date."""
        # build url
        url = f"https://{self.org_id}.api.nutrislice.com/menu/api/weeks/school/{school_slug}/menu-type/{menu}/{year}/{month:02}/{day:02}/"
        # make request
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=DEFAULT_HEADERS) as resp:
                    # get json
                    resp_payload = await resp.json()
                    _LOGGER.info(
                        "Got response data: %s",
                        resp_payload,
                    )
                    # parse days
                    days: list[MenuDay] = []
                    for day_raw in resp_payload["days"]:
                        day = MenuDay(
                            date=day_raw["date"],
                            sections=[],
                        )
                        # loop over all menu items to find the sections and foods for every section
                        current_section = None
                        for menu_item in day_raw["menu_items"]:
                            # check if new section
                            if menu_item["is_section_title"]:
                                # if we already have a current section, then append it to list
                                if current_section:
                                    day["sections"].append(current_section)
                                # create new section
                                current_section = MenuSection(
                                    id=menu_item["id"],
                                    text=menu_item["text"],
                                    food=[],
                                )
                                continue
                            # parse food
                            current_section["food"].append(
                                MenuFood(
                                    id=menu_item["id"],
                                    name=menu_item["food"]["name"],
                                    description=menu_item["food"]["description"],
                                    category=menu_item["food"]["food_category"],
                                )
                            )
                        # append last section
                        if current_section is not None:
                            day["sections"].append(current_section)
                        days.append(day)
                    return days
            except aiohttp.ClientConnectorError as e:
                _LOGGER.error("Error connecting to %s: %s", url, e)
                raise InvalidOrganiztion(self.org_id) from e
