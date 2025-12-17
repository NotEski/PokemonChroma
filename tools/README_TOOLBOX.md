# Toolbox (Plugin-based Tools)

This terminal-based `toolbox.py` consolidates all scripts in the `tools/` folder into a single plugin-driven application.

## Goals
- Single entry point with plugins loaded from `tools/plugins/`
- Plugins can reference each other; shared code lives in `tools/shared/`
- Config via INI with precedence: CLI > INI > plugin defaults
- Keep direct CLI for each tool, routed through `toolbox.py`

## Usage

List plugins:

```bash
python tools/toolbox.py list
```

Run a plugin and forward args to the underlying script:

```bash
python tools/toolbox.py run asset_downloader -- --help
python tools/toolbox.py run pokeapi_downloader -- --help
python tools/toolbox.py run type_chart -- --help
```

Interactive mode:

```bash
python tools/toolbox.py interactive
```

Override config via CLI (highest precedence):

```bash
python tools/toolbox.py run asset_downloader -c output_dir=assets -c concurrency=8 -- --limit 50
```

Refresh plugins:

```bash
python tools/toolbox.py refresh
```

## Config
See `tools/toolbox.ini`. Add per-plugin overrides under `[plugin:<name>]` sections.

## Notes
- Plugins here wrap existing scripts via `runpy`, preserving their CLIs.
- Shared utilities are under `tools/shared/`.
- Tools operate against the repo root (`tools/..`).
