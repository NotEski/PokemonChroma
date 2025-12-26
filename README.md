Pokemon Fan Game (Ash's Journey)
=================================

## Overview
Episodic Pokémon fangame built from scratch with `pyglet`. Follow Ash's anime route season by season and movie by movie, unlocking new regions as episodes release. Battles aim to mirror modern mainline mechanics while staying true to the show.

## Current Focus
- Core overworld traversal for the first Kanto arc.
- Turn-based battle engine modeled on contemporary games.
- Data-driven Pokémon, moves, and type charts for easy iteration.

## Roadmap (Episodic Releases)
1. Season 1 (Kanto): Pallet Town through the Indigo Plateau.
2. Movies between Seasons 1–2: Add event encounters and side areas.
3. Season 2 (Orange Islands): New maps, roster updates, and mechanics tweaks.
4. Later seasons/movies: Continue expanding regions, encounters, and story beats.

## Requirements
- Python 3.12+ (tested)
- Dependencies from `requirements.txt` (installs pyglet and supporting libs).

## Setup
1. Create and activate a virtual environment.
2. Install deps: `pip install -r requirements.txt`.
3. Run the game: `python main.py`.

## Repo Structure (key parts)
- `main.py` – entry point to launch the game.
- `engine/` – rendering and battle systems (pyglet windowing, battle logic, type effectiveness, damage/catch calculators).
- `shared/pokemon/` – data models for Pokémon, moves, trainers, teams, and types.
- `assets/` – sprite and media assets organized by Pokédex number.
- `tools/` – helpers (e.g., type chart and data download scripts).

## Contributing / Notes
- This is a fan project; please use original assets responsibly and respect Nintendo/The Pokémon Company IP guidelines.
- Issue ideas: balance tuning, AI improvements, map design, and episodic content scripting.





Notes for when I get back to this

Implimented the new battleposition system
implimented the new InPlayPokemon system

however they need to be linked together or ione needs to be superseeded as they now have conflicting information/inplaypokemon isnt being updated when it should be

then make sure the actions are working and thaqt there is only one action system, link that to the logging system or just keep them seperate
