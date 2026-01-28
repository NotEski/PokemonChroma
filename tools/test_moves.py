from pathlib import Path
import json

p = Path('pokeapi_database/move')
print(f'Directory exists: {p.exists()}')
print(f'Total JSON files: {len(list(p.glob("*.json")))}')

# Test with trick-room
tr = p / 'trick-room.json'
if tr.exists():
    data = json.load(open(tr))
    print(f'\nTrick Room effect: {data["effect_entries"][0]["short_effect"]}')
else:
    print('Trick room not found')
    
# List first 10 moves
print('\nFirst 10 moves:')
for f in sorted(p.glob('*.json'))[:10]:
    print(f'  {f.name}')
