import json
import os
import datetime
from data_fetcher import get_games_for_date
from espn_api import fetch_from_espn_api

HISTORY_PATH = 'history.json'

ALIASES = {
    "manchester city": ["man city", "city"],
    "manchester united": ["man utd", "united", "red devils"],
    "aston villa": ["villa"],
    "nottingham forest": ["nottingham"],
    "tottenham": ["spurs"],
    "newcastle": ["magpies"],
    "wolves": ["wolverhampton"],
    "west ham": ["hammers"],
    "atlético-mg": ["galo", "atletico"],
    "vasco": ["vasco da gama"],
    "botafogo": ["fogo"],
    "flamengo": ["mengo", "fla"],
    "corinthians": ["timao"],
    "palmeiras": ["verdao"],
    "são paulo": ["tricolor"],
    "santos": ["peixe"],
}

def is_team_in_string(team_name, text):
    t_lower = team_name.lower().strip()
    text_lower = text.lower().strip()
    
    if t_lower in text_lower:
        return True
    
    # Check aliases
    if t_lower in ALIASES:
        for alias in ALIASES[t_lower]:
            if alias in text_lower:
                return True
                
    # Check parts (risky but useful for "Villa" in "Aston Villa")
    # Only if name has multiple words
    parts = t_lower.split()
    if len(parts) > 1:
        # If any part of length > 3 is in text
        for p in parts:
            if len(p) > 3 and p in text_lower:
                return True
    
    return False

def main():
    print("🚀 Iniciando atualização inteligente do histórico (v2)...")
    
    target_date = "2026-02-11"
    
    print(f"📅 Obtendo dados para {target_date}...")
    try:
        daily_data = get_games_for_date(target_date)
        games_with_tips = daily_data.get('games', []) if isinstance(daily_data, dict) else daily_data
    except Exception as e:
        print(f"Error fetching games: {e}")
        return

    print(f"📡 Obtendo resultados da ESPN...")
    real_results = fetch_from_espn_api(target_date)
    
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []

    # Map existing entries by index for updating
    # Key: "DD/MM|HomeTeam"
    existing_map = {}
    for idx, entry in enumerate(history):
        d = entry.get('date')
        h = entry.get('home')
        existing_map[f"{d}|{h}"] = idx

    current_dd_mm = datetime.datetime.strptime(target_date, "%Y-%m-%d").strftime("%d/%m")
    
    updates_count = 0
    adds_count = 0
    
    for game in games_with_tips:
        home_team = game.get('home_team') or game.get('home')
        away_team = game.get('away_team') or game.get('away')
        
        tip = game.get('best_tip', {})
        selection = tip.get('selection', '') or game.get('selection', '')
        market = tip.get('market', '') or game.get('market', '')
        odd = float(tip.get('odd') or game.get('odd', 1.0))
        prob = tip.get('prob') or game.get('prob', 0)
        badge = tip.get('badge') or game.get('badge', '🤖 AI PICK')
        
        if not selection: continue

        key = f"{current_dd_mm}|{home_team}"
        
        # Check Result
        res = real_results.get(home_team)
        if not res: res = real_results.get(away_team)
        
        status = "PENDING"
        score_str = "0-0"
        profit = "0%"
        
        if res:
            try:
                score = res.get('score')
                s_parts = score.split('-')
                val1 = int(s_parts[0])
                val2 = int(s_parts[1])
                
                if res == real_results.get(home_team):
                    h_score = val1
                    a_score = val2
                else:
                    h_score = val2
                    a_score = val1
                
                score_str = f"{h_score}-{a_score}"
                sel_lower = selection.lower()
                
                is_win = False
                is_loss = False
                is_void = False
                
                # Logic
                if "vence" in sel_lower or "ml" in sel_lower:
                    if is_team_in_string(home_team, sel_lower) or "casa" in sel_lower:
                        if h_score > a_score: is_win = True
                        else: is_loss = True
                    elif is_team_in_string(away_team, sel_lower) or "fora" in sel_lower:
                        if a_score > h_score: is_win = True
                        else: is_loss = True
                
                elif "1x" in sel_lower or "dupla chance" in sel_lower or "ou empate" in sel_lower:
                    if is_team_in_string(home_team, sel_lower):
                        if h_score >= a_score: is_win = True
                        else: is_loss = True
                    elif is_team_in_string(away_team, sel_lower):
                        if a_score >= h_score: is_win = True
                        else: is_loss = True
                        
                elif "dnb" in sel_lower or "empate anula" in sel_lower:
                    if h_score == a_score:
                        is_void = True
                        status = "VOID"
                    elif is_team_in_string(home_team, sel_lower):
                        if h_score > a_score: is_win = True
                        else: is_loss = True
                    elif is_team_in_string(away_team, sel_lower):
                        if a_score > h_score: is_win = True
                        else: is_loss = True
                        
                elif "over" in sel_lower:
                     try:
                        line = float(sel_lower.split("over")[1].replace("gols","").replace("pontos","").strip().split()[0])
                        if (h_score + a_score) > line: is_win = True
                        else: is_loss = True
                     except: pass
                     
                elif "under" in sel_lower:
                     try:
                        line = float(sel_lower.split("under")[1].replace("gols","").replace("pontos","").strip().split()[0])
                        if (h_score + a_score) < line: is_win = True
                        else: is_loss = True
                     except: pass
                
                elif "btts" in sel_lower:
                     if h_score > 0 and a_score > 0: is_win = True
                     else: is_loss = True

                if is_win: status = "WON"
                elif is_loss: status = "LOST"
                
                if status == "WON":
                    profit = f"+{int((odd - 1) * 100)}%"
                elif status == "LOST":
                    profit = "-100%"
                elif status == "VOID":
                    profit = "VOID"
                    
            except Exception as e:
                print(f"Error logic {home_team}: {e}")
        
        # Entry Object
        new_entry = {
            "date": current_dd_mm,
            "time": game.get('time', "00:00"),
            "home": home_team,
            "away": away_team,
            "league": game.get('league', ''),
            "selection": selection,
            "odd": odd,
            "prob": prob,
            "status": status,
            "score": score_str,
            "profit": profit,
            "badge": badge
        }
        
        if key in existing_map:
            # Update existing
            idx = existing_map[key]
            history[idx] = new_entry
            updates_count += 1
            print(f"🔄 Atualizado: {home_team} -> {status} ({score_str})")
        else:
            # Add new
            history.insert(0, new_entry)
            adds_count += 1
            print(f"➕ Adicionado: {home_team} -> {status} ({score_str})")

    if updates_count > 0 or adds_count > 0:
        with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print(f"✅ Feito. Adds: {adds_count}, Updates: {updates_count}")
    else:
        print("ℹ️ Nenhuma mudanca.")

if __name__ == "__main__":
    main()
