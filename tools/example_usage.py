"""
Example usage of the download_pokeapi module.
"""

from download_pokeapi import PokeAPIDownloader, download_pokemon_data, AVAILABLE_ENDPOINTS


def example_1_basic_usage():
    """Example 1: Basic usage with convenience function."""
    print("Example 1: Download pokemon and moves using convenience function")
    print("-" * 60)
    
    # Simple download of specific endpoints
    results = download_pokemon_data(
        output_dir="my_pokemon_data",
        endpoints=["pokemon", "move"],
        verbose=True
    )
    
    print(f"\nDownload results: {results}")


def example_2_custom_downloader():
    """Example 2: Using the downloader class directly."""
    print("\nExample 2: Using PokeAPIDownloader class")
    print("-" * 60)
    
    # Create a downloader instance
    downloader = PokeAPIDownloader(
        output_dir="pokeapi_database",
        verbose=True
    )
    
    # Download specific endpoints
    results = downloader.download_endpoints(
        endpoints=["type", "ability"],
        max_workers=5
    )
    
    print(f"\nDownload results: {results}")


def example_3_list_endpoints():
    """Example 3: List available endpoints."""
    print("\nExample 3: List available endpoints")
    print("-" * 60)
    
    endpoints = PokeAPIDownloader.list_available_endpoints()
    print(f"Available endpoints ({len(endpoints)}):")
    for endpoint in endpoints:
        print(f"  - {endpoint}")


def example_4_download_all():
    """Example 4: Download all endpoints (commented out by default)."""
    print("\nExample 4: Download all endpoints")
    print("-" * 60)
    print("This would download all available endpoints.")
    print("Uncomment the code below to actually run it.")
    
    # Uncomment to actually download everything:
    # downloader = PokeAPIDownloader()
    # results = downloader.download_all(max_workers=10)
    # print(f"\nDownload results: {results}")


def example_5_quiet_mode():
    """Example 5: Download in quiet mode (no output)."""
    print("\nExample 5: Download in quiet mode")
    print("-" * 60)
    
    # Download without progress output
    results = download_pokemon_data(
        output_dir="silent_download",
        endpoints=["nature"],  # Small endpoint for quick testing
        verbose=False
    )
    
    print(f"Download completed: {results}")


if __name__ == "__main__":
    # Uncomment the examples you want to run:
    
    # example_1_basic_usage()
    # example_2_custom_downloader()
    example_3_list_endpoints()
    # example_4_download_all()
    # example_5_quiet_mode()
