import argparse
import configparser
import sys
import subprocess
from pathlib import Path
import importlib.util
import types
from typing import Dict, List, Optional

# Paths
TOOLS_DIR = Path(__file__).parent
REPO_ROOT = TOOLS_DIR.parent
SHARED_DIR = TOOLS_DIR / "shared"
PLUGINS_DIR = TOOLS_DIR / "plugins"
INI_PATH = TOOLS_DIR / "toolbox.ini"

# Ensure shared is importable
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from shared.plugin_base import ToolPluginBase  # type: ignore


class PluginManager:
    def __init__(self) -> None:
        self._plugins: Dict[str, ToolPluginBase] = {}
        self._modules: Dict[str, types.ModuleType] = {}

    def discover(self) -> List[Path]:
        paths: List[Path] = []
        if PLUGINS_DIR.exists():
            for p in PLUGINS_DIR.rglob("*.py"):
                if p.name.startswith("_"):
                    continue
                paths.append(p)
        return paths

    def load(self, module_path: Path) -> Optional[ToolPluginBase]:
        spec = importlib.util.spec_from_file_location(module_path.stem, str(module_path))
        if not spec or not spec.loader:
            return None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore
        except Exception as e:
            print(f"Failed to load plugin '{module_path}': {e}")
            return None
        self._modules[module_path.stem] = module
        plugin_cls = getattr(module, "Plugin", None)
        if not plugin_cls:
            return None
        plugin: ToolPluginBase = plugin_cls()
        # Allow plugin to setup
        try:
            plugin.setup(toolbox=self)
        except Exception:
            pass
        self._plugins[plugin.name] = plugin
        return plugin

    def load_all(self) -> None:
        self._plugins.clear()
        self._modules.clear()
        for path in self.discover():
            self.load(path)

    def refresh(self) -> None:
        self.load_all()

    def list(self) -> List[str]:
        return sorted(self._plugins.keys())

    def get(self, name: str) -> Optional[ToolPluginBase]:
        return self._plugins.get(name)

    # Cross-reference helpers for plugins
    def plugin(self, name: str) -> Optional[ToolPluginBase]:
        return self.get(name)


class ConfigLayer:
    def __init__(self, ini_path: Path) -> None:
        self._cfg = configparser.ConfigParser()
        self._cfg.read(ini_path)

    def get_toolbox(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._cfg.get("toolbox", key, fallback=default)

    def plugin_section(self, plugin_name: str) -> str:
        return f"plugin:{plugin_name}"

    def plugin_get(self, plugin_name: str, key: str, default: Optional[str] = None) -> Optional[str]:
        section = self.plugin_section(plugin_name)
        return self._cfg.get(section, key, fallback=default)

    def plugin_items(self, plugin_name: str) -> Dict[str, str]:
        section = self.plugin_section(plugin_name)
        if section in self._cfg:
            return dict(self._cfg[section])
        return {}


def merge_config(cli_kv: Dict[str, str], ini_kv: Dict[str, str], defaults: Dict[str, str]) -> Dict[str, str]:
    # Preference order: CLI > INI > plugin defaults
    out: Dict[str, str] = {}
    out.update(defaults or {})
    out.update(ini_kv or {})
    out.update(cli_kv or {})
    return out


def parse_cli_kv(pairs: List[str]) -> Dict[str, str]:
    kv: Dict[str, str] = {}
    for p in pairs:
        if "=" in p:
            k, v = p.split("=", 1)
            kv[k.strip()] = v.strip()
        else:
            # allow --key value style via parse_known_args
            if p.startswith("--"):
                k = p[2:]
                kv[k] = "true"
    return kv


def interactive(pm: PluginManager, cfg: ConfigLayer) -> int:
    print("Toolbox Interactive Mode")
    while True:
        print("\nPlugins:")
        names = pm.list()
        for i, n in enumerate(names, 1):
            print(f"  {i}. {n}")
        print("  r. refresh plugins")
        print("  q. quit")
        choice = input("Select an option: ").strip().lower()
        if choice in ("q", "quit", "exit"):
            return 0
        if choice in ("r", "refresh"):
            pm.refresh()
            print("Plugins refreshed.")
            continue
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(names):
                print("Invalid selection")
                continue
            name = names[idx]
        except ValueError:
            print("Invalid selection")
            continue
        plugin = pm.get(name)
        if not plugin:
            print("Plugin not found")
            continue
        print(f"Selected plugin: {plugin.name}")
        # Show the underlying script help so the user knows accepted arguments
        help_text = render_plugin_help(plugin)
        if help_text:
            print("\nPlugin CLI (--help):")
            print(help_text)
        else:
            print("\n(No help available; see plugin docs.)")
        print("\nEnter plugin args (space-separated), or empty for none:")
        raw = input("> ").strip()
        script_args = raw.split() if raw else []
        ini_items = cfg.plugin_items(plugin.name)
        merged = merge_config({}, ini_items, plugin.default_config or {})
        try:
            rc = plugin.run(script_args, merged, pm)
        except Exception as e:
            print(f"Plugin '{plugin.name}' error: {e}")
            rc = 1
        print(f"Plugin exit code: {rc}")


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="toolbox", description="PokemonFanGame Tools Toolbox")
    sub = parser.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="List available plugins")

    p_info = sub.add_parser("info", help="Show plugin info")
    p_info.add_argument("plugin", help="Plugin name")

    p_run = sub.add_parser("run", help="Run a plugin and forward args")
    p_run.add_argument("plugin", help="Plugin name")
    p_run.add_argument("--config", "-c", nargs="*", default=[], help="Config overrides as KEY=VALUE")
    p_run.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to the plugin script")

    p_refresh = sub.add_parser("refresh", help="Refresh plugin registry")

    p_inter = sub.add_parser("interactive", help="Interactive terminal UI")

    args = parser.parse_args(argv)

    cfg = ConfigLayer(INI_PATH)
    pm = PluginManager()
    pm.load_all()

    if args.cmd == "list":
        for n in pm.list():
            pl = pm.get(n)
            desc = pl.description if pl else ""
            print(f"{n}: {desc}")
        return 0

    if args.cmd == "info":
        pl = pm.get(args.plugin)
        if not pl:
            print("Plugin not found")
            return 1
        print(f"Name: {pl.name}")
        print(f"Version: {pl.version}")
        print(f"Description: {pl.description}")
        print("Defaults:")
        for k, v in (pl.default_config or {}).items():
            print(f"  {k} = {v}")
        ini_items = cfg.plugin_items(pl.name)
        if ini_items:
            print("INI overrides:")
            for k, v in ini_items.items():
                print(f"  {k} = {v}")
        return 0

    if args.cmd == "run":
        pl = pm.get(args.plugin)
        if not pl:
            print("Plugin not found")
            return 1
        cli_kv = parse_cli_kv(args.config)
        ini_items = cfg.plugin_items(pl.name)
        merged = merge_config(cli_kv, ini_items, pl.default_config or {})
        # Forward everything after '--' or remaining
        forwarded = args.args
        if forwarded and forwarded[0] == "--":
            forwarded = forwarded[1:]
        try:
            return int(pl.run(forwarded, merged, pm))
        except Exception as e:
            print(f"Plugin '{pl.name}' error: {e}")
            return 1

    if args.cmd == "refresh":
        pm.refresh()
        print("Plugins refreshed.")
        return 0

    if args.cmd == "interactive":
        return int(interactive(pm, cfg) or 0)

    # Default to interactive if no subcommand
    return int(interactive(pm, cfg) or 0)


def render_plugin_help(plugin: ToolPluginBase) -> str:
    script_path = getattr(plugin, "_script_path", None)
    if not script_path:
        return ""
    try:
        # Use the real interpreter to capture help output for clarity
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip()
    except Exception:
        return ""


if __name__ == "__main__":
    # Check if --cli flag is provided for CLI mode
    if "--cli" in sys.argv:
        # Remove --cli flag and run CLI mode
        sys.argv.remove("--cli")
        raise SystemExit(main())
    else:
        # Default to GUI mode
        try:
            from toolbox_gui import main as gui_main  # type: ignore
            gui_main()
        except ImportError as e:
            print(f"Error: Could not import GUI: {e}")
            print("Falling back to CLI mode...")
            raise SystemExit(main())
        except Exception as e:
            print(f"Error running GUI: {e}")
            print("Falling back to CLI mode...")
            raise SystemExit(main())
