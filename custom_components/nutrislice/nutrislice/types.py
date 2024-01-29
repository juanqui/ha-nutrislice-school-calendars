from typing import TypedDict


class OrgSettings(TypedDict):
    org_id: str
    district_name: str
    address1: str
    address2: str
    city: str
    state: str
    zip: str
    contact_email: str
    director_name: str


class SchoolMenu(TypedDict):
    id: int
    name: str
    slug: str


class School(TypedDict):
    id: int
    name: str
    slug: str
    menus: list[SchoolMenu]


class MenuFood(TypedDict):
    id: str
    name: str
    description: str
    category: str


class MenuSection(TypedDict):
    id: str
    text: str
    food: list[MenuFood]


class MenuDay(TypedDict):
    date: str
    sections: list[MenuSection]
