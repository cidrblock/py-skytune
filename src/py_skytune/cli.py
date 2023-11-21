# ruff: noqa: T201
"""The CLI entrypoint for py-skytune."""

from __future__ import annotations

import argparse

from py_skytune.radio import Radio


class Cli:
    """The CLI entrypoint for tunein."""

    def __init__(self: Cli, radio: Radio) -> None:
        """Initialize the CLI entrypoint."""
        self._args: argparse.Namespace
        self._radio = radio

    def parse_args(self: Cli) -> None:
        """Parse the command line arguments."""
        parser = argparse.ArgumentParser(
            description="py-skytune command line interface",
        )

        subparsers = parser.add_subparsers(
            title="Commands",
            dest="subcommand",
            metavar="",
            required=True,
        )

        subparsers.add_parser(
            "favorites",
            help="Search tunein for stations",
        )

        play = subparsers.add_parser(
            "play",
            help="Station to search for",
        )
        play.add_argument(
            "favorite",
            help="Favorite to play",
            nargs="?",
        )

        self._args = parser.parse_args()

    def run(self: Cli) -> None:
        """Run the CLI."""
        if self._args.subcommand == "favorites":
            favorites = self._radio.favorites
            for fav in favorites:
                print(fav.uid, fav.name, fav.location, fav.genre, fav.url)
        elif self._args.subcommand == "play":
            playing = self._radio.play_favorite(int(self._args.favorite))
            print(playing)


def main() -> None:
    """Run the CLI."""
    cli = Cli(radio=Radio())
    cli.parse_args()
    cli.run()


if __name__ == "__main__":
    main()
