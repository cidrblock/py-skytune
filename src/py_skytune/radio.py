"""The radio."""

from __future__ import annotations

import json
import logging

import requests

from .favorites import RE_CHANNEL, RE_FAV, FavDetails, Favorite
from .genre import Genre, Genres, SubGenre
from .locations import Country, Locations, Region, StateProvince


logger = logging.getLogger(__name__)


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
        self._genres: Genres = Genres(genres=[])
        self._locations: Locations = Locations(regions=[])

    def _get(self: Radio, url: str, params: dict) -> requests.Response:
        """Get the URL."""
        res = self.session.get(f"{self.base_url}{url}", params=params)
        return res

    def _post(self: Radio, url: str, data: dict) -> requests.Response:
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
                    favorite["genre"] = self.genres.find_by_uid(genre)
                favorite["skytune_maintained"] = bool(int(favorite["skytune_maintained"]))

                favorites.append(Favorite(**favorite))
        return favorites, fav_details

    def _get_favorites(self: Radio) -> None:
        """Get the favorites."""
        params = {"PG": 0, "EX": 0}
        logger.debug("Getting favorites: page %s", "0")
        res = self._get(url="php/favList.php", params=params)
        logger.debug("page: %s", res.text)
        favorites, fav_details = self._parse_favorite_page(res.text)
        self._favorites = favorites
        if len(self._favorites) >= fav_details.total:
            return
        total_pages = int(fav_details.total // fav_details.items_per_page)
        for page in range(1, total_pages + 1):
            logger.debug("Getting favorites: page %s", page)
            params = {"PG": page, "EX": 0}
            res = self._get(url="php/favList.php", params=params)
            favorites, _ = self._parse_favorite_page(res.text)
            self._favorites.extend(favorites)
        for idx, favorite in enumerate(self._favorites):
            favorite.uid = idx + 1
        return

    def _load_locations(self: Radio, locations_str: str) -> None:
        """Get the locations."""
        locations_str = locations_str.replace("mCountryList = ", "")
        locations_loaded = json.loads(locations_str)
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

    def _load_genres(self: Radio, genres_str: str) -> None:
        """Get the genres."""
        genres_loaded = json.loads(genres_str)
        for genre in genres_loaded:
            if genre[1] == -1:
                logger.debug("Found genre: %s", genre[2])
                self._genres.genres.append(Genre(name=genre[2], uid=tuple(genre[0:2]), subgenres=[]))
            elif genre[1] != -1:
                logger.debug("Found subgenre: %s", genre[2])
                parent_genre = self._genres.find_by_uid((genre[0], -1))
                subgenre = SubGenre(
                    genre=parent_genre, name=genre[2], uid=tuple(genre[0:2]),
                )
                parent_genre.subgenres.append(subgenre)
            else:
                msg = f"Unknown genre type: {genre}"
                raise ValueError(msg)

    def _load_locations_genres(self: Radio) -> None:
        """Get the countries."""
        res = self._get(url="php/get_CG.php", params={})
        text = res.text
        text = text.replace("];", "]").replace("'", '"')
        parts = text.split("mGenreList = ")
        self._load_locations(parts[0])
        self._load_genres(parts[1])


    def add_channel(self: Radio, name: str, url: str, location: str, genre: str) -> None:
        """Add a channel."""
        if not self._locations.regions:
            self._load_locations_genres()
        _location = self.locations.find_by_name(location)
        _genre = self.genres.find_by_name(genre)
        data = {
            "EX": 0,
            "chName": name,
            "chUrl": url,
            "chCountry": f"{_location.uid[0]};{_location.uid[1]};{_location.uid[2]}",
            "chGenre": f"{_genre.uid[0]};{_genre.uid[1]}",
        }
        _res = self._post("addCh.cgi", data)
        self._favorites = None
        favorites = self.favorites
        return next(fav for fav in favorites if fav.name == name and fav.url == url)

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
        res = self._get("php/favList.php", data)
        _stations, fav_details = self._parse_favorite_page(res.text)
        return fav_details.capacity_dict

    @property
    def genres(self: Radio) -> dict[tuple[int, int], str]:
        """Get the genres."""
        if self._genres is not None:
            return self._genres
        self._load_locations_genres()
        return self._genres

    @property
    def locations(self: Radio) -> dict[tuple[int, int, int], str]:
        """Get the countries."""
        if self._locations.regions:
            return self._locations
        self._load_locations_genres()
        return self._locations