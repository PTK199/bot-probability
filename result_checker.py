"""
result_checker.py — Sistema Automático de Resultados
Consulta ESPN API para scores finais, determina GREEN/RED,
e move jogos finalizados do dashboard para o history.json.
"""
import json
import os
import datetime
import requests
import time
import sys

# Fix encoding for Windows terminals
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")

# ESPN API endpoints by league
ESPN_ENDPOINTS = {
    "Champions League": "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/scoreboard",
    "Europa League": "https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.europa/scoreboard",
    "Premier League": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
    "La Liga": "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard",
    "Serie A": "https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard",
    "Bundesliga": "https://site.api.espn.com/apis/site/v2/sports/soccer/ger.1/scoreboard",
    "Ligue 1": "https://site.api.espn.com/apis/site/v2/sports/soccer/fra.1/scoreboard",
    "Brasileirão": "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard",
    "Libertadores": "https://site.api.espn.com/apis/site/v2/sports/soccer/conmebol.libertadores/scoreboard",
    "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    # Adicionados na auditoria 25/02/2026
    "FA Cup": "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.fa/scoreboard",
    "Segunda División": "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.2/scoreboard",
    "Süper Lig": "https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/scoreboard",
    "Eredivisie": "https://site.api.espn.com/apis/site/v2/sports/soccer/ned.1/scoreboard",
}

# Normalize team names for matching
TEAM_ALIASES = {
    "AS Monaco": ["Monaco", "AS Monaco", "MON"],
    "Paris Saint-Germain": ["PSG", "Paris Saint-Germain", "Paris SG"],
    "Borussia Dortmund": ["Dortmund", "Borussia Dortmund", "BVB", "DOR"],
    "Real Madrid": ["Real Madrid", "RMA"],
    "Benfica": ["Benfica", "SL Benfica", "SLB"],
    "Galatasaray": ["Galatasaray", "GAL"],
    "Juventus": ["Juventus", "Juve", "JUV"],
    "Independiente Medellín": ["Independiente Medellín", "Ind. Medellín", "DIM"],
    "Sporting Cristal": ["Sporting Cristal", "Cristal", "SCR"],
    "2 de Mayo": ["2 de Mayo", "MAY"],
    "Wolverhampton Wanderers": ["Wolves", "Wolverhampton", "WOL"],
    "AC Milan": ["AC Milan", "Milan", "MIL"],
    "Athletico Paranaense": ["Athletico-PR", "Athletico Paranaense", "CAP"],
}


def normalize_name(name):
    """Normalize team name for comparison."""
    name_lower = name.lower().strip()
    for canonical, aliases in TEAM_ALIASES.items():
        for alias in aliases:
            if alias.lower() == name_lower:
                return canonical.lower()
    return name_lower


def teams_match(espn_name, history_name):
    """Check if two team names refer to the same team."""
    return normalize_name(espn_name) == normalize_name(history_name)


def fetch_espn_results(league, date_str):
    """
    Fetch results from ESPN API for a given league and date.
    date_str format: YYYYMMDD
    Returns list of finished games with scores.
    """
    endpoint = ESPN_ENDPOINTS.get(league)
    if not endpoint:
        return []

    try:
        url = f"{endpoint}?dates={date_str}"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[RESULT-CHECK] ⚠️ ESPN {league} returned {resp.status_code}")
            return []

        data = resp.json()
        results = []

        for event in data.get("events", []):
            comp = event.get("competitions", [{}])[0]
            status = comp.get("status", {}).get("type", {})

            if not status.get("completed", False):
                continue  # Skip games that haven't finished

            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue

            home_team = None
            away_team = None
            home_score = 0
            away_score = 0

            for c in competitors:
                team_name = c.get("team", {}).get("displayName", "")
                score = int(c.get("score", "0"))
                if c.get("homeAway") == "home":
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score

            if home_team and away_team:
                results.append({
                    "home": home_team,
                    "away": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "score_str": f"{home_score}-{away_score}",
                    "league": league,
                })

        return results
    except Exception as e:
        print(f"[RESULT-CHECK] ❌ Error fetching {league}: {e}")
        return []


def determine_pick_result(pick, home_score, away_score):
    """
    Given a pick from history and the actual scores,
    determine if it's WON or LOST.
    """
    selection = pick.get("selection", "").lower()
    market = pick.get("market", "").lower()

    # Double Chance (Dupla Chance): Home or Draw
    if "ou empate" in selection or "dupla chance" in market:
        home_name_lower = pick.get("home", "").lower()
        # Check if home team is in the selection
        if any(part in selection for part in home_name_lower.split()):
            # Home win or draw = WON
            if home_score >= away_score:
                return "WON"
            else:
                return "LOST"
        else:
            # Away team DC
            if away_score >= home_score:
                return "WON"
            else:
                return "LOST"

    # ML / Vencedor
    if "vence" in selection or "vencedor" in market or "ml" in market:
        home_name_lower = pick.get("home", "").lower()
        if any(part in selection for part in home_name_lower.split()):
            return "WON" if home_score > away_score else "LOST"
        else:
            return "WON" if away_score > home_score else "LOST"

    # Over
    if "over" in selection or "acima" in selection or "mais de" in selection:
        import re
        # Extract the line number (e.g., "Over 220.5" -> 220.5)
        match = re.search(r'(\d+\.?\d*)', selection.split("over")[-1] if "over" in selection else selection)
        if match:
            line = float(match.group(1))
            total = home_score + away_score
            return "WON" if total > line else "LOST"

    # Under
    if "under" in selection or "abaixo" in selection or "menos de" in selection:
        import re
        match = re.search(r'(\d+\.?\d*)', selection)
        if match:
            line = float(match.group(1))
            total = home_score + away_score
            return "WON" if total < line else "LOST"

    print(f"[RESULT-CHECK] ⚠️ Could not determine result for: {selection}")
    return "PENDING"


def load_history():
    """Load history.json."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history):
    """Save history.json."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    print(f"[RESULT-CHECK] 💾 History saved ({len(history)} entries)")


def check_and_update_results():
    """
    Main function: checks all games from dashboard (active games)
    and finished PENDING games in history, updates with real results.
    Returns summary of updates made.
    """
    print(f"[RESULT-CHECK] 🔍 Starting result check at {datetime.datetime.now()}")

    history = load_history()
    updates_made = 0

    # Collect all dates that have PENDING entries
    pending_dates = set()
    for entry in history:
        if entry.get("status") == "PENDING":
            date_str = entry.get("date", "")
            if date_str:
                pending_dates.add(date_str)

    if not pending_dates:
        print("[RESULT-CHECK] ✅ No PENDING entries found")
        return {"updates": 0, "greens": 0, "reds": 0}

    # Convert dates to ESPN format (DD/MM -> YYYYMMDD)
    now = datetime.datetime.now()
    current_year = now.year
    espn_dates = {}
    for d in pending_dates:
        try:
            parts = d.split("/")
            day, month = int(parts[0]), int(parts[1])
            # Determine year (assume current year, or next year if month < current month)
            year = current_year
            espn_date = f"{year}{month:02d}{day:02d}"
            espn_dates[d] = espn_date
        except Exception:
            continue

    # Fetch results for each league and date
    all_results = []
    leagues_to_check = set(entry.get("league", "") for entry in history if entry.get("status") == "PENDING")

    for league in leagues_to_check:
        for display_date, espn_date in espn_dates.items():
            results = fetch_espn_results(league, espn_date)
            all_results.extend(results)
            time.sleep(0.3)  # Rate limit

    print(f"[RESULT-CHECK] 📊 Found {len(all_results)} finished games from ESPN")

    # Match results to PENDING entries
    greens = 0
    reds = 0

    for entry in history:
        if entry.get("status") != "PENDING":
            continue

        entry_home = entry.get("home", "")
        entry_away = entry.get("away", "")
        entry_league = entry.get("league", "")

        # Find matching ESPN result
        matched = False
        for result in all_results:
            if result["league"] != entry_league:
                continue

            home_match = teams_match(result["home"], entry_home) or teams_match(result["home"], entry_away)
            away_match = teams_match(result["away"], entry_away) or teams_match(result["away"], entry_home)

            if home_match and away_match:
                # Determine if home/away in ESPN matches our entry orientation
                if teams_match(result["home"], entry_home):
                    h_score = result["home_score"]
                    a_score = result["away_score"]
                else:
                    # Flipped orientation
                    h_score = result["away_score"]
                    a_score = result["home_score"]

                # Determine result
                status = determine_pick_result(entry, h_score, a_score)

                if status in ("WON", "LOST"):
                    entry["status"] = status
                    entry["score"] = f"{h_score}-{a_score}"

                    if status == "WON":
                        odd = float(entry.get("odd", 1.5))
                        entry["profit"] = f"+{int((odd - 1) * 100)}%"
                        entry["badge"] = "✅ GREEN"
                        greens += 1
                    else:
                        entry["profit"] = "-100%"
                        entry["badge"] = "❌ RED"
                        reds += 1

                    updates_made += 1
                    print(f"[RESULT-CHECK] {'🟢' if status == 'WON' else '🔴'} {entry_home} vs {entry_away}: {h_score}-{a_score} → {status}")

                matched = True
                break

        if not matched:
            print(f"[RESULT-CHECK] ⏳ No result yet for: {entry_home} vs {entry_away} ({entry_league})")

    if updates_made > 0:
        save_history(history)

    summary = {
        "updates": updates_made,
        "greens": greens,
        "reds": reds,
        "timestamp": datetime.datetime.now().isoformat()
    }

    print(f"[RESULT-CHECK] ✅ Done: {updates_made} updates ({greens}G/{reds}R)")
    return summary


def add_to_history(game_data):
    """
    Add a finished game directly to history.
    Called when a game on the dashboard finishes.
    """
    history = load_history()
    history.insert(0, game_data)  # Add to top (most recent first)
    save_history(history)
    return True


if __name__ == "__main__":
    result = check_and_update_results()
    print(f"\n📊 Summary: {result}")
