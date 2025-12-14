"""
PokeAPI Database Downloader

This script downloads the entire PokeAPI database and organizes it into
a well-structured folder hierarchy with JSON files.
"""

import requests
import json
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

# Base API URL
BASE_URL = "https://pokeapi.co/api/v2"

# Output directory
OUTPUT_DIR = Path("pokeapi_database")

# API endpoints to download
ENDPOINTS = [
    "pokemon",
    "move",
    "ability",
    "type",
    "item",
    "berry",
    "berry-flavor",
    "berry-firmness",
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
    "region",
    "location",
    "location-area",
    "pal-park-area",
    "language",
    "nature",
    "pokeathlon-stat",
    "growth-rate",
    "egg-group",
    "gender",
    "stat",
    "move-ailment",
    "move-battle-style",
    "move-category",
    "move-damage-class",
    "move-learn-method",
    "move-target",
    "characteristic",
    "machine",
    "pal-park-area",
]


class PokeAPIDownloader:
    def __init__(self, base_url: str, output_dir: Path):
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "PokeAPI-Downloader/1.0"})
        
    def create_directory_structure(self):
        """Create the base directory structure."""
        self.output_dir.mkdir(exist_ok=True)
        print(f"Created output directory: {self.output_dir}")
        
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
            
            print(f"Found {len(all_results)} items for {endpoint}")
            return all_results
        except Exception as e:
            print(f"Error fetching resource list for {endpoint}: {e}")
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
            print(f"Error downloading {name} from {endpoint}: {e}")
            return False
    
    def download_endpoint(self, endpoint: str, max_workers: int = 10):
        """Download all resources for a specific endpoint."""
        print(f"\n{'='*60}")
        print(f"Downloading {endpoint}...")
        print(f"{'='*60}")
        
        # Get list of all resources
        resources = self.get_resource_list(endpoint)
        
        if not resources:
            print(f"No resources found for {endpoint}")
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
                    print(f"Exception for {name}: {e}")
                    fail_count += 1
                
                # Progress indicator
                if i % 50 == 0 or i == len(resources):
                    print(f"Progress: {i}/{len(resources)} ({success_count} success, {fail_count} failed)")
        
        print(f"\nCompleted {endpoint}: {success_count} successful, {fail_count} failed")
        
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
        
        print(f"Saved index file: {index_path}")
    
    def download_all(self, endpoints: List[str], max_workers: int = 10):
        """Download all data from specified endpoints."""
        start_time = time.time()
        
        print(f"Starting PokeAPI database download...")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Endpoints to download: {len(endpoints)}")
        
        self.create_directory_structure()
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"\n[{i}/{len(endpoints)}] Processing endpoint: {endpoint}")
            self.download_endpoint(endpoint, max_workers)
            time.sleep(0.5)  # Small delay between endpoints to be polite
        
        elapsed_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Download complete!")
        print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"Data saved to: {self.output_dir.absolute()}")
        print(f"{'='*60}")
        
        # Create a summary file
        self.create_summary()
    
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
        
        print(f"\nSummary saved to: {summary_path}")
        print(f"Total resources downloaded: {total_files}")


def main():
    """Main entry point."""
    print("PokeAPI Database Downloader")
    print("=" * 60)
    
    downloader = PokeAPIDownloader(BASE_URL, OUTPUT_DIR)
    
    # You can customize which endpoints to download here
    # For a full download, use all ENDPOINTS
    # For testing, you can use a subset: ["pokemon", "move", "ability"]
    
    print("\nThis will download the entire PokeAPI database.")
    print("This may take a significant amount of time (30-60 minutes).")
    print("Press Ctrl+C to cancel at any time.\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print("Download cancelled.")
        return
    
    try:
        # Download all endpoints
        downloader.download_all(ENDPOINTS, max_workers=10)
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        print("Partial data has been saved.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
