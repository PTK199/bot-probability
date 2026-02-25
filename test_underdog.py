import requests

url = "https://api.underdogfantasy.com/beta/v3/over_under_lines"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

try:
    print(f"Fetching {url}")
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
