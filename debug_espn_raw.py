import json
from espn_api import fetch_from_espn_api
import datetime

def debug_espn():
    target_date = "2026-02-11"
    print(f"🔍 Inspecting ESPN API data for {target_date}...\n")
    
    results = fetch_from_espn_api(target_date)
    
    if not results:
        print("❌ No results returned from ESPN API.")
        return

    print(f"✅ Comparison Data Found: {len(results)} teams/entries.\n")
    
    # List of key teams we are looking for today
    key_teams = [
        "Nottingham Forest", "Wolves", "Aston Villa", "Brighton", 
        "Manchester City", "Fulham", "Sunderland", "Liverpool",
        "Atlético-MG", "Remo", "Vasco", "Bahia", "São Paulo", "Grêmio"
    ]
    
    for team in key_teams:
        # Fuzzy search/Direct access
        data = results.get(team)
        if data:
            print(f"🎯 {team}: {json.dumps(data, ensure_ascii=False)}")
        else:
            # Try finding by substring
            found = False
            for k, v in results.items():
                if team in k:
                    print(f"🎯 {team} (found as {k}): {json.dumps(v, ensure_ascii=False)}")
                    found = True
                    break
            if not found:
                print(f"⚠️ {team}: Not found in API response.")

if __name__ == "__main__":
    debug_espn()
