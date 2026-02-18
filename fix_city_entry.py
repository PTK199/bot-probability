import json
from espn_api import fetch_from_espn_api

HISTORY_PATH = 'history.json'

def fix_city_entry():
    # 1. Fetch real data
    results = fetch_from_espn_api("2026-02-11")
    
    # 2. Key logic
    home_key = "Manchester City"
    away_key = "Fulham"
    
    # 3. Find correct score
    res = results.get(home_key) # None
    if not res: res = results.get(away_key) # Fulham obj
    
    if not res:
        print("❌ Could not find City game in API.")
        return

    # Fulham obj: score="0-3" (Home-Away). Home=Fulham. Away=City.
    s_parts = res['score'].split('-')
    val1 = int(s_parts[0]) # 0
    val2 = int(s_parts[1]) # 3
    
    # Logic to normalize to Entry Home (City)
    if res == results.get(home_key):
        city_score = val1
        fulham_score = val2
    else:
        city_score = val2 # 3
        fulham_score = val1 # 0
        
    print(f"✅ Verified Score: City {city_score} - {fulham_score} Fulham")
    
    final_score_string = f"{city_score}-{fulham_score}"
    
    # 4. Update History
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)
        
    updated = False
    for h in history:
        if h['home'] == "Manchester City" and h['date'] == "11/02":
            print(f"📝 Found Entry: {h['score']} ({h['status']})")
            h['score'] = final_score_string
            h['status'] = "WON" # Force correct status for "Man City Vence"
            h['profit'] = f"+{int((h['odd']-1)*100)}%"
            updated = True
            print(f"🚀 Updated to: {h['score']} ({h['status']})")
            
    if updated:
        with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print("💾 File saved.")
    else:
        print("⚠️ Entry not found in history.json to update.")

if __name__ == "__main__":
    fix_city_entry()
