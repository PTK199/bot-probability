import requests
import json
url = 'https://stats.nba.com/stats/leaguedashplayerstats'
headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nba.com/',
}
params = {
    'LastNGames': '0',
    'LeagueID': '00',
    'MeasureType': 'Base',
    'Month': '0',
    'OpponentTeamID': '0',
    'Outcome': '',
    'PaceAdjust': 'N',
    'PerMode': 'PerGame',
    'Period': '0',
    'PlayerExperience': '',
    'PlayerPosition': '',
    'PlusMinus': 'N',
    'Rank': 'N',
    'Season': '2024-25',
    'SeasonSegment': '',
    'SeasonType': 'Regular Season',
    'TwoWay': '0'
}
try:
    r = requests.get(url, headers=headers, params=params, timeout=12)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        row_set = data['resultSets'][0]['rowSet']
        headers_list = data['resultSets'][0]['headers']
        print(f"Retrieved {len(row_set)} players")
        # Find indices
        pts_idx = headers_list.index('PTS')
        reb_idx = headers_list.index('REB')
        ast_idx = headers_list.index('AST')
        name_idx = headers_list.index('PLAYER_NAME')
        
        p1 = row_set[0]
        print(f"Player 1: {p1[name_idx]} | PTS: {p1[pts_idx]} | REB: {p1[reb_idx]} | AST: {p1[ast_idx]}")
except Exception as e:
    print(f"Error: {e}")
