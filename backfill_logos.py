import json
import os
import sys

# Add current path to import auto_picks get_logo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from auto_picks import get_logo
except ImportError:
    def get_logo(team_name, sport):
        safe = team_name.replace(" ", "+")
        return f"https://ui-avatars.com/api/?name={safe}&size=64&background=1a1a2e&color=a855f7&bold=true"

HISTORY_FILE = "history.json"

if not os.path.exists(HISTORY_FILE):
    print("No history.json found.")
    sys.exit(0)

with open(HISTORY_FILE, "r", encoding="utf-8") as f:
    history = json.load(f)

updated = 0
for entry in history:
    home = entry.get("home", "")
    away = entry.get("away", "")
    sport = "football" if entry.get("league") != "NBA" else "basketball"
    
    if "home_logo" not in entry or not entry["home_logo"]:
        entry["home_logo"] = get_logo(home, sport)
        updated += 1
    if "away_logo" not in entry or not entry["away_logo"]:
        entry["away_logo"] = get_logo(away, sport)
        updated += 1

if updated > 0:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    print(f"Backfilled {updated} logos in {HISTORY_FILE}.")
else:
    print("No missing logos found to backfill.")
