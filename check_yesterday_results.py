import requests
import json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Check UCL results from yesterday (Feb 17)
leagues = {
    "soccer/uefa.champions": "Champions League",
    "soccer/conmebol.libertadores": "Libertadores",
    "soccer/conmebol.sudamericana": "Sudamericana",
    "soccer/eng.1": "Premier League",
    "soccer/esp.1": "La Liga",
    "soccer/ita.1": "Serie A",
    "soccer/ger.1": "Bundesliga",
    "soccer/fra.1": "Ligue 1",
    "soccer/bra.1": "Brasileirao",
    "basketball/nba": "NBA",
}

base_url = "http://site.api.espn.com/apis/site/v2/sports/"

# Check dates around yesterday
for check_date in ["20260217", "20260218"]:
    print(f"\n{'='*60}")
    print(f"  DATE: {check_date}")
    print(f"{'='*60}")
    
    for league_path, league_name in leagues.items():
        url = f"{base_url}{league_path}/scoreboard?date={check_date}"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            data = r.json()
            events = data.get("events", [])
            
            completed_events = []
            scheduled_events = []
            
            for event in events:
                status_type = event["status"]["type"]
                completed = status_type["completed"]
                desc = status_type.get("description", "")
                
                comps = event.get("competitions", [])
                if not comps:
                    continue
                comp = comps[0]
                competitors = comp.get("competitors", [])
                home = next((t for t in competitors if t["homeAway"] == "home"), None)
                away = next((t for t in competitors if t["homeAway"] == "away"), None)
                if not home or not away:
                    continue
                    
                h_name = home["team"]["displayName"]
                a_name = away["team"]["displayName"]
                h_score = int(home.get("score", 0))
                a_score = int(away.get("score", 0))
                total = h_score + a_score
                
                game_date = event.get("date", "")[:10]
                
                info = {
                    "home": h_name,
                    "away": a_name,
                    "h_score": h_score,
                    "a_score": a_score,
                    "total": total,
                    "completed": completed,
                    "status": desc,
                    "date": game_date
                }
                
                if completed:
                    completed_events.append(info)
                else:
                    scheduled_events.append(info)
            
            if completed_events:
                print(f"\n  --- {league_name} (COMPLETED) ---")
                for g in completed_events:
                    print(f"    {g['home']} vs {g['away']}: {g['h_score']}-{g['a_score']} (Total: {g['total']}) [{g['date']}]")
                    
            if scheduled_events:
                print(f"\n  --- {league_name} (SCHEDULED/LIVE) ---")
                for g in scheduled_events:
                    print(f"    {g['home']} vs {g['away']}: {g['status']} [{g['date']}]")
                    
        except Exception as e:
            print(f"  Error fetching {league_name}: {e}")
