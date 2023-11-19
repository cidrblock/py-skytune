<a id="py_skytune.locations"></a>

# py\_skytune.locations

Location classes.

<a id="py_skytune.locations.Locations"></a>

## Locations Objects

```python
@dataclass
class Locations()
```

The Loactions class.

<a id="py_skytune.locations.Locations.find_by_uid"></a>

#### find\_by\_uid

```python
def find_by_uid(uid: tuple[int, int, int]) -> Country | StateProvince
```

Find a country by its uid.

<a id="py_skytune.locations.Locations.find_by_name"></a>

#### find\_by\_name

```python
def find_by_name(name: str) -> Country | StateProvince
```

Find a country by its name.

<a id="py_skytune.locations.Region"></a>

## Region Objects

```python
@dataclass
class Region()
```

The ParentLocation class.

<a id="py_skytune.locations.Region.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

Return the string representation.

<a id="py_skytune.locations.Country"></a>

## Country Objects

```python
@dataclass
class Country()
```

The SubLocation class.

<a id="py_skytune.locations.Country.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

Return the string representation.

<a id="py_skytune.locations.StateProvince"></a>

## StateProvince Objects

```python
@dataclass
class StateProvince()
```

The StateProvince class.

<a id="py_skytune.locations.StateProvince.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

Return the string representation.

