import requests
import json
url = 'https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byplayer?region=us&lang=en&contentorigin=espn&isQualified=false&limit=1000'
try:
    r = requests.get(url, timeout=15)
    if r.status_code == 200:
        data = r.json()
        headers = data.get('headers', [])
        print("Headers:", headers)
        categories = data.get('categories', [])
        if categories:
            stats_list = categories[0].get('statistics', [])
            print(f"Count: {len(stats_list)}")
            if stats_list:
                p = stats_list[0]
                print(f"Player: {p['athlete']['displayName']}")
                print(f"Stats: {p['stats']}")
except Exception as e:
    print(f"Error: {e}")
