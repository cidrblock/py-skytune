<a id="py_skytune.radio"></a>

# py\_skytune.radio

The radio.

<a id="py_skytune.radio.Radio"></a>

## Radio Objects

```python
class Radio()
```

The Radio class.

<a id="py_skytune.radio.Radio.__init__"></a>

#### \_\_init\_\_

```python
def __init__(ip_address: str) -> None
```

Initialize the Radio class.

**Arguments**:

- `ip_address` - The IP address of the radio.

<a id="py_skytune.radio.Radio.add_favorite"></a>

#### add\_favorite

```python
def add_favorite(name: str,
                 url: str,
                 location: str,
                 genre: str,
                 refresh: bool = True) -> Favorite | None
```

Add a channel.

**Arguments**:

- `name` - The name of the channel.
- `url` - The URL of the channel.
- `location` - The location of the channel.
- `genre` - The genre of the channel.
- `refresh` - Whether to refresh the favorites.
  
  

**Returns**:

  The new or updated favorite.

<a id="py_skytune.radio.Radio.add_by_rb_uuid"></a>

#### add\_by\_rb\_uuid

```python
def add_by_rb_uuid(rb_uuid: str, refresh: bool = True) -> Favorite
```

Add a channel from radio browser by uuid.

**Arguments**:

- `rb_uuid` - The uuid of the channel.
- `refresh` - Whether to refresh the favorites.
  

**Returns**:

  The new or updated favorite.

<a id="py_skytune.radio.Radio.delete_favorite"></a>

#### delete\_favorite

```python
def delete_favorite(favorite_id: int, refresh: bool = True) -> list[Favorite]
```

Delete a channel.

**Arguments**:

- `favorite_id` - The favorite to delete.

<a id="py_skytune.radio.Radio.delete_all_favorites"></a>

#### delete\_all\_favorites

```python
def delete_all_favorites() -> list[Favorite]
```

Delete all channels.

<a id="py_skytune.radio.Radio.export_favorites"></a>

#### export\_favorites

```python
def export_favorites(serialization: str = "json") -> str
```

Export favorites.

<a id="py_skytune.radio.Radio.import_favorites"></a>

#### import\_favorites

```python
def import_favorites(favorites_file: str) -> list[Favorite]
```

Import favorites.

**Arguments**:

- `favorites_file` - The file to import.
  
- `Returns` - The favorites.

<a id="py_skytune.radio.Radio.play_favorite"></a>

#### play\_favorite

```python
def play_favorite(favorite_id: int) -> Favorite
```

Play a favorite.

**Arguments**:

- `favorite` - The favorite to play.

<a id="py_skytune.radio.Radio.sort_favorites"></a>

#### sort\_favorites

```python
def sort_favorites(reverse: bool = False) -> list[Favorite]
```

Sort the favorites.

**Arguments**:

- `favorites` - The favorites to sort.

<a id="py_skytune.radio.Radio.favorites"></a>

#### favorites

```python
@property
def favorites() -> list[Favorite]
```

Get the favorites.

**Returns**:

  The favorites.

<a id="py_skytune.radio.Radio.favorites_capacity"></a>

#### favorites\_capacity

```python
@property
def favorites_capacity() -> dict[str, int]
```

Get the favorites capacity.

**Returns**:

  The favorites capacity.

<a id="py_skytune.radio.Radio.genres"></a>

#### genres

```python
@property
def genres() -> Genres
```

Get the genres.

**Returns**:

  The genres.

<a id="py_skytune.radio.Radio.locations"></a>

#### locations

```python
@property
def locations() -> Locations
```

Get the countries.

<a id="py_skytune.radio.Radio.playing"></a>

#### playing

```python
@property
def playing() -> Favorite
```

Get the currently playing favorite.

