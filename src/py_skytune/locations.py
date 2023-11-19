"""Location classes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Locations:
    """The Loactions class."""

    regions: list[Region]

    def find_by_uid(self: Locations, uid: tuple[int, int, int]) -> Country | StateProvince:
        """Find a country by its uid."""
        for region in self.regions:
            for country in region.countries:
                if country.uid == uid:
                    return country
                for state_province in country.states_provinces:
                    if state_province.uid == uid:
                        return state_province
        msg = f"Could not find location with uid {uid}"
        raise ValueError(msg)

    def find_by_name(self: Locations, name: str) -> Country | StateProvince:
        """Find a country by its name."""
        for region in self.regions:
            for country in region.countries:
                if country.name == name:
                    return country
                for state_province in country.states_provinces:
                    if state_province.name == name:
                        return state_province
        msg = f"Could not find location with name {name}"
        raise ValueError(msg)


@dataclass
class Region:
    """The ParentLocation class."""

    name: str
    countries: list[Country]

    def __str__(self: Region) -> str:
        """Return the string representation."""
        return self.name


@dataclass
class Country:
    """The SubLocation class."""

    uid: (tuple[int, int, int])
    name: str
    states_provinces: list[StateProvince]
    region: Region

    def __str__(self: Country) -> str:
        """Return the string representation."""
        return f"{self.region}/{self.name}"


@dataclass
class StateProvince:
    """The StateProvince class."""

    uid: (tuple[int, int, int])
    name: str
    country: Country
    region: Region

    def __str__(self: StateProvince) -> str:
        """Return the string representation."""
        return f"{self.country}/{self.name}"
