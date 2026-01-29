"""PokeAPI downloader plugin with GUI support."""

from __future__ import annotations

import json
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List, Union

import requests

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase

BASE_URL = "https://pokeapi.co/api/v2"

# Common endpoints for typical usage
COMMON_ENDPOINTS = ["pokemon", "move", "ability", "item", "type"]

# Full list of available endpoints
AVAILABLE_ENDPOINTS = [
    "berry",
    "berry-firmness",
    "berry-flavor",
    "contest-type",
    "contest-effect",
    "super-contest-effect",
    "encounter-method",
    "encounter-condition",
    "encounter-condition-value",
    "evolution-chain",
    "evolution-trigger",
    "generation",
    "pokedex",
    "version",
    "version-group",
    "item",
    "item-attribute",
    "item-category",
    "item-fling-effect",
    "item-pocket",
    "location",
    "location-area",
    "pal-park-area",
    "region",
    "machine",
    "move",
    "move-ailment",
    "move-battle-style",
    "move-category",
    "move-damage-class",
    "move-learn-method",
    "move-target",
    "ability",
    "characteristic",
    "egg-group",
    "gender",
    "growth-rate",
    "nature",
    "pokeathlon-stat",
    "pokemon",
    "pokemon-color",
    "pokemon-form",
    "pokemon-habitat",
    "pokemon-shape",
    "pokemon-species",
    "stat",
    "type",
    "language",
]


class PokeAPIDownloader:
    """A downloader for PokeAPI data."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        output_dir: Union[str, Path] = "pokeapi_database",
        verbose: bool = True,
    ):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "PokeAPI-Downloader/1.0"})

    def _print(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def create_directory_structure(self) -> None:
        """Create the base directory structure."""
        self.output_dir.mkdir(exist_ok=True)
        self._print(f"Created output directory: {self.output_dir}")

    def get_resource_list(self, endpoint: str) -> List[Dict[str, str]]:
        """Get the complete list of resources for an endpoint."""
        all_results: List[Dict[str, str]] = []
        url = f"{self.base_url}/{endpoint}?limit=100000"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_results = data.get("results", [])

            for resource in all_results:
                if "name" not in resource and "url" in resource:
                    resource["name"] = resource["url"].rstrip("/").split("/")[-1]

            self._print(f"Found {len(all_results)} items for {endpoint}")
            return all_results
        except Exception as e:
            self._print(f"Error fetching resource list for {endpoint}: {e}")
            return []

    def download_resource(self, url: str, endpoint: str, name: str) -> bool:
        """Download a single resource and save it as JSON."""
        try:
            endpoint_dir = self.output_dir / endpoint
            endpoint_dir.mkdir(exist_ok=True)

            if endpoint == "pokemon":
                pokemon_id = url.rstrip("/").split("/")[-1]
                filename = f"{int(pokemon_id):04d}-{name}.json"
            else:
                filename = f"{name}.json"

            file_path = endpoint_dir / filename

            if file_path.exists():
                return True

            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            if self.verbose:
                print(f"Error downloading {name} from {endpoint}: {e}")
            return False

    def download_endpoint(self, endpoint: str, max_workers: int = 10) -> None:
        """Download all resources for a specific endpoint."""
        self._print(f"\n{'=' * 60}")
        self._print(f"Downloading {endpoint}...")
        self._print(f"{'=' * 60}")

        resources = self.get_resource_list(endpoint)

        if not resources:
            self._print(f"No resources found for {endpoint}")
            return

        success_count = 0
        fail_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.download_resource, resource["url"], endpoint, resource["name"]
                ): resource["name"]
                for resource in resources
            }

            for i, future in enumerate(as_completed(futures), 1):
                name = futures[future]
                try:
                    if future.result():
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    self._print(f"Exception for {name}: {e}")
                    fail_count += 1

                if self.verbose and (i % 50 == 0 or i == len(resources)):
                    print(
                        f"Progress: {i}/{len(resources)} ({success_count} success, {fail_count} failed)"
                    )

        self._print(
            f"\nCompleted {endpoint}: {success_count} successful, {fail_count} failed"
        )

    def download_endpoints(
        self, endpoints: List[str], max_workers: int = 10
    ) -> None:
        """Download data for multiple endpoints."""
        self.create_directory_structure()

        for endpoint in endpoints:
            if endpoint not in AVAILABLE_ENDPOINTS:
                self._print(f"Warning: Unknown endpoint '{endpoint}'")
                continue
            self.download_endpoint(endpoint, max_workers)

        self._print("\n" + "=" * 60)
        self._print("Download complete!")
        self._print("=" * 60)


class Plugin(ToolPluginBase):
    """Plugin for downloading PokeAPI data."""

    name = "pokeapi_downloader"
    version = "1.0.0"
    description = "Download and cache data from the PokeAPI"
    default_config: Dict[str, str] = {
        "database_dir": "pokeapi_database",
    }

    def setup(self, toolbox: Any) -> None:
        """Initialize the plugin."""
        # No external script needed - logic is embedded

    def get_form_fields(self) -> List[FormFieldSpec]:
        """Get form field specifications."""
        return [
            FormFieldSpec(
                name="mode",
                label="Download Mode",
                field_type="combobox",
                choices=["Common Endpoints", "All Endpoints", "Custom"],
                default="Common Endpoints",
                required=True,
                help_text="What data to download",
            ),
            FormFieldSpec(
                name="endpoints",
                label="Custom Endpoints",
                field_type="text",
                default="",
                help_text="Comma-separated endpoints (for Custom mode)",
            ),
            FormFieldSpec(
                name="output_dir",
                label="Output Directory",
                field_type="directory",
                default=self.default_config["database_dir"],
                required=True,
            ),
            FormFieldSpec(
                name="workers",
                label="Concurrent Workers",
                field_type="spinbox",
                default="10",
                help_text="Number of concurrent downloads",
            ),
            FormFieldSpec(
                name="quiet",
                label="Quiet Mode",
                field_type="checkbox",
                default=False,
            ),
        ]

    def create_ui(
        self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
    ) -> tk.Frame:
        """Create the plugin's GUI interface."""
        frame = tk.Frame(parent)

        desc = ttk.Label(
            frame,
            text=self.description,
            wraplength=700,
            font=("TkDefaultFont", 10, "bold"),
        )
        desc.pack(pady=10)

        form_frame = tk.Frame(frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        form_frame.columnconfigure(1, weight=1)

        self.form_builder = FormBuilder(form_frame)

        for field_spec in self.get_form_fields():
            if field_spec.name in config:
                field_spec.default = config[field_spec.name]
            self.form_builder.add_field(field_spec)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        run_btn = ttk.Button(
            button_frame, text="Download Data", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        return frame

    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute the PokeAPI download with embedded business logic."""
        output_dir = form_data.get("output_dir", "pokeapi_database")
        workers = int(form_data.get("workers", 10))
        verbose = not form_data.get("quiet", False)

        downloader = PokeAPIDownloader(
            output_dir=output_dir, verbose=verbose
        )

        mode = form_data.get("mode", "Common Endpoints")

        if mode == "All Endpoints":
            downloader.download_endpoints(AVAILABLE_ENDPOINTS, max_workers=workers)
        elif mode == "Custom":
            endpoints_str = form_data.get("endpoints", "")
            if endpoints_str:
                endpoints = [
                    e.strip() for e in endpoints_str.split(",") if e.strip()
                ]
                downloader.download_endpoints(endpoints, max_workers=workers)
        else:  # Common Endpoints
            downloader.download_endpoints(COMMON_ENDPOINTS, max_workers=workers)
