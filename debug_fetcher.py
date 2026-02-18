from data_fetcher import get_games_for_date
import json

data = get_games_for_date("2026-02-11")
print(f"Keys: {data.keys()}")
print(f"Games count: {len(data.get('games', []))}")
if data.get('games'):
    print(f"Sample: {data['games'][0]['home']}")
