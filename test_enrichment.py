import json
from scores365 import get_game_details
details = get_game_details('4525753')
home_starters = details['home'].get('starters', [])
away_starters = details['away'].get('starters', [])
all_starters = home_starters + away_starters
for p in all_starters:
    print(f"Player: {p['name']} | Team: {p.get('team', '?')} | Stats: {p.get('avg_pts', 0)} PPG")
