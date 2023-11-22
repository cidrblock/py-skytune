"""The radio."""

from __future__ import annotations

import contextlib
import json
import logging
import os
import sys

from pathlib import Path

import requests

from pyradios import RadioBrowser

from .data import COUNTRY_MAP, US_STATES
from .favorites import RE_CHANNEL, RE_FAV, FavDetails, Favorite
from .genre import Genre, Genres, SubGenre
from .locations import Country, Locations, Region, StateProvince


logger = logging.getLogger(__name__)


class Radio:
    """The Radio class."""

    def __init__(self: Radio, ip_address: str | None = None) -> None:
        """Initialize the Radio class.

        Args:
            ip_address: The IP address of the radio.
        """
        if ip_address is None:
            try:
                self.ip_address = os.environ.get("SKYTUNE_IP_ADDRESS")
                logger.debug("Using SKYTUNE_IP_ADDRESS: %s", self.ip_address)
            except KeyError as exc:
                msg = "SKYTUNE_IP_ADDRESS not set"
                raise KeyError(msg) from exc
        else:
            self.ip_address = ip_address
        self.session = requests.Session()
        self.base_url = f"http://{self.ip_address}/"
        self._favorites: list[Favorite] | None = None
        self._countries: dict[tuple[int, int, int], str] | None = None
        self._genres: Genres = Genres(genres=[])
        self._locations: Locations = Locations(regions=[])
        self._rb: RadioBrowser | None = None

    def _get(self: Radio, url: str, params: dict) -> requests.Response:
        """Get the URL."""
        try:
            res = self.session.get(f"{self.base_url}{url}", params=params, timeout=5)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            logger.exception("Timeout getting %s, retrying", url)
            try:
                res = self.session.get(f"{self.base_url}{url}", params=params, timeout=5)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                logger.exception("Timeout getting %s, giving up", url)
                sys.exit(1)
        return res

    def _post(self: Radio, url: str, data: dict, params: dict) -> requests.Response:
        """Post the URL."""
        return self.session.post(f"{self.base_url}{url}", data=data, params=params)

    def _parse_favorite_page(self: Radio, page: str) -> tuple[list[Favorite], FavDetails]:
        """Parse the favorite page."""
        # pylint: disable=too-many-locals
        lines = page.split("\n")
        # remove initial favListInfo
        lines = lines[1:-1]
        fav_list_line = next(line for line in lines if line.startswith("favListInfo = "))
        match = RE_FAV.match(fav_list_line)
        if not match:
            err = f"Could not parse favListInfo: {fav_list_line}"
            raise ValueError(err)
        fav_details = FavDetails(**{k: int(v) for k, v in match.groupdict().items()})
        favorites = []
        for line in lines:
            if line.startswith("myFavChannelList.push"):
                match = RE_CHANNEL.match(line)
                if not match:
                    err = f"Could not parse myFavChannelList: {line}"
                    raise ValueError(err)
                favorite = match.groupdict()
                l1, l2, l3 = tuple(int(x) for x in favorite["location"].split(",", maxsplit=2))
                location = (l1, l2, l3)
                location_str = (
                    "Unknown"
                    if location == (-1, -1, -1)
                    else self.locations.find_by_uid(location).name
                )
                g1, g2 = tuple(int(x) for x in favorite["genre"].split(",", maxsplit=1))
                genre = (g1, g2)
                genre_str = "Unknown" if genre == (-1, -1) else self.genres.find_by_uid(genre).name
                skytune_maintained = bool(int(favorite["skytune_maintained"]))

                favorites.append(
                    Favorite(
                        name=favorite["name"],
                        url=favorite["url"],
                        skytune_maintained=skytune_maintained,
                        location=location_str,
                        genre=genre_str,
                    ),
                )
        return favorites, fav_details

    def _get_favorites(self: Radio) -> None:
        """Get the favorites."""
        params = {"PG": 0, "EX": 0}
        logger.debug("Getting favorites: page %s", "0")
        res = self._get(url="php/favList.php", params=params)
        favorites, fav_details = self._parse_favorite_page(res.text)
        self._favorites = favorites
        if len(self._favorites) >= fav_details.total:
            for idx, favorite in enumerate(self._favorites):
                favorite.uid = idx + 1
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
                if current_country is None:
                    msg = f"Found state/province without country: {location}"
                    raise ValueError(msg)
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
        """Get the genres.

        Args:
            genres_str: The genres string.
        """
        genres_loaded = json.loads(genres_str)
        for genre in genres_loaded:
            if genre[1] == -1:
                logger.debug("Found genre: %s", genre[2])
                self._genres.genres.append(
                    Genre(name=genre[2], uid=tuple(genre[0:2]), subgenres=[]),
                )
            elif genre[1] != -1:
                logger.debug("Found subgenre: %s", genre[2])
                parent_genre = self._genres.find_by_uid((genre[0], -1))
                if isinstance(parent_genre, SubGenre):
                    msg = f"Found subgenre with subgenre parent: {genre}"
                    raise ValueError(msg)
                subgenre = SubGenre(
                    genre=parent_genre,
                    name=genre[2],
                    uid=tuple(genre[0:2]),
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

    def add_favorite(  # noqa: PLR0913
        self: Radio,
        name: str,
        url: str,
        location: str,
        genre: str,
        refresh: bool = True,
    ) -> Favorite | None:
        """Add a channel.

        Args:
            name: The name of the channel.
            url: The URL of the channel.
            location: The location of the channel.
            genre: The genre of the channel.
            refresh: Whether to refresh the favorites.


        Returns:
            The new or updated favorite.
        """
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
        _res = self._post(url="addCh.cgi", data=data, params={})
        if refresh:
            self._favorites = None
            try:
                return next(fav for fav in self.favorites if fav.name == name and fav.url == url)
            except StopIteration:
                logger.exception("Could not find favorite: %s %s", name, url)
                logger.exception("Favorites: %s", self.favorites)
                return None
        return None

    def add_by_rb_uuid(self: Radio, rb_uuid: str, refresh: bool = True) -> Favorite:
        """Add a channel from radio browser by uuid.

        Args:
            rb_uuid: The uuid of the channel.
            refresh: Whether to refresh the favorites.

        Returns:
            The new or updated favorite.
        """
        if self._rb is None:
            self._rb = RadioBrowser()
        station = self._rb.station_by_uuid(stationuuid=rb_uuid)[0]
        location = None
        if station["state"]:
            try:
                state = next(
                    (
                        name
                        for name, abbr in US_STATES.items()
                        if station["state"].lower() == abbr.lower()
                    ),
                    None,
                )
                location = self.locations.find_by_name(state)
            except ValueError:
                try:
                    state = next(
                    (
                        name
                        for name, abbr in US_STATES.items()
                        if station["state"].split()[1].lower() == abbr.lower()
                    ),
                    None,
                )
                    location = self.locations.find_by_name(state)
                except (ValueError, IndexError):
                    with contextlib.suppress(ValueError):
                        location = self.locations.find_by_name(station["state"])
        if not location:
            if station["state"]:
                logger.error("Could not find state: %s", station["state"])
            try:
                country = next(
                    (
                        alt
                        for name, alt in COUNTRY_MAP.items()
                        if station["country"].lower() == name.lower()
                    ),
                    None,
                )
                location = self.locations.find_by_name(country)
            except ValueError:
                with contextlib.suppress(ValueError):
                    location = self.locations.find_by_name(station["country"])
        if not location:
            logger.error("Could not find country: %s", station["country"])
            location = self.locations.find_by_name("United States")
        genre = self.genres.find_by_name("Various")
        return self.add_favorite(
            name=station["name"],
            url=station["url_resolved"],
            location=location.name,
            genre=genre.name,
            refresh=True,
        )

    def delete_favorite(self: Radio, favorite_id: int, refresh: bool = True) -> list[Favorite]:
        """Delete a channel.

        Args:
            favorite_id: The favorite to delete.
        """
        data = {"CI": favorite_id - 1}
        _res = self._get(url="delCh.cgi", params=data)
        if refresh:
            self._favorites = None
        return self.favorites

    def delete_all_favorites(self: Radio) -> list[Favorite]:
        """Delete all channels."""
        for fav in reversed(self.favorites):
            self.delete_favorite(fav.uid, refresh=False)
        self._favorites = None
        return self.favorites

    def export_favorites(self: Radio, serialization: str = "json") -> str:
        """Export favorites."""
        if serialization != "json":
            msg = f"Unsupported format: {format}"
            raise RuntimeError(msg)
        favorites = [fav.json() for fav in self.favorites]
        return json.dumps(favorites, indent=4)

    def import_favorites(self: Radio, favorites_file: str) -> list[Favorite]:
        """Import favorites.

        Args:
            favorites_file: The file to import.

        Returns: The favorites.
        """
        file = Path(favorites_file)
        if not file.exists():
            msg = f"File does not exist: {favorites_file}"
            raise RuntimeError(msg)
        with file.open(encoding="utf-8") as f:
            favorites = json.load(f)
        for fav in favorites:
            if fav["skytune_maintained"]:
                logger.error("Skipping skytune maintained favorite: %s", fav["name"])
                continue
            fav.pop("skytune_maintained")
            logger.debug("Adding favorite: %s", fav)
            self.add_favorite(**fav, refresh=False)
        self._favorites = None
        return self.favorites

    def play_favorite(self: Radio, favorite_id: int) -> Favorite:
        """Play a favorite.

        Args:
            favorite: The favorite to play.
        """
        data = {"AI": 16, "CI": favorite_id - 1}
        _res = self._get(url="doApi.cgi", params=data)
        return self.playing

    def sort_favorites(self: Radio, reverse: bool = False) -> list[Favorite]:
        """Sort the favorites.

        Args:
            favorites: The favorites to sort.
        """
        idx = 0
        if self._favorites is None:
            self._get_favorites()
        if self._favorites is None:
            msg = "Could not get favorites"
            raise ValueError(msg)
        sorted_favorites = sorted(self.favorites, key=lambda fav: fav.name.lower())
        if reverse:
            sorted_favorites.reverse()
        while idx < len(self.favorites):
            process = sorted_favorites[idx]
            current_idx = self.favorites.index(process)
            current = self.favorites[current_idx]
            if idx == current_idx:
                logger.debug("Skipping %s %s == %s", current.name, idx, current_idx)
                idx += 1
                continue
            logger.debug("Moving %s to %s from %s", current.name, idx, current_idx)
            params = {"CI": current_idx, "DI": idx, "EX": 0}
            self._post(url="moveCh.cgi", data={}, params=params)
            self._favorites.insert(idx, self._favorites.pop(current_idx))
            idx += 1
        self._favorites = None
        return self.favorites

    @property
    def favorites(self: Radio) -> list[Favorite]:
        """Get the favorites.

        Returns:
            The favorites.
        """
        if self._favorites is not None:
            return self._favorites
        self._get_favorites()
        if self._favorites is None:
            msg = "Could not get favorites"
            raise ValueError(msg)
        return self._favorites

    @property
    def favorites_capacity(self: Radio) -> dict[str, int]:
        """Get the favorites capacity.

        Returns:
            The favorites capacity.
        """
        data = {"PG": 0, "EX": 0}
        logger.debug("Getting favorites: page %s", "0")
        res = self._get("php/favList.php", data)
        _stations, fav_details = self._parse_favorite_page(res.text)
        return fav_details.capacity_dict

    @property
    def genres(self: Radio) -> Genres:
        """Get the genres.

        Returns:
            The genres.
        """
        if self._genres is not None:
            return self._genres
        self._load_locations_genres()
        return self._genres

    @property
    def locations(self: Radio) -> Locations:
        """Get the countries."""
        if self._locations.regions:
            return self._locations
        self._load_locations_genres()
        return self._locations

    @property
    def playing(self: Radio) -> Favorite:
        """Get the currently playing favorite."""
        res = self._get(url="php/playing.php", params={})
        return res.json()
