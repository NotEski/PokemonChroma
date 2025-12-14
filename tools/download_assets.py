"""
Pokemon Asset Downloader

This module downloads sprites (Generation V), animations, and cries for Pokemon
from the PokeAPI database. Downloads are organized by Pokemon, with proper
file naming and directory structure.

Can be used as a module or CLI tool:
    # As a module
    from tools.download_assets import PokemonAssetDownloader
    downloader = PokemonAssetDownloader()
    downloader.download_pokemon_assets(start_id=1, end_id=151)
    
    # As CLI
    python download_assets.py --range 1 151
"""

import requests
import json
import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Default directories
DEFAULT_POKEAPI_DIR = Path("pokeapi_database/pokemon")
DEFAULT_OUTPUT_DIR = Path("assets")

# Sprite types to download from Generation V Black/White
GEN5_SPRITE_TYPES = [
    "front_default", "back_default", "front_shiny", "back_shiny",
    "front_female", "back_female", "front_shiny_female", "back_shiny_female"
]


class PokemonAssetDownloader:
    """
    Downloads Pokemon sprites, animations, and cries from PokeAPI data.
    
    Args:
        pokeapi_dir: Directory containing downloaded PokeAPI pokemon JSON files
        output_dir: Directory to save downloaded assets
        verbose: Whether to print progress messages
    """
    
    def __init__(
        self,
        pokeapi_dir: Union[str, Path] = DEFAULT_POKEAPI_DIR,
        output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
        verbose: bool = True
    ):
        self.pokeapi_dir = Path(pokeapi_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Pokemon-Asset-Downloader/1.0"})
        
    def _print(self, message: str, **kwargs):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message, **kwargs)
    
    def _get_pokemon_data(self, pokemon_file: Path) -> Optional[Dict]:
        """Load Pokemon data from JSON file."""
        try:
            with open(pokemon_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self._print(f"Error loading {pokemon_file.name}: {e}")
            return None
    
    def _download_file(self, url: str, output_path: Path) -> bool:
        """Download a file from URL to output path."""
        try:
            # Skip if file already exists
            if output_path.exists():
                return True
            
            # Create parent directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"  Error downloading {url}: {e}")
            return False
    
    def _extract_sprite_urls(self, pokemon_data: Dict) -> Dict[str, str]:
        """
        Extract Generation V sprite URLs from Pokemon data.
        
        Returns:
            Dictionary mapping sprite names to URLs
        """
        sprites = {}
        sprite_data = pokemon_data.get("sprites", {})
        
        # Navigate to Generation V sprites
        versions = sprite_data.get("versions", {})
        gen5 = versions.get("generation-v", {})
        black_white = gen5.get("black-white", {})
        
        # # Extract static sprites from black-white
        # for sprite_type in GEN5_SPRITE_TYPES:
        #     url = black_white.get(sprite_type)
        #     if url:
        #         sprite_name = f"{sprite_type}"
        #         sprites[sprite_name] = url
        
        # Extract animated sprites from black-white/animated
        animated = black_white.get("animated", {})
        for sprite_type in GEN5_SPRITE_TYPES:
            url = animated.get(sprite_type)
            if url:
                sprite_name = f"animated_{sprite_type}"
                sprites[sprite_name] = url
        
        return sprites
    
    def _extract_cry_urls(self, pokemon_data: Dict) -> Dict[str, str]:
        """
        Extract cry URLs from Pokemon data.
        
        Returns:
            Dictionary mapping cry names to URLs
        """
        cries = {}
        cry_data = pokemon_data.get("cries", {})
        
        for cry_type, url in cry_data.items():
            if url:
                cries[cry_type] = url
        
        return cries
    
    def _get_pokemon_identifier(self, pokemon_data: Dict) -> Tuple[int, str]:
        """
        Get Pokemon ID and name from data.
        
        Returns:
            Tuple of (id, name)
        """
        pokemon_id = pokemon_data.get("id", 0)
        pokemon_name = pokemon_data.get("name", "unknown")
        return pokemon_id, pokemon_name
    
    def download_pokemon_assets(
        self,
        pokemon_file: Path,
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Download all assets for a single Pokemon.
        
        Args:
            pokemon_file: Path to the Pokemon JSON file
            skip_existing: Whether to skip if assets already exist
            
        Returns:
            Dictionary with download statistics
        """
        stats = {
            "sprites_downloaded": 0,
            "sprites_failed": 0,
            "cries_downloaded": 0,
            "cries_failed": 0,
        }
        
        # Load Pokemon data
        pokemon_data = self._get_pokemon_data(pokemon_file)
        if not pokemon_data:
            return stats
        
        pokemon_id, pokemon_name = self._get_pokemon_identifier(pokemon_data)
        
        # Create Pokemon-specific directory
        pokemon_dir = self.output_dir / f"{pokemon_id:04d}-{pokemon_name.capitalize()}"
        
        self._print(f"Processing: {pokemon_id:04d} - {pokemon_name.capitalize()}")
        
        # Extract URLs
        sprite_urls = self._extract_sprite_urls(pokemon_data)
        cry_urls = self._extract_cry_urls(pokemon_data)
        
        # Download sprites
        for sprite_name, url in sprite_urls.items():
            # Determine file extension from URL
            ext = Path(url).suffix or ".png"
            output_path = pokemon_dir / f"{sprite_name}{ext}"
            
            if self._download_file(url, output_path):
                stats["sprites_downloaded"] += 1
            else:
                stats["sprites_failed"] += 1
        
        # Download cries
        for cry_name, url in cry_urls.items():
            # Determine file extension from URL
            ext = Path(url).suffix or ".ogg"
            output_path = pokemon_dir / f"cry_{cry_name}{ext}"
            
            if self._download_file(url, output_path):
                stats["cries_downloaded"] += 1
            else:
                stats["cries_failed"] += 1
        
        self._print(
            f"  Sprites: {stats['sprites_downloaded']} downloaded, "
            f"{stats['sprites_failed']} failed | "
            f"Cries: {stats['cries_downloaded']} downloaded, "
            f"{stats['cries_failed']} failed"
        )
        
        return stats
    
    def download_range(
        self,
        start_id: int = 1,
        end_id: Optional[int] = None,
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Download assets for a range of Pokemon.
        
        Args:
            start_id: Starting Pokemon ID (inclusive)
            end_id: Ending Pokemon ID (inclusive). If None, processes all available.
            skip_existing: Whether to skip Pokemon with existing asset directories
            
        Returns:
            Dictionary with overall download statistics
        """
        start_time = time.time()
        
        self._print(f"Pokemon Asset Downloader")
        self._print(f"{'='*60}")
        self._print(f"Source directory: {self.pokeapi_dir.absolute()}")
        self._print(f"Output directory: {self.output_dir.absolute()}")
        self._print(f"Pokemon range: {start_id} to {end_id or 'end'}")
        self._print(f"{'='*60}\n")
        
        # Get all Pokemon files
        pokemon_files = sorted(self.pokeapi_dir.glob("*.json"))
        pokemon_files = [f for f in pokemon_files if not f.name.startswith("_")]
        
        if not pokemon_files:
            self._print(f"No Pokemon files found in {self.pokeapi_dir}")
            return {
                "pokemon_processed": 0,
                "sprites_downloaded": 0,
                "sprites_failed": 0,
                "cries_downloaded": 0,
                "cries_failed": 0,
            }
        
        # Filter by ID range
        filtered_files = []
        for pfile in pokemon_files:
            # Extract ID from filename (e.g., "0001-bulbasaur.json")
            try:
                file_id = int(pfile.stem.split("-")[0])
                if file_id >= start_id and (end_id is None or file_id <= end_id):
                    filtered_files.append(pfile)
            except (ValueError, IndexError):
                continue
        
        if not filtered_files:
            self._print(f"No Pokemon files found in range {start_id}-{end_id}")
            return {
                "pokemon_processed": 0,
                "sprites_downloaded": 0,
                "sprites_failed": 0,
                "cries_downloaded": 0,
                "cries_failed": 0,
            }
        
        self._print(f"Found {len(filtered_files)} Pokemon to process\n")
        
        # Overall statistics
        total_stats = {
            "pokemon_processed": 0,
            "sprites_downloaded": 0,
            "sprites_failed": 0,
            "cries_downloaded": 0,
            "cries_failed": 0,
        }
        
        # Process each Pokemon sequentially
        for i, pokemon_file in enumerate(filtered_files, 1):
            self._print(f"[{i}/{len(filtered_files)}] ", end="")
            
            stats = self.download_pokemon_assets(pokemon_file, skip_existing)
            
            # Update totals
            total_stats["pokemon_processed"] += 1
            for key in ["sprites_downloaded", "sprites_failed", "cries_downloaded", "cries_failed"]:
                total_stats[key] += stats[key]
            
            # Small delay to be polite to the server
            time.sleep(0.1)
        
        # Summary
        elapsed_time = time.time() - start_time
        self._print(f"\n{'='*60}")
        self._print(f"Download Complete!")
        self._print(f"{'='*60}")
        self._print(f"Pokemon processed: {total_stats['pokemon_processed']}")
        self._print(f"Sprites downloaded: {total_stats['sprites_downloaded']}")
        self._print(f"Sprites failed: {total_stats['sprites_failed']}")
        self._print(f"Cries downloaded: {total_stats['cries_downloaded']}")
        self._print(f"Cries failed: {total_stats['cries_failed']}")
        self._print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        self._print(f"Output directory: {self.output_dir.absolute()}")
        self._print(f"{'='*60}")
        
        return total_stats
    
    def download_by_names(
        self,
        pokemon_names: List[str],
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Download assets for specific Pokemon by name.
        
        Args:
            pokemon_names: List of Pokemon names (e.g., ["bulbasaur", "pikachu"])
            skip_existing: Whether to skip Pokemon with existing asset directories
            
        Returns:
            Dictionary with overall download statistics
        """
        total_stats = {
            "pokemon_processed": 0,
            "sprites_downloaded": 0,
            "sprites_failed": 0,
            "cries_downloaded": 0,
            "cries_failed": 0,
        }
        
        self._print(f"Downloading assets for {len(pokemon_names)} specific Pokemon\n")
        
        for i, name in enumerate(pokemon_names, 1):
            # Find the Pokemon file
            pokemon_files = list(self.pokeapi_dir.glob(f"*-{name.lower()}.json"))
            
            if not pokemon_files:
                self._print(f"[{i}/{len(pokemon_names)}] Pokemon '{name}' not found")
                continue
            
            self._print(f"[{i}/{len(pokemon_names)}] ", end="")
            stats = self.download_pokemon_assets(pokemon_files[0], skip_existing)
            
            # Update totals
            total_stats["pokemon_processed"] += 1
            for key in ["sprites_downloaded", "sprites_failed", "cries_downloaded", "cries_failed"]:
                total_stats[key] += stats[key]
            
            time.sleep(0.1)
        
        self._print(f"\nCompleted: {total_stats['pokemon_processed']} Pokemon processed")
        return total_stats


def ensure_pokemon_data(pokeapi_dir: Union[str, Path] = DEFAULT_POKEAPI_DIR, verbose: bool = True) -> bool:
    """
    Check if Pokemon data exists, and download it if missing.
    
    Args:
        pokeapi_dir: Directory where Pokemon JSON files should be
        verbose: Whether to print progress messages
        
    Returns:
        True if data is available, False if download failed
    """
    pokeapi_dir = Path(pokeapi_dir)
    
    # Check if directory exists and has Pokemon files
    if pokeapi_dir.exists():
        pokemon_files = list(pokeapi_dir.glob("*.json"))
        pokemon_files = [f for f in pokemon_files if not f.name.startswith("_")]
        
        if len(pokemon_files) > 0:
            if verbose:
                print(f"✓ Found {len(pokemon_files)} Pokemon data files")
            return True
    
    # Data is missing, try to download it
    if verbose:
        print(f"Pokemon data not found in {pokeapi_dir}")
        print("Attempting to download Pokemon data from PokeAPI...")
        print()
    
    try:
        # Try to import and use the download_pokeapi module
        try:
            from download_pokeapi import PokeAPIDownloader
        except ImportError:
            # If running from a different directory, try adding tools to path
            tools_dir = Path(__file__).parent
            sys.path.insert(0, str(tools_dir))
            from download_pokeapi import PokeAPIDownloader
        
        # Download Pokemon data
        downloader = PokeAPIDownloader(
            output_dir=pokeapi_dir.parent,  # Use parent directory (pokeapi_database)
            verbose=verbose
        )
        
        if verbose:
            print("Downloading Pokemon endpoint data...")
        
        results = downloader.download_endpoints(["pokemon"], max_workers=10)
        
        if results.get("pokemon", 0) > 0:
            if verbose:
                print(f"\n✓ Successfully downloaded {results['pokemon']} Pokemon data files")
            return True
        else:
            if verbose:
                print("\n✗ Failed to download Pokemon data")
            return False
            
    except Exception as e:
        if verbose:
            print(f"\n✗ Error downloading Pokemon data: {e}")
            print("Please run manually: python download_pokeapi.py --endpoints pokemon")
        return False


def download_pokemon_assets(
    start_id: int = 1,
    end_id: Optional[int] = None,
    output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
    pokeapi_dir: Union[str, Path] = DEFAULT_POKEAPI_DIR,
    verbose: bool = True
) -> Dict[str, int]:
    """
    Convenience function to download Pokemon assets.
    
    Args:
        start_id: Starting Pokemon ID (inclusive)
        end_id: Ending Pokemon ID (inclusive). If None, processes all.
        output_dir: Directory to save assets
        pokeapi_dir: Directory containing Pokemon JSON files
        verbose: Whether to print progress
        
    Returns:
        Dictionary with download statistics
        
    Example:
        # Download Gen 1 Pokemon (1-151)
        download_pokemon_assets(start_id=1, end_id=151)
        
        # Download all available Pokemon
        download_pokemon_assets()
    """
    # Ensure Pokemon data exists first
    if not ensure_pokemon_data(pokeapi_dir, verbose):
        if verbose:
            print("Cannot proceed without Pokemon data.")
        return {
            "pokemon_processed": 0,
            "sprites_downloaded": 0,
            "sprites_failed": 0,
            "cries_downloaded": 0,
            "cries_failed": 0,
        }
    
    downloader = PokemonAssetDownloader(
        pokeapi_dir=pokeapi_dir,
        output_dir=output_dir,
        verbose=verbose
    )
    return downloader.download_range(start_id, end_id)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Download Pokemon sprites (Gen V) and cries from PokeAPI data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download Gen 1 Pokemon (1-151)
  python download_assets.py --range 1 151
  
  # Download specific Pokemon by name
  python download_assets.py --names bulbasaur pikachu charizard
  
  # Download all available Pokemon
  python download_assets.py --all
  
  # Custom directories
  python download_assets.py --range 1 151 --output my_assets --source my_pokeapi
  
  # Quiet mode
  python download_assets.py --range 1 151 --quiet
        """
    )
    
    parser.add_argument(
        "--range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Download Pokemon in ID range (e.g., 1 151 for Gen 1)"
    )
    
    parser.add_argument(
        "--names",
        nargs="+",
        metavar="NAME",
        help="Download specific Pokemon by name"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all available Pokemon"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for assets (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        default=str(DEFAULT_POKEAPI_DIR),
        help=f"Source directory with Pokemon JSON files (default: {DEFAULT_POKEAPI_DIR})"
    )
    
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Check if source directory exists and has Pokemon data
    # If not, automatically download it
    if not ensure_pokemon_data(args.source, verbose=not args.quiet):
        print("Error: Unable to obtain Pokemon data.")
        print("Please run manually: python download_pokeapi.py --endpoints pokemon")
        return
    
    # Create downloader
    downloader = PokemonAssetDownloader(
        pokeapi_dir=args.source,
        output_dir=args.output,
        verbose=not args.quiet
    )
    
    try:
        if args.names:
            # Download by names
            downloader.download_by_names(args.names)
        elif args.range:
            # Download by range
            start_id, end_id = args.range
            downloader.download_range(start_id, end_id)
        elif args.all:
            # Download all
            downloader.download_range(start_id=1, end_id=None)
        else:
            # Default: prompt user
            print("Pokemon Asset Downloader")
            print("=" * 60)
            print("\nNo options specified. Choose an option:")
            print("  1. Download Gen 1 Pokemon (1-151)")
            print("  2. Download Gen 1-5 Pokemon (1-649)")
            print("  3. Download all available Pokemon")
            print("  4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                downloader.download_range(1, 151)
            elif choice == "2":
                downloader.download_range(1, 649)
            elif choice == "3":
                downloader.download_range(1, None)
            else:
                print("Exiting.")
                return
                
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        print("Partial data has been saved.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
