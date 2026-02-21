import json
import datetime
import os

HISTORY_PATH = 'history.json'

def archive_old_history():
    print("--- 30-Day History Archiver ---")
    
    if not os.path.exists(HISTORY_PATH):
        print("No history file found.")
        return

    try:
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return

    original_count = len(history)
    today = datetime.datetime.now()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    # Assuming "DD/MM" format. We'll use current year to convert to datetime
    current_year = 2026
    
    kept = []
    removed = 0
    
    for entry in history:
        d_str = entry.get('date', '??/??')
        try:
            day, month = d_str.split('/')
            dt = datetime.datetime(current_year, int(month), int(day))
            
            if dt >= thirty_days_ago:
                kept.append(entry)
            else:
                removed += 1
        except:
            # Keep if we can't parse date (better safe than sorry)
            kept.append(entry)
            
    if removed > 0:
        with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(kept, f, indent=4, ensure_ascii=False)
        print(f"Cleanup complete: Removed {removed} entries older than 30 days.")
        print(f"Total current entries: {len(kept)}")
    else:
        print("No entries older than 30 days found.")

if __name__ == "__main__":
    archive_old_history()
