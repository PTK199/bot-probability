import auto_picks
from self_learning import get_active_thresholds

date = '2026-02-21'
print(f"--- Testing Sniper Logic for {date} ---")
thresholds = get_active_thresholds()
print(f"Active Thresholds: {thresholds}")

data = auto_picks.get_auto_games(date)
games = data.get('games', [])
print(f"Total games: {len(games)}")

snipers = [g for g in games if g.get('best_tip', {}).get('prob', 0) >= thresholds.get('sniper', 72)]
print(f"Snipers (>= {thresholds.get('sniper')}%): {len(snipers)}")

print("\n--- Top 5 Sniper Picks ---")
for g in snipers[:5]:
    tip = g['best_tip']
    print(f"[{tip.get('badge')}] {g['league']} | {g['home_team']} vs {g['away_team']} | {tip['selection']} ({tip['prob']}%)")
    if 'reason' in tip:
        # Show only the learning part of history if present
        if "AUTOCONHECIMENTO" in tip['reason']:
            learn_part = [p for p in tip['reason'].split('|') if "AUTOCONHECIMENTO" in p]
            print(f"   Insight: {learn_part[0].strip()}")
