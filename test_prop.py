import json
import traceback
import sys

from auto_picks import generate_nba_tip, monte_carlo_nba

home = 'Lakers'
away = 'Magic'
sim = monte_carlo_nba(75, 75)
game = {
    'home': home, 'away': away,
    '_team_intel': {
         'home': {'starters': [{'name': 'LeBron James', 'avg_pts': 25.5, 'position': 'Forward'}], 'missing': []},
         'away': {'starters': [], 'missing': []}
    }
}

print("Running Simulator...")
tip = generate_nba_tip(game, sim)
if tip:
    print("\nFINAL TIP:", json.dumps(tip[0] if tip else None, indent=2))
else:
    print("NO TIP GENERATED")
