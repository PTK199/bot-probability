import data_fetcher

d = data_fetcher.get_games_for_date('2026-02-12', skip_history=True)
print(f"Games: {len(d.get('games', []))}")
print(f"Trebles: {len(d.get('trebles', []))}")
print("---")
for g in d.get('games', [])[:10]:
    tip = g['best_tip']
    print(f"  {g['league']} | {g['home_team']} vs {g['away_team']} | {tip['selection']} @{tip['odd']} ({tip['prob']}%)")
print("---")
for t in d.get('trebles', []):
    print(f"  {t['name']} | Odd: {t['total_odd']} | {t['probability']}")
