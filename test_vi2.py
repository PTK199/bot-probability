import requests
from bs4 import BeautifulSoup
import json

url = "https://www.vegasinsider.com/nba/odds/player-props/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Fetching {url}")
r = requests.get(url, headers=headers, timeout=10)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    # Look for script tags with JSON data
    data_found = False
    for script in soup.find_all('script'):
        if script.string and 'window.__INITIAL_STATE__' in script.string:
            print("Found __INITIAL_STATE__!")
            data_found = True
            break
        if script.string and 'props' in script.string.lower():
            # might have nextjs data
            pass
    
    # Check if there is next.js data
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("Found __NEXT_DATA__!")
        data = json.loads(next_data.string)
        with open('vi_next.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Saved nextjs data.")

