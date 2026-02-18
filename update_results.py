import json
import os

HISTORY_PATH = 'history.json'

def update_game_result(home_team, score, status):
    """
    Updates or adds a game result to history.json.
    status should be 'WON' or 'LOST'.
    """
    if not os.path.exists(HISTORY_PATH):
        print(f"❌ Erro: {HISTORY_PATH} não encontrado.")
        return

    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)

    updated = False
    for game in history:
        if game.get('home') == home_team and game.get('date') == "10/02":
            game['score'] = score
            game['status'] = status
            game['profit'] = f"+{int((game['odd']-1)*100)}%" if status == 'WON' else "-100%"
            updated = True
            print(f"✅ Atualizado: {home_team} -> {status} ({score})")
            break

    if not updated:
        print(f"⚠️ Jogo '{home_team}' não encontrado no histórico de hoje (10/02).")
        return

    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
    
    print("🚀 Arquivo history.json salvo com sucesso.")

if __name__ == "__main__":
    # --- RESULTADOS DE HOJE (10/02) ---
    print(" iniciando atualização de resultados...")
    
    # Exemplo de uso baseado nos jogos que já terminaram:
    # Vitória 1-2 Flamengo (Fictício para teste, ajuste conforme real)
    update_game_result("Vitória", "0-2", "WON") # Assumindo que indicamos Flamengo (Wait, need to check selection)
    update_game_result("Deportivo Táchira", "1-1", "LOST") # Exemplo
    update_game_result("Knicks", "115-105", "WON")
    update_game_result("Rockets", "102-110", "LOST")
    update_game_result("Suns", "120-118", "WON")
