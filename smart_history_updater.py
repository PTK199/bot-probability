import json
import os
import datetime
import requests
import re
from espn_api import fetch_from_espn_api
# Note: scores365 is optional as it's not always in all environments, but we'll try to use it if available
try:
    from scores365 import fetch_results_365scores
except ImportError:
    fetch_results_365scores = None

HISTORY_PATH = 'history.json'

ALIASES = {
    "manchester city": ["man city", "city"],
    "manchester united": ["man utd", "united", "red devils"],
    "aston villa": ["villa"],
    "nottingham forest": ["nottingham", "forest"],
    "tottenham": ["spurs"],
    "newcastle": ["magpies", "newcastle united"],
    "wolves": ["wolverhampton"],
    "west ham": ["hammers", "west ham united"],
    "atlético-mg": ["galo", "atletico"],
    "vasco da gama": ["vasco"],
    "são paulo": ["tricolor"],
    "grêmio": ["gremio"],
    "brighton": ["brighton and hove", "brighton & hove albion"],
    "sunderland": ["black cats"],
    "liverpool": ["reds"],
    "fulham": ["cottagers"],
    "cavaliers": ["cavs"],
    "76ers": ["sixers"],
    "timberwolves": ["wolves"],
    "thunder": ["okc"],
    "mavericks": ["mavs"],
    "pelicans": ["pels"],
}

def is_team_in_string(team_name, text):
    t_lower = team_name.lower().strip()
    text_lower = text.lower().strip()
    if t_lower in text_lower: return True
    if t_lower in ALIASES:
        for alias in ALIASES[t_lower]:
            if alias in text_lower: return True
    parts = t_lower.split()
    if len(parts) > 1:
        for p in parts:
            if len(p) > 3 and p in text_lower: return True
    return False

def get_normalized_score(res, target_home):
    """Normalize score parts based on home/away match."""
    try:
        score = res.get('score', '0-0')
        parts = re.findall(r'\d+', score)
        if len(parts) < 2: return 0, 0
        
        val1, val2 = int(parts[0]), int(parts[1])
        
        # In results from ESPN/365, usually 'home' matches res['home']
        if 'home' in res and is_team_in_string(target_home, res['home']):
            return val1, val2
        elif 'away' in res and is_team_in_string(target_home, res['away']):
            return val2, val1
        else:
            # Fallback based on team names if res object is from espn_api custom format
            # Fetching from espn_api usually returns a dict where key is home_team or away_team
            return val1, val2 # Default to what's there
    except:
        return 0, 0

def resolve_status(selection, h_score, a_score, odd):
    sel = selection.lower()
    is_win = False
    is_loss = False
    is_void = False
    
    # ML / Winner
    if "vence" in sel or "ml" in sel:
        # We need to know who was picked. 
        # Selection usually looks like "Team Vence"
        # Since we don't have the picked team explicitly, we check team name in selection
        # (This logic is slightly limited without the full game object here, but we pass h_score as the target home's score)
        if h_score > a_score: is_win = True
        elif h_score < a_score: is_loss = True
        else: is_loss = True # Draw = Loss in ML
        
    # Double Chance
    elif "ou empate" in sel or "1x" in sel or "x2" in sel or "dupla chance" in sel:
        if h_score >= a_score: is_win = True
        else: is_loss = True
        
    # Over/Under
    elif "over" in sel or "mais de" in sel:
        nums = re.findall(r"\d+\.\d+|\d+", sel)
        if nums:
            line = float(nums[0])
            if (h_score + a_score) > line: is_win = True
            else: is_loss = True
    elif "under" in sel or "menos de" in sel:
        nums = re.findall(r"\d+\.\d+|\d+", sel)
        if nums:
            line = float(nums[0])
            if (h_score + a_score) < line: is_win = True
            else: is_loss = True
            
    # BTTS
    elif "btts" in sel or "ambas marcam" in sel:
        if h_score > 0 and a_score > 0: is_win = True
        else: is_loss = True
        
    # DNB
    elif "dnb" in sel or "empate anula" in sel:
        if h_score > a_score: is_win = True
        elif h_score == a_score: is_void = True
        else: is_loss = True

    if is_win: return "WON", f"+{int((odd-1)*100)}%"
    if is_loss: return "LOST", "-100%"
    if is_void: return "VOID", "0%"
    return "PENDING", "0%"

def main():
    if not os.path.exists(HISTORY_PATH):
        print("❌ history.json no found.")
        return

    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)

    pending_entries = [h for h in history if h.get('status') == 'PENDING']
    if not pending_entries:
        print("✅ No pending entries found.")
        return

    print(f"🔍 Found {len(pending_entries)} pending entries.")
    
    # Group by date to minimize API calls
    dates_to_fetch = set()
    for entry in pending_entries:
        d_str = entry.get('date') # "20/02"
        try:
            # Assume 2026 for now as per current date in system
            d_obj = datetime.datetime.strptime(f"{d_str}/2026", "%d/%m/%Y")
            dates_to_fetch.add(d_obj.strftime("%Y%m%d"))
        except: continue

    all_results = {}
    for date_key in dates_to_fetch:
        print(f"📡 Fetching results for {date_key}...")
        # Get from ESPN
        espn_res = fetch_from_espn_api(date_key)
        all_results[date_key] = espn_res
        
        # Get from 365 if available
        if fetch_results_365scores:
            try:
                # Convert back to YYYY-MM-DD
                d_api = datetime.datetime.strptime(date_key, "%Y%m%d").strftime("%Y-%m-%d")
                res365 = fetch_results_365scores(d_api)
                all_results[date_key].update(res365)
            except: pass

    updates = 0
    for h in history:
        if h.get('status') != 'PENDING': continue
        
        d_str = h.get('date')
        try:
            date_key = datetime.datetime.strptime(f"{d_str}/2026", "%d/%m/%Y").strftime("%Y%m%d")
        except: continue
        
        day_results = all_results.get(date_key, {})
        home = h['home']
        away = h['away']
        
        res = day_results.get(home)
        if not res: res = day_results.get(away)
        
        # Fuzzy match
        if not res:
            for team_name, data in day_results.items():
                if is_team_in_string(home, team_name) or is_team_in_string(away, team_name):
                    res = data
                    break
        
        if res:
            h_score, a_score = get_normalized_score(res, home)
            
            # Additional check: if it was away team picked in ML
            # Selection might be "Bucks Vence" whereas home is "Pelicans"
            # Our resolve_status expects h_score to be the picked side if picking team
            # Let's adjust logic:
            
            # Determine if target home is in selection
            target_is_home = is_team_in_string(home, h['selection'])
            target_is_away = is_team_in_string(away, h['selection'])
            
            # If we picked away team, we should swap scores for resolve_status
            if target_is_away and not target_is_home:
                status, profit = resolve_status(h['selection'], a_score, h_score, h.get('odd', 1.0))
            else:
                status, profit = resolve_status(h['selection'], h_score, a_score, h.get('odd', 1.0))
            
            if status != "PENDING":
                h['score'] = f"{h_score}-{a_score}"
                h['status'] = status
                h['profit'] = profit
                
                # Update badge if WON/LOST and doesn't have GREEN/RED
                if status == "WON" and "GREEN" not in h.get('badge', ''):
                    h['badge'] = "✅ GREEN"
                elif status == "LOST" and "RED" not in h.get('badge', ''):
                    h['badge'] = "❌ RED"
                
                updates += 1
                print(f"✅ Updated: {home} vs {away} -> {status} ({h['score']})")

    if updates > 0:
        with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print(f"🚀 Saved {updates} updates to history.json")
    else:
        print("ℹ️ No updates applied.")

if __name__ == "__main__":
    main()
