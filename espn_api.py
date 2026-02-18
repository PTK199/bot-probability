"""
🔌 ESPN API & RESULTS MODULE
Extracted from data_fetcher.py for modularity.
Contains: ESPN API fetching, ResultScoutBot, real-time odds API.
"""

import os
import datetime
import requests
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

THE_ODDS_API_KEY = os.environ.get("THE_ODDS_API_KEY", "")


def fetch_real_odds_from_api(sport_key):
    """
    Internal helper to fetch data from The Odds API.
    """
    if not THE_ODDS_API_KEY:
        return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {"apiKey": THE_ODDS_API_KEY, "regions": "eu", "markets": "h2h,totals", "oddsFormat": "decimal"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []


def fetch_real_scores_from_api(sport_key):
    """
    Fetches completed event scores from The Odds API.
    """
    if not THE_ODDS_API_KEY:
        return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/scores/"
    params = {"apiKey": THE_ODDS_API_KEY, "daysFrom": 1}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []


def fetch_from_espn_api(target_date=None):
    """
    Fetches real-time scores from ESPN's public hidden API (JSON).
    Supports date-specific queries (?date=YYYYMMDD).
    """
    print("[API-BOT] Conectando aos satélites de resultados (ESPN API)...")
    
    results = {}
    
    if target_date is None:
        target_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    date_param = target_date.replace("-", "")
    
    # ESPN API endpoints for live NBA and Football
    leagues = {
        "nba": f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_param}",
        "eng.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates={date_param}",
        "esp.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard?dates={date_param}",
        "ita.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard?dates={date_param}",
        "ger.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/ger.1/scoreboard?dates={date_param}",
        "fra.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/fra.1/scoreboard?dates={date_param}",
        "bra.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard?dates={date_param}",
        "por.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/por.1/scoreboard?dates={date_param}",
        "ned.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/ned.1/scoreboard?dates={date_param}",
        "tur.1": f"https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/scoreboard?dates={date_param}",
    }
    
    # Manual overrides for ESPN team names -> our names
    team_name_overrides = {
        "Boston Celtics": "Celtics", "New York Knicks": "Knicks", "Cleveland Cavaliers": "Cavaliers",
        "Oklahoma City Thunder": "Thunder", "Houston Rockets": "Rockets", "Golden State Warriors": "Warriors",
        "Denver Nuggets": "Nuggets", "LA Clippers": "Clippers", "Los Angeles Clippers": "Clippers",
        "Milwaukee Bucks": "Bucks", "Miami Heat": "Heat", "Phoenix Suns": "Suns",
        "Dallas Mavericks": "Mavericks", "Minnesota Timberwolves": "Timberwolves", "Sacramento Kings": "Kings",
        "Memphis Grizzlies": "Grizzlies", "Los Angeles Lakers": "Lakers", "Atlanta Hawks": "Hawks",
        "Charlotte Hornets": "Hornets", "San Antonio Spurs": "Spurs", "Chicago Bulls": "Bulls",
        "New Orleans Pelicans": "Pelicans", "Utah Jazz": "Jazz", "Portland Trail Blazers": "Blazers",
        "Brooklyn Nets": "Nets", "Indiana Pacers": "Pacers", "Washington Wizards": "Wizards",
        "Orlando Magic": "Magic", "Philadelphia 76ers": "Sixers", "Detroit Pistons": "Pistons",
        "Toronto Raptors": "Raptors",
        # Football overrides
        "Tottenham Hotspur": "Tottenham", "Manchester United": "Man United",
        "Manchester City": "Man City", "Wolverhampton Wanderers": "Wolves",
        "Nottingham Forest": "Nott. Forest", "Brighton and Hove Albion": "Brighton",
        "Paris Saint-Germain": "PSG",
    }
    
    for league_key, url in leagues.items():
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            
            for event in data.get('events', []):
                competitors = event.get('competitions', [{}])[0].get('competitors', [])
                if len(competitors) < 2:
                    continue
                
                home_comp = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                away_comp = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
                
                home_name_raw = home_comp.get('team', {}).get('displayName', 'Unknown')
                away_name_raw = away_comp.get('team', {}).get('displayName', 'Unknown')
                
                home_name = team_name_overrides.get(home_name_raw, home_name_raw)
                away_name = team_name_overrides.get(away_name_raw, away_name_raw)
                
                home_score = home_comp.get('score', '0')
                away_score = away_comp.get('score', '0')
                
                status_type = event.get('status', {}).get('type', {})
                is_completed = status_type.get('completed', False)
                
                if is_completed:
                    results[home_name] = {
                        "score": f"{home_score}-{away_score}",
                        "home_val": home_score,
                        "away_val": away_score,
                        "away": away_name,
                        "league": league_key.upper().replace(".", " ")
                    }
                    results[away_name] = {
                        "score": f"{away_score}-{home_score}",
                        "home_val": away_score,
                        "away_val": home_score,
                        "away": home_name,
                        "league": league_key.upper().replace(".", " ")
                    }
        except Exception as e:
            continue
    
    return results


class ResultScoutBot:
    """
    NEURAL RESULT SCOUT BOT 🤖
    Fetches real outcomes using ESPN Public API.
    """
    def __init__(self):
        pass
    
    def scout_results_for_date(self, target_date):
        return fetch_from_espn_api(target_date)
    
    def scout_today_results(self):
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        return fetch_from_espn_api(today_str)


def fetch_standings_from_espn(sport="soccer", league="eng.1"):
    """
    Fetches real-time standings from ESPN's public API.
    Returns a dictionary with team stats {team_name: {pos, gp, w, d, l, gf, ga, diff, pts}}
    """
    if sport == "basketball":
        url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
    else:
        # Default to the requested league or generic mapping
        league_map = {
            "premier-league": "eng.1", "england": "eng.1", "eng.1": "eng.1",
            "la-liga": "esp.1", "spain": "esp.1", "esp.1": "esp.1",
            "serie-a": "ita.1", "italy": "ita.1", "ita.1": "ita.1",
            "bundesliga": "ger.1", "germany": "ger.1", "ger.1": "ger.1",
            "ligue-1": "fra.1", "france": "fra.1", "fra.1": "fra.1",
            "brasileirao": "bra.1", "brazil": "bra.1", "bra.1": "bra.1",
            "argentina": "arg.1", "arg.1": "arg.1"
        }
        l_code = league_map.get(league.lower(), league)
        url = f"https://site.api.espn.com/apis/v2/sports/soccer/{l_code}/standings"

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        standings = {}
        
        # ESPN Structure: children -> groups -> standings -> entries -> stats
        # Note: varies slightly by sport
        
        # Helper to safely get stats
        def get_stat(stats_list, name):
            for s in stats_list:
                if s.get('name') == name:
                    return s.get('value')
            return 0

        # NBA Structure
        if sport == "basketball":
            # NBA has conferences, divisions... usually in children
            for child in data.get('children', []): # Conferences
                for group in child.get('standings', {}).get('entries', []):
                    team = group.get('team', {})
                    name = team.get('displayName')
                    stats = group.get('stats', [])
                    
                    # Common overrides
                    overrides = {
                        "Golden State Warriors": "Warriors", "Los Angeles Lakers": "Lakers", "Boston Celtics": "Celtics",
                        "New York Knicks": "Knicks", "Miami Heat": "Heat", "Chicago Bulls": "Bulls",
                        "San Antonio Spurs": "Spurs", "Dallas Mavericks": "Mavericks", "Phoenix Suns": "Suns",
                        "Denver Nuggets": "Nuggets", "Milwaukee Bucks": "Bucks", "Philadelphia 76ers": "Sixers",
                        "Cleveland Cavaliers": "Cavaliers", "Minnesota Timberwolves": "Timberwolves", "Oklahoma City Thunder": "Thunder",
                        "Orlando Magic": "Magic", "Houston Rockets": "Rockets", "Los Angeles Clippers": "Clippers",
                        "Atlanta Hawks": "Hawks", "Indiana Pacers": "Pacers", "New Orleans Pelicans": "Pelicans",
                        "Detroit Pistons": "Pistons", "Toronto Raptors": "Raptors", "Utah Jazz": "Jazz",
                        "Memphis Grizzlies": "Grizzlies", "Washington Wizards": "Wizards", "Charlotte Hornets": "Hornets",
                        "Sacramento Kings": "Kings", "Brooklyn Nets": "Nets", "Portland Trail Blazers": "Blazers"
                    }
                    clean_name = overrides.get(name, name)
                    
                    standings[clean_name] = {
                        "pos": 0, # NBA doesn't always show singular rank in this payload easily, usually conference rank
                        "gp": get_stat(stats, "gamesPlayed"),
                        "w": get_stat(stats, "wins"),
                        "l": get_stat(stats, "losses"),
                        "pts_for": get_stat(stats, "avgPointsFor"),
                        "pts_ag": get_stat(stats, "avgPointsAgainst")
                    }
            
            # Post-process to assign conference rankings if needed, or just leave as is
            # Ideally we want overall rank or conference rank. 
            # For simplicity, we trust the 'entries' order or stats.

        else:
            # Soccer Structure
            if "children" in data:
                entry_list = data['children'][0]['standings']['entries']
            else:
                entry_list = [] # Fallback
                
            for entry in entry_list:
                team = entry.get('team', {})
                name = team.get('displayName')
                stats = entry.get('stats', [])
                
                # Overrides
                overrides = {
                    "Manchester City": "Man City", "Manchester United": "Man United", 
                    "Paris Saint-Germain": "PSG", "Real Madrid": "Real Madrid", "Barcelona": "Barcelona"
                }
                clean_name = overrides.get(name, name)
                
                standings[clean_name] = {
                    "pos": get_stat(stats, "rank"),
                    "gp": get_stat(stats, "gamesPlayed"),
                    "w": get_stat(stats, "wins"),
                    "d": get_stat(stats, "ties"),
                    "l": get_stat(stats, "losses"),
                    "gf": get_stat(stats, "pointsFor"),
                    "ga": get_stat(stats, "pointsAgainst"),
                    "pts": get_stat(stats, "points")
                }
                
        return standings
        
    except Exception as e:
        print(f"⚠️ Error fetching standings: {e}")
        return {}

