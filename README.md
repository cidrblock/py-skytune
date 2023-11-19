# py-skytune

Python API for skytune radios

# Usage

```python
# ruff: noqa: T201

import logging

from py_skytune.radio import Radio


logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("charset_normalizer").setLevel(logging.INFO)


radio = Radio(ip_address="192.168.1.9")

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
fav = radio.add_channel(
    "Radio 1 Rock",
    "http://stream.radioreklama.bg:80/radio1rock128",
    "United States",
    "Old Time Radio",
)
print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

```