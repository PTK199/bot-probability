import requests
import json

url = "https://www.bovada.lv/services/sports/exchange/api/v1/events/path/basketball/nba"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print(f"Fetching {url}")
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        print("SUCCESS! Got data")
        
        events = data[0].get("events", []) if data else []
        print(f"Found {len(events)} events.")
        
        # Look for props
        if events:
            first = events[0]
            displayGroups = first.get("displayGroups", [])
            print(f"Display groups: {[g.get('description') for g in displayGroups]}")
            
        with open('bovada_sample.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    else:
        print(f"Failed. Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
