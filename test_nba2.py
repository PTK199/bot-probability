import json
from scores365 import get_games_today, _get

games = get_games_today('2026-02-25', sport_id=2)
for g in games:
    if g['status_group'] == 2 and g['has_lineups']:
        data = _get('game/', {'gameId': str(g['game_id'])})
        home = data['game'].get('homeCompetitor', {})
        members = home.get('lineups', {}).get('members', [])
        if members:
            m = members[0]
            print(f"Game {g['home']} vs {g['away']}")
            print("Keys in member:", list(m.keys()))
            if 'stats' in m:
                 print("Stats key present! First stat:", m['stats'][0])
            break
