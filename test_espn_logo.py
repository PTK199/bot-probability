import requests

url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard'
resp = requests.get(url, timeout=10)
data = resp.json()
if data.get('events'):
    event = data['events'][0]
    competitors = event.get('competitions', [{}])[0].get('competitors', [])
    for c in competitors:
        team = c.get('team', {})
        print(f"Team: {team.get('displayName')} | Logo: {team.get('logo')}")
