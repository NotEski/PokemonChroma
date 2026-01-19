from setuptools import setup, find_packages

# Panda3D build_apps configuration
# Build command (from venv):
#   python -m pip install panda3d --use-pep517
#   python setup.py build_apps
# Output goes to ./build/
# Adjust plugins/include_patterns as needed for your project assets.

setup(
    name="PokemonChroma",
    version="0.1.0",
    description="Pokemon fan game built with Panda3D",
    packages=find_packages(exclude=["tests", "tests.*"]),
    options={
        "build_apps": {
            # Entry points: GUI app for Windows
            "gui_apps": {
                "PokemonChroma": "main.py",
            },
            # Include all assets/data needed at runtime
            "include_patterns": [
                "assets/**",
                "data/**",
                "README.md",
                "LICENSE*",
            ],
            # Panda3D plugins commonly needed (adjust if unused)
            "plugins": [
                "pandagl",          # OpenGL renderer
                "p3openal_audio",   # Audio
                "p3assimp",         # Model import (if used)
            ],
            # Platforms to build (add more if cross-building)
            "platforms": ["win_amd64"],
            # Extra modules to force-include if the analyzer misses them
            "include_modules": [
                "engine",
                "shared",
            ],
            # Use a predictable build output folder
            "build_base": "build",
            # Enable optimization; set to False if you need .py source
            # "optimize": True,
        }
    },
)
