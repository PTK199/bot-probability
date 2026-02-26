
import json
import os
import datetime
import sys
from git_autopush import autopush

# Fix encoding for Windows terminals
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Add current directory to path
sys.path.append(os.getcwd())

from data_fetcher import get_games_for_date

HISTORY_PATH = 'history.json'

def main():
    # 1. Get Today's Date
    today = datetime.date.today()
    target_date = today.strftime("%Y-%m-%d")
    print(f"🚀 Iniciando atualização forçada para HOJE: {target_date}")

    # 2. Fetch Games (will trigger Auto Engine if no hardcoded data)
    print("📡 Buscando jogos (pode levar alguns segundos)...")
    try:
        data = get_games_for_date(target_date)
    except Exception as e:
        print(f"❌ Erro ao buscar jogos: {e}")
        return

    # Handle different return types (List vs Dict)
    games = []
    if isinstance(data, dict):
        games = data.get('games', [])
    elif isinstance(data, list):
        games = data
    
    if not games:
        print("⚠️ Nenhum jogo encontrado para hoje.")
        return

    print(f"✅ Encontrados {len(games)} jogos. Atualizando histórico...")

    # 3. Load History
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    else:
        history = []

    # Map existing entries for today to avoid duplicates
    # Key: "HomeTeam" (assuming strict naming from API)
    existing_today = {}
    today_fmt = today.strftime("%d/%m")
    
    for idx, entry in enumerate(history):
        if entry.get('date') == today_fmt:
            existing_today[entry.get('home')] = idx

    count_new = 0
    count_update = 0

    # 4. Process Games
    for game in games:
        # Auto picks structure is nested
        # game = { 'home_team': ..., 'best_tip': {...}, ... }
        
        home = game.get('home_team') or game.get('home')
        away = game.get('away_team') or game.get('away')
        league = game.get('league')
        time = game.get('time')
        
        tip = game.get('best_tip', {})
        if not tip and 'selection' in game:
            # Handle hardcoded flat structure if any
            tip = game

        selection = tip.get('selection')
        if not selection:
            continue

        odd = tip.get('odd', 1.0)
        prob = tip.get('prob', 0)
        reason = tip.get('reason', '')
        badge = tip.get('badge', '')
        market = tip.get('market', '')

        entry = {
            "date": today_fmt,
            "time": time,
            "home": home,
            "away": away,
            "league": league,
            "selection": selection,
            "market": market,
            "odd": float(odd),
            "prob": prob,
            "status": "PENDING",
            "score": "0-0",
            "profit": "...",
            "badge": badge,
            "reason": reason
        }

        if home in existing_today:
            # Update existing? Maybe just skip to preserve manual edits?
            # Let's update just in case probabilities changed
            idx = existing_today[home]
            # Don't overwrite status if it's already resolved
            if history[idx].get('status') == 'PENDING':
                history[idx].update(entry)
                count_update += 1
        else:
            history.insert(0, entry) # Add to top
            count_new += 1

    # 5. Save
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

    print(f"💾 Sucesso! Adicionados: {count_new}, Atualizados: {count_update}")
    print(f"📄 Verifique {HISTORY_PATH} ou o dashboard.")
    autopush(f"auto: force_update_today [{datetime.date.today().strftime('%d/%m/%Y')}]")

if __name__ == "__main__":
    main()
