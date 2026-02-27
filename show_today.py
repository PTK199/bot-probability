import json

with open('history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

picks = data if isinstance(data, list) else data.get('picks', data.get('history', []))

# Tenta os dois formatos de data para hoje
today_formats = ['26/02', '2026-02-26']
today_picks = [p for p in picks if p.get('date') in today_formats]

print(f"Picks de hoje (26/02): {len(today_picks)}")
print("-" * 90)
for p in today_picks:
    st   = str(p.get('status', 'PENDING'))
    home = p.get('home', '?')
    away = p.get('away', '?')
    sel  = p.get('selection', '?')
    odd  = p.get('odd', '?')
    prob = p.get('prob', '?')
    league = p.get('league', '?')
    badge  = p.get('badge', '')
    print(f"  [{st:7}] {home:28} vs {away:28} | {league:20} | {sel:35} @{odd} | {prob}% {badge}")
