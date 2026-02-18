import json
import os

HISTORY_PATH = 'history.json'

def fix_manual():
    if not os.path.exists(HISTORY_PATH):
        print("File not found")
        return

    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        history = json.load(f)

    updated = False
    for h in history:
        if h.get('date') == "11/02":
            # Fix Villa
            if "Aston Villa" in h.get('home', '') and "Villa Vence" in h.get('selection', ''):
                print(f"Fixing Villa: {h['status']} -> WON")
                h['status'] = "WON"
                h['profit'] = f"+{int((h['odd']-1)*100)}%"
                updated = True
            
            # Fix Palace
            if "Crystal Palace" in h.get('home', '') and "Palace Vence" in h.get('selection', ''):
                print(f"Fixing Palace: {h['status']} -> LOST")
                h['status'] = "LOST"
                h['profit'] = "-100%"
                updated = True

            # Fix City
            if "Manchester City" in h.get('home', '') and "Man City Vence" in h.get('selection', ''):
                print(f"Fixing City: {h['status']} -> WON")
                h['status'] = "WON"
                h['profit'] = f"+{int((h['odd']-1)*100)}%"
                updated = True

    if updated:
        with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print("History updated successfully.")
    else:
        print("No matches found to fix.")

if __name__ == "__main__":
    fix_manual()
