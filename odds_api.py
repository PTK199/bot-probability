import os
import requests
import json
import datetime

# Retrieve API key from Windows Environment Variable or use placeholder
ODDS_API_KEY = os.environ.get("THE_ODDS_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.the-odds-api.com/v4/sports"
CACHE_DIR = "cache_odds"

def _ensure_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_nba_player_props(target_date=None, market="player_points"):
    """
    Fetches Player Props from The-Odds-API for NBA games.
    market can be: player_points, player_rebounds, player_assists
    """
    if not target_date:
         target_date = datetime.datetime.now().strftime("%Y-%m-%d")
         
    _ensure_dir()
    cache_file = os.path.join(CACHE_DIR, f"nba_{market}_{target_date}.json")
    if os.path.exists(cache_file):
         mtime = os.path.getmtime(cache_file)
         if (datetime.datetime.now().timestamp() - mtime) < 1800:
             try:
                 with open(cache_file, "r", encoding="utf-8") as f:
                     return json.load(f)
             except:
                 pass
                 
    if not ODDS_API_KEY or ODDS_API_KEY == "YOUR_API_KEY_HERE":
        print("[ODDS-API] ⚠️ No API Key found. Set THE_ODDS_API_KEY environment variable. Defaulting to internal Simulator lines.")
        return {}
        
    print(f"[ODDS-API] 📡 Fetching {market} for NBA from The-Odds-API...")
    
    url = f"{BASE_URL}/basketball_nba/events"
    
    try:
        events_resp = requests.get(url, params={"apiKey": ODDS_API_KEY}, timeout=10)
        events_resp.raise_for_status()
        events = events_resp.json()
    except Exception as e:
        print(f"[ODDS-API] ⚠️ Error fetching events: {e}")
        return {}
        
    results = {}
    
    # Needs to fetch odds for each event using v4 endpoint
    for event in events:
        event_id = event['id']
        home_team = event['home_team']
        away_team = event['away_team']
        
        odds_url = f"{BASE_URL}/basketball_nba/events/{event_id}/odds"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "us,eu",
            "markets": market,
            "oddsFormat": "decimal"
        }
        try:
            odds_resp = requests.get(odds_url, params=params, timeout=10)
            if odds_resp.status_code == 200:
                odds_data = odds_resp.json()
                
                # Extract player prop lines
                for bookmaker in odds_data.get("bookmakers", []):
                    bm_name = bookmaker.get("key", "")
                    for mkt in bookmaker.get("markets", []):
                        if mkt.get("key") == market:
                            for outcome in mkt.get("outcomes", []):
                                player_name = outcome.get("description", "")
                                bet_type = outcome.get("name", "") # "Over" or "Under"
                                point_line = outcome.get("point", 0.0)
                                odd_val = outcome.get("price", 1.0)
                                
                                if player_name not in results:
                                    results[player_name] = {}
                                
                                if "lines" not in results[player_name]:
                                    results[player_name]["lines"] = {}
                                    
                                if bm_name not in results[player_name]["lines"]:
                                      results[player_name]["lines"][bm_name] = {}
                                      
                                results[player_name]["lines"][bm_name][bet_type] = {
                                    "val": point_line,
                                    "odd": odd_val
                                }
        except Exception as e:
            continue
            
    # Save cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
            
    return results

if __name__ == "__main__":
    print("Testing Odds-API Wrapper (Requires Key)")
    data = get_nba_player_props()
    print(f"Found {len(data)} player prop markers.")
