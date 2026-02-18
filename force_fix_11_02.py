
import json
import os
import datetime
import sys

# Fix encoding for Windows terminals
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Add current directory to path
sys.path.append(os.getcwd())

from data_fetcher import get_games_for_date
from espn_api import fetch_from_espn_api

HISTORY_PATH = 'history.json'

def is_team_in_string(team_name, text):
    t_lower = team_name.lower().strip()
    text_lower = text.lower().strip()
    
    if t_lower in text_lower:
        return True
    
    parts = t_lower.split()
    if len(parts) > 1:
        for p in parts:
            if len(p) > 3 and p in text_lower:
                return True
    
    return False

def main():
    print("🚀 Iniciando Auditoria de Resultados (Forced)...")
    
    target_date = "2026-02-11"
    
    print(f"📅 Baixando dados oficiais da ESPN para {target_date}...")
    real_results = fetch_from_espn_api(target_date)
    
    # Load Picks source - WE MUST RELOAD HISTORY AS SOURCE since data_fetcher might not have the 11/02 hardcoded anymore safely
    # Actually, let's load history.json directly to see what is pending for 11/02
    
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        print("History not found")
        return

    changes = 0
    
    print("\n📝 PROCESSANDO JOGOS PENDENTES DE 11/02:\n")
    
    for entry in history:
        if entry.get('date') != "11/02":
            continue

        home = entry.get('home')
        away = entry.get('away')
        selection = entry.get('selection')
        status = entry.get('status', 'PENDING')
        
        # Skip if already won/lost to save time, OR force update if requested
        # Let's force update
        
        # Find result
        res = None
        if home in real_results: res = real_results[home]
        elif away in real_results: res = real_results[away]
        
        if not res:
            # Fuzzy
            for k, v in real_results.items():
                if is_team_in_string(home, k) or is_team_in_string(away, k):
                    res = v
                    break
        
        if res:
            try:
                # Determine Score
                # ESPN result has home_val (score of ESPN Home Team)
                # We need to match ESPN Home with Our Home
                
                h_val = int(res.get('home_val', 0))
                a_val = int(res.get('away_val', 0))
                
                # Check if swap needed
                # If our 'home' is not in ESPN 'home' name, maybe we swaped?
                # Usually ESPN API defines Home/Away clearly.
                
                # Let's assume standard
                score_str = f"{h_val}-{a_val}"
                
                # Verdict
                is_win = False
                is_loss = False
                sel_lower = selection.lower()
                
                if "vence" in sel_lower or "ml" in sel_lower:
                     if is_team_in_string(home, sel_lower) or "casa" in sel_lower:
                         if h_val > a_val: is_win = True
                         else: is_loss = True
                     elif is_team_in_string(away, sel_lower) or "fora" in sel_lower:
                         if a_val > h_val: is_win = True
                         else: is_loss = True
                         
                elif "over" in sel_lower:
                     try:
                        line = float(sel_lower.split("over")[1].replace("gols","").replace("pts","").replace("pontos","").strip().replace("(","").replace(")","").split()[0])
                        if (h_val + a_val) > line: is_win = True
                        else: is_loss = True
                     except: pass

                elif "under" in sel_lower:
                     try:
                        line = float(sel_lower.split("under")[1].replace("gols","").replace("pts","").replace("pontos","").strip().replace("(","").replace(")","").split()[0])
                        if (h_val + a_val) < line: is_win = True
                        else: is_loss = True
                     except: pass
                     
                new_status = "PENDING"
                if is_win: new_status = "WON"
                elif is_loss: new_status = "LOST"
                
                if res.get('completed') is None:
                    # Debug fallback: check if 'score' ends in (Final)
                    pass
                
                # ESPN API structure check: 'completed' might be a boolean top level or not there if we built it manually
                # In espn_api.py, fetch_from_espn_api returns dict of dicts.
                # But looking at espn_api.py source:
                # results[home_name] = { ..., "home_val": ..., "away_val": ... } 
                # IT DOES NOT INCLUDE "completed" key in the result object!
                # Wait, looking at lines 130-144 in espn_api.py:
                # It only adds to results IF is_completed is True.
                # So if it is in results, it IS completed.
                
                is_completed_game = True # By definition of fetch_from_espn_api logic (lines 130)
                
                if is_completed_game:
                    entry['status'] = new_status
                    entry['score'] = score_str
                    
                    odd = float(entry.get('odd', 1.0))
                    if new_status == "WON":
                        entry['profit'] = f"+{int((odd-1)*100)}%"
                    elif new_status == "LOST":
                        entry['profit'] = "-100%"
                        
                    changes += 1
                    print(f"✅ {home}: {score_str} -> {new_status}")
                else:
                    entry['score'] = f"{score_str} (Live)"
                    print(f"⏳ {home}: {score_str} (Em andamento)")
                    
            except Exception as e:
                print(f"❌ Erro em {home}: {e}")

    if changes > 0:
        with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print(f"\n💾 Atualizados {changes} jogos no histórico.")
    else:
        print("\nℹ️ Nenhuma atualização encontrada.")

if __name__ == "__main__":
    main()
