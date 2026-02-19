"""Test the FORTRESS treble engine"""
from auto_picks import get_auto_games
import json, datetime

target = datetime.datetime.now().strftime('%Y-%m-%d')
print(f'Generating picks for {target}...')
result = get_auto_games(target)

games = result.get('games', [])
trebles = result.get('trebles', [])

print(f'\n{"="*60}')
print(f'  FORTRESS ENGINE RESULTS')
print(f'{"="*60}')
print(f'Total games: {len(games)}')
print(f'Total trebles: {len(trebles)}')

print(f'\n=== TOP 8 PICKS (by prob) ===')
sorted_games = sorted(games, key=lambda x: x['best_tip']['prob'], reverse=True)
for g in sorted_games[:8]:
    tip = g['best_tip']
    print(f'  {g["home_team"]} vs {g["away_team"]} [{g["league"]}]')
    print(f'    -> {tip["selection"]} | Prob: {tip["prob"]}% | Odd: {tip["odd"]} | {tip["badge"]}')

print(f'\n=== TREBLES (FORTRESS ENGINE v3.0) ===')
for t in trebles:
    print(f'\n  {t["name"]}')
    print(f'  Odd: {t["total_odd"]} | Prob: {t["probability"]}')
    for s in t['selections']:
        league = s.get("league", "")
        prob = s.get("prob", "")
        print(f'    - {s["pick"]} [{league}] (prob:{prob}%)')
