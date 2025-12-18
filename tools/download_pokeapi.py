"""
PokeAPI Database Downloader

This module downloads data from PokeAPI and organizes it into
a well-structured folder hierarchy with JSON files.

Can be used as a module or CLI tool:
    # As a module
    from tools.download_pokeapi import PokeAPIDownloader
    downloader = PokeAPIDownloader()
    downloader.download_endpoints(["pokemon", "move"])
    
    # As CLI
    python download_pokeapi.py --endpoints pokemon move
"""

import requests
import json
import os
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Union

# Base API URL
BASE_URL = "https://pokeapi.co/api/v2"

# Default output directory
DEFAULT_OUTPUT_DIR = Path("pokeapi_database")

# Available API endpoints
AVAILABLE_ENDPOINTS = [
    # Berry-related endpoints
    "berry",
    "berry-firmness",
    "berry-flavor",

    # Contest-related endpoints
    "contest-type",
    "contest-effect",
    "super-contest-effect",

    # Encounter-related endpoints
    "encounter-method",
    "encounter-condition",
    "encounter-condition-value",

    # Evolution-related endpoints
    "evolution-chain",
    "evolution-trigger",

    # Game-related endpoints
    "generation",
    "pokedex",
    "version",
    "version-group",

    # Item-related endpoints
    "item",
    "item-attribute",
    "item-category",
    "item-fling-effect",
    "item-pocket",

    # Location-related endpoints
    "location",
    "location-area",
    "pal-park-area",
    "region",

    # Machine-related endpoints
    "machine",

    # Move-related endpoints
    "move",
    "move-ailment",
    "move-battle-style",
    "move-category",
    "move-damage-class",
    "move-learn-method",
    "move-target",

    # Pokémon-related endpoints
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
    
    # Utility endpoints
    "language",
]


class PokeAPIDownloader:
    """
    A downloader for PokeAPI data.
    
    Args:
        base_url: Base URL for the PokeAPI (default: https://pokeapi.co/api/v2)
        output_dir: Directory to save downloaded data (default: pokeapi_database)
        verbose: Whether to print progress messages (default: True)
    """
    
    def __init__(
        self, 
        base_url: str = BASE_URL, 
        output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
        verbose: bool = True
    ):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "PokeAPI-Downloader/1.0"})
        
    def _print(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)
        
    def create_directory_structure(self):
        """Create the base directory structure."""
        self.output_dir.mkdir(exist_ok=True)
        self._print(f"Created output directory: {self.output_dir}")
        
    def get_resource_list(self, endpoint: str) -> List[Dict[str, str]]:
        """Get the complete list of resources for an endpoint."""
        all_results = []
        url = f"{self.base_url}/{endpoint}?limit=100000"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_results = data.get("results", [])
            
            # Some endpoints don't have 'name', extract from URL instead
            for resource in all_results:
                if "name" not in resource and "url" in resource:
                    # Extract the last part of the URL as the identifier
                    resource["name"] = resource["url"].rstrip("/").split("/")[-1]
            
            self._print(f"Found {len(all_results)} items for {endpoint}")
            return all_results
        except Exception as e:
            self._print(f"Error fetching resource list for {endpoint}: {e}")
            return []
    
    def download_resource(self, url: str, endpoint: str, name: str) -> bool:
        """Download a single resource and save it as JSON."""
        try:
            # Create endpoint directory
            endpoint_dir = self.output_dir / endpoint
            endpoint_dir.mkdir(exist_ok=True)

            # For Pokemon, extract ID from URL to construct filename with prefix
            if endpoint == "pokemon":
                # Extract ID from URL: https://pokeapi.co/api/v2/pokemon/133/ -> 133
                pokemon_id = url.rstrip("/").split("/")[-1]
                filename = f"{int(pokemon_id):04d}-{name}.json"
            else:
                filename = f"{name}.json"

            file_path = endpoint_dir / filename
            
            # Skip if file already exists
            if file_path.exists():
                return True

            # Download the resource
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Save the JSON file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error downloading {name} from {endpoint}: {e}")
            return False
    
    def download_endpoint(self, endpoint: str, max_workers: int = 10):
        """Download all resources for a specific endpoint."""
        self._print(f"\n{'='*60}")
        self._print(f"Downloading {endpoint}...")
        self._print(f"{'='*60}")
        
        # Get list of all resources
        resources = self.get_resource_list(endpoint)
        
        if not resources:
            self._print(f"No resources found for {endpoint}")
            return
        
        # Download resources with threading
        success_count = 0
        fail_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            futures = {
                executor.submit(
                    self.download_resource, 
                    resource["url"], 
                    endpoint, 
                    resource["name"]
                ): resource["name"]
                for resource in resources
            }
            
            # Process completed tasks
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
                
                # Progress indicator
                if self.verbose and (i % 50 == 0 or i == len(resources)):
                    print(f"Progress: {i}/{len(resources)} ({success_count} success, {fail_count} failed)")
        
        self._print(f"\nCompleted {endpoint}: {success_count} successful, {fail_count} failed")
        
        # Save index file
        self.save_index(endpoint, resources)
    
    def save_index(self, endpoint: str, resources: List[Dict[str, str]]):
        """Save an index file for the endpoint."""
        index_path = self.output_dir / endpoint / "_index.json"
        index_data = {
            "endpoint": endpoint,
            "count": len(resources),
            "resources": resources
        }
        
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        self._print(f"Saved index file: {index_path}")
    
    def download_endpoints(
        self, 
        endpoints: Optional[List[str]] = None, 
        max_workers: int = 10
    ) -> Dict[str, int]:
        """
        Download data from specified endpoints.
        
        Args:
            endpoints: List of endpoint names to download. If None, downloads all available.
            max_workers: Number of concurrent workers for downloads.
            
        Returns:
            Dictionary mapping endpoint names to number of resources downloaded.
        """
        start_time = time.time()
        
        # Use all endpoints if none specified
        if endpoints is None:
            endpoints = AVAILABLE_ENDPOINTS
        
        # Validate endpoints
        invalid_endpoints = [ep for ep in endpoints if ep not in AVAILABLE_ENDPOINTS]
        if invalid_endpoints:
            raise ValueError(
                f"Invalid endpoints: {invalid_endpoints}. "
                f"Available endpoints: {AVAILABLE_ENDPOINTS}"
            )
        
        self._print(f"Starting PokeAPI database download...")
        self._print(f"Output directory: {self.output_dir.absolute()}")
        self._print(f"Endpoints to download: {len(endpoints)}")
        
        self.create_directory_structure()
        
        results = {}
        for i, endpoint in enumerate(endpoints, 1):
            self._print(f"\n[{i}/{len(endpoints)}] Processing endpoint: {endpoint}")
            self.download_endpoint(endpoint, max_workers)
            
            # Count downloaded resources
            endpoint_dir = self.output_dir / endpoint
            if endpoint_dir.exists():
                file_count = len([f for f in endpoint_dir.glob("*.json") if f.name != "_index.json"])
                results[endpoint] = file_count
            else:
                results[endpoint] = 0
            
            time.sleep(0.5)  # Small delay between endpoints to be polite
        
        elapsed_time = time.time() - start_time
        self._print(f"\n{'='*60}")
        self._print(f"Download complete!")
        self._print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        self._print(f"Data saved to: {self.output_dir.absolute()}")
        self._print(f"{'='*60}")
        
        # Create a summary file
        self.create_summary()
        
        return results
    
    def download_all(self, max_workers: int = 10) -> Dict[str, int]:
        """
        Download all available endpoints.
        
        Args:
            max_workers: Number of concurrent workers for downloads.
            
        Returns:
            Dictionary mapping endpoint names to number of resources downloaded.
        """
        return self.download_endpoints(AVAILABLE_ENDPOINTS, max_workers)
    
    def create_summary(self):
        """Create a summary file with statistics."""
        summary = {
            "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "endpoints": {}
        }
        
        total_files = 0
        for endpoint_dir in self.output_dir.iterdir():
            if endpoint_dir.is_dir():
                files = list(endpoint_dir.glob("*.json"))
                # Exclude the index file from count
                file_count = len([f for f in files if f.name != "_index.json"])
                summary["endpoints"][endpoint_dir.name] = file_count
                total_files += file_count
        
        summary["total_resources"] = total_files
        
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self._print(f"\nSummary saved to: {summary_path}")
        self._print(f"Total resources downloaded: {total_files}")
    
    @staticmethod
    def list_available_endpoints() -> List[str]:
        """Return a list of all available endpoints."""
        return AVAILABLE_ENDPOINTS.copy()


def download_pokemon_data(
    output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
    endpoints: Optional[List[str]] = None,
    verbose: bool = True
) -> Dict[str, int]:
    """
    Convenience function to download PokeAPI data.
    
    Args:
        output_dir: Directory to save downloaded data.
        endpoints: List of endpoint names to download. If None, downloads common ones.
        verbose: Whether to print progress messages.
        
    Returns:
        Dictionary mapping endpoint names to number of resources downloaded.
        
    Example:
        # Download just pokemon and moves
        download_pokemon_data(endpoints=["pokemon", "move"])
        
        # Download all available data
        download_pokemon_data(endpoints=None)
    """
    if endpoints is None:
        # Default to commonly used endpoints
        endpoints = ["pokemon", "move", "ability", "type", "item"]
    
    downloader = PokeAPIDownloader(output_dir=output_dir, verbose=verbose)
    return downloader.download_endpoints(endpoints)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Download data from PokeAPI and organize it into JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download specific endpoints
  python download_pokeapi.py --endpoints pokemon move ability
  
  # Download all available endpoints
  python download_pokeapi.py --all
  
  # Download to a custom directory
  python download_pokeapi.py --endpoints pokemon --output my_data
  
  # List available endpoints
  python download_pokeapi.py --list
  
  # Silent mode (no progress output)
  python download_pokeapi.py --endpoints pokemon --quiet
        """
    )
    
    parser.add_argument(
        "--endpoints",
        nargs="+",
        metavar="ENDPOINT",
        help="Specific endpoints to download (e.g., pokemon move ability)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all available endpoints"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available endpoints and exit"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for downloaded data (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=10,
        help="Number of concurrent download workers (default: 10)"
    )
    
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Handle --list flag
    if args.list:
        print("Available endpoints:")
        for endpoint in AVAILABLE_ENDPOINTS:
            print(f"  - {endpoint}")
        return
    
    # Determine which endpoints to download
    if args.all:
        endpoints = AVAILABLE_ENDPOINTS
    elif args.endpoints:
        endpoints = args.endpoints
    else:
        # Default behavior: prompt user
        print("PokeAPI Database Downloader")
        print("=" * 60)
        print("\nNo endpoints specified. Choose an option:")
        print("  1. Download common endpoints (pokemon, move, ability, type, item)")
        print("  2. Download all available endpoints")
        print("  3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            endpoints = ["pokemon", "move", "ability", "type", "item"]
        elif choice == "2":
            endpoints = AVAILABLE_ENDPOINTS
        else:
            print("Exiting.")
            return
    
    # Confirm download
    if not args.quiet:
        print("\nPokeAPI Database Downloader")
        print("=" * 60)
        print(f"Endpoints to download: {len(endpoints)}")
        print(f"Output directory: {args.output}")
        print(f"\nThis may take a significant amount of time.")
        print("Press Ctrl+C to cancel at any time.\n")
        
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("Download cancelled.")
            return
    
    try:
        downloader = PokeAPIDownloader(
            output_dir=args.output,
            verbose=not args.quiet
        )
        downloader.download_endpoints(endpoints, max_workers=args.workers)
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        print("Partial data has been saved.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
