import json
import os
import datetime
import requests

HISTORY_PATH = 'history.json'

ALIASES = {
    "manchester city": ["man city", "city"],
    "manchester united": ["man utd", "united", "red devils"],
    "aston villa": ["villa"],
    "nottingham forest": ["nottingham", "forest"],
    "tottenham": ["spurs"],
    "newcastle": ["magpies"],
    "wolves": ["wolverhampton"],
    "west ham": ["hammers"],
    "atlético-mg": ["galo", "atletico"],
    "vasco da gama": ["vasco"],
    "são paulo": ["tricolor"],
    "grêmio": ["gremio"],
    "brighton": ["brighton and hove"],
    "sunderland": ["black cats"],
    "liverpool": ["reds"],
    "fulham": ["cottagers"],
    "cavaliers": ["cavs"],
    "76ers": ["sixers"],
    "timberwolves": ["wolves"],
    "rockets": ["clippers"], # wait, just parts
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

def fetch_all_espn(date_str):
    leagues = ["basketball/nba", "soccer/bra.1", "soccer/eng.1", "soccer/esp.1", "soccer/ita.1", "soccer/ger.1", "soccer/fra.1"]
    results = {}
    base_url = "https://site.api.espn.com/apis/site/v2/sports/"
    for l in leagues:
        url = f"{base_url}{l}/scoreboard?dates={date_str}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            for ev in data.get('events', []):
                comp = ev.get('competitions', [{}])[0]
                status = ev.get('status', {}).get('type', {})
                desc = status.get('description', '')
                completed = status.get('completed', False)
                
                teams = comp.get('competitors', [])
                if len(teams) >= 2:
                    h = next(t for t in teams if t['homeAway'] == 'home')
                    a = next(t for t in teams if t['homeAway'] == 'away')
                    h_name = h['team']['displayName']
                    a_name = a['team']['displayName']
                    h_val = int(h.get('score', 0))
                    a_val = int(a.get('score', 0))
                    
                    obj = {
                        "score": f"{h_val}-{a_val}",
                        "h_val": h_val,
                        "a_val": a_val,
                        "completed": completed,
                        "desc": desc,
                        "home": h_name,
                        "away": a_name
                    }
                    results[h_name] = obj
                    results[a_name] = obj
        except: continue
    return results

def main():
    print("🚀 Iniciando Atualização Completa de Hoje...")
    target_date = "2026-02-11"
    espn_date = "20260211"
    
    real_data = fetch_all_espn(espn_date)
    
    if not os.path.exists(HISTORY_PATH):
        print("❌ history.json não encontrado.")
        return

    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)

    updates = 0
    for h in history:
        if h.get('date') != "11/02": continue
        
        home = h['home']
        away = h['away']
        
        res = real_data.get(home)
        if not res: res = real_data.get(away)
        
        # Fuzzy match for NBA team names (e.g. "76ers" vs "Philadelphia 76ers")
        if not res:
            for k, v in real_data.items():
                if is_team_in_string(home, k) or is_team_in_string(away, k):
                    res = v
                    break
        
        if res:
            h_val = res['h_val']
            a_val = res['a_val']
            
            # Normalize to Entry Home/Away
            # If the found result's "home" doesn't match our "home" (even if alias), we might need to swap
            # But fetch_all_espn says res['h_val'] is always the Score of the ESPN Home team.
            # We need to know if OUR home matches ESPN home.
            if is_team_in_string(home, res['home']):
                my_h_val, my_a_val = h_val, a_val
            else:
                my_h_val, my_a_val = a_val, h_val
                
            h['score'] = f"{my_h_val}-{my_a_val}"
            
            # Determine status
            sel = h['selection'].lower()
            odd = float(h.get('odd', 1.0))
            is_win = False
            is_loss = False
            is_void = False
            
            # 1. Over/Under
            if "over" in sel or "mais de" in sel:
                try:
                    # Extraction line (e.g. "Over (Mais de 220 pts)")
                    line = 220.0
                    if "pts" in sel or "gols" in sel or "(" in sel:
                         # try to find numbers
                         import re
                         nums = re.findall(r"\d+\.\d+|\d+", sel)
                         if nums: line = float(nums[0])
                    
                    if (my_h_val + my_a_val) > line: is_win = True
                    else: is_loss = True
                except: pass
            
            # 2. Winner
            elif "vence" in sel or "ml" in sel:
                target_home = is_team_in_string(home, sel)
                target_away = is_team_in_string(away, sel)
                if target_home:
                    if my_h_val > my_a_val: is_win = True
                    else: is_loss = True
                elif target_away:
                    if my_a_val > my_h_val: is_win = True
                    else: is_loss = True

            # 3. Double Chance
            elif "ou empate" in sel or "1x" in sel or "x2" in sel:
                if is_team_in_string(home, sel) or "1x" in sel:
                    if my_h_val >= my_a_val: is_win = True
                    else: is_loss = True
                elif is_team_in_string(away, sel) or "x2" in sel:
                    if my_a_val >= my_h_val: is_win = True
                    else: is_loss = True

            # Final check status vs completion
            if res['completed']:
                if is_win: h['status'] = "WON"
                elif is_loss: h['status'] = "LOST"
                elif is_void: h['status'] = "VOID"
                
                if h['status'] == "WON": h['profit'] = f"+{int((odd-1)*100)}%"
                elif h['status'] == "LOST": h['profit'] = "-100%"
            else:
                h['status'] = "PENDING"
                h['score'] = f"{my_h_val}-{my_a_val} (Live)"
                h['profit'] = "..."
                
            updates += 1
            print(f"✅ {home} vs {away}: {h['score']} ({h['status']})")

    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    
    print(f"\n🚀 Sincronização finalizada. {updates} jogos atualizados.")

if __name__ == "__main__":
    main()
