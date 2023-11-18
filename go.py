from py_skytune import Radio

import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("charset_normalizer").setLevel(logging.INFO)


radio = Radio(ip_address="192.168.1.11")

favs = radio.favorites
for fav in favs:
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

capacity = radio.favorites_capacity
print(capacity)

locations = radio.locations
for region in locations.regions:
    for country in region.countries:
        print(country, country.uid)
        for state in country.states_provinces:
            print(state, state.uid)


genres = radio.genres
print(genres)

fav = radio.add_channel(
    "Radio 1 Rock",
    "http://stream.radioreklama.bg:80/radio1rock128",
    "United States",
    "Old Time Radio",
)
print(fav.uid, fav.name, fav.location, fav.genre, fav.url)
