# py-skytune

Python API for skytune radios

# Quick start

```python


from py_skytune.radio import Radio
radio = Radio(ip_address="192.168.1.9")

# Get favorites
favs = radio.favorites
print(f"\nFavorites{'-'*50}")
for fav in favs:
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

# Play a favorite
playing = radio.play_favorite(1)
print(playing)

# Sort the favorites
sorted_favorites = radio.sort_favorites(reverse=False)
for fav in sorted_favorites:
    print(fav.uid, fav.name, fav.location, fav.genre, fav.url)

```

## Documentation

See the `docs` directory or the source.

## Rebuild docs

```
pydoc-markdown -m py_skytune.radio -I src > docs/radio.md
pydoc-markdown -m py_skytune.favorites -I src > docs/favorites.md
pydoc-markdown -m py_skytune.genre -I src > docs/genre.md    
pydoc-markdown -m py_skytune.locations -I src > docs/locations.md
```