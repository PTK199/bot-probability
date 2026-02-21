import json
import datetime

def audit_history():
    try:
        with open('history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return

    # Normalized dates (assuming format DD/MM)
    # We need to guess the year or use current year
    current_year = 2026
    
    date_map = {}
    for entry in history:
        d_str = entry.get('date', '??/??')
        if '??' in d_str: continue
        
        try:
            day, month = d_str.split('/')
            full_date = f"{current_year}-{month}-{day}"
            dt = datetime.datetime.strptime(full_date, "%Y-%m-%d").date()
            
            if dt not in date_map:
                date_map[dt] = 0
            date_map[dt] += 1
        except:
            continue

    sorted_dates = sorted(date_map.keys())
    
    if not sorted_dates:
        print("No valid dates found in history.")
        return

    print(f"--- Audit Result ---")
    print(f"Total entries: {len(history)}")
    print(f"Unique days: {len(sorted_dates)}")
    print(f"Oldest: {sorted_dates[0]}")
    print(f"Newest: {sorted_dates[-1]}")
    
    # Check last 30 days coverage
    today = sorted_dates[-1]
    last_30 = [today - datetime.timedelta(days=i) for i in range(30)]
    
    missing = []
    for d in last_30:
        if d not in date_map:
            missing.append(d)
    
    print(f"Last 30 days coverage: {30 - len(missing)}/30 days")
    if missing:
        print(f"Missing days (last 30): {[d.strftime('%d/%m') for d in missing[:5]]}...")

if __name__ == "__main__":
    audit_history()
