# ruff: noqa: T201

"""Round trip mgmt of favorites."""
import logging

from pathlib import Path

from py_skytune.radio import Radio


logging.basicConfig(level=logging.DEBUG)

radio = Radio()
radio.delete_all_favorites()

stations = [
    "4517523d-6fb7-4e1b-9b1a-22fcae079099",  # venice
    "160ad93c-7e74-11ea-8a3b-52543be04c81",  # kuow
    "ddf8f87d-beb6-43d6-af5b-4a2026be8867",  # big 615
    "a3a37dbb-823d-49da-88f9-9d22e308c0c1",  # king fm
    "98adecf7-2683-4408-9be7-02d3f9098eb8",  # BBC world service
    "9617a958-0601-11e8-ae97-52543be04c81",  # Radio paradise
    "962a63f2-0601-11e8-ae97-52543be04c81",  # 1.fm country
    "313046e3-b203-4b9d-bc3e-393da7d97126",  # WALM
    "964b2829-0601-11e8-ae97-52543be04c81",  # Sona FM Groove Salad
    "19823255-193f-11ea-a620-52543be04c81",  # Soma FM Jolly Ol' Soul
]

for station in stations:
    fav = radio.add_by_rb_uuid(station)
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

radio.add_favorite(
    name = "1.FM Always Christmas",
    url = "https://strm112.1.fm/christmas_mobile_mp3",
    location = "Switzerland",
    genre = "Holiday & Seasonal",
)

radio.add_favorite(
    name = "WALM Christmas Vinyl",
    url = "http://icecast.walmradio.com:8000/christmas",
    location="New York",
    genre="Holiday & Seasonal",
)

radio.add_favorite(
    name= "SonaFM Folk Forward",
    url = "https://somafm.com/nossl/folkfwd130.pls",
    location="California",
    genre="Various",
)

radio.sort_favorites()

exported = radio.export_favorites()
print(exported)
with Path("sot.json").open("w", encoding="utf-8") as f:
    f.write(exported)

radio.delete_all_favorites()
favorites = radio.import_favorites("sot.json")
for fav in favorites:
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)
