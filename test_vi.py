import requests

url = "https://www.vegasinsider.com/nba/odds/player-props/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print(f"Fetching {url}")
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Success for VI. We can scrape it using BeautifulSoup.")
except Exception as e:
    print(f"Error: {e}")
