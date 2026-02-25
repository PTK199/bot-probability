import requests
import json

url = "https://api.actionnetwork.com/web/v1/scoreboard/nba?period=game"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

print(f"Fetching {url}")
r = requests.get(url, headers=headers, timeout=10)
if r.status_code == 200:
    data = r.json()
    with open('action_sample.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("SUCCESS! Saved action_sample.json")
else:
    print(f"Failed. Status: {r.status_code}")
