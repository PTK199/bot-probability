import requests
import json
import datetime

def fetch_all():
    target_date = "20260211"
    leagues = [
        ("NBA", "basketball/nba"),
        ("BRA", "soccer/bra.1"),
        ("EPL", "soccer/eng.1"),
        ("ESP", "soccer/esp.1"),
        ("ITA", "soccer/ita.1"),
        ("GER", "soccer/ger.1"),
        ("FRA", "soccer/fra.1"),
        ("POR", "soccer/por.1"),
    ]
    
    print(f"--- SCORES FOR {target_date} ---")
    
    for name, path in leagues:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard?dates={target_date}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            events = data.get('events', [])
            print(f"\n[{name}] Found {len(events)} events.")
            for ev in events:
                comp = ev.get('competitions', [{}])[0]
                date_str = ev.get('date', '')
                status = ev.get('status', {}).get('type', {}).get('description', '')
                completed = ev.get('status', {}).get('type', {}).get('completed', False)
                
                teams = comp.get('competitors', [])
                if len(teams) >= 2:
                    h = next(t for t in teams if t['homeAway'] == 'home')
                    a = next(t for t in teams if t['homeAway'] == 'away')
                    h_name = h['team']['displayName']
                    a_name = a['team']['displayName']
                    h_score = h.get('score', '0')
                    a_score = a.get('score', '0')
                    print(f"  {a_name} {a_score} @ {h_name} {h_score} | Status: {status} ({'FINAL' if completed else 'LIVE'})")
        except Exception as e:
            print(f"  Error {name}: {e}")

if __name__ == "__main__":
    fetch_all()
