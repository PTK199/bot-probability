import json
from scores365 import get_games_today, _get

games = get_games_today('2026-02-25', sport_id=2)
for g in games:
    if 'Lakers' in g['home'] or 'Lakers' in g['away']:
        print(f"Found game: {g['home']} vs {g['away']}, ID: {g['game_id']}")
        data = _get('game/', {'gameId': str(g['game_id'])})
        if data and 'game' in data:
            home_comp = data['game'].get('homeCompetitor', {})
            lineups = home_comp.get('lineups', {})
            members = lineups.get('members', [])
            print(f"Members count in lineup: {len(members)}")
            if members:
                 print(json.dumps(members[0], indent=2))
        break
