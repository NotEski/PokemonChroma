"""
Example usage of the download_assets module.
"""

from download_assets import PokemonAssetDownloader, download_pokemon_assets


def example_1_gen1_pokemon():
    """Example 1: Download all Gen 1 Pokemon (1-151)."""
    print("Example 1: Download Gen 1 Pokemon (1-151)")
    print("-" * 60)
    
    results = download_pokemon_assets(
        start_id=1,
        end_id=151,
        output_dir="assets",
        verbose=True
    )
    
    print(f"\nResults: {results}")


def example_2_specific_range():
    """Example 2: Download a specific range of Pokemon."""
    print("\nExample 2: Download Pokemon 25-30")
    print("-" * 60)
    
    downloader = PokemonAssetDownloader(
        output_dir="assets",
        verbose=True
    )
    
    results = downloader.download_range(start_id=25, end_id=30)
    print(f"\nResults: {results}")


def example_3_by_names():
    """Example 3: Download specific Pokemon by name."""
    print("\nExample 3: Download specific Pokemon by name")
    print("-" * 60)
    
    downloader = PokemonAssetDownloader(
        output_dir="assets",
        verbose=True
    )
    
    pokemon_names = ["bulbasaur", "pikachu", "charizard", "eevee"]
    results = downloader.download_by_names(pokemon_names)
    
    print(f"\nResults: {results}")


def example_4_quiet_mode():
    """Example 4: Download in quiet mode."""
    print("\nExample 4: Download in quiet mode")
    print("-" * 60)
    
    results = download_pokemon_assets(
        start_id=1,
        end_id=10,
        verbose=False
    )
    
    print(f"Quietly downloaded: {results}")


def example_5_single_pokemon():
    """Example 5: Download a single Pokemon."""
    print("\nExample 5: Download a single Pokemon")
    print("-" * 60)
    
    downloader = PokemonAssetDownloader(verbose=True)
    
    # Download just Bulbasaur
    from pathlib import Path
    bulbasaur_file = Path("pokeapi_database/pokemon/0001-bulbasaur.json")
    
    if bulbasaur_file.exists():
        results = downloader.download_pokemon_assets(bulbasaur_file)
        print(f"\nResults: {results}")
    else:
        print("Bulbasaur data file not found. Run download_pokeapi.py first.")


def example_6_custom_directories():
    """Example 6: Using custom directories."""
    print("\nExample 6: Custom source and output directories")
    print("-" * 60)
    
    downloader = PokemonAssetDownloader(
        pokeapi_dir="pokeapi_database/pokemon",
        output_dir="my_custom_assets",
        verbose=True
    )
    
    # Download just the first 5 Pokemon
    results = downloader.download_range(start_id=1, end_id=5)
    print(f"\nResults: {results}")


if __name__ == "__main__":
    # Uncomment the example you want to run:
    
    # example_1_gen1_pokemon()
    # example_2_specific_range()
    # example_3_by_names()
    # example_4_quiet_mode()
    example_5_single_pokemon()
    # example_6_custom_directories()
    
    print("\n✓ Example completed!")
