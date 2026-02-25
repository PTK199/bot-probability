import requests
import json

url = "https://sportsbook-us-nj.draftkings.com/sites/US-NJ-SB/api/v5/eventgroups/42648"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

try:
    print(f"Fetching DraftKings NBA...")
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        print("SUCCESS! Got data")
        
        # Save a sample
        with open('dk_sample.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        print(f"Keys: {data.keys()}")
    else:
        print(f"Failed. Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
