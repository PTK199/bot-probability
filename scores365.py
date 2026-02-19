"""
scores365.py — 365Scores Intelligence Module 🧠
Fetches REAL-TIME data from 365Scores internal API:
  - Lineups (confirmed/probable)
  - Missing players & injuries
  - Formations (4-3-3, 3-5-2, etc.)
  - Top performers & player stats
  - Public voting (who does the world think will win?)
  - Live scores during games
  
Integrates with auto_picks.py to enhance predictions.
"""
import requests
import datetime
import json
import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ═══════════════════════════════════════
# 365SCORES API CONFIG
# ═══════════════════════════════════════
BASE_URL = "https://webws.365scores.com/web"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
PARAMS = {
    "appTypeId": "5",
    "langId": "31",           # Portuguese
    "timezoneName": "America/Sao_Paulo",
    "userCountryId": "21",    # Brazil
}

# Sport IDs on 365Scores
SPORT_IDS = {
    "football": 1,
    "basketball": 2,
}

# Competition IDs on 365Scores
COMPETITION_MAP = {
    "Premier League": 7,
    "Campeonato Inglês": 7,
    "La Liga": 11,
    "Campeonato Espanhol": 11,
    "Serie A": 17,
    "Campeonato Italiano": 17,
    "Bundesliga": 35,
    "Ligue 1": 34,
    "Champions League": 572,
    "Liga dos Campeões": 572,
    "Copa Libertadores": 102,
    "Copa do Brasil": 115,
    "Brasileirão": 113,
    "NBA": 132,
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _get(endpoint, extra_params=None):
    """Make a GET request to 365Scores API."""
    params = {**PARAMS}
    if extra_params:
        params.update(extra_params)
    try:
        url = f"{BASE_URL}/{endpoint}"
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[365] ⚠️ API Error ({endpoint}): {e}")
    return None


# ═══════════════════════════════════════
# FETCH GAMES FOR A DATE
# ═══════════════════════════════════════
def get_games_today(target_date=None, competitions=None, sport_id=None):
    """
    Fetch all games for a date from 365Scores.
    Returns list of game dicts with IDs for further lookup.
    
    Args:
        target_date: "YYYY-MM-DD" format (default: today)
        competitions: list of competition IDs to filter (optional)
        sport_id: 1=football, 2=basketball (optional filter)
    """
    if not target_date:
        target_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Format date for API: dd/mm/yyyy
    dt = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    date_fmt = dt.strftime("%d/%m/%Y")
    
    extra = {"startDate": date_fmt, "endDate": date_fmt}
    if competitions:
        extra["competitions"] = ",".join(str(c) for c in competitions)
    if sport_id:
        extra["sports"] = str(sport_id)
    
    data = _get("games/", extra)
    if not data:
        return []
    
    games = []
    for g in data.get("games", []):
        home = g.get("homeCompetitor", {})
        away = g.get("awayCompetitor", {})
        
        games.append({
            "game_id": g.get("id"),
            "home": home.get("name", ""),
            "away": away.get("name", ""),
            "home_long": home.get("longName", ""),
            "away_long": away.get("longName", ""),
            "competition": g.get("competitionDisplayName", ""),
            "competition_id": g.get("competitionId"),
            "start_time": g.get("startTime", ""),
            "status": g.get("statusText", ""),
            "status_group": g.get("statusGroup"),  # 1=live, 2=pre, 3=finished
            "has_lineups": g.get("hasLineups", False),
            "has_missing_players": g.get("hasMissingPlayers", False),
            "lineups_status": g.get("lineupsStatusText", ""),
            "home_score": home.get("score", -1),
            "away_score": away.get("score", -1),
        })
    
    return games


# ═══════════════════════════════════════
# FETCH GAME DETAILS (LINEUPS, INJURIES, STATS)
# ═══════════════════════════════════════
def get_game_details(game_id):
    """
    Fetch full game details including lineups, injuries, formations.
    Returns a rich dict with everything we need for predictions.
    """
    # Check cache first (5 min TTL)
    cache_file = os.path.join(CACHE_DIR, f"365_game_{game_id}.json")
    if os.path.exists(cache_file):
        mtime = os.path.getmtime(cache_file)
        if (datetime.datetime.now().timestamp() - mtime) < 300:  # 5 min
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
    
    data = _get("game/", {"gameId": str(game_id)})
    if not data or "game" not in data:
        return None
    
    game = data["game"]
    members_lookup = {}
    for m in data.get("game", {}).get("members", []) if "members" in data.get("game", {}) else []:
        mid = m.get("id")
        if mid:
            members_lookup[mid] = m
    
    # Also check top-level members
    for m in data.get("members", []):
        mid = m.get("id")
        if mid:
            members_lookup[mid] = m
    
    result = {
        "game_id": game_id,
        "venue": game.get("venue", {}).get("name", ""),
        "referee": "",
        "home": _parse_competitor(game.get("homeCompetitor", {}), members_lookup),
        "away": _parse_competitor(game.get("awayCompetitor", {}), members_lookup),
        "voting": _parse_voting(game.get("promotedPredictions", {})),
        "top_performers": _parse_top_performers(game.get("topPerformers", {})),
    }
    
    # Referee
    for off in game.get("officials", []):
        result["referee"] = off.get("name", "")
        break
    
    # Cache result
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except:
        pass
    
    return result


def _parse_competitor(comp, members_lookup):
    """Parse a competitor's lineup info into structured data."""
    lineups = comp.get("lineups", {})
    members = lineups.get("members", [])
    
    starters = []
    substitutes = []
    missing = []
    doubtful = []
    coach = None
    
    for m in members:
        player_id = m.get("id")
        player_info = members_lookup.get(player_id, {})
        name = player_info.get("name", f"Player #{player_id}")
        short_name = player_info.get("shortName", name)
        jersey = player_info.get("jerseyNumber", "")
        position = m.get("position", {}).get("name", "")
        formation_pos = m.get("formation", {}).get("name", "")
        ranking = m.get("ranking", 0)
        status = m.get("status", 0)
        
        player_data = {
            "name": name,
            "short_name": short_name,
            "jersey": jersey,
            "position": position,
            "formation_role": formation_pos,
            "ranking": ranking,
        }
        
        if status == 1:  # Starting
            starters.append(player_data)
        elif status == 2:  # Substitute
            substitutes.append(player_data)
        elif status == 3:  # Missing/Injured
            injury = m.get("injury", {})
            player_data["injury_reason"] = injury.get("reason", "Desconhecido")
            player_data["expected_return"] = injury.get("expectedReturn", "")
            # Season stats
            stats = m.get("seasonStats", [])
            player_data["season_stats"] = [s.get("text", "") for s in stats]
            missing.append(player_data)
        elif status == 4:  # Management (Coach)
            coach = {"name": name}
        elif status == 5:  # Doubtful
            injury = m.get("injury", {})
            player_data["injury_reason"] = injury.get("reason", "Desconhecido")
            player_data["expected_return"] = injury.get("expectedReturn", "")
            stats = m.get("seasonStats", [])
            player_data["season_stats"] = [s.get("text", "") for s in stats]
            doubtful.append(player_data)
    
    return {
        "name": comp.get("name", ""),
        "formation": lineups.get("formation", ""),
        "lineup_status": lineups.get("status", ""),
        "is_probable": lineups.get("isProbable", False),
        "starters": starters,
        "substitutes": substitutes,
        "missing": missing,
        "doubtful": doubtful,
        "coach": coach,
        "missing_count": len(missing),
        "doubtful_count": len(doubtful),
    }


def _parse_voting(predictions):
    """Parse public voting data."""
    result = {}
    for pred in predictions.get("predictions", []):
        if pred.get("type") == 1:  # "Who will win?"
            for opt in pred.get("options", []):
                name = opt.get("name", "")
                pct = opt.get("vote", {}).get("percentage", 0)
                result[name.lower()] = pct
            result["total_votes"] = pred.get("totalVotes", 0)
        elif pred.get("type") == 3:  # Total Goals
            for opt in pred.get("options", []):
                key = "over" if opt.get("num") == 2 else "under"
                result[key] = opt.get("vote", {}).get("percentage", 0)
    return result


def _parse_top_performers(top):
    """Parse top performer stats."""
    result = []
    for cat in top.get("categories", []):
        entry = {"position": cat.get("name", "")}
        for side in ["homePlayer", "awayPlayer"]:
            player = cat.get(side, {})
            if player:
                stats = {s.get("name", ""): s.get("value", "") for s in player.get("stats", [])}
                entry[side] = {
                    "name": player.get("name", ""),
                    "stats": stats,
                }
        result.append(entry)
    return result


# ═══════════════════════════════════════
# TEAM NAME ALIASES (ESPN → 365Scores)
# ═══════════════════════════════════════
TEAM_ALIASES = {
    # Premier League
    "wolverhampton wanderers": ["wolves", "wolverhampton"],
    "manchester city": ["man city"],
    "manchester united": ["man united", "man utd"],
    "tottenham hotspur": ["tottenham", "spurs"],
    "brighton and hove albion": ["brighton"],
    "brighton & hove albion": ["brighton"],
    "west ham united": ["west ham"],
    "newcastle united": ["newcastle"],
    "leicester city": ["leicester"],
    "ipswich town": ["ipswich"],
    "luton town": ["luton"],
    "leeds united": ["leeds"],
    "nottingham forest": ["nott'ham forest", "nottingham"],
    "afc bournemouth": ["bournemouth"],
    "sheffield united": ["sheffield utd"],
    # La Liga
    "atletico madrid": ["atlético madrid", "atlético de madrid", "atl. madrid"],
    "athletic club": ["athletic bilbao", "bilbao"],
    "real sociedad": ["sociedad"],
    "real betis": ["betis"],
    "celta vigo": ["celta de vigo", "celta"],
    # Serie A
    "inter milan": ["internazionale", "inter"],
    "ac milan": ["milan"],
    # Bundesliga
    "bayer leverkusen": ["leverkusen"],
    "borussia dortmund": ["dortmund", "bvb"],
    "rb leipzig": ["leipzig"],
    "eintracht frankfurt": ["frankfurt", "ein. frankfurt"],
    "bayern munich": ["bayern münchen", "bayern"],
    "mainz": ["mainz 05", "1. fsv mainz 05"],
    "hamburg sv": ["hamburger sv", "hamburg", "hsv"],
    # Ligue 1
    "paris saint-germain": ["psg", "paris sg"],
    "marseille": ["olympique marseille", "marsell"],
    "lyon": ["olympique lyonnais", "ol"],
    "brest": ["stade brestois", "stade brest"],
    # Brasileirão
    "athletico paranaense": ["athletico-pr", "athletico", "cap", "ath paranaense"],
    "atletico mineiro": ["atlético-mg", "atlético mineiro", "galo"],
    "corinthians": ["corinthians", "timão"],
    "palmeiras": ["palm", "verdão"],
    "flamengo": ["fla", "mengão"],
    "sao paulo": ["são paulo", "spfc"],
    "vasco da gama": ["vasco"],
    "red bull bragantino": ["bragantino", "rb bragantino"],
    # Other
    "paris fc": ["paris fc"],
    # NBA Teams (ESPN name → 365Scores variants)
    "warriors": ["golden state warriors", "golden state", "gs warriors"],
    "celtics": ["boston celtics", "boston"],
    "cavaliers": ["cleveland cavaliers", "cleveland", "cavs"],
    "thunder": ["oklahoma city thunder", "oklahoma city", "okc"],
    "rockets": ["houston rockets", "houston"],
    "knicks": ["new york knicks", "ny knicks", "new york"],
    "nuggets": ["denver nuggets", "denver"],
    "clippers": ["los angeles clippers", "la clippers", "l.a. clippers"],
    "lakers": ["los angeles lakers", "la lakers", "l.a. lakers"],
    "suns": ["phoenix suns", "phoenix"],
    "mavericks": ["dallas mavericks", "dallas", "mavs"],
    "bucks": ["milwaukee bucks", "milwaukee"],
    "heat": ["miami heat", "miami"],
    "76ers": ["philadelphia 76ers", "philadelphia", "sixers", "phila"],
    "sixers": ["philadelphia 76ers", "philadelphia", "76ers", "phila"],
    "nets": ["brooklyn nets", "brooklyn"],
    "hawks": ["atlanta hawks", "atlanta"],
    "bulls": ["chicago bulls", "chicago"],
    "pistons": ["detroit pistons", "detroit"],
    "pacers": ["indiana pacers", "indiana"],
    "grizzlies": ["memphis grizzlies", "memphis"],
    "timberwolves": ["minnesota timberwolves", "minnesota", "wolves", "t-wolves"],
    "pelicans": ["new orleans pelicans", "new orleans"],
    "magic": ["orlando magic", "orlando"],
    "kings": ["sacramento kings", "sacramento"],
    "raptors": ["toronto raptors", "toronto"],
    "jazz": ["utah jazz", "utah"],
    "blazers": ["portland trail blazers", "portland", "trail blazers"],
    "wizards": ["washington wizards", "washington"],
    "hornets": ["charlotte hornets", "charlotte"],
    "spurs": ["san antonio spurs", "san antonio"],
}


def _normalize_name(name):
    """Returns the name + all its aliases as a list for matching."""
    n = name.lower().strip()
    aliases = [n]
    for key, vals in TEAM_ALIASES.items():
        if n == key or n in vals:
            aliases.extend([key] + vals)
    return list(set(aliases))


# ═══════════════════════════════════════
# INTELLIGENCE: ANALYZE GAME FOR PICKS
# ═══════════════════════════════════════
def get_lineup_intelligence(home_team, away_team, target_date=None, sport="football"):
    """
    Main entry point for auto_picks integration.
    Tries to find the game on 365Scores and extract intelligence.
    Works for both football AND basketball (NBA).
    
    Returns dict with:
        - formations (football)
        - missing_players impact
        - lineup_confidence_adjustment
        - public_sentiment
        - key_facts (list of strings for display)
    """
    if not target_date:
        target_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    sport_id = SPORT_IDS.get(sport, None)
    sport_label = "🏀" if sport == "basketball" else "⚽"
    print(f"[365] {sport_label} Buscando lineup intel: {home_team} vs {away_team}")
    
    # Fetch games filtered by sport
    games = get_games_today(target_date, sport_id=sport_id)
    game_id = None
    
    # Build alias sets for matching
    home_aliases = _normalize_name(home_team)
    away_aliases = _normalize_name(away_team)
    
    for g in games:
        h = g["home"].lower().strip()
        a = g["away"].lower().strip()
        hl = g.get("home_long", "").lower().strip()
        al = g.get("away_long", "").lower().strip()
        
        # Check all combinations of aliases against 365scores names
        home_match = False
        away_match = False
        
        for alias in home_aliases:
            if (alias in h or alias in hl or h in alias or hl in alias or
                any(w in alias for w in h.split() if len(w) > 3) or
                any(w in h for w in alias.split() if len(w) > 3)):
                home_match = True
                break
        
        for alias in away_aliases:
            if (alias in a or alias in al or a in alias or al in alias or
                any(w in alias for w in a.split() if len(w) > 3) or
                any(w in a for w in alias.split() if len(w) > 3)):
                away_match = True
                break
        
        if home_match and away_match:
            game_id = g["game_id"]
            break
    
    if not game_id:
        print(f"[365] ⚠️ Game not found on 365Scores")
        return None
    
    # Get full details
    details = get_game_details(game_id)
    if not details:
        return None
    
    # Build intelligence report
    intel = {
        "source": "365Scores",
        "game_id": game_id,
        "venue": details.get("venue", ""),
        "referee": details.get("referee", ""),
        "home_formation": details["home"].get("formation", ""),
        "away_formation": details["away"].get("formation", ""),
        "lineup_confirmed": not details["home"].get("is_probable", True),
        "key_facts": [],
        "prob_adjustment": 0,  # How much to adjust home team probability
    }
    
    # === INJURY IMPACT ANALYSIS ===
    h_missing = details["home"]["missing_count"]
    a_missing = details["away"]["missing_count"]
    h_doubtful = details["home"]["doubtful_count"]
    a_doubtful = details["away"]["doubtful_count"]
    
    # Check for key player injuries (high-ranking players missing)
    h_key_missing = [p for p in details["home"]["missing"] if any(
        "gol" in s.lower() for s in p.get("season_stats", [])
    )]
    a_key_missing = [p for p in details["away"]["missing"] if any(
        "gol" in s.lower() for s in p.get("season_stats", [])
    )]
    
    if h_missing > a_missing:
        diff = h_missing - a_missing
        intel["prob_adjustment"] -= diff * 2  # -2% per extra injury
        intel["key_facts"].append(
            f"🏥 {details['home']['name']} tem {h_missing} desfalques vs {a_missing} do rival"
        )
    elif a_missing > h_missing:
        diff = a_missing - h_missing
        intel["prob_adjustment"] += diff * 2
        intel["key_facts"].append(
            f"🏥 {details['away']['name']} tem {a_missing} desfalques vs {h_missing} do rival"
        )
    
    # Key player missing detail
    for p in details["home"]["missing"]:
        name = p["name"]
        reason = p.get("injury_reason", "")
        stats = ", ".join(p.get("season_stats", [])[:2])
        intel["key_facts"].append(f"❌ {name} FORA ({reason}) [{stats}]")
    
    for p in details["away"]["missing"]:
        name = p["name"]
        reason = p.get("injury_reason", "")
        stats = ", ".join(p.get("season_stats", [])[:2])
        intel["key_facts"].append(f"❌ {name} FORA ({reason}) [{stats}]")
    
    # Doubtful players
    for p in details["home"]["doubtful"]:
        intel["key_facts"].append(f"⚠️ {p['name']} DÚVIDA ({p.get('injury_reason', '')})")
    for p in details["away"]["doubtful"]:
        intel["key_facts"].append(f"⚠️ {p['name']} DÚVIDA ({p.get('injury_reason', '')})")
    
    # === FORMATION INSIGHT ===
    if details["home"]["formation"] and details["away"]["formation"]:
        intel["key_facts"].append(
            f"📋 Formação: {details['home']['name']} {details['home']['formation']} vs "
            f"{details['away']['name']} {details['away']['formation']}"
        )
    
    # === PUBLIC SENTIMENT ===
    voting = details.get("voting", {})
    if voting:
        h_vote = voting.get(details["home"]["name"].lower(), 0)
        a_vote = voting.get(details["away"]["name"].lower(), 0)
        draw_vote = voting.get("empate", 0)
        total = voting.get("total_votes", 0)
        
        intel["public_sentiment"] = {
            "home_pct": h_vote,
            "away_pct": a_vote,
            "draw_pct": draw_vote,
            "total_votes": total,
        }
        
        if total > 500:
            intel["key_facts"].append(
                f"🗳️ Torcida: {details['home']['name']} {h_vote}% | "
                f"Empate {draw_vote}% | {details['away']['name']} {a_vote}% ({total:,} votos)"
            )
    
    # === REFEREE ===
    if intel["referee"]:
        intel["key_facts"].append(f"🏁 Árbitro: {intel['referee']}")
    
    # === VENUE ===
    if intel["venue"]:
        intel["key_facts"].append(f"🏟️ Estádio: {intel['venue']}")
    
    print(f"[365] ✅ Intelligence ready: {len(intel['key_facts'])} facts, adj={intel['prob_adjustment']:+d}%")
    return intel


# ═══════════════════════════════════════
# RESULT FETCHER: GET SCORES FROM 365SCORES
# ═══════════════════════════════════════
def fetch_results_365scores(target_date=None):
    """
    Fetches finished game results from 365Scores API.
    Returns dict keyed by team name (multiple keys per game) with:
        - score: "H-A"
        - home_val, away_val: int scores
        - status: status text
        - completed: bool
    Compatible with ESPN's fetch_from_espn_api format.
    """
    if not target_date:
        target_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    results = {}
    
    # Fetch both basketball AND football
    for sport_name, sport_id in SPORT_IDS.items():
        try:
            games = get_games_today(target_date, sport_id=sport_id)
            
            for g in games:
                # status_group: 1=live, 2=pre, 3=finished
                h_score = g.get("home_score", -1)
                a_score = g.get("away_score", -1)
                status_grp = g.get("status_group", 0)
                is_live = status_grp == 1
                # 3=Finished, 4=Finished (FT/AET/Pens), 5+=Ended
                is_finished = status_grp >= 3 and status_grp <= 10
                
                if h_score < 0 or a_score < 0:
                    continue  # No score yet
                
                if not is_live and not is_finished:
                    continue  # Game hasn't started
                
                status_text = g.get("status", "")
                if is_finished:
                    status_text = "Encerrado"
                elif is_live:
                    status_text = "Ao Vivo"
                
                # Clean format for string
                try:
                    h_val = int(float(h_score))
                    a_val = int(float(a_score))
                except:
                    h_val = h_score
                    a_val = a_score
                    
                result_obj = {
                    "score": f"{h_val}-{a_val}",
                    "home_val": h_val,
                    "away_val": a_val,
                    "status": status_text,
                    "completed": is_finished,
                    "source": "365Scores",
                    "sport": sport_name
                }
                
                # Add multiple name keys for robust matching
                home_names = [g["home"], g.get("home_long", "")]
                away_names = [g["away"], g.get("away_long", "")]
                
                for name in home_names + away_names:
                    if name:
                        results[name] = result_obj
                        # Also add short versions (e.g., "Golden State Warriors" → "Warriors")
                        parts = name.split()
                        if len(parts) > 1:
                            results[parts[-1]] = result_obj  # Last word (e.g., "Warriors")
                            if len(parts) > 2:
                                results[parts[0]] = result_obj  # First word
                        
            print(f"[365-RESULTS] ✅ {sport_name}: {len(games)} jogos encontrados")
        except Exception as e:
            print(f"[365-RESULTS] ⚠️ Erro ao buscar {sport_name}: {e}")
    
    print(f"[365-RESULTS] 📊 Total: {len(results)} entradas de resultado")
    return results


# ═══════════════════════════════════════
# GOOGLE RESULT SCRAPER (FALLBACK)
# ═══════════════════════════════════════
def fetch_result_from_google(home_team, away_team):
    """
    Last resort: Scrape Google search for game result.
    Returns result_obj or None.
    """
    try:
        query = f"{home_team} vs {away_team} placar resultado hoje"
        url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=pt-BR"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return None
        
        text = resp.text
        
        # Google shows scores in specific patterns
        # Look for score patterns like "2 - 1" or "102 - 98" near team names
        import re
        
        # Pattern 1: "TeamA N - N TeamB" or "N - N" near team names
        # Google sports scores are in spans with specific classes
        # Try to find scores in the raw HTML
        score_patterns = [
            # NBA/Football: "105" ... "98" in score divs
            r'data-score="(\d+)"',
            # General pattern: digit-digit
            r'>(\d{1,3})\s*[-–]\s*(\d{1,3})<',
            # Google sports card
            r'"score":"(\d+)".*?"score":"(\d+)"',
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    h_score = int(matches[0][0])
                    a_score = int(matches[0][1])
                elif len(matches) >= 2:
                    h_score = int(matches[0])
                    a_score = int(matches[1])
                else:
                    continue
                
                # Sanity check
                if h_score > 300 or a_score > 300:
                    continue
                
                # Check if "encerrado" or "final" appears
                is_finished = any(kw in text.lower() for kw in [
                    "encerrado", "final", "finalizado", "ft", "full time",
                    "resultado final", "fim de jogo"
                ])
                
                return {
                    "score": f"{h_score}-{a_score}",
                    "home_val": h_score,
                    "away_val": a_score,
                    "status": "Encerrado" if is_finished else "Ao Vivo",
                    "completed": is_finished,
                    "source": "Google"
                }
        
    except Exception as e:
        print(f"[GOOGLE] ⚠️ Erro ao buscar resultado: {e}")
    
    return None


# ═══════════════════════════════════════
# TEST
# ═══════════════════════════════════════
if __name__ == "__main__":
    print("=== 365Scores Intelligence Module ===\n")
    
    # Test: Get today's games
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    games = get_games_today(today)
    print(f"📅 {len(games)} jogos encontrados para {today}\n")
    
    for g in games[:5]:
        print(f"  [{g['game_id']}] {g['home']} vs {g['away']} ({g['competition']}) - {g['status']}")
        if g['has_lineups']:
            print(f"         → Escalação: {g['lineups_status']}")
    
    # Test: Get lineup intelligence for first football match
    for g in games:
        if "NBA" not in g.get("competition", ""):
            print(f"\n🔍 Buscando detalhes de: {g['home']} vs {g['away']}")
            intel = get_lineup_intelligence(g["home"], g["away"], today)
            if intel:
                print(f"\n📊 INTELLIGENCE REPORT:")
                for fact in intel["key_facts"]:
                    print(f"   {fact}")
                print(f"\n   Prob Adjustment: {intel['prob_adjustment']:+d}%")
            break
