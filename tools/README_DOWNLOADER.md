# PokeAPI Downloader

A flexible Python module for downloading data from the PokeAPI. Can be used as both a command-line tool and a Python module.

## Features

- Download specific endpoints or all available data
- Use as a CLI tool or import as a module
- Concurrent downloads with configurable workers
- Progress tracking and verbose/quiet modes
- Automatic retry and error handling
- Organized folder structure with index files

## Installation

No additional dependencies beyond `requests` (already in requirements.txt).

## CLI Usage

### Download specific endpoints

```bash
python download_pokeapi.py --endpoints pokemon move ability
```

### Download all endpoints

```bash
python download_pokeapi.py --all
```

### List available endpoints

```bash
python download_pokeapi.py --list
```

### Custom output directory

```bash
python download_pokeapi.py --endpoints pokemon --output my_data
```

### Quiet mode (no progress output)

```bash
python download_pokeapi.py --endpoints pokemon --quiet
```

### Adjust concurrent workers

```bash
python download_pokeapi.py --endpoints pokemon --workers 20
```

### Interactive mode (no arguments)

```bash
python download_pokeapi.py
```

This will prompt you to choose between downloading common endpoints or all endpoints.

## Module Usage

### Basic Usage

```python
from tools.download_pokeapi import download_pokemon_data

# Download specific endpoints
results = download_pokemon_data(
    output_dir="my_pokemon_data",
    endpoints=["pokemon", "move", "ability"]
)

print(f"Downloaded: {results}")
# Output: {'pokemon': 1025, 'move': 937, 'ability': 367}
```

### Using the PokeAPIDownloader Class

```python
from tools.download_pokeapi import PokeAPIDownloader

# Create a downloader instance
downloader = PokeAPIDownloader(
    output_dir="pokeapi_database",
    verbose=True
)

# Download specific endpoints
results = downloader.download_endpoints(
    endpoints=["type", "ability", "item"],
    max_workers=10
)

# Download all endpoints
results = downloader.download_all(max_workers=10)
```

### List Available Endpoints

```python
from tools.download_pokeapi import PokeAPIDownloader

endpoints = PokeAPIDownloader.list_available_endpoints()
print(endpoints)
```

### Quiet Mode

```python
from tools.download_pokeapi import download_pokemon_data

# Download without progress output
results = download_pokemon_data(
    endpoints=["pokemon"],
    verbose=False
)
```

## Available Endpoints

- `pokemon` - Pokemon species data
- `move` - Move data
- `ability` - Ability data
- `type` - Type effectiveness data
- `item` - Item data
- `berry` - Berry data
- `evolution-chain` - Evolution chain data
- `generation` - Generation data
- `pokedex` - Pokedex data
- `location` - Location data
- `nature` - Nature data
- `stat` - Stat data
- And many more! Use `--list` to see all.

## Output Structure

Downloaded data is organized as follows:

```
pokeapi_database/
├── summary.json           # Summary of downloaded data
├── pokemon/
│   ├── _index.json       # Index of all pokemon
│   ├── 0001-bulbasaur.json
│   ├── 0002-ivysaur.json
│   └── ...
├── move/
│   ├── _index.json
│   ├── pound.json
│   └── ...
└── ability/
    ├── _index.json
    ├── overgrow.json
    └── ...
```

## API Reference

### `PokeAPIDownloader`

Main class for downloading PokeAPI data.

**Constructor:**
```python
PokeAPIDownloader(
    base_url: str = "https://pokeapi.co/api/v2",
    output_dir: Union[str, Path] = "pokeapi_database",
    verbose: bool = True
)
```

**Methods:**

- `download_endpoints(endpoints: List[str], max_workers: int = 10) -> Dict[str, int]`
  - Download specific endpoints
  - Returns dictionary of endpoint names to resource counts

- `download_all(max_workers: int = 10) -> Dict[str, int]`
  - Download all available endpoints
  - Returns dictionary of endpoint names to resource counts

- `list_available_endpoints() -> List[str]` (static method)
  - Returns list of all available endpoints

### `download_pokemon_data`

Convenience function for quick downloads.

```python
download_pokemon_data(
    output_dir: Union[str, Path] = "pokeapi_database",
    endpoints: Optional[List[str]] = None,
    verbose: bool = True
) -> Dict[str, int]
```

If `endpoints` is None, downloads common endpoints: `["pokemon", "move", "ability", "type", "item"]`

## Examples

See `example_usage.py` for more detailed examples:

```bash
python example_usage.py
```

## Notes

- Files are not re-downloaded if they already exist
- Downloads use concurrent workers for speed
- Progress is tracked and displayed (unless in quiet mode)
- A small delay is added between endpoints to be polite to the API
- Each endpoint directory contains an `_index.json` file with metadata
- A `summary.json` file is created with overall statistics
