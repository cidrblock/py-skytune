"""Favorites classes."""

from __future__ import annotations

import html
import re

from dataclasses import dataclass


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
    uid: int = -1

    def __post_init__(self: Favorite) -> None:
        """Post init."""
        # the skytune api may return html encoded chars
        self.name = html.unescape(self.name)

    def json(self: Favorite) -> dict[str, str]:
        """Get the JSON representation."""
        return {
            "name": self.name,
            "url": self.url,
            "skytune_maintained": self.skytune_maintained,
            "location": self.location,
            "genre": self.genre,
        }
