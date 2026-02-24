import datetime
import json
import os
import sys

# Add current dir to path to import local modules
sys.path.append(os.getcwd())

from data_fetcher import get_games_for_date
from espn_api import fetch_from_espn_api
from scores365 import fetch_results_365scores

HISTORY_PATH = 'history.json'

def resolve_status_logic(selection, h_score, a_score, odd):
    sel = selection.lower()
    is_win = False
    is_loss = False
    is_void = False
    
    # ML / Winner
    if "vence" in sel or "ml" in sel:
        if h_score > a_score: is_win = True
        elif h_score < a_score: is_loss = True
        else: is_loss = True
        
    # Double Chance
    elif "ou empate" in sel or "1x" in sel or "x2" in sel or "dupla chance" in sel:
        if h_score >= a_score: is_win = True
        else: is_loss = True
        
    # Over/Under
    import re
    if "over" in sel or "mais de" in sel:
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

def backfill_date(target_date):
    print(f"\n📅 --- Processando {target_date} ---")
    
    # 1. Get games/tips that would have been generated
    print("📡 Buscando tips retroativas...")
    try:
        data = get_games_for_date(target_date, force_refresh=True)
        games = data.get('games', [])
    except Exception as e:
        print(f"❌ Erro ao buscar games: {e}")
        return

    if not games:
        print("⚠️ Nenhum jogo encontrado para esta data.")
        return

    # 2. Fetch real results for the date
    print("📡 Buscando resultados oficiais (ESPN + 365)...")
    results_365 = fetch_results_365scores(target_date)
    results_espn = fetch_from_espn_api(target_date)
    all_results = results_365.copy()
    all_results.update(results_espn)

    # 3. Load history
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []

    date_short = datetime.datetime.strptime(target_date, "%Y-%m-%d").strftime("%d/%m")
    
    added = 0
    for g in games:
        home = g['home_team']
        away = g['away_team']
        tip = g.get('best_tip')
        if not tip: continue

        # Check if already in history
        if any(h.get('home') == home and h.get('date') == date_short for h in history):
            continue

        # Try to find result
        res = all_results.get(home)
        if not res:
            # Try fuzzy/alias
            for team_key, r in all_results.items():
                if home.lower() in team_key.lower() or team_key.lower() in home.lower():
                    res = r
                    break
        
        score = "---"
        status = "PENDING"
        profit = "0%"
        badge = tip.get('badge', '🎯 SNIPER')

        if res:
            score = res.get('score', '0-0')
            try:
                # Basic score parsing
                h_s, a_s = map(int, score.split('-'))
                status, profit = resolve_status_logic(tip['selection'], h_s, a_s, tip['odd'])
                badge = f"✅ GREEN" if status == "WON" else f"❌ RED" if status == "LOST" else badge
            except:
                pass

        new_entry = {
            "date": date_short,
            "time": g.get('time', '--:--'),
            "home": home,
            "away": away,
            "league": g.get('league', 'Unknown'),
            "selection": tip['selection'],
            "odd": tip['odd'],
            "prob": tip['prob'],
            "status": status,
            "score": score,
            "profit": profit,
            "badge": badge
        }
        history.insert(0, new_entry)
        added += 1

    # Save
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Adicionados {added} jogos para {target_date}")

if __name__ == "__main__":
    # Backfill last 3 days
    today = datetime.date.today()
    for i in range(3, 0, -1):
        d = today - datetime.timedelta(days=i)
        backfill_date(d.strftime("%Y-%m-%d"))
