"""The genre module."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Genres:
    """All the genres."""

    genres: list[Genre]

    def find_by_uid(self: Genres, uid: tuple[int, int]) -> Genre | SubGenre:
        """Find a genre by its uid."""
        for genre in self.genres:
            if genre.uid == uid:
                return genre
            for subgenre in genre.subgenres:
                if subgenre.uid == uid:
                    return subgenre
        msg = f"Could not find genre with uid {uid}"
        raise ValueError(msg)

    def find_by_name(self: Genres, name: str) -> Genre | SubGenre:
        """Find a genre by its name."""
        for genre in self.genres:
            if genre.name == name:
                return genre
            for subgenre in genre.subgenres:
                if subgenre.name == name:
                    return subgenre
        msg = f"Could not find genre with name {name}"
        raise ValueError(msg)


@dataclass
class Genre:
    """The genre class."""

    uid: tuple[int, int]
    name: str
    subgenres: list[SubGenre]

    def __str__(self: Genre) -> str:
        """Return the string representation."""
        return self.name


@dataclass
class SubGenre:
    """The SubGenre class."""

    uid: tuple[int, int]
    name: str
    genre: Genre

    def __str__(self: SubGenre) -> str:
        """Return the string representation."""
        return f"{self.genre}/{self.name}"
