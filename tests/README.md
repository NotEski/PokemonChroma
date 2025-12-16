# Pokemon Fan Game - Test Suite

This directory contains a comprehensive test suite for the Pokemon Fan Game project.

## Test Structure

### Test Files

- **test_pokemon.py** - Tests for Pokemon models, stats, IVs/EVs, and battle states
- **test_battle.py** - Tests for battle system, turn management, and battle flow
- **test_damage_calculator.py** - Tests for damage calculation, critical hits, and modifiers
- **test_type_effectiveness.py** - Tests for type matchups and effectiveness chart
- **test_moves_teams.py** - Tests for moves, movesets, teams, and trainers
- **test_integration.py** - End-to-end integration tests for complete battle scenarios

### Configuration Files

- **conftest.py** - Pytest fixtures and shared test setup
- **__init__.py** - Package initialization

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_pokemon.py
pytest tests/test_battle.py
```

### Run Specific Test Class
```bash
pytest tests/test_pokemon.py::TestPokemon
pytest tests/test_battle.py::TestBattleFlow
```

### Run Specific Test
```bash
pytest tests/test_pokemon.py::TestPokemon::test_create_pokemon
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=shared --cov=engine --cov-report=html
```

### Run Only Failed Tests
```bash
pytest --lf
```

### Run Tests Matching Pattern
```bash
pytest -k "damage"  # Runs all tests with "damage" in the name
pytest -k "type_effectiveness"
```

## Test Coverage

The test suite covers:

### Core Pokemon Functionality (test_pokemon.py)
- Pokemon creation and initialization
- Stat calculations (HP, Attack, Defense, etc.)
- Individual Values (IVs) and Effort Values (EVs)
- Battle state management
- Status conditions and effects
- Shiny Pokemon, genders, and natures

### Battle System (test_battle.py)
- Battle initialization (wild and trainer battles)
- Turn management and turn order
- Action selection (moves, switches, escape)
- Action cancellation
- Battle state tracking
- Battle flow and completion

### Damage Calculation (test_damage_calculator.py)
- Base damage calculation
- Critical hit mechanics
- Level modifiers
- Type effectiveness in damage
- Weather effects
- Status condition effects (burn, etc.)
- STAB (Same Type Attack Bonus)
- Damage randomness and variation

### Type Effectiveness (test_type_effectiveness.py)
- All 18 Pokemon types
- Super effective matchups (2x damage)
- Not very effective matchups (0.5x damage)
- No effect matchups (0x damage)
- Type strengths and weaknesses
- Dual-type considerations

### Moves and Teams (test_moves_teams.py)
- Move creation and properties
- PP (Power Points) management
- Movesets (up to 4 moves)
- Stat changes from moves
- Team creation (1-6 Pokemon)
- Trainer management
- Move usage scenarios

### Integration Tests (test_integration.py)
- Complete wild battles
- Complete trainer battles
- Multi-turn battles
- PP depletion over time
- Pokemon fainting
- Type advantage scenarios
- Battle state management
- Edge cases (level 1, level 100)
- Realistic game scenarios

## Test Fixtures

Common fixtures available in `conftest.py`:

### Pokemon Bases
- `pikachu_base` - Pikachu PokemonBase
- `charizard_base` - Charizard PokemonBase
- `eevee_base` - Eevee PokemonBase

### Moves
- `tackle_move` - Normal-type physical move
- `thunderbolt_move` - Electric-type special move
- `flamethrower_move` - Fire-type special move
- `water_gun_move` - Water-type special move

### Pokemon Instances
- `pikachu_pokemon` - Level 15 Pikachu with moves
- `charizard_pokemon` - Level 50 Charizard with moves
- `eevee_pokemon` - Level 10 Eevee with moves

### Teams and Trainers
- `basic_team` - Team with a single Pikachu
- `ash_trainer` - Trainer named Ash with a team

## Writing New Tests

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test
```python
def test_pokemon_takes_damage(pikachu_pokemon):
    """Test that a Pokemon's HP decreases when taking damage."""
    initial_hp = pikachu_pokemon.current_hp
    damage = 10
    
    pikachu_pokemon.current_hp -= damage
    
    assert pikachu_pokemon.current_hp == initial_hp - damage
    assert pikachu_pokemon.current_hp >= 0
```

### Using Fixtures
```python
def test_with_fixture(pikachu_pokemon, eevee_pokemon):
    """Test using multiple fixtures."""
    assert pikachu_pokemon.level > 0
    assert eevee_pokemon.level > 0
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Add to your workflow:

```yaml
- name: Run tests
  run: pytest --cov=. --cov-report=xml
```

## Test Statistics

- **Total Test Files**: 7
- **Test Coverage Areas**: 6 major components
- **Estimated Test Count**: 150+ individual tests
- **Test Execution Time**: ~2-5 seconds (varies by machine)

## Requirements

Make sure you have the required packages installed:

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Troubleshooting

### Import Errors
If you encounter import errors, make sure you're running pytest from the project root:
```bash
cd c:\Users\Declan\source\repos\PokemonFanGame
pytest
```

### Fixture Not Found
Ensure `conftest.py` is in the tests directory and fixtures are properly defined.

### Random Test Failures
Some tests involve randomness (critical hits, damage variation). These are designed to be stable but may occasionally vary.

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all existing tests pass
3. Aim for >80% code coverage
4. Document new fixtures in conftest.py
5. Update this README if adding new test categories
