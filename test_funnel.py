"""Quick test of the full funnel pipeline."""
import auto_picks

r = auto_picks.get_auto_games("2026-02-18")
print(f"\n{'='*60}")
print(f"GAMES: {len(r['games'])}")
print(f"TREBLES: {len(r['trebles'])}")
print(f"{'='*60}\n")

for g in r["games"][:10]:
    tip = g["best_tip"]
    print(f"  {g['home_team']:25s} vs {g['away_team']:25s}")
    print(f"    → {tip['selection']} ({tip['prob']}%) [{tip['badge']}] @{tip['odd']}")
    print(f"    Reason: {tip['reason'][:120]}...")
    print()
