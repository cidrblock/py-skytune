"""The py_skytune package."""

from __future__ import annotations

import json
import logging
import re

from dataclasses import dataclass

import requests


logger = logging.getLogger(__name__)

RE_FAV = re.compile(
    r"""
            .*{
            curPage:(?P<current_page>\d+),\s
            total:(?P<total>\d+),\s
            favCapacity:(?P<capacity>\d+),\s
            itemsPerPage:(?P<items_per_page>\d+),\s
            chIndex:(?P<ch_index>-?\d+),\s
            rowIdx:(?P<row_index>-?\d+),\s
            curPageCount:(?P<current_page_count>-?\d+)
            };
        """,
    re.VERBOSE,
)

RE_CHANNEL = re.compile(
    r"""
    .*\(\[
    "(?P<name>.*)",
    "(?P<url>.*)",
    (?P<skytune_maintained>\d),
    \[
    \[(?P<location>-?\d+,-?\d+,-?\d+)\],
    \[(?P<genre>-?\d+,-?\d+)\]
    \]
    \]\);
""",
    re.VERBOSE,
)


@dataclass
class FavDetails:
    """The FavDetails class."""

    current_page: int
    total: int
    capacity: int
    items_per_page: int
    ch_index: int
    row_index: int
    current_page_count: int

    @property
    def capacity_dict(self: FavDetails) -> dict[str, int]:
        """Get the capacity."""
        return {"capacity": self.capacity, "used": self.total, "free": self.capacity - self.total}


@dataclass
class Favorite:
    """The Favorite class."""

    name: str
    url: str
    skytune_maintained: bool
    location: str
    genre: str
    uid: int = None


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


class Radio:
    """The Radio class."""

    def __init__(self: Radio, ip_address: str) -> None:
        """Initialize the Radio class.

        Args:
            ip_address: The IP address of the radio.
        """
        self.ip_address = ip_address
        self.session = requests.Session()
        self.base_url = f"http://{self.ip_address}/"
        self._favorites: list[Favorite] = None
        self._countries: dict[tuple[int, int, int], str] = None
        self._genres: dict[tuple[int, int], str] = None
        self._locations: Locations = Locations(regions=[])

    def get(self: Radio, url: str, params: dict) -> requests.Response:
        """Get the URL."""
        res = self.session.get(f"{self.base_url}{url}", params=params)
        return res

    def post(self: Radio, url: str, data: dict) -> requests.Response:
        """Post the URL."""
        return self.session.post(f"{self.base_url}{url}", data=data)

    def _parse_favorite_page(self: Radio, page: str) -> tuple[list[Favorite], FavDetails]:
        """Parse the favorite page."""
        lines = page.split("\n")
        # remove initial favListInfo
        lines = lines[1:-1]
        fav_list_line = next(line for line in lines if line.startswith("favListInfo = "))
        match = RE_FAV.match(fav_list_line)
        fav_details = FavDetails(**{k: int(v) for k, v in match.groupdict().items()})
        favorites = []
        for line in lines:
            if line.startswith("myFavChannelList.push"):
                match = RE_CHANNEL.match(line)
                favorite = match.groupdict()
                location = tuple(int(x) for x in favorite["location"].split(","))
                if location == (-1, -1, -1):
                    favorite["location"] = "Unknown"
                else:
                    favorite["location"] = self.locations.find_by_uid(location)
                genre = tuple(int(x) for x in favorite["genre"].split(","))
                if genre == (-1, -1):
                    favorite["genre"] = "Unknown"
                else:
                    favorite["genre"] = self.genres[genre]
                favorite["skytune_maintained"] = bool(int(favorite["skytune_maintained"]))

                favorites.append(Favorite(**favorite))
        return favorites, fav_details

    def _get_favorites(self: Radio) -> None:
        """Get the favorites."""
        params = {"PG": 0, "EX": 0}
        logger.debug("Getting favorites: page %s", "0")
        res = self.get(url="php/favList.php", params=params)
        logger.debug("page: %s", res.text)
        favorites, fav_details = self._parse_favorite_page(res.text)
        self._favorites = favorites
        if len(self._favorites) >= fav_details.total:
            return
        total_pages = int(fav_details.total // fav_details.items_per_page)
        for page in range(1, total_pages + 1):
            logger.debug("Getting favorites: page %s", page)
            params = {"PG": page, "EX": 0}
            res = self.get(url="php/favList.php", params=params)
            favorites, _ = self._parse_favorite_page(res.text)
            self._favorites.extend(favorites)
        for idx, favorite in enumerate(self._favorites):
            favorite.uid = idx + 1
        return

    @property
    def favorites(self: Radio) -> list[Favorite]:
        """Get the favorites."""
        if self._favorites is not None:
            return self._favorites
        self._get_favorites()
        return self._favorites

    @property
    def favorites_capacity(self: Radio) -> dict[str, int]:
        """Get the favorites capacity."""
        data = {"PG": 0, "EX": 0}
        logger.debug("Getting favorites: page %s", "0")
        res = self.get("php/favList.php", data)
        _stations, fav_details = self._parse_favorite_page(res.text)
        return fav_details.capacity_dict

    def _load_countries_genres(self: Radio) -> None:
        """Get the countries."""
        res = self.get(url="php/get_CG.php", params={})
        text = res.text
        text = text.replace("];", "]").replace("'", '"')
        parts = text.split("mGenreList = ")
        locations_part = parts[0]
        locations_part = locations_part.replace("mCountryList = ", "")
        locations_loaded = json.loads(locations_part)
        current_country = None
        for location in locations_loaded:
            if location[1:4] == [-1, -1, -1]:
                pass
            elif location[2:4] == [-1, -1]:
                logger.debug("Found region: %s", location[4])
                self._locations.regions.append(Region(name=location[4], countries=[]))
            elif location[3] == -1:
                logger.debug("Found country: %s", location[4])
                current_country = Country(
                    name=location[4],
                    region=self._locations.regions[-1],
                    states_provinces=[],
                    uid=tuple(location[1:4]),
                )
                self._locations.regions[-1].countries.append(current_country)
            elif location[3] != -1:
                logger.debug("Found state/province: %s", location[4])
                sp = StateProvince(
                    country=current_country,
                    name=location[4],
                    region=self._locations.regions[-1],
                    uid=tuple(location[1:4]),
                )
                current_country.states_provinces.append(sp)
            else:
                msg = f"Unknown location type: {location}"
                raise ValueError(msg)

        genres_part = parts[1]
        genres_loaded = json.loads(genres_part)
        self._genres = {(g[0], g[1]): g[2] for g in genres_loaded}

    @property
    def locations(self: Radio) -> dict[tuple[int, int, int], str]:
        """Get the countries."""
        if self._locations.regions:
            return self._locations
        self._load_countries_genres()
        return self._locations

    @property
    def genres(self: Radio) -> dict[tuple[int, int], str]:
        """Get the genres."""
        if self._genres is not None:
            return self._genres
        self._load_countries_genres()
        return self._genres

    def add_channel(self: Radio, name: str, url: str, location: str, genre: str) -> None:
        """Add a channel."""
        if not self._locations.regions:
            self._load_countries_genres()
        _location = self._locations.find_by_name(location)
        _genre = next(k for k, v in self.genres.items() if v == genre)
        data = {
            "EX": 0,
            "chName": name,
            "chUrl": url,
            "chCountry": f"{_location.uid[0]};{_location.uid[1]};{_location.uid[2]}",
            "chGenre": f"{_genre[0]};{_genre[1]}",
        }
        _res = self.post("addCh.cgi", data)
        self._favorites = None
        favorites = self.favorites
        return next(fav for fav in favorites if fav.name == name and fav.url == url)
