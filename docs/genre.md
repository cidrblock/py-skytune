<a id="py_skytune.genre"></a>

# py\_skytune.genre

The genre module.

<a id="py_skytune.genre.Genres"></a>

## Genres Objects

```python
@dataclass
class Genres()
```

All the genres.

<a id="py_skytune.genre.Genres.find_by_uid"></a>

#### find\_by\_uid

```python
def find_by_uid(uid: tuple[int, int]) -> Genre | SubGenre
```

Find a genre by its uid.

<a id="py_skytune.genre.Genres.find_by_name"></a>

#### find\_by\_name

```python
def find_by_name(name: str) -> Genre | SubGenre
```

Find a genre by its name.

<a id="py_skytune.genre.Genre"></a>

## Genre Objects

```python
@dataclass
class Genre()
```

The genre class.

<a id="py_skytune.genre.Genre.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

Return the string representation.

<a id="py_skytune.genre.SubGenre"></a>

## SubGenre Objects

```python
@dataclass
class SubGenre()
```

The SubGenre class.

<a id="py_skytune.genre.SubGenre.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

Return the string representation.

