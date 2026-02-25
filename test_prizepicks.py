import requests
import json

url = "https://api.prizepicks.com/projections?league_id=7"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json'
}

try:
    print(f"Fetching {url}")
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        print("SUCCESS! Got data")
        
        # Save a sample to inspect the data structure
        with open('prizepicks_sample.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        projections = data.get("data", [])
        print(f"Found {len(projections)} projections in PrizePicks.")
        
    else:
        print(f"Failed. Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
