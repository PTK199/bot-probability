import json
import os

HISTORY_PATH = 'history.json'

def main():
    if not os.path.exists(HISTORY_PATH):
        print("❌ Arquivo history.json não encontrado.")
        return

    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)

    print("\n📅 JOGOS DE HOJE (11/02):\n")
    print(f"{'HORA':<8} | {'CONFRONTO':<35} | {'SELEÇÃO':<25} | {'STATUS':<10} | {'PLACAR'}")
    print("-" * 100)

    count = 0
    for h in history:
        if h.get('date') == "11/02":
            match = f"{h['home']} vs {h['away']}"
            sel = h.get('selection', '---')
            status = h.get('status', 'PENDING')
            score = h.get('score', '0-0')
            time = h.get('time', '00:00')
            
            # Color code (visual only for terminal)
            status_icon = "⏳"
            if status == "WON": status_icon = "✅ GREEN"
            elif status == "LOST": status_icon = "❌ RED"
            elif status == "VOID": status_icon = "⚪ VOID"
            
            print(f"{time:<8} | {match:<35} | {sel:<25} | {status_icon:<10} | {score}")
            count += 1
            
    print("-" * 100)
    print(f"\nTotal: {count} jogos encontrados.")

if __name__ == "__main__":
    main()
