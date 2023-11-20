# ruff: noqa: T201

import logging

from pathlib import Path

from py_skytune.radio import Radio


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("charset_normalizer").setLevel(logging.INFO)


radio = Radio(ip_address="192.168.1.11")

favs = radio.favorites
print(f"\nFavorites{'-'*50}")
for fav in favs:
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

print(f"\nCapacity{'-'*50}")
capacity = radio.favorites_capacity
print(capacity)

print(f"\nLocations{'-'*50}")

locations = radio.locations
for region in locations.regions:
    for country in region.countries:
        print(country, country.uid)
        for state in country.states_provinces:
            print(state, state.uid)

print(f"\nGenres{'-'*50}")
genres = radio.genres
for genre in genres.genres:
    for subgenre in genre.subgenres:
        print(subgenre)

print(f"\nAdd channel{'-'*50}")
fav = radio.add_favorite(
    "KEXP",
    "https://kexp.streamguys1.com/kexp160.aac",
    "Washington",
    "Pop",
)
print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

playing = radio.play_favorite(fav.uid)
print(playing)

updated_stations = radio.delete_favorite(fav.uid)
for fav in favs:
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

sorted_favorites = radio.sort_favorites(reverse=False)
for fav in sorted_favorites:
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)
