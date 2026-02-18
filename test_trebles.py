import auto_picks
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

d = auto_picks.get_auto_games("2026-02-12")
print(f"Jogos: {len(d['games'])}")
print(f"Trebles: {len(d['trebles'])}")
for t in d["trebles"]:
    print(f"  {t['name']} | Odd: {t['total_odd']} | Prob: {t['probability']}")
    for s in t["selections"]:
        print(f"    -> {s['match']}: {s['pick']}")
